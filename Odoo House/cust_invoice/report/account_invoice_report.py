# -*- coding: utf-8 -*-

from odoo import api, models


class ReportInvoiceWithPayment(models.AbstractModel):
    _inherit = 'report.account.report_invoice_with_payments'

    @api.model
    def _get_report_values(self, docids, data=None):
        rslt = super()._get_report_values(docids, data)
        if rslt.get('docs'):
            rec = rslt.get('docs')
            order = self.env['sale.order'].search([('name', '=', rec.invoice_origin)], limit=1)
            note_list = []
            if order:
                stock_piking_rec = self.env['stock.picking'].search([('sale_id', '=', order.id)])
                for delivery_note_rec in stock_piking_rec.filtered(lambda stock_piking_rec: stock_piking_rec.state  in ['done']):
                    if delivery_note_rec.name:
                        note_list.append(delivery_note_rec.name)
        delivery_note = ','.join(note_list)
        rslt['delivery_note'] = delivery_note or ''
        return rslt
