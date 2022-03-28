
{
    'name': 'Cust Delivery Slip',
    'description': """Cust Delivery Slip""",
    'version': '14.0.1.0.1',
    'summary': """Cust Delivery Slip""",
    'author': 'Odoo House ApS',
    'website': 'https://odoohouse.dk',
    'category': "Sale",
    'license': 'LGPL-3',
    'depends': ['sale', 'stock'],
    'data': [
        'views/assets.xml',
        'report/report_deliveryslip.xml',
        'report/stock_report_views.xml',
    ],
    'installable': True,
    'auto_install': False,

}
