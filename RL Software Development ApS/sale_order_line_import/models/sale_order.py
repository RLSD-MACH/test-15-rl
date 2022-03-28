# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import ValidationError, UserError

class SaleOrderLineInherit(models.Model):

    _inherit = 'sale.order'
    
    def _compute_reminder_count(self):

        list = self.env['sale.order.line.import']

        for record in self:

            record.line_import_count = list.search_count([('order_id','=', record.id)])

    line_import_count = fields.Integer(compute='_compute_line_import_count', string="Import Lines Count")
       