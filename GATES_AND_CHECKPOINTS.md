# GATES_AND_CHECKPOINTS

All gates are **go/no-go controls**. A gate is only passed when all pass criteria are met and evidence is attached.

## Gate 0.5 — Aug 22, 2026
**Goal:** iData SDK functional in Android emulator and real device.

### Pass Criteria
- SDK is imported and build succeeds.
- Emulator smoke test passes (init path callable).
- Real device init/read API call succeeds.
- QA evidence package uploaded (logs + screenshot/video).

### Fail Criteria
- SDK cannot be imported or initialized.
- Real device validation unavailable or unstable.

### Decision
- **PASS:** Proceed to foundation phase.
- **FAIL:** Trigger SDK fallback contingency immediately.

---

## Gate 1.5 — Sep 3, 2026
**Goal:** Odoo test instance + barcode nomenclature POC complete.

### Pass Criteria
- Odoo, PostgreSQL, Redis test stack healthy.
- EPC nomenclature maps to expected stock.lot behavior in POC.
- RFID module scaffold installed without load error.

### Fail Criteria
- Odoo stack unstable.
- Nomenclature POC unresolved.
- Module scaffold fails to install.

### Decision
- **PASS:** Start broadened integration phase.
- **FAIL:** Hold API and Android integration work.

---

## Gate 2.5 — Sep 10, 2026
**Goal:** Barcode event injection proof-of-concept.

### Pass Criteria
- RFID input reaches Odoo bridge endpoint with auth.
- Synthetic barcode event is visible in target barcode flow.
- End-to-end POC demo validated by QA.

### Fail Criteria
- Injection mechanism fails in practical workflow.
- Event path only works in isolated/mock conditions.

### Decision
- **PASS:** Continue to live RFID loop hardening.
- **FAIL:** Pivot to custom barcode UI extension (2-day plan).

---

## Gate 3.5 — Sep 24, 2026
**Goal:** Live RFID hardware loop confirmed.

### Pass Criteria
- iData reader loop runs with stable read/batch behavior.
- Odoo receives and records live loop traffic.
- Known failure tests (malformed EPC/network flap) complete.

### Fail Criteria
- Unstable read loop or unresolved data loss.
- Endpoint cannot sustain live burst traffic.

### Decision
- **PASS:** Start calibration and reliability validation.
- **FAIL:** Freeze calibration and resolve loop stability.

---

## Gate 4.5 — Oct 8, 2026
**Goal:** Calibration accuracy >=98% in test zone.

### Pass Criteria
- Calibration POC completed with documented settings.
- Measured accuracy is **>=98%** in agreed test zone.
- Offline queue replay validation passes.

### Fail Criteria
- Accuracy <98% in controlled retests.
- Offline queue replay produces mismatches or losses.

### Decision
- **PASS:** Enter pilot readiness and UAT.
- **FAIL:** Execute calibration contingency path.

---

## Gate 5 — Oct 20, 2026
**Goal:** Pilot zone RFID-tagged and UAT passed.

### Pass Criteria
- Pilot zone prepared and tagged.
- UAT scripts passed with sign-off.
- Production readiness checklist complete.

### Fail Criteria
- Zone incomplete or UAT has unresolved critical defects.
- Checklist gaps in monitoring, rollback, or operations readiness.

### Decision
- **PASS:** Run controlled pilot shadow operations.
- **FAIL:** Delay pilot and use lab testbed contingency.

---

## Gate 6 — Oct 28, 2026
**Goal:** Final go/no-go sign-off.

### Pass Criteria
- Prior gates passed (or waiver approved with remediation).
- Pilot evidence reviewed by Product, Ops, Engineering, QA.
- Final decision record signed.

### Fail Criteria
- Critical risks unresolved.
- Missing required sign-off from accountable stakeholders.

### Decision
- **GO:** Authorize production pilot continuation/rollout.
- **NO-GO:** Apply rollback and delayed cutover plan.
