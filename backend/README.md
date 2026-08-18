# Backend Module Structure

This directory contains Odoo custom modules for the RFID integration.

## Modules

### `stock_barcode_rfid/`
Main RFID bridge module. Handles:
- EPC ingestion from Android app
- Server-side deduplication
- Relay to Odoo Barcode UI
- API key management
- Audit logging

### `stock_barcode_rfid_calibration/` (Phase 4+)
Calibration profile management. Stores:
- RFID hardware tuning (power, session, RSSI floor)
- Per-zone profiles
- Profile versioning & audit trail

## Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v

# Code quality checks
black .          # Format
flake8 .         # Lint
mypy .           # Type checking
```

## Conventions

- PEP 8 + Odoo style guide
- Model names: `snake_case`
- Methods: `snake_case` with docstrings
- Constants: `UPPER_CASE`
- Logging via `_logger` (not `print()`)
- Comments explain WHY, not WHAT

## File Layout

```
stock_barcode_rfid/
├── __init__.py              # Module exports
├── __manifest__.py          # Module metadata
├── models/
│   ├── __init__.py
│   ├── stock_barcode_rfid.py       # Main audit log model
│   ├── ir_api_key.py               # API key extensions
│   └── res_users.py                # User extensions
├── controllers/
│   ├── __init__.py
│   └── main.py              # HTTP endpoints: /stock_barcode_rfid/scan, etc.
├── views/
│   ├── stock_barcode_rfid_views.xml
│   └── api_key_views.xml
├── tests/
│   ├── __init__.py
│   ├── test_epc_validation.py       # Unit tests
│   ├── test_dedup_logic.py
│   └── test_rfid_bridge_e2e.py      # Integration tests
├── static/
│   ├── js/                  # OWL/JS for custom UI
│   └── css/
└── README.md                # Module-specific docs
```

See DEVELOPMENT.md for coding examples and standards.
