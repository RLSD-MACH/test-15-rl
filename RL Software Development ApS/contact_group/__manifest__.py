# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Contact group",

    'summary': """
        Add a comtact group""",

    'description': """
        
    """,

    'author': "RL Software Development ApS",
    'website': "http://rlsd.dk/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales/CRM',
    'version': '15.0.1.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        # 'base',
        # 'sale',
        # 'account',
        'contacts'
        ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/view_partner.xml',
        'views/partner_group.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
}