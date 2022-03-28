from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
import base64

class StatementReportWizard(models.Model):

    _name = 'rlbooks_statement.report.print'
    _description = 'Statement report'
    _check_company_auto = True
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'id'    
    _order = 'id desc'

    name = fields.Char(required=True,string='Name',readonly=True)
    date_start = fields.Date(string='Periode start', required=True,readonly=True)
    date_end = fields.Date(string='Periode end', required=True,readonly=True)
    type = fields.Selection(selection = [('customer', 'Print customer statement'), ('supplier', 'Print supplier statement')], required=True,string='Type',default="customer",readonly=True)
    partner_id = fields.Many2one("res.partner", string='Partners', required=True,readonly=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    account_ids = fields.Many2many("account.account", string='Accounts',readonly=True, required=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    company_id = fields.Many2one('res.company', 'Company', required=True,readonly=True, index=True, default=lambda self: self.env.company)    
   
    send = fields.Boolean(required=True, string='Send',readonly=True, default=False)
    attachment = fields.Many2one("ir.attachment", string='Attachment',readonly=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    def action_generate_pdf_file(self, cr, uid, ids, context=None):
        
        if self.attachment.id == False:

            data, data_format = self.env.ref('rlbooks_statement.report_print').sudo()._render_qweb_pdf([self.id])

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

            raise UserError("Pis" + str(self.attachment))
        

class StatementReportWizard(models.TransientModel):

    _name = 'rlbooks_statement.report.wizard'
    _description = 'Statement report'
    _check_company_auto = True

    def _get_default_partner_ids(self):
        default_partner_ids = self.env.context.get('default_partner_ids')
        return [default_partner_ids] if default_partner_ids else None
    
    date_start = fields.Date(string='Periode start', required=True)
    date_end = fields.Date(string='Periode end', required=True)
    type = fields.Selection(selection = [('customer', 'Print customer statement'), ('supplier', 'Print supplier statement')], required=True,string='Type',default="customer")
    partner_ids = fields.Many2many("res.partner", string='Partners', default=_get_default_partner_ids, required=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    account_ids = fields.Many2many("account.account", string='Accounts', required=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    
    def action_print_save_pdf (self):

        if self.date_end < self.date_start:

            raise ValidationError("End date needs to be bigger than start date!")

        if self.type == "customer":

            account_ids = self.company_id.customer_statement_account_ids.ids
        
        elif self.type == "supplier":

            account_ids = self.company_id.supplier_statement_account_ids.ids

        attachments = []

        for partner in self.partner_ids:

            val = {

                'date_start': self.date_start,
                'date_end': self.date_end,
                'type': self.type,
                'partner_id': partner.id,
                'account_ids': account_ids,
                'company_id': self.company_id.id,
                'send': False,
                'attachment': False,
                'name': _('Statement from %s to %s for %s' % (self.date_start.strftime('%d-%m-%Y'), self.date_end.strftime('%d-%m-%Y'), partner.name)) 

            }

            report = self.env['rlbooks_statement.report.print'].create(val)

            attachment_id = report.action_generate_pdf_file(report,self._cr, self._uid, context=self._context)
            attachments += attachment_id

        if len(attachments) == 1:

            try:
                form_view_id = self.env.ref("rlbooks_statement.my_form_view_external_id").id
            except Exception as e:
                form_view_id = False

            return {

                'type': 'ir.actions.act_window',
                'name': 'Statement report',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': report.id,
                'res_model': 'rlbooks_statement.report.print',
                'views': [(form_view_id, 'form')],
                'target': 'current',

            }


        return  attachments

    def action_send_statement (self):

        if self.date_end < self.date_start:

            raise ValidationError("End date needs to be bigger than start date!")

        if self.type == "customer":

            account_ids = self.company_id.customer_statement_account_ids.ids
        
        elif self.type == "supplier":

            account_ids = self.company_id.supplier_statement_account_ids.ids
		
        missing_email = []
        have_email = []

        for partner in self.partner_ids:
            
            if partner.email:

                have_email += partner

            else:
                
                if partner.ref:

                    missing_email.append(partner.ref + " - " + partner.name)

                else:

                    missing_email.append(partner.name)

        template = self.env.ref('rlbooks_statement.rlbooks_statement_customer_statement')

        if len(missing_email) > 0:

            raise UserError("Nothing was sent. There is no email on the following: " + str(missing_email).strip('[]'))

        for partner in have_email:

            val = {

                'date_start': self.date_start,
                'date_end': self.date_end,
                'type': self.type,
                'partner_id': partner.id,
                'account_ids': account_ids,
                'company_id': self.company_id.id,
                'send': True,
                'attachment': False,
                'name': _('Statement from %s to %s for %s' % (self.date_start.strftime('%d-%m-%Y'), self.date_end.strftime('%d-%m-%Y'), partner.name)) 

            }

            report = self.env['rlbooks_statement.report.print'].create(val)

            attachment = report.action_generate_pdf_file(report,self._cr, self._uid, context=self._context)

            msg = _('Statement from %s to %s sent to %s - %s' % (self.date_start.strftime('%d-%m-%Y'), self.date_end.strftime('%d-%m-%Y'), partner.name, partner.email))
            
            lang = self.env.context.get('lang')     

            if partner.lang:

                lang = partner.lang

            template.attachment_ids = [(6, 0, [attachment.id])]

            ctx = {
                'default_model': 'res.partner',
                'default_res_id': partner.id,
                'default_use_template': bool(template.id),
                'default_template_id': template.id,
                'default_composition_mode': 'comment',
                'mark_so_as_sent': True,
                'custom_layout': "rlbooks_statement.rlbooks_statement_customer_statement",                
                'force_email': True
            }

            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(False, 'form')],
                'view_id': False,
                'target': 'new',
                'context': ctx,
            }


            # template.send_mail(partner.id, raise_exception=False, force_send=True)
            
            # partner.message_post(body=msg)

