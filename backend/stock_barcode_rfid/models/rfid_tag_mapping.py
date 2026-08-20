# -*- coding: utf-8 -*-
"""
rfid.tag.mapping — Maps a raw EPC to a product/lot via one of three encoding scenarios.

Scenario 1 — Supplier tags
    Supplier ships items with pre-printed RFID tags.  The EPC encodes a standard
    barcode (EAN-13/14) that Odoo already has on product.product.barcode.
    Field used: barcode

Scenario 2 — In-house encoded tags
    Your team writes the product barcode into the tag using an RFID encoder.
    The EPC carries your internal barcode; resolved the same way as Scenario 1.
    Field used: barcode + encoding_type='in_house'

Scenario 3 — Non-standard / proprietary EPC
    Supplier uses a proprietary EPC format that cannot be decoded to a standard
    barcode.  The operator manually maps the raw EPC to the product's serial
    number in Odoo.  Future scans resolve via serial.
    Field used: serial_number + encoding_type='non_standard'
"""

from odoo import fields, models, api
from odoo.exceptions import ValidationError
import re

EPC_RE = re.compile(r'^[0-9A-F]{24}$')


class RfidTagMapping(models.Model):
    _name = 'rfid.tag.mapping'
    _description = 'RFID Tag → Product/Lot Mapping'
    _order = 'create_date desc'

    epc = fields.Char(
        string='EPC',
        required=True,
        index=True,
        copy=False,
        help='96-bit EPC in uppercase hex (24 characters). Must be unique.',
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        ondelete='restrict',
    )
    lot_id = fields.Many2one(
        'stock.lot',
        string='Lot / Serial',
        ondelete='set null',
        help='Optional lot or serial number linkage',
    )
    # Scenario 1 & 2: resolved via barcode field
    barcode = fields.Char(
        string='Barcode',
        help='EAN-13/14 or internal barcode encoded in the EPC (Scenarios 1 & 2)',
    )
    # Scenario 3: resolved via serial number
    serial_number = fields.Char(
        string='Serial Number',
        help='Proprietary serial number from supplier EPC (Scenario 3)',
    )
    encoding_type = fields.Selection(
        [
            ('supplier', 'Supplier Tag'),
            ('in_house', 'In-House Encoded'),
            ('non_standard', 'Non-Standard EPC'),
        ],
        string='Encoding Type',
        required=True,
        default='supplier',
        help=(
            'supplier: EPC encodes a standard barcode from the supplier. '
            'in_house: Your team encoded a barcode into the tag. '
            'non_standard: Proprietary EPC; mapped manually via serial number.'
        ),
    )
    last_scanned = fields.Datetime(
        string='Last Scanned',
        readonly=True,
    )
    scan_count = fields.Integer(
        string='Scan Count',
        default=0,
        readonly=True,
    )
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('epc_unique', 'UNIQUE(epc)', 'EPC must be unique across all tag mappings.'),
    ]

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

    def write(self, vals):
        if 'epc' in vals and vals['epc']:
            vals['epc'] = vals['epc'].upper()
        return super().write(vals)

    def record_scan(self):
        """Increment scan counter and update last_scanned timestamp."""
        self.write({
            'last_scanned': fields.Datetime.now(),
            'scan_count': self.scan_count + 1,
        })
