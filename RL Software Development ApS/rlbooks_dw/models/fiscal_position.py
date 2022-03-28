
from odoo import api, fields, models


class FiscalPositionInherit(models.Model):
    
    _inherit = 'account.fiscal.position'

    default_warehouse_id = fields.Many2one("stock.warehouse", string='Default warehouse', ondelete='restrict', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", required=False)
    default_customer_location_id = fields.Many2one("stock.location", string='Default customer location', ondelete='restrict', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", required=False)
    default_supplier_location_id = fields.Many2one("stock.location", string='Default supplier location', ondelete='restrict', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", required=False)
    