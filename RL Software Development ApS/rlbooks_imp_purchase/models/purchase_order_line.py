from odoo import api, fields, models

class PurchaseOrderLineInherit(models.Model):
        
    _name = "purchase.order.line"
    _inherit = ['purchase.order.line', 'mail.thread']
    _description = "Puchase order line"
    
    qty_to_receive = fields.Float(string='To Recieve Qty',
        compute='_compute_qty_to_receive', readonly=True, store=True, copy=False, required=False, tracking=False, compute_sudo=True)

    open_purchasevalue = fields.Float(compute='_compute_open_purchasevalue', string='Open purchasevalue', store=True, readonly=True, compute_sudo=True)
    open_purchasevalue_DKK = fields.Float(compute='_compute_open_purchasevalue', string='Open purchasevalue DKK', store=True, readonly=True, compute_sudo=True)
    open_purchasevalue_base = fields.Float(compute='_compute_open_purchasevalue', string='Open purchasevalue Base', store=True, readonly=True, compute_sudo=True)
    purchasevalue_DKK = fields.Float(compute='_compute_open_purchasevalue', string='Purchasevalue DKK', store=True, readonly=True, compute_sudo=True)
    purchasevalue_base = fields.Float(compute='_compute_open_purchasevalue', string='Purchasevalue Base', store=True, readonly=True, compute_sudo=True)

    product_template_id = fields.Many2one('product.template', string="Product Template", readonly=True, related="product_id.product_tmpl_id", required=False)
    
    def init(self): 

        for record in self:
    
            record.update({
                
                'qty_to_receive': record.product_qty - record.qty_received

            })

        self._recalculate_open_purchasvalue()

    @api.depends('product_qty', 'qty_received', 'qty_received_manual')
    def _compute_qty_to_receive(self):
        
        for record in self:
    
            record.update({
                
                'qty_to_receive': record.product_qty - record.qty_received
            })   

    @api.depends('product_qty', 'qty_invoiced','state')
    def _compute_open_purchasevalue(self):
        
        self._recalculate_open_purchasvalue()

    def _recalculate_all_open_purchasevalue(self):
        
        self.env['purchase.order.line']._recalculate_open_purchasvalue()
    
    def _recalculate_open_purchasvalue(self): 
        
        DKK_rate = self.env['res.currency'].search([('name', '=', 'DKK')]).rate

        if len(self) == 0:

            records = self.env['purchase.order.line'].search([])

        else:

            records = self
                        
        for record in records:

            ours = True
            # settings = False

            # salesvalue_no_openvalue_ids = record.company_id.salesvalue_no_openvalue_ids

            # if salesvalue_no_openvalue_ids.ids:

            #     for l in salesvalue_no_openvalue_ids:

            #         if l.account_fiscal_position_id.id == record.order_id.fiscal_position_id.id:

            #             settings = l
                            
            #     if settings:
                    
            #         if record.product_type == "consu":

            #             ours = settings.consumable
                        
            #         elif record.product_type == "service":

            #             ours = settings.service

            #         elif record.product_type == "product":
                        
            #             ours = settings.storable_product                        
                                
            if ours == False:

                record.update({

                    'purchasevalue_base': 0,
                    'purchasevalue_DKK': 0,
                    'open_purchasevalue': 0,
                    'open_purchasevalue_base': 0,
                    'open_purchasevalue_DKK': 0,

                })

            else:

                if  record.product_qty != 0 and record.state not in ['draft','sent','cancel'] :
                                        
                    sales_val = (record.product_qty - record.qty_invoiced) / record.product_qty * record.price_subtotal
                    
                    if sales_val < 0:

                        sales_val  = 0

                    record.update({
                        
                        'purchasevalue_base': record.price_subtotal / record.currency_id.rate,
                        'purchasevalue_DKK': record.price_subtotal / record.currency_id.rate * DKK_rate,
                        'open_purchasevalue': sales_val,
                        'open_purchasevalue_base': sales_val / record.currency_id.rate,
                        'open_purchasevalue_DKK': sales_val / record.currency_id.rate * DKK_rate

                    })
                
                else:
                    
                    record.update({
                        
                        'purchasevalue_base': 0,
                        'purchasevalue_DKK': 0,
                        'open_purchasevalue': 0,
                        'open_purchasevalue_base': 0,
                        'open_purchasevalue_DKK': 0,

                    })



    
  