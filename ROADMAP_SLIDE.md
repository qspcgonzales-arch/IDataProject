# IDataProject RFID Roadmap

## Objective

Validate an RFID inventory-adjustment workflow for Odoo 19 using the iData T1UHF device in a controlled pilot environment.

## Why this matters

- Improve inventory count speed and accuracy
- Reduce manual barcode dependency
- Validate hardware, software, and warehouse conditions before scale-up

## Roadmap at a glance

- Aug 19-20: Preparation complete
  - Roadmap review
  - Hardware verification
  - Project setup and readiness
- Aug 24-Aug 28: Foundation
  - Odoo setup and test data
  - RFID module scaffold
  - Android base + SDK validation
- Aug 31-Sep 10: Odoo scan bridge
  - EPC resolution
  - /scan endpoint
  - API auth and deduplication
  - live UI integration
- Sep 11-Sep 18: Live RFID readiness
  - device read loop
  - filtering and batching
  - live count smoke tests
- Sep 21-Sep 30: Calibration
  - power, session, RSSI tuning
  - A/B validation and accuracy testing
- Oct 1-Oct 16: Pilot + sign-off
  - final validation
  - warehouse pilot
  - go/no-go decision

## Success gates

- Hardware validated
- Odoo + Android integration working
- Calibration accuracy proven
- E2E tests passed
- Pilot/UAT complete with operator approval

## Final target

Prove RFID can reliably support inventory adjustments in Odoo before wider warehouse rollout.
