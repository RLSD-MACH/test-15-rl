# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Contact statements",

    'summary': """
       Customer / Vendor statements""",

    'description': """
        Long description of module's purpose
    """,

    'author': "RL Software Development ApS",
    'website': "http://rlsd.dk/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '15.0.1.1.8',

    # any module necessary for this one to work correctly
    'depends': [
        'contacts',  
        'account', 
        'sale',         
        'rlbooks_imp_sale',
        'rlbooks_imp_purchase',
        'rlbooks_imp_stock_picking'
        ],

        
    # 'account_accountant', 

    # always loaded
    'data': [

        'data/email_templates.xml',
        'data/account_move_type_data.xml',
        'data/sale_order_state_data.xml',
        
        'data/page_data.xml',
        'reports/bonus_statement_report.xml',
        'reports/bonus_statement_wizard.xml',           
        'reports/statement_report.xml',
        'reports/statement_wizard.xml',
        'reports/sales_statement_report.xml',
        'reports/sales_statement_wizard.xml',
        'reports/templates.xml',
        'reports/sale_order_document_report.xml',
        'reports/purchase_order_document_report.xml',
        'reports/delivery_slip_document_report.xml',
        'reports/account_move_document_report.xml',
                
        'views/res_config_settings_views.xml',
        'views/res_partner_bank_view.xml',
        'views/view_sale.xml',
        'views/view_account_move.xml',
        'views/view_purchase.xml',
        'views/view_stock_picking.xml',
        'views/view_stock_warehouse.xml',
        
                
        'security/ir.model.access.csv',
        'security/security.xml',
        
    ],
    'css': [

        'static/src/css/statement_report.css'
    
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
}