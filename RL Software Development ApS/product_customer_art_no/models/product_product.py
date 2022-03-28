# -*- coding: utf-8 -*-

from odoo import fields, models

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    customer_art_no = fields.Char(related="product_tmpl_id.customer_art_no", readonly=False, tracking=True)
    

