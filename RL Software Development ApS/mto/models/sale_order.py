from odoo import api, fields, models
from odoo.tools import float_compare

class SaleOrderInherit(models.Model):
    
    _inherit = 'sale.order'

    def action_create_po_from_so(self):

        for record in self:
  
            order = record
            
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            procurements = []
            
            previous_product_uom_qty=False
            
            for line in order.order_line:
                
                line = line.with_company(line.company_id)
                
                if not line.product_id.type in ('consu','product'): #line.state != 'sale' or 
                    continue

                qty = line._get_qty_procurement(previous_product_uom_qty)

                if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
                    continue

                group_id = line._get_procurement_group()

                if not group_id:

                    group_id = self.env['procurement.group'].create(line._prepare_procurement_group_vals())

                    line.order_id.update({ 'procurement_group_id': group_id })

                else:
                    
                    updated_vals = {}
                    if group_id.partner_id != line.order_id.partner_shipping_id:
                        updated_vals.update({'partner_id': line.order_id.partner_shipping_id.id})

                    if group_id.move_type != line.order_id.picking_policy:
                        updated_vals.update({'move_type': line.order_id.picking_policy})

                    if updated_vals:
                        group_id.write(updated_vals)

                values = line._prepare_procurement_values(group_id=group_id)
                product_qty = line.product_uom_qty - qty

                line_uom = line.product_uom
                quant_uom = line.product_id.uom_id
                product_qty, procurement_uom = line_uom._adjust_uom_quantities(product_qty, quant_uom)
                
                procurements.append(self.env['procurement.group'].Procurement(
                
                    line.product_id, product_qty, procurement_uom,
                    line.order_id.partner_shipping_id.property_stock_customer,
                    line.name, line.order_id.name, line.order_id.company_id, values))
            
            if procurements:
                
                self.env['procurement.group'].run(procurements)
