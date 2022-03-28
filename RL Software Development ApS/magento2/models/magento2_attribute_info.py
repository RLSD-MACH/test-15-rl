from odoo import api, fields, models

class Magento2Attribute(models.Model):
    
    _name = 'magento2.attribute.info'
    _description = 'Magento2 attribute info'
    _order = 'id'
    _check_company_auto = True

    name = fields.Char(required=False,string='Name')
    category_id = fields.Integer(string='Category', required=False)
    sequence = fields.Integer(string='Sequence', required=False)
    external_id = fields.Char(required=False,string='External')    
    active = fields.Boolean(required=True, string='Active', default=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)

    def action_update_products_info(self):

        for record in self:
  
            products = self.env['product.template'].search([['default_code','=',record.external_id]])

            if len(products) == 1:
                
                for product in products:
                
                    categories = []

                    for ct in product.public_categ_ids:

                        categories.append(ct.id)

                    categories.append(record.category)

                    product.write({
                    
                        'public_categ_ids': categories
                    
                    })
                    
                    record.write({
                    
                        'active': False
                    
                    })
   