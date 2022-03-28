from odoo import fields, models

class ProductTemplate(models.Model):

    _inherit = ['product.template']

    name = fields.Char(translate=False)

    description = fields.Text(translate=False)

    description_purchase = fields.Text(translate=False)

    description_sale = fields.Text(translate=False)