# Copyright 2019 Odoo House
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    'name': 'Danish address layout on partner form',
    'summary': 'Danmarkspakken',
    'version': '13.0.1.0.0',
    'author': 'Odoo House ApS',
    'license': "LGPL-3",
    'website': 'https://odoohouse.dk',
    'category': 'Localization',
    'sequence': 100, 
    'description': """
**Danmarkspakken**

This module provides Danish address input field layout.
    """,
    'depends': [
        'base',
    ],
    'data': [
        'views/assets.xml',
        'views/res_partner_views.xml',
        'data/res_country_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
