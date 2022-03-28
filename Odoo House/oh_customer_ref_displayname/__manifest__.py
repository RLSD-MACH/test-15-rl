
{
    'name': 'Name and Reference Display on Partner Form',
    'description': """Name and Reference Display on Partner Form""",
    'version': '14.0.1.0.0',
    'summary': """Name and Reference Display on Partner Form""",
    'author': 'Odoo House ApS',
    'website': 'https://odoohouse.dk',
    'category': "Sales",
    'license': 'LGPL-3',
    'depends': ['sale', 'purchase'],
    'data': [
        'views/sale_views.xml',
        'views/purchase_views.xml',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
