# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Sourzing",

    'summary': """
       Customised changes specific for Sourzing A/S""",

    'description': """
        Contact Mads Christensen for more information
    """,

    'author': "RL Software Development ApS",
    'website': "http://rlsd.dk/",
    'category': 'Accounting/Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'account',
        'sale',
        'project',
        'mail',
        'base',
        'product_customer_art_no',
        ],

    # always loaded
    'data': [
        'views/assets.xml',     

        'views/account_move_views.xml',
        'views/res_company_views.xml'
                   
        'views/report_templates.xml',
        'views/sale_views.xml',

        'report/account_report.xml',
        'report/invoice_report_templates.xml',
    ],
    
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
}