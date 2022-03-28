from odoo import api, fields, models


class PurchaseOrderLineInherit(models.Model):
    
    _inherit = 'purchase.order.line'

    mto_ic_order_line_id = fields.Many2one("mto.ic_order_line", string='MTO IC Order Line', ondelete='set null',required=False)
