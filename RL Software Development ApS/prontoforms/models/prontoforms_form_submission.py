from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
import requests
import base64
import json
from types import SimpleNamespace


class ProntoformsForms(models.Model):
    
    _name = 'prontoforms.form.submission'
    _description = 'Prontoforms Form Submissions'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'identifier desc'
    _check_company_auto = True

    identifier = fields.Float(required=False, string='Identifier')  
    asyncStatus = fields.Char(required=False, string='Async Status')
    name = fields.Char(required=False, string='Name')
    description = fields.Char(required=False, string='Description')

    state = fields.Char(required=False, string='State')
    dataState = fields.Char(required=False, string='Data State')
    actionState = fields.Char(required=False, string='Action State')
    serverReceiveDate = fields.Char(required=False, string='Server Receive Date')
    serverReceiveDate_date = fields.Datetime(required=False, string='Server Receive Date (DT)')
    
    formVersionId = fields.Float(required=False, string='Form Version Id') 
    formId = fields.Float(required=False, string='Form Id') 
    userId = fields.Float(required=False, string='User Id') 
    username = fields.Char(required=False, string='Username') 
    
    dataPersisted = fields.Boolean(required=False, string='Data Persisted')

    attachments_attachment_id = fields.Many2one('ir.attachment', string='Attachments')
    report_pdf_attachment_id = fields.Many2one('ir.attachment', string='Report in PDF')
    report_xml_attachment_id = fields.Many2one('ir.attachment', string='Report in XML')

    inspection_report_id = fields.Many2one('inspection.report', string='Inspection report')

    form_id = fields.Many2one('prontoforms.form', string='Form', required=False)
    prontoforms_user_id = fields.Many2one('prontoforms.user', string='Prontoform User', required=False)
    user_id = fields.Many2one('res.users', related='prontoforms_user_id.user_id', stored=True)

    json_content = fields.Text(string='JSON Content')
    
    active = fields.Boolean(required=True, string='Active', default=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    
    def action_get_attachments(self, force = False):
        
        #https://support.prontoforms.com/hc/en-us/articles/217496568-API-Form-Submission-Retrieval-and-Deletion#getDataRecords

        if force == True or not self.attachments_attachment_id:

            headers = self.env.company._return_prontoform_headers()
                
            url = "https://api.prontoforms.com/api/1.1/data/%s/attachments.zip" % (str(int(self.identifier)))
                        
            response = requests.request("GET", url, headers=headers)

            if response.status_code == 200:

                content = base64.b64encode(response.content)

                attachment = self.env['ir.attachment'].create({

                    "datas": content,
                    "res_id": self.id,
                    "res_model": "prontoforms.form.submission", 
                    "name": self.name + " attachments.zip"              

                })    
                
                self.attachments_attachment_id = attachment.id          

            else:

                raise UserError(str(response) + " | " + str(response.status_code) + " | URL: " + url)

    def action_get_pdf_report(self, force = False):
        
        #https://support.prontoforms.com/hc/en-us/articles/217496568-API-Form-Submission-Retrieval-and-Deletion#getDataRecords

        if force == True or not self.report_pdf_attachment_id:

            headers = self.env.company._return_prontoform_headers()
                
            url = "https://api.prontoforms.com/api/1/data/%s.pdf" % (str(int(self.identifier)))
                        
            response = requests.request("GET", url, headers=headers)

            if response.status_code == 200:

                content = base64.b64encode(response.content)

                attachment = self.env['ir.attachment'].create({

                    "datas": content,
                    "res_id": self.id,
                    "res_model": "prontoforms.form.submission", 
                    "name": self.name + ".pdf"              

                })  

                self.report_pdf_attachment_id = attachment.id          
                
            else:

                raise UserError(str(response) + " | " + str(response.status_code) + " | URL: " + url)

    def action_get_xml_report(self, force = False):
        
        #https://support.prontoforms.com/hc/en-us/articles/217496568-API-Form-Submission-Retrieval-and-Deletion#getDataRecords

        if force == True or not self.report_xml_attachment_id:

            headers = self.env.company._return_prontoform_headers()
                
            url = "https://api.prontoforms.com/api/1/data/%s.xml" % (str(int(self.identifier)))
                        
            response = requests.request("GET", url, headers=headers)

            if response.status_code == 200:

                content = base64.b64encode(response.content)

                attachment = self.env['ir.attachment'].create({

                    "datas": content,
                    "res_id": self.id,
                    "res_model": "prontoforms.form.submission", 
                    "name": self.name + ".xml"              

                })  

                self.report_xml_attachment_id = attachment.id          
                
            else:

                raise UserError(str(response) + " | " + str(response.status_code) + " | URL: " + url)
    
    def action_get_json_report(self, force = False):
        
        #https://support.prontoforms.com/hc/en-us/articles/217496568-API-Form-Submission-Retrieval-and-Deletion#getDataRecords

        if force == True or not self.inspection_report_id:

            headers = self.env.company._return_prontoform_headers()
                
            url = "https://api.prontoforms.com/api/1/data/%s.json" % (str(int(self.identifier)))
                        
            response = requests.request("GET", url, headers=headers)

            if response.status_code == 200:
               
                report = {}

                try:
                    
                    self.update({

                        'json_content': response.json()

                    })

                    # Parse JSON into an object with attributes corresponding to dict keys.
                    content = json.loads(json.dumps(response.json()), object_hook=lambda d: SimpleNamespace(**d))

                    report['name'] = content.referenceNumber
                    report['prontoforms_form_submission_id'] = self.id
                    report['user_id'] = self.user_id.id
                    report['message_main_attachment_id'] = self.report_pdf_attachment_id.id
                   
                    page_count = 0

                    for page in content.pages:

                        page_correct = False

                        if hasattr(page,'label'):

                            if page.label == "Inspection Brief":

                                page_correct = True

                        elif hasattr(page,'name'):

                            if page.name == "Inspection Brief":

                                page_correct = True

                        if page_correct:

                            if hasattr(page,'sections'):

                                for section in page.sections:

                                    if section.name == "Section 1":

                                        for answer in section.answers:

                                            answer, report = self.analyse_answer(answer, report)

                            elif page_count == 0:

                                for answer in page.answers:

                                    answer, report = self.analyse_answer(answer, report)

                                break

                        page_count += 1
                                       
                    
                    exsting = self.env['inspection.report'].search([['name','=', content.referenceNumber ]])

                    if len(exsting) == 0 or len(exsting) > 1:

                        new_record = self.env['inspection.report'].create(report)

                        self.update({
                                
                                'inspection_report_id': new_record.id

                            })

                    else:

                        for rec in exsting:

                            rec.update(report)
                        
                        if len(exsting) == 1 and self.inspection_report_id.id == False:

                            # raise UserError(str(self.inspection_report_id))

                            self.update({
                                
                                'inspection_report_id': exsting[0].id

                            })
                    

                except Exception as e:

                    raise UserError(str(e))
                                   
            else:

                raise UserError(str(response) + " | " + str(response.status_code) + " | URL: " + url)

    def action_add_user_id(self):
            
        for record in self:

            if not record.prontoforms_user_id:

                users = self.env['prontoforms.user'].search([['identifier','=', float(record.userId) ]])

                if len(users) == 1:

                    record.update({

                        'prontoforms_user_id': users[0].id

                    })

    def analyse_answer(self, answer, report):

        if answer.label == "From":
                                                
            report['conducted_by'] = ", ".join(answer.values)

        elif answer.label == "Inspection Result":
            
            report['result'] = ", ".join(answer.values)
                                                    
        elif answer.label == "Inspection Date":
            
            if len(answer.values) > 0:
                
                report['date'] = datetime.strptime(answer.values[0], "%Y-%m-%d").date()
                                
        elif answer.label == "Expected Date" and not report.get('date', False):
            
            if len(answer.values) > 0:
                
                report['date'] = datetime.strptime(answer.values[0], "%Y-%m-%d").date()
        
        elif answer.label == "PO":
                                                        
            report['purchase_order'] = ", ".join(answer.values)
            purchas_orders = self.env['purchase.order'].search([['name','=',answer.values[0]]])

            if len(purchas_orders) == 1:

                report['purchase_order_id'] = purchas_orders[0].id

        elif answer.label == "item":
                                                        
            report['products'] = "/".join(answer.values)

            products_char = str("/".join(answer.values)).split("/")

            products = []
            products_not_found = []

            for product_char in products_char:

                product = self.env['product.template'].search([['default_code','=',product_char]])

                if len(product) == 1:

                    products.append(product.id)

                else:

                    product = self.env['product.template'].search([['customer_art_no','=',product_char]])

                    if len(product) == 1:

                        products.append(product.id)

                    else:

                        product = self.env['product.template'].search([['barcode','=',product_char]])

                        if len(product) == 1:

                            products.append(product.id)
                        
                        else:

                            products_not_found.append(product_char)

            report['product_ids'] = products
            report['products_not_found'] = ", ".join(products_not_found)


        return answer, report