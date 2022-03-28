from odoo import api, fields, models,  _

class ResPartnerInherit(models.Model):
    
    _inherit = 'res.partner'

    insurance_partner_ID = fields.Char(required=False, string='ID from Insurance')
    insurance_company_id = fields.Many2one('insurance.company', string='Insurance Provider', required=False,)
    insurance_credit_limit = fields.Float(string='Insurance Limit')
    insurance_credit_limit_currency_id = fields.Many2one('res.currency', string='Limit currency')
    
   
