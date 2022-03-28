# -*- coding: utf-8 -*-

from odoo import fields, models

class CompanyInherit(models.Model):
    
    _inherit = "res.company"

    fsc_certificate_id = fields.Many2one('fsc.certificate', string='FSC Certificate', required=False, domain="['&',('partner_id', '=', partner_id),'|', ('company_id', '=', False), ('company_id', '=', id)]")
