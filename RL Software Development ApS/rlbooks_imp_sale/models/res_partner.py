from odoo import api, fields, models
       
class ResPartnerInherit(models.Model):
   
    _inherit = 'res.partner'

    property_customer_incoterm_id = fields.Many2one('account.incoterms', 
        company_dependent=True,
        string='Customer Incoterm',
        help="This will be used instead of the default one for sale orders and customer invoices", 
        required=False, 
        #domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]"
        )

    property_default_bank_account_id = fields.Many2one('account.journal', 
        company_dependent=True,
        string='Default Bank Account',
        help="This will be used instead of the default one for sale orders and customer invoices", 
        required=False, 
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    
    property_default_partner_invoice_id = fields.Many2one('res.partner', 
        company_dependent=True,
        string='Default Invoice Address',
        help="This will be used instead of the default one for sale orders and customer invoices", 
        required=False, 
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    
    property_default_partner_shipping_id = fields.Many2one('res.partner', 
        company_dependent=True,
        string='Default Shipping Address',
        help="This will be used instead of the default one for sale orders and customer invoices", 
        required=False, 
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    contact_id = fields.Many2one('res.partner', 
        # company_dependent=True,
        string='Contactperson',
        help="The person we contact - if this is a delivery adresse, then you need to select our contact at their warehouse.",         
        required=False, 
        domain="[('is_company', '=', False), ('type', '=', 'contact')]")

