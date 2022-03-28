# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Magento2",

    'summary': """
       Integration to Magento2""",

    'description': """
        Contact Mads Christensen for more information
    """,

    'author': "RL Software Development ApS",
    'website': "http://rlsd.dk/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '15.0.1.0.2',

    # any module necessary for this one to work correctly
    'depends': [
        'rlbooks_api',
        'product',
        ],

    # always loaded
    'data': [      
        'views/magento2_api_call_view.xml',
        'views/magento2_api_standard_view.xml',
        'views/magento2_attribute_view.xml',
        'views/magento2_store_view.xml',
        'views/magento2_login_view.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
}