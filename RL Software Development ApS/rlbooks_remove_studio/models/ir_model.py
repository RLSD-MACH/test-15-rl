from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError


class IrModel(models.Model):
    
    _inherit = 'ir.model'

    state = fields.Selection(readonly=False)
    modules = fields.Char(readonly=False)


   