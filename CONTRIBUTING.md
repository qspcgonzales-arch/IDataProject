# Contributing to IDataProject

Thank you for helping build the next-generation warehouse inventory system!

## Before You Start

1. **Read the architecture** — See [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system design
2. **Check current status** — See [README.md](README.md#roadmap--phases) for the tracker-aligned roadmap and active milestone
3. **Check the code standards** — See [DEVELOPMENT.md](DEVELOPMENT.md) for Python/Kotlin style guides

## Getting Started

### 1. Clone & Setup
```bash
git clone https://github.com/qspcgonzales-arch/IDataProject.git
cd IDataProject
cp .env.example .env
docker-compose up -d
```

### 2. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
# OR
git checkout -b fix/issue-number
# OR
git checkout -b calibration/phase-4-work
```

Branch naming: `feature/*`, `fix/*`, `calibration/*`, `docs/*`

### 3. Make Your Changes

**For backend (Odoo/Python):**
```bash
cd backend
# Edit files...
python -m pytest tests/ -v      # Run tests
black . && flake8 .              # Format & lint
```

**For Android (Kotlin):**
```bash
cd android
# Edit files...
./gradlew test                   # Run tests
./gradlew ktlintFormat           # Format
```

### 4. Commit with Clear Messages

Use conventional commits:
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`  
**Scope:** `stock_barcode_rfid`, `android_scanner`, `calibration`, etc.

**Examples:**
```
feat(stock_barcode_rfid): add EPC validation endpoint

- Implement 96-bit EPC hex format validation
- Add unit tests for invalid inputs (empty, non-hex, wrong length)
- Add integration test: POST invalid EPC → 400 Bad Request

Closes #42
```

```
fix(android_scanner): handle Wi-Fi reconnection correctly

- Fix: offline queue not flushing on reconnect
- Add test: scan 5 tags offline, reconnect, verify all 5 in Odoo

Closes #51
```

### 5. Push & Create a Pull Request

```bash
git push origin feature/your-feature-name
```

Then on GitHub, create a PR with:
- **Title:** Clear description (e.g., "Add EPC to lot mapping in Barcode UI")
- **Description:** Why this change (reference the issue, explain the problem)
- **Link to issue:** "Closes #42" in description

### 6. Code Review

- **Maintainers** will review your code, ask questions, request changes
- **Address feedback** by pushing new commits (don't force-push)
- **If stuck,** ask in comments or team channel

### 7. Merge

Once approved and CI passes:
- **Squash & merge** if commits are small/incremental
- **Merge** if commits are logical and well-structured

---

## Code Review Checklist

Before submitting your PR, verify:

- [ ] **Tests pass:** `pytest` (backend) or `./gradlew test` (android)
- [ ] **Code formatted:** `black`, `flake8` (backend) or `ktlint` (android)
- [ ] **No secrets:** No API keys, passwords, private IPs in code
- [ ] **Security:** Input validation, no SQL injection, auth checks
- [ ] **Documentation:** Docstrings on public functions, complex logic commented
- [ ] **Performance:** No N+1 queries (Odoo), no main-thread blocking (Android)
- [ ] **Backwards compatible:** No breaking changes to API endpoints
- [ ] **Linked to issue:** PR references the GitHub issue it closes

---

## Common Workflows

### Adding a New Odoo Model Field

```python
# backend/stock_barcode_rfid/models/stock_barcode_rfid.py

class StockBarcodeRFID(models.Model):
    _name = 'stock.barcode.rfid'

    # NEW FIELD
    calibration_profile = fields.Char('Calibration Profile', required=False)

# Write test
# backend/stock_barcode_rfid/tests/test_calibration_field.py

def test_calibration_profile_storage(env):
    scan = env['stock.barcode.rfid'].create({
        'epc': '1234567890ABCDEF12345678',
        'calibration_profile': 'zone_a_dense',
    })
    assert scan.calibration_profile == 'zone_a_dense'
```

### Adding an Android Feature

```kotlin
// android/app/src/main/kotlin/com/idataproject/scanner/NewFeature.kt

class NewFeatureManager(private val context: Context) {
    suspend fun doSomething(): Result {
        return withContext(Dispatchers.IO) {
            // Implementation
        }
    }
}

// Test
// android/app/src/test/kotlin/com/idataproject/scanner/NewFeatureTest.kt

class NewFeatureTest {
    @Test
    fun testDoSomething() = runTest {
        val manager = NewFeatureManager(context)
        val result = manager.doSomething()
        assertEquals(expected, result)
    }
}
```

### Fixing a Bug

1. **Write a failing test** that reproduces the bug
2. **Fix the code** to make the test pass
3. **Run full test suite** to ensure no regressions
4. **Commit:** `fix(scope): brief description`

---

## Testing Guidelines

**Backend (Python/Pytest)**
- Unit tests: fast, isolated, no database
- Integration tests: use real DB, test full workflows
- Target: 80%+ code coverage for critical paths (dedup, EPC lookup)

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_dedup_logic.py::test_duplicate_dedup -v

# Coverage report
pytest --cov=stock_barcode_rfid tests/
```

**Android (Kotlin)**
- Unit tests: logic, data models, utilities (no device)
- Integration tests: UI interactions, network (requires device/emulator)

```bash
# Unit tests
./gradlew test

# Integration tests
./gradlew connectedAndroidTest

# Coverage
./gradlew jacocoTestReport
```

---

## Performance & Best Practices

### Backend (Odoo)
- ❌ Avoid N+1 queries: use `prefetch_related()` or `select_related()`
- ❌ Avoid bare `except:` — always specify exception type
- ✓ Use `_logger` for logging (not `print()`)
- ✓ Comment WHY, not WHAT
- ✓ Write doctstrings for public methods

### Android
- ❌ Avoid main-thread blocking — use coroutines/background threads
- ❌ Avoid memory leaks — use `viewModelScope`, not `GlobalScope`
- ✓ Use Kotlin idioms: `?.let`, `when`, scope functions
- ✓ Use suspend functions, not callbacks
- ✓ Keep UI layer simple (render only, let ViewModel handle logic)

---

## Debugging Help

**Backend (Odoo):**
```bash
# View logs
docker-compose logs -f odoo | grep "stock_barcode_rfid"

# Jump into Odoo shell
docker-compose exec odoo odoo shell
# Inside shell: env['stock.barcode.rfid'].search([...])

# Check PostgreSQL directly
docker-compose exec postgres psql -U odoo -d idata_dev -c "SELECT * FROM stock_barcode_rfid LIMIT 10;"
```

**Android:**
```bash
# View logs
adb logcat | grep "IDataProject"

# Run app in debug mode (Android Studio)
# Set breakpoint, run "Debug 'app'"

# Check HTTP traffic
# Use Charles Proxy or Fiddler to intercept API calls
```

---

## Security Concerns

Found a security issue? **Do NOT open a public GitHub issue.**

Email: security@idataproject.internal

Include:
- Description of vulnerability
- Steps to reproduce
- Potential impact
- Proof-of-concept (if safe to share)

---

## Questions?

- **Architecture?** → See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Code standards?** → See [DEVELOPMENT.md](DEVELOPMENT.md)
- **API endpoints?** → See [API_CONTRACT.md](API_CONTRACT.md)
- **Stuck on testing?** → See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- **Team discussion?** → Join #idata-project Slack channel

---

## Thank You!

Every contribution moves us closer to faster, more reliable warehouse inventory. We appreciate your effort! 🚀
