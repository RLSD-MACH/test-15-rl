from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
import base64

class SaleOrderState(models.Model):

    _name = 'sale_order_state'
    _description = 'Sale order state'

    name = fields.Char(required=True,string='Name', readonly=True)
    state = fields.Char(required=True,string='State', readonly=True)

class SalesStatementReportWizard(models.TransientModel):

    _name = 'rlbooks_statement.sales_report.wizard'
    _description = 'Sales report'
    _check_company_auto = True

    def _get_default_exclude_partner_ids(self):

        default_partner_ids = self.env.context.get('default_exclude_partner_ids')

        if default_partner_ids:

            return [default_partner_ids] 
        
        else:
            
            c_ids = []

            for company in self.env['res.company'].search([['id','>',0]]):

                c_ids.append(company.partner_id.id)

            return c_ids

    def _get_default_lang(self):

        default_lang_id = self.env.context.get('default_lang_id')

        if default_lang_id:

            return default_lang_id 
        
        else:                       

            return self.env['res.lang'].search([['code','=',self.env.user.lang]], limit=1).id


    def _get_default_include_partner_ids(self):
        
        default_partner_ids = self.env.context.get('default_include_partner_ids')
        return [default_partner_ids] if default_partner_ids else None

    def _get_default_sale_order_state_ids(self):

        default_sale_order_state_ids = self.env.context.get('default_sale_order_state_ids')

        if default_sale_order_state_ids:

            return default_sale_order_state_ids
        
        else:

            default_sale_order_state_ids = self.env['sale_order_state'].search([['state','in',['sale','done']]])
            return default_sale_order_state_ids if default_sale_order_state_ids else None

        
    date_start = fields.Date(string='Periode start', required=True, default=datetime.today().strftime('%Y-01-01'))
    date_end = fields.Date(string='Periode end', required=True, default=datetime.today().strftime('%Y-12-31'))    
    exclude_partner_ids = fields.Many2many("res.partner", 'rlbooks_statement_sales_report_parner_in_rel','s_partner_id', 'res_partner_id', string='Exclude Partners', required=True, default=_get_default_exclude_partner_ids)
    include_only_partner_ids = fields.Many2many("res.partner", 'rlbooks_statement_sales_report_parner_ex_rel','s_partner_id', 'res_partner_id', string='Include only Partners', required=False, default=_get_default_include_partner_ids)
    type = fields.Selection(selection = [('normal', 'Print normal'), ('detailed', 'Print detailed')], required=True, string='Type',default="normal")
    open_order_state_ids = fields.Many2many("sale_order_state", string='Open orders - included states', required=False, default=_get_default_sale_order_state_ids)
    languages_id = fields.Many2one("res.lang", string='Language', required=True, default=_get_default_lang, domain="[('active','=',True)]")
    currency_id = fields.Many2one("res.currency", string='Currency', required=True, default=lambda self: self.env.company.currency_id.id, domain="[('active','=',True)]")
    company_id = fields.Many2one('res.company', 'Company', required=True,readonly=True, default=lambda self: self.env.company)
    
    def action_print_pdf (self):
        
        if self.date_end < self.date_start:

            raise ValidationError("End date needs to be bigger than start date!")
            
        return self.env.ref('rlbooks_statement.sales_report_print').report_action(self.id)
        