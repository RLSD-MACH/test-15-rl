from odoo import api, fields, models

from odoo.exceptions import AccessError, UserError, ValidationError

class StockPickingInherit(models.Model):
    
    _inherit = 'stock.picking'

    container_id = fields.Many2one('container', string='Container')
    
    def _action_done(self):
        
        self._check_company()
        
        for picking in self:
                       
            if picking.container_id:
                
                correction_data = {}
                correction_data['container_id'] = picking.container_id.id

                picking.move_lines.write(correction_data)
                picking.move_line_ids.write(correction_data)
        
        res = super(StockPickingInherit, self)._action_done()
        
        return res