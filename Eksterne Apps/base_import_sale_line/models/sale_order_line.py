# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright Domiup (<http://domiup.com>).
#
##############################################################################

from odoo import api, models, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Sale Order Line'),
            'template': '/base_import_sale_line/static/import_template.xlsx'
        }]
