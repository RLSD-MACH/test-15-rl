from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date, timedelta
import requests
import json


class ProntoformsForms(models.Model):
    
    _name = 'prontoforms.form'
    _description = 'Prontoforms Forms'
    _order = 'identifier desc'
    _check_company_auto = True

    def _compute_submission_count(self):

        list = self.env['prontoforms.form.submission']
        for record in self:
            record.submission_count = list.search_count([('form_id','=', record.id)])

    identifier = fields.Float(required=False, string='Identifier',)    
    asyncStatus = fields.Char(required=False, string='Async Status')
    name = fields.Char(required=False, string='Name')
    description = fields.Char(required=False, string='Description')
    state = fields.Char(required=False, string='State')
    locked = fields.Boolean(required=False, string='Locked')
    formspace_id = fields.Many2one('prontoforms.formspace', string='Formspace', required=True)
    submission_ids = fields.One2many('prontoforms.form.submission', 'form_id', string='Submission')
    submission_count = fields.Integer(string='Submissions', compute="_compute_submission_count")
    last_retrive_of_submissions = fields.Char(string='Last retrived submissions')
        
    active = fields.Boolean(required=True, string='Active', default=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
       

    def action_get_submissions(self):
        
        #https://support.prontoforms.com/hc/en-us/articles/217496568-API-Form-Submission-Retrieval-and-Deletion#getDataRecords

        results_per_page = 100        
        current_page = 0
        total_pages = 1
        state = False
        form_ids = int(self.identifier) #Should be sperated by comma

        headers = self.env.company._return_prontoform_headers()

        while(current_page < total_pages):
               
            url = "https://api.prontoforms.com/api/1.1/data.json?s=%s&p=%s&fids=%s&ftime=DataRecordProcessedDate" % (str(results_per_page), str(current_page), str(form_ids))

            if state:

                url = url + "&state=" + state

            if self.last_retrive_of_submissions:

                url = url + "&stime=" + self.last_retrive_of_submissions

            last_retrive_of_submissions = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f%z')
           
            response = requests.request("GET", url, headers=headers)
            
            if response.status_code == 200:

                content = response.json()

                if "totalNumberOfPages" in content:
                    
                    total_pages = int(content.get("totalNumberOfPages", 0))

                if "pageData" in content:

                    for item in content.get("pageData", False):
                        
                        object = {}

                        object["form_id"] = self.id

                        for data in [
                            ('identifier','identifier'),
                            ('referenceNumber','name'),
                            ('asyncStatus','asyncStatus'),
                            ('description','description'),
                            ('state','state'),
                            ('dataState','dataState'),
                            ('actionState','actionState'),
                            ('serverReceiveDate','serverReceiveDate'),
                            ('formVersionId','formVersionId'),
                            ('formId','formId'),
                            ('userId','userId'),
                            ('username','username'),
                            ('dataPersisted','dataPersisted')]:


                            if data[0] in item:
                                
                                object[data[1]] =  item[data[0]]

                                if data[0] == "serverReceiveDate":
                                    
                                    try:

                                        object[data[1]+"_date"] = datetime.fromisoformat(str(item[data[0]]).replace("Z",""))
                                    
                                    except:

                                        None

                        exsting = self.env['prontoforms.form.submission'].search([['identifier','=', object['identifier'] ]])

                        if "userId" in data:

                            user = self.env['prontoforms.user'].search([['identifier','=', float(object['userId']) ]])

                            if len(user) == 1:

                                object["user_id"] = user[0].id


                        if len(exsting) == 0:

                            try:

                                new_record = self.env['prontoforms.form.submission'].create(object)

                            except Exception as e:
                                
                                raise UserError(str(object) + " | " + str(e)) 

                        else:

                            for rec in exsting:
                                
                                try:

                                    rec.update(object)

                                except Exception as e:
                                
                                    raise UserError(str(object) + " | " + str(e)) 
                        
                else:

                    raise UserError("Couldn't find pageData in content?! \\n" + str(content))

                current_page += 1

            else:

                raise UserError(str(response) + " | " + str(response.status_code) + " | URL: " + url)

        self.update({

            'last_retrive_of_submissions': last_retrive_of_submissions

        })
   
    def auto_synch_server(self):


        self.env['prontoforms.user'].action_refresh_list()
        self.env['prontoforms.formspace'].action_refresh_list()
        
        for formspace in self.env['prontoforms.formspace'].search([]):
            
            try:
            
                formspace.action_get_forms()

            except:

                None

        for form in self.env['prontoforms.form'].search([]):
            
            try:
            
                form.action_get_submissions()

            except:

                None

        for submission in self.env['prontoforms.form.submission'].search([['inspection_report_id','=', False]]):
            
            if not submission.report_pdf_attachment_id:

                try:
                
                    submission.action_get_pdf_report()

                except:

                    None

            try:
            
                submission.action_get_json_report()

            except:

                None


         