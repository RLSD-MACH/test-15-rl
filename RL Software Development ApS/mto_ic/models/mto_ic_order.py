from datetime import datetime, timedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.osv import expression


class MtoIcOrder(models.Model):
    
    _name = 'mto.ic_order'
    _description = 'MTO IC order'
    _order = 'create_date desc'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    def _compute_all_purchased(self):

        for order in self:

            lines_missing_purchase = order.line_ids.filtered(lambda p: p.to_request_from_supplier_qty != 0)

            if  lines_missing_purchase:

               order.all_purchased = False
            
            else:

                order.all_purchased = True
    
    def _compute_on_so(self):

        for order in self:

            lines_missing_so = order.line_ids.filtered(lambda p: p.to_sale_order_qty != 0)

            if  lines_missing_so:

               order.all_on_so = False
            
            else:

                order.all_on_so = True

    def _compute_purchase_order_count(self):

        for order in self:

            order.purchase_order_count = len(order.sudo().purchase_order_ids.ids)

    def _compute_sale_order_count(self):

        for order in self:

            order.sale_order_count = len(order.sudo().sale_order_ids.ids)

    name = fields.Char(required=True,string='Order', readonly=True, states={'draft': [('readonly', True)]}, index=True, default=lambda self: _('New'))
    customer_id = fields.Many2one("res.partner", string='Customer', ondelete='restrict')
    customer_order_ref = fields.Char(required=False,string='Customer order ref')
    seller_id = fields.Many2one('res.company', 'Seller', required=False)
    sale_order_ids = fields.One2many('sale.order', 'mto_ic_order_id', 'Sale orders', required=False)
    purchaser_id = fields.Many2one('res.company', 'Purchaser', required=False)
    purchase_order_ids = fields.One2many('purchase.order', 'mto_ic_order_id', 'Purchase orders', required=False)
    line_ids = fields.One2many('mto.ic_order_line', 'order_id', 'Order lines')
    confirmed = fields.Date(required=False, string='Confirmed', readonly=True, tracking=True)
    stage_id = fields.Many2one("mto.ic_order.stage", string='Stage', ondelete='restrict', index=True, tracking=True,
        compute='_compute_stage_id', readonly=False, store=True, copy=False, required=False)
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('confirmed', 'Confirmed'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    sale_order_count = fields.Integer(string='Sale order count', compute="_compute_sale_order_count", compute_sudo=True)
    purchase_order_count = fields.Integer(string='Purchase order count', compute="_compute_purchase_order_count", compute_sudo=True)
    
    active = fields.Boolean(required=True, string='Active', default=True, copy=False)
    all_purchased = fields.Boolean(required=False, string='All purchased', compute="_compute_all_purchased", compute_sudo=True)
    all_on_so = fields.Boolean(required=False, string='All on SO', compute="_compute_on_so", compute_sudo=True)
      
    def preview_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }
    
    @api.model    
    def create (self, vals):

        next_seq = self.env['ir.sequence'].next_by_code('mto.ic_order.sequence')

        if next_seq != False:

            vals['name'] = next_seq

        res = super(MtoIcOrder, self).create(vals)

        return res

    @api.depends(lambda self: (self._rec_name,) if self._rec_name else ())
    def _compute_display_name(self):

        names = dict(self.name_get())
        for record in self:

            if record.customer_order_ref != False and record.customer_order_ref != '':

                calc_name =  names.get(record.id, '') + " [" + record.customer_order_ref + "]"
            
            else:

                calc_name = names.get(record.id, False)

            if record.customer_id:

                calc_name += " - " + record.customer_id.name

            
            record.display_name = calc_name

    def _compute_stage_id(self):

        for order in self:

            if not order.stage_id:

                order.stage_id = self.env['mto.ic_order.stage'].search([('active','=',True)], order='sequence', limit=1).id

    def action_confirm(self):

        self.ensure_one()

        if self.confirmed == False:

            self.confirmed = datetime.today()
            self.state = 'confirmed'

            message = 'I dont know if we made any money, but a cofirmed order i always a good thing :)'

            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': message,
                    'img_url': '/web/static/src/img/smile.svg',
                    'type': 'rainbow_man',
                }
            }


    def action_create_sale_order(self):

        self.ensure_one()

        ic_order_line = self.env['mto.ic_order_line'].search([('order_id','=',self.id),('to_sale_order_qty','!=',0)])
        
        if len(ic_order_line)>0:

            sale_order = self.env['sale.order'].create({

            'partner_id': self.customer_id.id,
            # 'partner_invoice_id': False,
            # 'partner_shipping_id': False,
            #    'currency_id': self.customer_id.property_product_pricelist.currency_id.id,
            'date_order': datetime.today(),
            'pricelist_id': self.customer_id.property_product_pricelist.id,
            'fiscal_position_id': self.customer_id.property_account_position_id.id,
            'payment_term_id': self.customer_id.property_payment_term_id.id,
            'company_id': self.seller_id.id,
            'user_id': self.env.uid,
            'mto_ic_order_id': self.id

            }
            )

            for line in ic_order_line:

                sale_order_line = self.env['sale.order.line'].create({

                'order_id': sale_order.id,
                'company_id': self.seller_id.id,
                'product_uom_qty': line.to_sale_order_qty,
                'product_id': line.product_id.id,
                'price_unit': line.sale_price,
                'mto_ic_order_line_id': line.id

                }
                )

                line.on_sale_order_qty += line.to_sale_order_qty

            return {

                'type': 'ir.actions.act_window',
                'name': 'Sale order',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sale.order',
                "res_id": sale_order.id,
                'views': [(self.env.ref("sale.view_order_form").id, 'form')],
                'target': 'current',

            }

    def action_create_purchase_order(self):

        self.ensure_one()

        ic_order_lines = self.env['mto.ic_order_line'].search([('order_id','=',self.id),('to_request_from_supplier_qty','!=',0)])
                
        if len(ic_order_lines)>0:

            vendors = []
            vendor_id = []
            product_groups = []

            for ic_order_line in ic_order_lines:

                sellers = ic_order_line.product_id.seller_ids.filtered(lambda p: p.company_id == self.purchaser_id or p.company_id == False)

                if len(sellers) > 0:

                    if sellers[0].name not in vendors:

                        vendors.append(sellers[0].name)

                        new_sublist = []
                        new_sublist.append(ic_order_line)
                        product_groups.append(new_sublist)

                    else:

                        product_groups[vendors.index(sellers[0].name)].append(ic_order_line)

                else:

                    raise UserError("Product: '" + ic_order_line.product_id.display_name + "' dosen't have any vendors registred." )

            for vendor in vendors:    

                purchase_order = self.env['purchase.order'].create({

                    'partner_id': vendor.id,
                    #    'currency_id': self.customer_id.property_product_pricelist.currency_id.id,
                    'date_order': datetime.today(),
                    # 'requisition_id': vendor.purchase_requisition_id.id,
                    'fiscal_position_id': vendor.property_account_position_id.id,
                    'payment_term_id': vendor.property_supplier_payment_term_id.id,
                    'incoterm_id': vendor.property_supplier_incoterm_id.id,
                    'company_id': self.purchaser_id.id,
                    'user_id': self.env.uid,
                    'mto_ic_order_id': self.id,
                    'origin': self.name

                })

                for line in product_groups[vendors.index(vendor)]:
                    
                    purchase_order_line = self.env['purchase.order.line'].create({

                    'order_id': purchase_order.id,
                    'company_id': self.purchaser_id.id,
                    'product_qty': line.to_request_from_supplier_qty,
                    'product_id': line.product_id.id,
                    'price_unit': line.sale_price,
                    'mto_ic_order_line_id': line.id

                    })

                    line.requested_from_supplier_qty += line.to_request_from_supplier_qty

            return {

                'type': 'ir.actions.act_window',
                'name': 'Purchase order',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'purchase.order',
                "res_id": purchase_order.id,
                'views': [(self.env.ref("purchase.purchase_order_form").id, 'form')],
                'target': 'current',

            }

    def action_view_sale_orders(self, orders=False):
                  
        if not orders:

            self.sudo()._read(['sale_order_ids'])

            orders = self.sale_order_ids

        result = self.env['ir.actions.act_window']._for_xml_id('sale.action_quotation_form')
        
        if len(orders) > 1:

            result['domain'] = [('id', 'in', orders.ids)]

        elif len(orders) == 1:

            res = self.env.ref('sale.view_order_form', False)

            form_view = [(res and res.id or False, 'form')]

            if 'views' in result:

                result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']

            else:

                result['views'] = form_view

            result['res_id'] = orders.id

        else:

            result = {'type': 'ir.actions.act_window_close'}

        return result

    def action_view_purchase_orders(self, orders=False):
                  
        if not orders:

            self.sudo()._read(['purchase_order_ids'])

            orders = self.purchase_order_ids

        result = self.env['ir.actions.act_window']._for_xml_id('purchase.purchase_form_action')
        
        if len(orders) > 1:

            result['domain'] = [('id', 'in', orders.ids)]

        elif len(orders) == 1:

            res = self.env.ref('purchase.view_order_form', False)

            form_view = [(res and res.id or False, 'form')]

            if 'views' in result:

                result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']

            else:

                result['views'] = form_view

            result['res_id'] = orders.id

        else:

            result = {'type': 'ir.actions.act_window_close'}

        return result

class MtoIcOrder_Stage(models.Model):

    _name = 'mto.ic_order.stage'
    _description = 'MTO IC order stage'
    _order = 'sequence, name'

    name = fields.Char(required=True,string='Name')
    active = fields.Boolean(required=True,string='Active',default=True)
    is_closed = fields.Boolean(required=True,string='Is closed',default=False)
    sequence = fields.Integer(string='Sequence',required=True,default=0)