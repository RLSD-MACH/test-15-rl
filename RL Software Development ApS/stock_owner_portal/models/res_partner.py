# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, UserError


class ResPartnerInherit(models.Model):
    
    _inherit = ['res.partner']
        
    portal_access_to_stock_from_ids = fields.Many2many(comodel_name='res.partner', relation="track_access_to_stock_rel", column1='user_id', column2='res_partner_id', store=True, string='Portal access to see stock for Partners')