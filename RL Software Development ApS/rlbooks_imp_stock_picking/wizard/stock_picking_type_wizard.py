from odoo import models, fields, api
from datetime import datetime

class StockPickingTypeWizard(models.TransientModel):

    _name = 'stock.picking.change_type.wizard'
    _description = 'Stock picking change type'

    def _get_default_order_id(self):
        default_order_id = self.env.context.get('default_order_id')
        return [default_order_id] if default_order_id else None
    
    def _get_default_picking_type_id(self):
        default_picking_type_id = self.env.context.get('default_picking_type_id')
        return [default_picking_type_id] if default_picking_type_id else None
  
    order_id = fields.Many2one("stock.picking", string='Stock picking', ondelete='restrict',required=True, default=_get_default_order_id, readonly=True)
    picking_type_id = fields.Many2one("stock.picking.type", string='Operation Type', ondelete='restrict',required=True, default=_get_default_picking_type_id, readonly=False)

    def action_submit(self):
                
        order = self.env['stock.picking'].browse(self.order_id.id)
        
        order.picking_type_id = self.picking_type_id.id
    
        pass
        



    

