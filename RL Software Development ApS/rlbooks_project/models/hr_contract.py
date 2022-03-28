from odoo import api, fields, models

class Contract(models.Model):

    _name = 'hr.contract'
    _inherit = 'hr.contract'

    invoiceable_hourrate = fields.Float(string="Salesprice/hourrate",required=True, tracking=True)
    standard_costprice_hourrate = fields.Float(string="Standard costprice/hourrate",required=True, help="This costprice is the shown costprice. It is useally more round in the numbers, so other employees cant estimate an employees salary.")
    real_costprice_hourrate = fields.Float(string="Real costprice/hourrate",required=True, help="This should be the total costprice per hour of work, based on expected workhours in a calendar year.")
    product_id = fields.Many2one("product.product", string='Product', ondelete='restrict', required=False, domain="[('type', '=', 'service'),'|', ('company_id', '=', False), ('company_id', '=', company_id)]")