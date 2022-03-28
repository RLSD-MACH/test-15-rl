# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Excel import - stock picking",

    'summary': """
       """,

    'description': """
        
    """,

    'author': "RL Software Development ApS",
    'website': "http://rlsd.dk/",

    'category': 'Accounting/Accounting',
    'version': '15.0.1.0.2',

    'depends': [
  
        'excel_import',
        'stock',
        
        ],

    'data': [

        'views/stock_picking.xml'
        
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
}