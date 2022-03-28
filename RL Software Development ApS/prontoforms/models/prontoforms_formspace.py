from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
import requests
import json


class ProntoformsFormspace(models.Model):
    
    _name = 'prontoforms.formspace'
    _description = 'Prontoforms Formspaces'
    _order = 'identifier desc'
    _check_company_auto = True

    identifier = fields.Float(required=False, string='Identifier')    
    name = fields.Char(required=False, string='Username')
    problemContactEmail = fields.Char(required=False, string='Problem Contact Email')
    pushUpdatesToDevices = fields.Boolean(required=False, string='Push Updates To Devices')
    forms_ids = fields.One2many('prontoforms.form', 'formspace_id', string='Forms')
    active = fields.Boolean(required=True, string='Active', default=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    
    def action_refresh_list(self):
               
        url = "https://api.prontoforms.com/api/1.1/formspaces"

        headers = self.env.company._return_prontoform_headers()
        
        response = requests.request("GET", url, headers=headers)

        if response.status_code == 200:

            content = response.json()

            if "pageData" in content:

                for item in content.get("pageData", False):
                    
                    object = {}

                    for data in [('identifier','identifier'),('name','name'),('email','email'),('problemContactEmail','problemContactEmail'),('pushUpdatesToDevices','pushUpdatesToDevices')]:
        
                        if data[0] in item:
                            
                            object[data[1]] =  item[data[0]]

                    exsting = self.env['prontoforms.formspace'].search([['identifier','=', object['identifier'] ]])

                    if len(exsting) == 0:

                        new_record = self.env['prontoforms.formspace'].create(object)

                    else:

                        for rec in exsting:

                            rec.update(object)


            else:

                raise UserError("Couldn't find pageData in content?! \\n" + str(content))

        else:

            raise UserError(str(response) + " | " + str(response.status_code))
    

    def action_get_forms(self):
               
        url = "https://api.prontoforms.com/api/1.1/formspaces/%s/forms" % (str(int(self.identifier)))

        headers = self.env.company._return_prontoform_headers()
        
        response = requests.request("GET", url, headers=headers)

        if response.status_code == 200:

            content = response.json()

            if "pageData" in content:

                for item in content.get("pageData", False):
                    
                    object = {}

                    object["formspace_id"] = self.id

                    for data in [('identifier','identifier'),('asyncStatus','asyncStatus'),('name','name'),('description','description'),('state','state'),('locked','locked')]:
        
                        if data[0] in item:
                            
                            object[data[1]] =  item[data[0]]

                    exsting = self.env['prontoforms.form'].search([['identifier','=', object['identifier'] ]])

                    if len(exsting) == 0:

                        new_record = self.env['prontoforms.form'].create(object)

                    else:

                        for rec in exsting:

                            rec.update(object)

            else:

                raise UserError("Couldn't find pageData in content?! \\n" + str(content))

        else:

            raise UserError(str(response) + " | " + str(response.status_code) + " | " + url)