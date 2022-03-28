# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.exceptions import AccessError, UserError, ValidationError
import requests
import base64
import json
from datetime import datetime, timedelta, date

class ContactsInherit(models.Model):
    
    _inherit = 'res.partner'

    def control_vat_on_cvr_then_vies(self):
        
        for partner in self:
            
            controlled_vat = False

            if partner.vat:

                if self.env.company.country_id.with_context(lang='en_US').name == 'Denmark':

                    if len(partner.vat) in [8,10]:

                        if partner.country_id.with_context(lang='en_US').name == 'Denmark' or not partner.country_id.id:

                            values = partner.control_vat_on_cvr(silent = True, vat_obj = partner.vat)
                            
                            partner.update(values)

                            controlled_vat = True
            
            if not controlled_vat:

                partner.control_vat_on_vies(silent=True)

                controlled_vat = True

  
    # @api.model
    # def create(self, vals):

    #     res = super(ContactsInherit, self).create(vals)

    #     for record in res:

    #         if record.vat:

    #             record.control_vat_on_cvr(silent=True)
                    
    #     return res
        
    # def write(self, data):
    #     res = super(ContactsInherit, self).write(data)
        
    #     if 'vat' in data:

    #         auto = self.env.company.cvr_run_auto_contacts

    #         self.update({
                
    #             'last_cvr_message_id': False

    #         })     

    #         if auto:

    #             self.control_vat_on_cvr(silent=True)


    #     return res
    
    
    @api.onchange('vat')
    def _onchange_vat(self):

        self._control_existing_values_vat()

    def _create_control_vies(self):

        self._control_existing_values_vat()

    def _write_control_vies(self, data):
        
        controlled_vat = False

        if data.get('vat', False):

            if self.env.company.country_id.with_context(lang='en_US').name == 'Denmark':

                if len(data['vat']) in [8,10]:

                    country = False

                    if 'country_id' in data:

                        if data['country_id'] == False:

                            controlled_vat = True
                        
                        else:

                            country = self.env['res.country'].with_context(lang='en_US').browse(data['country_id'])

                            if country.name == 'Denmark':

                                controlled_vat = True
                    
                    else:

                        if self.country_id.name == 'Denmark' or self.country_id.id == False:

                            controlled_vat = True
            
            if not controlled_vat:
                
                data = super(ContactsInherit, self)._write_control_vies(data)
        
        return data          
    
    def _which_control_method(self):

        method = False

        if self.vat:

            if self.env.company.country_id.with_context(lang='en_US').name == 'Denmark':

                if len(self.vat) in [8,10]:

                    if self.country_id.with_context(lang='en_US').name == 'Denmark' or not self.country_id.id:

                        method = "cvr"
        
        if not method:

            method = "vies"

        return method

    def _control_existing_values_vat(self):

        context = self.env.context

        if context.get('ignore_control_vat', False) == False:

            for partner in self:

                method = partner._which_control_method()

                if method == "cvr":
                    
                    values = partner.control_vat_on_cvr(silent = True, vat_obj = partner.vat)
                    
                    if values != None:

                        partner.update(values)

                elif method == "vies":
                    
                    partner.control_vat_on_vies(silent=True) 