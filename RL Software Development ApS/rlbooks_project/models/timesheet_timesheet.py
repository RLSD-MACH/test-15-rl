from odoo import models, fields, api
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError, UserError

class Timesheet(models.Model):

    _name = 'rlbooks.timesheet.timesheet'
    _description = 'Timesheet'
    _order = 'start desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True
   
    def _compute_hours_registred(self):

        for timesheet in self:

            groups = self.env['rlbooks.project.entry'].read_group([('date','<=', timesheet.end),('date','>=', timesheet.start),('user_id','=', timesheet.user_id.id),('type','=', 'hours'),('company_id','=',timesheet.company_id.id)], ['qty_spent'], ['user_id'])

            total = 0

            for group in groups:
               
                total += group['qty_spent']
               
            timesheet.hours_registred = total

    def _compute_hours_no_salary(self):

        for timesheet in self:

            groups = self.env['rlbooks.project.entry'].read_group([('date','<=', timesheet.end),('date','>=', timesheet.start),('user_id','=', timesheet.user_id.id),('type','=', 'hours'),('company_id','=',timesheet.company_id.id),('project_id.group_id.overtime','=', False)], ['qty_spent'], ['user_id'])

            total = 0

            for group in groups:
               
                total += group['qty_spent']
               
            timesheet.hours_no_salary = total

    name = fields.Char(required=False,string='Name', compute='_compute_name')
    user_id = fields.Many2one("res.users", string='Employee', default=lambda self: self.env.uid, tracking=True, ondelete='restrict', required=False) 
    week = fields.Integer(required=True, string='Week', readonly=True, default=0, compute='_compute_week')
    year = fields.Integer(required=True, string='Year', readonly=True, default=0, compute='_compute_year')
    start = fields.Date(required=True, string='Start', readonly=False, default= lambda self: self._get_default_start_date())
    end = fields.Date(required=True, string='End', readonly=True, compute='_compute_end_date')
    day_1 = fields.Float(required=True, string='Day 1', readonly=True, help="Expected workhours day 1 of week", default=0)
    day_2 = fields.Float(required=True, string='Day 2', readonly=True, help="Expected workhours day 2 of week", default=0)
    day_3 = fields.Float(required=True, string='Day 3', readonly=True, help="Expected workhours day 3 of week", default=0)
    day_4 = fields.Float(required=True, string='Day 4', readonly=True, help="Expected workhours day 4 of week", default=0)
    day_5 = fields.Float(required=True, string='Day 5', readonly=True, help="Expected workhours day 5 of week", default=0)
    day_6 = fields.Float(required=True, string='Day 6', readonly=True, help="Expected workhours day 6 of week", default=0)
    day_7 = fields.Float(required=True, string='Day 7', readonly=True, help="Expected workhours day 7 of week", default=0)
    hours_planned = fields.Float(compute='_compute_hours_planned', required=True, string='Planned hours', readonly=True, help="Expected workhours all week", store=True, default=0)
    hours_registred = fields.Float(required=True, string='Actual hours', readonly=True, help="Hours registred", store=False, default=0, compute='_compute_hours_registred')
    hours_difference = fields.Float(compute='_compute_hours_difference', required=True, string='Difference', readonly=True, help="Difference between planned and registred hours", default=0)
    hours_no_salary = fields.Float(compute='_compute_hours_no_salary', required=True, string='Free', readonly=True, help="Selfpaid sparetime", default=0)
    hours_overtime = fields.Float(compute='_compute_hours_overtime', required=True, string='Overtime', readonly=True, help="Worked overtime", default=0)
    
    approver_id = fields.Many2one("res.users", string='Approver', readonly=True, tracking=True, ondelete='restrict', required=False) 
    approved = fields.Date(required=False, string='Approved', readonly=True)

    state = fields.Selection(selection = [('new', 'Draft'),('approval', 'Awaiting approval'),('rejected', 'Rejected'), ('approved', 'Approved'), ('ammented', 'Ammented'),('ammentmentrejected', 'Rejected'), ('re-approval', 'Awaiting re-approval')], required=True,string='State',default='new', tracking=True)
    rlbooks_project_entry_ids = fields.One2many("rlbooks.project.entry", 'timesheet_id', string='Entries', required=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    
    @api.model
    def create(self, values):

        start = date.fromisoformat(values.get('start'))
        start = start - timedelta(days=start.weekday())

        values['start'] =  start

        end = start + timedelta(days=6)

        timesheets = self.env['rlbooks.timesheet.timesheet'].search([('user_id','=',values.get('user_id')),('start','=',start)])
        
        if timesheets:

            raise UserError("A timesheet already exists for the given periode. Timesheets in periode: " + str(len(timesheets)) + " | Start: " + str(start)) 

        contracts = self.env['hr.contract'].search([['employee_id.user_id','=',values.get('user_id')],['date_start','<=',end],'|',['date_end','=',False],['date_end','>=',values.get('start')]], order='date_start')

        if len(contracts) > 0:

            if len(contracts) > 2:

                raise UserError("We found %s contracts for the periode start: %s. Please fix it - we can have a maximum of 2 contracts.") % (str(len(contracts)), values.get('start'))

            for contract in contracts:

                if contract.date_start <= start:
                    
                    d_start = 0
                
                else:

                    d_start = int(contract.date_start.weekday())

                if contract.date_end == False:
                    
                    d_end = 6

                elif contract.date_end >= end:

                    d_end = 6

                else:

                    d_end = int(contract.date_end.weekday())
                       

                calendar = contract.resource_calendar_id

            if calendar:

                for attendance in calendar.attendance_ids:

                    if int(attendance.dayofweek) == 0 and d_start <= 0 and d_end >= 0:

                        values['day_1'] = values.get('day_1',0) + attendance.hour_to - attendance.hour_from
                    
                    elif int(attendance.dayofweek) == 1 and d_start <= 1 and d_end >= 1:

                        values['day_2'] = values.get('day_2',0) + attendance.hour_to - attendance.hour_from
                        
                    elif int(attendance.dayofweek) == 2 and d_start <= 2 and d_end >= 2:

                        values['day_3'] = values.get('day_3',0) + attendance.hour_to - attendance.hour_from
                        
                    elif int(attendance.dayofweek) == 3 and d_start <= 3 and d_end >= 3:

                        values['day_4'] = values.get('day_4',0) + attendance.hour_to - attendance.hour_from
                        
                    elif int(attendance.dayofweek) == 4 and d_start <= 4 and d_end >= 4:

                        values['day_5'] = values.get('day_5',0) + attendance.hour_to - attendance.hour_from
                        
                    elif int(attendance.dayofweek) == 5 and d_start <= 5 and d_end >= 5:

                        values['day_6'] = values.get('day_6',0) + attendance.hour_to - attendance.hour_from
                        
                    elif int(attendance.dayofweek) == 6 and d_start <= 6 and d_end >= 6:

                        values['day_7'] = values.get('day_7',0) + attendance.hour_to - attendance.hour_from 
                

            else:

                raise UserError("The contract is missing a work schedule.")

        else:

            raise UserError("No contract found for this employee regarding this date.")

        return super(Timesheet, self).create(values)
    
    @api.model
    def _get_default_start_date(self):

        last_record = self.env['rlbooks.timesheet.timesheet'].search([['user_id', '=', self.env.uid]], order='id desc')

        if last_record: 
            
            return last_record[0].start + timedelta(days=7)

        else:

            contract = self.env['hr.contract'].search([['employee_id.user_id','=',self.env.uid]], limit=1, order='date_start')

            if contract:

                return contract.date_start + timedelta(days=-contract.date_start.weekday())

            
            else:
                
                return datetime.today() + timedelta(days=-datetime.today().weekday())

    @api.depends('start')
    def _compute_end_date(self):

        for timesheet in self:
           
            timesheet.end = timesheet.start + timedelta(days=6)

    @api.depends('start')
    def _compute_week(self):

        for timesheet in self:
           
            timesheet.week = timesheet.start.isocalendar()[1]

    @api.depends('start')
    def _compute_year(self):

        for timesheet in self:
           
            timesheet.year = timesheet.start.year

    @api.depends('day_1', 'day_2', 'day_3', 'day_4', 'day_5', 'day_6', 'day_7')
    def _compute_hours_planned(self):

        for timesheet in self:

            timesheet.hours_planned = timesheet.day_1 + timesheet.day_2 + timesheet.day_3 + timesheet.day_4 + timesheet.day_5 + timesheet.day_6 + timesheet.day_7
   
    @api.depends('hours_planned', 'hours_registred', 'hours_no_salary')
    def _compute_hours_overtime(self):

        for timesheet in self:
           
            timesheet.hours_overtime = timesheet.hours_registred - timesheet.hours_planned - timesheet.hours_no_salary

    @api.depends('hours_planned', 'hours_registred')
    def _compute_hours_difference(self):

        for timesheet in self:
           
            timesheet.hours_difference = timesheet.hours_registred - timesheet.hours_planned
    
    @api.depends('week', 'year')
    def _compute_name(self):

        for timesheet in self:
           
            timesheet.name = "{:04d}".format(timesheet.year) + "-" + "{:02d}".format(timesheet.week)

    def action_show_week_entries(self):

        return{

            'type': 'ir.actions.act_window',
            'name': 'Timesheet entries',
            'res_model': 'rlbooks.project.entry',
            'domain': [('date','<=', self.end),('date','>=',self.start),('type','=','hours'),('user_id','=',self.user_id.id)],
            'context': {'default_user_id': self.user_id.id, 'default_type': 'hours', 'group_by': 'date:day'},
            'view_mode': 'tree,form',
            'target': 'current'

        }

    def action_submit_for_approval(self):

        for timesheet in self:

            if timesheet.state == 'new' or timesheet.state == 'rejected' or timesheet.state == 'ammented' or timesheet.state == 'ammentmentrejected':

                if timesheet.hours_difference >= 0:
                    
                    employee = self.env['hr.employee'].search([['user_id','=',self.user_id.id]], limit=1)
                    
                    approver = employee.timesheet_manager_id
                    
                    if approver:

                        if self.state == 'ammented' or self.state == 'ammentmentrejected':
                            
                            self.state = "re-approval" 
                            self.approved = False

                        else:

                            self.state = "approval" 
                            self.approved = False

                        self.approver_id = approver.id

                        data = {
                            'res_id': self.id,
                            'res_model_id': self.env['ir.model'].search([('model', '=', 'rlbooks.timesheet.timesheet')]).id,
                            'user_id': approver.id,
                            'summary': 'Approve timesheet ' + self.name + ' for ' + str(self.user_id.name),
                            'activity_type_id': self.env['mail.activity.type'].search([['name','=','Approve timesheet']])[0].id,
                            'date_deadline': datetime.today() + timedelta(days=7)
                            }

                        self.env['mail.activity'].create(data)
                        
                        tasks = self.env['mail.activity'].search([['res_model_id','=',self.env['ir.model'].search([('model', '=', 'rlbooks.timesheet.timesheet')]).id],['res_id','=',self.id],['activity_type_id','=',self.env['mail.activity.type'].search([['name','=','Adjust timesheet']])[0].id]])
                        
                        for task in tasks:

                            task._action_done()

                        entries = self.env['rlbooks.project.entry'].search([('date','<=', timesheet.end),('date','>=', timesheet.start),('user_id','=', timesheet.user_id.id),('type','=', 'hours'),('company_id','=',timesheet.company_id.id),('approved','=',False)])

                        for entry in entries:

                            entry.locked = True                

                    else:

                        raise UserError("I dont know, who should approve your timesheet! Please ask to be assigned a timesheet manager.")           

                else:

                    raise UserError("Your timesheet is filled out with less hours than expected - difference: " + str(-timesheet.hours_difference) + " hours. If you took some time off, then please specify it in the timesheet, and then try to submit again!")

            else:

                raise UserError("Only timesheets with the state 'draft', 'rejected' or 'ammented', can be send for approval!")

            if len(self) == 1:

                return {

                    'effect': {
                        'fadeout': 'slow',
                        'message': "Send for " + approver.name + "'s approval",
                        'img_url': '/web/static/src/img/smile.svg',
                        'type': 'rainbow_man',
                    }

                }

    def action_cancel_approval(self):

        for timesheet in self:

            if timesheet.state == 'approval' or timesheet.state == 'rejected':

                tasks = self.env['mail.activity'].search([['res_model_id','=',self.env['ir.model'].search([('model', '=', 'rlbooks.timesheet.timesheet')]).id],['res_id','=',self.id],['activity_type_id','=',self.env['mail.activity.type'].search([['name','=','Approve timesheet']])[0].id]])
                
                for task in tasks:

                    task.unlink()

                self.state = 'new'

                entries = self.env['rlbooks.project.entry'].search([('date','<=', timesheet.end),('date','>=', timesheet.start),('user_id','=', timesheet.user_id.id),('type','=', 'hours'),('company_id','=',timesheet.company_id.id),('sale_order_id','=',False),('locked','=',True),('approved','=',False)])

                for entry in entries:

                    entry.locked = False
                      

            else:

                raise UserError("Only timesheets with the state 'awaiting approval' or 'rejected', can be canceled!")

    def action_approve(self):

        for timesheet in self:

            if (timesheet.state == 'approval' or timesheet.state == 're-approval') and self.approver_id.id == self.env.uid:

                tasks = self.env['mail.activity'].search([['res_model_id','=',self.env['ir.model'].search([('model', '=', 'rlbooks.timesheet.timesheet')]).id],['res_id','=',self.id],['activity_type_id','=',self.env['mail.activity.type'].search([['name','=','Approve timesheet']])[0].id]])
                
                for task in tasks:

                    task._action_done()

                self.state = 'approved'  
                self.approved = datetime.today()   

                entries = self.env['rlbooks.project.entry'].search([('date','<=', timesheet.end),('date','>=', timesheet.start),('user_id','=', timesheet.user_id.id),('type','=', 'hours'),('company_id','=',timesheet.company_id.id),('approved','=',False)])

                for entry in entries:

                    entry.approved = True
                    entry.timesheet_id = timesheet.id                 

            else:

                if timesheet.state != 'approval' and timesheet.state != 're-approval':

                    raise UserError("Only timesheets with the state 'awaiting approval', can be approved!")

                if self.approver_id.id != self.env.uid:

                    raise UserError("You are not the assigned approver!")
    
    def action_reject(self):

        for timesheet in self:

            if (timesheet.state == 'approval' or timesheet.state == 're-approval') and self.approver_id.id == self.env.uid:

                tasks = self.env['mail.activity'].search([['res_model_id','=',self.env['ir.model'].search([('model', '=', 'rlbooks.timesheet.timesheet')]).id],['res_id','=',self.id],['activity_type_id','=',self.env['mail.activity.type'].search([['name','=','Approve timesheet']])[0].id]])
                
                for task in tasks:

                    task._action_done()

                if timesheet.state == 'approval':

                    timesheet.state = 'rejected'
                
                else:

                    timesheet.state = 'ammentmentrejected'


                data = {

                    'res_id': self.id,
                    'res_model_id': self.env['ir.model'].search([('model', '=', 'rlbooks.timesheet.timesheet')]).id,
                    'user_id': self.user_id.id,
                    'summary': 'Adjust timesheet ' + self.name + ', since the submitted timesheet was rejected.',
                    'activity_type_id': self.env['mail.activity.type'].search([['name','=','Adjust timesheet']])[0].id,
                    'date_deadline': datetime.today() + timedelta(days=7)

                }

                self.env['mail.activity'].create(data)

                entries = self.env['rlbooks.project.entry'].search([('date','<=', timesheet.end),('date','>=', timesheet.start),('user_id','=', timesheet.user_id.id),('type','=', 'hours'),('company_id','=',timesheet.company_id.id),('sale_order_id','=',False),('locked','=',True),('approved','=',False)])

                for entry in entries:

                    entry.locked = False
                           
            else:

                if timesheet.state != 'approval' and timesheet.state != 're-approval':

                    raise UserError("Only timesheets with the state 'awaiting approval', can be rejected!")

                if self.approver_id.id != self.env.uid:

                    raise UserError("You are not the assigned approver!")


                
                