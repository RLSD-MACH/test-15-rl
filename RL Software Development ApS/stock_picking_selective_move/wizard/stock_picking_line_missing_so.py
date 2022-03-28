# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError, UserError
from odoo import models, fields, api


class StockPickingAddSolineWizard(models.TransientModel):

    _name = 'stock.picking.add_so_line.wizard'
    _description = 'Stock Picking line missing so'
    _check_company_auto = True

    def _get_default_picking_id(self):
        default_picking_id = self.env.context.get('default_picking_id')
        return [default_picking_id] if default_picking_id else None

    def _get_default_line_ids(self):

        default_picking_id = self.env.context.get('default_picking_id')
        picking = self.env['stock.picking'].browse(default_picking_id)
        
        if default_picking_id:
            lines = self.env['stock.move'].search([('picking_id', '=', default_picking_id),('sale_line_id','=',False),('quantity_done','!=',0)])
            if lines:

                new_lines = []

                for line in lines:

                    new_lines += [self.env['stock.picking.add_so_line.line.wizard'].sudo().create({

                        'wizard_id': self.id,
                        'line_id': line.id,
                        'quantity_done': line.quantity_done,
                        'default_code': line.product_id.default_code,
                        'description': line.product_id.name,
                        'product_uom_qty': line.product_uom_qty,
                        'sale_id': picking.sale_id.id

                    }).id]

                return new_lines

        return None
        
    line_ids = fields.Many2many('stock.picking.add_so_line.line.wizard', 'stock_picking_add_so_line_line_wizard_line_rel', 'line_id', 'wizard_id', string='Lines', default=_get_default_line_ids)
    picking_id = fields.Many2one('stock.picking', string='Picking', default=_get_default_picking_id)
    sale_id = fields.Many2one('sale.order', related="picking_id.sale_id")
    company_id = fields.Many2one('res.company', related="picking_id.company_id")
   
    def done(self):
       
        not_filled_out = []
        for line in self.line_ids:

            if not line.order_line_id.id and not line.new:
                not_filled_out += [line]
                
        if len(not_filled_out) > 0:
           raise UserError(str("You need to fill out all lines. Either select the create new line option or select an existing salesorder line"))

        for line in self.line_ids:

            if line.order_line_id.id:

                line.line_id.write({

                    'sale_line_id': line.order_line_id.id

                })

        return self.picking_id.with_context(ignore_missing_so_lines=True).button_validate()

        


                

class StockPickingAddSolineLineWizard(models.TransientModel):

    _name = 'stock.picking.add_so_line.line.wizard'
    _description = 'Select Outlays Lines'
    _check_company_auto = True

    wizard_id = fields.Many2one('stock.picking.add_so_line.wizard', string='Wizard', readonly=True,)
    sale_id = fields.Many2one('sale.order', readonly=True)
    order_line_id = fields.Many2one('sale.order.line', string='Salesorder line', readonly=False,domain=[('order_id','=',sale_id)])
    line_id = fields.Many2one('stock.move', string='Move', readonly=True,)
    default_code = fields.Char(required=False, string='Ref', readonly=True,)
    description = fields.Char(required=False, string='Description', readonly=True,)
    quantity_done = fields.Float(default="0", string='Done QTY', readonly=True,) 
    product_uom_qty = fields.Float(default="0", string='Demand QTY', readonly=True,) 
    new = fields.Boolean(string='New line on salesorder', default=False)
    company_id = fields.Many2one('res.company', related="wizard_id.company_id")
    
   