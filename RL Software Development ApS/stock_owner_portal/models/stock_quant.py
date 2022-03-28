# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, UserError
from odoo.http import content_disposition, Controller, request, route
import re

class StockQuantInherit(models.Model):
    
    _name = 'stock.quant'
    _inherit = ['stock.quant','portal.mixin']
        
    def _compute_access_url(self):

        super(StockQuantInherit, self)._compute_access_url()

        for quant in self:
            quant.access_url = '/my/stock/%s' % (quant.id)

    # def _get_portal_return_action(self):
    #     """ Return the action used to display statements when returning from customer portal. """
    #     self.ensure_one()
    #     return self.env.ref('stock_owner_portal.action_stock_with_onboarding')
      
    def preview_online(self):
        
        self.ensure_one()

        return {

            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
            
        }   
   