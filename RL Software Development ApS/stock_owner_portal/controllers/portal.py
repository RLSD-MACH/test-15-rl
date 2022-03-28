# -*- coding: utf-8 -*-

# import binascii
# from collections import OrderedDict
# from operator import itemgetter
# from markupsafe import Markup

from odoo import fields, http, _
# from odoo.exceptions import AccessError, MissingError, ValidationError
# from odoo.fields import Command
# from odoo.http import request

# from odoo.tools import groupby as groupbyelem
# from odoo.exceptions import ValidationError, UserError

from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager, get_records_pager
# from odoo.addons.web.controllers.main import HomeStaticTemplateHelpers

from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.osv.expression import OR

from odoo.exceptions import AccessError, MissingError, UserError
from collections import OrderedDict
from odoo.http import request

class PartnerStockPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        stock = request.env['stock.quant']
        
        domain = self._get_default_domain_stock(partner)

        if 'stock_count' in counters:
            
            values['stock_count'] = stock.search_count(domain) if stock.check_access_rights('read', raise_exception=False) else 0

        return values
   
    @http.route(['/my/stock', '/my/stock/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_stock(self, page=1, sortby=None, filterby=None, search=None, search_in='all', groupby=None, **kw):
        
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        
        stock = request.env['stock.quant']

        domain = self._get_default_domain_stock(partner)
        
        searchbar_filters = {
            '01_all': {'label': _('All'), 'domain': [], 'sequence': 1},
            '02_in_stock': {'label': _('In stock'), 'domain': [('quantity','>',0)], 'sequence': 2},
            '03_available': {'label': _('Available'), 'domain': [('available_quantity','>',0)], 'sequence': 3},
        }
        
        searchbar_sortings = self._get_searchbar_sortings_stock()
        searchbar_inputs = self._get_searchbar_inputs_stock()
        searchbar_groupby = self._get_searchbar_groupby_stock()
        
        # extends filterby criteria with users access to
#         projects = request.env['project.project'].search([])
#         for project in projects:
#             searchbar_filters.update({
#                 str(project.id): {'label': project.name, 'domain': [('project_id', '=', project.id)]}
#             })
                   
        # default sortby order
        if not sortby:
            sortby = 'product_id'
        sort_order = searchbar_sortings[sortby]['order']
        
        # default filter by value
        if not filterby:
            filterby = '01_all'
        domain += searchbar_filters.get(filterby, searchbar_filters.get('01_all'))['domain']
        
        # default group by value
        if not groupby:
            groupby = 'none'

        # search
        if search and search_in:
            domain += self._get_search_domain_stock(search_in, search)

        # count for pager
        stock_count = stock.search_count(domain)
        
        # make pager
        pager = portal_pager(
            url="/my/stock",
            url_args={'sortby': sortby, 'filterby': filterby, 'groupby': groupby, 'search_in': search_in, 'search': search},
            total=stock_count,
            page=page,
            step=self._items_per_page
        )
        
        
        # search the count to display, according to the pager data
#         stock = stock.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        
        stock = stock.sudo().read_group(domain, 
                                 fields=['owner_id', 'product_id', 'quantity', 'available_quantity'], 
                                 groupby=['owner_id', 'product_id'],
                                 lazy=False
                                )
        
        for line in stock:
            if '__domain' in line:
                lines = request.env['stock.quant'].sudo().search(line['__domain'])
                line['default_code'] = lines[0].product_id.default_code
                line['customer_art_no'] = lines[0].product_id.customer_art_no
                line['name'] = lines[0].product_id.name
                line['owner'] = lines[0].owner_id.name
                
        # extends filterby criteria with project (criteria name is the project id)
        # Note: portal users can't view projects they don't follow
        owners = request.env['stock.quant'].read_group(domain,['owner_id'], ['owner_id'])
        for owner in owners:
            owner_id = owner['owner_id'][0] if owner['owner_id'] else False
            owner_name = owner['owner_id'][1] if owner['owner_id'] else _('Others')
            searchbar_filters.update({
                str(owner_id): {'label': owner_name, 'domain': [('owner_id', '=', owner_id)]}
            })
        
        request.session['my_stock_history'] = stock
        
        # groupby_mapping = self._get_groupby_mapping_stock()
        # group = groupby_mapping.get(groupby)
        # if group:
        #     grouped_records = [Task.concat(*g) for k, g in groupbyelem(tasks, itemgetter(group))]
        # else:
        #     grouped_records = [tasks]


        values.update({
            
            'stock': stock,
            'page_name': 'stock',
            'pager': pager,
            'default_url': '/my/stock',
            'searchbar_sortings': searchbar_sortings,
#             'searchbar_groupby': searchbar_groupby,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
#             'groupby': groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            
        })
        
        return request.render("stock_owner_portal.portal_my_stock", values)
    

    # @http.route(['/my/stock/<int:product_id>'], type='http', auth="user", website=True)
    # def portal_statement_page(self, product_id, report_type=None, access_token=None, message=False, download=False, **kw):
        
    #     try:
            
    #         order_sudo = self._document_check_access('rlbooks_statement.report.print', product_id, access_token=access_token)
            
    #     except (AccessError, MissingError):
            
    #         return request.redirect('/my')        

    #     if report_type in ['pdf']:

    #         return order_sudo._show_report_custome(model=order_sudo, report_type=report_type, report_ref='partner_statement_portal.action_report_statement', download=download, attachment=True)

    #     elif report_type in ('html', 'pdf', 'text'):
            
    #         return self._show_report(model=order_sudo, report_type=report_type, report_ref='partner_statement_portal.action_report_statement', download=download)

    #     elif report_type in ['main_attachment']:
            
    #         if order_sudo.message_main_attachment_id:
                            
    #             return  {

    #                     'name': 'Report',
    #                     'type': 'ir.actions.act_url',
    #                     'url': "web/content/?id=" + str(
    #                         order_sudo.message_main_attachment_id.id) + "&download=true",
    #                     'target': 'self',
    #                 }
             

    #     # use sudo to allow accessing/viewing orders for public user
    #     # only if he knows the private token
    #     # Log only once a day
    #     if order_sudo:
    #         # store the date as a string in the session to allow serialization
    #         now = fields.Date.today().isoformat()
    #         session_obj_date = request.session.get('view_quote_%s' % order_sudo.id)
    #         if session_obj_date != now and request.env.user.share and access_token:
    #             request.session['view_quote_%s' % order_sudo.id] = now
    #             body = _('Report viewed by customer %s', order_sudo.partner_id.name)
    #             _message_post_helper(
    #                 "rlbooks_statement.report.print",
    #                 order_sudo.id,
    #                 body,
    #                 token=order_sudo.access_token,
    #                 message_type="notification",
    #                 subtype_xmlid="mail.mt_note",
    #                 partner_ids=order_sudo.user_id.sudo().partner_id.ids,
    #             )

    #     values = {
    #         'statement': order_sudo,
    #         'message': message,
    #         'token': access_token,
    #         'landing_route': '/shop/payment/validate',
    #         'bootstrap_formatting': True,
    #         'partner_id': order_sudo.partner_id.id,
    #         'report_type': 'html',
    #         'action': order_sudo._get_portal_return_action(),
    #     }
        
    #     if order_sudo.company_id:
    #         values['res_company'] = order_sudo.company_id
               
    #     history = request.session.get('my_statements_history', [])
            
    #     values.update(get_records_pager(history, order_sudo))

    #     return request.render('partner_statement_portal.portal_statement_page', values)

        
    
    def _get_searchbar_sortings_stock(self):
        
        return {
            
            'create_date': {'label': _('Created'), 'order': 'create_date desc', 'sequence': 1},
            'product_id': {'label': _('Product'), 'order': 'product_id asc', 'sequence': 2},
            'quantity': {'label': _('Quantity'), 'order': 'quantity asc', 'sequence': 3},
            'available': {'label': _('Available qty'), 'order': 'available_quantity asc', 'sequence': 3},
            
        }

    def _get_searchbar_groupby_stock(self):
        
        values = {
            'none': {'input': 'none', 'label': _('None'), 'order': 1},
            'create_date': {'input': 'create_date', 'label': _('Created'), 'order': 2},
            'product': {'input': 'product', 'label': _('Product'), 'order': 3},
#             'quantity': {'input': 'quantity', 'label': _('Quantity'), 'order': 4},
        }
        
        return dict(sorted(values.items(), key=lambda item: item[1]["order"]))
   
    def _get_groupby_mapping_stock(self):
        
        return {
            
            'create_date': 'create_date',
            'product': 'product_id',
            'quantity': 'quantity',
            'available': 'available_quantity',
        }
    
    def _get_searchbar_inputs_stock(self):
        
        values = {
            'all': {'input': 'all', 'label': _('Search in All'), 'order': 1},
            'name': {'input': 'name', 'label': _('Search in Ref'), 'order': 2},
            'product': {'input': 'product', 'label': _('Search in Product'), 'order': 3},
        }
        
        return dict(sorted(values.items(), key=lambda item: item[1]["order"]))

    def _get_search_domain_stock(self, search_in, search):
        search_domain = []
        if search_in in ('content', 'all'):
            search_domain.append([('product_id.name', 'ilike', search)])
        if search_in in ('name', 'all'):
            search_domain.append([('product_id.name', 'ilike', search)])
        if search_in in ('product', 'all'):
            search_domain.append([('product_id', 'ilike', search)])
        # if search_in in ('partners', 'all'):

        #     partner_ids = request.env['res.partner'].sudo().search([('name', 'ilike', search)])
        #     search_domain.append([('partner_id', 'in', partner_ids.ids)])
       
        return OR(search_domain)

    def _get_default_domain_stock(self, partner):

        list_ids = [partner.commercial_partner_id.id, partner.id]
        if partner.portal_access_to_stock_from_ids.ids:
            list_ids += partner.portal_access_to_stock_from_ids.ids

        domain = [
            ('owner_id', 'in', list_ids),
            ('location_id.usage','=', 'internal')
        ]

        return domain