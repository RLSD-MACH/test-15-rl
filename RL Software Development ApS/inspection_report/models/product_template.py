from odoo import api, fields, models

class ProductTemplateInherit(models.Model):
        
    _inherit = 'product.template'
    
    def _compute_inspection_reports_count(self):

        reports = self.env['inspection.report']

        for product in self:

            items_list = reports.search([('product_ids','in', [product.id])])
             
            product.inspection_reports_count = len(items_list)
   
    inspection_reports_count = fields.Integer(string="IR", help="Inspection reports", compute='_compute_inspection_reports_count', default=0, store=False)