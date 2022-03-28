# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "CVR",

    'summary': """
       Verify DK VAT-numbers and save the history of authenications as documentation.""",

    'description': """
    
    """,

    'author': "RL Software Development ApS",
    'website': "http://rlsd.dk/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '15.0.1.0.7',

    # any module necessary for this one to work correctly
    'depends': [
        'contacts',     
        'account',
        'sale_management',
        'base_vat'
        ],

    # always loaded
    'data': [
        'views/cvr_message.xml',
        'views/res_partner.xml',
        'views/view_account_move.xml',
        'views/view_sale_order.xml',
        'views/res_config_settings_views.xml',
        'views/menuitem.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/scheduled_actions.xml',
    ],
    'price': 200.0,
    'currency': 'EUR',
    'support': 'support@rlsd.dk',
    # 'live_test_url': '',
    "images":[
        'static/description/icon.png',
        
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
}

