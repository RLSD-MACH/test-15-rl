# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Inspection report",

    'summary': """
       """,

    'description': """
            
    """,

    'author': "RL Software Development ApS",
    'website': "http://rlsd.dk/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '15.0.1.0.12',

    # any module necessary for this one to work correctly
    'depends': [            
        'purchase',
        'product',
        'portal'
        ],

    # always loaded
    'data': [

        'security/ir.model.access.csv',
        'security/security.xml',

        'views/inspection_report.xml',      
        'views/view_product_template.xml',      
        'views/view_purchase.xml',   
        'views/menuitem.xml',     

        'views/res_config_settings_views.xml',              
        
    ],
    'price': 50.0,
    'currency': 'EUR',
    'support': 'support@rlsd.dk',
    # 'live_test_url': '',
    "images":[
        'static/description/icon.png', 
        'static/description/logo.png',         
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
}

