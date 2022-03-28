from odoo import api, fields, models


class MtoIcOrderLine(models.Model):
    
    _name = 'mto.ic_order_line'
    _description = 'MTO IC order line'
    _order = 'create_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_default_order_id(self):
        order_id = self.env.context.get('default_order_id')
        return order_id if order_id else None

    def _compute_requested_from_supplier_qty(self):

        for order_line in self:

            lines = order_line.purchase_order_line_ids.filtered(lambda p: p.state != 'cancel')

            if  lines:

                sum = 0

                for line in lines:

                    sum += line.product_uom_qty

                order_line.requested_from_supplier_qty = sum
            
            else:

                order_line.requested_from_supplier_qty = 0
    
    order_id = fields.Many2one("mto.ic_order", string='Order', ondelete='restrict',required=True,default=_get_default_order_id)
    product_id = fields.Many2one("product.product", string='Product', ondelete='restrict', required=True)
    requested_qty = fields.Float(required=True, string='Requested', default=0, tracking=True, readonly=False)
    on_sale_order_qty = fields.Float(required=True, string='On SO\'s', default=0, tracking=True, readonly=True)
    to_sale_order_qty = fields.Float(required=True, string='To put on SO', default=0, tracking=True, readonly=True, compute='_compute_to_put_on_so', store=True)
    sale_price = fields.Float(required=True, string='Price', default=0, tracking=True, readonly=False)
    delivered_qty = fields.Float(required=True, string='Delivered', default=0, tracking=True, readonly=True)
    invoiced_qty = fields.Float(required=True, string='Invoiced', default=0, tracking=True, readonly=True)
    to_invoice_qty = fields.Float(required=True, string='To invoice', default=0, tracking=True, readonly=True, compute='_compute_to_invoice', store=True)
    on_stock_seller_qty = fields.Float(required=True, string='At seller', default=0, tracking=True, readonly=True, help="On stock at seller's warehouse")
    in_transfer_ic_qty = fields.Float(required=True, string='IC trans', default=0, tracking=True, readonly=True, help="Is in process in an IC transfer")
    on_stock_purchaser_qty = fields.Float(required=True, string='At purchaser', default=0, tracking=True, readonly=True, help="On stock at purchaser's warehouse")
    requested_from_supplier_qty = fields.Float(required=False, string='RFQ supplier',tracking=True, readonly=True, help="Requested from supplier", compute="_compute_requested_from_supplier_qty", default=0)
    purchase_order_line_ids = fields.One2many('purchase.order.line', 'mto_ic_order_line_id', 'Purchase order lines', required=False)
    to_request_from_supplier_qty = fields.Float(string='To RFQ from supplier', readonly=True, compute='_compute_to_put_on_po')
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('confirmed', 'Confirmed'),
        ('cancel', 'Cancelled'),
        ('done', 'Done')
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    active = fields.Boolean(required=True, string='Active', default=True, copy=False)

    @api.depends('delivered_qty', 'invoiced_qty')
    def _compute_to_invoice(self):

        for line in self:

            line.to_invoice_qty = line.delivered_qty + line.invoiced_qty

    @api.depends('requested_qty', 'on_sale_order_qty')
    def _compute_to_put_on_so(self):

        for line in self:

            line.to_sale_order_qty = line.requested_qty - line.on_sale_order_qty

    @api.depends('requested_qty', 'requested_from_supplier_qty')
    def _compute_to_put_on_po(self):

        for line in self:

            line.to_request_from_supplier_qty = line.requested_qty - line.requested_from_supplier_qty

            