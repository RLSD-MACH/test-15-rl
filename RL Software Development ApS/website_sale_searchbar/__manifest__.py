# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Shop - searchbar ext",

    'summary': """
       Extends searchbar with barcode, customer art no and internal reference""",

    'description': """
        
    """,

    'author': "RL Software Development ApS",
    'website': "http://rlsd.dk/",

    'category': 'Website',
    'version': '15.0.1.0.1',

    'depends': [
        'website', 
        'portal',
        'website_sale',
        'rlbooks_imp_sale',
        'product'
        ],

    'data': [
        'views/searchbar.xml', 
    ],
    'qweb': ['static/src/snippets/s_searchbar/000.xml'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
}