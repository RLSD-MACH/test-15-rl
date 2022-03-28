# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountMove(models.Model):
    
    _inherit = "account.move"

    invoice_text = fields.Text('Invoice Text', translate=False)
   
    @api.model
    def create(self, vals):

        if vals.get('company_id', False) != False and vals.get('partner_id', False) != False and vals.get('move_type', False) in ['out_invoice','out_refund']:
            
            company = self.env['res.company'].browse(vals.get('company_id'))
            partner = self.env['res.partner'].browse(vals.get('partner_id'))

            if 'invoice_text' not in vals or vals.get('company_id', False) == False or vals.get('company_id', False) == "":

                vals['invoice_text'] = company.with_context(lang=partner.lang or self.env.lang).invoice_text

        res = super(AccountMove, self).create(vals)
        return res

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        # OVERRIDE
        # Recompute 'partner_shipping_id' based on 'partner_id'.
        res = super(AccountMove, self)._onchange_partner_id()

        # Recompute 'narration' based on 'company.invoice_terms'.
        if self.move_type in ['out_invoice','out_refund']:
            self.invoice_text = self.company_id.with_context(lang=self.partner_id.lang or self.env.lang).invoice_text

        return res
