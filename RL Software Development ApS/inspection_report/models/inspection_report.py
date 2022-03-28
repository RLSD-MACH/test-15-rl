# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, UserError
from odoo.http import content_disposition, Controller, request, route
import re

class InspectionReport(models.Model):
    
    _name = 'inspection.report'
    _description = 'Inspection report'
    _order = 'date desc'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _check_company_auto = True    
    
    partner_id = fields.Many2one('res.partner', related='purchase_order_id.partner_id', readonly="1", tracking=True)
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order', tracking=True)
    purchase_order_ids = fields.Many2many('purchase.order', string='Purchase Orders', tracking=True)
    purchase_order = fields.Char(string='Purchase order', readonly="1")
    product_ids = fields.Many2many('product.template', string='Products', tracking=True)
    
    date = fields.Date('Date of inspection', tracking=True)
    # report = fields.Binary("Report", attachment=True, help='Upload the file', tracking=True)
    message_main_attachment_id = fields.Many2one(domain="[('res_model','=','inspection.report'),('res_id','=',id),'|',('company_id', '=', False), ('company_id', '=', company_id)]")
    user_id = fields.Many2one("res.users", string='Resposible', default=lambda self: self.env.uid, ondelete='restrict', required=False)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('coditional_accepted', 'Coditional accepted'),
        ('rejected', 'Rejected')
    ], 
    string='State',
    default="draft",
    required=True, 
    help="Passed inspection or not?", 
    tracking=True)

    company_id = fields.Many2one('res.company', 'Company', required=False, index=True, default=lambda self: self.env.company, tracking=True)
    active = fields.Boolean(required=True, string='Active', default=True, copy=False, tracking=True)
