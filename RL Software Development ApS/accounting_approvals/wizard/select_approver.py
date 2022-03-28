# -*- coding: utf-8 -*-
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError, ValidationError


class SelectApprover(models.TransientModel):

    _name = 'select_approver.wizard'
    _description = 'Select approver'

    def _get_default_move_id(self):
        default_move_id = self.env.context.get('default_move_id')
        return [default_move_id] if default_move_id else None

    approver_id = fields.Many2one("res.users", string='Approver', readonly=False, ondelete='restrict', required=True, domain="[('share', '=', False)]") 
    move_id = fields.Many2one("account.move", string='Move', readonly=True, ondelete='restrict', required=False, default=_get_default_move_id) 
    
    def send(self):

        self.move_id.write({

            'approver_id': self.approver_id.id

        })

        return self.move_id.action_submit_for_approval()

    def approve_my_self(self):

        self.move_id.write({

            'approver_id': self.env.user.id

        })

        return self.move_id.action_submit_for_approval()