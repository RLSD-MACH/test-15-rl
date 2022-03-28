from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError


class AccountMoveInherit(models.Model):
    
    _inherit = 'account.move'

    def _compute_sale_order_count(self):

        for record in self:

            orders = []

            for line in record.invoice_line_ids:

                for s_line in line.sale_line_ids:

                    if s_line.order_id not in orders:

                        orders.append(s_line.order_id)
                     
            record.sale_order_count = len(orders)

    contact_id = fields.Many2one("res.partner", string='Contact', ondelete='restrict', required=False, readonly=False, copy=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id), ('parent_id', '=', partner_id), ('type', '=','contact')]")
    sale_order_id = fields.Many2one("sale.order", string='Sales order', ondelete='restrict', required=False, readonly=True, copy=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    sale_order_count = new_field = fields.Integer(string='Sales orders', compute="_compute_sale_order_count")    

    # @api.depends('order_line.invoice_lines')
    # def _get_invoiced(self):
        # The invoice_ids are obtained thanks to the invoice lines of the SO
        # lines, and we also search for possible refunds created directly from
        # existing invoices. This is necessary since such a refund is not
        # directly linked to the SO.
        # for order in self:
        #     invoices = order.order_line.invoice_lines.move_id.filtered(lambda r: r.move_type in ('out_invoice', 'out_refund'))
        #     order.invoice_ids = invoices
        #     order.invoice_count = len(invoices)
            
    @api.onchange('partner_id')
    def _onchange_sales_invoice_incoterm_id(self):
        
        for record in self:
    
            if record.is_sale_document(include_receipts=True):

                record.update({
                    
                    'invoice_incoterm_id': record.partner_id.property_customer_incoterm_id.id if record.partner_id.property_customer_incoterm_id else False,
                    'partner_shipping_id': record.partner_id.property_default_partner_shipping_id.id if record.partner_id.property_default_partner_shipping_id else record.partner_id.id,

                })

    @api.model_create_multi

    def create(self, vals_list):
        
        res = super(AccountMoveInherit, self).create(vals_list)
        
        if len(res) == 1:
            
            # raise ValidationError("Res does not return only 1 line. I dont know what to do. Call Mads.")

            for vals in vals_list:

                if vals.get('invoice_origin', False) != False and vals.get('move_type', False) in ['out_invoice','out_refund'] and self.env['res.users'].browse(vals.get('create_uid', False)).name != "OdooBot":

                    order = self.env['sale.order'].search([['name','=',vals.get('invoice_origin', False)],['partner_id','=',vals.get('partner_id', False)]])

                    if len(order) == 1:

                        res.update({

                            'partner_bank_id': order.bank_account_id.bank_account_id.id,
                            'contact_id': order.contact_id.id,
                            'invoice_incoterm_id': order.incoterm.id

                        })
                
        return res
    