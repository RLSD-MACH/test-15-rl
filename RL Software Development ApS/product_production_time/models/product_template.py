# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    production_time = fields.Integer(string="Production Time", default=0, required=False, tracking=True, help="Expected production time in Days.")