from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError

class AccountMoveInherit(models.Model):
    
    _inherit = 'account.move'

    def _post(self, soft=True):

        ids = []

        for move in self:

            if move.move_type in ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']:

                if not move.fiscal_position_id.id:

                    raise UserError("Missing fiscal position on entry %s" % move.name)

                if move.company_id.account_sale_tax_id.id:

                    ids += [move.id]
       
        if len(ids) > 0:

            missing_vat = self.env['account.move.line'].search([['move_id','in',ids],['exclude_from_invoice_tab','=', False],['tax_ids','=',False],['account_id','!=',False]])
            
            if len(missing_vat) > 0:

                raise UserError("Some lines are missing af tax-code. Please select a zero tax-code, if it is not supposed to have taxes applied. ---- " + str(missing_vat))
           
        res = super(AccountMoveInherit, self)._post(soft)

        return res


