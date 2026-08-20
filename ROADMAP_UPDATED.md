# IDataProject — Updated Project Roadmap
**RFID-Odoo Integration** | **Reference: Ventor RFID Guide**  
**Last Updated:** 2026-08-19  
**Scope Adjustment:** Inventory Adjustments only (pilot phase)  
**Timeline Revision:** 2-month validated pilot (NOT 8-week production-ready)

---

## Executive Summary

**Original Goal:** Build warehouse RFID scanning for Odoo 19, supporting multiple workflows (receiving, delivery, inventory adjustments), with 8 phases ending in production rollout.

**Revised Goal:** Build and validate an Odoo 19 Community RFID Inventory Adjustment workflow using iData T1UHF, including:
- EPC mapping (3 scenarios: supplier-provided, self-encoded, non-standard)
- Offline-safe scan recording
- Discrepancy handling for unknown EPCs
- RFID calibration (power, RSSI)
- Controlled warehouse pilot

**Feasibility:** ✅ Credible 2-month target (vs. 8-week production rollout)  
**Risk:** Hardware validation (Week 1 blocker)

---

## Phase Structure (Revised)

| Phase | Duration | Deliverable | Dependency | Status |
|-------|----------|-------------|-----------|--------|
| **0** | Complete | Requirements locked | — | ✅ Done |
| **1** | Week 1-2 | Hardware validation + Odoo setup | T1UHF SDK confirmation | 🔲 Next |
| **2** | Week 2-3 | Core RFID module (EPC mapping, dedup) | Phase 1 success | 🔲 Pending |
| **3** | Week 3-4 | Android scanner app (UHF + UI) | Phase 2 API stable | 🔲 Pending |
| **4** | Week 4-5 | Calibration profiles + tag enrollment | Phase 3 app working | 🔲 Pending |
| **5** | Week 5-6 | E2E integration + offline handling | Phases 2-4 complete | 🔲 Pending |
| **6** | Week 6-8 | Pilot/UAT + refinement | Phase 5 stable | 🔲 Pending |

**Production rollout:** NOT in scope; defer to Phase 7 (after pilot validation)

---

## Week-by-Week Detailed Plan

### **Week 1: Hardware Validation + Odoo Foundation** 🔴 CRITICAL

**Why first?** If iData T1UHF doesn't work, entire roadmap shifts. De-risk immediately.

#### **Day 1-2: Hardware Spike**
```
BLOCKERS MUST BE RESOLVED:
[ ] T1UHF SDK available (request from iData/Zebra)
[ ] SDK supports Android 13+ (confirmed)
[ ] SDK provides raw EPC reads (confirmed)
[ ] Power/session/Q-value control (confirmed)
[ ] RSSI or equivalent filtering (confirmed)
[ ] Network connectivity (test on site)

RISK: If ANY of the above fails, pivot to:
  - Alternative hardware (Zebra TC77/TC78)
  - Or defer Android to use mocked RFID in Phase 2
```

#### **Day 3: Odoo 19 Setup + Module Scaffold**
```bash
# Docker Compose: Get Odoo 19 + PostgreSQL running
docker-compose up -d

# Verify modules load
odoo shell

# Create module scaffold
mkdir -p backend/stock_barcode_rfid/{models,controllers,views,tests,data}
```

**Output:** Odoo running at localhost:8069, module structure ready

#### **Day 4-5: Data Model Design + Core Fixtures**

**NEW Model: `rfid.tag.mapping`** (Not Barcode Nomenclature)
```python
# models/rfid_tag_mapping.py

class RFIDTagMapping(models.Model):
    _name = 'rfid.tag.mapping'
    _description = 'RFID Tag → Product Mapping'
    _order = 'created_at DESC'

    # Core fields
    epc = fields.Char('EPC Code', required=True, unique=True, index=True)
    
    # Mapping targets (support all 3 Ventor scenarios)
    product_id = fields.Many2one('product.product', 'Product', required=True)
    lot_id = fields.Many2one('stock.lot', 'Lot/Serial (Optional)')
    barcode = fields.Char('Associated Barcode', help='EAN-13/14')
    serial_number = fields.Char('Serial Number (Non-Standard EPC)')
    
    # Metadata
    encoding_type = fields.Selection([
        ('supplier', 'Supplier Pre-Encoded'),
        ('in_house', 'In-House Encoded'),
        ('non_standard', 'Non-Standard EPC'),
    ], required=True)
    
    # Timestamps
    created_at = fields.Datetime('First Scanned', default=lambda self: fields.Datetime.now())
    last_scanned = fields.Datetime('Last Scanned', default=lambda self: fields.Datetime.now())
    scan_count = fields.Integer('Total Scans', default=0)
    
    # Status
    active = fields.Boolean('Active', default=True)
    notes = fields.Text('Mapping Notes')

    # Validation
    @api.constrains('epc')
    def _validate_epc_format(self):
        for record in self:
            if not self._is_valid_epc(record.epc):
                raise ValidationError(f"Invalid EPC: {record.epc}. Must be 24-char hex.")

    @staticmethod
    def _is_valid_epc(epc: str) -> bool:
        """Validate 96-bit EPC: 24 hex characters."""
        return epc and len(epc) == 24 and all(c in '0123456789ABCDEFabcdef' for c in epc)
```

**Audit Log Model: `stock.barcode.rfid.scan`**
```python
# models/stock_barcode_rfid_scan.py

class StockBarcodeRFIDScan(models.Model):
    _name = 'stock.barcode.rfid.scan'
    _description = 'RFID Scan Event'
    _order = 'created_at DESC'

    # Core event data
    epc = fields.Char('EPC Code', required=True, index=True)
    rssi = fields.Integer('Signal Strength (dBm)', default=-70)
    
    # Resolution
    tag_mapping_id = fields.Many2one('rfid.tag.mapping', 'Tag Mapping', readonly=True)
    product_id = fields.Many2one('product.product', 'Resolved Product', readonly=True)
    lot_id = fields.Many2one('stock.lot', 'Resolved Lot', readonly=True)
    
    # Inventory adjustment context
    inventory_id = fields.Many2one('stock.inventory', 'Inventory Adjustment', required=True)
    session_id = fields.Char('Scan Session', required=True)
    
    # Dedup flag
    is_duplicate = fields.Boolean('Server-Side Duplicate', default=False)
    
    # Status
    status = fields.Selection([
        ('resolved', 'Product Resolved'),
        ('unknown', 'Unknown EPC'),
        ('discrepancy', 'Discrepancy Found'),
    ], default='unknown', required=True)
    
    # Audit
    created_by = fields.Many2one('res.users', 'Scanned By')
    created_at = fields.Datetime('Timestamp', default=lambda self: fields.Datetime.now())
```

**Output:** Two core models ready; tests scaffolded

---

### **Week 2: Core RFID Module (POST /scan Endpoint + Dedup)**

#### **Day 6-7: Implement POST /stock_barcode_rfid/scan**

```python
# controllers/main.py

@http.route('/stock_barcode_rfid/scan', auth='bearer', type='json', methods=['POST'])
def scan(self, **kwargs):
    """
    Accept RFID scan from Android app.
    
    Corresponds to Ventor's tag scanning workflow.
    
    Request:
      {
        "epc": "1234567890ABCDEF12345678",
        "session_id": "inventory_123",
        "inventory_id": 1,
        "rssi": -65
      }
    
    Response:
      {
        "id": 123,
        "epc": "1234567890ABCDEF12345678",
        "product_id": 456,
        "lot_id": 789,
        "status": "resolved" | "unknown" | "discrepancy",
        "is_duplicate": false,
        "created_at": "2026-08-19T10:30:00"
      }
    
    Status codes:
      200: Scan accepted
      400: Invalid EPC or inventory
      401: Unauthorized
      429: Rate limited
      500: Server error
    """
    try:
        # Parse inputs
        epc = kwargs.get('epc', '').strip().upper()
        session_id = kwargs.get('session_id')
        inventory_id = kwargs.get('inventory_id')
        rssi = kwargs.get('rssi', -70)
        
        # Validate
        if not self._validate_inputs(epc, session_id, inventory_id):
            return {'error': 'Invalid input'}, 400
        
        # Check dedup (2-second window)
        is_duplicate = self._check_dedup(epc)
        
        # Resolve EPC → Product
        tag_mapping = request.env['rfid.tag.mapping'].search([('epc', '=', epc)], limit=1)
        if tag_mapping:
            product_id = tag_mapping.product_id.id
            lot_id = tag_mapping.lot_id.id if tag_mapping.lot_id else None
            status = 'resolved'
        else:
            product_id = None
            lot_id = None
            status = 'unknown'
        
        # Record scan event
        scan = request.env['stock.barcode.rfid.scan'].create({
            'epc': epc,
            'rssi': rssi,
            'session_id': session_id,
            'inventory_id': inventory_id,
            'tag_mapping_id': tag_mapping.id if tag_mapping else None,
            'product_id': product_id,
            'lot_id': lot_id,
            'status': status,
            'is_duplicate': is_duplicate,
            'created_by': request.env.user.id,
        })
        
        # Log to audit trail
        _logger.info(f"RFID Scan: EPC={epc} Inventory={inventory_id} Status={status} Dup={is_duplicate}")
        
        return {
            'id': scan.id,
            'epc': epc,
            'product_id': product_id,
            'lot_id': lot_id,
            'status': status,
            'is_duplicate': is_duplicate,
            'created_at': scan.created_at.isoformat(),
        }
    
    except Exception as e:
        _logger.error(f"Scan error: {e}", exc_info=True)
        return {'error': str(e)}, 500

@staticmethod
def _validate_inputs(epc, session_id, inventory_id):
    """Validate EPC format and required fields."""
    if not epc or len(epc) != 24:
        return False
    if not session_id or not inventory_id:
        return False
    return all(c in '0123456789ABCDEFabcdef' for c in epc)

@staticmethod
def _check_dedup(epc: str) -> bool:
    """Check if EPC seen in last 2 seconds."""
    from datetime import timedelta
    cutoff = fields.Datetime.now() - timedelta(seconds=2)
    return request.env['stock.barcode.rfid.scan'].search_count([
        ('epc', '=', epc),
        ('created_at', '>', cutoff),
    ]) > 0
```

#### **Day 8: Write Integration Tests**

```python
# tests/test_rfid_scan_endpoint.py

@pytest.mark.integration
class TestRFIDScanEndpoint:
    """Test POST /stock_barcode_rfid/scan endpoint."""
    
    def test_valid_epc_resolved(self, env, inventory, tag_mapping):
        """Valid EPC with existing mapping should resolve product."""
        response = self._post_scan(tag_mapping.epc, inventory.id)
        assert response['status'] == 'resolved'
        assert response['product_id'] == tag_mapping.product_id.id
    
    def test_unknown_epc_marked(self, env, inventory):
        """Unknown EPC should be marked as unknown, not resolved."""
        response = self._post_scan('FFFFFFFFFFFFFFFF00000001', inventory.id)
        assert response['status'] == 'unknown'
        assert response['product_id'] is None
    
    def test_dedup_within_2sec(self, env, inventory, tag_mapping):
        """Same EPC within 2 seconds marked duplicate."""
        r1 = self._post_scan(tag_mapping.epc, inventory.id)
        assert r1['is_duplicate'] == False
        
        r2 = self._post_scan(tag_mapping.epc, inventory.id)
        assert r2['is_duplicate'] == True
    
    def test_not_duplicate_after_2sec(self, env, inventory, tag_mapping):
        """Same EPC after 2+ seconds NOT marked duplicate."""
        # Use freezegun or time mock
        r1 = self._post_scan(tag_mapping.epc, inventory.id)
        assert r1['is_duplicate'] == False
        
        # Advance time 2+ seconds
        time.sleep(2.1)
        
        r2 = self._post_scan(tag_mapping.epc, inventory.id)
        assert r2['is_duplicate'] == False
    
    def _post_scan(self, epc, inventory_id):
        """Helper: POST to /scan endpoint."""
        return self.client.post(
            '/stock_barcode_rfid/scan',
            json={
                'epc': epc,
                'session_id': 'test_session_123',
                'inventory_id': inventory_id,
                'rssi': -65,
            },
            headers={'Authorization': 'Bearer test_key'},
        ).json()
```

**Output:** POST /scan working, tests passing, dedup validated

#### **Day 9-10: Implement Tag Mapping Workflows (3 Ventor Scenarios)**

**Scenario 1: Supplier Tags (Pre-Mapped)**
```python
# views/create_supplier_tag_mapping.py
# UI flow: Add barcode to product → scan tag → auto-map via barcode matching
```

**Scenario 2: Self-Encoded Tags (In-House)**
```python
# controllers/tag_enrollment.py
# POST /stock_barcode_rfid/write_tags
# Request: { product_id, epc_list }
# Response: { written_count, failed_count }
# Action: Create rfid.tag.mapping records for each EPC
```

**Scenario 3: Non-Standard EPC (Manual Mapping)**
```python
# views/rfid_tag_mapping_views.xml
# UI: Allow manual entry of EPC + Serial Number to product
# Query endpoint: GET /stock_barcode_rfid/scan/{epc}
# Shows: "Unknown EPC, add to Serial Number field"
```

**Output:** All 3 Ventor scenarios implemented and tested

---

### **Week 3: Android Scanner App (Phase 3)**

**Prerequisites:** Phase 2 API stable (Week 2 complete)

#### **Day 11-13: Zebra UHF Integration**
```kotlin
// android/app/src/main/kotlin/com/idataproject/scanner/ZebraUHFReader.kt

class ZebraUHFReader(private val context: Context) {
    private val epcsChannel = Channel<String>(Channel.BUFFERED)
    private val dedupeMap = ConcurrentHashMap<String, Long>()
    
    suspend fun startScanning() {
        // Initialize Zebra T1UHF via DataWedge or SDK
        val reader = initializeZebraReader()
        reader.setEventListener { epc, rssi ->
            handleEpc(epc, rssi)
        }
        reader.startInventory()
    }
    
    private fun handleEpc(epc: String, rssi: Int) {
        // Client-side dedup (1 sec window)
        val now = System.currentTimeMillis()
        val lastSeen = dedupeMap[epc] ?: 0L
        
        if (now - lastSeen < 1000) return
        
        dedupeMap[epc] = now
        Log.d(TAG, "EPC: $epc (RSSI: $rssi dBm)")
        
        GlobalScope.launch {
            epcsChannel.send(epc)
        }
    }
}
```

#### **Day 14: HTTP Client + Offline Queueing**
```kotlin
// android/app/src/main/kotlin/com/idataproject/network/OdooClient.kt

class OdooClient(private val apiUrl: String, private val apiKey: String) {
    
    suspend fun postScan(epc: String, inventoryId: Long, rssi: Int): ScanResponse? {
        return try {
            httpClient.post("$apiUrl/stock_barcode_rfid/scan") {
                header("Authorization", "Bearer $apiKey")
                contentType(ContentType.Application.Json)
                setBody(ScanRequest(epc, inventoryId, rssi))
            }.body()
        } catch (e: Exception) {
            Log.e(TAG, "Network error: ${e.message}")
            // Queue for retry
            queueForRetry(ScanRequest(epc, inventoryId, rssi))
            null
        }
    }
    
    private fun queueForRetry(scan: ScanRequest) {
        // Store in local SQLite database
        // Retry on network reconnect
    }
}
```

#### **Day 15: Basic UI + Session Management**
```kotlin
// android/app/src/main/kotlin/com/idataproject/ui/ScanScreen.kt

@Composable
fun ScanScreen(
    inventoryId: Long,
    viewModel: ScannerViewModel = viewModel()
) {
    var scannedCount by remember { mutableStateOf(0) }
    var lastEpc by remember { mutableStateOf("") }
    
    LaunchedEffect(Unit) {
        viewModel.epcsFlow.collect { epc ->
            val response = viewModel.postScan(epc, inventoryId)
            if (response != null) {
                scannedCount++
                lastEpc = epc
            }
        }
    }
    
    Column {
        Text("Inventory Adjustment #$inventoryId")
        Text("Scans: $scannedCount")
        Text("Last: $lastEpc")
        Button(onClick = { viewModel.stopScanning() }) {
            Text("Stop Scanning")
        }
    }
}
```

**Output:** Android app scanning and POSTing to backend

---

### **Week 4: Calibration Profiles + Tag Enrollment UI**

#### **Day 16-17: Calibration Model + Controllers**

```python
# models/rfid_calibration_profile.py

class RFIDCalibrationProfile(models.Model):
    _name = 'rfid.calibration.profile'
    _description = 'RFID Hardware Tuning Profile'
    
    name = fields.Char('Profile Name', required=True)
    power_dbm = fields.Integer('Power (dBm)', default=28, help='Zebra T1UHF: 10-30')
    session = fields.Selection([
        ('0', 'Session S0 (Gen1)'),
        ('1', 'Session S1'),
        ('2', 'Session S2'),
        ('3', 'Session S3'),
    ], default='1')
    rssi_floor_dbm = fields.Integer('RSSI Floor (dBm)', default=-68, help='Ignore weaker signals')
    q_value = fields.Integer('Q-Value', default=4, help='Tag density: 0-15')
    
    zone_id = fields.Char('Warehouse Zone', help='e.g., "Aisle 3, Shelf A"')
    description = fields.Text()
    
    # Audit
    created_at = fields.Datetime(default=lambda self: fields.Datetime.now())
    updated_at = fields.Datetime(default=lambda self: fields.Datetime.now())
    
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Profile name must be unique'),
    ]
```

**Endpoints:**
```python
# GET /stock_barcode_rfid/calibration/profiles
# POST /stock_barcode_rfid/calibration/profiles
# PUT /stock_barcode_rfid/calibration/profiles/{id}
# DELETE /stock_barcode_rfid/calibration/profiles/{id}
```

#### **Day 18: Tag Enrollment UI + Endpoint**

```python
# controllers/tag_enrollment.py

@http.route('/stock_barcode_rfid/write_tags', auth='bearer', type='json', methods=['POST'])
def write_tags(self, **kwargs):
    """
    Enroll (write) RFID tags with product barcodes.
    
    Corresponds to Ventor Scenario 2.
    
    Request:
      {
        "product_id": 123,
        "epc_list": ["1234567890ABCDEF12345678", ...],
        "encoding_type": "in_house"
      }
    
    Response:
      {
        "written_count": 5,
        "failed_count": 0,
        "mappings": [
          { "epc": "...", "product_id": 123, "status": "created" }
        ]
      }
    """
    product_id = kwargs.get('product_id')
    epc_list = kwargs.get('epc_list', [])
    encoding_type = kwargs.get('encoding_type', 'in_house')
    
    product = request.env['product.product'].browse(product_id)
    if not product.exists():
        return {'error': 'Product not found'}, 400
    
    written = []
    for epc in epc_list:
        try:
            mapping = request.env['rfid.tag.mapping'].create({
                'epc': epc,
                'product_id': product_id,
                'barcode': product.barcode,
                'encoding_type': encoding_type,
            })
            written.append({
                'epc': epc,
                'product_id': product_id,
                'status': 'created',
            })
        except Exception as e:
            _logger.error(f"Failed to write EPC {epc}: {e}")
    
    return {
        'written_count': len(written),
        'failed_count': len(epc_list) - len(written),
        'mappings': written,
    }
```

**Output:** Tag enrollment working via API + UI

---

### **Week 5: E2E Integration + Offline Handling**

#### **Day 19-20: Offline Queue + Sync**

```python
# models/stock_barcode_rfid_offline_queue.py

class RFIDOfflineQueue(models.Model):
    _name = 'stock.barcode.rfid.offline.queue'
    _description = 'Offline RFID Scan Queue'
    
    epc = fields.Char('EPC', required=True)
    inventory_id = fields.Integer('Inventory ID', required=True)
    rssi = fields.Integer('RSSI')
    
    # Status
    status = fields.Selection([
        ('pending', 'Pending Sync'),
        ('synced', 'Synced'),
        ('failed', 'Failed'),
    ], default='pending')
    
    created_at = fields.Datetime(default=lambda self: fields.Datetime.now())
    synced_at = fields.Datetime()
    error_message = fields.Text()
    
    @api.model
    def sync_pending(self):
        """Sync all pending scans to backend."""
        pending = self.search([('status', '=', 'pending')])
        for scan in pending:
            try:
                # POST to /scan endpoint
                # Mark as synced
                scan.status = 'synced'
                scan.synced_at = fields.Datetime.now()
            except Exception as e:
                scan.status = 'failed'
                scan.error_message = str(e)
```

#### **Day 21: E2E Test (Backend + Android + Inventory Adjustment)**

```python
# tests/test_e2e_inventory_adjustment.py

@pytest.mark.e2e
class TestInventoryAdjustmentRFID:
    """Full E2E test: Scan → Backend → Inventory Update."""
    
    def test_complete_workflow(self, env, warehouse, product, inventory):
        """
        1. Create inventory adjustment
        2. Map tag to product
        3. Scan tag via Android
        4. Verify scan recorded
        5. Apply adjustment
        """
        # Create tag mapping
        tag = env['rfid.tag.mapping'].create({
            'epc': '1234567890ABCDEF12345678',
            'product_id': product.id,
            'encoding_type': 'supplier',
        })
        
        # Scan via POST /stock_barcode_rfid/scan
        scan = self._post_scan(tag.epc, inventory.id)
        assert scan['status'] == 'resolved'
        assert scan['product_id'] == product.id
        
        # Verify scan recorded in audit log
        audit = env['stock.barcode.rfid.scan'].search([('epc', '=', tag.epc)])
        assert len(audit) == 1
        
        # Verify inventory adjustment can use scan
        # (This depends on how you integrate with stock.inventory model)
```

**Output:** Full end-to-end workflow tested

---

### **Week 6-8: Pilot/UAT + Refinement**

#### **Phase 6: Warehouse Pilot (2 weeks)**

**Prerequisites:** All phases 1-5 complete, tested

**Activities:**
1. Shadow warehouse operators for 2-3 days
2. Run 5-10 practice inventory adjustments with RFID
3. Collect operator feedback
4. Fix bugs/UX issues
5. Measure accuracy, speed, error rates

**Success Criteria:**
- ✅ ≥99% tag read accuracy in warehouse
- ✅ 60-70% faster counting vs. barcode
- ✅ <0.1% scan loss during 4-hour shift
- ✅ Operators can do adjustments without help
- ✅ Unknown EPCs handled via discrepancy UI

**Output:** Validated pilot, feedback, production readiness assessment

---

## Key Changes from Original Roadmap

| Item | Original | Revised | Reason |
|------|----------|---------|--------|
| **Hardware validation** | Week 5-6 (late) | Week 1 (immediate) | De-risk early; T1UHF SDK uncertain |
| **Core model** | Barcode Nomenclature | `rfid.tag.mapping` | Explicit EPC→Product mapping |
| **Scope** | Receiving + Delivery + Adjustments | Adjustments only | Simpler pilot, lower risk |
| **Tag enrollment** | Phase 4+ | Week 2-3 | Part of Phase 2 workflows |
| **Unknown EPC handling** | Not defined | Discrepancy workflow | Ventor reference |
| **Timeline** | 8 weeks → Production | 8 weeks → Validated pilot | Production deferred to Phase 7 |
| **Team size** | Parallel backend + Android | Sequential (backend first) | Solo dev constraint |

---

## Risk Register

| Risk | Impact | Mitigation | Owner |
|------|--------|-----------|-------|
| **T1UHF SDK unavailable** | 🔴 Blocker | Test Week 1; pivot to Zebra TC77 | Dev |
| **Odoo 19 API changes** | 🟡 Medium | Use LTS version; test early | Dev |
| **Warehouse access limited** | 🟡 Medium | Schedule pilot 2 weeks ahead | Ops |
| **Offline sync bugs** | 🟠 Moderate | Extra test coverage Week 5 | Dev |
| **Android SDK integration issues** | 🟡 Medium | Allocate 2-3 days buffer Week 3 | Dev |

---

## Success Metrics

**Phase 1-6 (Pilot):**
- Tag read accuracy: ≥99%
- Speed improvement: 60-70% vs. barcode
- Scan loss: <0.1%
- Uptime: 99.5% during warehouse hours
- Time to full adjustment: <half vs. barcode

**Code Quality:**
- Test coverage: ≥80% for critical paths
- Lint green: black + flake8
- Security: bandit + OWASP scan passing

---

## Dependencies & Assumptions

**Must be true for plan to work:**
1. ✅ Odoo 19.0 available (Docker image)
2. ✅ PostgreSQL 15+ (docker-compose)
3. ❓ iData T1UHF SDK available (action item Week 1)
4. ✅ Warehouse access for pilot (pre-arrange)
5. ✅ Test product/lot data (create Week 1)
6. ✅ One developer (solo, 40 hrs/week)

---

## Next Actions

**Right now (This week):**
- [ ] Acquire iData T1UHF + SDK documentation
- [ ] Test T1UHF on test device
- [ ] Confirm Android compatibility
- [ ] Get warehouse pilot dates (Week 6-8)
- [ ] Start Docker + Odoo 19 setup

**This roadmap is LIVING** — Update weekly based on pilot feedback and blockers.

---

**Roadmap Review:** 2026-08-26 (weekly sync)
