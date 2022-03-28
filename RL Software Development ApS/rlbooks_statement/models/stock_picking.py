from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError

class StockPickingInherit(models.Model):
    
    _inherit = 'stock.picking'

    display_backorder = fields.Boolean(string='Display backorder', required=False, tracking=False, default=False)
