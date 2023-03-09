{
    'name': 'GAP V1 LANDSCAPE CONDICIONES LEGALES',
    'sequence': -1005,
    'summary': 'Añadir botón para los términos legales',
    'description': """Botón para los términos legales de la compra""",
    'depends': ['website_sale','web','base','website'],
    'data': ['views/inherit_web_purchase.xml'],
    'auto_install': False,
    'assets': {
        'web.assets_frontend': [
            'gap_LANDSCAPE_TERMINOS/static/src/js/boton_terminos.js',
            'gap_LANDSCAPE_TERMINOS/static/src/css/clase_disabled.css',
        ],
    },
    'application': True
}