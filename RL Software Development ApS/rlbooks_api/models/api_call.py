from odoo import api, fields, models

class APICall(models.Model):
    
    _name = 'api.call'
    _description = 'API call'
    _order = 'id desc'
    _check_company_auto = True

    action = fields.Char(string='Action', required=False, readonly=True)    
    status_code = fields.Integer(string='Status code', required=False, readonly=True, help='')
    type = fields.Char(string='Type', required=False, readonly=True)   
    value = fields.Text(string='Value', required=False, readonly=True, help='')

    active = fields.Boolean(string='Active', required=True, readonly=True, default=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
   