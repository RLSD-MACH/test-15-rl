# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.

{
    'name': "Accounting joint",

    'summary': """
       One accountschema for all compnies - one reporting system - one common currency""",

    'description': """
        Contact Mads Christensen for more information
    """,

    'author': "RL Software Development ApS",
    'website': "http://rlsd.dk/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '15.0.1.0.1',

    # any module necessary for this one to work correctly
    'depends': [
         'account'
        ],

    # always loaded
    'data': [      
        'views/account_move.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
    
}