from odoo import api, fields, models


class ResPartnerInherit(models.Model):
    
    _inherit = 'res.partner'

    def _compute_distributors_statements_count(self):

        statements = self.env['rlbooks_dw.distributors_statement.print']
        for partner in self:
            partner.distributors_statements_count = statements.search_count([('partner_id','=', partner.id)])

    distributors_statements_count = fields.Integer(compute='_compute_distributors_statements_count', string="Distributors Statements Count")

    @api.onchange('property_account_position_id')
    def _onchange_property_account_position_id(self):
        
        for record in self:
        
            if record.property_account_position_id != False:
                
                if record.property_account_position_id.default_customer_location_id:

                    record.property_stock_customer = record.property_account_position_id.default_customer_location_id.id
                
                else:

                    locations = self.env['stock.location'].search([['complete_name','=','Partner Locations/Customers']])

                    if len(locations) == 1:

                        record.property_stock_customer = locations[0].id
                
                if record.property_account_position_id.default_supplier_location_id:

                    record.property_stock_supplier = record.property_account_position_id.default_supplier_location_id.id
                
                else:

                    locations = self.env['stock.location'].search([['complete_name','=','Partner Locations/Vendors']])

                    if len(locations) == 1:

                        record.property_stock_supplier = locations[0].id
                

