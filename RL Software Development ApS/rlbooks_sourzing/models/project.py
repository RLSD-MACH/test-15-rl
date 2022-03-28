# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class TaskInherit(models.Model):
    _inherit = "project.task"

    def _message_get_suggested_recipients(self):

        recipients = super(TaskInherit, self)._message_get_suggested_recipients()

        for task in self:

            if task.partner_id:

                for recipient in recipients[task.id]:

                    if recipient[0] == task.partner_id.id:
                        
                        recipients[task.id].remove(recipient)                

            # elif task.email_from:

            #     task._message_add_suggested_recipient(recipients, email=task.email_from, reason=_('Customer Email'))
        
        return recipients

class ProjectInherit(models.Model):

    _inherit = "project.project"

    def message_subscribe(self, partner_ids=None, subtype_ids=None):
       
        res = super(ProjectInherit, self).message_subscribe(partner_ids=partner_ids, subtype_ids=subtype_ids)
        
        project_subtypes = self.env['mail.message.subtype'].browse(subtype_ids) if subtype_ids else None

        task_subtypes = (project_subtypes.mapped('parent_id') | project_subtypes.filtered(lambda sub: sub.internal or sub.default)).ids if project_subtypes else None

        if not subtype_ids or task_subtypes:

            self.mapped('tasks').message_unsubscribe(partner_ids=partner_ids)

        # if partner_ids:

        #     all_users = self.env['res.partner'].browse(partner_ids).user_ids
        #     portal_users = all_users.filtered('share')
        #     internal_users = all_users - portal_users
        #     self.allowed_portal_user_ids |= portal_users
        #     self.allowed_internal_user_ids |= internal_users

        return res
