# IDataProject — Week-by-Week Todo Checklist
**2-Month Validated RFID Pilot** | **Reference: Ventor Guide**

---

## ⚠️ WEEK 1: Hardware Validation + Odoo Foundation

### **CRITICAL PATH: Hardware Spike (Days 1-2)**

- [ ] **Acquire iData T1UHF + SDK**
  - [ ] Download SDK from iData/Zebra portal
  - [ ] Verify Android 13+ support
  - [ ] Check SDK documentation for EPC read capability
  - [ ] Test raw EPC access (not just barcode)
  - [ ] Confirm power/session/Q-value control
  - [ ] Verify RSSI or filtering available
  - **BLOCKER:** If ANY fail → Escalate or pivot to Zebra TC77

- [ ] **Test Hardware Connectivity**
  - [ ] T1UHF pairs with test device
  - [ ] Network connection stable
  - [ ] Can reach Odoo at localhost:8069

### **Odoo Setup (Days 3-5)**

- [ ] **Docker + Odoo 19**
  - [ ] `docker-compose up -d`
  - [ ] Odoo running at localhost:8069
  - [ ] Admin login works
  - [ ] PostgreSQL health check passes

- [ ] **Module Scaffold**
  - [ ] Directory structure created
  - [ ] `__manifest__.py` ready
  - [ ] Models imported (but empty)
  - [ ] Controllers stub ready
  - [ ] Tests directory ready

- [ ] **Data Models Designed**
  - [ ] `rfid.tag.mapping` model (all 3 Ventor scenarios)
  - [ ] `stock.barcode.rfid.scan` audit log model
  - [ ] `rfid.calibration.profile` model
  - [ ] `stock.barcode.rfid.offline.queue` model
  - [ ] Model relationships mapped
  - [ ] Constraints & validations planned

### **Test Data Setup**

- [ ] Create test fixtures
  - [ ] Test warehouse
  - [ ] Test product + barcode
  - [ ] Test lot/serial
  - [ ] Test inventory adjustment
  - [ ] Test user (operator)
- [ ] Create 10 test RFID tags (EPC values)

### **Week 1 Definition of Done**

```
✅ Hardware works OR blocker identified
✅ Odoo 19 running at localhost:8069
✅ Module scaffold with correct structure
✅ Models defined in code + migrations ready
✅ Test data created
❌ FAIL = Hardware shows RED FLAG (pivot or escalate)
```

---

## 📡 WEEK 2: Core RFID Module (POST /scan + Dedup)

### **Implement `rfid.tag.mapping` Model**

- [ ] Create `models/rfid_tag_mapping.py`
  - [ ] EPC field (unique, index, 24-char validation)
  - [ ] Product FK
  - [ ] Lot/serial FK (optional)
  - [ ] Barcode field
  - [ ] Serial number field (non-standard EPC)
  - [ ] Encoding type (supplier | in_house | non_standard)
  - [ ] Timestamps (created_at, last_scanned)
  - [ ] Active flag
  - [ ] Scan count
  - [ ] Validation constraints
- [ ] Create migrations
- [ ] Test model constraints

### **Implement `stock.barcode.rfid.scan` Model**

- [ ] Create `models/stock_barcode_rfid_scan.py`
  - [ ] EPC field (index)
  - [ ] RSSI field
  - [ ] Tag mapping FK
  - [ ] Product FK (resolved)
  - [ ] Lot FK (resolved)
  - [ ] Inventory FK
  - [ ] Session ID
  - [ ] Duplicate flag
  - [ ] Status (resolved | unknown | discrepancy)
  - [ ] Created by user
  - [ ] Timestamps
- [ ] Create migrations
- [ ] Create database indices

### **Implement POST /stock_barcode_rfid/scan Endpoint**

- [ ] Create `controllers/main.py`
  - [ ] Route: `POST /stock_barcode_rfid/scan`
  - [ ] Auth via API key
  - [ ] Parse request JSON
  - [ ] Validate EPC format (24-char hex)
  - [ ] Validate inventory_id exists
  - [ ] Implement dedup logic (2-second window)
  - [ ] Look up tag mapping
  - [ ] Resolve product/lot
  - [ ] Create audit log entry
  - [ ] Return JSON response
  - [ ] Handle errors (400, 401, 429, 500)
- [ ] Test with curl

### **Write Unit Tests**

- [ ] Create `tests/test_epc_validation.py`
  - [ ] Valid EPC (24-char hex) passes
  - [ ] Invalid EPC (wrong length) raises error
  - [ ] Invalid EPC (non-hex) raises error
  - [ ] EPC case-insensitive normalization
  - [ ] Duplicate within 2 sec marked
  - [ ] Not duplicate after 2+ sec
  - [ ] Unknown EPC → status='unknown'
  - [ ] Known EPC → status='resolved'

### **Integrate with Inventory Adjustments**

- [ ] Verify scans can reference inventory.id
- [ ] Test that scans are linked to inventory
- [ ] Test that inventory.id validation works

### **Week 2 Definition of Done**

```
✅ POST /scan endpoint working
✅ Dedup logic tested (2-sec window)
✅ EPC validation passing
✅ Scans recorded in audit log
✅ Tag mapping lookup working
✅ Tests passing (unit + integration)
✅ API documented (Postman collection)
❌ FAIL = Integration test fails → fix before moving to Week 3
```

---

## 🏷️ WEEK 3: Ventor Mapping Scenarios + Tag Enrollment

### **Scenario 1: Supplier-Provided Tags**

- [ ] UI: Add product barcode in Odoo
- [ ] Endpoint: POST `/stock_barcode_rfid/tag_mapping`
  - [ ] Request: `{ epc, product_id, encoding_type: "supplier" }`
  - [ ] Create mapping
  - [ ] Return mapping ID
- [ ] Test: Supplier tag scans resolve product

### **Scenario 2: In-House Tag Encoding (NEW)**

- [ ] Endpoint: POST `/stock_barcode_rfid/write_tags`
  - [ ] Request: `{ product_id, epc_list[] }`
  - [ ] Validate product exists + has barcode
  - [ ] Create rfid.tag.mapping for each EPC
  - [ ] Return count + details
- [ ] Test: Multiple EPCs mapped in one call
- [ ] Test: Product barcode written to tag metadata

### **Scenario 3: Non-Standard EPC (Manual Mapping)**

- [ ] UI: Manual entry form for Serial Number
- [ ] Endpoint: PUT `/stock_barcode_rfid/tag_mapping/{id}`
  - [ ] Update serial_number field
  - [ ] Mark as "non_standard"
  - [ ] Allow future scans to resolve via serial
- [ ] Test: Non-standard EPC resolves via serial

### **Unknown EPC Handling (Discrepancy Workflow)**

- [ ] When EPC scanned → status='unknown'
- [ ] UI: Show discrepancy
- [ ] Operator can copy EPC to product serial → rescan
- [ ] Second scan → status='resolved'
- [ ] Test workflow

### **Week 3 Definition of Done**

```
✅ Scenario 1 (supplier) tested
✅ Scenario 2 (in-house) tested
✅ Scenario 3 (non-standard) tested
✅ Unknown EPC shows discrepancy
✅ Operator can map unknown EPC
✅ Rescan after mapping → resolved
✅ All 3 Ventor paths working
```

---

## 📱 WEEK 4: Android Scanner App (Phase 3)

### **Prerequisites**: Phase 2 API stable

### **Zebra UHF Integration**

- [ ] Download T1UHF SDK
- [ ] Create `android/app/src/main/kotlin/com/idataproject/scanner/ZebraUHFReader.kt`
  - [ ] Initialize Zebra SDK
  - [ ] Start inventory scan
  - [ ] EPC event listener
  - [ ] Client-side dedup (1-sec window)
  - [ ] Emit EPC to channel
- [ ] Test: Raw EPC reads working
- [ ] Test: RSSI values captured

### **HTTP Client + Offline Queueing**

- [ ] Create `android/app/src/main/kotlin/com/idataproject/network/OdooClient.kt`
  - [ ] POST to `/stock_barcode_rfid/scan`
  - [ ] API key from Keystore
  - [ ] Handle network errors
  - [ ] Queue scans when offline
  - [ ] Retry on reconnect
- [ ] Create `android/app/src/main/kotlin/com/idataproject/storage/OfflineQueue.kt`
  - [ ] SQLite local DB
  - [ ] Store pending scans
  - [ ] Sync on network restore

### **UI + Session Management**

- [ ] Create `android/app/src/main/kotlin/com/idataproject/ui/ScanScreen.kt`
  - [ ] Input: Inventory ID
  - [ ] Display: Scan count
  - [ ] Display: Last EPC
  - [ ] Button: Start/Stop scanning
  - [ ] Button: Sync offline queue
- [ ] Test: Can enter inventory ID
- [ ] Test: Scans display in real-time
- [ ] Test: Stop button works

### **Android Tests**

- [ ] Unit tests: ZebraUHFReader dedup logic
- [ ] Unit tests: OdooClient request formatting
- [ ] Integration test: Scan → POST → response
- [ ] Integration test: Offline queue → sync

### **Week 4 Definition of Done**

```
✅ Zebra UHF reading EPCs
✅ Android app running
✅ POST /scan working from Android
✅ Dedup on Android side working
✅ Offline queue implemented
✅ Sync on network restore working
✅ UI shows scans in real-time
```

---

## 🔧 WEEK 5: Calibration + Offline Handling

### **Calibration Profile Model**

- [ ] Create `models/rfid_calibration_profile.py`
  - [ ] Name (unique)
  - [ ] Power (dBm): 10-30
  - [ ] Session: 0-3
  - [ ] RSSI floor (dBm): -90 to 0
  - [ ] Q-value: 0-15
  - [ ] Zone (warehouse location)
  - [ ] Timestamps

### **Calibration Endpoints**

- [ ] GET `/stock_barcode_rfid/calibration/profiles`
- [ ] POST `/stock_barcode_rfid/calibration/profiles`
- [ ] PUT `/stock_barcode_rfid/calibration/profiles/{id}`
- [ ] DELETE `/stock_barcode_rfid/calibration/profiles/{id}`
- [ ] Test: CRUD operations working

### **Apply Profile to Android**

- [ ] Android fetches profiles via GET
- [ ] Android app UI: Select profile dropdown
- [ ] Android sends power/session/Q-value to Zebra SDK
- [ ] Test: Power/session changes via UI

### **Offline Queue Model**

- [ ] Create `models/stock_barcode_rfid_offline_queue.py`
  - [ ] EPC, inventory_id, RSSI
  - [ ] Status (pending | synced | failed)
  - [ ] Timestamps + error message
- [ ] Create sync logic
  - [ ] Fetch pending scans
  - [ ] POST to backend
  - [ ] Mark synced or failed
- [ ] Test: Queue fills when offline
- [ ] Test: Sync on reconnect works

### **E2E Test Setup**

- [ ] Create `tests/test_e2e_complete.py`
  - [ ] Full workflow: scan → backend → audit
  - [ ] Calibration applied
  - [ ] Offline sync verified

### **Week 5 Definition of Done**

```
✅ Calibration profiles stored
✅ Profiles fetchable via API
✅ Android applies profile
✅ Power/session/RSSI tunable
✅ Offline queue implemented
✅ Sync logic working
✅ E2E test passing
```

---

## ✅ WEEKS 6-8: Warehouse Pilot/UAT + Refinement

### **Pre-Pilot (Days 36-38)**

- [ ] Prepare test warehouse
  - [ ] 20-50 tagged products
  - [ ] 2-3 zones defined
  - [ ] Inventory data in Odoo
  - [ ] Test calibration profiles
- [ ] Operator training (1 day)
  - [ ] How to start scanning
  - [ ] How to handle unknown EPCs
  - [ ] How to apply adjustments
- [ ] Run 2 practice cycles
  - [ ] Measure time vs. barcode
  - [ ] Collect feedback
  - [ ] Fix obvious bugs

### **Pilot Week 1 (Days 39-45)**

- [ ] Run 5 inventory adjustments with RFID
- [ ] Measure:
  - [ ] Tag read accuracy
  - [ ] Time per adjustment
  - [ ] Discrepancies found
  - [ ] Operator satisfaction
- [ ] Collect feedback
  - [ ] What was hard?
  - [ ] What was slow?
  - [ ] What failed?
- [ ] Fix high-priority bugs

### **Pilot Week 2 (Days 46-52)**

- [ ] Run 5 more adjustments
- [ ] Verify fixes from Week 1
- [ ] Run 4-hour continuous scanning test
  - [ ] Measure scan loss
  - [ ] Measure uptime
  - [ ] Test offline handling
- [ ] Document results

### **Validation Checklist**

- [ ] Tag read accuracy ≥99%
- [ ] Speed improvement 60-70% vs. barcode
- [ ] Scan loss <0.1%
- [ ] Uptime 99.5% during 4-hour shift
- [ ] Operators can do full cycle without help
- [ ] Unknown EPCs handled correctly
- [ ] All scans recorded in audit log

### **Refinement Tasks**

- [ ] Bug fixes from pilot
- [ ] Performance tuning
- [ ] Security audit (API keys, auth)
- [ ] Documentation updates
- [ ] UAT sign-off

### **Week 6-8 Definition of Done**

```
✅ Pilot completed successfully
✅ Accuracy ≥99%
✅ Speed improvement validated
✅ Uptime 99.5%
✅ Operators trained + comfortable
✅ All critical bugs fixed
✅ Audit trail complete
✅ Production readiness assessment done
```

---

## 📊 Daily Standup Template

**Every morning (5 min):**
```
Yesterday:
  - [ ] Completed X feature
  - [ ] Fixed X bug
  - [ ] Wrote X tests

Today:
  - [ ] Implement X
  - [ ] Test X
  - [ ] Debug X

Blockers:
  - [ ] None / [ ] Hardware SDK / [ ] API issue
```

---

## 🚨 Red Flags (Stop & Escalate)

If ANY of these happen, pause and escalate:

1. **Hardware doesn't work (Week 1)**
   - T1UHF SDK missing or incompatible
   - RSSI/power control unavailable
   - Android compatibility issue
   → Action: Pivot to alternative hardware or stop

2. **Odoo API breaking changes**
   - Tests fail on Odoo 19 upgrade
   - Model constraints incompatible
   → Action: Pin Odoo version or adjust models

3. **Dedup logic has race condition**
   - Same EPC in 2-sec window sometimes not marked duplicate
   → Action: Add database lock or use cache (Redis)

4. **Offline sync loses scans**
   - Scans disappear on reconnect
   → Action: Add transaction handling + recovery

5. **Pilot shows <95% accuracy**
   - Tag reads unreliable
   - RSSI filtering not working
   → Action: Recalibrate or adjust Q-value

---

## 📈 Success Metrics by Week

| Week | Metric | Target |
|------|--------|--------|
| 1 | Hardware validation | ✅ Pass all checks |
| 2 | POST /scan tests passing | ✅ 100% green |
| 3 | All 3 Ventor scenarios working | ✅ Tested |
| 4 | Android app scanning | ✅ Scans POST to backend |
| 5 | Offline + calibration working | ✅ E2E passing |
| 6-8 | Pilot accuracy | ✅ ≥99% |
| 6-8 | Operator speed | ✅ 60-70% faster |

---

## 🎯 NEXT STEPS (Do This Now)

- [ ] **TODAY:** Read ROADMAP_UPDATED.md completely
- [ ] **TODAY:** Acquire iData T1UHF + SDK (if not already done)
- [ ] **TOMORROW:** Start Week 1 hardware validation
- [ ] **This week:** Get Docker + Odoo 19 running
- [ ] **This week:** Set up test data + fixtures

**Estimated timeline:** 2 months (8-9 weeks) for validated pilot

**NOT included:** Production rollout (Phase 7) — defer to post-pilot
