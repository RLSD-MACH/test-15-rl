from typing import DefaultDict
from odoo import api, fields, models


class SaleOrderInherit(models.Model):
    
    _inherit = 'sale.order'

    display_images = fields.Boolean(string='Display images', required=False, tracking=False, default=True)
    display_partner_shipping_id = fields.Boolean(string='Display shipping address', required=False, tracking=False, default=False)
    display_productspecifications = fields.Boolean(string='Display productspecifications', required=False, tracking=False, default=True)
    display_producttext_in_line = fields.Boolean(string='Display product text in order line', required=False, tracking=False, default=False)
    display_bomspecifications_sales_line = fields.Boolean(string='Display bomspecifications', required=False, tracking=False, default=True)
    display_bomspecifications_ps = fields.Boolean(string='Display bomspecifications', required=False, tracking=False, default=True)
    display_warehouse_message = fields.Boolean(string='Display warehouse message', required=False, tracking=False, default=True)
    display_prices = fields.Boolean(string='Display prices', required=False, tracking=False, default=True)