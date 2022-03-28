# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Stock Accounts reconciliation",

    'summary': """
       Makes the reconciliation with account easier""",

    'description': """
        Contact Mads Christensen for more information
    """,

    'author': "RL Software Development ApS",
    'website': "http://www.rlsd.dk/",

    'category': 'Inventory/Inventory',
    'version': '15.0.1.0.7',

    # any module necessary for this one to work correctly
    'depends': [
        'account',
        'stock'
        ],

    # always loaded
    'data': [
        'views/account_move_line.xml'
    ],
    'price': 14.99,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
}