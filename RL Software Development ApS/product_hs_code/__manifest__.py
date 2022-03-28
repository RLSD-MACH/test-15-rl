# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Product - HS Code",

    'summary': """
       Extends product template with HS Code""",

    'description': """
        
    """,

    'author': "RL Software Development ApS",
    'website': "http://rlsd.dk/",

    'category': 'Inventory',
    'version': '15.0.1.0.2',

    'depends': [
        'rlbooks_statement', 
        'delivery'
        ],

    'data': [
        'views/templates.xml', 
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
}