# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, UserError


class StockPickingInherit(models.Model):
    
    _inherit = ['stock.picking']

    custome_delivery_address = fields.Text('Costume address', help='Custome delivery address', required=False, readonly=False)  