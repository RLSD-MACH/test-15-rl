# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import ValidationError, UserError

class SaleOrderLineImport(models.Model):

    _name = 'sale.order.line.import'
    _description = 'Sale order line import'
    _order = 'id'
    _check_company_auto = True

    def _get_default_order_id(self):

        default_order_id = self.env.context.get('default_order_id')

        return [default_order_id] if default_order_id else None
    
    default_code = fields.Char(string='Default Code')
    barcode = fields.Char(string='Barcode')    
    customer_art_no = fields.Char(string='Customer art no') 
    product = fields.Char(string='Product')
    description = fields.Char(string='Description')

    order_id = fields.Many2one('sale.order', string='Sale order', ondelete='restrict')
    product_id = fields.Many2one(
        'product.product', 
        string='Product', 
        domain="[('sale_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        change_default=True, 
        ondelete='restrict')
    
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)
    discount = fields.Float(string='Discount (%)', digits='Discount', default=0.0)
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]")
    
    active = fields.Boolean(required=True,string='Active',default=True)
    user_id = fields.Many2one("res.users", string='User',default=lambda self: self.env.uid, ondelete='restrict', required=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)

    @api.model
    def create(self, vals):

        if 'product_id' not in vals:

            done = False

            if 'default_code' in vals and done == False:
                
                products = self.env['product.product'].search([['default_code','=',vals['default_code'].upper()]])
                
                if len(products) == 1:
                    
                    vals['product_id'] = products[0].id

                    done = True

            if 'barcode' in vals and done == False:

                products = self.env['product.product'].search([['barcode','=',vals['barcode'].upper()]])

                if len(products) == 1:

                    vals['product_id'] = products[0].id

                    done = True

            if 'customer_art_no' in vals and done == False:

                products = self.env['product.product'].search([['product_tmpl_id.customer_art_no','=',vals['customer_art_no'].upper()]])

                if len(products) == 1:

                    vals['product_id'] = products[0].id

                    done = True

        res = super(SaleOrderLineImport, self).create(vals)
            
        return res

    @api.onchange('default_code')
    def _onchange_default_code(self):

        for line in self:

            if line.default_code:

                products = self.env['product.product'].search([['default_code','=',line.default_code.upper()]])

                if len(products) == 1:

                    line.product_id = products[0].id

    @api.onchange('barcode')
    def _onchange_barcode(self):

        for line in self:

            if line.barcode:

                products = self.env['product.product'].search([['barcode','=',line.barcode.upper()]])

                if len(products) == 1:

                    line.product_id = products[0].id
               
    @api.onchange('customer_art_no')
    def _onchange_customer_art_no(self):

        for line in self:

            if line.customer_art_no:

                products = self.env['product.product'].search([['product_tmpl_id.customer_art_no','=',line.customer_art_no.upper()]])

                if len(products) == 1:

                    line.product_id = products[0].id

    # def action_submit_to_order(self):

    #     for record in self:

    #         if record.order_id and record.product_id:

    #             record.order_id.update({



    #             })
      

