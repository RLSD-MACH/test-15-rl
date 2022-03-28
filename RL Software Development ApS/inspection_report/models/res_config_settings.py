from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_inspection_report_portal = fields.Boolean("Add portal from inspection report")
