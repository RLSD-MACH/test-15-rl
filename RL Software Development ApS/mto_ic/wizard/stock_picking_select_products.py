# -*- coding: utf-8 -*-
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api


class SelectProductsStockPicking(models.TransientModel):

    _name = 'stock.picking.select.products.wizard'
    _description = 'Select Products'

    def _get_default_picking_id(self):
        default_picking_id = self.env.context.get('active_id')
        return [default_picking_id] if default_picking_id else None

    picking_id = fields.Many2one('stock.picking', string='Stock Picking', default=_get_default_picking_id)
    stock_quant_ids = fields.Many2many('stock.quant', string='Products', domain="['&','&', (owner_id','=', picking_id.owner_id), '|', ('company_id', '=', False), ('company_id', '=', company_id), ('location_id.usage','=', 'internal')]")
    
    @api.onchange('picking_id')
    def _campus_onchange(self):
        res = {}
        res['domain']={'stock_quant_ids':[('owner_id', '=', self.picking_id.owner_id.id), ('location_id.usage','=', 'internal')]}
        return res

    def select_products(self):
        
        order_id = self.env['stock.picking'].browse(self._context.get('active_id', False))

        for quant in self.stock_quant_ids:

            self.env['stock.move'].create({

                'picking_id': order_id.id,
                # 'shipping_order_id': order_id.id,
                'owner_id': quant.owner_id.id,
                'product_id': quant.product_id.id,
                'name': quant.product_id.name,
                'product_uom': quant.product_uom_id.id,
                'product_uom_qty': quant.available_quantity,
                'company_id': order_id.company_id.id,
                'date': order_id.scheduled_date,
                'date_deadline': order_id.date_deadline, 
                # 'picking_type_code': order_id.picking_type_code,
                # 'form_view_ref':'stock.view_move_form', 
                # 'address_in_id': order_id.partner_id.id, 
                'picking_type_id': order_id.picking_type_id.id, 
                # 'location_id': order_id.location_id.id, 
                'location_id': quant.location_id.id,                 
                'location_dest_id': order_id.location_dest_id.id


                })
