from odoo import api, fields, models


class Contacts(models.Model):
    
    _name = "res.partner"
    _inherit = 'res.partner'

    group_id = fields.Many2one("res.partner.group", string='Contact Group', ondelete='restrict', index=True, tracking=True, 
        readonly=False, store=True, copy=True, 
        required=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

class ContactsGroup(models.Model):

    _name = 'res.partner.group'
    _description = 'Contact group'
    _order = 'name'
    _check_company_auto = True

    def _compute_contacts_count(self):

        contacts = self.env['res.partner']
        for group in self:
            group.contacts_count = contacts.search_count([('group_id','=', group.id)])

    name = fields.Char(required=True,string='Name')
    contacts_count = fields.Integer(compute='_compute_contacts_count', string="Contacts Count")
    active = fields.Boolean(required=True,string='Active',default=True)
    company_id = fields.Many2one('res.company', 'Company', required=False, index=True, default=lambda self: self.env.company)