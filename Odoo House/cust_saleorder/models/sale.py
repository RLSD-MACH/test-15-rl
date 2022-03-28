# -*- coding: utf-8 -*-

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def get_sale_order_line_multiline_description_sale(self, product):
        description = super(SaleOrderLine, self
                            ).get_sale_order_line_multiline_description_sale(product)
        description = product.display_name
        return description
