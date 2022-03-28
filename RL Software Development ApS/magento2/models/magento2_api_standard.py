from odoo import api, fields, models
from openerp.exceptions import ValidationError, UserError
import requests
import json


class Magento2ApiStandard(models.Model):
    
    _name = 'magento2.api.standard'
    _description = 'Magento2 API Standard'
    _order = 'id'
    _check_company_auto = True

    name = fields.Char(required=False,string='Name')
    login_id = fields.Many2one('magento2.login', 'Login', required=True)
    store_ids = fields.Many2many(comodel_name = 'magento2.store', relation="magento2_api_standard_magento2_store_rel", column1="magento2_api_calls_id", column2="magento2_store_id", string='Stores', required=True)
    datatable_id = fields.Many2one('magento2.datatable', 'Datatable', required=True)
    action_type = fields.Selection([('PUT', 'PUT'),('PUT_BULK', 'PUT/BULK'),('GET', 'GET'),('POST', 'POST'),('DELETE', 'DELETE')], 'Action', required=True, default='GET') 
    body = fields.Text(required=False,string='Body')
    fields_text = fields.Char(required=False,string='Fields')
    search_text = fields.Char(required=False,string='Search')
    state = fields.Selection([('new', 'New'),('failed', 'Failed'),('success', 'Success')], 'State', required=True, default='new')   
    active = fields.Boolean(required=True, string='Active', default=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
   