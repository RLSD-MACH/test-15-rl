# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Sales - improvements",

    'summary': """
       Improved overview of sales""",

    'description': """
        Contact Mads Christensen for more information
    """,

    'author': "RL Software Development ApS",
    'website': "http://rlsd.dk/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales/Sales',
    'version': '15.0.1.0.14',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sale',
        'account',
        'purchase',
        'sale_stock',
        'sale_purchase',
        'stock',
        'product_customer_art_no'  
        ],

    # always loaded
    'data': [
        'views/view_account_move.xml',
        'views/view_sale.xml',
        'views/view_partner.xml',
        'views/view_product_template.xml',
        'views/res_company_views.xml',
        'views/res_config_settings_views.xml',
        
        'security/ir.model.access.csv',   
        'security/security.xml',   
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
}