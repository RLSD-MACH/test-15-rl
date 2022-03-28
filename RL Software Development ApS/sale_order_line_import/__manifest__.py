# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Sale order line import",

    'summary': """
       Extends import function to use default code""",

    'description': """
        
    """,

    'author': "RL Software Development ApS",
    'website': "http://rlsd.dk/",

    'category': 'Sales/Sales',
    'version': '15.0.1.0.2',

    'depends': [
        'sale', 
        'product_customer_art_no',
        'excel_import_sale',
        ],

    'data': [
        'views/sale_order_line_import.xml',
        'views/sale_order.xml',

        'security/ir.model.access.csv',   
        'security/security.xml',   
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
}