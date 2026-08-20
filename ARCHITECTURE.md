# IDataProject — System Architecture

**Goal:** Replace warehouse barcode scanning with UHF RFID (iData T1UHF / Zebra T1/T2), integrated into Odoo stock_barcode. Extensible to toll/highway asset tracking.

**Stack:** 
- Backend: Odoo 19.0 (Python, PostgreSQL)
- Frontend: Odoo Barcode App (OWL/JS)
- Mobile: iData T1UHF (primary) / Zebra T1/T2 (fallback) UHF handheld + custom Android app (Kotlin)
- Deployment: Docker Compose (dev), production-grade setup (post-pilot Phase 7)

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
│  │  - Resolves EPC via rfid.tag.mapping model            │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Database (PostgreSQL)                                │   │
│  │  - rfid.tag.mapping (EPC → product/lot mapping)       │   │
│  │  - stock.barcode.rfid.scan (audit log)                │   │
│  │  - stock.quant (inventory quantities)                 │   │
│  │  - stock.move_line (stock audit trail)                │   │
│  │  - rfid.calibration.profile (calibration settings)   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ HTTP/HTTPS
                            │
┌─────────────────────────────────────────────────────────────┐
│             iData T1UHF (Android Handheld)                  │
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
2. **Operator** starts scanning with iData T1UHF (or Zebra T1/T2)
3. **Android app:**
   - Reads UHF tag (EPC) via device UHF SDK
   - Dedup locally (Map<EPC, lastSeenTimestamp>)
   - Filter by RSSI threshold (configured)
   - Batch into burst (e.g., 10 EPCs per 500ms)
   - POST to Odoo: `POST /stock_barcode_rfid/scan` with `{epc: EPC, session_id: ...}`
4. **Odoo backend:**
   - Receives EPC at `/stock_barcode_rfid/scan` endpoint
   - Server-side dedup (check recent scans, ignore duplicates)
   - Throttle if burst exceeds rate limit
   - Queue if operator's session isn't active yet
   - Looks up EPC in `rfid.tag.mapping`; returns resolved/unknown status
   - Relay EPC as synthetic barcode_scanned event via SSE/long-poll
5. **Odoo Barcode UI:**
   - Receives barcode_scanned event
   - Resolves product/lot via `rfid.tag.mapping` (not Barcode Nomenclature)
   - Increments qty_done in active stock.move_line
   - Updates UI count in real-time
6. **Operator** finishes scanning zone, submits Inventory Adjustment
7. **Odoo** records stock.quant adjustment + full audit trail in stock.move_line

---

## Key Design Decisions

### 1. EPC → Product/Lot Mapping via `rfid.tag.mapping`
**Why:** Barcode Nomenclature alone is insufficient — it handles only one EPC-encoding scenario. The warehouse requires three distinct mapping paths depending on how tags were encoded.

Three supported scenarios (Ventor reference):
1. **Supplier tags** — EPC matches `product.barcode` directly; create mapping on first scan.
2. **In-house encoded tags** — Your team writes the product barcode into the EPC; resolved via `rfid.tag.mapping.barcode`.
3. **Non-standard EPC** — Proprietary supplier encoding; operator maps raw EPC to `product.serial_number` manually; future scans resolve via serial.

Unknown EPCs are flagged as `status='unknown'`; the operator can self-map them via the discrepancy workflow (no tech support needed).

Model: `rfid.tag.mapping` with fields `epc`, `product_id`, `lot_id`, `barcode`, `serial_number`, `encoding_type` (supplier | in_house | non_standard), timestamps, and scan count.

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

### 5. Calibration Profiles as Odoo ORM Model (`rfid.calibration.profile`)
**Why:** Profiles (power, session, RSSI floor, Q-value) are environment-specific. Storing them as a structured ORM model (not `ir.attachment`) provides:
- Full CRUD API endpoints for Android to fetch and apply profiles
- Operators select profiles via a dropdown in the Android app
- Profiles update across the fleet instantly (no manual device updates)
- Audit trail of which profile was used for each count

Fields: `name` (unique), `power_dbm`, `session`, `rssi_floor`, `q_value`, `zone`, timestamps.

---

## Tracker-Aligned Milestones

The tracker sheet (`TRACKER_UPDATED.txt`) is the source of truth for execution status. The implementation is organized into date-based windows rather than numbered phases. The table below maps the original phase concepts to the tracker schedule.

| Tracker Window | Deliverable | Stability |
|----------------|-------------|-----------|
| Aug 19–20 (complete) | Requirements locked, hardware selected | — |
| Aug 24–28 | Odoo foundation, module scaffold, Android base, SDK validation | Alpha |
| Aug 31–Sep 10 | Odoo scan bridge (`POST /scan`, dedup, auth, live UI) | Alpha |
| Sep 11–18 | Live RFID read loop, Android live count, smoke tests | Beta |
| Sep 21–30 | Offline handling, calibration profiles, accuracy testing | Beta |
| Oct 1–16 | Final calibration, E2E tests, warehouse pilot, UAT, go/no-go | Release Candidate |

**Phase 7 (Production Rollout) is out of scope for this pilot project** — it is deferred to a separate project after UAT sign-off.

See [ROADMAP_UPDATED.md](ROADMAP_UPDATED.md) for the full date-based tracker-aligned roadmap.

---

## Success Metrics

- **Accuracy:** ≥99% in calibrated read zone (Sep–Oct calibration)
- **Speed:** 60–70% faster than barcode scanning (Oct UAT measurement)
- **Stability:** <0.1% scan loss on live operator workflow (Oct load test)
- **Uptime:** 99.5% during warehouse hours (pilot monitoring)
- **Extensibility:** Support for toll/highway asset tracking without core changes (post-pilot)

---

## Technology Choices & Trade-offs

| Aspect | Choice | Why | Trade-off |
|--------|--------|-----|-----------|
| Odoo Version | 19.0 | Latest, improved stock_barcode | Newer = less field battle-testing |
| EPC Mapping | rfid.tag.mapping model | 3-scenario approach (supplier/in-house/non-standard) | Requires explicit mapping management |
| Dedup Strategy | Server-side + client | Resilient to network/retry | ~500ms latency (long-poll) |
| Android Dev | Kotlin + Gradle | Type-safe, Google standard | Smaller ecosystem than Java |
| Encoding | In-house + supplier hybrid | Flexible long-term | Must manage EPC prefix collisions |
| Scaling | Single Odoo instance (pilot scope) | Simpler deployment | Bottleneck for multi-zone scaling (post-pilot) |

---

## Future Extensions (Post-Pilot)

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
- iData T1UHF (primary) or Zebra T1/T2 Android SDK is available (sourced from device vendor portal)
- Initial single-zone pilot (scale horizontally post-pilot)
- No multi-warehouse federation in pilot scope (single Odoo instance)
