# -*- coding: utf-8 -*-

import binascii
from collections import OrderedDict
from operator import itemgetter
from markupsafe import Markup

from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.fields import Command
from odoo.http import request

from odoo.osv.expression import OR
from odoo.tools import groupby as groupbyelem

from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager, get_records_pager
from odoo.addons.web.controllers.main import HomeStaticTemplateHelpers

class ShipmentPortal(portal.CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        Orders = request.env['shipping.order']
        
        if 'shipment_count' in counters:
            
            values['shipment_count'] = Orders.search_count([
                
                ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
                ('state', 'in', [ 'underway', 'received', 'cancel'])
                
            ]) if Orders.check_access_rights('read', raise_exception=False) else 0

        return values
   
    @http.route(['/my/shipments', '/my/shipments/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_shipments(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='all', groupby=None, **kw):
        
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        
        Orders = request.env['shipping.order']

        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['underway', 'received', 'cancel'])
        ]
        
        searchbar_filters = {
            '01_all': {'label': _('All'), 'domain': [], 'sequence': 1},
            '02_plain': {'label': _('Air'), 'domain': [('shipping_type','=','plain')], 'sequence': 2},
            '03_ship': {'label': _('Sea'), 'domain': [('shipping_type','=','ship')], 'sequence': 3},
            '04_truck': {'label': _('Land'), 'domain': [('shipping_type','=','truck')], 'sequence': 4},
            '05_internal': {'label': _('Internal'), 'domain': [('shipping_type','=','internal')], 'sequence': 5},
            '06_other': {'label': _('Other'), 'domain': [('shipping_type','=','other')], 'sequence': 6},
            '07_underway': {'label': _('En route'), 'domain': [('state','=','underway')], 'sequence': 7},
            '08_received': {'label': _('Received'), 'domain': [('state','=','received')], 'sequence': 8},
            '09_cancel': {'label': _('Cancelled'), 'domain': [('state','=','cancel')], 'sequence': 9},
        }
        
        searchbar_sortings = self._get_searchbar_sortings()
        searchbar_inputs = self._get_searchbar_inputs()
        searchbar_groupby = self._get_searchbar_groupby()
        
        # extends filterby criteria with users access to
#         projects = request.env['project.project'].search([])
#         for project in projects:
#             searchbar_filters.update({
#                 str(project.id): {'label': project.name, 'domain': [('project_id', '=', project.id)]}
#             })
            
        # extends filterby criteria with project (criteria name is the project id)
        # Note: portal users can't view projects they don't follow
#         project_groups = request.env['project.task'].read_group([('project_id', 'not in', projects.ids)],
#                                                                 ['project_id'], ['project_id'])
#         for group in project_groups:
#             proj_id = group['project_id'][0] if group['project_id'] else False
#             proj_name = group['project_id'][1] if group['project_id'] else _('Others')
#             searchbar_filters.update({
#                 str(proj_id): {'label': proj_name, 'domain': [('project_id', '=', proj_id)]}
#             })
        
        # default sortby order
        if not sortby:
            sortby = 'create_date'
        sort_order = searchbar_sortings[sortby]['order']
        
        # default filter by value
        if not filterby:
            filterby = '01_all'
        domain = searchbar_filters.get(filterby, searchbar_filters.get('all'))['domain']
        
        # default group by value
#         if not groupby:
#             groupby = 'none'
            
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
            
         # search
        if search and search_in:
            domain += self._get_search_domain(search_in, search)

        # count for pager
        shipment_count = Orders.search_count(domain)
        
        # make pager
        pager = portal_pager(
            url="/my/shipments",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby, 'groupby': groupby, 'search_in': search_in, 'search': search},
            total=shipment_count,
            page=page,
            step=self._items_per_page
        )
        
        # search the count to display, according to the pager data
        shipments = Orders.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        
        request.session['my_shipments_history'] = shipments.ids[:100]
        
#         groupby_mapping = self._get_groupby_mapping()
#         group = groupby_mapping.get(groupby)
#         if group:
#             grouped_records = [Task.concat(*g) for k, g in groupbyelem(tasks, itemgetter(group))]
#         else:
#             grouped_records = [tasks]


        values.update({
            
            'date': date_begin,
            'date_end': date_end,
            'shipments': shipments.sudo(),
            'page_name': 'shipment',
            'pager': pager,
            'default_url': '/my/shipments',
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
        
        return request.render("mto_ic.portal_my_shipments", values)
    

    @http.route(['/my/shipments/<int:order_id>'], type='http', auth="public", website=True)
    def portal_shipment_page(self, order_id, report_type=None, access_token=None, message=False, download=False, **kw):
        
        try:
            
            order_sudo = self._document_check_access('shipping.order', order_id, access_token=access_token)
            
        except (AccessError, MissingError):
            
            return request.redirect('/my')        

        if report_type in ('html', 'pdf', 'text'):
            
            return self._show_report(model=order_sudo, report_type=report_type, report_ref='mto_ic.action_report_shippingorder', download=download)

        # use sudo to allow accessing/viewing orders for public user
        # only if he knows the private token
        # Log only once a day
        if order_sudo:
            # store the date as a string in the session to allow serialization
            now = fields.Date.today().isoformat()
            session_obj_date = request.session.get('view_quote_%s' % order_sudo.id)
            if session_obj_date != now and request.env.user.share and access_token:
                request.session['view_quote_%s' % order_sudo.id] = now
                body = _('Shipment viewed by customer %s', order_sudo.partner_id.name)
                _message_post_helper(
                    "shipping.order",
                    order_sudo.id,
                    body,
                    token=order_sudo.access_token,
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                    partner_ids=order_sudo.user_id.sudo().partner_id.ids,
                )

        values = {
            'shipping_order': order_sudo,
            'message': message,
            'token': access_token,
            'landing_route': '/shop/payment/validate',
            'bootstrap_formatting': True,
            'partner_id': order_sudo.partner_id.id,
            'report_type': 'html',
            'action': order_sudo._get_portal_return_action(),
        }
        
        if order_sudo.company_id:
            values['res_company'] = order_sudo.company_id

        # Payment values
        if order_sudo.has_to_be_paid():
            logged_in = not request.env.user._is_public()
            acquirers_sudo = request.env['payment.acquirer'].sudo()._get_compatible_acquirers(
                order_sudo.company_id.id,
                order_sudo.partner_id.id,
                currency_id=order_sudo.currency_id.id,
                sale_order_id=order_sudo.id,
            )  # In sudo mode to read the fields of acquirers and partner (if not logged in)
            tokens = request.env['payment.token'].search([
                ('acquirer_id', 'in', acquirers_sudo.ids),
                ('partner_id', '=', order_sudo.partner_id.id)
            ]) if logged_in else request.env['payment.token']
            fees_by_acquirer = {
                acquirer: acquirer._compute_fees(
                    order_sudo.amount_total,
                    order_sudo.currency_id,
                    order_sudo.partner_id.country_id,
                ) for acquirer in acquirers_sudo.filtered('fees_active')
            }
            # Prevent public partner from saving payment methods but force it for logged in partners
            # buying subscription products
            show_tokenize_input = logged_in \
                and not request.env['payment.acquirer'].sudo()._is_tokenization_required(
                    sale_order_id=order_sudo.id
                )
            values.update({
                'acquirers': acquirers_sudo,
                'tokens': tokens,
                'fees_by_acquirer': fees_by_acquirer,
                'show_tokenize_input': show_tokenize_input,
                'amount': order_sudo.amount_total,
                'currency': order_sudo.pricelist_id.currency_id,
                'partner_id': order_sudo.partner_id.id,
                'access_token': order_sudo.access_token,
                'transaction_route': order_sudo.get_portal_url(suffix='/transaction'),
                'landing_route': order_sudo.get_portal_url(),
            })

        if order_sudo.state in ('draft', 'sent', 'cancel'):
            history = request.session.get('my_quotations_history', [])
        else:
            history = request.session.get('my_orders_history', [])
            
        values.update(get_records_pager(history, order_sudo))

        return request.render('sale.sale_order_portal_template', values)
    
    searchbar_sortings = {
            
            'create_date': {'label': _('Created'), 'order': 'create_date desc'},
            'shipped': {'label': _('Shipped'), 'order': 'shipped desc'},
            'received': {'label': _('Received'), 'order': 'received desc'},
            'eta': {'label': _('ETA'), 'order': 'eta desc'},
            'etd': {'label': _('ETD'), 'order': 'etd desc'},
            'ett': {'label': _('ETT'), 'order': 'ett desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'state': {'label': _('Status'), 'order': 'state'},
            
        }
        
    
    def _get_searchbar_sortings(self):
        
        return {
            
            'create_date': {'label': _('Created'), 'order': 'create_date desc', 'sequence': 1},
            'shipped': {'label': _('Shipped'), 'order': 'shipped desc', 'sequence': 2},
            'received': {'label': _('Received'), 'order': 'received desc', 'sequence': 3},
            'eta': {'label': _('ETA'), 'order': 'eta desc', 'sequence': 4},
            'etd': {'label': _('ETD'), 'order': 'etd desc', 'sequence': 5},
            'ett': {'label': _('ETT'), 'order': 'ett desc', 'sequence': 6},
            'name': {'label': _('Reference'), 'order': 'name', 'sequence': 7},
            'state': {'label': _('Status'), 'order': 'state', 'sequence': 8},
            
        }

    def _get_searchbar_groupby(self):
        
        values = {
            'none': {'input': 'none', 'label': _('None'), 'order': 1},
            'trackingnumber': {'input': 'trackingnumber', 'label': _('Trackingnumber'), 'order': 2},
            'user': {'input': 'user', 'label': _('User'), 'order': 3},
            'container': {'input': 'container', 'label': _('Container'), 'order': 4},
            'origin': {'input': 'origin', 'label': _('Origin'), 'order': 5},
            'destination': {'input': 'destination', 'label': _('Destination'), 'order': 6},
            'shippingcompany': {'input': 'shippingcompany', 'label': _('Shipping Company'), 'order': 7},
            'type': {'input': 'type', 'label': _('Type'), 'order': 8},
            'state': {'input': 'state', 'label': _('Status'), 'order': 9},
        }
        
        return dict(sorted(values.items(), key=lambda item: item[1]["order"]))
   
    def _get_groupby_mapping(self):
        
        return {
            
            'trackingnumber': 'trackingnumber',
            'user': 'user_id',
            'container': 'container_id',
            'origin_id': 'origin_id',
            'destination': 'destination_id',
            'shippingcompany': 'shipping_company_id',
            'type': 'shipping_type',
            'state': 'state',
            
        }
    
    def _get_searchbar_inputs(self):
        
        values = {
            'all': {'input': 'all', 'label': _('Search in All'), 'order': 1},
            'content': {'input': 'content', 'label': Markup(_('Search <span class="nolabel"> (in Content)</span>')), 'order': 2},
            'name': {'input': 'name', 'label': _('Search in Ref'), 'order': 3},
            'trackingnumber': {'input': 'trackingnumber', 'label': _('Search in Trackingnumber'), 'order': 4},
            'container': {'input': 'container', 'label': _('Search in Container'), 'order': 5},
            'state': {'input': 'state', 'label': _('Search in Status'), 'order': 6},
            'users': {'input': 'users', 'label': _('Search in Users'), 'order': 7},
            'origin': {'input': 'origin', 'label': _('Search in Origin'), 'order': 8},
            'destination': {'input': 'destination', 'label': _('Search in Destination'), 'order': 8},
            'shippingcompany': {'input': 'shippingcompany', 'label': _('Search in Shipping Company'), 'order': 9},
            'type': {'input': 'type', 'label': _('Search in Type'), 'order': 10},
            'message': {'input': 'message', 'label': _('Search in Messages'), 'order': 11},
        }
        
        return dict(sorted(values.items(), key=lambda item: item[1]["order"]))

    def _get_search_domain(self, search_in, search):
        search_domain = []
        if search_in in ('content', 'all'):
            search_domain.append([('name', 'ilike', search)])
        if search_in in ('message', 'all'):
            search_domain.append([('message_ids.body', 'ilike', search)])
        if search_in in ('state', 'all'):
            search_domain.append([('state', 'ilike', search)])
        if search_in in ('name', 'all'):
            search_domain.append([('name', 'ilike', search)])
        if search_in in ('origin', 'all'):
            search_domain.append([('origin_id', 'ilike', search)])
        if search_in in ('destination', 'all'):
            search_domain.append([('destination_id', 'ilike', search)])
        if search_in in ('shippingcompany', 'all'):
            search_domain.append([('shipping_company_id', 'ilike', search)])
        if search_in in ('type', 'all'):
            search_domain.append([('shipping_type', 'ilike', search)])
        if search_in in ('container', 'all'):
            search_domain.append([('container', 'ilike', search)])
        if search_in in ('trackingnumber', 'all'):
            search_domain.append([('trackingnumber', 'ilike', search)])
        if search_in in ('users', 'all'):
            user_ids = request.env['res.users'].sudo().search([('name', 'ilike', search)])
            search_domain.append([('user_ids', 'in', user_ids.ids)])
       
        return OR(search_domain)

    