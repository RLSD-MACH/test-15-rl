# -*- coding: utf-8 -*-

from odoo import fields, models, api

class ProductSupplierinfoInherit(models.Model):
    _inherit = 'product.supplierinfo'
    
    company_id = fields.Many2one('res.company', 'Company', required=False, default=False)
    
