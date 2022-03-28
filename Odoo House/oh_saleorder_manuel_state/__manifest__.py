# -*- coding: utf-8 -*-
{
    'name': "Sale Order Manual Invoiced State",

    'summary': """
        Sale Order - manual invoiced state""",

    'description': """Manual invoiced state
    """,

    'author': "Odoo House",
    'website': "https://odoohouse.dk",
    'category': 'Extra',
    'version': '1.0',
    'depends': ['base','sale',],
    'data': [
        'views/pace_so.xml',
    ],
}