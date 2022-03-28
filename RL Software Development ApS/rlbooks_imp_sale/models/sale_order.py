
from odoo import api, fields, models

class SaleOrderInherit(models.Model):
    
    _inherit = 'sale.order'

    finished = fields.Boolean(string='Finished', compute='_compute_open_salesvalue', readonly=False, store=True, copy=False, required=False, tracking=True, default=False, compute_sudo=True)

    contact_id = fields.Many2one("res.partner", string='Contact', ondelete='restrict', required=False, readonly=False, copy=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id), ('parent_id', '=', partner_id), ('type', '=','contact')]")
    
    client_order_ref = fields.Char(string='Customer ref.', tracking=True)

    show_delivery_address = fields.Boolean(string='Show delivery address', default=False)

    bank_account_id = fields.Many2one('account.journal', 
        string='Bank Account',
        help="", 
        required=False, 
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    open_salesvalue = fields.Float(compute='_compute_open_salesvalue', string='Open salesvalue', store=True, readonly=True, compute_sudo=True)
    open_salesvalue_DKK = fields.Float(compute='_compute_open_salesvalue', string='Open salesvalue DKK', store=True, readonly=True, compute_sudo=True)
    open_salesvalue_base = fields.Float(compute='_compute_open_salesvalue', string='Open salesvalue Base', store=True, readonly=True, compute_sudo=True)
    salesvalue_DKK = fields.Float(compute='_compute_open_salesvalue', string='Salesvalue DKK', store=True, readonly=True, compute_sudo=True)
    salesvalue_base = fields.Float(compute='_compute_open_salesvalue', string='Salesvalue Base', store=True, readonly=True, compute_sudo=True)

    def init(self): 

        self._recalculate_open_salesvalue()
    
    def _prepare_invoice(self):

        res = super(SaleOrderInherit,self)._prepare_invoice()

        res['sale_order_id'] = self.id

        return res

    @api.onchange('partner_id')
    def onchange_partner_id(self):
            
        for record in self:

            orig_result = super(SaleOrderInherit,record).onchange_partner_id()

            if record.partner_id:

                partner = record.partner_id
    
                record.update({
                    
                    'incoterm': partner.property_customer_incoterm_id.id,
                    'payment_term_id': partner.property_payment_term_id.id if partner.property_payment_term_id.id else None,
                    'bank_account_id': partner.property_default_bank_account_id.id,
                    'partner_invoice_id': partner.property_default_partner_invoice_id.id if partner.property_default_partner_invoice_id.id else partner.id,
                    'partner_shipping_id': partner.property_default_partner_shipping_id.id if partner.property_default_partner_shipping_id.id else partner.id,
                    'contact_id':partner.contact_id.id,
                    
                })
    
    @api.depends('state', 'order_line')
    def _compute_open_salesvalue(self):

        self._recalculate_open_salesvalue()

    def _recalculate_open_salesvalue(self): 
        
        for record in self:

            finished = False

            if record.state == 'draft' or record.state == 'sent':
            
                finished = False
            
            elif record.state == 'cancel':
            
                finished = True
            
            else:
            
                finished = True
            
                for line in record.order_line:
                    
                    if line.product_type != 'service':
                        
                        if line.product_id.invoice_policy == 'order':

                            if line.qty_to_deliver != 0 or line.qty_to_invoice !=0:
                            
                                finished = False

                        else:

                            if line.qty_to_deliver > 0 or line.qty_to_invoice !=0:
                            
                                finished = False

                    
                    else:

                        if line.qty_to_invoice !=0:
                        
                            finished = False
    
            open_salesvalue = 0
            open_salesvalue_base = 0
            open_salesvalue_DKK = 0
            salesvalue_DKK = 0
            salesvalue_base = 0

            if record.state not in ['draft','sent','cancel']:
            
                open_salesvalue = sum(l.open_salesvalue for l in record.order_line)
                open_salesvalue_base = sum(l.open_salesvalue_base for l in record.order_line)
                open_salesvalue_DKK = sum(l.open_salesvalue_DKK for l in record.order_line)
                salesvalue_DKK = sum(l.salesvalue_DKK for l in record.order_line)
                salesvalue_base = sum(l.salesvalue_base for l in record.order_line)
                
            record.update({
                
                'finished': finished,
                'open_salesvalue': open_salesvalue,
                'open_salesvalue_base': open_salesvalue_base,
                'open_salesvalue_DKK': open_salesvalue_DKK,
                'salesvalue_DKK': salesvalue_DKK,
                'salesvalue_base': salesvalue_base

            })
            
    def action_recalculate_open_salesvalue(self):

        self._recalculate_open_salesvalue()