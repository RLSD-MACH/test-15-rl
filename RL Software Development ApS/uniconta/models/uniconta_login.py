from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError
import requests
import json


class UnicontaLogin(models.Model):
    
    _name = 'uniconta.login'
    _description = 'Uniconta login'
    _order = 'id'
    _check_company_auto = True

    name = fields.Char(required=False,string='Name')
    password = fields.Char(required=True,string='Password') 
    company_number = fields.Char(required=True,string='Company ID')   
    error = fields.Html('Error')
    active = fields.Boolean(required=True, string='Active', default=True)

    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
   

    def action_get_firms(self):
                   
        for row in self:

            action_type = "" #Read, Insert, Delete, Update
            model_id = "CompanyClient"
            CompanyID = row.company_number
            search = ""

            if len(CompanyID) < 7:

                for x in range(7 - len(CompanyID)):

                    CompanyID = "0" + CompanyID

            
            system_username = CompanyID + "/" + row.name

            url = 'https://odata.uniconta.com/api/Entities/'

            if action_type != '':

                url = url + action_type + '/' 

            url = url + model_id 

            if search != '':

                url = url + "?" + search  
                
            self.env['api.call'].create({
                            'status_code': 0,
                            'value': "Request url: " + str(url) + " | " + str((system_username)),
                            'action': 'Uniconta'
                        })

            response = requests.get(url, auth=(system_username, row.password))
            
            self.env['api.call'].create({
                    'status_code': response.status_code,
                    'value': str(response.content),
                    'action': 'Uniconta'
                })

            if response.status_code == 200:

                self.error = False
                
                object_response = json.loads(response.content)
                
                for row in object_response:
                
                    exists_firms = self.env['uniconta.firm'].search([['primary_key_id','=',row.get('PrimaryKeyId','')]])
                
                    if len(exists_firms) == 0:
                        
                        self.env['uniconta.firm'].create({
                            'name': row.get('CompanyName',''),
                            'primary_key_id': row.get('PrimaryKeyId',''),
                            'active': 1
                        })  

                return {

                    'type': 'ir.actions.act_window',
                    'name': 'Firms',
                    'view_type': 'form',
                    'view_mode': 'tree',
                    'res_model': 'uniconta.firm',
                    'search_view_id': self.env.ref('uniconta.uniconta_api_call_tree').id,
                    # 'context': "{}",
                    # 'target': 'current',

                }    

            else:

                self.error = response.content

                return {
                    'warning':{
                        'title': "ERROR",
                        'message': "An error accured during the login process. Please see refer to the Errormessage on the login-form.",
                    },
                }                             
        
    