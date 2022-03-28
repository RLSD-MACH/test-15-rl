from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError

class SaleOrderLineInherit(models.Model):
    
    _inherit = 'sale.order.line'

    qty_to_deliver = fields.Float(store=True, default=0)
    order_delivery_date = fields.Datetime(string='Delivery Date', readonly=True, related='order_id.commitment_date', store=True)    
    open_salesvalue = fields.Float(compute='_compute_open_salesvalue', string='Open salesvalue', store=True, readonly=True)
    open_salesvalue_DKK = fields.Float(compute='_compute_open_salesvalue', string='Open salesvalue DKK', store=True, readonly=True)
    open_salesvalue_base = fields.Float(compute='_compute_open_salesvalue', string='Open salesvalue Base', store=True, readonly=True)
    salesvalue_DKK = fields.Float(compute='_compute_open_salesvalue', string='Salesvalue DKK', store=True, readonly=True)
    salesvalue_base = fields.Float(compute='_compute_open_salesvalue', string='Salesvalue Base', store=True, readonly=True)
    date_order = fields.Datetime(related="order_id.date_order",store=True, readonly=True, string='Order Date', help="Creation date of draft/sent orders, Confirmation date of confirmed orders.")
  
    def init(self): 

        self._recalculate_open_salesvalue()

    @api.depends('product_uom_qty', 'qty_invoiced', 'price_subtotal','state')
    def _compute_open_salesvalue(self):
        
        self._recalculate_open_salesvalue()

    def _recalculate_all_open_salesvalue(self):
        
        self.env['sale.order.line']._recalculate_open_salesvalue()
    
    def _recalculate_open_salesvalue(self): 
        
        DKK_rate = self.env['res.currency'].search([('name', '=', 'DKK')]).rate

        if len(self) == 0:

            records = self.env['sale.order.line'].search([])

        else:

            records = self
                        
        for record in records:

            ours = True
            settings = False

            salesvalue_no_openvalue_ids = record.company_id.salesvalue_no_openvalue_ids

            if salesvalue_no_openvalue_ids.ids:

                for l in salesvalue_no_openvalue_ids:

                    if l.account_fiscal_position_id.id == record.order_id.fiscal_position_id.id:

                        settings = l
                            
                if settings:
                    
                    if record.product_type == "consu":

                        ours = settings.consumable
                        
                    elif record.product_type == "service":

                        ours = settings.service

                    elif record.product_type == "product":
                        
                        ours = settings.storable_product                        
                                
            if ours == False:

                record.update({

                    'salesvalue_base': 0,
                    'salesvalue_DKK': 0,
                    'open_salesvalue': 0,
                    'open_salesvalue_base': 0,
                    'open_salesvalue_DKK': 0,

                })

            else:

                if  record.product_uom_qty != 0 and record.state not in ['draft','sent','cancel'] :
                                        
                    sales_val = (record.product_uom_qty - record.qty_invoiced) / record.product_uom_qty * record.price_subtotal
                    
                    if sales_val < 0:

                        sales_val  = 0

                    record.update({
                        
                        'salesvalue_base': record.price_subtotal / record.currency_id.rate,
                        'salesvalue_DKK': record.price_subtotal / record.currency_id.rate * DKK_rate,
                        'open_salesvalue': sales_val,
                        'open_salesvalue_base': sales_val / record.currency_id.rate,
                        'open_salesvalue_DKK': sales_val / record.currency_id.rate * DKK_rate

                    })
                
                else:
                    
                    record.update({
                        
                        'salesvalue_base': 0,
                        'salesvalue_DKK': 0,
                        'open_salesvalue': 0,
                        'open_salesvalue_base': 0,
                        'open_salesvalue_DKK': 0,

                    })


   