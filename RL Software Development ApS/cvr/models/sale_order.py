# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime, timedelta, date

class SaleOrderInherit(models.Model):
    
    _inherit = 'sale.order'

    partner_last_cvr_message_valid = fields.Boolean(related='partner_id.last_cvr_message_valid', readonly=True)
    partner_last_cvr_message_id = fields.Many2one("cvr.message", related='partner_id.last_cvr_message_id', readonly=True)

    @api.model
    def create(self, vals):

        res = super(SaleOrderInherit, self).create(vals)
        
        if 'partner_id' in vals:

            auto = self.env.company.cvr_run_auto_sale_order
            days = self.env.company.cvr_days_between_validations

            if auto:

                if self.partner_id.vat != False:

                    if self.partner_id.last_cvr_message_id.id:

                        deadline = self.partner_id.last_cvr_message_date + timedelta(days=days)

                        if date.today() > deadline.date() or self.partner_id.last_cvr_message_valid == False:

                            self.partner_id.control_vat_on_cvr(silent=True)

                    else:

                        self.partner_id.control_vat_on_cvr(silent=True)

        return res

    def write(self, vals):

        res = super(SaleOrderInherit, self).write(vals)
        
        if 'partner_id' in vals:

            auto = self.env.company.cvr_run_auto_sale_order
            days = self.env.company.cvr_days_between_validations

            if auto:

                if self.partner_id.vat != False:

                    if self.partner_id.last_cvr_message_id.id:

                        deadline = self.partner_id.last_cvr_message_date + timedelta(days=days)

                        if date.today() > deadline.date() or self.partner_id.last_cvr_message_valid == False:

                            self.partner_id.control_vat_on_cvr(silent=True)

                    else:

                        self.partner_id.control_vat_on_cvr(silent=True)

        return res