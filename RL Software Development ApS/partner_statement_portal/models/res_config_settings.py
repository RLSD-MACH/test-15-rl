from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_partner_statement_portal_published = fields.Boolean("Add portal restriction to Published or Unpublished documents")
