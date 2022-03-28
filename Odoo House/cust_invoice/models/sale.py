# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if self.env.user.company_id:
            res['order_text'] = _(self.env.user.company_id.order_text)
        return res

    order_text = fields.Text('Quotation/Order Text', translate=True)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = super(SaleOrder, self).onchange_partner_id()
        self.order_text = self.company_id.with_context(lang=self.partner_id.lang or self.env.lang).order_text
        return res
