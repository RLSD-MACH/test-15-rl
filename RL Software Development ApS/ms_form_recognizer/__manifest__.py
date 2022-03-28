# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "MS Form Recognizer",

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
    'version': '15.0.1.0.13',

    # any module necessary for this one to work correctly
    'depends': [
        'base_setup',
        'sale',
        'account',
        ],

    # always loaded
    'data': [
        'security/groups.xml',  
        'views/view_sale_order.xml',
        'views/view_ir_attachment.xml',
        'views/res_config_settings_views.xml',
        'views/form_recognizer.xml',
        'views/danloen.xml',
        'views/account_move.xml',
        'views/menuitem.xml',
        
        'security/ir.model.access.csv',
        'security/security.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [
           
        ],
        'web.assets_backend': [
            
            'ms_form_recognizer/static/src/js/file_upload.js',

        ],
        'web.assets_frontend': [
        ],
        'web.assets_tests': [
        ],
        'web.qunit_suite_tests': [
        ],
        'web.assets_qweb': [
            'ms_form_recognizer/static/src/xml/**/*',
        ],
    },
    'price': 100.0,
    'currency': 'EUR',
    'support': 'support@rlsd.dk',
    # 'live_test_url': '',
    "images":[
        'static/description/icon.png',
        'static/description/logo.png',        
    ],
    'external_dependencies': {

        'python' : ['pdfplumber', 'pyperclip'],

    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
}

