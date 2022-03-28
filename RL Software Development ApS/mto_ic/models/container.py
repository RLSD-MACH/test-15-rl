from datetime import datetime, timedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.osv import expression
from .shipping_order import TRANSPORT_TYPE_SELECTION

class Container(models.Model):
    
    _name = 'container'
    _description = 'Container'
    _order = 'name desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True,string='No.', readonly=True, states={'draft': [('readonly', True)]}, index=True, default=lambda self: _('New'), copy=False)
    container = fields.Char(string='Container no.', tracking=True, required=False, copy=False)
    container_size_id = fields.Many2one('container.size', string='Size', copy=True)
    container_manual_size = fields.Boolean(string='Manual Size', default=False)

    manual_capacity_cubic_meter = fields.Float(string="Capacity Cubic Meter (Manual)")
    capacity_cubic_meter = fields.Float(related='container_size_id.capacity_cubic_meter', string="Capacity Cubic Meter")
    capacity_cubic_meter_total = fields.Float(string="Capacity in CBM Total", required=False, readonly=True, compute="_compute_capacity_cubic_meter_total")
    remaining_capacity_cubic_meter = fields.Float(compute="_compute_remaining_capacity_cubic_meter", string="Free CBM")

    capacity_kg = fields.Float(related='container_size_id.capacity_kg', string="Capacity in Kg")
    manual_capacity_kg = fields.Float(string="Capacity in Kg (Manual)")
    capacity_kg_total = fields.Float(string="Capacity in Kg Total", required=False, readonly=True, compute="_compute_capacity_kg_total")
    
    weight_kg_total = fields.Float(string="Weight kg", required=False, readonly=True, compute="_compute_weight_kg_total")
    remaining_capacity_kg = fields.Float(compute="_compute_remaining_capacity_kg", string="Free Kg")

    # planning_line_ids = fields.One2many('container.stock', 'container_id', string='Stock')

    move_ids = fields.One2many('stock.move', 'container_id', string='Stock Moves')

    stock_ids = fields.One2many('container.stock', 'container_id', string='Stock')
    
    line_ids = fields.One2many('stock.quant', 'container_id', 'Order lines')

    volume_cubic_meter_total = fields.Float(string="Cubic Meter", required=False, readonly=True, compute="_compute_volume_cubic_meter_total")
    
    note = fields.Text(string="Note")
    
    # state = fields.Selection([
    #     ('draft', 'Draft'),
    #     ('underway', 'En route'),
    #     ('received', 'Received'),
    #     ('cancel', 'Cancelled'),
    #     ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    state = fields.Selection(TRANSPORT_TYPE_SELECTION, related="shipping_order_id.state")
    shipping_order_id = fields.Many2one('shipping.order', string='Shipping order')
    current_location_id = fields.Many2one("res.partner", string='Current Place', ondelete='restrict', required=False)
    current_stock_location_id = fields.Many2one("stock.location", string='Current Stock Location', ondelete='restrict', required=False, domain="[('usage', '=', 'internal')]")
    current_port_id = fields.Many2one('res.port', string='Current Port', ondelete='restrict')

    active = fields.Boolean(required=True, string='Active', default=True, copy=False)
  
    @api.model    
    def create (self, vals):

        next_seq = self.env['ir.sequence'].next_by_code('container.sequence')

        if next_seq != False:

            vals['name'] = next_seq

        res = super(Container, self).create(vals)

        return res

    @api.depends('stock_ids.volume_cubic_meter_total')
    def _compute_volume_cubic_meter_total(self):
        
        for record in self:
        
            if record.stock_ids:

                record.volume_cubic_meter_total = sum(l.volume_cubic_meter_total for l in record.stock_ids)
            
            else:

                record.volume_cubic_meter_total = 0
    
    @api.depends('stock_ids.weight_kg_total')
    def _compute_weight_kg_total(self):
        
        for record in self:
        
            if record.stock_ids:

                record.weight_kg_total = sum(l.weight_kg_total for l in record.stock_ids)
            
            else:

                record.weight_kg_total = 0

    @api.depends('volume_cubic_meter_total', 'capacity_cubic_meter_total')
    def _compute_remaining_capacity_cubic_meter(self):
        
        for record in self:
                    
            record.remaining_capacity_cubic_meter = record.capacity_cubic_meter_total - record.volume_cubic_meter_total

    @api.depends('capacity_cubic_meter', 'manual_capacity_cubic_meter')
    def _compute_capacity_cubic_meter_total(self):
        
        for record in self:
                    
            record.capacity_cubic_meter_total = record.capacity_cubic_meter + record.manual_capacity_cubic_meter

    @api.depends('capacity_kg', 'manual_capacity_kg')
    def _compute_capacity_kg_total(self):
        
        for record in self:
                    
            record.capacity_kg_total = record.capacity_kg + record.manual_capacity_kg

    @api.depends('weight_kg_total', 'capacity_kg_total')
    def _compute_remaining_capacity_kg(self):
        
        for record in self:
                    
            record.remaining_capacity_kg = record.capacity_kg_total - record.weight_kg_total

    @api.depends(lambda self: (self._rec_name,) if self._rec_name else ())
    def _compute_display_name(self):

        names = dict(self.name_get())
        for record in self:

            if record.container != False and record.container != '':

                calc_name =  names.get(record.id, '') + " [" + record.container + "]"
            
            else:

                calc_name = names.get(record.id, False)
                       
            record.display_name = calc_name


class ContainerSize(models.Model):
    
    _name = 'container.size'
    _description = 'Container Size'
    _order = 'name asc'

    name = fields.Char(required=True, string='Name')
    length = fields.Float(string="Length cm", required=True, default="0")
    width = fields.Float(string="Width cm", required=True, default="0")
    height = fields.Float(string="Height cm", required=True, default="0")
    capacity_cubic_meter = fields.Float(string="Capacity CBM", required=False, readonly=True, compute="_compute_capacity_cubic_meter")
    capacity_kg = fields.Float(string="Capacity kg", required=True, readonly=False,default="0")

    active = fields.Boolean(required=True, string='Active', default=True, copy=False)
  
    @api.depends('length', 'width', 'height')
    def _compute_capacity_cubic_meter(self):
        
        for record in self:
        
            record.capacity_cubic_meter = record.length * record.width * record.height / 1000000
   

class ContainerStock(models.Model):
    
    _name = 'container.stock'
    _description = 'Container Stock'
    _order = 'name asc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_default_order_id(self):
        order_id = self.env.context.get('default_order_id')
        return order_id if order_id else None

    def _get_default_container_id(self):
        container_id = self.env.context.get('default_container_id')
        return container_id if container_id else None

    name = fields.Char(required=False, string='Name')
    order_id = fields.Many2one("mto.ic_order", string='Order', ondelete='restrict', required=True, default=_get_default_order_id, copy=True)
    container_id = fields.Many2one("container", string='Container', ondelete='restrict', required=True, default=_get_default_container_id, copy=True)
    state = fields.Selection(related='container_id.state')

    product_id = fields.Many2one("product.product", string='Product', ondelete='restrict', required=True, readonly=True, states={'draft': [('readonly', False)]}, domain="[('type', 'in', ['product'])]", copy=True)
    packs = fields.Float(required=True, string='Packs', default=0, tracking=True, readonly=True, states={'draft': [('readonly', False)]}, copy=True)
    pack_qty = fields.Float(required=True, string='Pack Qty', default=0, tracking=True, readonly=True, states={'draft': [('readonly', False)]}, copy=True)
    qty = fields.Float(string='Quantity', default=0, compute="_compute_qty")
    volume_cubic_meter_unit = fields.Float(string="Volume/unit", readonly=True, states={'draft': [('readonly', False)]}, copy=True)
    volume_cubic_meter_total = fields.Float(string="Cubic Meter", required=False, readonly=True, compute="_compute_volume_cubic_meter_total")

    weight_kg_unit = fields.Float(string="Kg/unit", readonly=True, states={'draft': [('readonly', False)]}, copy=True)
    weight_kg_total = fields.Float(string="Weight kg", required=False, readonly=True, compute="_compute_weight_kg_total")
    
    active = fields.Boolean(required=True, string='Active', default=True, copy=False)
    note = fields.Char(string="Note", copy=True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        
        for record in self:
            
            if record.product_id:

                record.update({
                    
                    'volume_cubic_meter_unit': record.product_id.volume,
                    'weight_kg_unit': record.product_id.weight,

                })  
                
    @api.depends('packs', 'pack_qty')
    def _compute_qty(self):
        
        for record in self:
        
            record.qty = record.packs * record.pack_qty
            
    @api.depends('qty', 'volume_cubic_meter_unit')
    def _compute_volume_cubic_meter_total(self):
        
        for record in self:
        
            record.volume_cubic_meter_total = record.qty * record.volume_cubic_meter_unit

    @api.depends('qty', 'weight_kg_unit')
    def _compute_weight_kg_total(self):
        
        for record in self:
        
            record.weight_kg_total = record.qty * record.weight_kg_unit

  
   