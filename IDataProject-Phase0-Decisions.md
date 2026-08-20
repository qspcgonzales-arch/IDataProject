# IDataProject — Phase 0 Decisions Log

**Last Updated:** 2026-08-20  
**Status:** Locked. These decisions are the implementation baseline.

---

## 1. Hardware — Primary Device

**Decision:** iData T1UHF is the primary UHF handheld scanner.  
**Fallback:** Zebra TC77 / TC78 (Ventor-validated) if iData T1UHF SDK is unavailable.  
**Action required:** Acquire iData T1UHF SDK by Aug 21 (Gate 1). Test raw EPC reads, RSSI control, power, session, and Q-value access. See TRACKER_UPDATED.txt for the Aug 21 tasks.

## 2. Odoo Version

**Decision:** Odoo 19.0.  
**Rationale:** Latest LTS branch; improved `stock_barcode` OWL component model.

## 3. EPC Resolution Model

**Decision:** `rfid.tag.mapping` ORM model — not Barcode Nomenclature.  
**Rationale:** Barcode Nomenclature handles only one EPC-encoding scenario. Three are required (see ARCHITECTURE.md §Key Design Decision 1 and GAP_ANALYSIS.md §Problem 2).

## 4. Calibration Storage

**Decision:** `rfid.calibration.profile` ORM model — not `ir.attachment`.  
**Rationale:** Structured model enables REST CRUD, fleet-wide instant updates, and per-session audit trail.

## 5. Pilot Scope

**Decision:** Inventory Adjustments workflow only. Receiving and Delivery are deferred post-pilot.  
**Rationale:** Inventory Adjustments is the lowest-complexity entry point. Receiving adds PO validation, partial receipts, and serial conflict handling (≈3× complexity).

## 6. Timeline

**Decision:** 8-week validated pilot (Aug 19 – Oct 16), not production rollout.  
**Rationale:** Production rollout is a separate phase after pilot UAT sign-off. The tracker is the source of truth for execution status.

## 7. Android Architecture

**Decision:** Kotlin + Jetpack Compose + MVVM + Hilt DI + Retrofit/OkHttp.  
**Auth:** Odoo API key stored in Android Keystore (hardware-backed where available).

## 8. Deployment (Dev)

**Decision:** Docker Compose (Odoo 19 + PostgreSQL 15 + Redis 7).  
**Production deployment** is deferred to the post-pilot phase.
