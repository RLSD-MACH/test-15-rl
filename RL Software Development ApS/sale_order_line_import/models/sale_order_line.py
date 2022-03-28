# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class SaleOrderLineInherit(models.Model):

    _inherit = 'sale.order.line'
    
    product_default_code = fields.Char(string='Default Code')
    product_barcode = fields.Char(string='Barcode')    
    product_customer_art_no = fields.Char(string='Customer art no') 
       
    @api.model
    def create(self, vals):

        if 'product_id' not in vals:

            done = False

            if 'product_default_code' in vals and done == False:
                
                products = self.env['product.product'].search([['default_code','=',vals['product_default_code'].upper()]])
                
                if len(products) == 1:
                    
                    vals['product_id'] = products[0].id

                    if 'name' not in vals:

                        vals['name'] = products[0].description_sale

                    done = True

            if 'product_barcode' in vals and done == False:

                products = self.env['product.product'].search([['barcode','=',vals['product_barcode'].upper()]])

                if len(products) == 1:

                    vals['product_id'] = products[0].id

                    if 'name' not in vals:

                        vals['name'] = products[0].description_sale

                    done = True

            if 'product_customer_art_no' in vals and done == False:

                products = self.env['product.product'].search([['product_tmpl_id.customer_art_no','=',vals['product_customer_art_no'].upper()]])

                if len(products) == 1:

                    vals['product_id'] = products[0].id

                    if 'name' not in vals:

                        vals['name'] = products[0].description_sale

                    done = True

        res = super(SaleOrderLineInherit, self).create(vals)
            
        return res

    @api.model
    def get_import_templates(self):

        return [{

            'label': _('Import Template'),
            'template': '/sale_order_line_import/static/templates/import_sale_order_line.xlsx'

        }]  

    # @api.onchange('default_code')
    # def _onchange_default_code(self):

    #     for line in self:

    #         if line.default_code:

    #             products = self.env['product.product'].search([['default_code','=',line.default_code.upper()]])

    #             if len(products) == 1:

    #                 line.product_id = products[0].id

    # @api.onchange('barcode')
    # def _onchange_barcode(self):

    #     for line in self:

    #         if line.barcode:

    #             products = self.env['product.product'].search([['barcode','=',line.barcode.upper()]])

    #             if len(products) == 1:

    #                 line.product_id = products[0].id
        
       
    # @api.onchange('customer_art_no')
    # def _onchange_customer_art_no(self):

    #     for line in self:

    #         if line.customer_art_no:

    #             products = self.env['product.product'].search([['product_tmpl_id.customer_art_no','=',line.customer_art_no.upper()]])

    #             if len(products) == 1:

    #                 line.product_id = products[0].id


      

