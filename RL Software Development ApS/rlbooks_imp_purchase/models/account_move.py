from odoo import api, fields, models


class AccountMoveInherit(models.Model):
    
    _inherit = 'account.move'
    
    @api.onchange('partner_id')

    def _onchange_purchase_invoice_incoterm_id(self):
        
        for record in self:
    
            if record.is_purchase_document(include_receipts=True):

                record.update({
                    
                    'invoice_incoterm_id': record.partner_id.property_customer_incoterm_id.id
                })
    