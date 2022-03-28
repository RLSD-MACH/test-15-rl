# -*- coding: utf-8 -*-

import binascii

from odoo import fields, http, _
# from odoo.exceptions import AccessError, MissingError
from odoo.http import request
# from odoo.addons.payment.controllers import portal as payment_portal
# from odoo.addons.payment import utils as payment_utils
# from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager, get_records_pager
# from odoo.osv import expression
from odoo.osv.expression import OR
from odoo.exceptions import AccessError, UserError, ValidationError

class CustomerPortal(portal.CustomerPortal):
	  
    @http.route()    
    def portal_my_quotes(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='all', groupby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']

        if request.env.user.share:

            domain = [
                ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
                ('state', 'in', ['sent', 'cancel'])
            ]

        else:

            domain = [
                ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
                # ('state', 'in', ['sent', 'cancel'])
            ]


        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'commitment_date': {'label': _('Delivery Date'), 'order': 'commitment_date desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'client_order_ref': {'label': _('Customer ref.'), 'order': 'client_order_ref'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }
       
        searchbar_inputs = {
            'name': {'input': 'name', 'label': _('Search in Reference')},
            'client_order_ref': {'input': 'client_order_ref', 'label': _('Search in Customer ref.')},            
            # 'date': {'input': 'date', 'label': _('Search in Order Date')},
            # 'commitment_date': {'input': 'commitment_date', 'label': _('Search in Delivery Date')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # search
        if search and search_in:
            search_domain = []            
            if search_in in ('name', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            if search_in in ('client_order_ref', 'all'):
                search_domain = OR([search_domain, [('client_order_ref', 'ilike', search)]])
            # if search_in in ('date', 'all'):
            #     search_domain = OR([search_domain, [('date.strftime("%Y-%m-%d")', 'ilike', search)]])
            # if search_in in ('commitment_date', 'all'):
            #     search_domain = OR([search_domain, [('commitment_date.strftime("%Y-%m-%d")', 'ilike', search)]])
            domain += search_domain

        # count for pager
        quotation_count = SaleOrder.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/quotes",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby, 'groupby': groupby, 'search_in': search_in, 'search': search},
            total=quotation_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        quotations = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_quotations_history'] = quotations.ids[:100]

        values.update({
            'date': date_begin,
            'quotations': quotations.sudo(),
            'page_name': 'quote',
            'pager': pager,
            'default_url': '/my/quotes',
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'filterby': filterby,
        })
        return request.render("sale.portal_my_quotations", values)

    @http.route(['/my/orders', '/my/orders/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_orders(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='all', groupby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']

        if request.env.user.share:

            domain = [
                ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
                ('state', 'in', ['sale', 'done'])
            ]

        else:

            domain = [
                ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
                # ('state', 'in', ['sale', 'done'])
            ]

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'commitment_date': {'label': _('Delivery Date'), 'order': 'commitment_date desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'client_order_ref': {'label': _('Customer ref.'), 'order': 'client_order_ref'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }
       
        searchbar_inputs = {
            'name': {'input': 'name', 'label': _('Search in Reference')},
            'client_order_ref': {'input': 'client_order_ref', 'label': _('Search in Customer ref.')},            
            # 'date': {'input': 'date', 'label': _('Search in Order Date')},
            # 'commitment_date': {'input': 'commitment_date', 'label': _('Search in Delivery Date')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # search
        if search and search_in:
            search_domain = []            
            if search_in in ('name', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            if search_in in ('client_order_ref', 'all'):
                search_domain = OR([search_domain, [('client_order_ref', 'ilike', search)]])
            # if search_in in ('date', 'all'):
            #     search_domain = OR([search_domain, [('date.strftime("%Y-%m-%d")', 'ilike', search)]])
            # if search_in in ('commitment_date', 'all'):
            #     search_domain = OR([search_domain, [('commitment_date.strftime("%Y-%m-%d")', 'ilike', search)]])
            domain += search_domain

        # count for pager
        order_count = SaleOrder.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/orders",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby, 'groupby': groupby, 'search_in': search_in, 'search': search},
            total=order_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager
        orders = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_orders_history'] = orders.ids[:100]

        values.update({
            'date': date_begin,
            'orders': orders.sudo(),
            'page_name': 'order',
            'pager': pager,
            'default_url': '/my/orders',
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'filterby': filterby,
        })

        return request.render("sale.portal_my_orders", values)
