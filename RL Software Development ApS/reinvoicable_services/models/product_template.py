from odoo import api, fields, models
from odoo.tools import float_compare

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _check_company_auto = True

    # detailed_type = fields.Selection(selection_add=[
    #     ('outlay', 'Outlay')
    # ], tracking=True, ondelete={'outlay': 'set service'})

    # type = fields.Selection(selection_add=[
    #     ('outlay', 'Outlay')
    # ], ondelete={'outlay': 'set service'})