import asyncio
import json
import logging
import traceback
from typing import Optional
from autonomous_lending_capture_hook.payload import PayloadExtractor
from autonomous_lending_capture_hook.crypto import CryptoSealer
from autonomous_lending_capture_hook.merkle import MerkleLog
from autonomous_lending_capture_hook.receipt import ReceiptBuilder

logger = logging.getLogger(__name__)

class CaptureHook:
    def __init__(
        self,
        merkle_log: Optional[MerkleLog] = None,
        queue_size: int = 100,
        queue_maxsize: Optional[int] = None
    ):
        effective_queue_size = queue_maxsize if queue_maxsize is not None else queue_size
        self.queue = asyncio.Queue(maxsize=effective_queue_size)
        self.drop_counter = 0
        self.merkle_log = merkle_log if merkle_log is not None else MerkleLog("merkle_state.json")
        self.extractor = PayloadExtractor()
        self.crypto = CryptoSealer()
        self.receipt = ReceiptBuilder("receipt.json")
        self._pause_worker_for_test = False
        self._worker_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Starts the background cryptographic sealing worker."""
        if self._worker_task is None or self._worker_task.done():
            self._worker_task = asyncio.create_task(self._worker())

    async def stop(self) -> None:
        """Stops the background worker gracefully."""
        if self._worker_task and not self._worker_task.done():
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
            self._worker_task = None

    @property
    def is_running(self) -> bool:
        return self._worker_task is not None and not self._worker_task.done()

    @property
    def dropped_events_counter(self) -> int:
        return self.drop_counter

    @property
    def memory_log(self) -> list:
        return self.merkle_log.leaves

    async def record(self, decision: dict) -> None:
        try:
            # Non-blocking put for out-of-band fail-open guarantee
            self.queue.put_nowait(decision)
        except asyncio.QueueFull:
            self.drop_counter += 1
            logger.warning("CaptureHook queue is full. Event dropped (fail-open engaged).")

    async def capture_event(self, decision: dict) -> None:
        """Alias for record() to maintain standard interface."""
        await self.record(decision)

    async def _worker(self) -> None:
        while True:
            try:
                # Wait for test pause if necessary
                while self._pause_worker_for_test:
                    await asyncio.sleep(0.01)

                decision = await self.queue.get()

                # Check if we dropped events and log a signed loss entry
                if self.drop_counter > 0:
                    missed = self.drop_counter
                    self.drop_counter = 0  # reset immediately

                    loss_payload = {
                        "type": "loss_entry",
                        "missed_events": missed
                    }
                    cbor_loss = self.crypto.canonicalize(loss_payload)
                    loss_hash, _, _ = self.crypto.seal(cbor_loss)
                    self.merkle_log.append(loss_hash)
                    logger.error(f"Logged signed loss entry for {missed} missed events.")

                # Process the actual decision
                try:
                    payload = self.extractor.extract(decision)
                    cbor_bytes = self.crypto.canonicalize(payload)
                    hash_hex, ed_sig, ml_sig = self.crypto.seal(cbor_bytes)

                    self.merkle_log.append(hash_hex)
                    # Get inclusion proof for the leaf we just added (index = size - 1)
                    proof = self.merkle_log.get_inclusion_proof(self.merkle_log.size - 1)

                    self.receipt.build_and_save(
                        cbor_bytes,
                        hash_hex,
                        ed_sig,
                        ml_sig,
                        proof
                    )
                except Exception as e:
                    logger.error(f"Failed to process decision: {e}")
                    traceback.print_exc()

                self.queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker encountered error: {e}")
                await asyncio.sleep(1)  # Backoff on unexpected errors
