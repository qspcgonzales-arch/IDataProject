# IDataProject — System Architecture

**Goal:** Replace warehouse barcode scanning with UHF RFID (Zebra T1/T2), integrated into Odoo stock_barcode. Extensible to toll/highway asset tracking.

**Stack:** 
- Backend: Odoo 19.0 (Python, PostgreSQL)
- Frontend: Odoo Barcode App (OWL/JS)
- Mobile: Zebra T1/T2 UHF handheld + custom Android app (Kotlin)
- Deployment: Docker Compose (dev), production-grade setup (Phase 7)

---

## System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Odoo 19 Backend                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  stock_barcode_rfid Module (Custom)                  │   │
│  │  ┌─────────────────────────────────────────────────┐ │   │
│  │  │ POST /stock_barcode_rfid/scan                   │ │   │
│  │  │ - Accepts EPC from Android app                  │ │   │
│  │  │ - Server-side dedup (Map<EPC, timestamp>)       │ │   │
│  │  │ - Throttle rapid bursts                         │ │   │
│  │  │ - Queue if no active session, retry on connect  │ │   │
│  │  └─────────────────────────────────────────────────┘ │   │
│  │                                                         │   │
│  │  ┌─────────────────────────────────────────────────┐ │   │
│  │  │ SSE/Long-Poll Stream to Barcode UI               │ │   │
│  │  │ - Relay dedup'd EPC as barcode_scanned event    │ │   │
│  │  │ - Keep session alive during operator's scan     │ │   │
│  │  │ - Handle reconnect gracefully                   │ │   │
│  │  └─────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  stock_barcode (Native Odoo App)                      │   │
│  │  - Inventory Adjustments workflow                     │   │
│  │  - Receives EPC as if barcode scan                    │   │
│  │  - Updates stock.move_line.qty_done                   │   │
│  │  - Validates EPC against Barcode Nomenclature rule    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Database (PostgreSQL)                                │   │
│  │  - stock.lot (EPC → lot.name mapping)                │   │
│  │  - stock.quant (inventory quantities)                 │   │
│  │  - stock.move_line (audit trail)                      │   │
│  │  - ir.attachment (calibration profiles)               │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ HTTP/HTTPS
                            │
┌─────────────────────────────────────────────────────────────┐
│             Zebra T1/T2 (Android Handheld)                  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  rfid-scanner-android (Kotlin App)                   │   │
│  │  ┌─────────────────────────────────────────────────┐ │   │
│  │  │ Zebra UHF Reader Integration                    │ │   │
│  │  │ - Continuous scan loop (in-memory dedup)        │ │   │
│  │  │ - RSSI-based software filtering                 │ │   │
│  │  │ - Batch-and-throttle EPC bursts                 │ │   │
│  │  │ - Offline queue (Wi-Fi drop resilience)         │ │   │
│  │  └─────────────────────────────────────────────────┘ │   │
│  │                                                        │   │
│  │  ┌─────────────────────────────────────────────────┐ │   │
│  │  │ Operator UI                                      │ │   │
│  │  │ - Live unique-tag count                         │ │   │
│  │  │ - Connection health indicator                   │ │   │
│  │  │ - Manual flush/sync control                     │ │   │
│  │  │ - Configurable calibration presets              │ │   │
│  │  └─────────────────────────────────────────────────┘ │   │
│  │                                                        │   │
│  │  ┌─────────────────────────────────────────────────┐ │   │
│  │  │ Secure Auth & Storage                            │ │   │
│  │  │ - Odoo API key in Android Keystore               │ │   │
│  │  │ - Device paired to Odoo user                     │ │   │
│  │  │ - TLS pinning for API calls                      │ │   │
│  │  └─────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Inventory Adjustment Workflow

1. **Operator** opens Inventory Adjustment in Odoo Barcode app
2. **Operator** starts scanning with Zebra T1/T2
3. **Android app:**
   - Reads UHF tag (EPC) via Zebra UHF SDK
   - Dedup locally (Map<EPC, lastSeenTimestamp>)
   - Filter by RSSI threshold (configured)
   - Batch into burst (e.g., 10 EPCs per 500ms)
   - POST to Odoo: `POST /stock_barcode_rfid/scan` with `{barcode: EPC, session_id: ...}`
4. **Odoo backend:**
   - Receives EPC at `/stock_barcode_rfid/scan` endpoint
   - Server-side dedup (check recent scans, ignore duplicates)
   - Throttle if burst exceeds rate limit
   - Queue if operator's session isn't active yet
   - Relay EPC as synthetic barcode_scanned event via SSE/long-poll
5. **Odoo Barcode UI:**
   - Receives barcode_scanned event
   - Looks up EPC in stock.lot via Barcode Nomenclature rule
   - Increments qty_done in active stock.move_line
   - Updates UI count in real-time
6. **Operator** finishes scanning zone, submits Inventory Adjustment
7. **Odoo** records stock.quant adjustment + full audit trail in stock.move_line

---

## Key Design Decisions

### 1. EPC → stock.lot.name Mapping
**Why:** Odoo's Barcode Nomenclature rules already handle barcode → lot lookup. We reuse the same pipeline.
- Configure rule: EPC pattern (e.g., `^(.{24})$` for 96-bit hex EPC) → Rule Type = Lot/Serial Number
- On first scan, if EPC not in stock.lot, auto-create (or manual import)
- No custom lookup logic; leverages battle-tested Odoo validation

### 2. Server-Side Dedup + Throttle
**Why:** Android app's local dedup is best-effort. Network retries, rapid re-scan during operator motion, or late arrivals can duplicate. Server must enforce dedup.
- Track scans in a temporary cache (Redis or in-memory, 5-min TTL)
- If EPC seen in last 2sec, reject as duplicate
- Throttle: max 50 EPCs/sec per session (adjust per Odoo load testing)
- Queue overflow: buffer in database, retry on next connection

### 3. SSE vs Long-Poll
**Decision:** Start with **long-poll** (simpler, compatible with Odoo's OWL/JS). Upgrade to SSE in Phase 5+ if latency becomes critical.
- Long-poll: Android POST → Odoo accepts + responds immediately with dedup'd EPCs
- Barcode UI long-polls on fixed interval (500ms) for new scans
- Trade-off: ~500ms latency vs. real-time, but acceptable for warehouse speed

### 4. Offline Queue
**Why:** Warehouse Wi-Fi can drop briefly. Don't lose scans.
- Android SQLite buffer: store EPCs locally if POST fails
- On reconnect, bulk-POST buffered EPCs with replay flag
- Odoo dedup handles replay (same EPC in buffer gets deduplicated)

### 5. Calibration Profiles as Odoo Attachments
**Why:** Profiles (power, session, RSSI floor) are environment-specific. Store in Odoo so:
- Operators download profiles to Android on login
- Profiles update across the fleet instantly (no manual device updates)
- Audit trail of which profile was used for each count

---

## Phases & Deliverables

| Phase | Duration | Deliverable | Stability |
|-------|----------|-------------|-----------|
| 0 | Week 1 | Requirements locked (this doc) | — |
| 1 | Week 1–2 | "Hello World" (EPC → Odoo lot resolution) | Alpha |
| 2 | Week 2–3 | Odoo bridge module (POST endpoint + dedup) | Alpha |
| 3 | Week 3–5 | Android scanner app (UHF loop + UI) | Beta |
| 4 | Week 5–6 | Calibration profiles (power, session, RSSI) | Beta |
| 5 | Week 6–7 | Integration tests (E2E, multi-user, failure modes) | Release Candidate |
| 6 | Week 7–8 | Pilot/UAT (shadow-run on real zone) | Release Candidate |
| 7 | Week 8–10 | Production rollout (zone-by-zone, monitoring) | Production |
| 8 | Ongoing | Post-launch (weekly accuracy checks, firmware updates) | Stable |

---

## Success Metrics

- **Accuracy:** ≥99% in calibrated read zone (Phase 4)
- **Speed:** 60–70% faster than barcode scanning (Phase 6 UAT measurement)
- **Stability:** <0.1% scan loss on live operator workflow (Phase 5 load test)
- **Uptime:** 99.5% during warehouse hours (Phase 7 monitoring)
- **Extensibility:** Support for toll/highway asset tracking without core changes (Phase 8)

---

## Technology Choices & Trade-offs

| Aspect | Choice | Why | Trade-off |
|--------|--------|-----|-----------|
| Odoo Version | 19.0 | Latest, improved stock_barcode | Newer = less field battle-testing |
| EPC Mapping | stock.lot.name | Reuse Barcode Nomenclature | Less flexible if EPC ≠ lot semantically |
| Dedup Strategy | Server-side + client | Resilient to network/retry | ~500ms latency (long-poll) |
| Android Dev | Kotlin + Gradle | Type-safe, Google standard | Smaller ecosystem than Java |
| Encoding | In-house + supplier hybrid | Flexible long-term | Must manage EPC prefix collisions |
| Scaling | Single Odoo instance (Phase 1-6) | Simpler deployment | Bottleneck for multi-zone scaling (Phase 8) |

---

## Future Extensions (Phase 8+)

- **Multi-reader gateway:** Aggregate data from multiple T1/T2 units into one stream
- **Receiving/Delivery workflows:** High-risk, requires stock move locking
- **Toll/Highway integration:** Fixed portal readers, vehicle plate capture, audit triggers
- **Real-time dashboard:** Zone-level scan counts, accuracy heatmaps
- **Firmware auto-update:** Push Zebra firmware updates to fleet via Odoo
- **Tag lifecycle:** Damaged/lost tag replacement, re-encoding workflow

---

## Assumptions & Constraints

- Warehouse Wi-Fi is stable (≥3 bars in scan zones)
- EPC structure encodes lot identity (or manual mapping table)
- Odoo barcode_scanned event model remains stable across 19.x patches
- Zebra T1/T2 Android SDK is available (sourced from Zebra portal)
- Initial single-zone pilot (scale horizontally in Phase 7)
- No multi-warehouse federation in Phase 1 (single Odoo instance)
