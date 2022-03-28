from odoo import api, fields, models

class Contract(models.Model):

    _name = 'hr.employee'
    _inherit = 'hr.employee'

    timesheet_manager_id = fields.Many2one("res.users", string='Timesheet', tracking=True, ondelete='restrict', required=False) 
    vehicle_ids = fields.One2many('vehicle', 'employee_id', string='Vehicles', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")