# -*- coding: utf-8 -*-

{
    'name': 'Dynamic Product Name & Ref. Generator',
    'version': '1.0',
    'summary': 'Create Dynamic Name & Ref. For Products',
    'sequence': 30,
    'description': """
Dynamic Product Name & Ref.
===========================
    """,
    'category': 'Sales',
    'website': '',
    'depends': ['product_pim', 'dynamic_base_attributes'],
    'data': [
        'views/product_category_view.xml',
        'views/product_template_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
