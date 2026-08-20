# -*- coding: utf-8 -*-
"""
stock.barcode.rfid.scan — Audit log for every RFID scan accepted by the bridge.

Fields
------
epc             : 96-bit EPC in uppercase hex (24 chars)
session_id      : Barcode app session identifier
device_id       : Android device serial (optional, for fleet audit)
rssi            : Signal strength in dBm at scan time
timestamp_ms    : Client-side epoch timestamp (ms) for replay ordering
tag_mapping_id  : FK to rfid.tag.mapping — null when EPC is unknown
product_id      : Resolved product (denormalised for fast reporting)
lot_id          : Resolved lot/serial (denormalised, nullable)
is_duplicate    : True when server-side dedup rejected this EPC
scan_status     : 'resolved' | 'unknown'
relay_status    : 'relayed' | 'queued' | 'buffered'
operator_id     : Odoo user who owned the session
"""

from odoo import fields, models, api
from odoo.exceptions import ValidationError
import re

EPC_RE = re.compile(r'^[0-9A-F]{24}$')


class StockBarcodeRfidScan(models.Model):
    _name = 'stock.barcode.rfid.scan'
    _description = 'RFID Scan Audit Log'
    _order = 'create_date desc'

    epc = fields.Char(
        string='EPC',
        required=True,
        index=True,
        help='96-bit EPC in uppercase hex (24 characters)',
    )
    session_id = fields.Char(
        string='Session ID',
        required=True,
        index=True,
        help='Barcode app session identifier',
    )
    device_id = fields.Char(
        string='Device ID',
        help='Android device serial for fleet audit trail',
    )
    rssi = fields.Integer(
        string='RSSI (dBm)',
        help='Signal strength at scan time',
    )
    timestamp_ms = fields.Char(
        string='Client Timestamp (ms)',
        help='Client-side epoch timestamp in milliseconds',
    )
    tag_mapping_id = fields.Many2one(
        'rfid.tag.mapping',
        string='Tag Mapping',
        ondelete='set null',
        help='Resolved tag mapping record; null when EPC is unknown',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        ondelete='set null',
        help='Resolved product (denormalised for fast reporting)',
    )
    lot_id = fields.Many2one(
        'stock.lot',
        string='Lot / Serial',
        ondelete='set null',
        help='Resolved lot or serial number',
    )
    is_duplicate = fields.Boolean(
        string='Duplicate',
        default=False,
        help='True when server-side dedup identified this as a repeat within the 2-second window',
    )
    scan_status = fields.Selection(
        [('resolved', 'Resolved'), ('unknown', 'Unknown')],
        string='Scan Status',
        required=True,
        default='unknown',
    )
    relay_status = fields.Selection(
        [('relayed', 'Relayed'), ('queued', 'Queued'), ('buffered', 'Buffered')],
        string='Relay Status',
        required=True,
        default='queued',
    )
    operator_id = fields.Many2one(
        'res.users',
        string='Operator',
        ondelete='set null',
    )

    @api.constrains('epc')
    def _check_epc_format(self):
        for rec in self:
            if not EPC_RE.match((rec.epc or '').upper()):
                raise ValidationError(
                    f'Invalid EPC format: "{rec.epc}". '
                    'Must be exactly 24 uppercase hex characters (96-bit EPC).'
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'epc' in vals and vals['epc']:
                vals['epc'] = vals['epc'].upper()
        return super().create(vals_list)
