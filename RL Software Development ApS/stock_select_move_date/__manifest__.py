# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Stock - select move date",

    'summary': """
       """,

    'description': """
        
    """,

    'author': "RL Software Development ApS",
    'website': "http://rlsd.dk/",

    'category': 'Inventory',
    'version': '15.0.1.1.4',

    'depends': [
        'stock_account', 
        'stock', 
        ],

    'data': [
        'views/stock_picking.xml',
        'views/stock_valuation_layer.xml',
        
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
}