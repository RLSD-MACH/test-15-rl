# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def init(self): 

        for record in self:

            if record.partner_id.id != record.partner_invoice_id.id:

                record.update({

                    'partner_invoice_id': record.partner_id.id,

                })

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if self.company_id:
            res['order_text'] = self.company_id.with_context(lang=self.partner_id.lang or self.env.lang).order_text
        return res

    order_text = fields.Text('Quotation/Order Text', translate=False)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = super(SaleOrder, self).onchange_partner_id()

        self.order_text = self.company_id.with_context(lang=self.partner_id.lang or self.env.lang).order_text
               
        return res
