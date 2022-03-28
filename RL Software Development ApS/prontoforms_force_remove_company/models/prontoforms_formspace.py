# -*- coding: utf-8 -*-

from odoo import fields, models, api

class ProntoformsInherit(models.Model):
    _inherit = 'prontoforms.formspace'
    
    company_id = fields.Many2one('res.company', 'Company', required=False, default=False)
    
    @api.model
    def create(self, vals):

        if "company_id" in vals:

            vals['company_id'] = False

        res =  super(ProntoformsInherit, self).create(vals)

        return res

    def write(self, vals):
       
        if "company_id" in vals:

            vals['company_id'] = False
       
        res = super(ProntoformsInherit, self).write(vals)

        return res
