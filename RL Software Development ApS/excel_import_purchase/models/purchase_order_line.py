# -*- coding: utf-8 -*-

from odoo import api, models, _


class PurchaseOrderLineInherit(models.Model):

    _inherit = 'purchase.order.line'

    @api.model
    def get_import_templates(self):

        return [{

            'label': _('Import Template'),
            'template': '/excel_import_purchase/static/templates/import_purchase_order_line.xlsx'

        }]  
    