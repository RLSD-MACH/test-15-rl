# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime, timedelta, date
from odoo.exceptions import AccessError, UserError, ValidationError
import requests
import time

class FormRecognizer(models.Model):
    
    _name = 'form.recognizer'
    _description = 'Form Recognizer'
    _order = 'create_date desc'
    _check_company_auto = True

    ir_attachment_id = fields.Many2one('ir.attachment', string='Attachment', required=True)
    result_id = fields.Char(string='Result id')
    type = fields.Char(string='Type')
    response_headers = fields.Text(string='Response headers')
    response_data = fields.Text(string='Response data')
    status_code = fields.Integer(string='Status Code')    
    operation_location = fields.Char(string='Operation-Location')
    fetched = fields.Boolean(string='Fetched', default=False)

    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    active = fields.Boolean(required=True, string='Active', default=True, copy=False)


    def analyze_request_attached_pdf (self, subscription_key, end_point, file, type, ir_attachment_id):
        
        if end_point and type:

            url = end_point + "/formrecognizer/v2.1/prebuilt/" + type + "/analyze"

        else:

            raise UserError(str('end_point: %s | type: %s' %(str(end_point),str(type))))

        headers = {
            'content-type': "application/pdf",
            'ocp-apim-subscription-key': subscription_key,
            'cache-control': "no-cache",
            }

        response = requests.request("POST", url, headers=headers, data=file)

        result_id = response.headers.get('apim-request-id', "")

        new_record = self.env['form.recognizer'].create({

            'ir_attachment_id': ir_attachment_id,
            'result_id': result_id,
            'status_code': response.status_code,
            'type':type,
            'operation_location': response.headers.get('Operation-Location', ""),
            'response_headers': str(response.headers),
            'fetched': False

        })

        return new_record

    def action_analyze_get_analyze_reciept_result (self):

        company = self.company_id

        subscription_key = company.ms_form_recognizer_subscription_key

        new_record =  self.analyze_get_analyze_reciept_result(subscription_key, self.operation_location)
            
        try:
            form_view_id = self.env.ref("").id
        except Exception as e:
            form_view_id = False

        return {

            'type': 'ir.actions.act_window',
            'name': 'From Recognizer',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': new_record.id,
            'res_model': 'form.recognizer',
            'views': [(form_view_id, 'form')],
            'target': 'current',
        }

    def analyze_get_analyze_reciept_result (self, subscription_key, url):
        
        headers = {

            'ocp-apim-subscription-key': subscription_key,
            'cache-control': "no-cache",

            }
                
        status = ""

        while status != "succeeded":

            time.sleep(5)

            response = requests.request("GET", url, headers=headers)

            status = response.json().get("status", "")
                        
            if status == "succeeded":

                new_record = self.env['form.recognizer'].create({

                    'ir_attachment_id': self.ir_attachment_id.id,
                    'result_id': self.result_id,
                    'status_code': response.status_code,
                    'type': self.type,
                    'operation_location': url,
                    'response_headers': str(response.headers),
                    'response_data': str(response.content.decode("utf-8")),
                    'fetched': True

                })                

                self.update({

                    'fetched': True

                })  


        return new_record

    