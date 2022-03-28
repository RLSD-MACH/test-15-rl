# -*- coding: utf-8 -*-

from odoo import api, fields, models


class InspectionReportInherit(models.Model):
    
    _inherit = 'inspection.report'

    name = fields.Char(string='Reference Number', readonly="1")
    prontoforms_form_submission_id = fields.Many2one('prontoforms.form.submission', string='Prontoforms form submission', readonly="1")
    pfs_user_id = fields.Many2one('res.users', related='prontoforms_form_submission_id.user_id', readonly="1", string="Submitter")
    conducted_by = fields.Char(string='THIS INSPECTION WAS CONDUCTED BY', readonly="1")
           
    products = fields.Char(string='Products', readonly="1")
    products_not_found = fields.Char(string='Products not found', readonly="1")

    result = fields.Char(string='Inspection Result', readonly="1")

    #Approved for Shipment
    #Conditional Accepted for Shipment
    #On Hold for Further Evaluation
    #Rejected for Sorting/Rework
    

    @api.depends(lambda self: (self._rec_name,) if self._rec_name else ())
    def _compute_display_name(self):

        names = dict(self.name_get())

        for record in self:

            if  names.get(record.id, False):

                record.display_name = names.get(record.id, '')
            
            else:

                record.display_name = "Unnamed report"