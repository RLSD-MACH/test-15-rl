# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if self.env.user.company_id:
            res['invoice_text'] = self.env.user.company_id.invoice_text
        return res

    invoice_text = fields.Text('Invoice Text', translate=True)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        # OVERRIDE
        # Recompute 'partner_shipping_id' based on 'partner_id'.
        res = super(AccountMove, self)._onchange_partner_id()

        # Recompute 'narration' based on 'company.invoice_terms'.
        if self.move_type == 'out_invoice':
            self.invoice_text = self.company_id.with_context(lang=self.partner_id.lang or self.env.lang).invoice_text

        return res
