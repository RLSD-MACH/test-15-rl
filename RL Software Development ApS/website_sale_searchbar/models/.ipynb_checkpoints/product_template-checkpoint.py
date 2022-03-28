# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons.http_routing.models.ir_http import slug, unslug
from odoo.tools.translate import html_translate
from odoo.osv import expression


class ProductTemplate(models.Model):
    _inherit = [
        "product.template"
    ]
    
    barcode = fields.Char(store=True)
   
    @api.model
    def _search_get_detail(self, website, order, options):

        # See original in Website_sale > models > product_template

        rtn = super(ProductTemplate, self)._search_get_detail(website, order, options)

        with_default_code = options.get('displayDefault_code',False)
        with_barcode = options.get('displayBarcode',False)
        with_customer_art_no = options.get('displayCustomer_art_no',False)

        domains = rtn['base_domain']
        search_fields = rtn['search_fields']
        fetch_fields = rtn['fetch_fields']
        mapping = rtn['mapping']
        
        if with_default_code:
            search_fields.append('default_code')
            fetch_fields.append('default_code')
            mapping['default_code'] = {'name': 'default_code', 'type': 'text', 'match': True}
        
        if with_barcode:
            search_fields.append('barcode')
            fetch_fields.append('barcode')
            mapping['barcode'] = {'name': 'barcode', 'type': 'text', 'match': True}

        if with_customer_art_no:
            search_fields.append('customer_art_no')
            fetch_fields.append('customer_art_no')
            mapping['customer_art_no'] = {'name': 'customer_art_no', 'type': 'text', 'match': True}
        
        return {
            'model': 'product.template',
            'base_domain': domains,
            'search_fields': search_fields,
            'fetch_fields': fetch_fields,
            'mapping': mapping,
            'icon': 'fa-shopping-cart',
        }
 

   