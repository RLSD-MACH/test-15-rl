from xml.etree.ElementTree import Comment
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
import requests
import json


class Outlay(models.Model):
    
    _name = 'outlay'
    _description = 'Outlay'
    _order = 'name'
    _check_company_auto = True
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _compute_open_balance(self):

        for record in self:

            open_balance = 0

            for line in record.balance_account_move_line_ids:            
                open_balance += line.balance

            record.open_balance = open_balance

    name = fields.Char(required=True,string='Outlay', index=True, default=lambda self: _('New')) #readonly=True, states={'draft': [('readonly', True)]}, 
    account_move_id = fields.Many2one('account.move', string='Account Move', related="cost_line_id.move_id", readonly=True, store=True)
    date = fields.Date(string='Date', related="account_move_id.date", readonly=True, store=True)    
    expected_date = fields.Date(string='Expected', readonly=False, traking=True)    
    
    account_move_partner_id = fields.Many2one('res.partner', string='Vendor', related="account_move_id.partner_id", readonly=True, store=True)
    cost_line_id = fields.Many2one('account.move.line', string='Cost Account Move Line', readonly=True,)
    partner_ids = fields.Many2many('res.partner', string='Customer(s)')
    new_description = fields.Char(required=False, string='Description', readonly=False,)
    description = fields.Char(required=False, string='Description', readonly=True,)
    product_id = fields.Many2one('product.product', string='Product', readonly=True,)
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', readonly=True,)
    quantity = fields.Float(required=True, string='Quantity', default="1", readonly=True,)        
    cost_price_unit = fields.Float(required=True, string='Cost Unit Price', readonly=True,) 
    cost_price_total = fields.Float(required=True, string='Cost Total', readonly=True,) 
    account_move_line_ids = fields.One2many('account.move.line', 'outlay_id', string='Account Move Lines', readonly=True,)
    specification_ids = fields.One2many('outlay.specification', 'outlay_id', string='Manual cost specification', readonly=False,)
    
    balance_account_move_line_ids = fields.One2many('account.move.line', 'outlay_id', string='Balance Account Move Lines', domain=[('account_id.user_type_id.include_initial_balance','=',True)], readonly=True,copy=False)
    outlay_entry_ids = fields.One2many('outlay.entry', 'outlay_id', string='Outlay Entries', readonly=True,)
    open_balance = fields.Float(default="0", string='Open Balance', compute='_compute_open_balance', readonly=True, store=True) 
    comment = fields.Text('Comment',help='')
    user_id = fields.Many2one("res.users", string='Responsible for billing', readonly=False, tracking=True, ondelete='restrict', required=False) 
        
    active = fields.Boolean(required=True, string='Active', default=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company, readonly=True,)
           
    message_main_attachment_id = fields.Many2one('ir.attachment', related="account_move_id.message_main_attachment_id")
       
    @api.model    
    def create (self, vals):

        next_seq = self.env['ir.sequence'].next_by_code('reinvoicable_services.outlay.sequence')

        if next_seq != False:

            vals['name'] = next_seq

        vals['open_balance'] = vals.get('cost_price_total',0)
        
        res = super(Outlay, self).create(vals)

        return res


class OutlayEntry(models.Model):
    
    _name = 'outlay.entry'
    _description = 'Outlay Entry'
    _order = 'id desc'
    _check_company_auto = True
      
    outlay_id = fields.Many2one('outlay', string='Outlay')
    
    move_line_ids = fields.One2many('account.move.line', 'outlay_entry_id', string='Account move lines') #, ondelete='cascade'
    active = fields.Boolean(required=True, string='Active', default=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company, readonly=True,)
       

class OutlaySpecification(models.Model):
    
    def _get_default_outlay_id(self):
        outlay_id = self.env.context.get('default_outlay_id')
        return outlay_id if outlay_id else None

    _name = 'outlay.specification'
    _description = 'Outlay Specification'
    _order = 'sequence'
    _check_company_auto = True

    outlay_id = fields.Many2one('outlay', string='Outlay')
    sequence = fields.Integer(string='Sequence')
    date = fields.Date(string='Date', readonly=False,)
    name = fields.Char(required=True)
    partner_id = fields.Many2one('res.partner', string='Customer', readonly=False,)    
    note = fields.Text(required=False, string='Internal note', readonly=False,)
    product_id = fields.Many2one('product.product', string='Product', readonly=False,)
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', readonly=False,  compute='_compute_Measure')
    quantity = fields.Float(required=True, string='Quantity', default="1", readonly=False,)        
    cost_price_unit = fields.Float(required=True, string='Cost Unit Price', readonly=False, compute='_compute_cost_price') 
    cost_price_total = fields.Float(required=True, string='Cost Total', readonly=False, compute='_compute_cost_price_total', store=True) 
    sales_price_unit = fields.Float(required=True, string='Sales Unit Price', readonly=False, compute='_compute_sales_price') 
    sales_price_total = fields.Float(required=True, string='Sales Total', readonly=False, compute='_compute_sales_price_total', store=True) 

    account_move_line_id = fields.Many2one('account.move.line', string='Account Move Lines', readonly=False,)
    account_move_id = fields.Many2one('account.move', string='Journal entry', readonly=True, related="account_move_line_id.move_id")
    
  
    active = fields.Boolean(required=True, string='Active', default=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company, readonly=True,)
       

    @api.onchange('cost_price_unit','quantity')
    def _compute_cost_price_total(self):

        for record in self:
            
            record.cost_price_total = record.quantity * record.cost_price_unit

    @api.onchange('cost_price_total')
    def _compute_cost_price(self):

        for record in self:
            
            record.cost_price_unit = record.cost_price_total / record.quantity if record.quantity != 0 else record.cost_price_total


    @api.onchange('sales_price_total')
    def _compute_sales_price(self):

        for record in self:
            
            record.sales_price_unit = record.sales_price_total / record.quantity if record.quantity != 0 else record.sales_price_total

    @api.onchange('sales_price_unit','quantity')
    def _compute_sales_price_total(self):

        for record in self:
            
            record.sales_price_total = record.quantity * record.sales_price_unit

   

    @api.onchange('product_id')
    def _compute_Measure(self):

        for record in self:
            
            if not record.product_uom_id:
                record.product_uom_id = record.product_id.uom_id.id
            
            if not record.name:
                record.name = record.product_id.name