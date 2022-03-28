# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PaceManualStatus(models.Model):
    _inherit = 'sale.order'

    def action_manual_inv_status(self):
        if self.invoice_status=='to invoice':
            self.write({'invoice_status': 'invoiced'})
        if self.invoice_status=='no':
            self.write({'invoice_status': 'invoiced'})