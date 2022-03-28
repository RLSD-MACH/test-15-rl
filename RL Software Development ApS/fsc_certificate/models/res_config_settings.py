# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    fsc_days_between_validations = fields.Integer(required=True, default=30, string='Days Between Automatic Validations of FSC Certificate', help="Validations will only be excecuted, if the last validation date is more than X days old.")
    fsc_run_auto_create_edit = fields.Boolean(required=True,string='FSC check - Run automatic',help="If you create a new certificate or change the number, it will try to validate it.", default=True)
    fsc_run_auto_account_move = fields.Boolean(required=False,string='FSC check - Run automatic on certificate change on account move',help="If you change a the certificate on an account move, then it vil try to validate the certificate.", default=True)
    fsc_run_auto_sale_order = fields.Boolean(required=False,string='FSC check - Run automatic on certificate change on sale order',help="If you change a the certificate on a sale order, then it vil try to validate the certificate.", default=True)
    fsc_run_auto_purchase_order = fields.Boolean(required=False,string='FSC check - Run automatic on certificate change on purchase order',help="If you change a the certificate on a purchase order, then it vil try to validate the certificate.", default=True)

class ResConfigSettings(models.TransientModel):

    _inherit = ['res.config.settings']
    
    fsc_days_between_validations = fields.Integer(required=False,related='company_id.fsc_days_between_validations', readonly=False)
    fsc_run_auto_create_edit = fields.Boolean(required=False,related='company_id.fsc_run_auto_create_edit', readonly=False)
    fsc_run_auto_account_move = fields.Boolean(required=False,related='company_id.fsc_run_auto_account_move', readonly=False)
    fsc_run_auto_sale_order = fields.Boolean(required=False,related='company_id.fsc_run_auto_sale_order', readonly=False)
    fsc_run_auto_purchase_order = fields.Boolean(required=False,related='company_id.fsc_run_auto_purchase_order', readonly=False)