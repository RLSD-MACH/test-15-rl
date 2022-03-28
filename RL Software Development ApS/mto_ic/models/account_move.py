from odoo import api, fields, models


class AccountMoveInherit(models.Model):
    
    _inherit = 'account.move'

    sale_order_id = fields.Many2one("sale.order", string='Sales order', ondelete='restrict',required=False)
