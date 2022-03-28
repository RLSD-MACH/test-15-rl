# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Prontoforms",

    'summary': """
       Integration to Prontoforms""",

    'description': """
        Contact Mads Christensen for more information
    """,

    'author': "RL Software Development ApS",
    'website': "http://rlsd.dk/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '15.0.1.0.15',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'base_setup',
        'inspection_report',
        'product_customer_art_no',
        'product'
        ],

    # always loaded
    'data': [      
        'views/prontoforms_user.xml',
        'views/prontoforms_formspace.xml',
        'views/prontoforms_form.xml',
        'views/prontoforms_form_submission.xml',
        'views/inspection_report.xml',  
        'views/res_config_settings_views.xml',
        'views/prontoforms_menuitem.xml',        
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/scheduled_actions.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
}