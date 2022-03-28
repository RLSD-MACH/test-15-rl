# -*- coding: utf-8 -*-

from werkzeug.exceptions import NotFound

from odoo import http, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale_searchbar.controllers.controllers import WebsiteSaleInherit

from odoo.osv import expression
# from odoo.exceptions import AccessError, UserError, ValidationError


class WebsiteSaleSearchbarInherit(WebsiteSaleInherit):
	
    def _get_search_domain(self, search, category, attrib_values, search_in_description=True, search_default_code=True, search_barcode = True, search_customer_art_no = True):
        
        domain = super(WebsiteSaleSearchbarInherit, self)._get_search_domain(
            search, category, attrib_values, search_in_description, search_default_code, search_barcode, search_customer_art_no
        )
        
        domains = [domain]

        context = http.request.env.context

        if request.env.user.share:

            pricelist_context, pricelist = self._get_pricelist_context()
            
            domains.append([
                ('id', 'in', pricelist.item_ids.product_tmpl_id.ids)
            ])
                   
        return expression.AND(domains) 


class WebsiteSaleInherit2(WebsiteSale):
    
    @http.route(auth="user")
    def product(self, product, category='', search='', **kwargs):

        res = super(WebsiteSaleInherit2, self).product(product, category, search, **kwargs)

        context = http.request.env.context

        if request.env.user.share:

            if not context.get('pricelist'):

                pricelist_context, pricelist = self._get_pricelist_context()
                pricelist_id_int = pricelist.id

            else:

                pricelist_id_int = context['pricelist']
                pricelist = self.env['product.pricelist'].browse(pricelist_id_int)
       
            if product.id not in pricelist.item_ids.product_tmpl_id.ids:

                raise NotFound()

        return res

    @http.route(auth="user")
    def shop(self, page=0, category=None, search='', ppg=False, **post):

        res = super(WebsiteSaleInherit2, self).shop(page, category, search, ppg, **post)
        
        return res

