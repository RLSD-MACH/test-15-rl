# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class StockMoveInherit(models.Model):

    _inherit = 'stock.move'
    
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

                        vals['name'] = products[0].name

                    if 'product_uom' not in vals:

                        vals['product_uom'] = products[0].uom_id.id

                    done = True

            if 'product_barcode' in vals and done == False:

                products = self.env['product.product'].search([['barcode','=',vals['product_barcode'].upper()]])

                if len(products) == 1:

                    vals['product_id'] = products[0].id

                    if 'name' not in vals:

                        vals['name'] = products[0].name

                    if 'product_uom' not in vals:

                        vals['product_uom'] = products[0].uom_id.id

                    done = True

            if 'product_customer_art_no' in vals and done == False:

                products = self.env['product.product'].search([['product_tmpl_id.customer_art_no','=',vals['product_customer_art_no'].upper()]])

                if len(products) == 1:

                    vals['product_id'] = products[0].id

                    if 'name' not in vals:

                        vals['name'] = products[0].name
                        
                    if 'product_uom' not in vals:

                        vals['product_uom'] = products[0].uom_id.id

                    done = True

        res = super(StockMoveInherit, self).create(vals)
            
        return res

    @api.model
    def get_import_templates(self):

        return [{

            'label': _('Import Template'),
            'template': '/stock_move_import/static/templates/import_stock_move.xlsx'

        }]  