from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    outlay_balance_account_id = fields.Many2one("account.account", string='Outlays balance account', ondelete='set null', required=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    outlay_expence_account_id = fields.Many2one("account.account", string='Outlays expense account', ondelete='set null', required=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    outlay_default_journal = fields.Many2one("account.journal", string='Outlays default journal', ondelete='set null', required=False, domain="[('type','=','general'),'|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    
   
class ResConfigSettings(models.TransientModel):

    _inherit = ['res.config.settings']
  
    outlay_balance_account_id = fields.Many2one("account.account", related='company_id.outlay_balance_account_id', string='Outlays balance account', ondelete='set null', required=False, readonly=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    outlay_expence_account_id = fields.Many2one("account.account", related='company_id.outlay_expence_account_id', string='Outlays expense account', ondelete='set null', required=False, readonly=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    outlay_default_journal = fields.Many2one("account.journal", related='company_id.outlay_default_journal', string='Outlays default journal', ondelete='set null', required=False, readonly=False, domain="[('type','=','general'),'|', ('company_id', '=', False), ('company_id', '=', company_id)]")