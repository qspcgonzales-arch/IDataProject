# -*- coding: utf-8 -*-
"""
HTTP Controllers for stock_barcode_rfid module.

Endpoints:
- POST /stock_barcode_rfid/scan: Accept RFID scan (EPC) from Android app
- POST /stock_barcode_rfid/session/create: Create RFID scan session
- GET /stock_barcode_rfid/session/{session_id}/stream: SSE stream for real-time relay
- POST /stock_barcode_rfid/session/{session_id}/poll: Long-poll alternative
- GET /stock_barcode_rfid/calibration/profiles: List calibration profiles
- POST /stock_barcode_rfid/calibration/profiles: Create/update profile
"""

from . import main

__all__ = [
    'main',
]
