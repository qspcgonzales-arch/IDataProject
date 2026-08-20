# MILESTONES_CRITICAL_PATH

## Critical Path Sequence (Must-Happen Order)

1. **Hardware validation (Gate 0.5, Aug 22)**  
2. **Odoo scaffold + test instance + nomenclature POC (Gate 1.5, Sep 3)**  
3. **Android scaffold + API wiring**  
4. **iData SDK integration + live reader loop**  
5. **Odoo RFID bridge and barcode event injection POC (Gate 2.5, Sep 10)**  
6. **Live RFID hardware loop confirmation (Gate 3.5, Sep 24)**  
7. **Calibration POC + accuracy validation (Gate 4.5, Oct 8)**  
8. **Production readiness checklist (Phase 7 / Gate 5, Oct 20)**  
9. **Pilot shadow-run execution**  
10. **Final go/no-go sign-off (Gate 6, Oct 28)**

---

## Task Dependency Logic

- Calibration cannot begin until **live RFID loop** is confirmed.
- Live RFID loop cannot be trusted until **barcode event injection** is proven.
- Barcode event injection cannot be validated until **Android + Odoo bridge** are connected.
- Android/Odoo integration cannot proceed without **hardware SDK validation**.

---

## Parallelizable Workstreams

### Parallel Track A (Backend)
- Odoo scaffold, endpoint modeling, auth, dedup, audit trail.

### Parallel Track B (Android)
- App scaffold, SDK integration hardening, UI shell, offline queue shell.

### Parallel Track C (QA + DevOps)
- Gate evidence templates, test scripts, environment reliability checks, pilot readiness checklist.

**Constraint:** Parallel tracks converge at each gate; no downstream phase starts without gate pass.

---

## Bottlenecks and Why They Matter

1. **SDK availability and functionality (early bottleneck)**
   - If unresolved, all Android and live RFID tasks block.
2. **Barcode event injection (integration bottleneck)**
   - Failure here breaks the intended Odoo barcode workflow path.
3. **Live RFID loop stability (hardware bottleneck)**
   - Calibration and UAT depend on repeatable read behavior.
4. **Calibration accuracy threshold (quality bottleneck)**
   - Pilot readiness is invalid if calibration cannot meet target.
5. **Warehouse zone readiness (operational bottleneck)**
   - Even with working software, pilot cannot start without physical zone readiness.

---

## Critical Path Risk Controls

- Place buffer between major dependent phases (W2→W3, W5→W6, W7→W8).
- Trigger fallback plans immediately when a gate misses its date.
- Keep barcode fallback active through pilot shadow-run.
- Require documented waiver for any gate bypass.
