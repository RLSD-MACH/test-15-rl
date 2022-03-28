# -*- coding: utf-8 -*-

from odoo import fields, models

class PartnerInherit(models.Model):
    
    _inherit = "res.partner"

    fsc_certificate_ids = fields.One2many('fsc.certificate','partner_id', string='FSC Certificates', required=False, domain="['&','|', ('company_id', '=', False), ('company_id', '=', company_id),'|',('partner_id', '=', False), ('partner_id', '=', id)]")

