from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError


class AccountMoveLineInherit(models.Model):
    
    _inherit = 'account.move.line'

    origin_reference = fields.Char(string='Origin Reference', default="", store=True)    
        
    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:
            if "move_id" in vals:

                move = self.env['account.move'].browse(vals['move_id'])

                if move.id:

                    if move.stock_move_id.id:

                        vals['origin_reference'] = move.stock_move_id.origin

                    else:

                        vals['origin_reference'] = move.invoice_origin

                else:

                    vals['origin_reference'] = ""

        return super(AccountMoveLineInherit, self).create(vals_list)
    
    @api.model
    def write(self, vals):

        if "move_id" in vals:

            move = self.env['account.move'].browse(vals['move_id'])

            if move.id:

                if move.stock_move_id.id:

                    vals['origin_reference'] = move.stock_move_id.origin

                else:

                    vals['origin_reference'] = move.invoice_origin

            else:

                vals['origin_reference'] = ""

        return super(AccountMoveLineInherit, self).write(vals)

    
    
