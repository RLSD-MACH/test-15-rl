# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Filter by Fiscal Position",

    'summary': """
       Makes it possible to filter by Partner Fiscal Position in Aged Recievables and Aged Payables""",

    'description': """
        Contact Mads Christensen for more information
    """,

    'author': "RL Software Development ApS",
    'website': "http://www.rlsd.dk/",

    'category': 'Accounting/Accounting',
    'version': '15.0.1.0.5',

    # any module necessary for this one to work correctly
    'depends': [
        'account_reports'
        ],

    # always loaded
    'data': [
        'views/search_template_view.xml'
    ],
    'price': 14.99,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
}