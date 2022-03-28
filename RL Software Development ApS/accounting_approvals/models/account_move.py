from datetime import datetime, timedelta
from odoo.exceptions import ValidationError, UserError
from odoo import api, fields, models,  _

class AccountMoveInherit(models.Model):
    
    _inherit = 'account.move'

    approver_id = fields.Many2one("res.users", string='Approver', readonly=True, tracking=True, ondelete='restrict', required=False) 
    approved = fields.Date(required=False, string='Approved', readonly=True)
    released_for_payment = fields.Date(required=False, string='Released for payment', readonly=True)
    approval_state = fields.Selection(selection = [('new', 'Draft'),('approval', 'Awaiting approval'),('rejected', 'Rejected'), ('approved', 'Approved'), ('ammented', 'Ammented'),('ammentmentrejected', 'Rejected'), ('re-approval', 'Awaiting re-approval'), ('payment', 'Released for payment')], required=False,string='Approval State', default='new', tracking=True)
        
    def action_submit_for_approval(self):

        for move in self:

            if move.approval_state== 'new' or move.approval_state== 'rejected' or move.approval_state== 'ammented' or move.approval_state== 'ammentmentrejected':
                    
                if move.approver_id.id != False:

                    if move.approver_id.id != self.env.user.id:

                        if self.approval_state== 'ammented' or self.approval_state== 'ammentmentrejected':
                            
                            self.approval_state = "re-approval" 
                            self.approved = False

                        else:

                            self.approval_state = "approval" 
                            self.approved = False

                        data = {
                            'res_id': self.id,
                            'res_model_id': self.env['ir.model'].sudo().search([('model', '=', 'account.move')]).id,
                            'user_id': move.approver_id.id,
                            'summary': 'Journal entry ' + self.name + ' for ' + str(self.user_id.name),
                            'activity_type_id': self.env['mail.activity.type'].sudo().search([['name','=','Approve Move']])[0].id,
                            'date_deadline': datetime.today()
                            }

                        self.env['mail.activity'].sudo().create(data)
                    
                    else:

                        self.approver_id = self.env.user.id  
                        self.approval_state = 'approved'  
                        self.approved = datetime.today()  
                        
                    tasks = self.env['mail.activity'].sudo().search([['res_model_id','=',self.env['ir.model'].sudo().search([('model', '=', 'account.move')]).id],['res_id','=',self.id],['activity_type_id','=',self.env['mail.activity.type'].sudo().search([['name','=','Adjust Move']])[0].id]])
                    
                    for task in tasks:

                        task.sudo()._action_done()

                else:

                    return {

                        'name': _("Choose an approver"),

                        'type': 'ir.actions.act_window',

                        'res_model': 'select_approver.wizard',

                        'view_mode': 'form',

                        'view_type': 'form',

                        'views': [[False, 'form'],],

                        'context': {'default_move_id': self.id},

                        'target': 'new',

                    }
                      
            else:

                raise UserError("Only moves with the state 'draft', 'rejected' or 'ammented', can be send for approval!")

            if len(self) == 1:

                if move.approver_id.id != self.env.user.id:
                    return {

                        'effect': {
                            'fadeout': 'slow',
                            'message': "Send for " + move.approver_id.name + "'s approval",
                            'img_url': '/web/static/src/img/smile.svg',
                            'type': 'rainbow_man',
                        }

                    }

                else:
                    return {

                        'effect': {
                            'fadeout': 'slow',
                            'message': "You have approved the bill!",
                            'img_url': '/web/static/src/img/smile.svg',
                            'type': 'rainbow_man',
                        }

                    }

    def action_cancel_approval(self):

        for move in self:

            if move.approval_state == 'approval' or move.approval_state == 'rejected':

                tasks = self.env['mail.activity'].sudo().search([['res_model_id','=',self.env['ir.model'].sudo().search([('model', '=', 'account.move')]).id],['res_id','=',self.id],['activity_type_id','=',self.env['mail.activity.type'].sudo().search([['name','=','Approve Move']])[0].id]])
                
                for task in tasks:

                    task.sudo().unlink()

                self.approval_state = 'new'                      

            else:

                raise UserError("Only moves with the state 'awaiting approval' or 'rejected', can be canceled!")

    def action_approve(self):

        for move in self:

            if (move.approval_state == 'approval' or move.approval_state == 're-approval') and self.env.user.has_group('accounting_approvals.bill_approver'):

                tasks = self.env['mail.activity'].sudo().search([['res_model_id','=',self.env['ir.model'].sudo().search([('model', '=', 'account.move')]).id],['res_id','=',self.id],['activity_type_id','=',self.env['mail.activity.type'].sudo().search([['name','=','Approve Move']])[0].id]])
                
                for task in tasks:

                    task.sudo()._action_done()

                self.approver_id = self.env.user.id  
                self.approval_state = 'approved'  
                self.approved = datetime.today()   
     
            else:

                if move.approval_state != 'approval' and move.approval_state != 're-approval':

                    raise UserError("Only moves with the state 'awaiting approval', can be approved!")

                if self.env.user.has_group('accounting_approvals.bill_approver'):

                    raise UserError("You are not allowed to approve bills!")
    
    def action_release_for_payment(self):

        if not self.env.user.has_group('accounting_approvals.payment_approver'):
            raise UserError("You can not approve bills for payment! Contact your system administrator to get these rights.")

        for move in self:
            
            if (move.approval_state == 'approved' and move.released_for_payment == False):

                tasks = self.env['mail.activity'].sudo().search([['res_model_id','=',self.env['ir.model'].sudo().search([('model', '=', 'account.move')]).id],['res_id','=',self.id],['activity_type_id','=',self.env['mail.activity.type'].sudo().search([['name','=','Pay bill']])[0].id]])
                
                for task in tasks:
                    task.sudo()._action_done()

                self.approval_state = 'payment'  
                self.released_for_payment = datetime.today()   

            elif move.released_for_payment != False:
                raise UserError("It is already released for payment!")

            else:
                raise UserError("The bill is not approved!")

    def action_reject(self):

        for move in self:

            if (move.approval_state == 'approval' or move.approval_state == 're-approval') and self.env.user.has_group('accounting_approvals.bill_approver'):

                tasks = self.env['mail.activity'].sudo().search([['res_model_id','=',self.env['ir.model'].sudo().search([('model', '=', 'account.move')]).id],['res_id','=',self.id],['activity_type_id','=',self.env['mail.activity.type'].sudo().search([['name','=','Approve Move']])[0].id]])
                
                for task in tasks:

                    task.sudo()._action_done()

                if move.approval_state == 'approval':

                    move.approval_state = 'rejected'
                
                else:

                    move.approval_state = 'ammentmentrejected'


                data = {

                    'res_id': self.id,
                    'res_model_id': self.env['ir.model'].sudo().search([('model', '=', 'account.move')]).id,
                    'user_id': self.user_id.id,
                    'summary': 'Adjust move ' + self.name + ', since the submitted move was rejected.',
                    'activity_type_id': self.env['mail.activity.type'].sudo().search([['name','=','Adjust Move']])[0].id,
                    'date_deadline': datetime.today()

                }

                self.env['mail.activity'].sudo().create(data)
                           
            else:

                if move.approval_state != 'approval' and move.approval_state != 're-approval':

                    raise UserError("Only moves with the state 'awaiting approval', can be rejected!")

                if self.env.user.has_group('accounting_approvals.bill_approver'):

                    raise UserError("You are not allowed to approve bills!")


                