from odoo import api, fields, models
       
class ResPartnerInherit(models.Model):
   
    _inherit = 'res.partner'

    property_stock_picking_responsible_id = fields.Many2one('res.users', 
        company_dependent=True,
        string='Responsible on pickings',
        help="This will be used instead of the default one for stock pickings", 
        required=False, 
        #domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]"
        )

   
