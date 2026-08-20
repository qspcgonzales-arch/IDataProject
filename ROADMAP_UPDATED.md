# IDataProject - Updated Project Roadmap

RFID-Odoo Integration | Updated from the tracker sheet
Last Updated: 2026-08-20
Tracker Status Reference: Aug 19, 2026 to Oct 16, 2026

This roadmap is now aligned to the current tracker sheet and supersedes the earlier generic phase plan. The tracker dates are the controlling schedule for execution.

## Executive Summary

The implementation is now organized around the active tracker window:
- Preparation completed on Aug 19-20
- Environmental setup and hardware validation are the gating items for Aug 24 onward
- Core Odoo RFID development starts immediately after the foundation work
- Android, calibration, pilot, and UAT are scheduled as distinct milestone blocks

The tracker explicitly treats weekend rows as non-working/rest days, and it clearly states that Aug 24 onward must not be marked complete until the work is actually performed.

## Current Status Snapshot

| Window | Scope | Status |
|---|---|---|
| Aug 19-20 | Project setup, roadmap review, hardware verification | Complete |
| Aug 24 onward | Phase 0 closure + implementation foundation | Planned / in progress |
| Sep 1-Sep 18 | Odoo bridge + Android live scan app | Planned |
| Sep 21-Sep 30 | Offline handling + calibration | Planned |
| Oct 1-Oct 16 | Final calibration, E2E, pilot, and UAT | Planned |

## Tracker-Based Roadmap

### Phase 0 / Preparation (Aug 19-20) - Complete

- VS Code setup and full roadmap review
- Project hardware verification and selection of iData T1UHF as the primary focus
- Initial planning, setup, and project readiness check

Deliverable: Prepared project environment and implementation sequence agreed.

### Foundation Block (Aug 24-Aug 28) - Planned

- Aug 24: Confirm Phase 0 decisions log; verify Docker Compose; create realistic Odoo test dataset
- Aug 25: Configure Barcode nomenclature for EPC format; verify stock.lot resolution; confirm XML-RPC/JSON-RPC auth and uid via Python
- Aug 26: Scaffold stock_barcode_rfid module with manifest, models, controllers, security; install empty module; draft architecture notes
- Aug 27: Create Kotlin Android project/package structure; verify build on T1UHF/emulator; set Git repo/branch strategy
- Aug 28: Source and import correct iData T1UHF SDK; resolve Gradle issues; smoke-test SDK init

Deliverable: Odoo environment working, RFID module scaffolded, Android foundation generated, hardware SDK ready for implementation.

### Odoo Scan Bridge (Aug 31-Sep 10) - Planned

- Aug 31: Design rfid.scan.session and rfid.scan.line (reusing stock.move.line patterns); run migration; validate ORM model design
- Sep 1: Build POST /stock_barcode_rfid/scan; implement EPC -> stock.lot.name lookup/create logic; unit-test single EPC resolution
- Sep 2: Add Odoo API key authentication; document Android Keystore contract; add basic rate-limit stub
- Sep 3: Scaffold OWL/QWeb scan UI with session management, live count, manual EPC entry, and poll/long-poll scan count
- Sep 4: Implement server-side duplicate suppression with 2-second EPC dedup window; test burst duplicates with batch E2E checks
- Sep 7: Implement server-side fallback queue when a session is not actively connected; test close/reopen behavior
- Sep 8: Finalize long-poll/SSE behavior; test 50+ EPC bursts and confirm responsiveness
- Sep 9: Add Retrofit/OkHttp API client; secure API key storage in Android Keystore
- Sep 10: Build manual send-test-EPC Android screen; verify EPC reaches Odoo and appears in custom UI

Deliverable: Working Odoo scan endpoint, authenticated bridge, live scan UI, and initial Android integration test path.

### Live RFID + Hardware Readiness (Sep 11-Sep 18) - Planned

- Sep 11: Run rapid-burst, malformed EPC, invalid key, and expired-key tests; document known issues and triage
- Sep 14: Implement T1UHF SDK inventory loop with power/session/inventory-model configuration; log raw EPC reads
- Sep 15: Add tunable in-memory dedup window; confirm duplicate read suppression without flooding logs
- Sep 16: Add RSSI filtering and batch/throttle logic; target throughput and read stability
- Sep 17: Build live unique-tag count, manual flush/sync, and connection-health indicator; connect batches to /scan endpoint
- Sep 18: Perform RFID vs Odoo live-count smoke test; capture over-reads and missed reads for baseline

Deliverable: Device-level read loop and Android/Odoo integration are validated against live tag inventory patterns.

### Offline Handling + Calibration (Sep 21-Sep 30) - Planned

- Sep 21: Implement SQLite offline queue; buffer scans on Wi-Fi drop and resync on reconnect
- Sep 22: Add empty/default calibration preset selector; freeze Android features until calibration Step 6 A/B is complete
- Sep 23: Calibration Step 1 and Step 2; record max-power baseline and lowest complete-read power
- Sep 24: Calibration Step 3; test Sessions 0/1/2 and identify the best session setting
- Sep 25: Calibration Step 4; evaluate Multi-label, Adaptive power-saving, and Fast-read settings
- Sep 28: Calibration Step 5; sweep RSSI floor and identify the threshold that preserves valid reads while reducing cross-shelf noise
- Sep 29: Calibration Step 6; run A/B RFID vs manual count accuracy tests across 5+ varied shelf-density trials
- Sep 30: Calibration Step 7; tune Q-value/anti-collision; profile any throughput bottleneck while holding power/session/RSSI constant

Deliverable: Calibration settings documented and validated against live floor conditions, with a recommended default preset.

### Final Calibration and Pilot (Oct 1-Oct 16) - Planned

- Oct 1: Calibration Step 8; repeat Step 6 A/B accuracy test and verify no regression
- Oct 2: Write final calibration profile; bake power/session/mode/RSSI/Q-value settings into the Android default preset
- Oct 5: Run full E2E test from RFID -> Android dedup -> Odoo bridge -> custom UI -> stock.quant audit trail
- Oct 6: Test concurrent dual-device sessions to ensure no cross-talk
- Oct 7: Validate failure modes: Odoo outage, network drop, garbage EPC, unknown EPC
- Oct 8: Run dense-shelf performance test with 200+ tags and validate throughput requirements
- Oct 9: Security pass and sign-off report; confirm authenticated scan endpoint cannot inject arbitrary stock adjustments
- Oct 12: Start pilot in one real warehouse zone with barcode fallback retained
- Oct 13: Shadow-run Day 1 and compare counts against manual inventory checks
- Oct 14: Shadow-run Day 2 and capture drift between lab calibration and real-floor conditions
- Oct 15: Collect operator feedback; adjust the calibration profile as necessary
- Oct 16: Compile go/no-go decision; finalize OJT documentation and handoff backlog for production rollout/post-launch

Deliverable: A validated pilot, signed-off performance results, and a go/no-go decision based on real warehouse conditions.

## Milestones and Gates

The tracker sheet introduces clear gates for the project:

- Gate 1: Hardware validation and SDK access confirmed
- Gate 2: Odoo foundation and RFID module working
- Gate 3: Android app and live scan UI connected
- Gate 4: Calibration accuracy validated against real inventory conditions
- Gate 5: End-to-end performance and security checks passed
- Gate 6: Pilot/UAT complete with operator sign-off

## Tracker Rule

Any task from Aug 24 onward remains open until the actual work is completed. The roadmap reflects planned execution; the tracker is the record of what has been performed, what is in progress, and what is still blocked.
