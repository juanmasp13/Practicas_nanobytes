{
    'name': 'GAP V1 PARAGON REQUERIMIENTOS DE VENTAS E INVENTARIO',
    'sequence': -1001,
    'summary': 'Gap de paragon',
    'description': """Gap de paragon""",
    'depends': ['base','stock','stock_barcode','web','account_financial_risk','sale','sale_stock','product'],
    'data': [
        'views/stock_production_lot_form_inherit.xml',
        'views/partner_risk_exceeded_view_inherit.xml',
        'views/sale_order_line_tree_inherit.xml',
        'models/view_stock_move_operations_inherit.xml',
        'views/stock_picking_form_inherit.xml',
            ],
    'auto_install': False,
    'assets': {
        'web.assets_backend': [
            'gap_paragon/static/src/js/escanear_productos.js',
        ],
        'web.assets_qweb': [
            'gap_paragon/static/src/xml/qty_at_date_widget_inherit.xml',
        ],
    },
    'application': True
}