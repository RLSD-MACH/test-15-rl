from odoo import api, fields, models


class ClearhausToken(models.Model):
    
    _name = 'clearhaus.token'
    _description = 'Clearhaus token'
    _order = 'id'
    _check_company_auto = True
    
    token = fields.Char(required=True,string='Token')
    login_id = fields.Many2one("clearhaus.login", string='Login ID', ondelete='cascade', required=False) 
    expires = fields.Datetime(required=True,string='Expires',readonly=True)
    active = fields.Boolean(required=True, string='Active', default=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
   