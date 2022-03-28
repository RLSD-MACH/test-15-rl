from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.osv import expression
from datetime import datetime

class MileageReport(models.Model):

    _name = 'rlbooks.mileage.report'
    _description = 'Mileage report'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True

    def _compute_total_mileage(self):

        for mileage_report in self:

            entries = self.env['rlbooks.project.entry']
            val = 0

            for row in entries.search([('report_id','=', mileage_report.id)]):
                val += row.qty_spent

            mileage_report.total_mileage = val

    def _compute_total_value(self):
        
        for mileage_report in self:

            entries = self.env['rlbooks.project.entry']

            val = 0

            for row in entries.search([('report_id','=', mileage_report.id)]):
                val += row.r_costprice_t

            mileage_report.total_value = val
   
    name = fields.Char(required=True,string='Number', readonly=True, states={'draft': [('readonly', True)]}, index=True, default=lambda self: _('New'))
    user_id = fields.Many2one("res.users", string='User', default=lambda self: self.env.uid, tracking=True, ondelete='restrict', required=True)    
    approver_id =  fields.Many2one("res.users", string='Approver', tracking=True, ondelete='restrict', required=True)        
    vehicle_id = fields.Many2one('vehicle', string='Vehicle', required=True , domain="['&', ('employee_id.user_id','=',user_id), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    stage = fields.Selection(selection = [('new', 'New'), ('approval', 'Awaiting approval'), ('ammented', 'Ammented'), ('re-approval', 'Awaiting re-approval'), ('approved', 'Approved'), ('paid', 'Paid')], required=True,string='Stage',default='new')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    entry_ids = fields.One2many('rlbooks.project.entry', 'report_id', 'Entries')
    total_mileage = fields.Float(compute='_compute_total_mileage', string='Total mileage')
    total_value = fields.Float(compute='_compute_total_value', string='Total value')
    active = fields.Boolean(required=True, string='Active', default=True,tracking=True, copy=False)
    
    @api.model    
    def create (self, vals):

        next_seq = self.env['ir.sequence'].next_by_code('mileage.report.sequence')

        if next_seq != False:

            vals['name'] = next_seq

        res = super(MileageReport, self).create(vals)

        return res

                
class MileageCost(models.Model):
    _name = 'mileage.cost'
    _description = 'Mileage cost'

    def _get_default_project_group_id(self):

        group_id = self.env.context.get('default_project_group_id')

        return group_id if group_id else None

    name = fields.Char(string='Name')
    date_from = fields.Date(required=True, string='From',  default= datetime.today())
    date_to = fields.Date(required=True, string='To', default= datetime.today())
    cost = fields.Float(required=True, string='Cost', default=0)
    project_group_id = fields.Many2one('rlbooks.project.group', string='Project Group', required=True, default=_get_default_project_group_id)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
