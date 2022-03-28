# -*- coding: utf-8 -*-

from odoo import models


class ProductCategory(models.Model):
    _name = 'product.category'
    _inherit = ['product.category', 'base.dyn.name.generator']
