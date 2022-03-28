from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError
import requests
import json


class Magento2Login(models.Model):
    
    _name = 'magento2.login'
    _description = 'Magento2 login'
    _order = 'id'
    _check_company_auto = True

    name = fields.Char(required=False,string='Name')
    password = fields.Char(required=True,string='Password') 
    access_token = fields.Char(required=True,string='Access Token') 
    access_token_secret = fields.Char(required=True,string='Access Token Secret') 
    consumer_key = fields.Char(required=True,string='Consumer Key') 
    consumer_secret = fields.Char(required=True,string='Consumer Secret') 
    url = fields.Char(required=True,string='Url')     
    active = fields.Boolean(required=True, string='Active', default=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
   