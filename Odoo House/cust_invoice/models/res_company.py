# -*- coding: utf-8 -*-

from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    invoice_text = fields.Text('Invoice Text', translate=True)
    order_text = fields.Text('Quotation/Order Text', translate=True)
