"""
Pytest configuration and fixtures for IDataProject backend tests.
"""

import pytest
from odoo.tests import TransactionCase, BaseTest
from odoo import fields


@pytest.fixture
def sample_lot(env):
    """Create a sample stock.lot for testing."""
    return env['stock.lot'].create({
        'name': 'LOT-2024-08-001',
        'product_id': env['product.product'].create({
            'name': 'Test Product',
            'type': 'product',
        }).id,
    })


@pytest.fixture
def sample_warehouse(env):
    """Create a sample warehouse."""
    return env['stock.warehouse'].search([], limit=1) or env['stock.warehouse'].create({
        'name': 'Test Warehouse',
        'code': 'TEST',
    })


@pytest.fixture
def sample_user(env):
    """Create a sample warehouse operator user."""
    return env['res.users'].create({
        'name': 'RFID Operator',
        'login': 'operator@test.local',
        'password': 'operator123',
        'email': 'operator@test.local',
    })


@pytest.fixture
def barcode_session(env, sample_user, sample_warehouse):
    """Create a mock barcode session for testing."""
    session = {
        'id': 'barcode_session_test123',
        'user_id': sample_user.id,
        'warehouse_id': sample_warehouse.id,
        'picking_type_id': env['stock.picking.type'].search([
            ('code', '=', 'internal'),
            ('warehouse_id', '=', sample_warehouse.id),
        ], limit=1).id,
    }
    return session


@pytest.fixture
def sample_rfid_scan(sample_lot):
    """Sample RFID scan data."""
    return {
        'epc': '1234567890ABCDEF12345678',
        'lot_id': sample_lot.id,
        'session_id': 'barcode_session_test123',
        'rssi': -65,
        'timestamp_ms': 1692374400000,
    }


# Markers for test categorization
def pytest_configure(config):
    config.addinivalue_line("markers", "unit: unit tests (no database)")
    config.addinivalue_line("markers", "integration: integration tests (with database)")
    config.addinivalue_line("markers", "slow: slow tests (skip with -m 'not slow')")
