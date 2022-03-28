from odoo import api, fields, models
import requests
import json


class UnicontaApiCall(models.Model):
    
    _name = 'uniconta.datatable'
    _description = 'Uniconta Datatable'
    _order = 'id'
    # _check_company_auto = True

    name = fields.Char(required=False,string='Name')
    model_id = fields.Many2one('ir.model', 'Model', required=False)

    # company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
   

  
    