from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError

class ProductTemplateInherit(models.Model):
    
    _inherit = 'product.template'

    @api.model
    def create(self, vals):

        product = super(ProductTemplateInherit, self).create(vals)

        if not product.company_id.id:

            companies = self.env['res.company'].sudo().search([['id','!=',self.env.company.id]])

            if len(companies) > 0:
                
#                 category = product.categ_id
                
#                 if category.id:
                    
#                     for company in companies:
                                                
#                         sale_tax = []
#                         for tax in product.with_context(force_company=company.id).sudo().categ_id.property_account_income_categ_id.tax_ids:                            
#                             sale_tax += [tax.id]
                                                    
#                         purchase_tax = []                        
#                         for tax in product.with_context(force_company=company.id).sudo().categ_id.property_account_expense_categ_id.tax_ids:
#                              purchase_tax += [tax.id]
                        
#                         product.with_context(force_company=company.id).sudo().write({

#                             'taxes_id': [(6,0,sale_tax)],
#                             'supplier_taxes_id': [(6,0,purchase_tax)]

#                         })
                        
#                 else:
                    
                for company in companies:


                    product.with_context(force_company=company.id).sudo().write({

                        'taxes_id': [(6,0,[company.account_sale_tax_id.id] if company.account_sale_tax_id.id else [])],
                        'supplier_taxes_id': [(6,0,[company.account_purchase_tax_id.id] if company.account_purchase_tax_id.id else [])]

                    })

        return product

