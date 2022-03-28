# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, UserError
from odoo.http import content_disposition, Controller, request, route
import re

class InspectionReportInherit(models.Model):
    
    _inherit = 'inspection.report'   
        
    is_published = fields.Boolean(string='Is Published', deafult=False)

    def _compute_access_url(self):

        super(InspectionReportInherit, self)._compute_access_url()
        for order in self:
            order.access_url = '/my/inspections/%s' % (order.id)

    def _get_portal_return_action(self):
        """ Return the action used to display inspections when returning from customer portal. """
        self.ensure_one()
        return self.env.ref('inspection_report_portal.action_inspections_with_onboarding')
   
    def get_portal_url_main_attachment_download(self, report_type=None, download=False):
        
        self.ensure_one()

        if self.message_main_attachment_id and report_type == 'main_attachment':

            if download:

                url = "/web/content/?id=" + str(self.message_main_attachment_id.id) + "&download=" + str(download)
            
            else:

                url = self.message_main_attachment_id.local_url
            
        elif self.message_main_attachment_id and report_type == 'main_attachment_pdf':

            url = "/web/static/lib/pdfjs/web/viewer.html?file=/web/content/" + str(self.message_main_attachment_id.id) + "?filename%3D" + self.message_main_attachment_id.name
                                   
        else:

            url = self.get_portal_url(report_type=report_type, download=download)
            
        return url

    def _show_report_custome(self, model, report_type, report_ref, download=False, attachment = False):
        if report_type not in ('html', 'pdf', 'text'):
            raise UserError(_("Invalid report type: %s", report_type))

        if not attachment:

            report_sudo = request.env.ref(report_ref).with_user(SUPERUSER_ID)

            if not isinstance(report_sudo, type(request.env['ir.actions.report'])):
                raise UserError(_("%s is not the reference of a report", report_ref))

            method_name = '_render_qweb_%s' % (report_type)
            report = getattr(report_sudo, method_name)([model.id], data={'report_type': report_type})[0]
            reporthttpheaders = [
                ('Content-Type', 'application/pdf' if report_type == 'pdf' else 'text/html'),
                ('Content-Length', len(report)),
            ]
            if report_type == 'pdf' and download:
                filename = "%s.pdf" % (re.sub('\W+', '-', model._get_report_base_filename()))
                reporthttpheaders.append(('Content-Disposition', content_disposition(filename)))
            return request.make_response(report, headers=reporthttpheaders)

        else:

            if self.message_main_attachment_id and report_type == "pdf":
                
                attchment_record = self.message_main_attachment_id
                
                reporthttpheaders = [

                    ('Content-Type', 'application/pdf;base64'),
                    ('Content-Length', attchment_record.file_size),

                ]

                if report_type == 'pdf' and download:

                    filename = "%s.pdf" % (re.sub('\W+', '-', model._get_report_base_filename()))
                    reporthttpheaders.append(('Content-Disposition', content_disposition(filename)))

                return request.make_response(attchment_record.local_url, headers=reporthttpheaders)

            else:

                raise UserError("Not report matching the criteria")

    def preview_online(self):
        
        self.ensure_one()

        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }

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
   