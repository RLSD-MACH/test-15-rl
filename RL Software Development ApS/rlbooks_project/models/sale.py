from odoo import api, fields, models


class SaleOrder(models.Model):
    
    _inherit = 'sale.order'

    rlbooks_project_id = fields.Many2one("rlbooks.project.project", string='Project', ondelete='restrict', required=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
