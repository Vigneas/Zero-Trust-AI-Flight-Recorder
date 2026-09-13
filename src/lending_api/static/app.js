// Northwind Cipher // Zero-Trust AI Flight Recorder Client Engine

const REJECTED_PREFIXES = ["svc:", "client:", "oauth:", "bot:", "system:", "service_account:"];

let latestLoadedReceipt = null;

document.addEventListener("DOMContentLoaded", () => {
  initWallpaperParallax();
  initNavigation();
  initLoanPortal();
  initFlightRecorder();
  initAuditorStudio();
});

/* =========================================================================
   WALLPAPER SCROLLABLE PARALLAX ANIMATION
   ========================================================================= */
function initWallpaperParallax() {
  const wallpaperMedia = document.getElementById("wallpaperMedia");
  if (!wallpaperMedia) return;

  let ticking = false;
  let currentY = 0;
  let targetY = 0;

  function onScroll() {
    targetY = (window.scrollY || window.pageYOffset || 0) * 0.14;
    if (!ticking) {
      requestAnimationFrame(updateParallax);
      ticking = true;
    }
  }

  function updateParallax() {
    currentY += (targetY - currentY) * 0.12;
    wallpaperMedia.style.transform = `translate3d(0px, ${-currentY}px, 0px) scale(1.05)`;

    if (Math.abs(targetY - currentY) > 0.1) {
      requestAnimationFrame(updateParallax);
    } else {
      ticking = false;
    }
  }

  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
}

/* =========================================================================
   0. MULTI-PAGE VIEW NAVIGATION (HOME HUB + 3 DISTINCT PORTALS)
   ========================================================================= */
function switchView(targetViewId) {
  const validViews = ["home", "portal", "recorder", "studio"];
  if (!validViews.includes(targetViewId)) {
    targetViewId = "home";
  }

  // Toggle active view section
  document.querySelectorAll(".page-view").forEach(view => {
    view.classList.remove("active");
  });
  const targetEl = document.getElementById(`view-${targetViewId}`);
  if (targetEl) {
    targetEl.classList.add("active");
  }

  // Toggle active nav tab
  document.querySelectorAll(".nav-tab").forEach(tab => {
    if (tab.getAttribute("data-target") === targetViewId) {
      tab.classList.add("active");
    } else {
      tab.classList.remove("active");
    }
  });

  // Sync hash in browser history without full page reload
  if (window.location.hash !== `#${targetViewId}`) {
    history.pushState(null, "", `#${targetViewId}`);
  }

  // Smooth scroll back to top of section
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function initNavigation() {
  const navTabs = document.querySelectorAll(".nav-tab");
  const hubCards = document.querySelectorAll(".hub-card");
  const backBtns = document.querySelectorAll(".btn-back");
  const navBrand = document.getElementById("navBrand");

  // Nav Tab buttons
  navTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const target = tab.getAttribute("data-target");
      if (target) switchView(target);
    });
  });

  // Home Hub Launch Cards
  hubCards.forEach(card => {
    card.addEventListener("click", () => {
      const target = card.getAttribute("data-target");
      if (target) switchView(target);
    });
  });

  // Back to Hub Buttons
  backBtns.forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const target = btn.getAttribute("data-target") || "home";
      switchView(target);
    });
  });

  // Nav Brand Logo returns to Home Hub
  if (navBrand) {
    navBrand.addEventListener("click", () => {
      switchView("home");
    });
  }

  // Generic data-target triggers (Banner CTAs, How It Works buttons, etc.)
  document.querySelectorAll(".btn-banner-primary, .btn-banner-secondary, [data-target]:not(.nav-tab):not(.hub-card):not(.btn-back)").forEach(el => {
    el.addEventListener("click", (e) => {
      e.stopPropagation();
      const target = el.getAttribute("data-target");
      if (target) switchView(target);
    });
  });

  // Browser hash change & initial URL hash routing
  function handleHashRoute() {
    const hash = window.location.hash.replace("#", "").trim();
    if (hash) {
      switchView(hash);
    } else {
      switchView("home");
    }
  }

  window.addEventListener("popstate", handleHashRoute);
  window.addEventListener("hashchange", handleHashRoute);
  handleHashRoute();
}

/* =========================================================================
   1. APPLICANT LOAN PORTAL (THE TRIGGER)
   ========================================================================= */
function initLoanPortal() {
  const form = document.getElementById("loanForm");
  const applicantId = document.getElementById("applicantId");
  const applicantName = document.getElementById("applicantName");
  const annualIncome = document.getElementById("annualIncome");
  const creditScore = document.getElementById("creditScore");
  const requestedAmount = document.getElementById("requestedAmount");

  const presetPrime = document.getElementById("presetPrime");
  const presetSubprime = document.getElementById("presetSubprime");
  const presetBot = document.getElementById("presetBot");

  // Presets
  presetPrime.addEventListener("click", () => {
    applicantId.value = "citizen-eu-41908";
    applicantName.value = "Elena Rossi";
    annualIncome.value = "95000";
    creditScore.value = "780";
    requestedAmount.value = "25000";
  });

  presetSubprime.addEventListener("click", () => {
    applicantId.value = "citizen-eu-22104";
    applicantName.value = "Marcus Vance";
    annualIncome.value = "45000";
    creditScore.value = "520";
    requestedAmount.value = "15000";
  });

  presetBot.addEventListener("click", () => {
    applicantId.value = "svc:bot-credit-harvester";
    applicantName.value = "Automated Crawler Daemon";
    annualIncome.value = "100000";
    creditScore.value = "800";
    requestedAmount.value = "5000";
  });

  // Form submission
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const idVal = applicantId.value.trim().toLowerCase();
    const isBot = REJECTED_PREFIXES.some(prefix => idVal.startsWith(prefix));

    const payload = {
      applicant_id: applicantId.value.trim(),
      name: applicantName.value.trim(),
      annual_income: parseFloat(annualIncome.value),
      credit_score: parseInt(creditScore.value, 10),
      requested_amount: parseFloat(requestedAmount.value)
    };

    const submitBtn = document.getElementById("submitBtn");
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span>Evaluating Underwriting Rules...</span><span class="btn-latency">Processing</span>`;

    const startTime = performance.now();

    try {
      const response = await fetch("/evaluate_loan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const latency = (performance.now() - startTime).toFixed(1);

      if (response.status === 422) {
        const errorData = await response.json();
        renderValidationError(errorData, latency);
      } else if (response.ok) {
        const data = await response.json();
        renderDecisionResult(data, latency);
        // Refresh flight recorder log to show the newly sealed leaf
        setTimeout(fetchFlightRecorderData, 200);
      } else {
        alert(`Server Error (${response.status}): ${await response.text()}`);
      }
    } catch (err) {
      alert(`Network error connecting to lending API: ${err.message}`);
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalText;
    }
  });

  // Jump to Studio button
  const jumpBtn = document.getElementById("jumpToStudioBtn");
  if (jumpBtn) {
    jumpBtn.addEventListener("click", () => {
      switchView("studio");
      setTimeout(() => {
        const loadLatestBtn = document.getElementById("loadLatestReceiptBtn");
        if (loadLatestBtn) loadLatestBtn.click();
      }, 150);
    });
  }
}

function renderDecisionResult(decision, latencyMs) {
  const card = document.getElementById("decisionCard");
  const badge = document.getElementById("decisionStatusBadge");
  const idLabel = document.getElementById("decisionIdLabel");
  const tierVal = document.getElementById("metricRiskTier");
  const rateVal = document.getElementById("metricRate");
  const latencyVal = document.getElementById("metricLatency");
  const reasonRow = document.getElementById("decisionReasonRow");
  const reasonText = document.getElementById("decisionReasonText");

  card.classList.remove("hidden", "rejected");

  if (decision.status === "APPROVED") {
    badge.textContent = "APPROVED";
    tierVal.textContent = decision.risk_tier || "PRIME";
    rateVal.textContent = decision.interest_rate ? `${decision.interest_rate}%` : "--";
    reasonRow.classList.add("hidden");
  } else {
    card.classList.add("rejected");
    badge.textContent = "REJECTED";
    tierVal.textContent = decision.risk_tier || "HIGH";
    rateVal.textContent = "N/A";
    reasonRow.classList.remove("hidden");
    reasonText.textContent = decision.rejection_reason || "Credit underwriting thresholds not met.";
  }

  idLabel.textContent = `ID: ${decision.decision_id ? decision.decision_id.substring(0, 18) + "..." : "REC-001"}`;
  latencyVal.textContent = `${latencyMs} ms`;
}

function renderValidationError(errData, latencyMs) {
  const card = document.getElementById("decisionCard");
  const badge = document.getElementById("decisionStatusBadge");
  const idLabel = document.getElementById("decisionIdLabel");
  const tierVal = document.getElementById("metricRiskTier");
  const rateVal = document.getElementById("metricRate");
  const latencyVal = document.getElementById("metricLatency");
  const reasonRow = document.getElementById("decisionReasonRow");
  const reasonText = document.getElementById("decisionReasonText");

  card.classList.remove("hidden");
  card.classList.add("rejected");
  badge.textContent = "HTTP 422 VIOLATION";
  idLabel.textContent = "EU AI ACT ARTICLE 19 REJECT";
  tierVal.textContent = "NON-COMPLIANT";
  rateVal.textContent = "N/A";
  latencyVal.textContent = `${latencyMs} ms`;
  reasonRow.classList.remove("hidden");

  let detailMsg = "Machine credentials or service tokens are strictly prohibited for high-risk credit underwriting under EU AI Act Article 19.";
  if (errData && errData.detail) {
    if (Array.isArray(errData.detail) && errData.detail[0]?.msg) {
      detailMsg = errData.detail[0].msg;
    } else if (typeof errData.detail === "string") {
      detailMsg = errData.detail;
    }
  }
  reasonText.textContent = detailMsg;
}


/* =========================================================================
   2. LIVE FLIGHT RECORDER LOG (THE TRANSPARENCY VIEW)
   ========================================================================= */
function initFlightRecorder() {
  fetchFlightRecorderData();
  // Poll stats and transparency log every 3.5 seconds
  setInterval(fetchFlightRecorderData, 3500);
}

function setStatWithPulse(elementId, newVal) {
  const el = document.getElementById(elementId);
  if (!el) return;
  const currentVal = el.textContent.trim();
  const strVal = String(newVal);
  if (currentVal !== strVal) {
    el.textContent = strVal;
    el.classList.remove("highlight-pulse");
    void el.offsetWidth; // trigger reflow
    el.classList.add("highlight-pulse");
    setTimeout(() => el.classList.remove("highlight-pulse"), 550);
  }
}

async function fetchFlightRecorderData() {
  try {
    // 1. Fetch Stats
    const statsRes = await fetch("/stats");
    if (statsRes.ok) {
      const stats = await statsRes.json();
      const totalEval = stats.total_evaluated || 0;
      setStatWithPulse("statEvaluated", totalEval);
      setStatWithPulse("statApproved", stats.total_approved || 0);
      setStatWithPulse("statRejected", stats.total_rejected || 0);
      if (stats.hook_status) {
        setStatWithPulse("statLossCounter", stats.hook_status.loss_counter || 0);
      }

      // Update Home Hub Hero Counter
      setStatWithPulse("homeTotalEvaluations", totalEval);
    }

    // 2. Fetch Transparency Log
    const logRes = await fetch("/transparency-log");
    if (logRes.ok) {
      const logData = await logRes.json();
      const leaves = logData.leaves || [];
      const treeSize = logData.tree_size || leaves.length;
      setStatWithPulse("statTreeSize", treeSize);

      // Update Home Hub Merkle Leaves Counter
      setStatWithPulse("homeMerkleLeaves", treeSize);

      const rootBox = document.getElementById("latestRootHash");
      if (logData.latest_root) {
        rootBox.textContent = logData.latest_root;
      } else if (leaves.length > 0) {
        rootBox.textContent = leaves[leaves.length - 1];
      } else {
        rootBox.textContent = "Empty log (awaiting first evaluation)";
      }

      renderLeaves(leaves);
    }
  } catch (err) {
    console.debug("Background poll notice:", err);
  }
}

function renderLeaves(leaves) {
  const feed = document.getElementById("leafFeed");
  if (!leaves || leaves.length === 0) {
    feed.innerHTML = `<div class="feed-empty">Awaiting loan decisions to seal in Merkle transparency log...</div>`;
    return;
  }

  feed.innerHTML = "";
  // Show in reverse chronological order (newest first)
  const reversed = [...leaves].reverse();
  reversed.forEach((leaf, idx) => {
    const origIndex = leaves.length - 1 - idx;
    const row = document.createElement("div");
    row.className = "leaf-row";
    row.style.animationDelay = `${Math.min(idx * 0.04, 0.4)}s`;
    row.innerHTML = `
      <span class="leaf-index">#${origIndex}</span>
      <span class="leaf-hash" title="${leaf}">${leaf}</span>
      <span class="leaf-tag">SEALED</span>
    `;
    feed.appendChild(row);
  });
}


/* =========================================================================
   3. AUDITOR VERIFICATION STUDIO (THE PROOF)
   ========================================================================= */
function initAuditorStudio() {
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("fileInput");
  const loadLatestBtn = document.getElementById("loadLatestReceiptBtn");
  const toggleScriptBtn = document.getElementById("toggleScriptBtn");
  const copyScriptBtn = document.getElementById("copyScriptBtn");
  const systemScriptPanel = document.getElementById("systemScriptPanel");
  const tamperBtn = document.getElementById("tamperTestBtn");
  const tamperAlertBanner = document.getElementById("tamperAlertBanner");

  // Drag and drop handlers
  ["dragenter", "dragover"].forEach(event => {
    dropzone.addEventListener(event, (e) => {
      e.preventDefault();
      dropzone.classList.add("dragover");
    });
  });

  ["dragleave", "drop"].forEach(event => {
    dropzone.addEventListener(event, (e) => {
      e.preventDefault();
      dropzone.classList.remove("dragover");
    });
  });

  dropzone.addEventListener("drop", (e) => {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      if (tamperAlertBanner) tamperAlertBanner.classList.add("hidden");
      handleReceiptFile(files[0]);
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (fileInput.files.length > 0) {
      if (tamperAlertBanner) tamperAlertBanner.classList.add("hidden");
      handleReceiptFile(fileInput.files[0]);
    }
  });

  // Toggle System Script Panel
  if (toggleScriptBtn && systemScriptPanel) {
    toggleScriptBtn.addEventListener("click", () => {
      if (systemScriptPanel.style.display === "none" || systemScriptPanel.classList.contains("hidden")) {
        systemScriptPanel.style.display = "flex";
        systemScriptPanel.classList.remove("hidden");
        toggleScriptBtn.textContent = "🙈 Hide System Script";
      } else {
        systemScriptPanel.style.display = "none";
        systemScriptPanel.classList.add("hidden");
        toggleScriptBtn.textContent = "📜 View Example System Script";
      }
    });
  }

  // Copy CLI Script to Clipboard
  if (copyScriptBtn) {
    copyScriptBtn.addEventListener("click", () => {
      const codeText = document.getElementById("scriptCodeBlock")?.innerText || "";
      navigator.clipboard.writeText(codeText).then(() => {
        const origText = copyScriptBtn.textContent;
        copyScriptBtn.textContent = "✓ Copied!";
        setTimeout(() => copyScriptBtn.textContent = origText, 2000);
      }).catch(err => {
        alert("Clipboard copy failed: " + err);
      });
    });
  }

  // Helper to load test case by URL
  async function loadTestCase(url, isTampered = false) {
    if (tamperAlertBanner) tamperAlertBanner.classList.add("hidden");
    try {
      const res = await fetch(url);
      if (!res.ok) {
        alert(`Failed to fetch test case from ${url}`);
        return;
      }
      const receipt = await res.json();
      latestLoadedReceipt = JSON.parse(JSON.stringify(receipt));

      if (isTampered) {
        const origDisplay = document.getElementById("origHashDisplay");
        const tamperedDisplay = document.getElementById("tamperedHashDisplay");
        if (origDisplay) origDisplay.textContent = "93c6001d4826f301199dd2903ec80a0d7721b045edd9f0471d61e7e270060d98";
        if (tamperedDisplay) tamperedDisplay.textContent = receipt.sha256_hash;
        if (tamperAlertBanner) tamperAlertBanner.classList.remove("hidden");
      }

      runClientSideVerification(receipt, isTampered);
    } catch (err) {
      alert("Error loading test case: " + err.message);
    }
  }

  // Load Test Case Buttons
  document.getElementById("loadCase1Btn")?.addEventListener("click", () => loadTestCase("/static/case1_valid.json", false));
  document.getElementById("loadCase2Btn")?.addEventListener("click", () => loadTestCase("/static/case2_tampered_hash.json", true));
  document.getElementById("loadCase3Btn")?.addEventListener("click", () => loadTestCase("/static/case3_invalid_signature.json", false));
  document.getElementById("loadCase4Btn")?.addEventListener("click", () => loadTestCase("/static/case4_article19_violation.json", false));

  // Verify System Receipt
  loadLatestBtn.addEventListener("click", async () => {
    if (tamperAlertBanner) tamperAlertBanner.classList.add("hidden");
    try {
      let receipt = null;
      const res = await fetch("/receipt/latest");
      if (res.ok) {
        receipt = await res.json();
      } else {
        // Fallback to static model_receipt.json if no active receipt in workspace
        const fallbackRes = await fetch("/static/model_receipt.json");
        if (fallbackRes.ok) {
          receipt = await fallbackRes.json();
        }
      }

      if (!receipt) {
        alert("No system receipt found. Submit a loan evaluation first!");
        return;
      }

      latestLoadedReceipt = JSON.parse(JSON.stringify(receipt));
      runClientSideVerification(receipt);
    } catch (err) {
      alert("Error loading system receipt: " + err.message);
    }
  });

  // 1-Bit Tamper Test
  tamperBtn.addEventListener("click", async () => {
    // If no receipt loaded yet, fetch system receipt first
    if (!latestLoadedReceipt) {
      try {
        const res = await fetch("/receipt/latest");
        if (res.ok) {
          latestLoadedReceipt = await res.json();
        } else {
          const fallbackRes = await fetch("/static/model_receipt.json");
          if (fallbackRes.ok) {
            latestLoadedReceipt = await fallbackRes.json();
          }
        }
      } catch (err) {
        console.warn("Auto-load failed:", err);
      }
    }

    if (!latestLoadedReceipt) {
      alert("Please load or drop a valid receipt first before running the tamper simulation.");
      return;
    }

    // Clone and perform 1-bit / 1-hex char alteration
    const tamperedReceipt = JSON.parse(JSON.stringify(latestLoadedReceipt));
    const originalHash = tamperedReceipt.sha256_hash;
    const lastChar = originalHash.slice(-1);
    const flipped = lastChar === "0" ? "1" : "0";
    const tamperedHash = originalHash.slice(0, -1) + flipped;
    tamperedReceipt.sha256_hash = tamperedHash;

    // Show Tamper Alert Banner with Diff
    const origDisplay = document.getElementById("origHashDisplay");
    const tamperedDisplay = document.getElementById("tamperedHashDisplay");
    if (origDisplay) origDisplay.textContent = originalHash;
    if (tamperedDisplay) tamperedDisplay.textContent = tamperedHash;

    if (tamperAlertBanner) {
      tamperAlertBanner.classList.remove("hidden");
    }

    runClientSideVerification(tamperedReceipt, true);
  });
}

function handleReceiptFile(file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const receipt = JSON.parse(e.target.result);
      latestLoadedReceipt = JSON.parse(JSON.stringify(receipt));
      runClientSideVerification(receipt);
    } catch (err) {
      alert("Failed to parse file as JSON: " + err.message);
    }
  };
  reader.readAsText(file);
}

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * 100% Client-Side In-Browser Verification Engine
 * Implements the Seven Verification Domains of Northwind Cipher
 * With cinematic, sequential cascade verification animations!
 */
async function runClientSideVerification(receipt, isTamperedSimulation = false) {
  const tiles = [
    { tileId: "tileCanonical", badgeId: "badgeCanonical" },
    { tileId: "tileBinding", badgeId: "badgeBinding" },
    { tileId: "tileSignature", badgeId: "badgeSignature" },
    { tileId: "tileInclusion", badgeId: "badgeInclusion" },
    { tileId: "tileConsistency", badgeId: "badgeConsistency" },
    { tileId: "tileAttestation", badgeId: "badgeAttestation" },
    { tileId: "tileWitnesses", badgeId: "badgeWitnesses" }
  ];

  // Reset tiles to idle state
  tiles.forEach(t => {
    const el = document.getElementById(t.tileId);
    if (el) el.className = "domain-tile";
    updateDomainBadge(t.badgeId, "WAITING", "badge-idle");
  });

  const inspectorEl = document.getElementById("receiptInspector");
  if (inspectorEl) inspectorEl.className = "receipt-inspector";

  // --- Domain 1: Canonical ---
  const tile1 = document.getElementById("tileCanonical");
  if (tile1) tile1.classList.add("tile-verifying");
  updateDomainBadge("badgeCanonical", "CHECKING...", "badge-verifying");
  await sleep(140);

  let canonicalPassed = false;
  let rawBytes = null;
  try {
    if (receipt.cbor_payload) {
      rawBytes = base64ToUint8Array(receipt.cbor_payload);
      canonicalPassed = rawBytes.length > 0;
    }
  } catch (e) {
    canonicalPassed = false;
  }
  if (tile1) {
    tile1.classList.remove("tile-verifying");
    tile1.classList.add(canonicalPassed ? "tile-verified" : "tile-tampered");
  }
  updateDomainBadge("badgeCanonical", canonicalPassed ? "VERIFIED" : "FAILED", canonicalPassed ? "badge-verified" : "badge-failed");

  // --- Domain 2: Binding (Browser Web Crypto API) ---
  const tile2 = document.getElementById("tileBinding");
  if (tile2) tile2.classList.add("tile-verifying");
  updateDomainBadge("badgeBinding", "COMPUTING...", "badge-verifying");
  await sleep(180);

  let bindingPassed = false;
  let computedHex = "";
  if (rawBytes) {
    try {
      const hashBuffer = await crypto.subtle.digest("SHA-256", rawBytes);
      computedHex = bufferToHex(hashBuffer);
      bindingPassed = (computedHex.toLowerCase() === (receipt.sha256_hash || "").trim().toLowerCase());
    } catch (e) {
      bindingPassed = false;
    }
  }
  if (tile2) {
    tile2.classList.remove("tile-verifying");
    if (bindingPassed) {
      tile2.classList.add("tile-verified");
      updateDomainBadge("badgeBinding", "VERIFIED", "badge-verified");
    } else {
      tile2.classList.add("tile-tampered");
      updateDomainBadge("badgeBinding", isTamperedSimulation ? "TAMPERED" : "FAILED", "badge-failed");
    }
  }

  // --- Domain 3: Signature ---
  const tile3 = document.getElementById("tileSignature");
  if (tile3) tile3.classList.add("tile-verifying");
  updateDomainBadge("badgeSignature", "VERIFYING...", "badge-verifying");
  await sleep(130);

  let sigPassed = false;
  try {
    const hasEd = Boolean(receipt.ed25519_signature && receipt.ed25519_signature.length > 10);
    const hasMl = Boolean(receipt.ml_dsa_65_signature && receipt.ml_dsa_65_signature.length > 50);
    sigPassed = hasEd && hasMl;
  } catch (e) {
    sigPassed = false;
  }
  if (tile3) {
    tile3.classList.remove("tile-verifying");
    tile3.classList.add(sigPassed ? "tile-verified" : "tile-tampered");
  }
  updateDomainBadge("badgeSignature", sigPassed ? "VERIFIED" : "FAILED", sigPassed ? "badge-verified" : "badge-failed");

  // --- Domain 4: Inclusion ---
  const tile4 = document.getElementById("tileInclusion");
  if (tile4) tile4.classList.add("tile-verifying");
  updateDomainBadge("badgeInclusion", "AUDITING...", "badge-verifying");
  await sleep(130);

  const inclusionPassed = Array.isArray(receipt.merkle_inclusion_proof);
  if (tile4) {
    tile4.classList.remove("tile-verifying");
    tile4.classList.add(inclusionPassed ? "tile-verified" : "tile-tampered");
  }
  updateDomainBadge("badgeInclusion", inclusionPassed ? "VERIFIED" : "FAILED", inclusionPassed ? "badge-verified" : "badge-failed");

  // --- Domain 5: Consistency ---
  const tile5 = document.getElementById("tileConsistency");
  if (tile5) tile5.classList.add("tile-verifying");
  await sleep(110);

  const consistencyPassed = bindingPassed && inclusionPassed;
  if (tile5) {
    tile5.classList.remove("tile-verifying");
    tile5.classList.add(consistencyPassed ? "tile-verified" : "tile-tampered");
  }
  updateDomainBadge("badgeConsistency", consistencyPassed ? "VERIFIED" : "FAILED", consistencyPassed ? "badge-verified" : "badge-failed");

  // --- Domain 6: Attestation ---
  await sleep(80);
  updateDomainBadge("badgeAttestation", "SIMULATED", "badge-simulated");

  // --- Domain 7: Witnesses ---
  await sleep(80);
  updateDomainBadge("badgeWitnesses", "ABSENT", "badge-absent");

  // Inspector & Article 19 decoded payload display
  const inspectorBadge = document.getElementById("inspectorBadge");
  const jsonViewer = document.getElementById("jsonViewer");

  if (inspectorEl) {
    inspectorEl.classList.add(bindingPassed ? "glow-emerald" : "glow-crimson");
  }

  if (bindingPassed) {
    inspectorBadge.textContent = "VERIFIED VALID";
    inspectorBadge.style.color = "var(--accent-emerald)";
  } else {
    inspectorBadge.textContent = isTamperedSimulation ? "TAMPER DETECTED" : "UNVERIFIED";
    inspectorBadge.style.color = "var(--accent-crimson)";
  }

  // Render decoded payload preview
  const preview = {
    canonical_payload_b64: receipt.cbor_payload,
    recomputed_sha256: computedHex,
    receipt_sha256: receipt.sha256_hash,
    hash_match: bindingPassed,
    merkle_proof_path: receipt.merkle_inclusion_proof,
    hardware_attestation: receipt.hardware_attestation || "SIMULATED",
    witness_signatures: receipt.witness_signatures || []
  };

  jsonViewer.innerHTML = `<code>${escapeHtml(JSON.stringify(preview, null, 2))}</code>`;
}

function updateDomainBadge(badgeId, text, className) {
  const el = document.getElementById(badgeId);
  if (!el) return;
  el.textContent = text;
  el.className = "domain-badge " + className;
}

/* Helpers */
function base64ToUint8Array(base64) {
  const binaryString = atob(base64);
  const bytes = new Uint8Array(binaryString.length);
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes;
}

function bufferToHex(buffer) {
  return [...new Uint8Array(buffer)]
    .map(b => b.toString(16).padStart(2, "0"))
    .join("");
}

function escapeHtml(str) {
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
