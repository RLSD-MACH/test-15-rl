# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    vies_asker_country_code = fields.Char(required=False,string='Asker countrycode',help="Max. two letters. Like: DK", size=2)
    vies_asker_vat = fields.Char(required=False,string='Asker VAT-number - without contry-code',help="The number without the countrycode")
    vies_days_between_validations = fields.Integer(required=True, default=30, help="Validations will only be excecuted, if the last validation date is more than X days old.")
    vies_run_auto_contacts = fields.Boolean(required=False,string='Run automatic on changed VAT-number in contacts',help="If you change a contacts VAT-number it will try to validate it.", default=False)
    vies_run_auto_sales_invoice = fields.Boolean(required=False,string='Run automatic on partner change on sales invoice',help="If you change a the partner on a sales invoice, then it vil try to validate the VAT-number.", default=False)
    vies_run_auto_sale_order = fields.Boolean(required=False,string='Run automatic on partner change on sale order',help="If you change a the partner on a sale order, then it vil try to validate the VAT-number.", default=False)

class ResConfigSettings(models.TransientModel):

    _inherit = ['res.config.settings']
    
    vies_asker_country_code = fields.Char(required=False,related='company_id.vies_asker_country_code', readonly=False, size=2)
    vies_asker_vat = fields.Char(required=False,related='company_id.vies_asker_vat', readonly=False)
    vies_days_between_validations = fields.Integer(required=True,related='company_id.vies_days_between_validations', readonly=False)
    vies_run_auto_contacts = fields.Boolean(required=False,related='company_id.vies_run_auto_contacts', readonly=False)
    vies_run_auto_sales_invoice = fields.Boolean(required=False,related='company_id.vies_run_auto_sales_invoice', readonly=False)
    vies_run_auto_sale_order = fields.Boolean(required=False,related='company_id.vies_run_auto_sale_order', readonly=False)