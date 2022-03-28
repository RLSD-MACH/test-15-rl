# -*- coding: utf-8 -*-
{
    'name': 'Dynamic Product Attributes',
    'version': '14.0.1.0.0',
    'summary': 'Create Dynamic Attributes For Products',
    'sequence': 30,
    'description': """
        Dynamic Product Attributes
        ==========================
        Create attributes for products based on predefined
        product attribute set. Attribute set can be
        independently for each product.
    """,
    'category': 'Sales',
    'author': 'Odoo House ApS',
    'website': 'https://odoohouse.dk',
    'depends': ['dynamic_base_attributes', 'sale_management'],
    'data': [
        'views/product_category_view.xml',
        'views/product_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
