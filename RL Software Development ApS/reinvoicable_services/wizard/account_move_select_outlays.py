# -*- coding: utf-8 -*-
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError, UserError
from odoo import models, fields, api


class AccountMoveSelectOutlay(models.TransientModel):

    _name = 'account.move.select.outlay.wizard'
    _description = 'Select Outlays'

    def _get_default_partner_id(self):
        default_partner_id = self.env.context.get('default_partner_id')
        return [default_partner_id] if default_partner_id else None

    def _get_default_line_ids(self):
        default_partner_id = self.env.context.get('default_partner_id')

        if default_partner_id:
            outlays = self.env['outlay'].search(['|',('partner_ids', '=', False),('partner_ids','in',[default_partner_id]),('open_balance','!=',0)])
            if outlays:

                new_outlays = []

                for outlay in outlays:

                    new_outlays += [self.env['account.move.select.outlay.line.wizard'].sudo().create({

                        'account_move_select_outlay_wizard_id': self.id,
                        'outlay_id': outlay.id,
                        'product_id': outlay.product_id.id,
                        'description': outlay.description,
                        'open_balance': outlay.open_balance,
                        'selected_percentage': 0,
                        'selected_balance': 0

                    }).id]
                # raise UserError(str(new_outlays))
                return new_outlays

        return None
        
    line_ids = fields.Many2many('account.move.select.outlay.line.wizard', 'account_move_select_outlay_line_wizard_line_rel', 'line_id', 'wizard_id', string='Lines', default=_get_default_line_ids)
    partner_id = fields.Many2one('res.partner', string='Customer', default=_get_default_partner_id)
       
    def select_outlays(self):
        
        move_id = self.env['account.move'].browse(self._context.get('active_id', False))
        outlays = []
        fiscal_position = move_id.fiscal_position_id
        lines_create = []

        for line in self.line_ids:

            if line.selected_balance != 0:

                outlay = line.outlay_id
                accounts = outlay.product_id.product_tmpl_id.get_product_accounts(fiscal_pos=fiscal_position)
                
                outlay_entry = self.env['outlay.entry'].create({

                    'active': True,
                    'company_id': move_id.company_id.id,
                    'outlay_id': outlay.id,
                    
                })
                   
                new_move_obj = {

                    'move_id': move_id.id,
                    'product_id': outlay.product_id.id,
                    'name': line.description,
                    'product_uom_id': outlay.product_uom_id.id,
                    'quantity': 1,
                    'price_unit': line.selected_balance,
                    'company_id': move_id.company_id.id,
                    'account_id': accounts['income'].id,
                    'exclude_from_invoice_tab': False,
                    'journal_id': move_id.journal_id.id,
                    'partner_id': move_id.commercial_partner_id.id,
                    'currency_id': move_id.currency_id.id,
                    'outlay_entry_id': outlay_entry.id

                }

                invoice_line = new_move_obj.copy()
                
                new_move_obj['account_id'] = accounts['expense'].id
                new_move_obj['exclude_from_invoice_tab'] = True
                new_move_obj['tax_ids'] = False                
                new_move_obj['price_unit'] = -new_move_obj['price_unit']
                
                debit = new_move_obj.copy()
                debit['outlay_id'] = outlay.id

                credit = new_move_obj.copy()
                credit['outlay_id'] = outlay.id
                credit['account_id'] = outlay.cost_line_id.account_id.id
                credit['price_unit'] = -new_move_obj['price_unit']
                                
                lines_create += [(0,0,invoice_line),(0,0,debit),(0,0,credit)]
                
                if outlay.id not in outlays:

                    outlays.append(outlay.id)
        
        if lines_create:

            move_id.update({'invoice_line_ids':lines_create})

            for line_tax in move_id.invoice_line_ids:

                taxes = line_tax._get_computed_taxes()
                if taxes and line_tax.move_id.fiscal_position_id:
                    taxes = line_tax.move_id.fiscal_position_id.map_tax(taxes)
                line_tax.tax_ids = taxes
                
        if outlays:
            
            outlays_ids = self.env['outlay'].browse(outlays)
            
            outlays_ids._compute_open_balance()


                

class AccountMoveSelectOutlayLine(models.TransientModel):

    _name = 'account.move.select.outlay.line.wizard'
    _description = 'Select Outlays Lines'

    account_move_select_outlay_wizard_id = fields.Many2one('account.move.select.outlay.wizard', string='Wizard', readonly=True,)
    outlay_id = fields.Many2one('outlay', string='Outlay', readonly=True,)
    product_id = fields.Many2one('product.product', string='Product', readonly=True,)
    description = fields.Char(required=False, string='Description', readonly=False,)
    open_balance = fields.Float(default="0", string='Open Balance', readonly=True,) 
    selected_percentage = fields.Float(default="0", string='Selected Percentage', readonly=False,) 
    selected_balance = fields.Float(default="0", string='Selected Balance', readonly=False,) 

    @api.onchange('selected_percentage')
    def _onchange_selected_percentage(self):

        self.selected_balance = self.selected_percentage / 100 * self.open_balance
    
    @api.onchange('selected_balance')
    def _onchange_selected_balance(self):

        if self.open_balance != 0:

            self.selected_percentage = self.selected_balance / self.open_balance * 100
        
        else:

            self.selected_percentage = 100

    @api.constrains('selected_balance')
    def _check_selected_balance(self):

        for record in self:

            if record.open_balance > 0:

                if record.selected_balance > record.open_balance:

                    raise ValidationError("You have selected more than there is open. Selected value: %s" % record.selected_balance)

            else:

                if -record.selected_balance > -record.open_balance:

                    raise ValidationError("You have selected more than there is open. Selected value: %s" % record.selected_balance)

    @api.constrains('selected_percentage')
    def _check_selected_percentage(self):

        for record in self:

            if record.selected_percentage > 100 or record.selected_percentage < 0:

                raise ValidationError("The percentage is invalid: %s" % record.selected_percentage)
                
   