# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime, timedelta, date

class AccountMoveInherit(models.Model):
    
    _inherit = 'account.move'

    partner_last_cvr_message_valid = fields.Boolean(related='partner_id.last_cvr_message_valid', readonly=True)
    partner_last_cvr_message_id = fields.Many2one("cvr.message", related='partner_id.last_cvr_message_id', readonly=True)

    @api.model
    def create(self, vals):

        res = super(AccountMoveInherit, self).create(vals)
        
        if self.move_type in ['out_invoice','out_refund']:

            if 'partner_id' in vals:

                auto = self.env.company.cvr_run_auto_sales_invoice
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

    def write(self, data):

        res = super(AccountMoveInherit, self).write(data)
        
        for record in self:

            if record.move_type in ['out_invoice','out_refund']:

                if 'partner_id' in data:

                    auto = self.env.company.cvr_run_auto_sales_invoice
                    days = self.env.company.cvr_days_between_validations
        
                    if auto:

                        if record.partner_id.vat != False:

                            if record.partner_id.last_cvr_message_id.id:

                                deadline = record.partner_id.last_cvr_message_date + timedelta(days=days)

                                if date.today() > deadline.date() or record.partner_id.last_cvr_message_valid == False:

                                    record.partner_id.control_vat_on_cvr(silent=True)

                            else:

                                record.partner_id.control_vat_on_cvr(silent=True)

        return res