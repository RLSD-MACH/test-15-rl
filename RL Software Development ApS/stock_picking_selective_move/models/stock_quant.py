from odoo import api, fields, models

import logging

from psycopg2 import Error, OperationalError

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools.float_utils import float_compare, float_is_zero

class StockQuantInherit(models.Model):
    
    _inherit = 'stock.quant'

    # container_id = fields.Many2one('container', string='Container')
    sale_order_id = fields.Many2one('sale.order', string='Sale order')
    so_cutomer_id = fields.Many2one('res.partner', string='End customer', related="sale_order_id.partner_id")
    # shipping_order_id = fields.Many2one('shipping.order', string='Shipping order')
   

    def _gather(self, product_id, location_id, lot_id=None, package_id=None, owner_id=None, container_id=None, sale_order_id=None, shipping_order_id=None, strict=False):
        
        removal_strategy = self._get_removal_strategy(product_id, location_id)
        removal_strategy_order = self._get_removal_strategy_order(removal_strategy)

        domain = [('product_id', '=', product_id.id)]
        if not strict:

            if lot_id:
                domain = expression.AND([[('lot_id', '=', lot_id.id)], domain])
            if package_id:
                domain = expression.AND([[('package_id', '=', package_id.id)], domain])
            if owner_id:
                domain = expression.AND([[('owner_id', '=', owner_id.id)], domain])
            # if container_id:
            #     domain = expression.AND([[('container_id', '=', container_id.id if container_id else False)], domain])
            if sale_order_id:
                domain = expression.AND([[('sale_order_id', '=', sale_order_id.id if sale_order_id else False)], domain])
            # if shipping_order_id:
            #     domain = expression.AND([[('shipping_order_id', '=', shipping_order_id.id if shipping_order_id else False)], domain])

            domain = expression.AND([[('location_id', 'child_of', location_id.id if location_id else False)], domain])

        else:

            domain = expression.AND([[('lot_id', '=', lot_id and lot_id.id or False)], domain])
            domain = expression.AND([[('package_id', '=', package_id and package_id.id or False)], domain])
            domain = expression.AND([[('owner_id', '=', owner_id and owner_id.id or False)], domain])
            domain = expression.AND([[('location_id', '=', location_id.id)], domain])
            # domain = expression.AND([[('container_id', '=', container_id.id if container_id else False)], domain])
            domain = expression.AND([[('sale_order_id', '=', sale_order_id.id if sale_order_id else False)], domain])
            # domain = expression.AND([[('shipping_order_id', '=', shipping_order_id.id if shipping_order_id else False)], domain])

        return self.search(domain, order=removal_strategy_order)

    @api.model
    def _get_available_quantity(self, product_id, location_id, lot_id=None, package_id=None, owner_id=None, container_id=None, sale_order_id=None, shipping_order_id=None, strict=False, allow_negative=False):
        """ Return the available quantity, i.e. the sum of `quantity` minus the sum of
        `reserved_quantity`, for the set of quants sharing the combination of `product_id,
        location_id` if `strict` is set to False or sharing the *exact same characteristics*
        otherwise.
        This method is called in the following usecases:
            - when a stock move checks its availability
            - when a stock move actually assign
            - when editing a move line, to check if the new value is forced or not
            - when validating a move line with some forced values and have to potentially unlink an
              equivalent move line in another picking
        In the two first usecases, `strict` should be set to `False`, as we don't know what exact
        quants we'll reserve, and the characteristics are meaningless in this context.
        In the last ones, `strict` should be set to `True`, as we work on a specific set of
        characteristics.

        :return: available quantity as a float
        """
        self = self.sudo()
        quants = self._gather(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, container_id=container_id, sale_order_id=sale_order_id, shipping_order_id=shipping_order_id, strict=strict)
        rounding = product_id.uom_id.rounding
        if product_id.tracking == 'none':
            available_quantity = sum(quants.mapped('quantity')) - sum(quants.mapped('reserved_quantity'))
            if allow_negative:
                return available_quantity
            else:
                return available_quantity if float_compare(available_quantity, 0.0, precision_rounding=rounding) >= 0.0 else 0.0
        else:
            availaible_quantities = {lot_id: 0.0 for lot_id in list(set(quants.mapped('lot_id'))) + ['untracked']}
            for quant in quants:
                if not quant.lot_id:
                    availaible_quantities['untracked'] += quant.quantity - quant.reserved_quantity
                else:
                    availaible_quantities[quant.lot_id] += quant.quantity - quant.reserved_quantity
            if allow_negative:
                return sum(availaible_quantities.values())
            else:
                return sum([available_quantity for available_quantity in availaible_quantities.values() if float_compare(available_quantity, 0, precision_rounding=rounding) > 0])

    @api.onchange('location_id', 'product_id', 'lot_id', 'package_id', 'owner_id', 'sale_order_id') #'container_id', 'shipping_order_id'
    def _onchange_location_or_product_id(self):
        vals = {}

        # Once the new line is complete, fetch the new theoretical values.
        if self.product_id and self.location_id:
            # Sanity check if a lot has been set.
            if self.lot_id:
                if self.tracking == 'none' or self.product_id != self.lot_id.product_id:
                    vals['lot_id'] = None

            quant = self._gather(
                self.product_id, self.location_id, lot_id=self.lot_id,
                package_id=self.package_id, owner_id=self.owner_id,
                # container_id= self.container_id, sale_order_id= self.sale_order_id, 
                # shipping_order_id= self.shipping_order_id, strict=True
                )
            if quant:
                self.quantity = quant.quantity

            # Special case: directly set the quantity to one for serial numbers,
            # it'll trigger `inventory_quantity` compute.
            if self.lot_id and self.tracking == 'serial':
                vals['inventory_quantity'] = 1
                vals['inventory_quantity_auto_apply'] = 1

        if vals:
            self.update(vals)