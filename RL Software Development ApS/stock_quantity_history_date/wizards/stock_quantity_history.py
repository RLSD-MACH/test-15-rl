# -*- coding: utf-8 -*-

from odoo import _, models, fields
from odoo.tools.misc import format_datetime
from odoo.osv import expression

class StockQuantityHistoryInherit(models.TransientModel):
    _inherit = 'stock.quantity.history'

    owner_id = fields.Many2one('res.partner', string='Owner', required=False)

    def open_at_date(self):
        active_model = self.env.context.get('active_model')
        if active_model == 'stock.valuation.layer':
            action = self.env["ir.actions.actions"]._for_xml_id("stock_account.stock_valuation_layer_action")
            action['domain'] = [
            
                '&',

                    ('stock_move_id.owner_id', '=', self.owner_id.id),

                    '&',
                                                
                        ('product_id.type', '=', 'product'), 

                        '|',

                            ('account_move_date', '<=', self.inventory_datetime),

                            '&',
                                ('create_date', '<=', self.inventory_datetime), 
                                ('account_move_id', '=', False),             
                
            ]
            action['display_name'] = str(self.owner_id.name) + "'s goods per " + format_datetime(self.env, self.inventory_datetime) if self.owner_id.id else "Only our goods per " + format_datetime(self.env, self.inventory_datetime)
            return action

        else:

            tree_view_id = self.env.ref('stock.view_stock_product_tree').id
            form_view_id = self.env.ref('stock.product_form_view_procurement_button').id
            domain = [
                ('type', '=', 'product'),              
            ]
            product_id = self.env.context.get('product_id', False)
            product_tmpl_id = self.env.context.get('product_tmpl_id', False)
            if product_id:
                domain = expression.AND([domain, [('id', '=', product_id)]])
            elif product_tmpl_id:
                domain = expression.AND([domain, [('product_tmpl_id', '=', product_tmpl_id)]])                
            # We pass `to_date` in the context so that `qty_available` will be computed across
            # moves until date.
            action = {
                'type': 'ir.actions.act_window',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,form',
                'name': _('Products'),
                'res_model': 'product.product',
                'domain': domain,
                'context': dict(self.env.context, to_date=self.inventory_datetime, owner_id= self.owner_id.id),
            }
            return action

        # return super(StockQuantityHistoryInherit, self).open_at_date()

