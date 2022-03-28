from odoo import api, fields, models
from odoo import _, api, fields, models

class StockMoveInherit(models.Model):
    
    _inherit = 'stock.move'

    container_id = fields.Many2one('container', string='Container')
    
    @api.model
    def _prepare_merge_moves_distinct_fields(self):

        res = super(StockMoveInherit, self)._prepare_merge_moves_distinct_fields()

        res.append('container_id')

        return res   
   
class StockMoveLineInherit(models.Model):
    
    _inherit = 'stock.move.line'

    container_id = fields.Many2one('container', string='Container')