# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Grupos vistas',
    'version' : '1.2',
    'summary': 'Invoices & Payments',
    'sequence': 10,
    'description': """
        grupos
    """,
    'category': 'Accounting/Accounting',
    'depends' : ['base_setup','sale','sale_management'],
    'data': [
        'views/views_inherit.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
