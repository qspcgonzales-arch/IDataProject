# IDataProject Roadmap Summary

## Objective

The project goal is to build and validate a practical RFID-based inventory adjustment workflow for Odoo 19 using the iData T1UHF device. The roadmap is intentionally focused on a controlled pilot and real-world validation instead of broad production rollout.

## Scope

This roadmap covers the implementation path from project preparation through live warehouse pilot testing. The scope is limited to inventory adjustments and RFID validation for a realistic pilot environment.

## Core Purpose

- Confirm the iData T1UHF device works reliably for the intended workflow
- Connect device-read data to Odoo in a secure and measurable way
- Resolve EPC values to product or lot records
- Handle duplicates, unknown tags, and offline conditions safely
- Calibrate the device for warehouse accuracy and throughput
- Prove the system works in a pilot before considering further expansion

## Updated Timeline

### 1) Preparation Complete (Aug 19-20)

Completed work includes:
- VS Code setup and full roadmap review
- Hardware verification and selection of iData T1UHF as the main device focus
- Project readiness checks and planning setup

This phase confirms the project is ready to move into implementation work.

### 2) Foundation Block (Aug 24-Aug 28)

Planned execution includes:
- Verify Docker Compose and Odoo environment
- Create realistic Odoo test data
- Configure EPC-related barcode and stock handling
- Scaffold the Odoo RFID module
- Create the Android project structure
- Source and validate the T1UHF SDK

This phase establishes the working base for both backend and mobile implementation.

### 3) Odoo Scan Bridge (Aug 31-Sep 10)

Planned work includes:
- Design and validate RFID session/scan models
- Build the POST /stock_barcode_rfid/scan endpoint
- Implement EPC-to-product or lot resolution
- Add API key authentication
- Add duplicate suppression and fallback queue logic
- Create the custom scan UI and connect Android to the backend

This is the core backend integration stage where RFID reads are converted into Odoo actions.

### 4) Live RFID + Hardware Readiness (Sep 11-Sep 18)

Planned work includes:
- Implement the physical RFID inventory loop on T1UHF
- Log raw EPC reads
- Add in-memory deduplication and filtering
- Add batching and throttling for stable upload behavior
- Validate live counts between the device and Odoo backend

This phase verifies whether the hardware and read logic can support the actual operational workflow.

### 5) Offline Handling + Calibration (Sep 21-Sep 30)

Planned work includes:
- Add offline scan buffering for Wi-Fi interruption
- Define and test calibration presets
- Run calibration steps for power, RSSI, session, mode, and throughput
- Compare RFID results against manual counts
- Tune the configuration for reliability and accuracy

This phase is critical to the project success because the business value depends on accurate reads with minimal false positives.

### 6) Final Calibration and Pilot (Oct 1-Oct 16)

Planned work includes:
- Repeat final calibration validation
- Finalize the default profile for the Android app
- Run end-to-end tests across system components
- Perform concurrency, failure-mode, and performance tests
- Launch a warehouse pilot with barcode fallback available
- Capture operator feedback and compare with manual counts
- Finalize the go/no-go decision

This phase validates whether the solution is ready for a real-world warehouse use case.

## Success Gates

The roadmap includes clear project gates:

1. Hardware validation confirmed
2. Odoo foundation and RFID module working
3. Android app and live scan UI connected
4. Calibration accuracy validated in real conditions
5. End-to-end performance and security checks passed
6. Pilot/UAT complete with operator sign-off

## Final Outcome

The overall objective is not to deliver a large-scale rollout immediately. Instead, the project aims to prove that RFID can reliably support inventory adjustments in Odoo with the iData T1UHF device, under controlled conditions, and with measurable performance and accuracy.

If this validation succeeds, the project can move into more advanced warehouse adoption and future expansion with confidence.
