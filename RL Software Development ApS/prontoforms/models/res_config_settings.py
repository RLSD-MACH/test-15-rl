# -*- coding: utf-8 -*-

from odoo import api, fields, models
import base64

class ResCompany(models.Model):
    _inherit = 'res.company'

    prontoforms_api_key = fields.Char(required=False,string='API key',help="Prontoforms API key")
    prontoforms_api_secret = fields.Char(required=False,string='API Secret',help="Prontoforms API Secret")

    def _return_prontoform_headers(self):

        userpass = self.prontoforms_api_key + ':' + self.prontoforms_api_secret
        base64authorization = base64.b64encode(userpass.encode()).decode()

        headers = {

            'authorization': "Basic %s" % base64authorization,
            'content-type': "application/json; charset=utf-8",
            'cache-control': "no-cache",
            }

        return headers
   
class ResConfigSettings(models.TransientModel):

    _inherit = ['res.config.settings']
    
    prontoforms_api_key = fields.Char(required=False,related='company_id.prontoforms_api_key', readonly=False)
    prontoforms_api_secret = fields.Char(required=False,related='company_id.prontoforms_api_secret', readonly=False)