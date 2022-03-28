# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "MTO IC",

    'summary': """
       MTO with intercompany workflow.""",

    'description': """
        Is used for specific products to specific orders, which can be produce in another company to forfill a requst in another intercompany.
        You can also bill services and put services on stock. More features will be created in the future!
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
        'mail',
        'sale',
        'account',
        'purchase',
        'stock',
        'rlbooks_imp_sale',
        'rlbooks_imp_purchase',
        'portal'
        ],

    # always loaded
    'data': [
        'data/ir_sequence_data.xml',
        
        'wizard/container_select_products.xml',
        'wizard/shipping_order_select_products.xml',
        'wizard/shipping_order_wizard_view.xml',
        'wizard/stock_picking_select_products.xml',
        
        'views/mto_ic_order_view.xml',
        'views/shipping_order_view.xml',
        'views/container_view.xml',
        'views/container_size_view.xml',
        'views/res_port.xml',
        'views/res_vessel.xml',
        'views/stock_quant.xml',
        'views/stock_picking.xml',
        
        
        'views/shipping_order_portal.xml',

        'views/purchase_order.xml',
        'views/sale_order.xml',

        
        'security/ir.model.access.csv',
        'security/security.xml',
        
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
}
