# IDataProject — API Contract

**Version:** 1.0.0  
**Status:** In development (Aug 31 – Sep 10 tracker window)  
**Base URL:** `https://<odoo-host>/stock_barcode_rfid/` (or `http://localhost:8069` for local dev)

---

## Overview

The `stock_barcode_rfid` module exposes REST endpoints for:
1. **RFID scan ingestion** — Android app sends EPCs → Odoo processes them
2. **Tag mapping management** — Create/update EPC→product mappings (3 Ventor scenarios)
3. **Session management** — Create/track operator scan sessions
4. **Calibration profile CRUD** — Android fetches and applies tuned hardware settings (Sep 21–30 calibration block)

All endpoints require **authentication** (Odoo session + API key) and return JSON.

---

## Authentication

Two mechanisms:

### 1. Odoo Session (Browser/Cookie-based)
```
GET /web/login
POST /web/session/authenticate
```
Standard Odoo login. Used by Barcode UI webapp.

### 2. API Key (for Android app)
```
Authorization: Bearer <ODOO_API_KEY>
```
- API key generated in Odoo Settings → Users, stored in Android Keystore
- Must validate on every request
- Rate-limit per key: 100 requests/min (configurable)

---

## Endpoints

### 1. POST /stock_barcode_rfid/scan

**Purpose:** Submit a scan (EPC) from Android app into active Inventory Adjustment session.

**Request:**
```json
{
  "epc": "1234567890ABCDEF12345678",
  "session_id": "barcode_session_abc123",
  "rssi": -65,
  "timestamp_ms": 1692374400000,
  "device_id": "zebra_t1_serial_abc"
}
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `epc` | string | ✓ | 96-bit EPC in hex format (24 chars) |
| `session_id` | string | ✓ | Barcode app session ID (link to stock.barcode_session) |
| `rssi` | integer | ✓ | Signal strength in dBm (e.g., -65) |
| `timestamp_ms` | integer | — | Client-side timestamp for replay ordering |
| `device_id` | string | — | Device serial, for audit trail |

**Response (200 OK):**
```json
{
  "success": true,
  "scan_id": "stock.barcode.rfid.scan_12345",
  "tag_mapping_id": 42,
  "product_id": 101,
  "product_name": "Widget A",
  "lot_id": 789,
  "lot_name": "LOT-2024-08-001",
  "is_duplicate": false,
  "scan_status": "resolved",
  "relay_status": "queued",
  "message": "EPC accepted, relaying to Barcode app"
}
```

| Field | Notes |
|-------|-------|
| `success` | Always true if 200 OK |
| `scan_id` | Internal audit record ID |
| `tag_mapping_id` | ID of the matched `rfid.tag.mapping` record, or null if unknown |
| `product_id` | Resolved product.id, or null if EPC unknown |
| `product_name` | Human-readable product name, or null |
| `lot_id` | Resolved lot.id, or null (only present when lot-tracked product) |
| `lot_name` | Human-readable lot identifier, or null |
| `is_duplicate` | True if this EPC was seen <2sec ago (server-side dedup) |
| `scan_status` | `resolved` (EPC mapped to product), `unknown` (no mapping found — operator must map) |
| `relay_status` | `queued` (waiting for active session), `relayed` (session active), `buffered` (no session) |

**Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "Invalid EPC format",
  "details": "EPC must be 24 hex characters, got: 1234"
}
```

**Response (401 Unauthorized):**
```json
{
  "success": false,
  "error": "Invalid API key",
  "details": "API key is expired or invalid"
}
```

**Response (429 Too Many Requests):**
```json
{
  "success": false,
  "error": "Rate limit exceeded",
  "details": "Max 100 requests/min per API key. Retry after 30 sec"
}
```

**Behavior:**
- Server-side dedup: if EPC seen in same session <2sec, return `is_duplicate: true` but still process
- EPC lookup: resolve via `rfid.tag.mapping` model; returns `scan_status: 'unknown'` if no mapping found
- Unknown EPC workflow: operator copies EPC, maps it via `PUT /tag_mapping/{id}`, then rescans → resolved
- If no active Barcode app session: buffer the scan in database, don't fail
- Relay: if session active, emit `barcode_scanned` event to trigger qty increment in UI

**Rate Limiting:**
- Default: 100 EPCs/min per API key per session
- Configurable in Odoo settings (Sep 2 — auth implementation day)
- If exceeded: 429 response, back off exponentially (Android app built-in)

---

### 2. POST /stock_barcode_rfid/session/create

**Purpose:** Create a new RFID scan session (optional, called by Android when operator starts counting).

**Request:**
```json
{
  "barcode_session_id": "barcode_session_xyz789",
  "warehouse_id": 1,
  "picking_type_id": 4,
  "operator_user_id": 42,
  "calibration_profile": "zone_a_shelf_dense"
}
```

| Field | Notes |
|-------|-------|
| `barcode_session_id` | ID of active Odoo Barcode session (from Barcode app) |
| `warehouse_id` | Warehouse where scanning happens |
| `picking_type_id` | Type of operation (4 = Inventory Adjustments) |
| `operator_user_id` | Odoo user performing the scan |
| `calibration_profile` | Profile name to use (e.g., "zone_a_shelf_dense") |

**Response (201 Created):**
```json
{
  "success": true,
  "rfid_session_id": "rfid_session_abc123",
  "calibration_profile": {
    "name": "zone_a_shelf_dense",
    "power_dbm": 28,
    "session": 1,
    "rssi_floor": -68
  },
  "message": "Session created, operator can start scanning"
}
```

**Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "Invalid barcode session",
  "details": "Barcode session xyz789 not found or inactive"
}
```

**Behavior:**
- Optional endpoint — can also omit and scans are queued until Barcode app session is active
- Creates audit trail linking RFID scans to operator + workflow context
- Downloads calibration profile for this zone/operator

---

### 3. GET /stock_barcode_rfid/session/{rfid_session_id}/stream

**Purpose:** SSE (Server-Sent Events) stream for real-time EPC relay to Barcode app.

**Request:**
```
GET /stock_barcode_rfid/session/rfid_session_abc123/stream
Authorization: Bearer <ODOO_API_KEY>
Accept: text/event-stream
```

**Response (200 OK, streaming):**
```
data: {"event": "barcode_scanned", "epc": "1234567890ABCDEF12345678", "product_id": 101, "lot_id": 789, "scan_status": "resolved", "is_duplicate": false}
data: {"event": "session_status", "status": "active", "tag_count": 42}
data: {"event": "error", "message": "Connection from Android app lost, buffering scans"}
```

**Behavior:**
- Keeps connection open, streams EPC events as they arrive
- Barcode app subscribes to this stream
- On Android disconnect: server buffers EPCs, retries relaying when Android reconnects
- Every 30sec: send keepalive `{"event": "ping"}` to detect stale connections
- On stream close: Android app falls back to long-poll (below)

---

### 4. POST /stock_barcode_rfid/session/{rfid_session_id}/poll

**Purpose:** Alternative to SSE — long-poll for EPC relay (better compatibility).

**Request:**
```json
{
  "timeout_sec": 30,
  "last_scan_id": "stock.barcode.rfid_12344"
}
```

| Field | Notes |
|-------|-------|
| `timeout_sec` | Wait up to 30sec for new events; return immediately if events exist |
| `last_scan_id` | Return only scans after this ID (for pagination) |

**Response (200 OK):**
```json
{
  "success": true,
  "events": [
    {
      "event": "barcode_scanned",
      "epc": "1234567890ABCDEF12345678",
      "product_id": 101,
      "lot_id": 789,
      "scan_status": "resolved",
      "scan_id": "stock.barcode.rfid.scan_12345"
    },
    {
      "event": "barcode_scanned",
      "epc": "ABCDEF1234567890ABCDEF12",
      "product_id": 101,
      "lot_id": 790,
      "scan_status": "resolved",
      "scan_id": "stock.barcode.rfid.scan_12346"
    }
  ]
}
```

**Behavior:**
- Long-poll: POST every 1-2 sec, waits for up to 30sec for new events
- Returns immediately if ≥1 new event, or after timeout if none
- Barcode app processes events and increments qty in UI
- Fallback when SSE is unavailable (Android compatibility)

---

### 5. GET /stock_barcode_rfid/calibration/profiles

**Purpose:** List available calibration profiles for this warehouse/zone.

**Request:**
```
GET /stock_barcode_rfid/calibration/profiles?warehouse_id=1
Authorization: Bearer <ODOO_API_KEY>
```

**Response (200 OK):**
```json
{
  "success": true,
  "profiles": [
    {
      "name": "zone_a_shelf_dense",
      "zone": "Zone A",
      "shelf_density": "dense",
      "power_dbm": 28,
      "session": 1,
      "rssi_floor": -68,
      "description": "High-density shelf, tested 2024-08-15"
    },
    {
      "name": "zone_b_shelf_sparse",
      "zone": "Zone B",
      "shelf_density": "sparse",
      "power_dbm": 20,
      "session": 0,
      "rssi_floor": -65,
      "description": "Open bins, minimal interference"
    }
  ]
}
```

**Behavior:**
- Returns all active profiles for the warehouse
- Android app displays to operator for manual selection
- Profile includes RFID hardware tuning (power, session, RSSI floor, Q-value)

---

### 6. POST /stock_barcode_rfid/calibration/profiles

**Purpose:** Create a calibration profile (admin only, Sep 21–30).

**Request:**
```json
{
  "name": "zone_c_shelf_metal",
  "zone": "Zone C",
  "shelf_density": "dense_metal",
  "power_dbm": 30,
  "session": 2,
  "rssi_floor": -70,
  "q_value": 5,
  "description": "Metal shelving, high RF interference"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "profile_id": 567,
  "message": "Profile created. Download to devices via app settings."
}
```

**Behavior:**
- Admin/warehouse manager creates profiles after Sep 29–30 calibration steps
- Profiles stored in `rfid.calibration.profile` ORM model
- Android app polls for new profiles on app startup

---

### 7. PUT /stock_barcode_rfid/calibration/profiles/{id}

**Purpose:** Update an existing calibration profile (admin only).

**Request:**
```json
{
  "power_dbm": 27,
  "rssi_floor": -65
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "profile_id": 567,
  "message": "Profile updated."
}
```

---

### 8. DELETE /stock_barcode_rfid/calibration/profiles/{id}

**Purpose:** Remove a calibration profile (admin only).

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Profile deleted."
}
```

---

### 9. POST /stock_barcode_rfid/tag_mapping

**Purpose:** Create an EPC→product mapping (Scenario 1: supplier tags / Scenario 2: in-house encoded). Available from Aug 31 (Scan Bridge block).

**Request:**
```json
{
  "epc": "1234567890ABCDEF12345678",
  "product_id": 101,
  "encoding_type": "supplier"
}
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `epc` | string | ✓ | 24-char hex EPC |
| `product_id` | integer | ✓ | Odoo product.product ID |
| `encoding_type` | string | ✓ | `supplier`, `in_house`, or `non_standard` |
| `lot_id` | integer | — | Optional lot linkage |

**Response (201 Created):**
```json
{
  "success": true,
  "tag_mapping_id": 42,
  "message": "EPC mapped to product."
}
```

---

### 10. POST /stock_barcode_rfid/write_tags

**Purpose:** Batch-create EPC mappings for in-house encoding (Scenario 2). Available from Aug 31 (Scan Bridge block).

**Request:**
```json
{
  "product_id": 101,
  "epc_list": [
    "1234567890ABCDEF12345678",
    "ABCDEF1234567890ABCDEF12"
  ]
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "written_count": 2,
  "failed_count": 0,
  "tag_mapping_ids": [42, 43]
}
```

**Behavior:**
- Product must have a barcode set in Odoo; returns 400 if missing
- Creates one `rfid.tag.mapping` record per EPC

---

### 11. PUT /stock_barcode_rfid/tag_mapping/{id}

**Purpose:** Update a tag mapping — used for Scenario 3 (non-standard EPC) and the unknown-EPC discrepancy workflow. Available from Aug 31 (Scan Bridge block).

**Request:**
```json
{
  "serial_number": "SN-PROPRIETARY-ABC",
  "encoding_type": "non_standard"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "tag_mapping_id": 42,
  "message": "Mapping updated. Rescan tag to resolve."
}
```

**Behavior:**
- Operator maps an unknown EPC to a product serial number
- After this call, rescanning the same EPC returns `scan_status: 'resolved'`

---

## Error Handling

All errors return JSON with `success: false`:

| HTTP Code | Error Type | Retry? | Example |
|-----------|-----------|--------|---------|
| 400 | Invalid request | No | Bad EPC format, missing required field |
| 401 | Unauthorized | No | Expired API key, invalid session |
| 429 | Rate limit | Yes | Exponential backoff (1s, 2s, 4s, ...) |
| 500 | Server error | Yes | Database connection lost, Odoo crashed |
| 503 | Service unavailable | Yes | Odoo under maintenance |

**Client behavior:**
- 4xx errors: log and discard
- 5xx/429 errors: buffer scan locally, retry on next connection attempt

---

## Data Types

### EPC Format
- **96-bit EPC** (most common): 24 hex characters (case-insensitive internally, normalize to uppercase)
- Example: `1234567890ABCDEF12345678`
- Validation: must be hex-decodable, exactly 24 chars

### Session IDs
- Barcode app session: `barcode_session_<uuid>`
- RFID session: `rfid_session_<uuid>`

### Timestamps
- Milliseconds since epoch (JavaScript-compatible)
- Server adjusts for clock skew

### RSSI
- Range: -100 to 0 dBm (higher = stronger signal)
- Typical warehouse: -50 to -75 dBm

---

## Backwards Compatibility

**Current pilot scope (Aug–Oct):** Single-zone, single-reader, single-operator  
**Post-pilot (post-pilot production rollout):** Multi-reader, multi-operator concurrent scanning  

Future changes will increment API version:
- `/v2/stock_barcode_rfid/...` for multi-reader gateway support
- Legacy v1 endpoints remain functional for 2+ releases (graceful deprecation)

---

## Security Considerations

1. **API Key rotation:** Keys expire every 90 days, operator prompted to re-generate
2. **HTTPS only:** All prod traffic encrypted TLS 1.2+
3. **Rate limiting:** Prevents brute-force, DoS
4. **Input validation:** EPC format, session ID format, rssi range
5. **Audit trail:** Every scan logged with operator, device, timestamp, result
6. **No secrets in logs:** API keys, user IDs redacted in debug output

See `SECURITY.md` for details.

---

## Testing

**Mock the endpoints locally:**
```bash
curl -X POST http://localhost:8069/stock_barcode_rfid/scan \
  -H "Authorization: Bearer test_key_abc" \
  -H "Content-Type: application/json" \
  -d '{
    "epc": "1234567890ABCDEF12345678",
    "session_id": "barcode_session_test",
    "rssi": -65
  }'
```

**Postman collection:**
See `tests/postman_collection.json` for full endpoint test suite.

**Pytest integration tests:**
```bash
cd backend
python -m pytest tests/test_rfid_bridge_e2e.py::test_epc_to_lot_mapping -v
```
