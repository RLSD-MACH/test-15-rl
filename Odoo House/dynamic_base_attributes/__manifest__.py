# -*- coding: utf-8 -*-
{
    'name': 'Dynamic Base Attributes',
    'version': '14.0.1.0.0',
    'summary': 'Create Dynamic Attributes',
    'sequence': 30,
    'description': """
        Dynamic Base Attributes
        ==========================
        Create Dynamic attributes.
    """,
    'category': 'base',
    'author': 'Odoo House ApS',
    'website': 'https://odoohouse.dk',
    'depends': ['product'],
    'data': [
        'security/ir.model.access.csv',
        'views/dyn_attribute_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
