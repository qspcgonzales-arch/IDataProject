# -*- coding: utf-8 -*-
"""
rfid.calibration.profile — Hardware tuning settings for a warehouse zone.

Storing calibration as a structured ORM model (not ir.attachment) provides:
- Full CRUD API endpoints for Android to fetch and apply profiles
- Operators select profiles via a dropdown in the Android app
- Profiles update across the fleet instantly (no manual device updates)
- Audit trail of which profile was used for each counting session

Fields correspond directly to iData T1UHF / Zebra T1/T2 SDK parameters.
"""

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class RfidCalibrationProfile(models.Model):
    _name = 'rfid.calibration.profile'
    _description = 'RFID Calibration Profile'
    _order = 'name'

    name = fields.Char(
        string='Profile Name',
        required=True,
        index=True,
        help='Unique identifier shown to operators in the Android app (e.g., "zone_a_shelf_dense")',
    )
    zone = fields.Char(
        string='Zone',
        help='Warehouse zone this profile was calibrated for (e.g., "Zone A")',
    )
    description = fields.Text(
        string='Description',
        help='Human-readable notes about when and how this profile was validated',
    )
    # Core RFID hardware parameters
    power_dbm = fields.Integer(
        string='TX Power (dBm)',
        required=True,
        default=28,
        help='Transmit power in dBm. Range: 5–33 dBm typical for UHF handheld.',
    )
    session = fields.Selection(
        [('0', 'Session 0'), ('1', 'Session 1'), ('2', 'Session 2'), ('3', 'Session 3')],
        string='Session',
        required=True,
        default='1',
        help=(
            'RFID session parameter (Gen2 protocol). '
            'Session 1 is the recommended default for inventory adjustments.'
        ),
    )
    rssi_floor = fields.Integer(
        string='RSSI Floor (dBm)',
        required=True,
        default=-68,
        help=(
            'Minimum RSSI threshold. Tags below this value are filtered out '
            'to reduce cross-shelf over-reads. Typical range: -50 to -80 dBm.'
        ),
    )
    q_value = fields.Integer(
        string='Q Value',
        default=4,
        help=(
            'Anti-collision Q-value. Higher values reduce collisions in dense tag '
            'environments at the cost of throughput. Typical range: 2–8.'
        ),
    )
    # Validation metadata
    validated_date = fields.Date(
        string='Validated On',
        help='Date this profile was validated against live inventory',
    )
    accuracy_pct = fields.Float(
        string='Accuracy (%)',
        digits=(5, 2),
        help='Read accuracy percentage measured during calibration step 6 A/B test',
    )
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Calibration profile name must be unique.'),
    ]

    @api.constrains('power_dbm')
    def _check_power(self):
        for rec in self:
            if not (1 <= rec.power_dbm <= 33):
                raise ValidationError('TX Power must be between 1 and 33 dBm.')

    @api.constrains('rssi_floor')
    def _check_rssi(self):
        for rec in self:
            if not (-100 <= rec.rssi_floor <= 0):
                raise ValidationError('RSSI floor must be between -100 and 0 dBm.')

    @api.constrains('q_value')
    def _check_q_value(self):
        for rec in self:
            if rec.q_value is not False and not (0 <= rec.q_value <= 15):
                raise ValidationError('Q value must be between 0 and 15.')
