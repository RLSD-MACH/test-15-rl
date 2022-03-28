# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime, timedelta, date
from odoo.exceptions import AccessError, UserError, ValidationError

class SaleOrderInherit(models.Model):
    
    _inherit = 'sale.order'


    def action_extract_text_pdf (self):
        
        for record in self:

            if record.state in ['draft','sent']:

                docs = record.message_main_attachment_id.extract_text_pdf(docs=record.message_main_attachment_id)

                line_env = self.env['sale.order.line']

                for doc in docs:
                    
                    for line in doc["table_lines"]:

                        product = self.env['product.template'].search([('default_code','=',line['product_supplier'])])

                        if product:
                            
                            discount = 100 - float(line['unit_price'].replace(".","").replace(',','.')) * float(line['quantity'].replace(".","").replace(',','.')) / float(line['price'].replace(".","").replace(',','.')) * 100
                            
                            if discount != 0:

                                new_line = line_env.create({

                                    'order_id': record.id,
                                    'product_id': product.id,
                                    'product_uom_qty': float(line['quantity'].replace(".","").replace(',','.')),
                                    'name': line['description'],
                                    'price_unit': float(line['unit_price'].replace(".","").replace(',','.')),
                                    'discount': discount
                                    # 'price_subtotal': float(line['price'].replace(".","").replace(',','.'))
                                })

                                # new_line.product_id_change()
                            
                            else:

                                new_line = line_env.create({

                                    'order_id': self.id,
                                    'product_id': product.id,
                                    'product_uom_qty': float(line['quantity'].replace(".","").replace(',','.')),
                                    'name': line['description'],
                                    'price_unit': float(line['unit_price'].replace(".","").replace(',','.')),
                                    # 'price_subtotal': float(line['price'].replace(".","").replace(',','.')) 

                                })

                                # new_line.product_id_change()
                            
                                    # obj_rows['recieve_date'] = line.group(4)                            
                                    # obj_rows['unit'] = line.group(6)
    
