
{
    'name': 'Move Cust Order Ref MC',
    'description': """Move Cust Order Ref Multi Company""",
    'version': '14.0.1.0.0',
    'summary': """Move Cust Order Ref Multi Company""",
    'author': 'Odoo House ApS',
    'website': 'https://odoohouse.dk',
    'category': "Productivity",
    'depends': ['sale_purchase_inter_company_rules'],
    'data': [
        'views/sale_views.xml',
    ],
    'installable': True,
    'auto_install': False,

}
