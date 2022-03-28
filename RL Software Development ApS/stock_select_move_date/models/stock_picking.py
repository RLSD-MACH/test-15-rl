# -*- coding: utf-8 -*-

from odoo import fields, models, api

class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'
    
    date_of_transport = fields.Date(
        string='Date of transport', 
        readonly=True, 
        states={
            
            'draft':[('readonly',False)],
            'waiting':[('readonly',False)],
            'confirmed':[('readonly',False)],
            'assigned':[('readonly',False)],
            
        },
        copy=False)

    def write(self, vals):

        if 'date_done' in vals and 'priority' in vals:

            if self.date_of_transport:

                vals['date_done'] = self.date_of_transport

        res = super(StockPickingInherit, self).write(vals)
        
        return res

    def _action_done(self):

        res = super(StockPickingInherit, self)._action_done()
        
        if self.date_of_transport:

            done_moves = self.mapped('move_lines').filtered(lambda self: self.state in ['done'])

            done_moves.with_context(bypass_reservation_update=True).write({

                'date': self.date_of_transport

            })

        return res

    