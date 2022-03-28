
from odoo import api, fields, models


class Vehicle(models.Model):
    _name = 'vehicle'
    _description = 'Vehicle'
    _check_company_auto = True

    name = fields.Char(string='License plate', required=True)
    description = fields.Text(string='Description', required=False)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)

