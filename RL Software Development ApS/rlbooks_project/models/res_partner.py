from odoo import api, fields, models


class Partner(models.Model):
   
    _inherit = 'res.partner'

    projects_count = fields.Integer("Projects", compute='_compute_project_count')

    def _compute_project_count(self):
        projects = self.env['rlbooks.project.project']
        for project in self:
            project.projects_count = projects.search_count([('parent_id','=',False), '|','|', ('partner_id', '=', project.id), ('contact_id', '=', project.id), ('user_id', '=', project.id)])
