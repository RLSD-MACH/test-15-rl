# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "MTO",

    'summary': """
       MTO""",

    'description': """
        
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
        'contacts',
        # 'mail',
        'sale',
        'account',
        'purchase',
        # 'rlbooks_imp_sale',
        # 'rlbooks_imp_purchase',
        # 'portal'
        ],

    # always loaded
    'data': [

        # 'data/ir_sequence_data.xml',
                
        'views/sale_order.xml',

        # 'wizard/shipping_order_wizard_view.xml',
        # 'security/ir.model.access.csv',
        # 'security/security.xml',
        
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
}
