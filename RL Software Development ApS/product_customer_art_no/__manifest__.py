# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Product - customer_art_no",

    'summary': """
       Extends product template with customer_art_no""",

    'description': """
        
    """,

    'author': "RL Software Development ApS",
    'website': "http://rlsd.dk/",

    'category': 'Inventory',
    'version': '15.0.1.0.1',

    'depends': [
        'product', 
        ],

    'data': [
        'views/view_product_template.xml', 
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
}