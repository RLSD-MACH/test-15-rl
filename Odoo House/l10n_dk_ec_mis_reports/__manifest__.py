# © 2015-2017 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>

{
    'name': 'MIS reports for Denmark (E-conomics)',
    'version': '12.0.1.0.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'MIS Report templates for the Danish P&L and Balance Sheets following the style from E-conomics',
    'author': 'Odoo House',
    'website': 'https://www.odoohouse.dk',
    'depends': ['mis_builder', 'l10n_dk_ec'],
    'data': [
        'data/mis_report_styles.xml',
        'data/mis_report_pl_bs.xml',
        'data/mis_report_vat.xml',
        ],
    'installable': True,
}
