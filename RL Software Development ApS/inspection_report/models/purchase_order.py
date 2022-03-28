from odoo import api, fields, models

class PurchaseOrderInherit(models.Model):
        
    _inherit = 'purchase.order'
    
    def _compute_inspection_reports_count(self):

        reports = self.env['inspection.report']

        for order in self:

            items_list = reports.search([('purchase_order_id','=', order.id)])
             
            order.inspection_reports_count = len(items_list)
   
    inspection_reports_count = fields.Integer(string="IR", help="Inspection reports FSC", compute='_compute_inspection_reports_count', default=0, store=False)