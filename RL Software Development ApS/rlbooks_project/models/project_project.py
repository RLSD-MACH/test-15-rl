from odoo import models, fields, api, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError

class Project(models.Model):

    _name = 'rlbooks.project.project'
    _description = 'Projects'
    _order = 'id'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True
    #_inherit = ['portal.mixin', 'mail.alias.mixin', 'mail.thread', 'rating.parent.mixin']
    #_rec_name = 'name' #The displayed name can be overwritten

    def _get_default_parent_id(self):
        default = self.env.context.get('default_parent_id')
        return [default] if default else None
    
    def _get_default_partner_id(self):
        default = self.env.context.get('default_partner_id')
        return [default] if default else None

        

    def _compute_reminder_count(self):

        reminders = self.env['rlbooks.project.reminder']
        
        for project in self:
            project.reminders_count = reminders.search_count([('project_id','=', project.id)])
            
    def _compute_entries_count(self):

        entries = self.env['rlbooks.project.entry']
        for project in self:
            project.entries_count = entries.search_count([('project_id','=', project.id)])

    def _compute_subprojects_count(self):

        for project in self:

            project.subprojects_count = len(project.child_ids)
            

    def _compute_open_salesvalue(self):

        entries = self.env['rlbooks.project.entry']
        for project in self:

            val = 0

            for row in entries.search([('project_id','=', project.id),('open','=',True)]):
                val += row.s_salesprice_t

            project.open_salesvalue = val

    def _compute_attachment_number(self):
        domain = [('res_model', '=', 'rlbooks.project.project'), ('res_id', 'in', self.ids)]
        attachment_data = self.env['ir.attachment'].read_group(domain, ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for request in self:
            request.attachment_number = attachment.get(request.id, 0)
      
    name = fields.Char(required=True,string='Name')
    default_code = fields.Char('Internal Reference', index=True)
    active = fields.Boolean(required=True, string='Active', default=True,tracking=True, copy=False)
    contact_id = fields.Many2one("res.partner", string='Contact', ondelete='restrict', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    contact_email = fields.Char(
        compute='_compute_contact_email', inverse='_inverse_contact_email',
        string='Email', readonly=False, store=True, copy=False)
    contact_phone = fields.Char(
        compute='_compute_contact_phone', inverse='_inverse_contact_phone',
        string="Phone", readonly=False, store=True, copy=False)
    partner_id = fields.Many2one("res.partner", string='Customer', ondelete='restrict', default=_get_default_partner_id, domain="['|',('company_id', '=', False),('company_id', '=', company_id)]")
    partner_email = fields.Char(
        compute='_compute_partner_email', inverse='_inverse_partner_email',
        string='Email', readonly=False, store=True, copy=False)
    partner_phone = fields.Char(
        compute='_compute_partner_phone', inverse='_inverse_partner_phone',
        string="Phone", readonly=False, store=True, copy=False)
    deadline = fields.Date(string='Deadline',tracking=True)
    description = fields.Html(string='Description')
    entries_count = fields.Integer(compute='_compute_entries_count', string="Entries Count")
    subprojects_count = fields.Integer(compute='_compute_subprojects_count', string="Subprojects Count")
    
    group_id = fields.Many2one("rlbooks.project.group", string='Group', ondelete='restrict', index=True, tracking=True, 
        default=lambda self:self.env.company.project_group_default_id.id, readonly=False, store=True, copy=True, required=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    open_salesvalue = fields.Float(compute='_compute_open_salesvalue', string='Open salesvalue')
    discount = fields.Float(default=0, string='Discount %')
    
    original_project_id = fields.Many2one("rlbooks.project.project", string='Original', ondelete='restrict', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    parent_id = fields.Many2one("rlbooks.project.project", string='Parent', ondelete='restrict', default=_get_default_parent_id)
    child_ids = fields.One2many('rlbooks.project.project', 'parent_id', string='Children')
    reminders_count = fields.Integer(compute='_compute_reminder_count', string="Reminders Count")
    restricted = fields.Boolean(string='Restricted',default=False,tracking=True, required=True)
    mileage_allowed = fields.Boolean(required=True, string='Mileage entries allowed', default=True, tracking=True, copy=False)
    mileage_invoiced = fields.Boolean(required=True, string='Mileage is invoiced to customer', default=True, tracking=True, copy=False)
    attachment_number = fields.Integer('Number of Attachments', compute='_compute_attachment_number')
    stage_id = fields.Many2one("rlbooks.project.stage", string='Stage', ondelete='restrict', index=True, tracking=True,
        compute='_compute_stage_id', readonly=True, store=True, copy=False, required=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    user_id = fields.Many2one("res.users", string='User',default=lambda self: self.env.uid,tracking=True, ondelete='restrict', required=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)

    def create(self, vals):

        if "parent_id" in vals:

            parent_id = vals['parent_id']

            if parent_id:

                parent = self.env['rlbooks.project.project'].browse(parent_id)

                vals['group_id'] = parent.group_id.id
                vals['partner_id'] = parent.partner_id.id
                vals['contact_id'] = parent.contact_id.id


        res = super(Project, self).create(vals)
        
        return res

    @api.constrains('active')
    def _check_stage(self):

        for record in self:

            if record.stage_id.is_closed == False and record.active == False:

                record.active = True
                raise ValidationError("You can't deactivate a project, when it is in a stage marked as 'Is closed': 'False'")
    
    @api.constrains('stage_id')
    def _check_stage_close(self):

        for record in self:

            if record.stage_id.is_closed == True:

                if record.reminders_count > 0:

                    raise ValidationError("You can't close a project, when it has open reminders.")
                
                if len(self.env['rlbooks.project.entry'].search([['project_id','=',record.id],['open','=',True]])) > 0:

                    raise ValidationError("You can't close a project, when it has open entries.")

    @api.depends('company_id')
    def _compute_stage_id(self):

        for project in self:

            if not project.stage_id:

                project.stage_id = self.env['rlbooks.project.stage'].search([('active','=',True),('company_id', '=', project.company_id.id)], order='sequence', limit=1).id
       
    @api.depends('partner_id.email')
    def _compute_partner_email(self):
        for project in self:
            if project.partner_id and project.partner_id.email != project.partner_email:
                project.partner_email = project.partner_id.email

    def _inverse_partner_email(self):
        for project in self:
            if project.partner_id and project.partner_email != project.partner_id.email:
                project.partner_id.email = project.partner_email

    @api.depends('partner_id.phone')
    def _compute_partner_phone(self):
        for project in self:
            if project.partner_id and project.partner_phone != project.partner_id.phone:
                project.partner_phone = project.partner_id.phone

    def _inverse_partner_phone(self):
        for project in self:
            if project.partner_id and project.partner_phone != project.partner_id.phone:
                project.partner_id.phone = project.partner_phone
    
    @api.depends('contact_id.email')
    def _compute_contact_email(self):
        for project in self:
            if project.contact_id and project.contact_id.email != project.contact_email:
                project.contact_email = project.contact_id.email

    def _inverse_contact_email(self):
        for project in self:
            if project.contact_id and project.contact_email != project.contact_id.email:
                project.contact_id.email = project.contact_email

    @api.depends('contact_id.phone')
    def _compute_contact_phone(self):
        for project in self:
            if project.contact_id and project.contact_phone != project.contact_id.phone:
                project.contact_phone = project.contact_id.phone

    def _inverse_contact_phone(self):
        for project in self:
            if project.contact_id and project.contact_phone != project.contact_id.phone:
                project.contact_id.phone = project.contact_phone

    @api.depends(lambda self: (self._rec_name,) if self._rec_name else ())
    def _compute_display_name(self):

        names = dict(self.name_get())
        for record in self:

            if record.default_code != False and record.default_code != '':

                record.display_name = "[" + record.default_code + "] " + names.get(record.id, '')
            
            else:

                record.display_name = names.get(record.id, False)

    def action_set_done(self):

        self.stage_id = self.env['rlbooks.project.stage'].search([('active','=',True),('is_closed','=',True)], order='sequence', limit=1).id
        self.active = False

        message = 'I dont know if we made any money, but know it is done :)'

        return {
            'effect': {
                'fadeout': 'slow',
                'message': message,
                'img_url': '/web/static/src/img/smile.svg',
                'type': 'rainbow_man',
            }
        }
    
    def action_next_stage(self):

        if self.stage_id.is_closed != True:

            self.stage_id = self.env['rlbooks.project.stage'].search([('active','=',True),('sequence','>',self.stage_id.sequence)], order='sequence', limit=1).id
            
            if self.stage_id.is_closed == True:

                return self.action_set_done()

    def _prepare_invoice(self):
        
        self.ensure_one()
        journal = self.env['account.move'].with_context(default_move_type='out_invoice')._get_default_journal()
        
        if not journal:
            raise UserError(_('Please define an accounting sales journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))

        invoice_vals = {
            'ref': self.default_code or '',
            'move_type': 'out_invoice',
            # 'narration': self.note,
            'currency_id': self.partner_id.property_product_pricelist.currency_id.id,
            # 'campaign_id': self.campaign_id.id,
            # 'medium_id': self.medium_id.id,
            # 'source_id': self.source_id.id,
            'invoice_user_id': self.user_id and self.user_id.id,
            # 'team_id': self.team_id.id,
            'partner_id': self.partner_id.id,
            'partner_shipping_id': False,
            'fiscal_position_id': (self.partner_id.property_account_position_id).id,
            'partner_bank_id': self.company_id.partner_id.bank_ids[:1].id,
            'journal_id': journal.id,  
            'invoice_origin': self.display_name,
            'invoice_payment_term_id': self.partner_id.property_payment_term_id.id,
            'invoice_incoterm_id': self.partner_id.property_customer_incoterm_id.id,
            'payment_reference': self.default_code,
            # 'transaction_ids': [(6, 0, self.transaction_ids.ids)],
            'invoice_line_ids': [],
            'company_id': self.company_id.id,
            'project_invoice': True,
            'invoice_date': datetime.today()
        }
        return invoice_vals

    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        res['domain'] = [('res_model', '=', 'rlbooks.project.project'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'rlbooks.project.project', 'default_res_id': self.id}
        return res

    # def action_get_attachment_view(self):
    #     self.ensure_one()
    #     res = self.env['ir.actions.act_window']._for_xml_id('documents.document_action')
    #     res['domain'] = [('res_model', '=', 'rlbooks.project.project'), ('res_id', 'in', self.ids)]
    #     res['context'] = {'default_res_model': 'rlbooks.project.project', 'default_res_id': self.id}
    #     return res

class Project_Stage(models.Model):

    _name = 'rlbooks.project.stage'
    _description = 'Project stage'
    _order = 'sequence, name'
    _check_company_auto = True

    name = fields.Char(required=True,string='Name')
    active = fields.Boolean(required=True,string='Active',default=True)
    is_closed = fields.Boolean(required=True,string='Is closed',default=False)
    sequence = fields.Integer(string='Sequence',required=True,default=0)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)

class Project_Group(models.Model):

    _name = 'rlbooks.project.group'
    _description = 'Project group'
    _order = 'name'
    _check_company_auto = True

    name = fields.Char(required=True,string='Name')
    active = fields.Boolean(required=True,string='Active',default=True)
    default = fields.Boolean(required=True,string='Default',default=False)
    cost_price = fields.Boolean(required=True,string='Cost price',default=False)
    overtime = fields.Boolean(required=True,string='Overtime',default=False)
    sales_price = fields.Boolean(required=True,string='Sales price',default=False)
    mileage_cost_ids = fields.One2many('mileage.cost', 'project_group_id', string='Mileage cost')
    type = fields.Selection(selection = [('external', 'External'), ('internal', 'Internal'), ('free work', 'Free work')], required=True,string='Type',default=False)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)

class Reminder(models.Model):

    _name = 'rlbooks.project.reminder'
    _description = 'Project reminder'
    _order = 'deadline'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True

    def _get_default_project_ids(self):
        default_project_id = self.env.context.get('default_project_id')
        return [default_project_id] if default_project_id else None
    
    name = fields.Char(required=True,string='Name')
    active = fields.Boolean(string='Active',
        default=True, readonly=False, store=True, copy=False, required=True,tracking=True)
    deadline = fields.Date(required=True,string='Deadline',tracking=True)
    description = fields.Html(string='Description')
    project_id = fields.Many2one("rlbooks.project.project", string='Project', required=True,
        default=_get_default_project_ids, ondelete='restrict', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",tracking=True)    
    partner_id = fields.Many2one("res.partner", string='Customer', ondelete='restrict', related='project_id.partner_id', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",tracking=True)
    contact_id = fields.Many2one("res.partner", string='Contact', ondelete='restrict', related='project_id.contact_id', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",tracking=True)
    user_id = fields.Many2one("res.users", string='Responsible', default=lambda self: self.env.uid, ondelete='restrict',tracking=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company,tracking=True)
    stage_id = fields.Many2one("rlbooks.project.reminder.stage", string='Stage', ondelete='restrict', index=True, tracking=True,
        default=lambda self: self.env['rlbooks.project.reminder.stage'].search([('active','=',True)], order='sequence', limit=1).id, readonly=False, store=True, copy=False, required=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")    
    repeat = fields.Boolean(required=False, string='Repeat on close',default=False,tracking=True)
    repeat_qty_move_one = fields.Integer(required=True, string='Repeat after Qty of periode 1',default=0)
    repeat_periode_move_one = fields.Selection(selection = [('days', 'Days'),('weeks', 'Weeks'),('months', 'Months'),('years', 'Years')], required=False, string='Repeat periode 1', default=False)
    repeat_qty_move_two = fields.Integer(required=True, string='Repeat after Qty of periode 2',default=0)
    repeat_periode_move_two = fields.Selection(selection = [('days', 'Days'),('weeks', 'Weeks'),('months', 'Months'),('years', 'Years')], required=False, string='Repeat periode 2', default=False)
    next_deadline = fields.Date(string='Next deadline', 
        compute='_compute_next_deadline', readonly=True, store=True, copy=True, required=False)
    next_reminder_id = fields.Many2one("rlbooks.project.reminder", string='Next reminder', readonly=True, store=True, copy=False, ondelete='set null', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",tracking=True)

    @api.constrains('active')
    def _check_stage(self):

        for record in self:

            if record.stage_id.is_closed == False and record.active == False:

                self.active = True
                raise ValidationError("You cant archive a record, when it is in a stage marked as 'Is closed': 'False'")

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
            
            else:

                reminder.repeat = False

    def _create_next_remnder(self):
        
        Reminders = self.env['rlbooks.project.reminder']
        
        return Reminders.create(self._prepare_next_remnder_values())

    def _prepare_next_remnder_values(self):
        
        res = {
            'deadline': self.next_deadline, 
            'stage_id': self.env['rlbooks.project.reminder.stage'].search([('active','=',True),('company_id', '=', self.company_id.id)], order='sequence', limit=1).id, 
            'active': True,
            'name': self.name,
            'description': self.description,
            'project_id': self.project_id.id,
            'contact_id': self.contact_id.id,
            'user_id': self.user_id.id,
            'company_id': self.company_id.id,
            'repeat': self.repeat,
            'repeat_qty_move_one': self.repeat_qty_move_one,
            'repeat_periode_move_one': self.repeat_periode_move_one,
            'repeat_qty_move_two': self.repeat_qty_move_two,
            'repeat_periode_move_two': self.repeat_periode_move_two,
            'next_deadline': False,
            'next_reminder_id': False
        }

        return res

    def action_set_done(self):

        self.stage_id = self.env['rlbooks.project.reminder.stage'].search([('active','=',True),('is_closed','=',True)], order='sequence', limit=1).id
        self.active = False

        if self.repeat == True:

            self.next_reminder_id = self._create_next_remnder().id

            message = "Success!! The reminder is now closed and the next reminder is created automatically :)"
        
        else:

            message = "Success!! The reminder is now closed :)"
        
        return {
            'effect': {
                'fadeout': 'slow',
                'message': message,
                'img_url': '/web/static/src/img/smile.svg',
                'type': 'rainbow_man',
            }
        }
    
    def action_next_stage(self):

        if self.stage_id.is_closed != True:

            self.stage_id = self.env['rlbooks.project.reminder.stage'].search([('active','=',True),('sequence','>',self.stage_id.sequence)], order='sequence', limit=1).id
            
            if self.stage_id.is_closed == True:

                return self.action_set_done()

class Reminder_Stage(models.Model):

    _name = 'rlbooks.project.reminder.stage'
    _description = 'Reminder stage'
    _order = 'sequence, name'
    _check_company_auto = True

    name = fields.Char(required=True,string='Name')
    active = fields.Boolean(required=True,string='Active',default=True)
    is_closed = fields.Boolean(required=True,string='Is closed',default=False)
    sequence = fields.Integer(string='Sequence',required=True,default=0)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)