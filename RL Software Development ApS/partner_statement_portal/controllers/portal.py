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

from odoo.exceptions import AccessError, MissingError
from collections import OrderedDict
from odoo.http import request

class PartnerStatementPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        Orders = request.env['rlbooks_statement.report.print']
        
        domain = self._get_default_domain(partner)

        if 'statements_count' in counters:
            
            values['statements_count'] = Orders.search_count(domain) if Orders.check_access_rights('read', raise_exception=False) else 0

        return values
   
    @http.route(['/my/statements', '/my/statements/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_statements(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='all', groupby=None, **kw):
        
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        
        Orders = request.env['rlbooks_statement.report.print']

        domain = self._get_default_domain(partner)
        
        searchbar_filters = {
            '01_all': {'label': _('All'), 'domain': [], 'sequence': 1},
            # '02_plain': {'label': _('Air'), 'domain': [('shipping_type','=','plain')], 'sequence': 2},
            # '03_ship': {'label': _('Sea'), 'domain': [('shipping_type','=','ship')], 'sequence': 3},
            # '04_truck': {'label': _('Land'), 'domain': [('shipping_type','=','truck')], 'sequence': 4},
            # '05_internal': {'label': _('Internal'), 'domain': [('shipping_type','=','internal')], 'sequence': 5},
            # '06_other': {'label': _('Other'), 'domain': [('shipping_type','=','other')], 'sequence': 6},
            # '07_underway': {'label': _('En route'), 'domain': [('state','=','underway')], 'sequence': 7},
            # '08_received': {'label': _('Received'), 'domain': [('state','=','received')], 'sequence': 8},
            # '09_cancel': {'label': _('Cancelled'), 'domain': [('state','=','cancel')], 'sequence': 9},
        }
        
        searchbar_sortings = self._get_searchbar_sortings_statements()
        searchbar_inputs = self._get_searchbar_inputs_statements()
        searchbar_groupby = self._get_searchbar_groupby_statements()
        
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
        domain += searchbar_filters.get(filterby, searchbar_filters.get('all'))['domain']
        
        # default group by value
#         if not groupby:
#             groupby = 'none'

        #Filter all by this
        # domain += [('is_published', '=', True), ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id])]

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
            
         # search
        if search and search_in:
            domain += self._get_search_domain_statements(search_in, search)

        # count for pager
        statements_count = Orders.search_count(domain)
        
        # make pager
        pager = portal_pager(
            url="/my/statements",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby, 'groupby': groupby, 'search_in': search_in, 'search': search},
            total=statements_count,
            page=page,
            step=self._items_per_page
        )
        
        # search the count to display, according to the pager data
        statements = Orders.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        
        request.session['my_statements_history'] = statements.ids[:100]
        
#         groupby_mapping = self._get_groupby_mapping_statements()
#         group = groupby_mapping.get(groupby)
#         if group:
#             grouped_records = [Task.concat(*g) for k, g in groupbyelem(tasks, itemgetter(group))]
#         else:
#             grouped_records = [tasks]


        values.update({
            
            'date': date_begin,
            'date_end': date_end,
            'statements': statements.sudo(),
            'page_name': 'statement',
            'pager': pager,
            'default_url': '/my/statements',
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
        
        return request.render("partner_statement_portal.portal_my_statements", values)
    

    @http.route(['/my/statements/<int:order_id>'], type='http', auth="user", website=True)
    def portal_statement_page(self, order_id, report_type=None, access_token=None, message=False, download=False, **kw):
        
        try:
            
            order_sudo = self._document_check_access('rlbooks_statement.report.print', order_id, access_token=access_token)
            
        except (AccessError, MissingError):
            
            return request.redirect('/my')        

        if report_type in ['pdf']:

            return order_sudo._show_report_custome(model=order_sudo, report_type=report_type, report_ref='partner_statement_portal.action_report_statement', download=download, attachment=True)

        elif report_type in ('html', 'pdf', 'text'):
            
            return self._show_report(model=order_sudo, report_type=report_type, report_ref='partner_statement_portal.action_report_statement', download=download)

        elif report_type in ['main_attachment']:
            
            if order_sudo.message_main_attachment_id:
                            
                return  {

                        'name': 'Report',
                        'type': 'ir.actions.act_url',
                        'url': "web/content/?id=" + str(
                            order_sudo.message_main_attachment_id.id) + "&download=true",
                        'target': 'self',
                    }
             

        # use sudo to allow accessing/viewing orders for public user
        # only if he knows the private token
        # Log only once a day
        if order_sudo:
            # store the date as a string in the session to allow serialization
            now = fields.Date.today().isoformat()
            session_obj_date = request.session.get('view_quote_%s' % order_sudo.id)
            if session_obj_date != now and request.env.user.share and access_token:
                request.session['view_quote_%s' % order_sudo.id] = now
                body = _('Report viewed by customer %s', order_sudo.partner_id.name)
                _message_post_helper(
                    "rlbooks_statement.report.print",
                    order_sudo.id,
                    body,
                    token=order_sudo.access_token,
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                    partner_ids=order_sudo.message_partner_ids.ids, #user_id.sudo().partner_id
                )

        values = {
            'statement': order_sudo,
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
               
        history = request.session.get('my_statements_history', [])
            
        values.update(get_records_pager(history, order_sudo))

        return request.render('partner_statement_portal.portal_statement_page', values)
    
    searchbar_sortings = {
            
            'create_date': {'label': _('Created'), 'order': 'create_date desc'},
            # 'user_id': {'label': _('Responsible'), 'order': 'user_id desc'},
            'partner_id': {'label': _('Partner'), 'order': 'partner_id desc'},
            'start': {'label': _('Start'), 'order': 'date_start desc'},
            'end': {'label': _('End'), 'order': 'date_end desc'},
            # 'ett': {'label': _('ETT'), 'order': 'ett desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            # 'state': {'label': _('Status'), 'order': 'state'},
            
        }
        
    
    def _get_searchbar_sortings_statements(self):
        
        return {
            
            'create_date': {'label': _('Created'), 'order': 'create_date desc', 'sequence': 1},
            # 'user_id': {'label': _('Responsible'), 'order': 'user_id desc', 'sequence': 2},
            'partner_id': {'label': _('Partner'), 'order': 'partner_id desc', 'sequence': 3},
            'start': {'label': _('Start'), 'order': 'date_start desc', 'sequence': 4},
            'end': {'label': _('End'), 'order': 'date_end desc', 'sequence': 5},
            # 'ett': {'label': _('ETT'), 'order': 'ett desc', 'sequence': 6},
            'name': {'label': _('Reference'), 'order': 'name', 'sequence': 7},
            # 'state': {'label': _('Status'), 'order': 'state', 'sequence': 8},
            
        }

    def _get_searchbar_groupby_statements(self):
        
        values = {
            'none': {'input': 'none', 'label': _('None'), 'order': 1},
            'create_date': {'input': 'create_date', 'label': _('Created'), 'order': 2},
            # 'user': {'input': 'user', 'label': _('Responsible'), 'order': 3},
            'partner': {'input': 'partner', 'label': _('Partner'), 'order': 4},
            # 'origin': {'input': 'origin', 'label': _('Origin'), 'order': 5},
            # 'destination': {'input': 'destination', 'label': _('Destination'), 'order': 6},
            # 'shippingcompany': {'input': 'shippingcompany', 'label': _('Shipping Company'), 'order': 7},
            # 'type': {'input': 'type', 'label': _('Type'), 'order': 8},
            # 'state': {'input': 'state', 'label': _('Status'), 'order': 9},
        }
        
        return dict(sorted(values.items(), key=lambda item: item[1]["order"]))
   
    def _get_groupby_mapping_statements(self):
        
        return {
            
            'create_date': 'create_date',
            # 'user': 'user_id',
            'partner': 'partner_id',
            # 'origin_id': 'origin_id',
            # 'destination': 'destination_id',
            # 'shippingcompany': 'shipping_company_id',
            # 'type': 'shipping_type',
            # 'state': 'state',
            
        }
    
    def _get_searchbar_inputs_statements(self):
        
        values = {
            'all': {'input': 'all', 'label': _('Search in All'), 'order': 1},
            # 'content': {'input': 'content', 'label': Markup(_('Search <span class="nolabel"> (in Content)</span>')), 'order': 2},
            'name': {'input': 'name', 'label': _('Search in Ref'), 'order': 3},
            'partners': {'input': 'partners', 'label': _('Search in Partners'), 'order': 4},
            # 'container': {'input': 'container', 'label': _('Search in Container'), 'order': 5},
            # 'state': {'input': 'state', 'label': _('Search in Status'), 'order': 6},
            # 'users': {'input': 'users', 'label': _('Search in Users'), 'order': 7},
            # 'origin': {'input': 'origin', 'label': _('Search in Origin'), 'order': 8},
            # 'destination': {'input': 'destination', 'label': _('Search in Destination'), 'order': 8},
            # 'shippingcompany': {'input': 'shippingcompany', 'label': _('Search in Shipping Company'), 'order': 9},
            # 'type': {'input': 'type', 'label': _('Search in Type'), 'order': 10},
            'message': {'input': 'message', 'label': _('Search in Messages'), 'order': 11},
        }
        
        return dict(sorted(values.items(), key=lambda item: item[1]["order"]))

    def _get_search_domain_statements(self, search_in, search):
        search_domain = []
        if search_in in ('content', 'all'):
            search_domain.append([('name', 'ilike', search)])
        if search_in in ('message', 'all'):
            search_domain.append([('message_ids.body', 'ilike', search)])
        # if search_in in ('state', 'all'):
            # search_domain.append([('state', 'ilike', search)])
        if search_in in ('name', 'all'):
            search_domain.append([('name', 'ilike', search)])
        # if search_in in ('origin', 'all'):
        #     search_domain.append([('origin_id', 'ilike', search)])
        # if search_in in ('destination', 'all'):
        #     search_domain.append([('destination_id', 'ilike', search)])
        # if search_in in ('shippingcompany', 'all'):
        #     search_domain.append([('shipping_company_id', 'ilike', search)])
        # if search_in in ('type', 'all'):
        #     search_domain.append([('shipping_type', 'ilike', search)])
        # if search_in in ('container', 'all'):
        #     search_domain.append([('container', 'ilike', search)])
        if search_in in ('partners', 'all'):

            partner_ids = request.env['res.partner'].sudo().search([('name', 'ilike', search)])
            search_domain.append([('partner_id', 'in', partner_ids.ids)])
            
        # if search_in in ('users', 'all'):

        #     user_ids = request.env['res.users'].sudo().search([('name', 'ilike', search)])
        #     search_domain.append([('user_id', 'in', user_ids.ids)])
       
        return OR(search_domain)

    def _get_default_domain(self, partner):

        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            # ('is_published', '=', True)
        ]

        return domain