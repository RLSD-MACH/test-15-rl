# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Re-invoice services",

    'summary': """
       """,

    'description': """
        
    """,

    'author': "RL Software Development ApS",
    'website': "http://rlsd.dk/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '15.0.1.1.32',

    # any module necessary for this one to work correctly
    'depends': [
        'contacts',
        'mail',
        'sale',
        'account',
        'purchase',
        'base'
        ],

    # always loaded
    'data': [

        'wizard/account_move_select_outlays.xml',
        'wizard/outlay_connect_to_invoice.xml',
        'wizard/outlay_expense.xml',

        'data/ir_sequence_data.xml',
                
        'views/account_move.xml',
        'views/outlay.xml',

        'views/menuitem.xml',
        'views/res_config_settings.xml',
        
        'security/ir.model.access.csv',
        'security/security.xml',
        
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
}
