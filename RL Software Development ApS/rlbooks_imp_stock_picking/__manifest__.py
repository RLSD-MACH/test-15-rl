# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Stock picking - improvments",

    'summary': """
       Customised actions """,

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
        'stock',
        'sale',
        'purchase',
        'sale_stock'
        ],

    # always loaded
    'data': [
        'views/view_stock_picking.xml',
        'views/view_partner.xml',
        # 'wizard/stock_picking_type_wizard_view.xml',
        # 'security/ir.model.access.csv',
        # 'security/security.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
}