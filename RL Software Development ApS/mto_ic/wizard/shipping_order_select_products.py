# -*- coding: utf-8 -*-
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api


class SelectProductsShippingOrder(models.TransientModel):

    _name = 'shipping.order.select.products.wizard'
    _description = 'Select Products'

    stock_quant_ids = fields.Many2many('stock.quant', string='Products')
    type = fields.Selection([
        ('select', 'Select products'),
        ('move', 'Create moves')
    ], string='')


    def select_products(self):
        
        order_id = self.env['shipping.order'].browse(self._context.get('active_id', False))

        if self.type == 'select':
            
            self.stock_quant_ids.write({
                
                'shipping_order_id': order_id.id

            })

        elif self.type == 'move':

            for quant in self.stock_quant_ids:

                self.env['stock.move'].create({

                    'shipping_order_id': order_id.id,
                    'product_id': quant.product_id.id,
                    'location_id': order_id.stock_origin_id.id,
                    'location_dest_id': order_id.stock_destination_id.id,
                    'name': quant.product_id.name,
                    'product_uom': quant.product_uom_id.id,
                    'product_uom_qty': quant.available_quantity,
                    'company_id': quant.company_id.id

                    })
