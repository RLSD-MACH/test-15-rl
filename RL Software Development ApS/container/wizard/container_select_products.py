# -*- coding: utf-8 -*-
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError


class SelectProductsContainer(models.TransientModel):

    _name = 'container.select.products.wizard'
    _description = 'Select Products'

    product_ids = fields.Many2many('stock.quant', string='Products')
    # flag_order = fields.Char('Flag Order')

    def select_products(self):
        # if self.flag_order == 'so':

        container_id = self.env['container'].browse(self._context.get('active_id', False))

        if container_id.current_stock_location_id:

            self.product_ids.write({
                
                'container_id': container_id.id,
                'location_id': container_id.current_stock_location_id.id,

            })
        
        else:

            self.product_ids.write({
                
                'container_id': container_id.id,

            })

        # for product in self.product_ids:
            # self.env['sale.order.line'].create({
            #     'product_id': product.id,
            #     'product_uom': product.uom_id.id,
            #     'price_unit': product.lst_price,
            #     'order_id': order_id.id
            #     })

        # elif self.flag_order == 'po':
        #     order_id = self.env['purchase.order'].browse(self._context.get('active_id', False))
        #     for product in self.product_ids:
        #         self.env['purchase.order.line'].create({
        #             'product_id': product.id,
        #             'name': product.name,
        #             'date_planned': order_id.date_planned or datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
        #             'product_uom': product.uom_id.id,
        #             'price_unit': product.lst_price,
        #             'product_qty': 1.0,
        #             'display_type': False,
        #             'order_id': order_id.id
        #         })

    def unselect_products(self):
        
        not_my_stock = self.product_ids.filtered(lambda stock: stock.container_id.id  != self._context.get('active_id', False))

        if not_my_stock:

            raise UserError("Not all stock selected where from current container!")

        self.product_ids.write({
            
            'container_id': False

        })
        