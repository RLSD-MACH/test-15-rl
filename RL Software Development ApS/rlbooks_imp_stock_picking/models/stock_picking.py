from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError

class StockPickingInherit(models.Model):
    
    _inherit = 'stock.picking'

    contact_id = fields.Many2one("res.partner", string='Contact', ondelete='restrict', required=False, readonly=False, copy=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id), ('parent_id', '=', partner_id), ('type', '=','contact')]")
    external_note_for_customer = fields.Text('External note',help='External note for Customer/Vendor')
       
    @api.model
    def create(self, vals):

        if "partner_id" in vals:

            partner = self.env['res.partner'].browse(vals['partner_id'])

            if "contact_id" not in vals or vals.get('contact_id', False) == False:

                vals.update({

                    'contact_id': partner.contact_id.id,

                })

            if "user_id" not in vals or vals.get('user_id', False) == False:

                vals.update({

                    'user_id': partner.property_stock_picking_responsible_id.id,

                })

        rec = super(StockPickingInherit, self).create(vals)

        return rec

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        
        for record in self:

            if record.partner_id:

                partner = record.partner_id
    
                record.update({
                    
                    'contact_id':partner.contact_id.id,
                    'user_id': partner.property_stock_picking_responsible_id.id,
                    
                })