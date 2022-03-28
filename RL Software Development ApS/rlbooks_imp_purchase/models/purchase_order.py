from odoo import api, fields, models

class PurchaseOrderInherit(models.Model):
        
    _inherit = 'purchase.order'
    
    finished = fields.Boolean(string='Finished', compute='_compute_open_purchasevalue', readonly=False, store=True, copy=False, required=False, tracking=True, default=False, compute_sudo=True)

    contact_id = fields.Many2one("res.partner", string='Contact', ondelete='restrict', required=False, readonly=False, copy=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id), ('parent_id', '=', partner_id), ('type', '=','contact')]")

    order_text = fields.Text('Quotation/Order Text', translate=False)
    
    open_purchasevalue = fields.Float(compute='_compute_open_purchasevalue', string='Open purchasevalue', store=True, readonly=True, compute_sudo=True)
    open_purchasevalue_DKK = fields.Float(compute='_compute_open_purchasevalue', string='Open purchasevalue DKK', store=True, readonly=True, compute_sudo=True)
    open_purchasevalue_base = fields.Float(compute='_compute_open_purchasevalue', string='Open purchasevalue Base', store=True, readonly=True, compute_sudo=True)
    purchasevalue_DKK = fields.Float(compute='_compute_open_purchasevalue', string='Purchasevalue DKK', store=True, readonly=True, compute_sudo=True)
    purchasevalue_base = fields.Float(compute='_compute_open_purchasevalue', string='Purchasevalue Base', store=True, readonly=True, compute_sudo=True)

    def init(self): 

        self._recalculate_open_purchasevalue()    
   

    @api.onchange('partner_id')
    def _onchange_incoterm_id(self):
        
        for record in self:
    
            partner = record.partner_id

            record.update({
                
                'incoterm_id': partner.property_supplier_incoterm_id.id if partner.property_supplier_incoterm_id.id else None,
                'payment_term_id': partner.property_supplier_payment_term_id.id if partner.property_supplier_payment_term_id.id else None,
                'contact_id': partner.contact_id.id if partner.contact_id.id else None,
            })

    @api.depends('state', 'order_line')
    def _compute_open_purchasevalue(self):

        self._recalculate_open_purchasevalue()

    def _recalculate_open_purchasevalue(self): 
        
        for record in self:

            if record.state == 'draft' or record.state == 'sent':
            
                record.update({
                    
                    'finished': False
                })
            
            elif record.state == 'cancel':
            
                record.update({
                    
                    'finished': True
                })
            
            else:
            
                finished = True
            
                for line in record.order_line:
                    
                    # if line.product_type != 'service':
                        
                        if line.qty_to_receive > 0 or line.qty_to_invoice !=0:
                        
                            finished = False
                    
                    # else:

                    #     if line.qty_to_invoice !=0:
                        
                    #         finished = False
            
                record.update({
                    
                    'finished': finished

                })
    
            if record.state in ['draft','sent','cancel']:
            
                record.update({
                    
                    'open_purchasevalue': 0,
                    'open_purchasevalue_base': 0,
                    'open_purchasevalue_DKK': 0,
                    'purchasevalue_DKK': 0,
                    'purchasevalue_base': 0

                })
            
            else:
            
                record.update({
                    
                    'open_purchasevalue': sum(l.open_purchasevalue for l in record.order_line),
                    'open_purchasevalue_base': sum(l.open_purchasevalue_base for l in record.order_line),
                    'open_purchasevalue_DKK': sum(l.open_purchasevalue_DKK for l in record.order_line),
                    'purchasevalue_DKK': sum(l.purchasevalue_DKK for l in record.order_line),
                    'purchasevalue_base': sum(l.purchasevalue_base for l in record.order_line)

                })
    
    def action_recalculate_open_purchasevalue(self):

        self._recalculate_open_purchasevalue()