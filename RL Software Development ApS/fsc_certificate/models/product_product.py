# -*- coding: utf-8 -*-

from odoo import fields, models

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    fsc_claim_id = fields.Many2one('fsc.claim', related="product_tmpl_id.fsc_claim_id", readonly=False, tracking=True)
    fsc_artwork = fields.Binary(related="product_tmpl_id.fsc_artwork")
    
    

