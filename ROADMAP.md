# IDataProject — Project Roadmap
**RFID-Odoo Integration**
**Last Updated:** 2026-08-18

---

# 0. Project Summary

**Goal:** Replace barcode scanning as the primary inventory-counting method with UHF RFID (Zebra T1/T2), integrated directly into Odoo's native Barcode application, without breaking existing barcode-based workflows.

## Success Criteria

- RFID scans flow into the same stock_barcode screens (Receipts, Deliveries, Inventory Adjustments) operators already use.
- Bulk-read accuracy ≥ 99% against ground-truth counts in the calibrated read zone, with near-zero false cross-reads from adjacent bins.
- Full-shelf inventory count time reduced by a target of 60–70% vs. barcode-by-barcode scanning.
- System is stable enough for daily warehouse floor use — not just a demo.

## Stack

Android (Kotlin, Zebra UHF SDK)  ·  Odoo 19.0 (Python, OWL/JS)  ·  PostgreSQL  ·  self-hosted Docker deployment.

## Dual Use Case

1. **Warehouse (immediate):** RFID calibration + Odoo Barcode integration (Phase 1–7)
2. **Toll/Highway (future):** RFID vehicle/asset tracking at toll plazas using calibrated profiles (Phase 8+)

---

# 1. Phased Roadmap

---

## Phase 0 — Discovery & Requirements Lock ✅ COMPLETE
**Week 1**

Before writing code, nail down the things that are expensive to change later.

- [x] Confirm Odoo version → **Odoo 19.0 (deployed)**
- [x] Decide EPC encoding strategy → **Hybrid: in-house (Zebra printer) + pre-encoded from supplier**
- [x] Define EPC ↔ Odoo data model mapping → **EPC → stock.lot.name via Barcode Nomenclature rule**
- [x] Inventory the physical environment → **Mixed shelf inventory, mid-range operator distance (~50cm–1.5m)**
- [x] Lock which workflow goes RFID-first → **Inventory Adjustments (cycle counts)**
- [x] Hardware confirmed → **Zebra T1/T2 UHF handheld + Zebra UHF printer for tag encoding**
- [x] Architecture confirmed → **Monorepo (IDataProject), backend + android in one repo**

**Deliverable: ✅ Phase 0 Decisions doc + one-page requirements signed off**
> See: `IDataProject-Phase0-Decisions.md`

---

## Phase 1 — Environment & Foundations 🔲 IN PROGRESS
**Week 1–2**

- [x] Git monorepo scaffold (IDataProject) with branch strategy
- [x] CI/CD pipelines: GitHub Actions for backend (Python tests, lint, coverage) + Android (build, ktlint, OWASP)
- [x] Security scan pipeline (truffleHog, CodeQL, bandit, dependency audit)
- [x] Odoo module scaffold: `stock_barcode_rfid` (manifest, models, controllers)
- [x] Android app scaffold: Kotlin project structure, test skeleton
- [x] Architecture, API contract, security, development, contributing docs
- [x] Docker Compose dev environment (Odoo 19 + PostgreSQL + Redis)
- [ ] Odoo 19 dev instance running in Docker with stock_barcode enabled
- [ ] Configure Barcode Nomenclature rule matching EPC format (Rule Type = Lot/Serial Number)
- [ ] Zebra UHF Android SDK sourced and integrated into Android project
- [ ] Basic scan loop confirmed against physical tags (Zebra T1/T2)

**Deliverable: "Hello World" on both ends**
> Android reads a tag and logs an EPC → Odoo Barcode app resolves a manually-typed EPC as a known lot.

---

## Phase 2 — Odoo-Side Bridge Module 🔲 PENDING
**Week 2–3**

RFID becomes a first-class scan source inside Odoo's real Barcode app.

- [ ] `stock_barcode_rfid` controller: `POST /stock_barcode_rfid/scan` endpoint
- [ ] Session/stream mechanism (SSE or long-poll) to relay EPCs into Barcode app's `barcode_scanned` event bus
- [ ] Server-side dedup/throttle logic (Map<EPC, timestamp>, 2-second window, 50 EPCs/sec max)
- [ ] Fallback queue: buffer EPCs server-side if session is not connected
- [ ] API key authentication (Odoo API key → Android Keystore)
- [ ] Unit tests: simulate rapid EPC bursts, confirm no duplicates in stock move lines
- [ ] Rate limiting: 100 requests/min per API key

**Deliverable:**
> Manually POSTing an EPC via curl/Postman correctly increments a quantity in an open Inventory Adjustment session in the Odoo Barcode UI.

---

## Phase 3 — Android Scanning App 🔲 PENDING
**Week 3–5**

- [ ] Core scan loop with in-memory dedup (`Map<EPC, lastSeenTimestamp>`)
- [ ] RSSI-based software filtering, exposed as a tunable setting
- [ ] Batch-and-throttle logic (10 EPCs per 500ms burst to Odoo)
- [ ] Auth: Odoo API key stored in Android Keystore, device paired to specific Odoo user
- [ ] Operator UI: live unique-tag count, manual flush/sync control, connection-health indicator
- [ ] Offline queue: buffer scans locally on Wi-Fi drop, resync on reconnect (SQLite)
- [ ] Pre-encoded tag import: option to upload supplier EPC file (CSV/Excel)
- [ ] Calibration preset selector: operator can switch between zone profiles

**Deliverable:**
> Operator can walk a shelf, watch tag count climb live, and see it reflected in the Odoo Barcode Inventory Adjustment in near-real-time.

---

## Phase 4 — RFID Calibration 🔲 PENDING
**Week 5–6 (parallel to late Phase 3)**

This phase determines whether the project succeeds. RFID is only better than barcode if it's tuned correctly.

| Step | Action | Target Output |
|------|--------|---------------|
| 1 | Baseline test: max power, Session 0, Multi-label mode | Establish worst-case over-read radius |
| 2 | Step power down (`setReadWritePower`) in ~4dBm increments at real bin distance | Lowest power that still reliably reads every in-zone tag |
| 3 | Switch Session 0→1→2, re-test dupe rate per sweep | Session value minimizing redundant reads without missing tags |
| 4 | Test inventory modes: Multi-label vs Adaptive power-saving vs Fast-read | Best mode for actual scan pattern |
| 5 | RSSI-floor sweep in Android app | Threshold that cuts cross-shelf reads without cutting real ones |
| 6 | Combine best settings; A/B RFID vs manual count, 5+ trials, varied shelf densities | Documented accuracy % and time-savings % |

**Deliverable:**
> A written calibration profile (power, session, mode, RSSI floor) per shelf/zone type, baked into the Android app as selectable presets.

---

## Phase 5 — Integration Testing 🔲 PENDING
**Week 6–7**

- [ ] End-to-end test: RFID scan → Android dedup → Odoo bridge → Barcode UI → stock.quant adjustment, verified against audit trail
- [ ] Multi-user test: two devices scanning into two different sessions concurrently, no cross-talk
- [ ] Failure-mode testing: server restart mid-scan, network drop, garbage EPC, unknown EPC
- [ ] Load test: dense shelf sweep (200+ tags), no dropped scans, acceptable controller latency
- [ ] Security pass: push endpoint cannot inject arbitrary stock adjustments without valid authenticated session
- [ ] Performance targets: POST /scan <100ms p95, ≥50 EPCs/sec per session

**Deliverable:**
> Signed-off test report; known-issues list triaged into "fix before launch" vs. "acceptable for v1."

---

## Phase 6 — Pilot / UAT 🔲 PENDING
**Week 7–8**

- [ ] Run pilot on one real warehouse zone, RFID-tagged, operators trained, barcode kept as fallback
- [ ] Shadow-run: RFID counts logged but not authoritative — compare against manual counts for 3–5 working days
- [ ] Collect operator feedback on device ergonomics (T1 vs T2), scan speed, false-read incidents
- [ ] Adjust calibration profiles based on real floor conditions (always differs from Phase 4 lab tests)

**Deliverable:**
> Go/no-go decision with real accuracy numbers, not lab numbers.

---

## Phase 7 — Production Rollout 🔲 PENDING
**Week 8–10**

### Infrastructure
- [ ] Move off dev Docker Compose to production-grade setup: dedicated PostgreSQL with scheduled + offsite backups, Odoo behind Nginx/Traefik with HTTPS, resource limits on containers
- [ ] Separate staging environment mirroring production for future changes
- [ ] Odoo logs + lightweight monitoring so scan-related errors are visible, not silent

### Rollout Sequence — do not big-bang this
- Enable RFID counting in pilot zone only; barcode remains available everywhere else
- Expand zone-by-zone over 2–3 weeks, monitoring accuracy metrics each time
- Only after 2+ zones are stable, consider RFID for receiving/delivery workflows (higher-risk)

**Deliverable:**
> Production system live, monitored, with a documented rollback path (disable the bridge module, operators fall back to barcode with zero data loss).

---

## Phase 8 — Post-Launch (ongoing) 🔲 PENDING

- [ ] Weekly accuracy spot-checks for the first month, then monthly
- [ ] Firmware/SDK update process defined — test on staging device before pushing to fleet
- [ ] Tag lifecycle process: how damaged/lost tags get re-encoded and re-linked to their stock.lot
- [ ] Backlog: RFID for receiving/delivery, read-zone dashboard, multi-reader gateway support

### Future Extension: Toll/Highway RFID
- Fixed UHF portal readers at toll plazas/highway gates
- Vehicle/asset tag scanning using calibration profiles from Phase 4
- Backend integration (Odoo or separate service TBD)
- Multi-reader gateway aggregation

---

# 2. Current Status

| Phase | Status | Completion |
|-------|--------|-----------|
| 0 — Requirements Lock | ✅ Complete | 100% |
| 1 — Environment & Foundations | 🔄 In Progress | 60% |
| 2 — Odoo Bridge Module | 🔲 Pending | 0% |
| 3 — Android Scanning App | 🔲 Pending | 0% |
| 4 — RFID Calibration | 🔲 Pending | 0% |
| 5 — Integration Testing | 🔲 Pending | 0% |
| 6 — Pilot / UAT | 🔲 Pending | 0% |
| 7 — Production Rollout | 🔲 Pending | 0% |
| 8 — Post-Launch | 🔲 Pending | 0% |

**Next milestone:** Complete Phase 1 (Odoo 19 + Android "Hello World")

---

# 3. Key Decisions Log

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Odoo version | 19.0 | Latest, already deployed |
| EPC mapping | EPC → stock.lot.name | Reuse Barcode Nomenclature, minimal custom code |
| EPC encoding | Hybrid (in-house + supplier) | Flexibility for replacements + speed of pre-encoded |
| Workflow priority | Inventory Adjustments first | Lowest risk, best proving ground |
| Hardware | Zebra T1/T2 UHF handheld | Available in-house, dual warehouse/highway use |
| Tag encoder | Zebra UHF printer | In-house control over encoding |
| Architecture | Monorepo | Shared infrastructure, easy to split later |
| Dedup strategy | Client + server-side | Resilient to network retries and rapid re-scans |
| Stream mechanism | Long-poll (→ SSE in Phase 5+) | Simpler, compatible with Odoo OWL/JS |

---

# 4. References

- `ARCHITECTURE.md` — System design and data flows
- `DEVELOPMENT.md` — Dev environment, coding standards, testing
- `API_CONTRACT.md` — RFID endpoint specifications
- `SECURITY.md` — Auth, encryption, threat model
- `CONTRIBUTING.md` — Contribution workflow and code review checklist
- `IDataProject-Phase0-Decisions.md` — Phase 0 sign-off document
- `docker-compose.yml` — Local development environment
- [Spider's RFID — Odoo Integration Best Practices](https://www.spidersrfid.com/en/articles/rfid-odoo-integration-best-practices) — Additional implementation guidance for RFID/Odoo integration best practices
