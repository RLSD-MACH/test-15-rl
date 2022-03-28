from odoo import _, api, fields, models

class StockQuantInherit(models.Model):
    
    _inherit = 'stock.quant'

    container_id = fields.Many2one('container', string='Container')   