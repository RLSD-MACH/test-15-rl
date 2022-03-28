# -*- coding: utf-8 -*-

from odoo.addons.portal.controllers.portal import CustomerPortal

class PartnerStatementPortal(CustomerPortal):
    
    def _get_default_domain(self, partner):

        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('is_published', '=', True)
        ]

        return domain