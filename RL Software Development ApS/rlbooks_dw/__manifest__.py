# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "DW",

    'summary': """
       Customised actions - nessecary for DW-case to work""",

    'description': """
        Contact Mads Christensen for more information
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
        'account',
        'sale',
        'stock',
        'contact_group'
        ],

    # always loaded
    'data': [

        'data/page_data.xml',

        'reports/distributors_statement_report.xml',
        'reports/distributors_statement_wizard.xml',        

        'views/account_view_account_position_form_view.xml',
        'views/res_config_settings_views.xml',
        'views/view_res_partner.xml',
        'views/view_stock_picking.xml',
        
        'security/ir.model.access.csv',
        'security/security.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
}