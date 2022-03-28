# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Stock Valuation Report Date",

    'summary': """
       Makes the Stock Valuation Report based on accounting date if possible""",

    'description': """
        Contact Mads Christensen for more information
    """,

    'author': "RL Software Development ApS",
    'website': "http://www.rlsd.dk/",

    'category': 'Inventory/Inventory',
    'version': '15.0.1.0.7',

    # any module necessary for this one to work correctly
    'depends': [
        'stock_account',
        'stock'
        ],

    # always loaded
    'data': [
        'wizards/stock_quantity_history.xml'
    ],
    'price': 14.99,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
}