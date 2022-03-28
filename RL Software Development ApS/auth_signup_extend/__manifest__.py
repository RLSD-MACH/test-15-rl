# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Extend auth_signup",

    'summary': """
       """,

    'description': """
        Contact Mads Christensen for more information
    """,

    'author': "RL Software Development ApS",
    'website': "http://www.rlsd.dk/",

    'category': 'Accounting/Accounting',
    'version': '15.0.1.0.2',

    # any module necessary for this one to work correctly
    'depends': [
        'auth_signup',
        ],

    # always loaded
    'data': [
        'views/templates.xml'
    ],
    'price': 14.99,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
}