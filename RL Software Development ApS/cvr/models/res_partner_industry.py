# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

class ResPartnerIndustryInherit(models.Model):
    
    _inherit = 'res.partner.industry'
    
    code_on_cvr = fields.Char(string='Code on CVR')
    