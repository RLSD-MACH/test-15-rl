# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Sales - improvements Dashboards - community",

    'summary': """
       Improved overview of sales - Install Dashboards""",

    'description': """
        Contact Mads Christensen for more information
    """,

    'author': "RL Software Development ApS",
    'website': "http://rlsd.dk/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales/Sales',
    'version': '15.0.1.0.2',

    # any module necessary for this one to work correctly
    'depends': [
        'rlbooks_imp_sale','board', 'board_ext'
        ],

    # always loaded
    'data': [
        
        'views/view_sale.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
}