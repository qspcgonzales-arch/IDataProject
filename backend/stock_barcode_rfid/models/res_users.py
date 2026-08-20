# -*- coding: utf-8 -*-
"""
Extension to res.users for RFID operator management.

Adds convenience fields so warehouse managers can see which operators have
active RFID device keys and review per-operator scan history.
"""

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    rfid_scan_count = fields.Integer(
        string='Total RFID Scans',
        compute='_compute_rfid_scan_count',
        store=False,
        help='Total number of RFID scans submitted by this operator.',
    )

    def _compute_rfid_scan_count(self):
        for user in self:
            user.rfid_scan_count = self.env['stock.barcode.rfid.scan'].search_count(
                [('operator_id', '=', user.id)]
            )
