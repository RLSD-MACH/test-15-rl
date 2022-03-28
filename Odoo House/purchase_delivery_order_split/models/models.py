# -*- coding: utf-8 -*-

import datetime

from odoo import models, api, fields
from odoo.exceptions import ValidationError


class StockPickingExtended(models.Model):
    _inherit = "stock.picking"

    def split_purchase_delivery_order(self):
        for rec in self:
            delivery_items = []
            for move_id in rec.move_ids_without_package:
                delivery_items.append([0, 0, {'picking_id': move_id.picking_id.id,
                                              'product_id': move_id.product_id.id,
                                              'quantity': move_id.product_uom_qty,
                                              'source_loc_id': move_id.location_id.id,
                                              'destination_loc_id': move_id.location_dest_id.id,
                                              'stock_move_id': move_id.id,
                                              }])
            res_id = (
                self.env['purchase.delivery.order.split.wizard'].create(
                    {'transfer_item_detail_ids': delivery_items})).id

            return {
                'name': 'Split Transfer',
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.delivery.order.split.wizard',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': False,
                'res_id': res_id,
                'target': 'new',
            }


class TransferItemDetail(models.TransientModel):
    _name = "purchase.transfer.item.detail"
    _description = "purchase.transfer.item.detail"

    picking_id = fields.Many2one('stock.picking')
    stock_move_id = fields.Many2one('stock.move')
    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Float(string='Quantity')
    source_loc_id = fields.Many2one('stock.location', string='Source Location')
    destination_loc_id = fields.Many2one('stock.location', string='Destination Location')
    delivery_order_id = fields.Many2one('purchase.delivery.order.split.wizard')


class SplitDelivery(models.TransientModel):
    _name = "purchase.delivery.order.split.wizard"
    _description = "purchase.delivery.order.split.wizard"

    transfer_item_detail_ids = fields.One2many('purchase.transfer.item.detail', 'delivery_order_id')

    def split_purchase_transfer(self):

        flag = 1
        split_one = []
        split_two = []
        for rec in self.transfer_item_detail_ids:
            for move_id in rec.picking_id.move_ids_without_package:
                if rec.product_id == move_id.product_id:
                    if rec.quantity < move_id.product_uom_qty:
                        flag = 0
                        break
        if flag == 1:
            raise ValidationError('Orders with no modification is not allowed.')
        else:
            for rec in self.transfer_item_detail_ids:
                move_id = rec.stock_move_id
                qty_one = rec.quantity
                qty_two = move_id.product_uom_qty - rec.quantity
                if qty_one > 0.0:
                    split_one.append([0, 0, {'product_id': rec.product_id.id,
                                             'product_uom_qty': qty_one,
                                             'name': rec.product_id.name_get()[0][1],
                                             'date': datetime.datetime.now(),
                                             'date_deadline': datetime.datetime.now(),
                                             'product_uom': rec.product_id.uom_po_id.id,
                                             'location_id': rec.source_loc_id.id,
                                             'location_dest_id': rec.destination_loc_id.id,
                                             'purchase_line_id': move_id.purchase_line_id.id,
                                             }])
                if qty_two > 0.0:
                    split_two.append([0, 0, {'product_id': rec.product_id.id,
                                             'product_uom_qty': qty_two,
                                             'name': rec.product_id.name_get()[0][1],
                                             'date': datetime.datetime.now(),
                                             'date_deadline': datetime.datetime.now(),
                                             'product_uom': rec.product_id.uom_po_id.id,
                                             'location_id': rec.source_loc_id.id,
                                             'location_dest_id': rec.destination_loc_id.id,
                                             'purchase_line_id': move_id.purchase_line_id.id,
                                             }])
            new_delivery_orders_ids = []
            if len(split_one) > 0:
                obj = self.env['stock.picking'].create({
                    'partner_id': self.transfer_item_detail_ids[0].picking_id.partner_id.id,
                    'location_id': self.transfer_item_detail_ids[0].picking_id.location_id.id,
                    'location_dest_id': self.transfer_item_detail_ids[0].picking_id.location_dest_id.id,
                    'picking_type_id': self.transfer_item_detail_ids[0].picking_id.picking_type_id.id,
                    'backorder_id': self.transfer_item_detail_ids[0].picking_id.id,
                    'origin': self.transfer_item_detail_ids[0].picking_id.origin,
                    'move_ids_without_package': split_one})
                new_delivery_orders_ids.append(self.transfer_item_detail_ids[0].picking_id.id)
                new_delivery_orders_ids.append(obj.id)
                self.transfer_item_detail_ids[0].picking_id.state = 'cancel'

            if len(split_two) > 0:
                obj = self.env['stock.picking'].create({
                    'partner_id': self.transfer_item_detail_ids[0].picking_id.partner_id.id,
                    'location_id': self.transfer_item_detail_ids[0].picking_id.location_id.id,
                    'location_dest_id': self.transfer_item_detail_ids[0].picking_id.location_dest_id.id,
                    'picking_type_id': self.transfer_item_detail_ids[0].picking_id.picking_type_id.id,
                    'backorder_id': self.transfer_item_detail_ids[0].picking_id.id,
                    'origin': self.transfer_item_detail_ids[0].picking_id.origin,
                    'move_ids_without_package': split_two})
                new_delivery_orders_ids.append(obj.id)

            action = self.env.ref('stock.action_picking_tree_all').read()[0]
            action['domain'] = [('id', 'in', new_delivery_orders_ids)]
            return action
