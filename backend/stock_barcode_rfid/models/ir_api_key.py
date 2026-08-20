# -*- coding: utf-8 -*-
"""
Extension to ir.api.key for RFID-specific auth tracking.

Adds a flag so Android devices can be identified as RFID operators and
rate-limit thresholds can be configured per key.
"""

from odoo import fields, models


class IrApiKey(models.Model):
    _inherit = 'ir.api.key'

    is_rfid_device = fields.Boolean(
        string='RFID Device Key',
        default=False,
        help='Mark this API key as belonging to an Android RFID scanner device.',
    )
    rfid_device_serial = fields.Char(
        string='Device Serial',
        help='iData T1UHF or Zebra device serial number associated with this key.',
    )
    rfid_rate_limit = fields.Integer(
        string='Rate Limit (req/min)',
        default=100,
        help='Maximum scan POST requests per minute for this device key.',
    )
