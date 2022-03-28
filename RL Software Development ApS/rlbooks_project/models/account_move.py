from odoo import api, fields, models


class AccountMoveLineInherit(models.Model):
   
    _inherit = 'account.move.line'

    rlbooks_project_id = fields.Many2one("rlbooks.project.project", string='Project', ondelete='restrict', required=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    rlbooks_project_entry_ids = fields.One2many("rlbooks.project.entry", 'move_line_id', string='Entry', ondelete='restrict', required=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

class AccountMoveInherit(models.Model):
   
    _inherit = 'account.move'

    project_invoice = fields.Boolean(required=True, string='Project invoice', default=False, tracking=True)
    rlbooks_project_entry_ids = fields.One2many("rlbooks.project.entry", 'sales_invoice_id', string='Entry', required=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    rlbooks_project_entry_cost = fields.Float(required=False, string='Project entry cost', tracking=False, store=False, compute='_compute_project_stats', readonly=True)
    rlbooks_project_entry_est_salesvalue = fields.Float(required=False, string='Project entry est. sale', tracking=False, store=False, compute='_compute_project_stats', readonly=True)

    def _compute_project_stats(self):

        for rec in self:

            total = sum(rec.rlbooks_project_entry_ids.mapped('s_costprice_t')) if rec.rlbooks_project_entry_ids else 0
            rec.rlbooks_project_entry_cost = total

            total = sum(rec.rlbooks_project_entry_ids.mapped('s_salesprice_t')) if rec.rlbooks_project_entry_ids else 0
            rec.rlbooks_project_entry_est_salesvalue = total


    def _post(self, soft=True):

        for record in self:

            if record.is_sale_document():

                type_doc = "revenue"
                

            else:

                type_doc = 'expense'

                for line in self.env['account.move.line'].search([['move_id','=',record.id],['rlbooks_project_id','!=', False]]):

                    self.env['rlbooks.project.entry'].create({

                        'project_id': line.rlbooks_project_id.id,
                        'type': type_doc,
                        'date': record.date,
                        'description': line.name,
                        'qty_spent': line.quantity,
                        'qty_invoiceable': line.quantity,
                        'salesprice': line.price_unit,
                        'r_costprice': line.price_unit,
                        's_costprice': line.price_unit,
                        'move_id': record.id,
                        'move_line_id': line.id,
                        'product_id': line.product_id.id,
                        'user_id': False,
                        'locked': True

                    })


        res = super(AccountMoveInherit, self)._post(soft)

        return res