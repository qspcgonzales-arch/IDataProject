{
    'name': 'Stock Barcode RFID',
    'version': '19.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Custom UHF RFID scanning bridge for Odoo 19 Community',
    'description': """
        stock_barcode_rfid - RFID Bridge Module
        ========================================

        Custom RFID scanning integration for Odoo 19 Community, built for the
        iData T1UHF handheld exclusively. Odoo Community does not include the
        Enterprise-only stock_barcode app or Barcode Nomenclature-driven RFID
        path, so this module implements its own EPC resolution, audit log,
        and live scan UI rather than depending on stock_barcode.

        Features:
        - rfid.tag.mapping: EPC <-> product mapping (reuses standard Barcode
          and Serial Number fields on product.product; no Barcode Nomenclature)
        - stock.barcode.rfid.scan: audit log of every scan (resolved/unknown/discrepancy)
        - POST /stock_barcode_rfid/scan: accepts EPCs from the Android app
        - Server-side dedup (2-second window, keyed on EPC)
        - Custom OWL/QWeb scan UI fed via SSE/long-poll (no dependency on
          stock_barcode's Enterprise-only barcode_scanned event bus)
        - API key auth: auth='public' route + manual key check against
          res.users.apikeys inside the controller (not auth='bearer')

        Phase: 1-2 (in development)
        See: https://github.com/qspcgonzales-arch/IDataProject
    """,
    'author': 'IData Project',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
    ],
    'external_dependencies': {
        'python': [],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
    'website': 'https://github.com/qspcgonzales-arch/IDataProject',
}
