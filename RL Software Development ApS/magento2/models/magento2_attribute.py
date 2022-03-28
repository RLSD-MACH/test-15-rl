from odoo import api, fields, models
import requests
import base64

class Magento2Attribute(models.Model):
    
    _name = 'magento2.attribute'
    _description = 'Magento2 attribute'
    _order = 'id'
    _check_company_auto = True

    name = fields.Char(required=False,string='Name')
    product_id = fields.Many2one('product.template', string='Product', required=True)
    store_id = fields.Many2one('magento2.store', string='Store', required=True) 
    value = fields.Char(required=False,string='Value')    
    active = fields.Boolean(required=True, string='Active', default=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)

    def action_get_pictures_from_magento2(self):

        for record in self:
  
            if record.active == True:
                
                attributes = []
                
                pictures_here = self.env['magento2.attribute'].search([['name','=','image'],['product_id','=',record.product_id.id]])
                attributes += pictures_here
                
                pictures_here = self.env['magento2.attribute'].search([['name','=','small_image'],['product_id','=',record.product_id.id]])
                attributes += pictures_here
                
                pictures_here = self.env['magento2.attribute'].search([['name','=','swatch_image'],['product_id','=',record.product_id.id]])
                attributes += pictures_here
                
                pictures_here = self.env['magento2.attribute'].search([['name','=','thumbnail'],['product_id','=',record.product_id.id]])
                attributes += pictures_here
                
                pictures = []
                
                for test in attributes:
                
                    if test.value not in pictures:
                        
                        pictures.append(test.value)
                
                for attribute in pictures:
                
                
                    image_url = "https://www.tukanpetproducts.dk/pub/media/catalog/product" + attribute
                    filename = image_url.split("/")[-1]
                    
                    r = requests.get(image_url, stream = True)
                    
                    if r.status_code == 200:
                        
                        #photo = r.content
                        photo = base64.b64encode(requests.get(image_url).content)
                        
                        #raise UserError(photo)
                        
                        if record.x_product_id.image_1920 != False:
                        
                            self.env['product.image'].create({
                                
                                'product_tmpl_id': record.x_product_id.id,
                                'name': filename,
                                'image_1920': photo
                                
                            })
                            
                        else:
                        
                            record.product_id.write({
                                
                                'image_1920': photo
                                
                            })
                            
                        To_close = self.env['magento2.attribute'].search([['value','=',attribute],['product_id','=',record.product_id.id]])
                        
                        To_close.write({
                        
                        'active': False
                        
                        })
                            
                    else:
                        
                        pass
                        #raise UserError("Error")
   