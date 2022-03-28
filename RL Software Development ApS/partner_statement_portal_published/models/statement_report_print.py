# -*- coding: utf-8 -*-

from odoo import fields, models, _

class StatementReportWizardInherit(models.Model):
    
    _inherit = 'rlbooks_statement.report.print'
        
    is_published = fields.Boolean(string='Is Published', deafult=False)
    
    def action_publish(self):

        for record in self:

            record.update({

                'is_published': True

            })    

    def action_unpublish(self):

        for record in self:

            record.update({

                'is_published': False

            })    
   