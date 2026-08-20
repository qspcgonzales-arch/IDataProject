# ROADMAP_12WEEK_REALISTIC

**Window:** Aug 19, 2026 – Oct 28, 2026  
**Primary Objective:** Production-ready iData T1UHF + Odoo 19 RFID workflow with pilot sign-off  
**Planning Mode:** Risk-aware, gate-driven, with explicit validation checkpoints

## 1) Weekly Breakdown (12-Week Plan)

| Week | Dates | Focus | Entry Criteria | Exit Criteria | Key Dependencies | Buffer / Risk Mitigation | Gate |
|---|---|---|---|---|---|---|---|
| W0 | Aug 19–Aug 22 | Phase 0 closure + hardware validation | Repo and baseline docs available | iData SDK loaded in Android project and tested on emulator + real device | Device access, SDK package, Android toolchain | If SDK blocked by Aug 21 noon, trigger Zebra fallback prep | **Gate 0.5 (Aug 22)** |
| W1 | Aug 24–Aug 28 | Odoo foundation + Android scaffold | Gate 0.5 pass | Odoo test instance online, EPC nomenclature POC, Android scaffold booting | Gate 0.5, Docker/Odoo readiness | Reserve 1 day for Odoo config drift and dependency fixes | **Gate 1.5 (Sep 3 prep)** |
| W2 | Aug 31–Sep 4 | Odoo scan bridge v1 | W1 outputs complete | `/stock_barcode_rfid/scan` handles validation, auth, and dedup | Odoo module scaffold, EPC mapping | Keep one day for route/model adjustments after first integration | Gate 1.5 final |
| W3 | Sep 7–Sep 11 | Barcode event injection POC + Android API client | Odoo scan bridge reachable | Synthetic barcode event visible in Odoo barcode flow from RFID input | W2 API stability | If injection fails by Sep 10, pivot to custom barcode UI extension | **Gate 2.5 (Sep 10)** |
| W4 | Sep 14–Sep 18 | Live RFID device loop + transport hardening | Gate 2.5 pass | Real device reads, batches, and syncs EPCs to Odoo with stable throughput | iData SDK read loop + backend endpoint | Reserve final day for malformed EPC/network failure retests | Gate 3.5 prep |
| W5 | Sep 21–Sep 25 | Live RFID hardware loop confirmation + calibration setup | W4 live loop stable | Session/power/RSSI knobs validated and baseline profile captured | Live hardware loop, tagged test zone | Keep 1-day contingency for RF noise/environment reset | **Gate 3.5 (Sep 24)** |
| W6 | Sep 28–Oct 2 | Calibration execution + offline queue validation | Gate 3.5 pass | Calibration POC measured and offline queue replay proven | Calibration fixtures, known-good test scripts | If queue replay fails, freeze feature work until retry/repair closes | Gate 4.5 prep |
| W7 | Oct 5–Oct 9 | Accuracy closure + stability tests | W6 calibration datasets complete | Accuracy at/above target in controlled zone, dual-device and outage tests done | Live tag inventory + Odoo logs | Reserve 2 days for parameter retuning and repeat tests | **Gate 4.5 (Oct 8)** |
| W8 | Oct 12–Oct 16 | Pilot readiness + UAT execution | Gate 4.5 pass | Pilot zone prepared, UAT scripts passed, operator training done | Calibrated profile + warehouse access | If zone not ready, run lab testbed and shift pilot window within W9 | Gate 5 prep |
| W9 | Oct 19–Oct 20 | Production readiness checklist + pilot go-live pack | W8 evidence complete | Production checklist signed, rollback plan approved, release candidate tagged | UAT pass, monitoring checks | 1-day hold for unresolved critical defects only | **Gate 5 (Oct 20)** |
| W10 | Oct 21–Oct 23 | Controlled pilot run + shadow operations | Gate 5 pass | Pilot shadow-run evidence captured with manual reconciliation | Pilot zone operations | Keep barcode fallback active throughout shadow-run | Gate 6 prep |
| W11 | Oct 26–Oct 28 | Final decision window + sign-off | Pilot evidence available | Go/no-go decision signed by Product, Ops, Engineering, QA | All prior gates passed or approved exceptions | If go deferred, execute contingency schedule in rollback playbook | **Gate 6 (Oct 28)** |

## 2) Phase Entry / Exit Criteria

## Phase 0 — Hardware Validation (W0)
- **Entry:** iData hardware delivered or available, Android build environment ready.
- **Exit:** SDK initialization demonstrated on emulator and real device; read API callable.

## Phase 1 — Foundation (W1–W2)
- **Entry:** Gate 0.5 pass.
- **Exit:** Odoo test instance stable; barcode nomenclature POC complete; RFID module scaffold + scan endpoint online.

## Phase 2 — Integration Expansion (W3–W4)
- **Entry:** Foundation artifacts merged and callable from Android.
- **Exit:** Barcode event injection POC proven; Android API client connected; live scan traffic visible in Odoo.

## Phase 3 — Live RFID Loop (W5)
- **Entry:** Integration path stable in test environment.
- **Exit:** Real RFID loop confirmed with hardware in a live-like zone and baseline read metrics logged.

## Phase 4 — Calibration + Offline Reliability (W6–W7)
- **Entry:** Live RFID loop confirmed.
- **Exit:** Calibration profile validated, offline queue replay validated, accuracy criteria evidence complete.

## Phase 5 — Pilot Readiness + UAT (W8)
- **Entry:** Calibration and resilience tests passed.
- **Exit:** Pilot zone prepared and UAT passed with evidence.

## Phase 5B — Production Readiness Checklist (Requested “Phase 7” Gate) (W9)
- **Entry:** UAT evidence complete.
- **Exit:** Monitoring, rollback, operations checklist, and release readiness sign-offs completed before pilot launch.

## Phase 6 — Pilot + Final Decision (W10–W11)
- **Entry:** Gate 5 pass (after Phase 5B readiness completion).
- **Exit:** Pilot run evidence reviewed and Gate 6 go/no-go signed.

## 3) Dependency Map (High-Level)

1. Hardware validation (Gate 0.5) → 2. Odoo scaffold and nomenclature (Gate 1.5)  
2. Odoo scaffold → 3. Android scaffold and API connectivity  
3. Android + Odoo bridge → 4. Barcode event injection POC (Gate 2.5)  
4. Injection POC → 5. Live RFID hardware loop (Gate 3.5)  
5. Live loop → 6. Calibration + offline queue validation (Gate 4.5)  
6. Calibration/UAT → 7. Production readiness checklist (Gate 5)  
7. Production readiness (Phase 5B / requested Phase 7 gate) → 8. Pilot sign-off (Gate 6)

## 4) Go/No-Go Structure

- **No phase starts without prior gate pass or explicit exception approval.**
- **Exception approvals** require Product + Engineering + QA sign-off with dated remediation plan.
- **Hard stop criteria:** SDK unavailable, injection POC unresolved, calibration below threshold, unresolved critical UAT defect.

## 5) Success Definition by Oct 28, 2026

- Hardware-supported RFID loop is stable on iData T1UHF.
- Odoo integration path is validated with auditability and controlled failure behavior.
- Calibration and offline handling milestones are evidenced.
- Pilot and production readiness checklist are complete.
- Final go/no-go decision documented with stakeholder sign-off.
