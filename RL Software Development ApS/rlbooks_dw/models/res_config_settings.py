from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    dw_statement_revenue_account_ids = fields.Many2many("account.account", relation="account_account_dw_statement_revenue_account_ids_rel", string='Revenue accounts', required=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    dw_statement_recievable_account_ids = fields.Many2many("account.account", relation="account_account_dw_statement_recievable_account_ids_rel", string='Recievable accounts', required=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    dw_statement_recievable_afp_ids = fields.Many2many("account.fiscal.position", relation="account_account_dw_statement_recievable_afp_ids_rel", string='Recievable Fiscal Position', required=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    dw_statement_dwbank_account_id = fields.Many2one("account.account", string='DW Bank', required=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    dw_statement_dwloss_account_id = fields.Many2one("account.account", string='DW Write-off', required=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    dw_statement_recievable_group_ids = fields.Many2many("res.partner.group", relation="res_partner_group_dw_statement_recievable_group_ids_rel", string='Other Partners shown as Recievables', required=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    dw_statement_languages_id = fields.Many2one("res.lang", string='Language', required=False, domain="[('active','=',True)]")
    dw_statement_currency_id = fields.Many2one("res.currency", string='Currency', required=False, domain="[('active','=',True)]")
    dw_statement_partner_id = fields.Many2one(
        'res.partner', 
        string='Adressed to customer',           
        required=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'
    
    dw_statement_revenue_account_ids = fields.Many2many("account.account", relation="account_account_dw_statement_revenue_account_ids_rel", related='company_id.dw_statement_revenue_account_ids', readonly=False)
    dw_statement_recievable_account_ids = fields.Many2many("account.account", relation="account_account_dw_statement_recievable_account_ids_rel", related='company_id.dw_statement_recievable_account_ids', readonly=False)
    dw_statement_recievable_afp_ids = fields.Many2many("account.fiscal.position", relation="account_account_dw_statement_recievable_afp_ids_rel", related='company_id.dw_statement_recievable_afp_ids', readonly=False)
    dw_statement_dwbank_account_id = fields.Many2one("account.account", related='company_id.dw_statement_dwbank_account_id', readonly=False)
    dw_statement_dwloss_account_id = fields.Many2one("account.account", related='company_id.dw_statement_dwloss_account_id', readonly=False)
    dw_statement_recievable_group_ids = fields.Many2many("res.partner.group", related='company_id.dw_statement_recievable_group_ids', readonly=False)
    dw_statement_languages_id = fields.Many2one("res.lang", related='company_id.dw_statement_languages_id', readonly=False)
    dw_statement_currency_id = fields.Many2one("res.currency", related='company_id.dw_statement_currency_id', readonly=False)
    dw_statement_partner_id = fields.Many2one('res.partner', related='company_id.dw_statement_partner_id', readonly=False)
