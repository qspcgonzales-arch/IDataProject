# IDataProject — Development Guide

**Last Updated:** 2026-08-18

---

## Quick Start (5 minutes)

```bash
# Clone the monorepo
git clone https://github.com/qspcgonzales-arch/IDataProject.git
cd IDataProject

# Copy environment template
cp .env.example .env

# Start dev environment (Odoo 19 + PostgreSQL)
docker-compose up -d

# Odoo available at http://localhost:8069
# Default: admin / admin
# Database: idata_dev
```

For Android development, see `/android/README.md`.

---

## Project Structure

```
IDataProject/
├── ARCHITECTURE.md              # System design (read first!)
├── DEVELOPMENT.md               # This file
├── SECURITY.md                  # Auth, data validation, secrets
├── API_CONTRACT.md              # OpenAPI spec for /stock_barcode_rfid/*
├── .env.example                 # Environment variables template
├── docker-compose.yml           # Local dev stack
├── .github/
│   └── workflows/
│       ├── backend-tests.yml    # Python tests + lint (Odoo)
│       ├── android-build.yml    # Kotlin build + lint
│       └── security-scan.yml    # OWASP, secrets scanning
├── backend/                     # Odoo custom modules
│   ├── stock_barcode_rfid/      # Main RFID bridge module
│   │   ├── __init__.py
│   │   ├── __manifest__.py
│   │   ├── models/              # ORM models
│   │   ├── controllers/         # HTTP endpoints
│   │   └── views/               # UI templates
│   ├── stock_barcode_rfid_calibration/  # Phase 4: calibration profiles
│   ├── scripts/                 # Local DB/bootstrap scripts
│   ├── tests/                   # Backend pytest suite + fixtures
│   │   ├── conftest.py
│   │   ├── test_epc_validation.py
│   │   └── data/
│   │       └── rfid_test_dataset.json
│   ├── odoo.conf                # Odoo runtime config mounted by Docker
│   └── requirements.txt          # Python dependencies (Odoo addons)
├── android/                     # Zebra T1/T2 scanner app
│   ├── README.md                # Android setup guide
│   ├── build.gradle.kts         # Project config
│   ├── gradle/                  # Gradle wrapper
│   ├── app/
│   │   ├── build.gradle.kts
│   │   ├── src/
│   │   │   ├── main/
│   │   │   │   ├── kotlin/
│   │   │   │   │   └── com/idataproject/
│   │   │   │   │       ├── MainActivity.kt
│   │   │   │   │       ├── scanner/         # Zebra UHF logic
│   │   │   │   │       ├── ui/              # Compose UI
│   │   │   │   │       ├── network/         # Odoo API client
│   │   │   │   │       └── storage/         # Local persistence
│   │   │   │   └── AndroidManifest.xml
│   │   │   └── test/
│   │   │       ├── kotlin/                  # Unit tests
│   │   │       └── androidTest/             # Integration tests
│   │   └── proguard-rules.pro
│   └── gradle.properties
├── docs/                        # Extended documentation
│   ├── SETUP_ODOO.md            # Odoo 19 Docker setup details
│   ├── SETUP_ANDROID.md         # Android dev environment
│   ├── CALIBRATION_GUIDE.md     # Phase 4 calibration procedure
│   ├── DEPLOYMENT.md            # Production rollout checklist
│   └── TROUBLESHOOTING.md       # Common issues + fixes
├── IDataProject-Phase0-Decisions.md  # Phase 0 decisions log
└── ROADMAP_UPDATED.md           # Tracker-aligned roadmap (source of truth)
```

---

## Development Workflow

### 1. Branch Strategy

```
main              → Production-ready (post-pilot Phase 7)
├── develop       → Integration branch (PR target)
│   ├── feature/* → New features
│   ├── fix/*     → Bug fixes
│   └── calibration/* → Week 5 calibration work
└── release/*     → Release candidates (pilot/UAT window)
```

**Naming convention:** `feature/epc-tag-mapping`, `fix/dedup-race-condition`, `calibration/rssi-floor-sweep`

### 2. Code Review Checklist (before PR merge)

- [ ] Tests pass locally + CI green
- [ ] Code follows style guide (see below)
- [ ] No secrets in commit (run `git-secrets --scan`)
- [ ] Security: input validation, rate limiting, auth checks
- [ ] Documentation: docstrings on public functions, comments on non-obvious logic
- [ ] Backwards compatibility: no breaking changes to API endpoints
- [ ] Performance: no N+1 queries (Odoo), no main-thread blocking (Android)

### 3. Making Changes

**Backend (Odoo)**

```bash
# Create feature branch
git checkout -b feature/epc-to-lot-mapping

# Make changes in backend/stock_barcode_rfid/
# Write tests in backend/tests/

# Run tests locally
cd backend
python -m pytest tests/ -v

# Lint & format
black .
flake8 . --max-line-length=100

# Commit
git commit -m "feat(stock_barcode_rfid): add EPC to lot mapping

- Implement Barcode Nomenclature rule for 96-bit EPC format
- Add unit tests for EPC validation and lot lookup
- Closes #42"

# Push and create PR
git push origin feature/epc-to-lot-mapping
```

**Android (Kotlin)**

```bash
# Create feature branch
git checkout -b feature/zebra-uhf-scan-loop

# Make changes in android/app/src/

# Run tests
cd android
./gradlew test          # Unit tests
./gradlew connectedAndroidTest  # Integration tests (requires device/emulator)

# Lint & format
./gradlew ktlintFormat
./gradlew lint

# Commit
git commit -m "feat(scanner): implement Zebra UHF scan loop with dedup

- Add ZebraUHFReader integration via DataWedge
- Implement in-memory dedup (Map<EPC, timestamp>)
- Add unit tests for duplicate filtering
- Closes #43"

# Push and create PR
git push origin feature/zebra-uhf-scan-loop
```

---

## Coding Standards

### Python (Odoo Backend)

**Follow PEP 8 + Odoo conventions:**

```python
# models/stock_barcode_rfid.py

from odoo import models, fields, api, exceptions
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

class StockBarcodeRFID(models.Model):
    _name = 'stock.barcode.rfid'
    _description = 'RFID Scan Log'
    _order = 'create_date DESC'

    epc = fields.Char('EPC', required=True, index=True)
    barcode = fields.Char('Barcode', related='epc')  # Treat EPC as barcode
    lot_id = fields.Many2one('stock.lot', 'Lot', required=True)
    session_id = fields.Char('Session ID', required=True)
    rssi = fields.Integer('RSSI (dBm)', help='Signal strength')
    source = fields.Selection([
        ('android_app', 'Android App'),
        ('gateway', 'Portal/Gateway (Phase 8)'),
    ], default='android_app')
    is_duplicate = fields.Boolean('Marked as Duplicate', default=False)
    duplicate_of_id = fields.Many2one('stock.barcode.rfid', 'Original Scan')

    @api.model
    def validate_epc(self, epc):
        """Validate EPC format (96-bit hex = 24 chars)."""
        if not isinstance(epc, str) or len(epc) != 24:
            raise exceptions.ValidationError(
                f"Invalid EPC format. Expected 24 hex chars, got: {epc}"
            )
        try:
            int(epc, 16)  # Validate hex
        except ValueError:
            raise exceptions.ValidationError(f"EPC contains non-hex characters: {epc}")

    @api.model
    def deduplicate_and_queue(self, epc, session_id, rssi=0):
        """
        Server-side dedup: check if EPC seen in last 2 seconds.
        If not: create record and return it.
        If yes: mark as duplicate and return original.
        """
        two_sec_ago = datetime.now() - timedelta(seconds=2)
        original = self.search([
            ('epc', '=', epc),
            ('session_id', '=', session_id),
            ('create_date', '>=', two_sec_ago),
        ], order='create_date DESC', limit=1)

        if original:
            dup = self.create({
                'epc': epc,
                'session_id': session_id,
                'rssi': rssi,
                'is_duplicate': True,
                'duplicate_of_id': original.id,
            })
            _logger.info(f"Duplicate EPC {epc} in session {session_id}, deduplicated")
            return original  # Return the original scan
        else:
            scan = self.create({
                'epc': epc,
                'session_id': session_id,
                'rssi': rssi,
            })
            _logger.info(f"New EPC {epc} in session {session_id}")
            return scan
```

**Conventions:**
- Model names: `snake_case` (e.g., `stock_barcode_rfid`)
- Methods: `snake_case`, document with docstring
- Constants: `UPPER_CASE`
- Use `_logger` for logging (not `print()`)
- No bare `except:`, always specify exception type
- Comment WHY, not WHAT (code should be self-documenting)

### Kotlin (Android Scanner)

**Follow Google Android style + Kotlin idioms:**

```kotlin
// app/src/main/kotlin/com/idataproject/scanner/ZebraUHFReader.kt

package com.idataproject.scanner

import android.content.Context
import android.util.Log
import kotlinx.coroutines.*
import java.util.concurrent.ConcurrentHashMap

private const val TAG = "ZebraUHFReader"
private const val DEDUP_WINDOW_MS = 2000L  // 2 second dedup window

class ZebraUHFReader(private val context: Context) {
    private val dedupeMap = ConcurrentHashMap<String, Long>()
    private val epcsChannel = Channel<String>(Channel.BUFFERED)

    suspend fun startScanning() = withContext(Dispatchers.IO) {
        try {
            // Initialize Zebra UHF reader (via DataWedge or direct SDK)
            val reader = initializeZebraReader()
            reader.setEventListener { epc, rssi ->
                handleEpc(epc, rssi)
            }
            reader.startInventory()
        } catch (e: Exception) {
            Log.e(TAG, "Failed to start scanner", e)
            throw e
        }
    }

    private fun handleEpc(epc: String, rssi: Int) {
        // Validate EPC format
        if (!isValidEpc(epc)) {
            Log.w(TAG, "Invalid EPC format: $epc")
            return
        }

        // Client-side dedup: avoid duplicate POSTs within window
        val now = System.currentTimeMillis()
        val lastSeen = dedupeMap[epc] ?: 0L

        if (now - lastSeen < DEDUP_WINDOW_MS) {
            Log.d(TAG, "Deduped EPC: $epc (last seen ${now - lastSeen}ms ago)")
            return
        }

        dedupeMap[epc] = now
        Log.d(TAG, "New EPC: $epc (RSSI: $rssi dBm)")

        // Emit for upstream processing
        GlobalScope.launch {
            epcsChannel.send(epc)
        }
    }

    private fun isValidEpc(epc: String): Boolean {
        // 96-bit EPC = 24 hex characters
        return epc.length == 24 && epc.all { it in '0'..'9' || it in 'A'..'F' || it in 'a'..'f' }
    }

    fun stopScanning() {
        epcsChannel.close()
        dedupeMap.clear()
    }
}
```

**Conventions:**
- Class names: `PascalCase`
- Functions/variables: `camelCase`
- Constants: `UPPER_SNAKE_CASE`
- Use Kotlin idioms: `?.let { }`, `when`, scope functions
- Prefer sealed classes over enums when variants carry data
- Suspend functions for async work (not callbacks)
- Use `Log.d()` for debugging, `Log.e()` for errors
- Comment the WHY, not the WHAT

---

## Testing Strategy

### Backend (Odoo)

**Unit tests** (fast, isolated):
```bash
cd backend
python -m pytest tests/test_epc_validation.py -v
```

**Integration tests** (with real DB):
```bash
python -m pytest tests/ -m integration -v
```

**Coverage requirement:** 80%+ for critical paths (dedup, EPC lookup)

### Android

**Unit tests** (no device):
```bash
cd android
./gradlew test
```

**Integration tests** (device/emulator):
```bash
./gradlew connectedAndroidTest
```

**Manual testing checklist:**
- [ ] Scan 10 tags in rapid succession, verify no duplicates sent to Odoo
- [ ] Disconnect Wi-Fi, scan 5 tags, reconnect, verify all 5 arrive in Odoo
- [ ] Scan 100 tags on a shelf, compare count vs manual inventory

---

## Debugging Tips

### Odoo Backend

```python
# Add to /backend/stock_barcode_rfid/controllers/main.py

from odoo.addons.web.controllers import main
import logging
_logger = logging.getLogger(__name__)

# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check Odoo logs
docker-compose logs -f odoo | grep "stock_barcode_rfid"

# Jump into Odoo shell for ad-hoc queries
docker-compose exec odoo odoo shell

# Inside shell:
from odoo.addons.stock_barcode_rfid.models import *
env['stock.barcode.rfid'].search([('epc', '=', '123abc...')])
```

### Android

```kotlin
// Check logcat
./gradlew connectedAndroidTest --info

// Or in Android Studio
adb logcat | grep "ZebraUHFReader"

// Simulate network failure
adb shell setprop net.hostname localhost  # Forces localhost fallback
```

---

## Environment Variables (.env)

Copy `.env.example` and fill in:

```bash
# Odoo
ODOO_ADMIN_PASSWD=<strong-password>
ODOO_DB_NAME=idata_dev
POSTGRES_USER=odoo
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=idata_dev

# Android (API endpoint)
ODOO_API_URL=http://10.0.2.2:8069  # 10.0.2.2 = Android emulator's localhost
ODOO_API_KEY=<generated-in-phase-2>

# Calibration settings (Week 5)
RFID_POWER_DEFAULT=30  # dBm
RFID_SESSION_DEFAULT=0
RFID_RSSI_FLOOR_DEFAULT=-70  # dBm
```

---

## CI/CD Pipeline

Every push to any branch runs:

1. **Lint** (black, flake8 for Python; ktlint for Kotlin)
2. **Unit tests** (pytest, gradle test)
3. **Security scan** (bandit for Python, lint for Android)
4. **Coverage report** (must be ≥80%)

Merge to `develop` only if CI is green.

---

## Performance Baseline

**Backend targets (Phase 5 load testing):**
- POST /stock_barcode_rfid/scan: <100ms (p95) per EPC
- Dedup check: <5ms
- Barcode Nomenclature validation: <10ms
- Throughput: ≥50 EPCs/sec per session

**Android targets (Phase 3):**
- Zebra UHF scan loop: ≥20 tags/sec
- Local dedup: <1ms per EPC
- POST to Odoo: batch 10 EPCs per 500ms (throttle)
- Memory: <100MB baseline

---

## Common Tasks

### Add a new Odoo model field for RFID metadata

```python
# In stock_barcode_rfid/models/__init__.py, add:

class StockLot(models.Model):
    _inherit = 'stock.lot'

    rfid_epc = fields.Char('RFID EPC', unique=True, index=True)
    rfid_encoded_by = fields.Selection([
        ('in_house', 'In-House Encoder'),
        ('supplier', 'Pre-Encoded from Supplier'),
    ])
    rfid_last_scanned = fields.Datetime('Last RFID Scan')
```

Then run `python -m pytest tests/test_lot_rfid_fields.py` to verify.

### Deploy to staging

```bash
# After code review + merge to develop
git checkout develop
git pull origin develop

# Tag a release candidate
git tag -a rc-0.1.0 -m "Release candidate for Phase 2"
git push origin rc-0.1.0

# CI automatically builds and pushes docker image to staging
# See .github/workflows/deploy-staging.yml
```

---

## Getting Help

- **Architecture questions:** See `ARCHITECTURE.md`
- **Security concerns:** See `SECURITY.md`
- **API endpoint details:** See `API_CONTRACT.md`
- **Troubleshooting:** See `docs/TROUBLESHOOTING.md`
- **Android setup issues:** See `android/README.md`
- **Slack:** #idata-project (team channel)
