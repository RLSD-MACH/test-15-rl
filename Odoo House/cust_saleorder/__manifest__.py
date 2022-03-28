
{
    'name': 'Cust Saleorder',
    'description': """Cust Saleorder""",
    'version': '15.0.1.0.2',
    'summary': """Cust Saleorder""",
    'author': 'Odoo House ApS',
    'website': 'https://odoohouse.dk',
    'category': "Sales",
    'license': 'LGPL-3',
    'depends': ['sale'],
    'data': [
        # 'views/assets.xml',
        #'report/sale_report_templates.xml',
        'report/sale_report.xml',
    ],
    'assets': {
        
        'web.report_assets_pdf': [
            
            "cust_saleorder/static/src/scss/cust_saleorder_reports.scss",
            
        ],
        
    },
    'installable': True,
    'auto_install': False,

}
