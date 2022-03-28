from datetime import datetime, timedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.osv import expression

class ContainerStock(models.Model):
    
    _name = 'container.stock'
    _description = 'Container Stock'
    _order = 'name asc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_default_container_id(self):
        container_id = self.env.context.get('default_container_id')
        return container_id if container_id else None

    name = fields.Char(required=False, string='Name')
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
