from odoo import api, fields, models
       
class ResUsersInherit(models.Model):
   
    _inherit = 'res.users'

    contactperson_id = fields.Many2one('res.partner', 
        string='Contactperson',
        help="The person we contact - if this is a delivery adresse, then you need to select our contact at their warehouse.", 
        related="partner_id.contactperson_id",
        required=False, 
        store=False)

