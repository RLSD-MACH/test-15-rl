# -*- coding: utf-8 -*-
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError, UserError
from odoo import models, fields, api
import copy


class OutlaySelectAccountMoveWizard(models.TransientModel):

    _name = 'outlay.select.account.move.wizard'
    _description = 'Outlay Select Account Moves'

    def _get_default_outlay_id(self):
        default_outlay_id = self.env.context.get('default_outlay_id')
        return [default_outlay_id] if default_outlay_id else None
    
    
    line_ids = fields.One2many('outlay.select.account.move.line.wizard', 'wizard_id', string='Lines',)
    open_balance = fields.Float( related="outlay_id.open_balance", string='Cost to distribute', readonly=True,) 
    outlay_id = fields.Many2one('outlay', string='Outlay', default=_get_default_outlay_id)
    company_id = fields.Many2one('res.company', related="outlay_id.company_id")
    
       
    def action_confirm_disbursment(self):
        
        original_cost_line = self.outlay_id.cost_line_id

        for line in self.line_ids:
            
            if line.selected_balance != 0:

                move = line.account_move_id

                if move.partner_id.id not in self.outlay_id.partner_ids.ids:

                    self.outlay_id.write({
                        'partner_ids':  [(4, move.partner_id.id)]
                    })

                vals = {
                    'quantity': -1,
                    'exclude_from_invoice_tab': True,
                    'account_id': original_cost_line.account_id.id,
                    'debit': -line.selected_balance if line.selected_balance < 0 else 0 ,
                    'credit': line.selected_balance if line.selected_balance > 0 else 0,
                    'currency_id': original_cost_line.currency_id.id,
                    'amount_currency': (-1) * (line.selected_balance / (original_cost_line.price_subtotal if original_cost_line.price_subtotal != 0 else 1)) * original_cost_line.amount_currency,
                    'product_id': original_cost_line.product_id.id,
                    'price_unit': original_cost_line.price_unit * (line.selected_balance / (original_cost_line.price_subtotal if original_cost_line.price_subtotal != 0 else 1)),
                    'product_uom_id': original_cost_line.product_uom_id.id,
                    'price_subtotal': (-1) * line.selected_balance,
                    'name': "B: " + original_cost_line.move_id.name + " - " + original_cost_line.name + " (moved to invoice costs)%s" % (" - " + line.comment if line.comment else ""),
                    'company_id': original_cost_line.company_id.id,
                    'journal_id': original_cost_line.journal_id.id,
                    'partner_id':original_cost_line.partner_id.id,
                    'outlay_entry_id': original_cost_line.outlay_entry_id.id,
                    'move_id': move.id
                }

                vals2 = copy.deepcopy(vals)

                accounts = original_cost_line.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=move.fiscal_position_id)

                vals2['quantity'] = -vals['quantity']
                vals2['debit'] = vals['credit']
                vals2['credit'] = vals['debit']
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

                line.account_move_line_id.write({

                    'outlay_entry_id': outlay_entry.id

                })

        self.outlay_id._compute_open_balance()
                            

class OutlaySelectAccountMoveLineWizard(models.TransientModel):

    _name = 'outlay.select.account.move.line.wizard'
    _description = 'Outlay Select Account Moves Lines'

    def _get_default_wizard_id(self):
        wizard_id = self.env.context.get('default_wizard_id')
        return wizard_id if wizard_id else None

    company_id = fields.Many2one('res.company', related="wizard_id.company_id")
    wizard_id = fields.Many2one('outlay.select.account.move.wizard', string='Wizard', readonly=True, default=_get_default_wizard_id)
    account_move_line_id = fields.Many2one('account.move.line', string='Invoice Line', readonly=False,)
    account_move_id = fields.Many2one('account.move', string='Invoice', related="account_move_line_id.move_id", readonly=True,)
    description = fields.Char(required=False, string='Description', readonly=True, related="account_move_line_id.name")  
    comment = fields.Text('Comment',help='')  
    selected_percentage = fields.Float(default="0", string='Cost - %', readonly=False,) 
    selected_balance = fields.Float(default="0", string='Cost Added', readonly=False,) 

    @api.onchange('selected_percentage')
    def _onchange_selected_percentage(self):

        self.selected_balance = self.selected_percentage / 100 * self.wizard_id.open_balance
    
    @api.onchange('selected_balance')
    def _onchange_selected_balance(self):

        if self.wizard_id.open_balance != 0:

            self.selected_percentage = self.selected_balance / self.wizard_id.open_balance * 100
        
        else:

            self.selected_percentage = 100

    @api.constrains('selected_balance')
    def _check_selected_balance(self):

        for record in self:

            if record.wizard_id.open_balance > 0:

                if record.selected_balance > record.wizard_id.open_balance:

                    raise ValidationError("You have selected more than there is open. Selected value: %s" % record.selected_balance)

            else:

                if -record.selected_balance > -record.wizard_id.open_balance:

                    raise ValidationError("You have selected more than there is open. Selected value: %s" % record.selected_balance)

    @api.constrains('selected_percentage')
    def _check_selected_percentage(self):

        for record in self:

            if record.selected_percentage > 100 or record.selected_percentage < 0:

                raise ValidationError("The percentage is invalid: %s" % record.selected_percentage)
                
   