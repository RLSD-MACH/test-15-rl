
{
    'name': 'Cust Purchaseorder',
    'description': """Cust Purchaseorder""",
    'version': '14.0.1.0.0',
    'summary': """Cust Purchaseorder""",
    'author': 'Odoo House ApS',
    'website': 'https://odoohouse.dk',
    'category': "Purchase",
    'license': 'LGPL-3',
    'depends': ['purchase'],
    'data': [
        'views/assets.xml',
        'report/purchase_order_templates.xml',
        'report/purchase_reports.xml',
    ],
    'installable': True,
    'auto_install': False,

}
