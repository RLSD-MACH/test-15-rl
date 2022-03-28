# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Accounting approvals",

    'summary': """
       Send for approval.""",

    'description': """
        
    """,

    'author': "RL Software Development ApS",
    'website': "http://rlsd.dk/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '15.0.1.0.8',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account'
        ],

    # always loaded
    'data': [
        'data/mail_activity_type.xml',
        'views/account_move.xml',  
        'wizard/select_approver.xml',   
        'security/groups.xml',  
        'security/ir.model.access.csv',
        # 'security/security.xml',
        
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
}
