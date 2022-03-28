# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Profile - filter orders",

    'summary': """
       Extends portal with filters in the order section""",

    'description': """
        
    """,

    'author': "RL Software Development ApS",
    'website': "http://rlsd.dk/",

    'category': 'Website',
    'version': '15.0.1.0.3',

    'depends': [
        'website', 
        'portal',
        'sale'
        ],

    'data': [
        'views/portal_orders.xml', 
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
}