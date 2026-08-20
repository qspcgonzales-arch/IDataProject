# -*- coding: utf-8 -*-
"""
ORM Models for stock_barcode_rfid module.

Defines:
- stock.barcode.rfid: Audit log of all RFID scans
- Extensions to ir.api.key for RFID-specific auth
- Extensions to res.users for RFID operator management
"""

from . import rfid_tag_mapping
from . import rfid_calibration_profile
from . import stock_barcode_rfid
from . import ir_api_key
from . import res_users

__all__ = [
    'rfid_tag_mapping',
    'rfid_calibration_profile',
    'stock_barcode_rfid',
    'ir_api_key',
    'res_users',
]
