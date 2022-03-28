from odoo import api, fields, models


class Magento2Store(models.Model):
    
    _name = 'magento2.store'
    _description = 'Magento2 Store'
    _order = 'id'
    _check_company_auto = True

    name = fields.Char(required=False,string='Name')
    store_code = fields.Char(required=False,string='Store Code') 
    pricelist_id  = fields.Many2one('product.pricelist', 'Pricelist', required=False)
    active = fields.Boolean(required=True, string='Active', default=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
   