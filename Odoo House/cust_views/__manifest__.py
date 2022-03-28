
{
    'name': 'Sales Custom View',
    'description': """Sales Custom View""",
    'version': '14.0.1.0.0',
    'summary': """Sales Custom View""",
    'author': 'Odoo House ApS',
    'website': 'https://odoohouse.dk',
    'category': "Sales",
    'license': 'LGPL-3',
    'depends': ['sale'],
    'data': [
        'views/sale_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
