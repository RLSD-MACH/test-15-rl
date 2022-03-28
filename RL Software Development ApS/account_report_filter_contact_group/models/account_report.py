# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class AccountReportInherit(models.AbstractModel):

    _inherit = "account.report"

    filter_contact_groups = None

    @api.model
    def _init_filter_partner(self, options, previous_options=None):
        
        res = super(AccountReportInherit, self)._init_filter_partner(options, previous_options)
        
        if not self.filter_contact_groups:           
            return

        previous_contact_groups = (previous_options or {}).get('contact_groups', [])  
        
        if str(previous_contact_groups).startswith("res.partner.group(") == True:
            
            selected_contact_groups = None
            options['selected_contact_groups_names'] = None

        else:
        
            contact_groups_ids = [int(x.get('id') if x.get('id') != 'zero' else 0) for x in previous_contact_groups if x.get('selected') == True]
            selected_contact_groups = self.env['res.partner.group'].search([('id', 'in', contact_groups_ids)])
            
            values = selected_contact_groups.mapped('name')
            not_set = False
            
            if 0 in contact_groups_ids:
                not_set = True
                values +=['Not set']
                                
            options['selected_contact_groups_names'] = values
                                  
        options['contact_groups'] = self._get_filter_contact_groups(selected_contact_groups, not_set)

    def _get_filter_contact_groups(self, selected_contact_groups, not_set=False):

        exists =  self.env['res.partner.group'].with_context(active_test=False).search([
            '|',('company_id', 'in', self.env.user.company_ids.ids or [self.env.company.id]), ('company_id', '=', False)
        ], order="company_id, name")

        list = []

        list.append({

            'id': 'zero',
            'name': "Not set",
            'selected': not_set

        })

        for value in exists:

            list.append(
                {

                    'id': value.id,
                    'name': value.name,
                    'selected': True if value in selected_contact_groups else False

                }
            )
          
        return list

    @api.model
    def _get_options_partner_domain(self, options):

        domain = super(AccountReportInherit, self)._get_options_partner_domain(options)

        if options.get('contact_groups'):           
            
            account_position_ids = [int(acc.get('id') if acc.get('id') != 'zero' else False) for acc in options['contact_groups'] if acc.get('selected') == True]

            if len(account_position_ids) > 0:
                                    
                domain.append(('partner_id.group_id', 'in', account_position_ids))

        return domain


class ReportAccountAgedPartnerInherit(models.AbstractModel):
    
    _inherit = 'account.accounting.report'
   
    filter_contact_groups = True
    
class ReportPartnerLedgerInherit(models.AbstractModel):
    
    _inherit = 'account.partner.ledger'
   
    filter_contact_groups = True

