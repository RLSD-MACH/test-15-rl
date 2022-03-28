# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Remove Studio",

    'summary': """
       Tries to unlock, what should not be unlocked""",

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
        # 'contacts',
        # 'account'
        ],

    # always loaded
    'data': [
        # 'views/vies_message.xml',
        # 'views/res_partner.xml',
        # 'views/res_config_settings_views.xml',
        # 'security/ir.model.access.csv',
        # 'security/security.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
}