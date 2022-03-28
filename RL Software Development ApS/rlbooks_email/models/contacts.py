from odoo import api, fields, models


class Contacts(models.Model):
    
    _name = "res.partner"
    _inherit = 'res.partner'
    
    email_cc = fields.Char(string='Email CC', required=False, store=True)
    contact_cc_ids = fields.Many2many('res.partner', "res_partner_contact_cc_rel", 's_partner_id', 'res_partner_id', string='Contacts CC', required=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id), ('email', '!=', False),('id','not in',contact_bcc_ids)]")
    email_bcc = fields.Char(string='Email BCC', required=False, store=True)
    contact_bcc_ids = fields.Many2many('res.partner', "res_partner_contact_bcc_rel", 's_partner_id', 'res_partner_id', string='Contacts BCC', required=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id), ('email', '!=', False),('id','not in',contact_cc_ids)]")
    
