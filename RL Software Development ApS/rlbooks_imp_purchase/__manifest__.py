# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Purchase - improvements",

    'summary': """
       Impored overview of purchase""",

    'description': """
        Contact Mads Christensen for more information
    """,

    'author': "RL Software Development ApS",
    'website': "http://rlsd.dk/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Inventory/Purchase',
    'version': '15.0.1.0.9',

    # any module necessary for this one to work correctly
    'depends': [
        'purchase',
        'account',
        'base'   
        ],

    # always loaded
    'data': [
        'views/view_purchase.xml',
        'views/view_partner.xml',
        'views/view_product_template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
}