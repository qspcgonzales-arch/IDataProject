# -*- coding: utf-8 -*-
"""
rfid.tag.mapping

EPC <-> product mapping for the iData T1UHF RFID bridge.

Reuses standard Barcode (EAN-13/14) and Serial Number fields on
product.product rather than Odoo's Barcode Nomenclature, because
Nomenclature has no way to represent status='unknown' for an
unrecognized EPC (Rev. 2 roadmap, Section 2).

encoding_type reflects which of the three Ventor-pattern scenarios
produced the mapping:
- supplier: EPC resolves via an exact match against product.barcode
- in_house: written in bulk via POST /stock_barcode_rfid/write_tags
- non_standard: EPC doesn't decode to a barcode; operator manually
  attaches it via product.product's Serial Number field instead
"""

from odoo import fields, models


class RfidTagMapping(models.Model):
    _name = 'rfid.tag.mapping'
    _description = 'RFID Tag to Product Mapping'
    _rec_name = 'epc'

    epc = fields.Char(
        string='EPC',
        required=True,
        index=True,
        copy=False,
        help='96-bit EPC (24 hex chars) read from the iData T1UHF tag.',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        ondelete='cascade',
    )
    barcode = fields.Char(
        string='Barcode',
        help='EAN-13/14 barcode this EPC resolves to, if supplier-encoded.',
    )
    serial_number = fields.Char(
        string='Serial Number',
        help='Manually-entered value for non-standard EPCs that do not '
             'decode to a barcode.',
    )
    encoding_type = fields.Selection(
        selection=[
            ('supplier', 'Supplier pre-encoded'),
            ('in_house', 'In-house write'),
            ('non_standard', 'Non-standard EPC'),
        ],
        string='Encoding Type',
        required=True,
        default='in_house',
    )
    lot_id = fields.Many2one(
        'stock.lot',
        string='Lot/Serial',
        help='Optional. Never required — an unmapped lot must not block '
             'the unknown-EPC workflow.',
    )
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            'epc_unique',
            'unique(epc)',
            'This EPC is already mapped to a product.',
        ),
    ]
