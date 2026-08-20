# -*- coding: utf-8 -*-
"""
HTTP Controllers for stock_barcode_rfid.

Endpoints
---------
POST /stock_barcode_rfid/scan
    Accept an EPC from the Android app.  Validates format, performs server-side
    dedup, resolves via rfid.tag.mapping, writes an audit record, and returns
    a structured JSON response.

POST /stock_barcode_rfid/session/create
    Create a new RFID scan session linked to an active Barcode app session.

POST /stock_barcode_rfid/session/<session_id>/poll
    Long-poll endpoint: returns new scan events since last_scan_id.

GET  /stock_barcode_rfid/calibration/profiles
    List calibration profiles available for a warehouse.

POST /stock_barcode_rfid/calibration/profiles
    Create a new calibration profile (admin only).

PUT  /stock_barcode_rfid/calibration/profiles/<profile_id>
    Update an existing calibration profile (admin only).

DELETE /stock_barcode_rfid/calibration/profiles/<profile_id>
    Delete a calibration profile (admin only).

POST /stock_barcode_rfid/tag_mapping
    Create an EPC → product mapping.

POST /stock_barcode_rfid/write_tags
    Batch-create EPC mappings for in-house encoding (Scenario 2).

PUT  /stock_barcode_rfid/tag_mapping/<mapping_id>
    Update an existing tag mapping (used for Scenario 3 unknown-EPC flow).
"""

import json
import re
import logging
from datetime import datetime, timedelta, timezone

from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)

EPC_RE = re.compile(r'^[0-9A-Fa-f]{24}$')
# Server-side dedup window in seconds
DEDUP_WINDOW_SEC = 2


def _json_response(data, status=200):
    return Response(
        json.dumps(data),
        status=status,
        mimetype='application/json',
    )


def _error(message, details='', status=400):
    return _json_response({'success': False, 'error': message, 'details': details}, status=status)


def _validate_epc(epc):
    """Return normalised uppercase EPC or None if invalid."""
    if not epc or not isinstance(epc, str):
        return None
    epc = epc.strip().upper()
    return epc if EPC_RE.match(epc) else None


class RfidScanController(http.Controller):
    # ------------------------------------------------------------------
    # POST /stock_barcode_rfid/scan
    # ------------------------------------------------------------------
    @http.route(
        '/stock_barcode_rfid/scan',
        type='http',
        auth='api_key',
        methods=['POST'],
        csrf=False,
    )
    def post_scan(self, **kwargs):
        """Accept an EPC scan from the Android app."""
        try:
            body = json.loads(request.httprequest.data or '{}')
        except (json.JSONDecodeError, ValueError):
            return _error('Invalid JSON body')

        epc_raw = body.get('epc', '')
        epc = _validate_epc(epc_raw)
        if not epc:
            return _error(
                'Invalid EPC format',
                f'EPC must be 24 hex characters, got: {epc_raw!r}',
            )

        session_id = body.get('session_id', '')
        if not session_id:
            return _error('Missing session_id')

        rssi = body.get('rssi')
        timestamp_ms = body.get('timestamp_ms')
        device_id = body.get('device_id', '')

        env = request.env

        # --- Server-side dedup -------------------------------------------
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=DEDUP_WINDOW_SEC)
        recent = env['stock.barcode.rfid.scan'].sudo().search([
            ('epc', '=', epc),
            ('session_id', '=', session_id),
            ('create_date', '>=', cutoff.strftime('%Y-%m-%d %H:%M:%S')),
        ], limit=1)
        is_duplicate = bool(recent)

        # --- EPC resolution via rfid.tag.mapping -------------------------
        mapping = env['rfid.tag.mapping'].sudo().search([('epc', '=', epc)], limit=1)
        scan_status = 'resolved' if mapping else 'unknown'
        product_id = mapping.product_id.id if mapping else None
        product_name = mapping.product_id.display_name if mapping else None
        lot_id = mapping.lot_id.id if mapping else None
        lot_name = mapping.lot_id.name if mapping else None

        if mapping:
            mapping.sudo().record_scan()

        # --- Write audit record ------------------------------------------
        operator = request.env.user
        scan_vals = {
            'epc': epc,
            'session_id': session_id,
            'device_id': device_id,
            'rssi': rssi,
            'timestamp_ms': str(timestamp_ms) if timestamp_ms is not None else False,
            'tag_mapping_id': mapping.id if mapping else False,
            'product_id': product_id,
            'lot_id': lot_id,
            'is_duplicate': is_duplicate,
            'scan_status': scan_status,
            'relay_status': 'queued',
            'operator_id': operator.id if operator else False,
        }
        scan_rec = env['stock.barcode.rfid.scan'].sudo().create(scan_vals)

        return _json_response({
            'success': True,
            'scan_id': f'stock.barcode.rfid.scan_{scan_rec.id}',
            'tag_mapping_id': mapping.id if mapping else None,
            'product_id': product_id,
            'product_name': product_name,
            'lot_id': lot_id,
            'lot_name': lot_name,
            'is_duplicate': is_duplicate,
            'scan_status': scan_status,
            'relay_status': 'queued',
            'message': 'EPC accepted, relaying to Barcode app',
        })

    # ------------------------------------------------------------------
    # POST /stock_barcode_rfid/session/create
    # ------------------------------------------------------------------
    @http.route(
        '/stock_barcode_rfid/session/create',
        type='http',
        auth='api_key',
        methods=['POST'],
        csrf=False,
    )
    def create_session(self, **kwargs):
        """Create a new RFID scan session."""
        try:
            body = json.loads(request.httprequest.data or '{}')
        except (json.JSONDecodeError, ValueError):
            return _error('Invalid JSON body')

        barcode_session_id = body.get('barcode_session_id', '')
        if not barcode_session_id:
            return _error('Missing barcode_session_id')

        # TODO (Aug 31): Link to rfid.scan.session model once implemented
        return _json_response({
            'success': True,
            'rfid_session_id': f'rfid_session_{barcode_session_id}',
            'message': 'Session created, operator can start scanning',
        }, status=201)

    # ------------------------------------------------------------------
    # POST /stock_barcode_rfid/session/<session_id>/poll
    # ------------------------------------------------------------------
    @http.route(
        '/stock_barcode_rfid/session/<string:session_id>/poll',
        type='http',
        auth='api_key',
        methods=['POST'],
        csrf=False,
    )
    def poll_session(self, session_id, **kwargs):
        """Long-poll: return new scan events since last_scan_id."""
        try:
            body = json.loads(request.httprequest.data or '{}')
        except (json.JSONDecodeError, ValueError):
            return _error('Invalid JSON body')

        last_scan_id_str = body.get('last_scan_id', '')
        last_id = 0
        if last_scan_id_str:
            try:
                last_id = int(last_scan_id_str.split('_')[-1])
            except (ValueError, IndexError):
                pass

        domain = [('session_id', '=', session_id), ('id', '>', last_id)]
        scans = request.env['stock.barcode.rfid.scan'].sudo().search(domain, order='id asc', limit=50)

        events = []
        for s in scans:
            events.append({
                'event': 'barcode_scanned',
                'epc': s.epc,
                'product_id': s.product_id.id if s.product_id else None,
                'lot_id': s.lot_id.id if s.lot_id else None,
                'scan_status': s.scan_status,
                'scan_id': f'stock.barcode.rfid.scan_{s.id}',
            })

        return _json_response({'success': True, 'events': events})

    # ------------------------------------------------------------------
    # Calibration profile endpoints
    # ------------------------------------------------------------------
    @http.route(
        '/stock_barcode_rfid/calibration/profiles',
        type='http',
        auth='api_key',
        methods=['GET'],
        csrf=False,
    )
    def list_calibration_profiles(self, **kwargs):
        """List calibration profiles, optionally filtered by warehouse."""
        profiles = request.env['rfid.calibration.profile'].sudo().search([('active', '=', True)])
        result = []
        for p in profiles:
            result.append({
                'name': p.name,
                'zone': p.zone or '',
                'power_dbm': p.power_dbm,
                'session': p.session,
                'rssi_floor': p.rssi_floor,
                'q_value': p.q_value,
                'description': p.description or '',
            })
        return _json_response({'success': True, 'profiles': result})

    @http.route(
        '/stock_barcode_rfid/calibration/profiles',
        type='http',
        auth='api_key',
        methods=['POST'],
        csrf=False,
    )
    def create_calibration_profile(self, **kwargs):
        """Create a calibration profile (admin only)."""
        if not request.env.user.has_group('stock.group_stock_manager'):
            return _error('Forbidden', 'Only stock managers can create calibration profiles.', status=403)
        try:
            body = json.loads(request.httprequest.data or '{}')
        except (json.JSONDecodeError, ValueError):
            return _error('Invalid JSON body')

        required = ('name', 'power_dbm', 'session', 'rssi_floor')
        missing = [f for f in required if f not in body]
        if missing:
            return _error('Missing required fields', f'Required: {missing}')

        profile = request.env['rfid.calibration.profile'].sudo().create({
            'name': body['name'],
            'zone': body.get('zone', ''),
            'power_dbm': int(body['power_dbm']),
            'session': str(body['session']),
            'rssi_floor': int(body['rssi_floor']),
            'q_value': int(body.get('q_value', 4)),
            'description': body.get('description', ''),
        })
        return _json_response({
            'success': True,
            'profile_id': profile.id,
            'message': 'Profile created. Download to devices via app settings.',
        }, status=201)

    @http.route(
        '/stock_barcode_rfid/calibration/profiles/<int:profile_id>',
        type='http',
        auth='api_key',
        methods=['PUT'],
        csrf=False,
    )
    def update_calibration_profile(self, profile_id, **kwargs):
        """Update an existing calibration profile (admin only)."""
        if not request.env.user.has_group('stock.group_stock_manager'):
            return _error('Forbidden', 'Only stock managers can update calibration profiles.', status=403)
        profile = request.env['rfid.calibration.profile'].sudo().browse(profile_id)
        if not profile.exists():
            return _error('Profile not found', f'Profile ID {profile_id} does not exist.', status=404)
        try:
            body = json.loads(request.httprequest.data or '{}')
        except (json.JSONDecodeError, ValueError):
            return _error('Invalid JSON body')
        allowed = ('power_dbm', 'session', 'rssi_floor', 'q_value', 'description', 'zone', 'name')
        vals = {k: v for k, v in body.items() if k in allowed}
        profile.write(vals)
        return _json_response({'success': True, 'profile_id': profile.id, 'message': 'Profile updated.'})

    @http.route(
        '/stock_barcode_rfid/calibration/profiles/<int:profile_id>',
        type='http',
        auth='api_key',
        methods=['DELETE'],
        csrf=False,
    )
    def delete_calibration_profile(self, profile_id, **kwargs):
        """Delete a calibration profile (admin only)."""
        if not request.env.user.has_group('stock.group_stock_manager'):
            return _error('Forbidden', 'Only stock managers can delete calibration profiles.', status=403)
        profile = request.env['rfid.calibration.profile'].sudo().browse(profile_id)
        if not profile.exists():
            return _error('Profile not found', f'Profile ID {profile_id} does not exist.', status=404)
        profile.unlink()
        return _json_response({'success': True, 'message': 'Profile deleted.'})

    # ------------------------------------------------------------------
    # Tag mapping endpoints
    # ------------------------------------------------------------------
    @http.route(
        '/stock_barcode_rfid/tag_mapping',
        type='http',
        auth='api_key',
        methods=['POST'],
        csrf=False,
    )
    def create_tag_mapping(self, **kwargs):
        """Create an EPC → product mapping."""
        try:
            body = json.loads(request.httprequest.data or '{}')
        except (json.JSONDecodeError, ValueError):
            return _error('Invalid JSON body')

        epc = _validate_epc(body.get('epc', ''))
        if not epc:
            return _error('Invalid EPC format', f'Got: {body.get("epc")!r}')

        product_id = body.get('product_id')
        if not product_id:
            return _error('Missing product_id')

        encoding_type = body.get('encoding_type', 'supplier')
        if encoding_type not in ('supplier', 'in_house', 'non_standard'):
            return _error('Invalid encoding_type', 'Must be supplier, in_house, or non_standard')

        mapping = request.env['rfid.tag.mapping'].sudo().create({
            'epc': epc,
            'product_id': int(product_id),
            'encoding_type': encoding_type,
            'lot_id': body.get('lot_id') or False,
            'barcode': body.get('barcode', ''),
            'serial_number': body.get('serial_number', ''),
        })
        return _json_response({
            'success': True,
            'tag_mapping_id': mapping.id,
            'message': 'EPC mapped to product.',
        }, status=201)

    @http.route(
        '/stock_barcode_rfid/write_tags',
        type='http',
        auth='api_key',
        methods=['POST'],
        csrf=False,
    )
    def write_tags(self, **kwargs):
        """Batch-create EPC mappings for in-house encoding (Scenario 2)."""
        try:
            body = json.loads(request.httprequest.data or '{}')
        except (json.JSONDecodeError, ValueError):
            return _error('Invalid JSON body')

        product_id = body.get('product_id')
        epc_list = body.get('epc_list', [])
        if not product_id:
            return _error('Missing product_id')
        if not epc_list or not isinstance(epc_list, list):
            return _error('epc_list must be a non-empty list')

        product = request.env['product.product'].sudo().browse(int(product_id))
        if not product.exists() or not product.barcode:
            return _error('Product not found or missing barcode', 'Product must have a barcode set.')

        written, failed, ids = 0, 0, []
        for raw_epc in epc_list:
            epc = _validate_epc(raw_epc)
            if not epc:
                failed += 1
                continue
            try:
                rec = request.env['rfid.tag.mapping'].sudo().create({
                    'epc': epc,
                    'product_id': product.id,
                    'encoding_type': 'in_house',
                    'barcode': product.barcode,
                })
                ids.append(rec.id)
                written += 1
            except Exception as e:
                _logger.warning('write_tags: failed for EPC %s: %s', epc, e)
                failed += 1

        return _json_response({
            'success': True,
            'written_count': written,
            'failed_count': failed,
            'tag_mapping_ids': ids,
        }, status=201)

    @http.route(
        '/stock_barcode_rfid/tag_mapping/<int:mapping_id>',
        type='http',
        auth='api_key',
        methods=['PUT'],
        csrf=False,
    )
    def update_tag_mapping(self, mapping_id, **kwargs):
        """Update a tag mapping (Scenario 3 unknown-EPC discrepancy workflow)."""
        mapping = request.env['rfid.tag.mapping'].sudo().browse(mapping_id)
        if not mapping.exists():
            return _error('Mapping not found', f'Tag mapping ID {mapping_id} does not exist.', status=404)

        try:
            body = json.loads(request.httprequest.data or '{}')
        except (json.JSONDecodeError, ValueError):
            return _error('Invalid JSON body')

        allowed = ('serial_number', 'encoding_type', 'barcode', 'lot_id', 'product_id')
        vals = {k: v for k, v in body.items() if k in allowed}
        mapping.write(vals)
        return _json_response({
            'success': True,
            'tag_mapping_id': mapping.id,
            'message': 'Mapping updated. Rescan tag to resolve.',
        })
