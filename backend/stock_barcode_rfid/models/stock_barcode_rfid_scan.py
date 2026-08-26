# -*- coding: utf-8 -*-
"""
stock.barcode.rfid.scan

Audit log of every RFID scan received via POST /stock_barcode_rfid/scan,
whether it resolved to a known product, came back unknown, or needs
operator review as a discrepancy. Unknown/unmapped EPCs are always
logged here rather than silently dropped (Rev. 2 roadmap, Success
Criteria and Section 2 "Discrepancies" pattern).
"""

from odoo import fields, models


class StockBarcodeRfidScan(models.Model):
    _name = 'stock.barcode.rfid.scan'
    _description = 'RFID Scan Audit Log'
    _order = 'create_date desc'
    _rec_name = 'epc'

    epc = fields.Char(
        string='EPC',
        required=True,
        index=True,
        help='Raw EPC as read from the iData T1UHF tag.',
    )
    rssi = fields.Float(
        string='RSSI (dBm)',
        help='Signal strength reported by the reader for this scan.',
    )
    tag_mapping_id = fields.Many2one(
        'rfid.tag.mapping',
        string='Tag Mapping',
        help='The mapping this EPC resolved against, if any.',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        help='Denormalized from tag_mapping_id for easier reporting; '
             'left empty when status is unknown.',
    )
    lot_id = fields.Many2one(
        'stock.lot',
        string='Lot/Serial',
    )
    status = fields.Selection(
        selection=[
            ('resolved', 'Resolved'),
            ('unknown', 'Unknown'),
            ('discrepancy', 'Discrepancy'),
        ],
        string='Status',
        required=True,
        default='unknown',
        index=True,
        help='resolved: matched rfid.tag.mapping. unknown: no mapping '
             'found, logged for operator resolution, never dropped. '
             'discrepancy: resolved but flagged for manual review '
             '(e.g. quantity mismatch).',
    )
    is_duplicate = fields.Boolean(
        default=False,
        help='True if this scan fell within the 2-second server-side '
             'dedup window of a prior scan of the same EPC.',
    )
    session_id = fields.Char(
        string='Scan Session',
        index=True,
        help='Android app scan session identifier.',
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Location',
        index=True,
        help='The stock location this scan session is counting against. '
             'Odoo 14+ (including v19) does inventory adjustments '
             'directly against stock.quant/stock.location; there is no '
             'separate stock.inventory model to reference.',
    )
    scanned_at = fields.Datetime(
        string='Scanned At',
        required=True,
        default=fields.Datetime.now,
    )
