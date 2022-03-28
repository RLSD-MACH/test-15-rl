from odoo import api, fields, models

class AccountMoveInherit(models.Model):
   
    _inherit = 'account.move'

    rlbooks_goods = fields.Float(readonly=True, store=False, string='Goods', compute="_compute_sub_line_products")
    rlbooks_services = fields.Float(readonly=True, store=False,string='Services', compute="_compute_sub_line_products")
    rlbooks_consums = fields.Float(readonly=True, store=False,string='Consus', compute="_compute_sub_line_products")

    display_images = fields.Boolean(string='Display images', required=False, tracking=False, default=True)
    display_partner_shipping_id = fields.Boolean(string='Display shipping address', required=False, tracking=False, default=False)
    display_productspecifications = fields.Boolean(string='Display productspecifications', required=False, tracking=False, default=False)
    display_producttext_in_line = fields.Boolean(string='Display product text in order line', required=False, tracking=False, default=False)
    display_bomspecifications_sales_line = fields.Boolean(string='Display bomspecifications', required=False, tracking=False, default=True)
    display_bomspecifications_ps = fields.Boolean(string='Display bomspecifications', required=False, tracking=False, default=True)
    display_warehouse_message = fields.Boolean(string='Display warehouse message', required=False, tracking=False, default=True)
    document_lines_display_HS_code = fields.Boolean(string='Display HS-Code in document lines', required=False, tracking=False, default=True)
    
    def _compute_sub_line_products(self):

        for rec in self:

            goods = 0
            services = 0
            consus = 0

            company = rec.company_id

            for line in rec.line_ids:

                if line.exclude_from_invoice_tab == False:

                    if line.product_id in company.statement_goods_product_ids:

                        goods += line.amount_currency
                    
                    elif line.product_id in company.statement_services_product_ids:

                        services += line.amount_currency

                    elif line.product_id in company.statement_consus_product_ids:

                        consus += line.amount_currency
                
                    elif line.product_type == 'product':

                        goods += line.amount_currency
                    
                    elif line.product_type == 'service':

                        services += line.amount_currency

                    elif line.product_type == 'consu':

                        consus += line.amount_currency
            
            rec.rlbooks_goods = -goods
            rec.rlbooks_services = -services
            rec.rlbooks_consums = -consus

class AccountMoveLineInherit(models.Model):
   
    _inherit = 'account.move.line'

    product_type = fields.Selection("product.product", store=False, readonly=True, required=False, tracking=100, string='Product Type', related="product_id.type")
