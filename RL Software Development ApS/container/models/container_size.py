from odoo import api, fields, models, _

class ContainerSize(models.Model):
    
    _name = 'container.size'
    _description = 'Container Size'
    _order = 'name asc'

    name = fields.Char(required=True, string='Name')
    code = fields.Char(required=True, string='Code', help='Short code for name')
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
   
