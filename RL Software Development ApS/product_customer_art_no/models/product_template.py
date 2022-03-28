# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    customer_art_no = fields.Char(string="Customer art no", tracking=True)