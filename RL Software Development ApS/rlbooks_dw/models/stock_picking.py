from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError

class StockPickingInherit(models.Model):
    
    _inherit = 'stock.picking'

    def _compute_original_transfer_count(self):

        model = self.env['stock.picking']
        for record in self:
            record._compute_original_transfer_count = model.search_count([('original_transfer_id','=', record.id)])

    dw_moves = fields.One2many('stock.picking', 'original_transfer_id', string='DW Moves')
    original_transfer_id = fields.Many2one('stock.picking', string='Original transfer')
    original_transfer_stock_picking_count = fields.Integer(string="Original transfer count", compute="_compute_original_transfer_count")