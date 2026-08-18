# -*- coding: utf-8 -*-
"""
Stock Barcode RFID Module Initialization

This module provides RFID scanning integration for Odoo's Barcode application.
Zebra T1/T2 UHF readers send EPCs to the Odoo backend, which relays them to
the Barcode UI as synthetic barcode scans.
"""

from . import models
from . import controllers

__all__ = [
    'models',
    'controllers',
]
