"""
Pytest fixtures for IDataProject backend tests.

This file now includes a realistic Aug 24 baseline dataset:
- 1 warehouse context
- 10 products
- 10 stock lots
- 10 EPC samples
- 1 warehouse operator user
"""

import json
from pathlib import Path

import pytest


DATASET_PATH = Path(__file__).parent / "data" / "rfid_test_dataset.json"


@pytest.fixture(scope="session")
def rfid_test_dataset():
    """Load the realistic RFID test dataset used across backend tests."""
    with DATASET_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@pytest.fixture
def sample_warehouse(env):
    """Create or reuse a sample warehouse."""
    warehouse = env["stock.warehouse"].search([("code", "=", "RFID")], limit=1)
    if warehouse:
        return warehouse
    return env["stock.warehouse"].create(
        {
            "name": "RFID Test Warehouse",
            "code": "RFID",
        }
    )


@pytest.fixture
def sample_products(env, rfid_test_dataset):
    """Create 10 test products for scan resolution scenarios."""
    model = env["product.product"]
    created = []

    for item in rfid_test_dataset["products"]:
        product = model.search([("default_code", "=", item["default_code"])], limit=1)
        if product:
            created.append(product)
            continue

        vals = {
            "name": item["name"],
            "default_code": item["default_code"],
            "barcode": item["barcode"],
        }
        if "type" in model._fields:
            vals["type"] = "product"
        if "detailed_type" in model._fields:
            vals["detailed_type"] = "product"

        created.append(model.create(vals))

    return created


@pytest.fixture
def sample_lots(env, sample_products):
    """Create one lot per product for EPC-to-lot matching scenarios."""
    lot_model = env["stock.lot"]
    lots = []

    for index, product in enumerate(sample_products, start=1):
        lot_name = f"LOT-2026-08-{index:03d}"
        lot = lot_model.search(
            [("name", "=", lot_name), ("product_id", "=", product.id)],
            limit=1,
        )
        if not lot:
            lot = lot_model.create({"name": lot_name, "product_id": product.id})
        lots.append(lot)

    return lots


@pytest.fixture
def sample_user(env):
    """Create or reuse a warehouse operator user for RFID scan sessions."""
    user = env["res.users"].search([("login", "=", "operator@test.local")], limit=1)
    if user:
        return user
    return env["res.users"].create(
        {
            "name": "RFID Operator",
            "login": "operator@test.local",
            "password": "operator123",
            "email": "operator@test.local",
        }
    )


@pytest.fixture
def sample_inventory_context(sample_warehouse, sample_user):
    """Provide a stable inventory-session context payload for integration tests."""
    return {
        "inventory_ref": "INV-RFID-2026-08-24-001",
        "session_id": "rfid_session_aug24_001",
        "warehouse_id": sample_warehouse.id,
        "user_id": sample_user.id,
    }


@pytest.fixture
def sample_rfid_scan(sample_lots, rfid_test_dataset, sample_inventory_context):
    """Sample RFID scan payload aligned with the Aug 24 baseline dataset."""
    first_epc = rfid_test_dataset["epcs"][0]["epc"]
    return {
        "epc": first_epc,
        "lot_id": sample_lots[0].id,
        "session_id": sample_inventory_context["session_id"],
        "rssi": -65,
        "timestamp_ms": 1787485200000,
    }


def pytest_configure(config):
    """Register custom markers used by backend tests."""
    config.addinivalue_line("markers", "unit: unit tests (no database)")
    config.addinivalue_line("markers", "integration: integration tests (with database)")
    config.addinivalue_line("markers", "slow: slow tests (skip with -m 'not slow')")
