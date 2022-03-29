# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Picking Workflow",

    'summary': """
       Stock picking workflow.""",

    'description': """
        
    """,

    'author': "RL Software Development ApS",
    'website': "http://rlsd.dk/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '15.0.1.0.13',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'contacts',
        'mail',
        'sale',
        'sale_purchase',
        'sale_stock',
        'account',
        'purchase',
        'stock',
        ],

    # always loaded
    'data': [
                       
        'wizard/stock_picking_select_products.xml',
        'wizard/stock_picking_line_missing_so.xml',
                
        'views/stock_quant.xml',
        'views/stock_picking.xml',
                        
        'security/ir.model.access.csv',
        'security/security.xml',
        
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
}
