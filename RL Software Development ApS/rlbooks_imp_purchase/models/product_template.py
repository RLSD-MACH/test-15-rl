# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'
 
    def _compute_open_purchase_orders_count(self):

        orders = self.env['purchase.order']

        for product in self:

            orders_list = orders.search([('order_line.product_template_id','=', product.id),('finished','=',False),('order_line.qty_to_receive','>',0)])
             
            product.open_purchase_orders_count = len(orders_list)
   
    open_purchase_orders_count = fields.Integer(string="Open purchase orders", compute='_compute_open_purchase_orders_count', default=0, store=False)