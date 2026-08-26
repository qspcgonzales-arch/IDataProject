# -*- coding: utf-8 -*-
"""
HTTP controller for the RFID scan bridge.

auth='public' + manual API-key check, NOT auth='bearer' — Odoo's
@http.route auth parameter only supports 'user', 'public', and 'none'
(Rev. 2 roadmap, Section 5). API-key authentication is implemented in
this module's res.users extension (added in a later step); for now
this endpoint resolves EPCs and writes the audit log, matching the
2026-09-08 tracker item. Auth wiring lands with the 2026-09-09 item.
"""

from odoo import http
from odoo.http import request


class StockBarcodeRfidController(http.Controller):

    @http.route(
        '/stock_barcode_rfid/scan',
        auth='public',
        type='json',
        methods=['POST'],
        csrf=False,
    )
    def scan(self, epc=None, rssi=None, session_id=None, **kwargs):
        """Resolve a single EPC against rfid.tag.mapping and log the scan.

        Returns:
            {'status': 'resolved', 'product_id': int, 'product_name': str}
            {'status': 'unknown'}
        """
        if not epc:
            return {'error': 'epc is required'}, 400

        env = request.env
        mapping = env['rfid.tag.mapping'].sudo().search(
            [('epc', '=', epc)], limit=1
        )

        scan_vals = {
            'epc': epc,
            'rssi': rssi,
            'session_id': session_id,
        }

        if mapping:
            scan_vals.update(
                {
                    'status': 'resolved',
                    'tag_mapping_id': mapping.id,
                    'product_id': mapping.product_id.id,
                    'lot_id': mapping.lot_id.id,
                }
            )
        else:
            scan_vals['status'] = 'unknown'

        scan = env['stock.barcode.rfid.scan'].sudo().create(scan_vals)

        if mapping:
            return {
                'status': 'resolved',
                'scan_id': scan.id,
                'product_id': mapping.product_id.id,
                'product_name': mapping.product_id.display_name,
            }
        return {'status': 'unknown', 'scan_id': scan.id}
