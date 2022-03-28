from datetime import datetime, timedelta

from odoo import api, fields, models,  _

class ResVessel(models.Model):
    
    _name = 'res.vessel'
    _description = 'Vessel'
    _order = 'name asc'

    name = fields.Char(required=True, string='Name')
    country_id = fields.Many2one('res.country', string='Country', required=False,)
    active = fields.Boolean(required=True, string='Active', default=True, copy=False)  
   
