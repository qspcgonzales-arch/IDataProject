# CONTINGENCY_AND_ROLLBACK

## Purpose
Risk mitigation playbook for the 12-week iData T1UHF + Odoo roadmap.

## 1) If iData SDK Is Unavailable

- **Trigger:** SDK cannot be acquired or initialized by Gate 0.5 (Aug 22).
- **Fallback:** Use generic Zebra SDK path for temporary continuity.
- **Expected Delay:** ~1 day.
- **Actions:**
  1. Switch Android integration branch to fallback SDK adapter.
  2. Run compatibility smoke test with existing scanner abstraction.
  3. Keep iData path open for later rebase when SDK arrives.
- **Rollback to Primary Path:** Re-enable iData adapter once SDK is stable and re-run Gate 0.5 checks.

---

## 2) If Barcode Event Injection Fails

- **Trigger:** Gate 2.5 (Sep 10) fails to show reliable injection into barcode workflow.
- **Fallback:** Implement custom barcode UI extension and connect RFID bridge directly.
- **Expected Pivot Cost:** ~2 days.
- **Actions:**
  1. Freeze nonessential feature work.
  2. Branch to UI extension implementation.
  3. Run focused end-to-end validation with QA.
- **Rollback to Preferred Path:** Return to native injection approach only after stable proof in real workflow.

---

## 3) If Calibration Accuracy Drops Below 95%

- **Trigger:** Calibration retests are <95% during Gate 4.5 prep/execution.
- **Fallback:** Proceed with controlled pilot shadow-run and schedule live calibration refinement.
- **Expected Impact:** Pilot proceeds with constrained scope and tighter monitoring.
- **Actions:**
  1. Lock conservative read profile.
  2. Add manual reconciliation checkpoints each cycle count.
  3. Execute post-pilot calibration plan with production-like data.
- **Rollback of Risk Posture:** Restore full automation mode only once target calibration confidence is re-established.

---

## 4) If Warehouse Zone Is Not Ready

- **Trigger:** Pilot zone cannot be prepared by Gate 5 date.
- **Fallback:** Use lab testbed and move pilot to late October window.
- **Expected Impact:** Delay pilot launch while preserving integration and UAT momentum.
- **Actions:**
  1. Continue UAT and stability testing in lab testbed.
  2. Keep operations team on parallel zone-prep track.
  3. Re-run zone-readiness checklist before relaunch.
- **Rollback to Original Schedule:** Resume normal pilot plan immediately once zone readiness is confirmed.

---

## Cross-Cutting Rollback Controls

- Keep barcode fallback process active during pilot shadow-run.
- Maintain release-candidate tags for every gate-approved state.
- Require incident log and owner for every contingency activation.
- Re-run failed gate criteria after mitigation before continuing downstream phases.
