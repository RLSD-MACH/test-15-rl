# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.tools.misc import format_datetime

class StockQuantityHistoryInherit(models.TransientModel):
    _inherit = 'stock.quantity.history'

    owner_id = fields.Many2one('res.partner', string='Owner', required=False)

    def open_at_date(self):
        active_model = self.env.context.get('active_model')
        if active_model == 'stock.valuation.layer':
            action = self.env["ir.actions.actions"]._for_xml_id("stock_account.stock_valuation_layer_action")
            action['domain'] = ['&','&','|','&',
            ('create_date', '<=', self.inventory_datetime), 
            ('account_move_date', '=', False), 
            ('account_move_date', '<=', self.inventory_datetime),
             ('product_id.type', '=', 'product'), 
             ('stock_move_id.owner_id', '=', self.owner_id.id)]
            action['display_name'] = str(self.owner_id.name) + "'s goods per " + format_datetime(self.env, self.inventory_datetime) if self.owner_id.id else "Only our goods per " + format_datetime(self.env, self.inventory_datetime)
            return action

        return super(StockQuantityHistoryInherit, self).open_at_date()

