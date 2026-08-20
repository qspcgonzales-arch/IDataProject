# Troubleshooting Guide

**Status:** Placeholder — expanded as known issues are encountered during implementation.  
**See also:** `DEVELOPMENT.md` for common setup steps.

---

## Docker / Odoo

### Odoo won't start

```bash
docker-compose logs odoo | tail -50
```

Common causes:
- `backend/odoo.conf` is missing → it is now present in the repo; verify the file was mounted.
- PostgreSQL not ready → wait 10–15 sec after `docker-compose up -d`, or check healthcheck status with `docker-compose ps`.

### PostgreSQL connection error

```bash
docker-compose restart postgres
sleep 10
docker-compose restart odoo
```

### Module not found after install

- Verify `ODOO_ADDONS_PATH` in `docker-compose.yml` includes `/mnt/backend`.
- Confirm the module directory exists and `__manifest__.py` is valid Python.

---

## Android

### Build fails: "app/build.gradle.kts not found"

The file was missing in the original scaffold; it is now present at `android/app/build.gradle.kts`.

### Build fails: "Could not resolve dependency from jcenter"

jcenter was shut down. The repo's `settings.gradle.kts` now uses `mavenCentral()` only. Run `./gradlew clean` and rebuild.

### Build fails: "iData T1UHF SDK not found"

The SDK line is commented out in `app/build.gradle.kts`:
```kotlin
// implementation(files("libs/idataT1UHF-sdk.aar"))
```
Place the AAR in `android/app/libs/` and uncomment the line once Gate 1 is cleared.

---

## Backend Tests

### `pip install odoo` fails

Odoo is not on PyPI. The CI workflow installs it via the official Docker image, not pip. For local unit tests that do not need the full Odoo ORM, use the mock fixtures in `backend/tests/conftest.py`.

---

*This document will be expanded during implementation (Aug 24 onward).*
