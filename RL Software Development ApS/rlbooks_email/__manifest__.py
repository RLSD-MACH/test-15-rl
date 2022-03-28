# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Email",

    'summary': """
       Gives extra email settings on contacts""",

    'description': """
        Long description of module's purpose
    """,

    'author': "RL Software Development ApS",
    'website': "http://rlsd.dk/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '15.0.1.0.3',

    # any module necessary for this one to work correctly
    'depends': [
        'contacts',
        'sale',
        'mail'
        ],

    # always loaded
    'data': [
        # 'views/res_partner_view.xml',
        # 'views/mail_compose_message_view.xml',
        # 'views/mail_mail_view.xml',
        'views/templates.xml',
        
        # 'security/ir.model.access.csv',
        # 'security/security.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
}