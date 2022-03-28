# -*- coding: utf-8 -*-

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    cust_sale_order_id = fields.Many2one(
        'sale.order', string='Cust Sales Order', readonly=True, copy=False)

    def _prepare_sale_order_data(self, name, partner, company, direct_delivery_address):
        res = super(PurchaseOrder, self)._prepare_sale_order_data(
            name, partner, company, direct_delivery_address)
        if self.cust_sale_order_id.client_order_ref:
            client_order_ref = res.get(
                'client_order_ref') + '/' + self.cust_sale_order_id.client_order_ref
        else:
            client_order_ref = res.get('client_order_ref')
        res['client_order_ref'] = client_order_ref
        return res
