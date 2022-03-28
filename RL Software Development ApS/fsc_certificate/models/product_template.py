# -*- coding: utf-8 -*-

from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    fsc_claim_id = fields.Many2one('fsc.claim', string='FSC Claim', required=True, tracking=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    fsc_artwork = fields.Binary("Artwork")

