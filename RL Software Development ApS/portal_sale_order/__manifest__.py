# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Portal - sale order",

    'summary': """
       Extends portal for sale orders""",

    'description': """
        
    """,

    'author': "RL Software Development ApS",
    'website': "http://rlsd.dk/",

    'category': 'Website',
    'version': '15.0.1.0.3',

    'depends': [
        'website', 
        'portal',
        'sale',
        'purchase',
        'product_customer_art_no',
        'sale_management',
        ],

    'data': [
        'views/templates.xml', 
        'views/portal_sale_orders.xml', 
        'views/portal_purchase_orders.xml', 
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
}