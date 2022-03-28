# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange('partner_id')
    def onchange_partner_id(self):

        res = super(SaleOrder, self).onchange_partner_id()
        
        if self.partner_id.property_account_position_id.default_warehouse_id:
            
            self.warehouse_id = self.partner_id.property_account_position_id.default_warehouse_id.id
                
        return res
