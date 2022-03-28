# -*- coding: utf-8 -*-

from odoo import api,fields, models
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta, date
import requests
import lxml.html

class FscClaim(models.Model):
    _name = 'fsc.claim'
    _description = 'FSC Claim'
    # _check_company_auto = True

    name = fields.Char(string='Name', translate=True, required=True)    
    allowed_with_other_claims = fields.Boolean(required=False, string='Allowed with other claims', default=False)
    is_claim = fields.Boolean(required=True, string='Is a claim', default=True)    
    active = fields.Boolean(required=True, string='Active', default=True)
    company_id = fields.Many2one('res.company', 'Company', required=False, index=True, default=lambda self: self.env.company)

class FscCertificateValidation(models.Model):
    
    _name = 'fsc.certificate.validation'
    _description = 'FSC Certificate Validation'
    _order = 'create_date desc'
    _check_company_auto = True

    fsc_certificate = fields.Char(required=True,string='FSC certificate')
    valid = fields.Boolean(required=True, string='Valid')
    request_identifier = fields.Char(required=False,string='Request Identifier')
    certificate_id = fields.Many2one("fsc.certificate", string='FSC Certificate', ondelete='set null', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")    
    full_response = fields.Html(required=False, string="Full response", store=True )
    
    company_id = fields.Many2one('res.company', 'Company', required=False, index=True, default=lambda self: self.env.company)
    active = fields.Boolean(required=True, string='Active', default=True, copy=False)
        
    # @api.depends(lambda self: (self._rec_name,) if self._rec_name else ())
    # def _compute_display_name(self):

    #     names = dict(self.name_get())
    #     for record in self:

    #         if record.request_identifier:

    #             record.display_name = record.request_identifier
            
    #         else:

    #             record.display_name = "Invalid"
    
class FscCertificate(models.Model):
    _name = 'fsc.certificate'
    _description = 'FSC Certificate'
    _check_company_auto = True

    def _compute_validations_count(self):

        messages = self.env['vies.message']
        for partner in self:
            partner.validations_count = messages.search_count([('partner_id','=', partner.id)])

    last_validation_id = fields.Many2one("fsc.certificate.validation", string='Validation', ondelete='restrict', readonly=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", required=False)
    last_validation_valid = fields.Boolean(string='Certificate Valid', related='last_validation_id.valid', readonly=True)
    last_validation_date = fields.Datetime(string='Validation Date', related='last_validation_id.create_date',readonly=True)
    validations_count = fields.Integer(compute='_compute_validations_count', string="Validations Count")

    name = fields.Char(string='FSC Certificate No.', translate=False, required=True)
    partner_id = fields.Many2one('res.partner', string="Partner",required=True)
    active = fields.Boolean(required=True, string='Active', default=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)

    def action_control_certificate(self, silent = False):

        url = "https://info.fsc.org/index.php"

        payload = ("------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"code\"\r\n\r\n%s\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"submit\"\r\n\r\nSearch\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--" % self.name)
        
        headers = {
            'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
            'cache-control': "no-cache",
            'postman-token': "77cb501e-2139-5d45-18f5-076a66fadd9a"
        }

        response = requests.request("POST", url, data=payload, headers=headers)

        tree = lxml.html.fromstring(response.content)

        try:
            results = lxml.html.tostring(tree.xpath("//div[@id='details']")[0])
        except:
            # try:
            #     results = lxml.html.tostring(tree)
            # except:
                results = False

        valid = False

        try:

            certificatecl = tree.xpath("//div[@id='details']/div[@class='certificatecl']")[0]

            x = 0

            children = certificatecl.xpath('.//child::*')

            for path in children:
                
                x += 1

                if str(path.text).lower() == 'status':
                    
                    if str(children[x].text).lower() == 'valid':

                        valid = True    
        except:

            valid = False           

        try:

            certcodescl = tree.xpath("//div[@id='details']/div[@class='certcodescl']")[0]

            children = certcodescl.xpath('.//child::div')
            
            found_it = False

            for path in children:            
                
                if len(path.xpath(".//label")) > 0:

                    if str(path.xpath(".//label")[0].text).lower() == 'certificate code':
                        
                        found_it = True

                        if len(path.xpath(".//span")) > 0:

                            if str(path.xpath(".//span")[0].text).lower() != str(self.name).lower():
                                
                                valid = False    
                        
            if found_it == False:   

                valid = False

        except:

            valid = False    
        

        object = {}

        object['fsc_certificate'] = self.name
        object['valid'] = valid
        object['request_identifier'] = False
        object['certificate_id'] = self.id
        object['full_response'] = results


        validation = self.env['fsc.certificate.validation'].create(object)

        self.update({
                        
            "last_validation_id": validation.id

        })

        if silent == False:

            try:
                    form_view_id = self.env.ref("fsc_certificate.view_fsc_certificate_validation_form").id

            except Exception as e:

                    form_view_id = False

            return {

                    'type': 'ir.actions.act_window',
                    'name': 'Validation',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_id': validation.id,
                    'res_model': 'fsc.certificate.validation',
                    'views': [(form_view_id, 'form')],
                    'target': 'current',
                }

        else:

            return None

    @api.model
    def create(self, vals):

        rec = super(FscCertificate, self).create(vals)

        auto = self.env.company.fsc_run_auto_create_edit

        if auto:
            
            rec.action_control_certificate(silent = True)

        return rec

    def write(self, data):

        if 'name' in data or 'partner_id' in data or 'company_id' in data:

           raise UserError("The number, partner and company can't be changed after creation. Please archive this record instead.")

        res = super(FscCertificate, self).write(data)
                
        # if 'name' in data:

        #     auto = self.env.company.fsc_run_auto_create_edit

        #     if auto:

        #         self.action_control_certificate(silent = True)

        return res

    @api.depends(lambda self: (self._rec_name,) if self._rec_name else ())
    def _compute_display_name(self):

        for record in self:

            if record.last_validation_id:

                if record.last_validation_valid:
                    
                    record.display_name = record.name
                
                else:

                    record.display_name = record.name + " (INVALID!)" 
            
            else:

                record.display_name = record.name





