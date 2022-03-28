# -*- encoding: utf-8 -*-
# Copyright 2019 Odoo House
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Denmark - Accounting Reports EC',
    'summary': 'Danmarkspakken',
    'version': '13.0.1.0.0',
    'author': 'Odoo House ApS',
    'website': 'https://odoohouse.dk',
    'category': 'Localization',
    'description': """
Accounting reports for Denmark
=================================
    """,
    'category': 'Accounting',
    'depends': ['l10n_dk_ec', 'account_reports','account_accountant'],
    'data': [
        'data/res_config_data.xml',
        'data/account_income_statement_report_data.xml',
        'data/account_balance_report_data.xml',
        'data/account_vat_report_data.xml',
    ],
    'demo': [],
    'auto_install': False,
    'installable': True,
    'license': 'OEEL-1',
}