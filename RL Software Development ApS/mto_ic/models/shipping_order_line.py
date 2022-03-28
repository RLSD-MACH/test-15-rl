from datetime import datetime, timedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.osv import expression


class ShippingOrderLine(models.Model):
    
    _name = 'shipping.order.line'
    _description = 'Shipping order line'
    _order = 'create_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_default_order_id(self):
        order_id = self.env.context.get('default_order_id')
        return order_id if order_id else None

    order_id = fields.Many2one("shipping.order", string='Shipping Order', ondelete='restrict',required=True, default=_get_default_order_id)
    product_id = fields.Many2one("product.product", string='Product', ondelete='restrict', required=True)
    requested_qty = fields.Float(required=True, string='Requested', default=0, tracking=True, readonly=False)
    shipped_qty = fields.Float(required=True, string='Shipped', default=0, tracking=True, readonly=False)
    mto_order_line_id = fields.Many2one("mto.ic_order_line", string='MTO Order line', ondelete='restrict',required=False)
    mto_order_id = fields.Many2one("mto.ic_order", string='MTO Order line', ondelete='restrict', readonly=False, related='mto_order_line_id.order_id')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('underway', 'En route'),
        ('received', 'Received'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, related='order_id.state')

    active = fields.Boolean(required=True, string='Active', default=True, copy=False, related='order_id.active')
  