# -*- encoding: utf-8 -*-

from odoo import models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_purchase_order(self, company_id, origins, values):
        res = super(StockRule, self)._prepare_purchase_order(company_id, origins, values)
        cust_sale_order_id = self._context.get('cust_sale_order_id')
        if cust_sale_order_id:
            res['cust_sale_order_id'] = cust_sale_order_id[0]
        return res
