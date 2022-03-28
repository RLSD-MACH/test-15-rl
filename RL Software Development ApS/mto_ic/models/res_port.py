from datetime import datetime, timedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.osv import expression

class ResPort(models.Model):
    
    _name = 'res.port'
    _description = 'Port'
    _order = 'name asc'

    name = fields.Char(required=True, string='Name')
    country_id = fields.Many2one('res.country', string='Country', required=True,)
    active = fields.Boolean(required=True, string='Active', default=True, copy=False)  
   
