from email.policy import default
from odoo import api, fields, models
from odoo.tools import float_compare
from odoo.exceptions import ValidationError, UserError

class AccountMoveInherit(models.Model):
    
    _inherit = 'account.move'

    def _compute_outlay_count(self):

        entries = self.env['outlay']
        for move in self:
            move.outlay_count = entries.search_count([('account_move_id','=', move.id)])

    outlay_count = fields.Integer(string='Outlays', default="0", compute="_compute_outlay_count")
    
    def _post(self, soft=True):

        # raise UserError(str(self))

        res = super(AccountMoveInherit, self)._post(soft)

        for move in res:

            for line in move.invoice_line_ids:

                if line.product_id.type == 'service' and line.is_outlay:
                    
                    if move.move_type in ['in_invoice', 'in_refund']:

                        if line.outlay_id.id:

                            raise UserError("Why is there already a outlay registred on account move line id %s") % str(line.id)
                        
                        new_outlay = line._create_outlay()

                        line.outlay_id = new_outlay.id

                    elif move.move_type in ['out_invoice', 'out_refund']:

                        # new_outlay = self.env['outlay'].sudo().create({

                        #     'cost_line_id': line.id,
                        #     'partner_id': line.outlay_customer_id.id,
                        #     'description': line.name,
                        #     'product_id': line.product_id.id,
                        #     'product_uom_id': line.product_uom_id.id,
                        #     'quantity': line.quantity,
                        #     'cost_price_unit': line.balance / line.quantity if line.quantity != 0 else 0,
                        #     'cost_price_total': line.balance,

                        # })

                        continue


                  
                
        return res

class AccountMoveLineInherit(models.Model):
    
    _inherit = 'account.move.line'

    outlay_id = fields.Many2one('outlay', string='Outlay', copy=False)
    outlay_customer_ids = fields.Many2many('res.partner', string='Re-invoice outlay to', copy=False)
    outlay_entry_id = fields.Many2one('outlay.entry', string='Outlay Entry', readonly=True, ondelete='cascade', copy=True)
    is_outlay = fields.Boolean(string='Is outlay', default=False)
    
    
    def unlink(self):

        
        list_records = []
        
        for record in self:

            if record.outlay_entry_id: 

                outlay_entry = self.env['outlay.entry'].browse(record.outlay_entry_id.id)

                outlay_entry.unlink()

            else:

                list_records.append(record.id)

        if len(list_records) > 0:

            list_records = self.env['account.move.line'].search([['id','in',list_records]])
            
            return super(AccountMoveLineInherit, list_records).unlink()

        else:

            return False

    def _get_computed_account(self):
      
        self.ensure_one()

        self = self.with_company(self.move_id.journal_id.company_id)
        
        if self.product_id.type == 'service' and self.is_outlay \
            and self.move_id.company_id.anglo_saxon_accounting \
            and self.move_id.is_purchase_document():

            if self.company_id.outlay_balance_account_id:
                return self.company_id.outlay_balance_account_id.id

        return super(AccountMoveLineInherit, self)._get_computed_account()
    
    def action_move_to_outlay(self):
                    
        for line in self:

            account_id =  line.company_id.outlay_balance_account_id.id

            if not account_id:

                raise UserError("The balance account for outlays are not set in %s" % line.company_id.name)

            if line.outlay_id.id:
                
                raise UserError("%s - %s - Already is a part of an outlay (%s)" % (line.display_name, line.name, line.outlay_id.display_name)) 
                
            else:
                
                move = line.move_id

                vals = {
                      'quantity': (-1) * line.quantity,
                      'exclude_from_invoice_tab': True,
                      'account_id': line.account_id.id,
                      'debit':line.credit,
                      'credit': line.debit,
                      'currency_id': line.currency_id.id,
                      'amount_currency': (-1) * line.amount_currency,
                      'product_id': line.product_id.id,
                      'price_unit': line.price_unit,
                      'product_uom_id': line.product_uom_id.id,
                      'price_subtotal': (-1) * line.price_subtotal,
                      'name': line.name + " (moved to outlays)",
                      'company_id': line.company_id.id,
                      'journal_id': line.journal_id.id,
                      'partner_id':line.partner_id.id,
                      'outlay_entry_id': line.outlay_entry_id.id,
                      'move_id': move.id
                  }

                vals2 = {
                      'quantity': (1) * line.quantity,
                      'exclude_from_invoice_tab': True,
                      'account_id': account_id,
                      'debit': line.debit,
                      'credit': line.credit,
                      'currency_id': line.currency_id.id,
                      'amount_currency': (1) * line.amount_currency,
                      'product_id': line.product_id.id,
                      'price_unit': line.price_unit,
                      'product_uom_id': line.product_uom_id.id,
                      'price_subtotal': (1) * line.price_subtotal,
                      'name': line.name,
                      'company_id': line.company_id.id,
                      'journal_id': line.journal_id.id,
                      'partner_id':line.partner_id.id,
                      'outlay_entry_id': line.outlay_entry_id.id,
                      'move_id': move.id
                  }

                new_records = self.env['account.move.line'].create([

                    vals, vals2

                    ])

                outlay = new_records[1]._create_outlay()
                new_records[0].write({

                    'outlay_id': outlay.id

                })

                line.write({

                    'outlay_id': outlay.id

                })
                
                to_match = self.env['account.move.line'].browse([new_records[0].id, line.id])
                to_match.action_reconcile()
                
                
    
    def _create_outlay(self):
        
        return self.env['outlay'].sudo().create(self._get_outlay_values())
        
    def _get_outlay_values(self):
        
        return {

            'cost_line_id': self.id,
            'partner_ids': self.outlay_customer_ids.ids,
            'description': self.name,
            'new_description': self.name,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom_id.id,
            'quantity': self.quantity,
            'cost_price_unit': self.balance / self.quantity if self.quantity != 0 else 0,
            'cost_price_total': self.balance,
            'open_balance': self.balance,

        }
    
    