# -*- coding: utf-8 -*-
{
    'name': "Purchase Delivery Order Split",

    'summary': """
        This module allows you to split the purchase delivery order according to the product's availability """,

    'description': """
        This module allows you to split the purchase delivery order according to the product's availability in the vendor's warehouse""",

    'author': "ErpMstar Solutions / Odoo House ApS",

    'category': 'Purchase',
    'version': '14.0.1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase_stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/wizard.xml',
    ],
    'images': [
        'static/description/confirmed_purchase.jpg',
    ],
    'installable': True,
    'website': '',
    'auto_install': False,
    'price': 20,
    'currency': 'EUR',
}
