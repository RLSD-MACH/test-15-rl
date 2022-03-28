from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    project_group_default_id = fields.Many2one("rlbooks.project.group", string='Default project-group', ondelete='set null', required=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    google_maps_api_key = fields.Char(string="Google maps api key", required=False, readonly=False, default="")
       
   
class ResConfigSettings(models.TransientModel):

    _inherit = ['res.config.settings']
  
    project_group_default_id = fields.Many2one("rlbooks.project.group", related='company_id.project_group_default_id', string='Default project-group', ondelete='set null', required=False, readonly=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    google_maps_api_key = fields.Char(string="Google maps api key", related='company_id.google_maps_api_key', readonly=False)
  
    module_rlbooks_project_entry_dashboard = fields.Boolean("Add Dashboard to Project Entry section")