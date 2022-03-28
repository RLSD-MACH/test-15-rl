from odoo import api, fields, models


class PurchaseOrderInherit(models.Model):
    
    _inherit = 'purchase.order'

    mto_ic_order_id = fields.Many2one("mto.ic_order", string='MTO IC Order', ondelete='set null',required=False)

    def action_view_mto_id(self):
       
        if self.mto_ic_order_id:
                       
            result = self.env['ir.actions.act_window']._for_xml_id('mto_ic.action_order_window')
           
            res = self.env.ref('mto_ic.view_order_form', False)

            form_view = [(res and res.id or False, 'form')]

            if 'views' in result:

                result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']

            else:

                result['views'] = form_view

            result['res_id'] = self.mto_ic_order_id.id
            

            return result