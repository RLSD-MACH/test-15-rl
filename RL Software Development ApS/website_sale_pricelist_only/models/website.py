# -*- coding: utf-8 -*-

from odoo import api, fields, http, models, _
from odoo.http import request
from odoo.exceptions import ValidationError, UserError
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteInherit(models.Model):
    
    _inherit = [
        "website"
    ]
     
    def _search_with_fuzzy(self, search_type, search, limit, order, options):
      
        count, results, fuzzy_term = super(WebsiteInherit, self)._search_with_fuzzy(search_type, search, limit, order, options)
          
        if search_type == 'products' or search_type == 'products_only':
                
            context = http.request.env.context

            pricelist_id_int = context.get('pricelist', False)
            pricelist = False
            count_all = 0
            results_all = []

            if pricelist_id_int:

                pricelist = self.env['product.pricelist'].browse(pricelist_id_int)

            else:

                pricelist_context, pricelist = WebsiteSale._get_pricelist_context(self)

            for result in results:
                
                if result['model'] == 'product.template':
                    
                    if pricelist.id:

#                         raise UserError("website; results: " + str(results[0]['results']) + " | >> " + str(pricelist.item_ids.product_tmpl_id.ids) + " | >> " + str(results))

                        filtered = [a for a in result['results'].ids if a in pricelist.item_ids.product_tmpl_id.ids]
                        result['results'] = self.env['product.template'].search([['id', 'in', filtered]])
                        result['count'] = len(filtered)

#                         raise UserError("website; results: " + str(results[0]['results']) + " | >> " + str(pricelist.item_ids.product_tmpl_id.ids))

                    else:

                        result['count'] = 0
                        result['results'] = self.env['product.template'].search([['id', 'in', []]])
                
                    
                count_all += result['count']
                                            
        
            count = count_all
                       
        return count, results, fuzzy_term
   