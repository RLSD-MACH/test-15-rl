# -*- coding: utf-8 -*-

from odoo import fields, models, api

class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'
    
    detailed_type = fields.Selection(default='product')
