# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta, date
from odoo.exceptions import AccessError, UserError, ValidationError

class DanloenBookkeepingEmployee(models.Model):
    
    _name = 'danloen.bookkeeping.employee'
    _description = 'Danløn bogføringsbilag medarbejder'
    _order = 'id'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _check_company_auto = True

    def _compute_debit_credit(self):
        
        for record in self:

            debit = 0
            credit = 0

            for row in record.line_ids:

                debit += row.debit
                credit += row.credit

            record.write({

                'debit': debit,
                'credit': credit,
                'control': debit - credit

            })
   

    periode = fields.Char(string='Periode')

    name = fields.Char(string='Name')
    
    line_ids = fields.One2many('danloen.bookkeeping.employee.line', 'file_id', string='Lines')

    debit = fields.Float(string='Debit', compute='_compute_debit_credit')
    credit = fields.Float(string='Credit', compute='_compute_debit_credit')
    control = fields.Float(string='Control', compute='_compute_debit_credit')
    
    active = fields.Boolean(required=True, string='Active', default=True)
    
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)


    def action_extract_text_pdf (self):
        
        for record in self:

            docs = record.message_main_attachment_id.extract_text_pdf_danloen_bookkeeping_employee()

            line_env = self.env['danloen.bookkeeping.employee.line']

            for doc in docs:

                if 'periode' in doc:

                    self.periode = doc['periode']

                if 'name' in doc:

                    self.name = doc['name']

                # raise UserError(str(doc["table_lines"]))

                for line in doc["table_lines"]:

                    new_line = line_env.create({

                        'file_id': record.id,
                        'employee': line['employee'],
                        'account': line['account'],
                        'text': line['text'],
                        'debit': float(line['debit'].replace(".","").replace(',','.')) if line['debit'] != '' else 0,
                        'credit': float(line['credit'].replace(".","").replace(',','.')) if line['credit'] != '' else 0,

                    })
                        
    def create_from_attachment(self, attachment_ids=[]):
        
        attachments = self.env['ir.attachment'].browse(attachment_ids)

        if not attachments:

            raise UserError(_("No attachment was provided"))

        files = self.env['danloen.bookkeeping.employee']

        for attachment in attachments:

            attachment.write({'res_model': 'mail.compose.message'})
            
            file = self.env['danloen.bookkeeping.employee'].create({

                'name': "Uploaded - draft"

            })
            
            file.with_context(no_new_file=True).message_post(attachment_ids=[attachment.id])

            file.action_extract_text_pdf()

            files += file

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

        # action_vals = {
        #     'name': _('Generated Files'),
        #     'domain': [('id', 'in', files.ids)],
        #     'res_model': 'danloen.bookkeeping.employee',
        #     'views': [[False, "tree"], [False, "form"]],
        #     'view_id': False,
        #     'target': 'current',
        #     'type': 'ir.actions.act_window',
        #     'view_mode': 'tree, form',
        #     'context': self._context
        # }

        # return action_vals

    
class DanloenBookkeepingEmployeeLine(models.Model):
    
    _name = 'danloen.bookkeeping.employee.line'
    _description = 'Danløn bogføringsbilag medarbejder linjer'
    _order = 'id'
    _check_company_auto = True

    def _compute_balance(self):
        
        for record in self:

            record.balance = record.debit - record.credit

    file_id = fields.Many2one('danloen.bookkeeping.employee', string='File')
    periode = fields.Char(related="file_id.periode")
    employee = fields.Char(string='Employee')
    account = fields.Integer(string='Account')
    text = fields.Char(string='Text')
    debit = fields.Float(string='Debit')
    credit = fields.Float(string='Credit')
    balance = fields.Float(string='Balance', compute='_compute_balance')
    
    active = fields.Boolean(related="file_id.active")
    
    company_id = fields.Many2one('res.company', 'Company', related="file_id.company_id")

    