from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError

class StockWarehouseInherit(models.Model):
    
    _inherit = 'stock.warehouse'

    text_on_invoices = fields.Text('Text on invoices',help='')
    text_placement = fields.Selection(string='Text placement', selection=[('top', 'Top'), ('bottom', 'Bottom'),])    
    text_on_purchase_orders = fields.Text('Text on purchase orders',help='')