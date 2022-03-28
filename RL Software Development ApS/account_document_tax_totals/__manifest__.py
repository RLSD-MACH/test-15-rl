# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Account - template update",

    'summary': """
       Extends account document_tax_totals and account.tax_groups_totals""",

    'description': """
        
    """,

    'author': "RL Software Development ApS",
    'website': "http://rlsd.dk/",

    'category': 'Website',
    'version': '15.0.1.0.0',

    'depends': [
        'account', 
        ],

    'data': [
        'views/template.xml', 
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
}