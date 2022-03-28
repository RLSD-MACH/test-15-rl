# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Excel import - sale",

    'summary': """
       """,

    'description': """
        
    """,

    'author': "RL Software Development ApS",
    'website': "http://rlsd.dk/",

    'category': 'Accounting/Accounting',
    'version': '15.0.1.0.1',

    'depends': [
  
        'excel_import',
        'sale',
        
        ],

    'data': [

        'views/sale_order.xml'
        
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
}