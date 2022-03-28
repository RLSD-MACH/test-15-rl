# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Uniconta",

    'summary': """
       Integration to Uniconta""",

    'description': """
        Contact Mads Christensen for more information
    """,

    'author': "RL Software Development ApS",
    'website': "http://rlsd.dk/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '15.0.1.0.2',

    # any module necessary for this one to work correctly
    'depends': [
        'rlbooks_api',
        'contact_group'
        ],

    # always loaded
    'data': [      
        'views/uniconta_api_call_view.xml',
        'views/uniconta_firm_view.xml',
        'views/uniconta_login_view.xml',
        'views/uniconta_creditor_group_view.xml',
        # 'views/uniconta_creditor_view.xml',
        'views/uniconta_debtor_group_view.xml',
        'views/uniconta_partner_view.xml',
        'views/vies_menuitem.xml',
        'data/api_call_data.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
}