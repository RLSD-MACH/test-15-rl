# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_repr
from odoo.exceptions import ValidationError
from collections import defaultdict


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.depends('stock_valuation_layer_ids')
    @api.depends_context('to_date', 'company')
    def _compute_value_svl(self):
        """Compute `value_svl` and `quantity_svl`."""
        company_id = self.env.company.id
        domain = [
            ('product_id', 'in', self.ids),
            ('company_id', '=', company_id),
        ]

        owner_id = self.env.context.get('owner_id', False)
        domain.append(('stock_move_id.owner_id', '=', owner_id))
        
        if self.env.context.get('to_date'):
            to_date = fields.Datetime.to_datetime(self.env.context['to_date'])      
            domain.append(
                '|',

                    ('account_move_date', '<=', to_date),

                    '&',
                        ('create_date', '<=', to_date), 
                        ('account_move_id', '=', False),      
            )
                    
        groups = self.env['stock.valuation.layer'].read_group(domain, ['value:sum', 'quantity:sum'], ['product_id'])
        products = self.browse()
        for group in groups:
            product = self.browse(group['product_id'][0])
            product.value_svl = self.env.company.currency_id.round(group['value'])
            product.quantity_svl = group['quantity']
            products |= product
        remaining = (self - products)
        remaining.value_svl = 0
        remaining.quantity_svl = 0
