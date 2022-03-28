from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_rlbooks_imp_sale_dashboards = fields.Boolean("Add Dashboards from Improved Sale")

class ResCompany(models.Model):
    _inherit = 'res.company'

    salesvalue_no_openvalue_ids = fields.Many2many("salesvalue.no.openvalue", string='Revenue counted as ours', required=False, domain="['|', ('company_id', '=', False), ('company_id', '=', id)]")
    
    @api.onchange('salesvalue_no_openvalue_ids')
    def _onchange_salesvalue_no_openvalue_ids(self):
        
        self.env['sale.order.line']._recalculate_all_open_salesvalue()
        
class SalesvalueNoOpenvalue(models.Model):

    _name = 'salesvalue.no.openvalue'
    _description = 'Our Salesvalue'
    _check_company_auto = True

    name = fields.Char(related='account_fiscal_position_id.name')
    account_fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Positions')
    consumable = fields.Boolean(string='Consumable', default=False)
    service = fields.Boolean(string='Service', default=False)
    storable_product = fields.Boolean(string='Storable Product', default=False)
    
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
