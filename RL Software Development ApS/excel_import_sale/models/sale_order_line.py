# -*- coding: utf-8 -*-

from odoo import api, models, _


class SaleOrderLineInherit(models.Model):

    _inherit = 'sale.order.line'

    @api.model
    def get_import_templates(self):

        return [{

            'label': _('Import Template'),
            'template': '/excel_import_sale/static/templates/import_sale_order_line.xlsx'

        }]  
    