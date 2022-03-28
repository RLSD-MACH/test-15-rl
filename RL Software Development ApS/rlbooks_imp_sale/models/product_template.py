# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _compute_open_sale_orders_count(self):

        orders = self.env['sale.order']

        for product in self:

            orders_list = orders.search([('order_line.product_template_id','=', product.id),('finished','=',False),('order_line.qty_to_deliver','>',0)])
            
            product.open_sale_orders_count = len(orders_list)

    open_sale_orders_count = fields.Integer(string="Open sale orders", compute='_compute_open_sale_orders_count', default=0, store=False)