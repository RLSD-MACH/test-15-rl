# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    cvr_password = fields.Char(required=False,string='CVR Password',help="")
    cvr_user_id = fields.Char(required=False,string='CVR User ID',help="")
    cvr_days_between_validations = fields.Integer(required=True, default=30, help="Validations will only be excecuted, if the last validation date is more than X days old.")
    cvr_run_auto_contacts = fields.Boolean(required=False,string='Run automatic on changed VAT-number in contacts',help="If you change a contacts VAT-number it will try to validate it.", default=False)
    cvr_run_auto_sales_invoice = fields.Boolean(required=False,string='Run automatic on partner change on sales invoice',help="If you change a the partner on a sales invoice, then it vil try to validate the VAT-number.", default=False)
    cvr_run_auto_sale_order = fields.Boolean(required=False,string='Run automatic on partner change on sale order',help="If you change a the partner on a sale order, then it vil try to validate the VAT-number.", default=False)

class ResConfigSettings(models.TransientModel):

    _inherit = ['res.config.settings']
    
    cvr_password = fields.Char(required=False,related='company_id.cvr_password', readonly=False)
    cvr_user_id = fields.Char(required=False,related='company_id.cvr_user_id', readonly=False)
    cvr_days_between_validations = fields.Integer(required=True,related='company_id.cvr_days_between_validations', readonly=False)
    cvr_run_auto_contacts = fields.Boolean(required=False,related='company_id.cvr_run_auto_contacts', readonly=False)
    cvr_run_auto_sales_invoice = fields.Boolean(required=False,related='company_id.cvr_run_auto_sales_invoice', readonly=False)
    cvr_run_auto_sale_order = fields.Boolean(required=False,related='company_id.cvr_run_auto_sale_order', readonly=False)