from odoo import api, fields, models
       
class ResPartnerInherit(models.Model):
   
    _inherit = 'res.partner'

    property_supplier_incoterm_id = fields.Many2one('account.incoterms', 
        company_dependent=True,
        string='Vendor Incoterm',
        help="This incoterm term will be used instead of the default one for purchase orders and vendor bills")

    contact_id = fields.Many2one('res.partner', 
        # company_dependent=True,
        string='Contactperson',
        help="The person we contact - if this is a delivery adresse, then you need to select our contact at their warehouse.",         
        required=False, 
        domain="[('is_company', '=', False), ('type', '=', 'contact')]")

    