# -*- coding: utf-8 -*-

from odoo import api, models, _


class StockMoveInherit(models.Model):

    _inherit = 'stock.move'

    @api.model
    def get_import_templates(self):

        return [{

            'label': _('Import Template'),
            'template': '/excel_import_stock_move/static/templates/import_stock_move.xlsx'

        }]  
    