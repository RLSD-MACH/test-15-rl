# -*- coding: utf-8 -*-

from odoo import fields, models, api

class ProntoformsFormSubmissionInherit(models.Model):
    _inherit = 'prontoforms.form.submission'
    
    company_id = fields.Many2one('res.company', 'Company', required=False, default=False)
    
    @api.model
    def create(self, vals):

        if "company_id" in vals:

            vals['company_id'] = False

        res =  super(ProntoformsFormSubmissionInherit, self).create(vals)

        return res

    def write(self, vals):
       
        if "company_id" in vals:

            vals['company_id'] = False
       
        res = super(ProntoformsFormSubmissionInherit, self).write(vals)

        return res
