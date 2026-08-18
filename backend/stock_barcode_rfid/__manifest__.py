{
    'name': 'Stock Barcode RFID',
    'version': '19.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Integrate UHF RFID scanning into Odoo Barcode application',
    'description': """
        stock_barcode_rfid - RFID Bridge Module
        ========================================

        This module provides a bridge between Zebra T1/T2 UHF RFID readers and Odoo's native Barcode app.

        Features:
        - Accept RFID scans (EPCs) from Android app via HTTP endpoint
        - Server-side deduplication of rapid scans
        - Relay EPCs to Barcode app as synthetic barcode_scanned events
        - Support for Inventory Adjustments (cycle counts) workflow
        - Audit logging of all scans
        - Configurable rate limiting and dedup windows
        - API key management for Android app authentication

        Phase: 1-3 (in development)
        See: https://github.com/qspcgonzales-arch/IDataProject
    """,
    'author': 'IData Project',
    'license': 'AGPL-3',
    'depends': [
        'stock_barcode',
        'base',
    ],
    'data': [
        # Views
        'views/stock_barcode_rfid_views.xml',
        'views/ir_api_key_views.xml',

        # Security
        'security/ir.model.access.csv',

        # Data
        'data/ir_default_data.xml',
    ],
    'external_dependencies': {
        'python': [
            'requests',
            'pydantic',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
    'website': 'https://github.com/qspcgonzales-arch/IDataProject',
    'images': ['static/images/icon.png'],
}
