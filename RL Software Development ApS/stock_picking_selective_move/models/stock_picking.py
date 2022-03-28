from odoo import api, fields, models, _

from odoo.exceptions import AccessError, UserError, ValidationError

class StockPickingInherit(models.Model):
    
    _inherit = 'stock.picking'

    # container_id = fields.Many2one('container', string='Container')
    # sale_order_id = fields.Many2one('sale.order', string='Sale order')
    # shipping_order_id = fields.Many2one('shipping.order', string='Sale order')
    allow_diff_owner = fields.Boolean('Allow diffrint owners on stock', default=False)

    def action_confirm(self):

        res = super(StockPickingInherit, self).action_confirm()

        return res
        
        self._check_company()
        # self.mapped('package_level_ids').filtered(lambda pl: pl.state == 'draft' and not pl.move_ids)._generate_moves()
        # # call `_action_confirm` on every draft move
        # self.mapped('move_lines')\
        #     .filtered(lambda move: move.state == 'draft')\
        #     ._action_confirm()

        # # run scheduler for moves forecasted to not have enough in stock
        # self.mapped('move_lines').filtered(lambda move: move.state not in ('draft', 'cancel', 'done'))._trigger_scheduler()
        # return True

    def button_validate(self):
        
        ctx = dict(self.env.context)
        ctx.pop('default_immediate_transfer', None)
        self = self.with_context(ctx)
        
        self._check_company()
        
        for picking in self:
            
            correction_data = {}

            # if picking.container_id:
                
            #     correction_data['container_id'] = picking.container_id.id
            
            # if picking.shipping_order_id:
                
            #     correction_data['shipping_order_id'] = picking.shipping_order_id.id

            if correction_data == {}:

                picking.move_lines.write(correction_data)

                picking.move_line_ids.write(correction_data)

        if self.picking_type_code == "outgoing":

            if self.allow_diff_owner == False and self.env.context.get('ignore_missing_so_lines', False) == False:

                if self.location_dest_id.usage in ['customer']:

                    owner = self.owner_id

                    for line in self.move_ids_without_package:

                        if line.owner_id != owner:

                            raise UserError("The moves dosent seem to have the same owner, as assigned on the picking. When we ship stock to the customer, then we cant mix and match stock from diffrent owners on the same delivery note. We can sell %s new stock by removing them from 'assigned owner' or we can change the delivery lines be removing 'owner' from it settings." % self.owner_id)

                    
                    if not owner:

                        no_so = []
                        no_so_product = []

                        all_is_zero = True

                        for line in self.move_ids_without_package:

                            if not line.sale_line_id and line.quantity_done != 0:

                                no_so.append(line)
                                no_so_product.append(line.product_id.display_name)
                            
                            if line.quantity_done != 0:
                                all_is_zero = False

                        if all_is_zero:

                            for line in self.move_ids_without_package:

                                if not line.sale_line_id:

                                    no_so.append(line)
                                    no_so_product.append(line.product_id.display_name)

                        if len(no_so):

                            if self.sale_id:
                                
                                return {

                                    'name': _("Missing salesorder line id's on delivery lines"),

                                    'type': 'ir.actions.act_window',

                                    'res_model': 'stock.picking.add_so_line.wizard',

                                    'view_mode': 'form',

                                    'view_type': 'form',

                                    'views': [[False, 'form'],],

                                    'context': {'default_picking_id': self.id},

                                    'target': 'new',

                                }
                            
                            else:

                                raise UserError("%s line(s) are missing a SO reference. It dosent seem to be right. If you want to use the wizard for adding sales order lines to the delivery lines, then please select a sales order on the delivery order and press validate again! Please look at these: %s -> as products: %s" % (str(len(no_so)), str(no_so), str(no_so_product) )) 
                

        elif self.picking_type_code == "internal":
            
            if self.allow_diff_owner == False:

                owner = self.owner_id

                for line in self.move_ids_without_package:

                    if line.owner_id != owner:

                        raise UserError("The moves dosent seem to have the same owner, as assigned on the picking. When moving stocks internally, this should not happen?")

        elif self.picking_type_code == "incoming":

            if self.allow_diff_owner == False:

                if self.location_id.usage in ['supplier']:
                    #['supplier','view','internal','customer','inventory','production','transit']

                    if self.owner_id:

                        # check if they have a PO attached
                        for line in self.move_ids_without_package:

                            if line.purchase_line_id:

                                raise UserError("One or more of the moves have a PO reference. It dosent seem to be right, when we have assigned %s as the owner.") % self.owner_id

                    else:

                        no_po = []
                        no_po_product = []

                        for line in self.move_ids_without_package:

                            if not line.purchase_line_id:

                                no_po.append(line)
                                no_po_product.append(line.product_id.display_name)

                        if len(no_po):

                            raise UserError("%s line(s) are missing a PO reference. It dosent seem to be right. Please look at these: %s -> as products: %s" % (str(len(no_po)), str(no_po), str(no_po_product) )) 
         
        res = super(StockPickingInherit, self).button_validate()
        
        return res