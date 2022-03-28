# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError
import requests
from datetime import datetime, timedelta, date

class ContactsInherit(models.Model):
    
    _inherit = 'res.partner'

    def _compute_vies_message_count(self):

        messages = self.env['vies.message']
        for partner in self:
            partner.vies_message_count = messages.search_count([('partner_id','=', partner.id)])

    last_vies_message_id = fields.Many2one("vies.message", string='VIES', ondelete='restrict', readonly=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", required=False)
    last_vies_message_valid = fields.Boolean(string='VIES Valid', related='last_vies_message_id.valid', readonly=True,tracking=True)
    last_vies_message_date = fields.Datetime(string='VIES Date', related='last_vies_message_id.create_date',readonly=True)
    vies_message_count = fields.Integer(compute='_compute_vies_message_count', string="VIES messages Count")

    def action_control_all(self, periodically=False):
        
        if periodically:

            days = self.env.company.vies_days_between_validations

            partners = self.env['res.partner'].search(['|', ['last_vies_message_date', '<', date.today() - timedelta(days=days)], ['last_vies_message_id', '=', False],['vat','!=',False],['parent_id','=',False]])

        else:

            partners = self.env['res.partner'].search([['vat','!=',False],['parent_id','=',False]])

        
        if len(partners) > 0:

            partners.control_vat_on_vies(silent=True)



    def control_vat_on_vies(self, silent=False, write = False):

        for partner_id in self.ids:

            partner = self.env['res.partner'].browse(partner_id)

            Asker_countryCode = self.env.company.vies_asker_country_code
            Asker_CVR = self.env.company.vies_asker_vat

            if Asker_countryCode == False or Asker_CVR == False:
                
                if silent:

                    return None

                else:

                    return {
                            'effect': 
                            {
                                'fadeout': 'slow',
                                'message': "We need informations about your company. Please go to settings and fill-in the neccesary information"
                            }
                        }

            
            if partner.vat != False and partner.parent_id.id == False:
                
                if len(partner.vat) > 5:
                
                    countryCode = partner.vat[0:2]
                    cvrNumber = partner.vat[2:]
                    
                    request = """              
                    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:ec.europa.eu:taxud:vies:services:checkVat:types">";
                        <soapenv:Header/>
                        <soapenv:Body>
                        <urn:checkVatApprox>
                        <urn:countryCode>COUNTRY</urn:countryCode>
                        <urn:vatNumber>VATNUMBER</urn:vatNumber>
                        <urn:traderName>partner_name</urn:traderName>
                        <urn:traderCompanyType>partner_CompanyType</urn:traderCompanyType>
                        <urn:traderStreet>partner_street</urn:traderStreet>
                        <urn:traderPostcode>partner_zip</urn:traderPostcode>
                        <urn:traderCity>partner_city</urn:traderCity>
                        <urn:requesterCountryCode>Asker_countryCode</urn:requesterCountryCode>
                        <urn:requesterVatNumber>Asker_CVR</urn:requesterVatNumber>
                        </urn:checkVatApprox>
                        </soapenv:Body>
                    </soapenv:Envelope>"""
                    
                    request = request.replace("COUNTRY", countryCode)
                    request = request.replace("VATNUMBER", cvrNumber)
                    request = request.replace("Asker_countryCode", Asker_countryCode)
                    request = request.replace("Asker_CVR", Asker_CVR)
                    request = request.replace("partner_city", partner.city if partner.city else "" )
                    request = request.replace("partner_zip", partner.zip if partner.zip else "")
                    request = request.replace("partner_street", (partner.street if partner.street else "") + ("\n" + partner.street2 if partner.street2 else "") )
                    request = request.replace("partner_name", partner.name)
                    request = request.replace("partner_CompanyType", partner.name)
                        
                    encoded_request = request.encode('utf-8')

                    url = "http://ec.europa.eu/taxation_customs/vies/services/checkVatService"
                    
                    
                    headers = {
                        
                        'cache-control': "no-cache",
                        "Content-Type": "text/xml; charset=UTF-8",
                        "Content-Length": str(len(encoded_request))
                        
                    }
                    
                    response = requests.request("POST", url, data=encoded_request, headers=headers)                  
                    content = str(response.content, response.encoding)
                
                    if "<valid>" in content:

                        start_index = content.index("<valid>") + len("<valid>")
                        end_index = content.index("</valid>")
                        
                        valid_answer = content[start_index:end_index]
                        
                        if valid_answer == "true":
                            
                            valid = True
                        
                        else:
                            
                            valid = False
                    
                    else:

                        valid = False
                    
                    if "<requestIdentifier>" in content:

                        start_index = content.index("<requestIdentifier>") + len("<requestIdentifier>")
                        end_index = content.index("</requestIdentifier>")
                        
                        requestIdentifier = content[start_index:end_index]

                        object = {}

                        for item in ['requestDate','countryCode','vatNumber','traderName','traderCompanyType','traderAddress','traderStreet','traderPostcode','traderCity','traderNameMatch','traderCompanyTypeMatch','traderStreetMatch','traderPostcodeMatch','traderCityMatch']:
    
                            if "<" + item + ">" in content:

                                start_index = content.index("<" + item + ">") + len("<" + item + ">")
                                end_index = content.index("</" + item + ">")
                                
                                if end_index - start_index > 1:
                                    
                                    object[item] =  content[start_index:end_index]
                                
                                        
                        object['company_id'] = partner.company_id.id
                        object['full_response'] = response.content
                        object['partner_id'] = partner.id
                        object['request_identifier'] = requestIdentifier
                        object['valid'] = valid
                        object['vat_number'] = partner.vat
                        object['full_request'] = request

                        message = self.env['vies.message'].create(object)

                        if write:

                            return message.id

                        else:

                            partner.update({
                                
                                "last_vies_message_id": message.id
                            })
                        
                    else:

                        requestIdentifier = False

                        if not silent:
                            
                            return {

                                'effect': 
                                {
                                    'fadeout': 'slow',
                                    'message': "Message returned: " + str(content)
                                }
                            }
                                                       
                else:
                
                    if not silent:

                        return {
                            'effect': 
                            {
                                'fadeout': 'slow',
                                'message': "VAT number is to short for " + partner.name
                            }
                        }
            
            else:
            
                if not silent:

                    return {
                        'effect': 
                        {
                            'fadeout': 'slow',
                            'message': "Partner dosn't have a VAT-number: " + partner.name
                        }
                    }

            if not silent:

                try:
                    form_view_id = self.env.ref("vies.vies_message_view_form").id
                except Exception as e:
                    form_view_id = False

                return {

                    'type': 'ir.actions.act_window',
                    'name': 'VIES Message',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_id': message.id,
                    'res_model': 'vies.message',
                    'views': [(form_view_id, 'form')],
                    'target': 'current',
                }

    @api.model
    def create(self, vals):

        res = super(ContactsInherit, self).create(vals)

        res._create_control_vies()
                    
        return res

    @api.model 
    def write(self, data):
        
        data = self._write_control_vies(data)

        res = super(ContactsInherit, self).write(data)

        return res
    
    def encodeXMLText(self, text):
        
        if len(text) > 0:

            text = text.replace("&",  "&amp;")
            text = text.replace("\"", "&quot;")
            text = text.replace("'",  "&apos;")
            text = text.replace("<",  "&lt;")
            text = text.replace(">",  "&gt;")
            text = text.replace("\n", "&#xA;")
            text = text.replace("\r", "&#xD;")
            
        return text

    def _create_control_vies(self):

        for record in self:

            if record.vat:

                record.control_vat_on_vies(silent=True)

    def _write_control_vies(self, data):

        if 'vat' in data and 'last_vies_message_id' not in data:

            auto = self.env.company.vies_run_auto_contacts

            data['last_vies_message_id'] = False    

            if auto:

                data['last_vies_message_id'] = self.control_vat_on_vies(silent=True, write = True)

        return data
