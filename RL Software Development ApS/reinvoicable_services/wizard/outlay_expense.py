# -*- coding: utf-8 -*-
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError, UserError
from odoo import models, fields, api
import copy


class OutlayExpenseWizard(models.TransientModel):

    _name = 'outlay.expense.wizard'
    _description = 'Outlay Expense'

    def _get_default_outlay_id(self):
        default_outlay_id = self.env.context.get('default_outlay_id')
        return [default_outlay_id] if default_outlay_id else None
    
    def _get_default_line_ids(self):
        default_outlay_id = self.env.context.get('default_outlay_id')
        
        if default_outlay_id:
            outlays = self.env['outlay'].browse(default_outlay_id)

            if outlays:

                new_outlays = []

                new_outlays += [self.env['outlay.expense.line.wizard'].sudo().create({

                    'wizard_id': self.id,
                    'partner_id': outlays.account_move_partner_id.id,
                    'account_id': outlays.company_id.outlay_expence_account_id.id,
                    'description': outlays.new_description,
                    'selected_percentage': 100,
                    'selected_balance': outlays.open_balance,
                    'date': outlays.date

                }).id]                    

                return new_outlays

        return None
    
    open_balance = fields.Float( related="outlay_id.open_balance", string='Cost to distribute', readonly=True,) 
    outlay_id = fields.Many2one('outlay', string='Outlay', default=_get_default_outlay_id)
    line_ids = fields.One2many('outlay.expense.line.wizard', 'wizard_id', string='Lines', default=_get_default_line_ids)    
    outlay_name = fields.Char(string='Outlay name', related="outlay_id.new_description")
    open_balance = fields.Float(string='Open', related="outlay_id.open_balance")
    default_account = fields.Many2one('account.account', related="outlay_id.company_id.outlay_expence_account_id")   
    company_id = fields.Many2one('res.company', related="outlay_id.company_id")
    date = fields.Date(string='Date', related="outlay_id.date")
    partner_id = fields.Many2one('res.partner', string='Partner', required=False, readonly=True, related="outlay_id.account_move_partner_id")
       
    def action_confirm_disbursment(self):
        
        original_cost_line = self.outlay_id.cost_line_id
        orginal_move = original_cost_line.move_id
                
        for line in self.line_ids:
            new_move = False
            
            if line.date != orginal_move.date:
                new_move = True
                move = self.env['account.move'].create({
                    
                    'date': line.date,
                    'currency_id': orginal_move.currency_id.id,
                    'move_type': 'entry',
                    'ref': 'Original entry: ' + orginal_move.name,
                    'journal_id': orginal_move.company_id.outlay_default_journal.id,
                    'fiscal_position_id': orginal_move.fiscal_position_id.id,
                    'company_id': orginal_move.company_id.id,                    
                    
                })

            else:
                move = orginal_move
            
            vals = {
                'quantity': -1,
                'exclude_from_invoice_tab': True,
                'account_id': original_cost_line.account_id.id,
                'debit': -line.selected_balance if line.selected_balance < 0 else 0 ,
                'credit': line.selected_balance if line.selected_balance > 0 else 0,
                'currency_id': original_cost_line.currency_id.id,
                'amount_currency': (-1) * (line.selected_balance / (original_cost_line.price_subtotal if original_cost_line.price_subtotal != 0 else 1)) * original_cost_line.amount_currency,
                'product_id': original_cost_line.product_id.id,
                'price_unit': original_cost_line.price_unit,
                'product_uom_id': original_cost_line.product_uom_id.id,
                'price_subtotal': (-1) * line.selected_balance,
                'name': original_cost_line.name + " (expenced)%s" % (" - " + line.description if line.description and line.description != original_cost_line.name else ""),
                'company_id': original_cost_line.company_id.id,
                'journal_id': original_cost_line.journal_id.id,
                'partner_id':original_cost_line.partner_id.id,
                'outlay_entry_id': original_cost_line.outlay_entry_id.id,
                'move_id': move.id
            }

            vals2 = copy.deepcopy(vals)
            
            vals2['quantity'] = -vals['quantity']
            vals2['debit'] = vals['credit']
            vals2['credit'] = vals['debit']
            if line.description:
                vals2['name'] = line.description
                
            if line.account_id.id:
                vals2['account_id'] = line.account_id.id  
            else:
                accounts = original_cost_line.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=move.fiscal_position_id)            
                vals2['account_id'] = accounts['expense'].id

            vals2['amount_currency'] = -vals['amount_currency']
            vals2['price_subtotal'] = -vals['price_subtotal']
            
            new_records = self.env['account.move.line'].create([
                vals, vals2
                ])

            outlay_entry = self.env['outlay.entry'].create({
                'active': True
            })

            new_records.write({

                'outlay_entry_id': outlay_entry.id

            })

            # line.account_move_line_id.write({

            #     'outlay_entry_id': outlay_entry.id

            # })
            
            if new_move:
                move.action_post()

        self.outlay_id._compute_open_balance()
                            

class OutlayExpenseLineWizard(models.TransientModel):

    _name = 'outlay.expense.line.wizard'
    _description = 'Outlay Expense Lines'

    def _get_default_wizard_id(self):
        wizard_id = self.env.context.get('default_wizard_id')
        return wizard_id if wizard_id else None

    def _get_default_description(self):
        description = self.env.context.get('default_description')
        return description if description else None

    def _get_default_account(self):
        account =  self.env.context.get('default_account_id') 
        return account if account else None
    
    def _get_default_partner(self):
        partner =  self.env.context.get('default_partner_id') 
        return partner if partner else None
    
    def _get_default_date(self):
        date =  self.env.context.get('default_date') 
        return date if date else None
            
    company_id = fields.Many2one('res.company', related="wizard_id.company_id")
    wizard_id = fields.Many2one('outlay.expense.wizard', string='Wizard', readonly=True, default=_get_default_wizard_id)
    account_id = fields.Many2one('account.account', string='Expence account', required=True, readonly=False, default=_get_default_account)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True, readonly=False, default=_get_default_partner)
    description = fields.Char(required=True, string='Description', readonly=False, default=_get_default_description)  
    selected_percentage = fields.Float(default="0", string='Cost - %', readonly=False,) 
    selected_balance = fields.Float(default="0", string='Cost Added', readonly=False,) 
    date = fields.Date(string='Date', default=_get_default_date)
    


    @api.onchange('selected_percentage')
    def _onchange_selected_percentage(self):

        self.selected_balance = self.selected_percentage / 100 * self.wizard_id.open_balance
    
    @api.onchange('selected_balance')
    def _onchange_selected_balance(self):

        if self.wizard_id.open_balance != 0:

            self.selected_percentage = self.selected_balance / self.wizard_id.open_balance * 100
        
        else:

            self.selected_percentage = 100

#     @api.constrains('selected_balance')
#     def _check_selected_balance(self):

#         for record in self:

#             if record.wizard_id.open_balance >= 0:

#                 if record.selected_balance > record.wizard_id.open_balance:

#                     raise ValidationError("You have selected more than there is open. Selected value: %s vs Open value: %s" % (record.selected_balance, record.wizard_id.open_balance))

#             else:

#                 if -record.selected_balance > -record.wizard_id.open_balance:

#                     raise ValidationError("You have selected more than there is open. Selected value: %s vs Open value: %s" % (record.selected_balance, record.wizard_id.open_balance))

    @api.constrains('selected_percentage')
    def _check_selected_percentage(self):

        for record in self:

            if record.selected_percentage > 100 or record.selected_percentage < 0:

                raise ValidationError("The percentage is invalid: %s" % record.selected_percentage)
                
   