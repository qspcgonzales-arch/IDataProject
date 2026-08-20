# IDataProject Phase 0 Decisions Log

Last Updated: 2026-08-24 (foundation baseline)

## Scope and Workflow

- Odoo Version: 19.0
- Primary Workflow: Inventory Adjustments (cycle counts)
- Pilot Strategy: Controlled warehouse pilot before production rollout

## Hardware and Read Strategy

- Primary Reader: iData T1UHF handheld
- Fallback Reader: Zebra T1/T2 UHF handheld
- Read Path: Android app reads EPC, then sends to Odoo bridge endpoint

## EPC and Data Resolution

- EPC resolution target: `stock.lot`/serial-aware matching workflow
- API bridge contract: authenticated POST-based scan ingestion
- Scan controls: server-side deduplication and rate limiting

## Infrastructure Baseline

- Local runtime: Docker Compose (`postgres`, `odoo`, `redis`)
- Odoo module roots:
  - `backend/stock_barcode_rfid`
  - `backend/stock_barcode_rfid_calibration`
- Odoo config baseline: `backend/odoo.conf`
- Postgres bootstrap: `backend/scripts/init-db.sql`

## Aug 24 Foundation Deliverables

- [x] Phase 0 decisions captured in this log
- [x] Docker Compose mount prerequisites created in repository
- [x] Realistic test dataset scaffold added:
  - `backend/tests/data/rfid_test_dataset.json`
  - `backend/tests/conftest.py` fixture loader and object factories

## Deferred Until Hardware Validation Gate

- Live SDK integration and physical tag read tests
- Production calibration values
- Pilot go/no-go decision

