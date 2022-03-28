# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "VIES",

    'summary': """
       Verify EU VAT-numbers and save the history of authenications as documentation for tax-free B2B sales within EU.""",

    'description': """
    
        This module (VIES) makes it easy to control your contacts VAT-number in a timely fashion as required by law, if your trade goods or service B2B in Europe. 

        VIES gives you the ability to control the VAT-number directly from Odoo without having to go to https://ec.europa.eu/taxation_customs/vies/vatResponse.html and manually check it. 
        
        VIES saves the response to your database and clearly shows the user whether the VAT-number was correct. Further more you can tell the module to control the VAT-number whenever it is used on a new sales order or a new sales invoice. By law you don’t need to check the VAT-number every time, so we have made it possible to tell the system only to re-check the VAT-number after a given number of days. 
        
        The check is of cause made against the API on https://ec.europa.eu/taxation_customs/vies/, so the module will send your VAT-number and your contacts VAT-number to this API in order to return with an answer.

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
        'contacts',     
        'account',
        'sale_management',
        'base_vat'
        ],

    # always loaded
    'data': [
        'views/vies_message.xml',
        'views/res_partner.xml',
        'views/view_account_move.xml',
        'views/view_sale_order.xml',
        'views/res_config_settings_views.xml',
        'views/vies_menuitem.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/scheduled_actions.xml',
    ],
    'price': 50.0,
    'currency': 'EUR',
    'support': 'support@rlsd.dk',
    # 'live_test_url': '',
    "images":[
        'static/description/icon.png',
        'static/description/banner.png',
        'static/description/api_response_from_vies.png',
        'static/description/history_vies_messages.png',
        'static/description/invalid_contact.png',
        'static/description/invalid_customer_invoice.png',
        'static/description/invalid_sales_order.png',
        'static/description/logo.png',
        'static/description/request_to_vies.png',
        'static/description/response_from_view.png',
        'static/description/settings.png',
        
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
}

