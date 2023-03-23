{
    'name': 'GAP V1 PARAGON REQUERIMIENTOS DE VENTAS E INVENTARIO',
    'sequence': -1001,
    'summary': 'Gap de paragon',
    'description': """Gap de paragon""",
    'depends': ['base_setup','stock','stock_barcode'],
    'data': [
        'views/stock_production_lot_form_inherit.xml',
            ],
    'auto_install': False,
    'application': True
}