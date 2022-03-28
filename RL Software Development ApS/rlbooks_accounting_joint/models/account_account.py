from odoo import api, fields, models


class AccountAccountInherit(models.Model):
    
    _inherit = 'account.account'

    company_id = fields.Many2one(required=False, readonly=False)

    # def init(self): 
