# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "CVR control before VIES",

    'summary': """
       """,

    'description': """
        
    """,

    'author': "RL Software Development ApS",
    'website': "http://rlsd.dk/",

    'category': 'Accounting/Accounting',
    'version': '15.0.1.0.7',

    'depends': [

        'contacts',     
        'account',
        'sale_management',
        'base_vat',
        'cvr', 
        'vies', 
        
        ],

    'data': [

        'views/res_partner.xml',
        
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
}