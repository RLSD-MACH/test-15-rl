# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime, timedelta, date

class SaleOrderInherit(models.Model):
    
    _inherit = 'sale.order'

    partner_last_vies_message_valid = fields.Boolean(related='partner_id.last_vies_message_valid', readonly=True)
    partner_last_vies_message_id = fields.Many2one("vies.message", related='partner_id.last_vies_message_id', readonly=True)

    @api.model
    def create(self, vals):

        res = super(SaleOrderInherit, self).create(vals)
        
        if 'partner_id' in vals:

            auto = self.env.company.vies_run_auto_sale_order
            days = self.env.company.vies_days_between_validations

            if auto:

                if self.partner_id.vat != False:

                    if self.partner_id.last_vies_message_id.id:

                        deadline = self.partner_id.last_vies_message_date + timedelta(days=days)

                        if date.today() > deadline.date() or self.partner_id.last_vies_message_valid == False:

                            self.partner_id.control_vat_on_vies(silent=True)

                    else:

                        self.partner_id.control_vat_on_vies(silent=True)

        return res

    def write(self, vals):

        res = super(SaleOrderInherit, self).write(vals)
        
        if 'partner_id' in vals:

            auto = self.env.company.vies_run_auto_sale_order
            days = self.env.company.vies_days_between_validations

            if auto:

                if self.partner_id.vat != False:

                    if self.partner_id.last_vies_message_id.id:

                        deadline = self.partner_id.last_vies_message_date + timedelta(days=days)

                        if date.today() > deadline.date() or self.partner_id.last_vies_message_valid == False:

                            self.partner_id.control_vat_on_vies(silent=True)

                    else:

                        self.partner_id.control_vat_on_vies(silent=True)

        return res