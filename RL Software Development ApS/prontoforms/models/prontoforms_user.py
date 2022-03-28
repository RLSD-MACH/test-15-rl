from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
import requests
import json


class ProntoformsUser(models.Model):
    
    _name = 'prontoforms.user'
    _description = 'Prontoforms Users'
    _order = 'identifier desc'
    _check_company_auto = True

    user_id = fields.Many2one('res.users', string='User in Odoo')
    identifier = fields.Float(required=False, string='Identifier')    
    name = fields.Char(required=False, string='Username')
    email = fields.Char(required=False, string='Email')
    first_name = fields.Char(required=False, string='First name')
    last_name = fields.Char(required=False, string='Last name') 
    active = fields.Boolean(required=True, string='Active', default=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    
    def action_refresh_list(self):
               
        url = "https://api.prontoforms.com/api/1.1/users"

        headers = self.env.company._return_prontoform_headers()
        
        response = requests.request("GET", url, headers=headers)

        if response.status_code == 200:

            content = response.json()

            if "pageData" in content:

                for item in content.get("pageData", False):
                    
                    object = {}

                    for data in [('identifier','identifier'),('username','name'),('email','email'),('firstName','first_name'),('lastName','last_name')]:
        
                        if data[0] in item:
                            
                            object[data[1]] =  item[data[0]]

                    exsting = self.env['prontoforms.user'].search([['identifier','=', object['identifier'] ]])

                    if len(exsting) == 0:

                        new_record = self.env['prontoforms.user'].create(object)

                    else:

                        for rec in exsting:

                            rec.update(object)

            else:

                raise UserError("Couldn't find pageData in content?! \\n" + str(content))

        else:

            raise UserError(str(response) + " | " + str(response.status_code))
    