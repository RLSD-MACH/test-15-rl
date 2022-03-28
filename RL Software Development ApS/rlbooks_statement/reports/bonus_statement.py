from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
import base64

class BonusStatementReportPrint(models.Model):

    _name = 'rlbooks_statement.bonus_report.print'
    _description = 'Bonus report'
    _check_company_auto = True
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'id'    
    _order = 'id desc'

    
    name = fields.Char(required=True,string='Name', readonly=True)
    date_start = fields.Date(string='Periode start', required=True, readonly=True)
    date_end = fields.Date(string='Periode end', required=True, readonly=True)
    type = fields.Selection(selection = [('customer', 'Print customer statement'), ('supplier', 'Print supplier statement')], required=True, readonly=True,string='Type',default="customer")
    partner_id = fields.Many2one("res.partner", string='Partner', readonly=True, required=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    type_ids = fields.Many2many("account_move_type", string='Types', required=True, readonly=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, readonly=True, index=True, default=lambda self: self.env.company)   
    bonus_goods = fields.Float(required=True, readonly=True, string='Bonus % goods', default=0) 
    bonus_consus = fields.Float(required=True, readonly=True, string='Bonus % consus', default=0) 
    bonus_services = fields.Float(required=True, readonly=True, string='Bonus % services', default=0)
    bonus_goods_pct = fields.Float(readonly=True, string='Bonus % goods', compute="_compute_bonus_goods_pct") 
    bonus_consus_pct = fields.Float(readonly=True, string='Bonus % consus', compute="_compute_bonus_consus_pct") 
    bonus_services_pct = fields.Float(readonly=True, string='Bonus % services', compute="_compute_bonus_services_pct")
   
    send = fields.Boolean(required=True, readonly=True, string='Send', default=False)
    attachment = fields.Many2one("ir.attachment", string='Attachment', readonly=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    
    @api.depends('bonus_goods')
    def _compute_bonus_goods_pct(self):

        for record in self:

            if record.bonus_goods:

                record.bonus_goods_pct = record.bonus_goods * 100
            
            else:

                record.bonus_goods_pct = 0

    @api.depends('bonus_consus')
    def _compute_bonus_consus_pct(self):

        for record in self:

            if record.bonus_consus:

                record.bonus_consus_pct = record.bonus_consus * 100
            
            else:

                record.bonus_consus_pct = 0

    @api.depends('bonus_services')
    def _compute_bonus_services_pct(self):

        for record in self:

            if record.bonus_services:

                record.bonus_services_pct = record.bonus_services * 100
            
            else:

                record.bonus_services_pct = 0

    def action_generate_pdf_file(self, cr, uid, ids, context=None):
        
        if self.attachment.id == False:

            data, data_format = self.env.ref('rlbooks_statement.bonus_report_print').sudo()._render_qweb_pdf([self.id])

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

class AccountMoveType(models.Model):

    _name = 'account_move_type'
    _description = 'Account move type'

    name = fields.Char(required=True,string='Name', readonly=True)
    type = fields.Char(required=True,string='Type', readonly=True)
        

class BonusStatementReportWizard(models.TransientModel):

    _name = 'rlbooks_statement.bonus_report.wizard'
    _description = 'Bonus report'
    _check_company_auto = True

    def _get_default_partner_id(self):
        default_partner_id = self.env.context.get('default_partner_id')
        return [default_partner_id] if default_partner_id else None

    def _get_default_types(self):
        
        default_type_ids = self.env['account_move_type'].search([['type','in',['out_invoice','out_refund']]])
        return default_type_ids if default_type_ids else None
    
    date_start = fields.Date(string='Periode start', required=True)
    date_end = fields.Date(string='Periode end', required=True)
    type = fields.Selection(selection = [('customer', 'Print customer statement'), ('supplier', 'Print supplier statement')], required=True,string='Type',default="customer")
    partner_id = fields.Many2one("res.partner", string='Partners', default=_get_default_partner_id, required=True, domain="['&',('property_bonus_schema','=',True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    type_ids = fields.Many2many("account_move_type", string='Types', required=True, default=_get_default_types)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    bonus_goods = fields.Float(required=True, string='Bonus % goods', default=0) 
    bonus_consus = fields.Float(required=True, string='Bonus % consumables', default=0) 
    bonus_services = fields.Float(required=True, string='Bonus % services', default=0)
    
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        
        for record in self:

            if record.partner_id:

                if record.partner_id.property_bonus_schema:
                           
                    record.update({
                        
                        'bonus_goods': record.partner_id.property_bonus_goods,
                        'bonus_consus': record.partner_id.property_bonus_consus,
                        'bonus_services': record.partner_id.property_bonus_services

                    })

                else:

                    raise UserError("This partner is not registred as 'Earns bonus'!")

    @api.constrains('bonus_goods')
    def _check_bonus_goods(self):

        for record in self:

            if record.bonus_goods:

                if record.bonus_goods > 1 or record.bonus_goods < -1:

                    record.bonus_goods = 0

                    raise ValidationError("A bonus can only be between -100% and 100%")

    @api.constrains('bonus_consus')
    def _check_bonus_consus(self):

        for record in self:

            if record.bonus_consus:

                if record.bonus_consus > 1 or record.bonus_consus < -1:

                    record.bonus_consus = 0

                    raise ValidationError("A bonus can only be between -100% and 100%")
    
    @api.constrains('bonus_services')
    def _check_bonus_services(self):

        for record in self:

            if record.bonus_services:

                if record.bonus_services > 1 or record.bonus_services < -1:

                    record.bonus_services = 0

                    raise ValidationError("A bonus can only be between -100% and 100%")

    def action_print_save_pdf (self):

        if self.date_end < self.date_start:

            raise ValidationError("End date needs to be bigger than start date!")
       
        attachments = []

        val = {

            'date_start': self.date_start,
            'date_end': self.date_end,
            'type': self.type,
            'partner_id': self.partner_id.id,
            'type_ids': self.type_ids.ids,
            'company_id': self.company_id.id,
            'bonus_goods': self.bonus_goods,
            'bonus_consus': self.bonus_consus,
            'bonus_services': self.bonus_services,
            'send': False,
            'attachment': False,
            'name': _('Bonus statement from %s to %s for %s' % (self.date_start.strftime('%d-%m-%Y'), self.date_end.strftime('%d-%m-%Y'), self.partner_id.name)) 

        }
       
        report = self.env['rlbooks_statement.bonus_report.print'].create(val)

        attachment_id = report.action_generate_pdf_file(report,self._cr, self._uid, context=self._context)
        attachments += attachment_id

        if len(attachments) == 1:

            try:
                form_view_id = self.env.ref("rlbooks_statement.my_form_view_external_id").id
            except Exception as e:
                form_view_id = False

            return {

                'type': 'ir.actions.act_window',
                'name': 'Bonus Statement',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': report.id,
                'res_model': 'rlbooks_statement.bonus_report.print',
                'views': [(form_view_id, 'form')],
                'target': 'current',
            }

        return  attachments

    def action_send_statement (self):

        if self.date_end < self.date_start:

            raise ValidationError("End date needs to be bigger than start date!")
       
        if self.partner_id.email == False:

            raise UserError("Partner is missing email")
        
        val = {

            'date_start': self.date_start,
            'date_end': self.date_end,
            'type': self.type,
            'partner_id': self.partner_id.id,
            'type_ids': self.type_ids.ids,
            'company_id': self.company_id.id,            
            'bonus_goods': self.bonus_goods,
            'bonus_consus': self.bonus_consus,
            'bonus_services': self.bonus_services,
            'send': True,
            'attachment': False,
            'name': _('Bonus statement from %s to %s for %s' % (self.date_start.strftime('%d-%m-%Y'), self.date_end.strftime('%d-%m-%Y'), self.partner_id.name)) 

        }

        report = self.env['rlbooks_statement.bonus_report.print'].create(val)

        attachment = report.action_generate_pdf_file(report,self._cr, self._uid, context=self._context)

        msg = _('Bonus statement from %s to %s sent to %s - %s' % (self.date_start.strftime('%d-%m-%Y'), self.date_end.strftime('%d-%m-%Y'), self.partner_id.name, self.partner_id.email))
        
        lang = self.env.context.get('lang')     

        if self.partner_id.lang:

            lang = self.partner_id.lang

        template = self.env.ref('rlbooks_statement.rlbooks_statement_customer_statement')
        template.attachment_ids = [(6, 0, [attachment.id])]

        ctx = {
            'default_model': 'res.partner',
            'default_res_id': self.partner_id.id,
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


