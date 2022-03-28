from odoo import api, fields, models

class ResPartnerBankInherit(models.Model):
   
    _inherit = 'res.partner.bank'

    iban = fields.Char(required=False,string='IBAN', readonly=False)