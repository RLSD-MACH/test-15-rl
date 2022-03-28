# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import ValidationError, UserError

class StockMoveInherit(models.Model):
    _inherit = 'stock.move'
    
    def _account_entry_move(self, qty, description, svl_id, cost):

        am_vals = super(StockMoveInherit, self)._account_entry_move(qty, description, svl_id, cost)

        if am_vals:
            
            for val in am_vals:

                stock_move = self.env['stock.move'].browse(val['stock_move_id'])
                
                if stock_move:

                    if stock_move.picking_id.id:

                        if stock_move.picking_id.date_of_transport:

                            val['date'] = stock_move.picking_id.date_of_transport 

        return am_vals
