from odoo import models, fields, api
from datetime import datetime
from datetime import timedelta  
from dateutil.relativedelta import relativedelta

class CreateReminderWizard(models.TransientModel):

    _name = 'rlbooks.project.reminder.create.wizard'
    _description = 'Create reminder'

    def _get_default_project_ids(self):
        default_project_id = self.env.context.get('default_project_id')
        return [default_project_id] if default_project_id else None
  
    name = fields.Char(required=True,string='Name')
    deadline = fields.Date(required=True,string='Deadline')
    user_id = fields.Many2one("res.users", string='Responsible', default=lambda self: self.env.uid, ondelete='restrict')    
    description = fields.Html(string='Description')    
    project_id = fields.Many2one("rlbooks.project.project", string='Project', required=True,
        default=_get_default_project_ids, ondelete='restrict', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    repeat = fields.Boolean(required=False, string='Repeat on close',default=False)
    repeat_qty_move_one = fields.Integer(required=True, string='Repeat after Qty of periode 1',default=0)
    repeat_periode_move_one = fields.Selection(selection = [('days', 'Days'),('weeks', 'Weeks'),('months', 'Months'),('years', 'Years')], required=False, string='Repeat periode 1', default=False)
    repeat_qty_move_two = fields.Integer(required=True, string='Repeat after Qty of periode 2',default=0)
    repeat_periode_move_two = fields.Selection(selection = [('days', 'Days'),('weeks', 'Weeks'),('months', 'Months'),('years', 'Years')], required=False, string='Repeat periode 2', default=False)
    next_deadline = fields.Date(string='Next deadline', 
        compute='_compute_next_deadline', readonly=True, store=True, copy=True, required=False)

    @api.depends('deadline', 'repeat', 'repeat_qty_move_one', 'repeat_periode_move_one', 'repeat_qty_move_two', 'repeat_periode_move_two')
    def _compute_next_deadline(self):

        for reminder in self:
            
            if reminder.repeat == True and reminder.deadline != False:
                
                next_repeat = reminder.deadline

                if reminder.repeat_periode_move_one != False:

                    if reminder.repeat_periode_move_one == 'days':

                        next_repeat += timedelta(days=reminder.repeat_qty_move_one)
                    
                    elif reminder.repeat_periode_move_one == 'weeks':

                        next_repeat += timedelta(days=reminder.repeat_qty_move_one*7)
                    
                    elif reminder.repeat_periode_move_one == 'months':

                        next_repeat += relativedelta(months=reminder.repeat_qty_move_one)
                    
                    elif reminder.repeat_periode_move_one == 'years':

                        next_repeat += relativedelta(years=reminder.repeat_qty_move_one)
                    
                    if reminder.repeat_periode_move_two != False:

                        if reminder.repeat_periode_move_two == 'days':

                            next_repeat += timedelta(days=reminder.repeat_qty_move_two)
                        
                        elif reminder.repeat_periode_move_two == 'weeks':

                            next_repeat += timedelta(days=reminder.repeat_qty_move_two*7)
                        
                        elif reminder.repeat_periode_move_two == 'months':

                            next_repeat += relativedelta(months=reminder.repeat_qty_move_two)
                        
                        elif reminder.repeat_periode_move_two == 'years':

                            next_repeat += relativedelta(years=reminder.repeat_qty_move_two)

                reminder.next_deadline = next_repeat
            
            elif reminder.repeat == True:

                pass

            else:

                reminder.repeat = False

    def action_create_reminder(self):
        
        vals = {

            'name': self.name,
            'active': True,
            'deadline': self.deadline,
            'description': self.description,
            'project_id': self.project_id.id,
            'user_id': self.user_id.id,
            'company_id': self.company_id.id,
            'repeat': self.repeat,
            'repeat_qty_move_one': self.repeat_qty_move_one,
            'repeat_periode_move_one': self.repeat_periode_move_one,
            'repeat_qty_move_two': self.repeat_qty_move_two,
            'repeat_periode_move_two': self.repeat_periode_move_two,
            'next_deadline': self.next_deadline

        }

        self.env['rlbooks.project.reminder'].create(vals)
        pass
        



    

