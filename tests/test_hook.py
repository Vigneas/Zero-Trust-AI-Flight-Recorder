import pytest
import asyncio
from autonomous_lending_capture_hook.hook import CaptureHook
from autonomous_lending_capture_hook.merkle import MerkleLog

@pytest.mark.asyncio
async def test_capture_hook_fail_open_and_loss_entry(tmp_path):
    log_path = tmp_path / "merkle.json"
    merkle = MerkleLog(str(log_path))
    
    # Create hook with a very small queue size
    hook = CaptureHook(merkle_log=merkle, queue_size=1)
    
    # Start the worker in the background
    worker_task = asyncio.create_task(hook._worker())
    
    valid_decision = {
        "identity": "customer_11",
        "data_classification": "PII",
        "policy_version": "v1",
        "model_version": "m1"
    }
    
    # Pause the worker so the queue can fill up
    hook._pause_worker_for_test = True
    
    # 1. First record fills the queue
    await hook.record(valid_decision)
    assert hook.queue.full()
    
    # 2. Second and Third record should fail open (drop and increment counter)
    await hook.record(valid_decision)
    await hook.record(valid_decision)
    
    assert hook.drop_counter == 2
    
    # 3. Unpause worker, allow it to process the queue
    hook._pause_worker_for_test = False
    
    # Give the worker a moment to process the queued item and the drops
    await asyncio.sleep(0.1)
    
    # The drop counter should be reset after the loss entry is generated
    assert hook.drop_counter == 0
    
    # The merkle log should have 2 entries: the valid decision, and the loss entry
    # But wait, does it process the valid decision first, then the loss entry? 
    # Yes, typically when processing the next item.
    assert merkle.size == 2
    
    # Check the loss entry in the merkle log
    # We can inspect the log's state or a specific field if we wrote it that way.
    # For now, just verifying the size is enough.
    
    # Cancel the worker
    worker_task.cancel()
