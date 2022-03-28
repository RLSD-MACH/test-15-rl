# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.exceptions import AccessError, UserError, ValidationError

class ContactsInherit(models.Model):
    
    _inherit = 'res.partner'

    @api.constrains('vat', 'country_id')
    
    def check_vat(self):
        
        context = self.env.context

        if context.get('ignore_control_vat', False) == False:

            return super(ContactsInherit, self).check_vat()           