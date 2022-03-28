# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright Domiup (<http://domiup.com>).
#
##############################################################################

{
    'name': 'Import Sale Order Line',
    'version': '14.0.1.0',
    'category': 'Tools',
    'description': """
        Import sale order lines from CSV / Excel file using Odoo native interface
    """,
    'summary': '''
        Import sale order lines from CSV / Excel file using Odoo native interface
    ''',
    'live_test_url': 'https://demo14.domiup.com',
    'author': 'Domiup',
    'price': 25,
    'currency': 'EUR',
    'license': 'OPL-1',
    'support': 'domiup.contact@gmail.com',
    'website': 'https://youtu.be/K2d4ODpJr0I',
    'depends': [
        'base_import_line',
        'sale',
    ],
    'data': [
        'views/sales.xml'
    ],

    'test': [],
    'demo': [],
    'images': ['static/description/banner.jpg'],
    'installable': True,
    'active': False,
    'application': True,
}
