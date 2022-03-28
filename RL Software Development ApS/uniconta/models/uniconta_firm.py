from odoo import api, fields, models


class UnicontaFirm(models.Model):
    
    _name = 'uniconta.firm'
    _description = 'Uniconta Firm'
    _order = 'primary_key_id'
    _check_company_auto = True

    name = fields.Char(required=False,string='Name', readonly=True)
    primary_key_id = fields.Integer(required=True,string='Primary key id', readonly=True)     
    active = fields.Boolean(required=True, string='Active', default=True)
    
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
   