# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    ms_form_recognizer_subscription_key = fields.Char(required=False,string='Ocp-Apim-Subscription-Key',help="MS Form Recognizer Subscription key")
    ms_form_recognizer_endpoint = fields.Char(required=False,string='End point',help="MS Form Recognizer Endpoint")
   
class ResConfigSettings(models.TransientModel):

    _inherit = ['res.config.settings']
    
    ms_form_recognizer_subscription_key = fields.Char(required=False,related='company_id.ms_form_recognizer_subscription_key', readonly=False)
    ms_form_recognizer_endpoint = fields.Char(required=False,related='company_id.ms_form_recognizer_endpoint', readonly=False)