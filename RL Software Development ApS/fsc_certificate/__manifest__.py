# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "FSC certificate",

    'summary': """
       """,

    'description': """
        Contact Mads Christensen for more information
    """,

    'author': "RL Software Development ApS",
    'website': "http://www.rlsd.dk/",

    'category': 'Accounting/Accounting',
    'version': '15.0.1.0.21',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'sale',
        'purchase',
        'rlbooks_statement'
        ],

    # always loaded
    'data': [

        'data/fsc_claim_data.xml',

        'views/res_company_views.xml',
        'views/fsc_claim.xml',
        'views/fsc_certificate.xml',
        'views/fsc_certificate_validation.xml',
        'views/view_product_template.xml',
        'views/view_sale_order.xml',
        'views/view_purchase_order.xml',
        'views/view_account_move.xml',
        'views/res_partner.xml',
        'views/fsc_certificate_validation.xml',
        'views/res_config_settings_views.xml',
        
        'reports/saleorder_document_report.xml',
        'reports/delivery_slip_document_report.xml',
        'reports/purchase_order_document_report.xml',
        'reports/account_move_document_report.xml',
                        
        'security/ir.model.access.csv',   
        'security/security.xml',   
    ],
    'price': 99.99,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
}