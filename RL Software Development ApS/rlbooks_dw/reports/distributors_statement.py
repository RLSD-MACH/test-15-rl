from typing import DefaultDict
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
import base64

class DistributorsStatementReportPrint(models.Model):


    _name = 'rlbooks_dw.distributors_statement.print'
    _description = 'Distributors Statement'
    _check_company_auto = True
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'id'    
    _order = 'id desc'

    def _compute_stat_dw_distributors_invoice_service(self):

        for rec in self:

            rec.stat_dw_distributors_invoice_service = rec.stat_dw_distributors_invoice_total - rec.stat_dw_distributors_invoice_goods

    def _compute_stat_dw_distributors_invoice_service_periode(self):

        for rec in self:

            rec.stat_dw_distributors_invoice_service_periode = rec.stat_dw_distributors_invoice_total_periode - rec.stat_dw_distributors_invoice_goods_periode

    def _compute_stat_dw_distributors_invoice_service(self):

        for rec in self:

            rec.stat_dw_distributors_invoice_service = rec.stat_dw_distributors_invoice_total - rec.stat_dw_distributors_invoice_goods

    def _compute_stat_dw_net_income_periode(self):

        for rec in self:

            rec.stat_dw_net_income_periode = rec.stat_dw_distributors_invoice_goods_periode - rec.stat_dw_distributors_write_off_periode

    def _compute_stat_dw_net_income(self):

        for rec in self:

            rec.stat_dw_net_income = rec.stat_dw_distributors_invoice_goods - rec.stat_dw_distributors_write_off

    def _compute_stat_dw_bank_periode(self):

        for rec in self:

            rec.stat_dw_bank_periode = rec.stat_dw_net_income_periode - rec.stat_used_dw_bank_periode - rec.stat_dw_distributors_recievables_periode

    def _compute_stat_dw_bank(self):

        for rec in self:

            rec.stat_dw_bank = rec.stat_dw_net_income - rec.stat_used_dw_bank - rec.stat_dw_distributors_recievables
    
    
    name = fields.Char(required=True,string='Name', readonly=True)
    date_start = fields.Date(string='Periode start', required=False, readonly=True)
    date_end = fields.Date(string='Periode end', required=False, readonly=True)    
    languages_id = fields.Many2one("res.lang", string='Language', required=True, domain="[('active','=',True)]")
    currency_id = fields.Many2one("res.currency", string='Currency', required=True, domain="[('active','=',True)]")
    company_id = fields.Many2one('res.company', 'Company', required=True, readonly=True, index=True, default=lambda self: self.env.company)   
    type = fields.Selection(selection = [('long', 'Print full version'), ('short', 'Print first page'), ('long_debug', 'Print full version with debug')], readonly=True, required=True, string='Type',default="long")
    user_id = fields.Many2one(
        'res.users', 
        string='Contactperson',
        readonly=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    partner_id = fields.Many2one(
        'res.partner', 
        string='Customer',           
        readonly=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    send = fields.Boolean(required=True, readonly=True, string='Send', default=False)
    attachment = fields.Many2one("ir.attachment", string='Attachment', readonly=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    
    stat_dw_distributors_invoice_total_periode = fields.Float(string='Invoices DW Distributor Total in Periode', default="0")
    stat_dw_distributors_invoice_service_periode = fields.Float(string='Invoices DW Distributor Service in Periode', default="0", compute="_compute_stat_dw_distributors_invoice_service_periode")
    stat_dw_distributors_invoice_goods_periode = fields.Float(string='Invoices DW Distributor Goods in Periode', default="0")
    stat_dw_distributors_write_off_periode = fields.Float(string='Witeoff DW Distributor in Periode', default="0")
    stat_dw_net_income_periode = fields.Float(string='DW\'s net income in Periode', default="0", compute="_compute_stat_dw_net_income_periode")
    stat_used_dw_bank_periode = fields.Float(string='Used DW Bank in Periode', default="0")
    stat_dw_distributors_recievables_periode  = fields.Float(string='Recievables DW Distributors in Periode', default="0")
    stat_dw_bank_periode = fields.Float(string='DW Bank in Periode', default="0", compute="_compute_stat_dw_bank_periode")
    acc22200_periode = fields.Float(string='Account 22200 in Periode', default="0")
    acc22400_periode = fields.Float(string='Account 22400 in Periode', default="0")

    stat_dw_distributors_invoice_total = fields.Float(string='Invoices DW Distributor Total', default="0")
    stat_dw_distributors_invoice_service = fields.Float(string='Invoices DW Distributor Service', default="0", compute="_compute_stat_dw_distributors_invoice_service")
    stat_dw_distributors_invoice_goods = fields.Float(string='Invoices DW Distributor Goods', default="0")
    stat_dw_distributors_write_off = fields.Float(string='Witeoff DW Distributor', default="0")
    stat_dw_net_income = fields.Float(string='DW\'s net income', default="0", compute="_compute_stat_dw_net_income")
    stat_used_dw_bank = fields.Float(string='Used DW Bank', default="0")
    stat_dw_distributors_recievables = fields.Float(string='Recievables DW Distributors', default="0")
    stat_dw_bank = fields.Float(string='DW Bank', default="0", compute="_compute_stat_dw_bank")
    acc22200 = fields.Float(string='Account 22200', default="0")
    acc22400 = fields.Float(string='Account 22400', default="0")

    partners = fields.Many2many('res.partner', string='Partners')

    # stat_dw_distributors_invoice_total = fields.Float(string='Invoices DW Distributor Total')
    # stat_dw_distributors_invoice_total = fields.Float(string='Invoices DW Distributor Total')
    # stat_dw_distributors_invoice_total = fields.Float(string='Invoices DW Distributor Total')
    # stat_dw_distributors_invoice_total = fields.Float(string='Invoices DW Distributor Total')
    # stat_dw_distributors_invoice_total = fields.Float(string='Invoices DW Distributor Total')
    

    def action_generate_pdf_file(self, cr, uid, ids, context=None):
        
        if self.attachment.id == False:

            data, data_format = self.env.ref('rlbooks_dw.distributors_statement_print').sudo()._render_qweb_pdf([self.id])

            result = base64.b64encode(data)
            file_name = self.name
            file_name += ".pdf"
            
            vals ={
                    'name': file_name,
                    'datas': result,
                    'name': file_name,
                    # 'datas_fname': file_name,
                    'res_model': self._name,
                    'res_id': self.id,
                    # 'type': 'binary',
                    'mimetype': 'application/pdf'

                }

            attachment_id = self.env['ir.attachment'].create(vals)

            self.attachment = attachment_id

            return attachment_id
        
        else:

            raise UserError("Pis " + str(self.attachment))


class DistributorsStatementReportWizard(models.TransientModel):

    _name = 'rlbooks_dw.distributors_statement.wizard'
    _description = 'Distributors Statement'
    _check_company_auto = True

    def _get_default_lang(self):

        default_lang_id = self.env.context.get('default_lang_id')

        if default_lang_id:

            return default_lang_id 
        
        elif self.env.company.dw_statement_languages_id:

            return self.env.company.dw_statement_languages_id.id

        else:                       

            return self.env['res.lang'].search([['code','=',self.env.user.lang]], limit=1).id

    def _get_default_currency(self):

        default_currency_id = self.env.context.get('default_currency_id')

        if default_currency_id:

            return default_currency_id 
        
        elif self.env.company.dw_statement_currency_id:

            return self.env.company.dw_statement_currency_id.id

        else:                       

            return self.env.company.currency_id.id

    def _get_default_partner(self):

        default_partner_id = self.env.context.get('default_partner_id')

        if default_partner_id:

            return default_partner_id 
        
        elif self.env.company.dw_statement_partner_id:

            return self.env.company.dw_statement_partner_id.id

        else:                       

            return None
    
    def _get_default_user(self):

        default_user_id = self.env.context.get('default_user_id')

        if default_user_id:

            return default_user_id 
        
        elif self.env.company.dw_statement_partner_id.user_id:

            return self.env.company.dw_statement_partner_id.user_id.id

        else:                       

            return self.env.user

    date_start = fields.Date(string='Periode start', required=True, default="1900-01-01")
    date_end = fields.Date(string='Periode end', required=True,default=datetime.today())    
    languages_id = fields.Many2one("res.lang", string='Language', required=True, default=_get_default_lang, domain="[('active','=',True)]")
    currency_id = fields.Many2one("res.currency", string='Currency', required=True, default=_get_default_currency, domain="[('active','=',True)]")
    type = fields.Selection(selection = [('long', 'Print full version'), ('short', 'Print first page'), ('long_debug', 'Print full version with debug')], required=True, string='Type',default="long")
    user_id = fields.Many2one(
        'res.users', 
        string='Contactperson',
        required=True,
        default=_get_default_user,
       domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    partner_id = fields.Many2one(
        'res.partner', 
        string='Customer',           
        required=True,
        default=_get_default_partner,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
        
    def action_print_save_pdf (self):

        if self.date_end and self.date_start:

            if self.date_end < self.date_start:

                raise ValidationError("End date needs to be bigger than start date!")
       
        attachments = []

        val = {

            'date_start': self.date_start,
            'date_end': self.date_end,               
            'languages_id': self.languages_id.id,     
            'currency_id': self.currency_id.id, 
            'user_id': self.user_id.id,    
            'partner_id': self.partner_id.id,   
            'type': self.type, 
            'company_id': self.company_id.id,    
            'send': False,
            'attachment': False,
            'name': _('Distributors statement from %s to %s' % (self.date_start.strftime('%d-%m-%Y'), self.date_end.strftime('%d-%m-%Y'))) 

        }
       
        report = self.env['rlbooks_dw.distributors_statement.print'].create(val)

        attachment_id = report.action_generate_pdf_file(report,self._cr, self._uid, context=self._context)
        attachments += attachment_id

        if len(attachments) == 1:

            try:
                form_view_id = self.env.ref("rlbooks_dw.my_form_view_external_id").id
            except Exception as e:
                form_view_id = False

            return {

                'type': 'ir.actions.act_window',
                'name': 'Distributors Statement',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': report.id,
                'res_model': 'rlbooks_dw.distributors_statement.print',
                'views': [(form_view_id, 'form')],
                'target': 'current',
            }

        return  attachments

class DistributorsStatementReport(models.AbstractModel):

    _name = 'report.rlbooks_dw.distributors_statement'
    _description = 'Distributors Statement'

    @api.model
    def _get_report_values(self, docids, data=None):
        
        docs = []
        
        for doc in docids:

            
            doc = self.env['rlbooks_dw.distributors_statement.print'].browse(doc)
            company = doc.company_id

            doc.stat_dw_distributors_invoice_total = sum(l.balance for l in self.env['account.move.line'].search([['account_id','in',company.dw_statement_recievable_account_ids.ids],['parent_state','=','posted'],['date','<=',doc.date_end],['partner_id.property_account_position_id','in',company.dw_statement_recievable_afp_ids.ids], ['move_id.move_type','in',['out_invoice','out_refund']]]))
            doc.stat_dw_distributors_invoice_total_periode = sum(l.balance for l in self.env['account.move.line'].search([['account_id','in',company.dw_statement_recievable_account_ids.ids],['parent_state','=','posted'],['date','>=',doc.date_start],['date','<=',doc.date_end],['partner_id.property_account_position_id','in',company.dw_statement_recievable_afp_ids.ids], ['move_id.move_type','in',['out_invoice','out_refund']]]))

            doc.stat_dw_distributors_invoice_goods = -sum(l.balance for l in self.env['account.move.line'].search([['account_id','=',company.dw_statement_dwbank_account_id.id],['parent_state','=','posted'],['date','<=',doc.date_end],['partner_id.property_account_position_id','in',company.dw_statement_recievable_afp_ids.ids], ['move_id.move_type','in',['out_invoice','out_refund']]]))
            doc.stat_dw_distributors_invoice_goods_periode = -sum(l.balance for l in self.env['account.move.line'].search([['account_id','=',company.dw_statement_dwbank_account_id.id],['parent_state','=','posted'],['date','>=',doc.date_start],['date','<=',doc.date_end],['partner_id.property_account_position_id','in',company.dw_statement_recievable_afp_ids.ids], ['move_id.move_type','in',['out_invoice','out_refund']]]))

            doc.stat_dw_distributors_write_off_periode = sum(l.balance for l in self.env['account.move.line'].search([['account_id','=',company.dw_statement_dwloss_account_id.id],['parent_state','=','posted'],['date','>=',doc.date_start],['date','<=',doc.date_end]]))
            doc.stat_dw_distributors_write_off = sum(l.balance for l in self.env['account.move.line'].search([['account_id','=',company.dw_statement_dwloss_account_id.id],['parent_state','=','posted'],['date','<=',doc.date_end]]))

            doc.stat_used_dw_bank_periode = doc.stat_dw_distributors_invoice_goods_periode + sum(l.balance for l in self.env['account.move.line'].search([['account_id','=',company.dw_statement_dwbank_account_id.id],['parent_state','=','posted'],['date','>=',doc.date_start],['date','<=',doc.date_end]]))
            doc.stat_used_dw_bank = doc.stat_dw_distributors_invoice_goods + sum(l.balance for l in self.env['account.move.line'].search([['account_id','=',company.dw_statement_dwbank_account_id.id],['parent_state','=','posted'],['date','<=',doc.date_end]]))

            doc.stat_dw_distributors_recievables_periode = sum(l.balance for l in self.env['account.move.line'].search([['account_id','in',company.dw_statement_recievable_account_ids.ids],['parent_state','=','posted'],['date','>=',doc.date_start],['date','<=',doc.date_end],['partner_id.property_account_position_id','in',company.dw_statement_recievable_afp_ids.ids]]))
            doc.stat_dw_distributors_recievables = sum(l.balance for l in self.env['account.move.line'].search([['account_id','in',company.dw_statement_recievable_account_ids.ids],['parent_state','=','posted'],['date','<=',doc.date_end],['partner_id.property_account_position_id','in',company.dw_statement_recievable_afp_ids.ids]]))

            doc.acc22200_periode = sum(l.balance for l in self.env['account.move.line'].search([['account_id','=',company.dw_statement_dwbank_account_id.id],['parent_state','=','posted'],['date','>=',doc.date_start],['date','<=',doc.date_end]]))
            doc.acc22200 = sum(l.balance for l in self.env['account.move.line'].search([['account_id','=',company.dw_statement_dwbank_account_id.id],['parent_state','=','posted'],['date','<=',doc.date_end]]))

            doc.acc22400_periode = sum(l.balance for l in self.env['account.move.line'].search([['account_id','=',company.dw_statement_dwloss_account_id.id],['parent_state','=','posted'],['date','>=',doc.date_start],['date','<=',doc.date_end]]))
            doc.acc22400 = sum(l.balance for l in self.env['account.move.line'].search([['account_id','=',company.dw_statement_dwloss_account_id.id],['parent_state','=','posted'],['date','<=',doc.date_end]]))
            
            if doc.type in ['long','long_debug']:

                p_list = []

                for group in self.env['account.move.line'].read_group([['account_id','in',company.dw_statement_recievable_account_ids.ids],['parent_state','=','posted'],['date','>=',doc.date_start],['date','<=',doc.date_end],['partner_id.property_account_position_id','in',company.dw_statement_recievable_afp_ids.ids]], ['partner_id'], groupby=['partner_id'], lazy=False):
                    
                    # p = self.env['res.partner'].browse(group['partner_id'][0])
                    p_list.append(group['partner_id'][0])

                doc.partners = self.env['res.partner'].search([['id','in',p_list]], order='name asc')

            docs.append(doc)

        return {

            'doc_ids':docids,
            'doc_model': 'rlbooks_dw.distributors_statement.print',           
            'docs': docs,
        }