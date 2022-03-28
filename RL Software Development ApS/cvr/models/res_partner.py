# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.exceptions import AccessError, UserError, ValidationError
import requests
import base64
import json
from datetime import datetime, timedelta, date

class ContactsInherit(models.Model):
    
    _inherit = 'res.partner'

    def _compute_cvr_message_count(self):

        messages = self.env['cvr.message']
        for partner in self:
            partner.cvr_message_count = messages.search_count([('partner_id','=', partner.id)])

    last_cvr_message_id = fields.Many2one("cvr.message", string='CVR', ondelete='restrict', readonly=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", required=False)
    last_cvr_message_valid = fields.Boolean(string='CVR Valid', related='last_cvr_message_id.valid', readonly=True,tracking=True)
    last_cvr_message_date = fields.Datetime(string='CVR Date', related='last_cvr_message_id.create_date',readonly=True)
    cvr_message_count = fields.Integer(compute='_compute_cvr_message_count', string="CVR messages Count")
    status_cvr = fields.Char(string='Status on CVR')
    
    cvr_qty_employees = fields.Integer(string='Employees',readonly=False)
    cvr_fulltime_employees = fields.Integer(string='Fulltime Employees',readonly=False)
    cvr_company_type = fields.Char(string='Company Type',readonly=False)  
    founded = fields.Date(string='Founded',readonly=False)
    cvr_id = fields.Char(string='Entity number',readonly=False)
    cvr_relation_ids = fields.One2many('res.partner.relation.cvr', 'regardig_partner_id', string='Relations on CVR')

    def action_control_all_on_cvr(self, periodically=False):
        
        if periodically:

            days = self.env.company.cvr_days_between_validations

            partners = self.env['res.partner'].search(['|', ['last_cvr_message_date', '<', date.today() - timedelta(days=days)], ['last_cvr_message_id', '=', False],['vat','!=',False],['parent_id','=',False]])

        else:

            partners = self.env['res.partner'].search([['vat','!=',False],['parent_id','=',False]])

        
        if len(partners) > 0:

            partners.control_vat_on_cvr(silent=True)

    def control_vat_on_cvr(self, silent=False, vat_obj = False, term = False):
        
        for record in self:
            
            search_term = "Vrvirksomhed.cvrNummer"

            if term:

                search_term = term
                

            if vat_obj:

                cvr = vat_obj

                partner = record

                partner_id = False

            else:

                partner_id = record.id

                partner = self.env['res.partner'].browse(partner_id)
                
                if not partner.vat:
                    
                    if silent or vat_obj:

                        return None

                    else:

                        return {
                                'effect': 
                                {
                                    'fadeout': 'slow',
                                    'message': "VAT number is missing for " + partner.name
                                }
                            }

                cvr = partner.vat

            if search_term == "Vrvirksomhed.cvrNummer":

                if len(cvr) == 10 and str(cvr[0:2]).lower() == 'dk':

                    cvr = cvr[2:]

                if len(cvr) != 8:
                    
                    if silent or vat_obj:

                        return None

                    else:

                        return {
                                'effect': 
                                {
                                    'fadeout': 'slow',
                                    'message': "VAT number dosent fit DKxxxxxxxx " + partner.name
                                }
                            }
                        

            url = "http://distribution.virk.dk/cvr-permanent/_search"

            querystring = {

                "from":"0",
                "size":"1"
                
                }

            if self.env.company.cvr_user_id == False or self.env.company.cvr_password == False:
                
                if silent or vat_obj:

                    return None

                else:

                    return {
                            'effect': 
                            {
                                'fadeout': 'slow',
                                'message': "We need informations about your company. Please go to settings and fill-in the neccesary information"
                            }
                        }

            userpass = self.env.company.cvr_user_id + ':' + self.env.company.cvr_password
            base64authorization = base64.b64encode(userpass.encode()).decode()

            headers = {
    
                'authorization': "Basic %s" % base64authorization,
                'content-type': "application/json; charset=UTF-8",
                'cache-control': "no-cache"
            
            }
            
            payload =  {
                
                "query": {
                    
                    "bool": {
                        
                        "must": {
                            
                            "term": {
                                
                                search_term: cvr
                                
                            }      
                        
                        }
                    
                    }
                    
                }
                
            }

            payload = json.dumps(payload, indent=4, sort_keys=True, default=str)

            response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
            json_response = json.loads(response.content.decode('utf-8')) 
            contact_values = {}
            
            if response.status_code == 200:
                
                hits_section = json_response['hits']

                hits = hits_section['hits']

                for hit in hits:

                    if search_term in['Vrvirksomhed.cvrNummer', 'Vrvirksomhed.enhedsNummer']:
                    
                        virksomhed = hit['_source']['Vrvirksomhed']

                        if 'cvrNummer' in virksomhed:

                            cvr = str(virksomhed['cvrNummer'])
                            contact_values['vat'] = 'DK' + str(cvr)

                        if 'deltagerRelation' in virksomhed:

                            deltagerRelationer = virksomhed['deltagerRelation']

                            existing_relations = self.env['res.partner.relation.cvr'].search([['regardig_partner_id','=',partner_id]])
                            existing_relations_ids = []

                            for relation in existing_relations:

                                existing_relations_ids.append(relation['cvr_id'])
                                
                            for deltagerRelation in deltagerRelationer:

                                deltager = deltagerRelation['deltager']

                                if deltager:
                                    
                                    organisationer = deltagerRelation['organisationer']
                                
                                    if str(deltager['enhedsNummer']) not in existing_relations_ids:

                                        other_partners = self.env['res.partner'].search([['cvr_id','=', str(deltager['enhedsNummer'])]])

                                        if len(other_partners) == 1:

                                            other_partner = other_partners[0].id

                                        else:

                                            other_partner = False

                                        # if 'livsforloeb' in deltager:

                                        #     valid_from = deltager['livsforloeb'][-1]['periode']['gyldigFra']
                                        #     valid_to = deltager['livsforloeb'][-1]['periode']['gyldigTil'] if deltager['livsforloeb'][-1]['periode']['gyldigTil'] != 'None' else False


                                        self.env['res.partner.relation.cvr'].create({
                                            
                                            'cvr_id': deltager['enhedsNummer'],
                                            'having_partner_id': other_partner,
                                            'regardig_partner_id': partner_id,
                                            'type': deltager['enhedstype'],
                                            'name': deltager['navne'][-1]['navn'],
                                            'attributes': str(organisationer),
                                            # 'valid_from': valid_from,
                                            # 'valid_to': valid_to,

                                        })

                        nyesteBeliggenhedsadresse = virksomhed['virksomhedMetadata']['nyesteBeliggenhedsadresse']

                        street1 = nyesteBeliggenhedsadresse['vejnavn']

                        if nyesteBeliggenhedsadresse.get('husnummerFra', False):

                            street1 += " " + str(nyesteBeliggenhedsadresse['husnummerFra'])

                            if nyesteBeliggenhedsadresse.get("bogstavFra", False):

                                street1 += str(nyesteBeliggenhedsadresse['bogstavFra'])

                        if nyesteBeliggenhedsadresse.get('husnummerTil', False):

                            street1 += " - " + str(nyesteBeliggenhedsadresse['husnummerTil'])

                            if nyesteBeliggenhedsadresse.get("bogstavTil", False):

                                street1 += str(nyesteBeliggenhedsadresse['bogstavTil'])

                        if nyesteBeliggenhedsadresse.get("etage",False):

                            street1 += ", " + str(nyesteBeliggenhedsadresse['etage'])

                            if nyesteBeliggenhedsadresse.get("sidedoer", False):

                                street1 += str(nyesteBeliggenhedsadresse['sidedoer'])

                        contact_values['street'] = street1
                        contact_values['street2'] = ""

                        if nyesteBeliggenhedsadresse.get("conavn", False):

                            contact_values['street2'] = str(nyesteBeliggenhedsadresse['conavn'])

                        if nyesteBeliggenhedsadresse.get("postnummer", False):

                            contact_values['zip'] = str(nyesteBeliggenhedsadresse['postnummer'])
                        
                        if nyesteBeliggenhedsadresse.get("postdistrikt", False):

                            contact_values['city'] = str(nyesteBeliggenhedsadresse['postdistrikt'])
                        
                        if nyesteBeliggenhedsadresse.get("landekode", False):

                            exists = self.env['res.country'].search([['code','=',nyesteBeliggenhedsadresse.get("landekode", False)]], limit=1)

                            if len(exists) == 1:

                                contact_values['country_id'] = exists[0].id

                        if virksomhed['virksomhedMetadata'].get("nyesteHovedbranche", False):
                            
                            nyesteHovedbranche = virksomhed['virksomhedMetadata']['nyesteHovedbranche']

                            exists = self.env['res.partner.industry'].search([['code_on_cvr','=',nyesteHovedbranche['branchekode']]], limit=1)

                            if exists:

                                industry = exists[0]

                            else:

                                industry = self.env['res.partner.industry'].create({

                                    'code_on_cvr': nyesteHovedbranche['branchekode'],
                                    'full_name': nyesteHovedbranche['branchetekst'],
                                    'name': nyesteHovedbranche['branchekode'] + " - " + nyesteHovedbranche['branchetekst']

                                })

                            contact_values['industry_id'] = industry.id

                        if virksomhed['virksomhedMetadata'].get("nyesteKontaktoplysninger", False):

                            nyesteKontaktoplysninger = virksomhed['virksomhedMetadata']['nyesteKontaktoplysninger']
                            
                            for info in nyesteKontaktoplysninger:

                                if "@" in info and not partner.email:

                                    if 'email' in contact_values:

                                        if not info in contact_values['email']:

                                            contact_values['email'] += ";" + info
                                    
                                    else:

                                        contact_values['email'] = info
                                
                                elif "http" in info.lower() or "www." in info.lower():
                                
                                    if not partner.website:

                                        contact_values['website'] = info

                                
                                else:
                                    
                                    if not partner.comment:

                                        contact_values['comment'] = info
        
                        if virksomhed.get('obligatoriskEmail', False) and not partner.email:

                            for email in virksomhed['obligatoriskEmail']:

                                if 'email' in contact_values:
                                    
                                    if type(email) is dict:

                                        if email.get('kontaktoplysning', False):

                                            if email.get('kontaktoplysning', False) not in contact_values['email']:

                                                contact_values['email'] += ";" + email.get('kontaktoplysning', False)

                                    else:

                                        if email not in contact_values['email']:

                                            contact_values['email'] += ";" + email
                                    
                                else:

                                    contact_values['email'] = email
                        
                        if virksomhed['virksomhedMetadata'].get('sammensatStatus', False):
                            
                            contact_values['status_cvr'] = virksomhed['virksomhedMetadata']['sammensatStatus']

                        contact_values['cvr_qty_employees'] = virksomhed['virksomhedMetadata']['nyesteErstMaanedsbeskaeftigelse']['antalAnsatte'] if virksomhed['virksomhedMetadata'].get('nyesteErstMaanedsbeskaeftigelse', False) else 0
                        contact_values['cvr_fulltime_employees'] = virksomhed['virksomhedMetadata']['nyesteErstMaanedsbeskaeftigelse']['antalAarsvaerk'] if virksomhed['virksomhedMetadata'].get('nyesteErstMaanedsbeskaeftigelse', False) else 0
                        contact_values['cvr_company_type'] = virksomhed['virksomhedMetadata']['nyesteVirksomhedsform']['kortBeskrivelse'] if virksomhed['virksomhedMetadata'].get('nyesteVirksomhedsform', False) else False
                        contact_values['founded'] = virksomhed['virksomhedMetadata']['stiftelsesDato'] if virksomhed['virksomhedMetadata'].get('stiftelsesDato', False) else False
                    
                    else:

                        virksomhed = hit['_source']['Vrdeltagerperson']

                        if virksomhed.get('elektroniskPost', False) and not partner.email:

                            for email in virksomhed['elektroniskPost']:

                                if 'email' in contact_values:

                                    if email not in contact_values['email']:

                                        contact_values['email'] += ";" + email
                                
                                else:

                                    contact_values['email'] = email

                        if virksomhed.get('telefonNummer', False) and not partner.phone:

                            for phone in virksomhed['telefonNummer']:

                                if 'phone' in contact_values:

                                    if phone not in contact_values['phone']:

                                        contact_values['phone'] += ";" + phone
                                
                                else:

                                    contact_values['phone'] = phone

                        if virksomhed.get('stilling', False) and not partner.function:

                            contact_values['function'] = virksomhed.get('stilling', False)

                        if 'beliggenhedsadresse' in virksomhed:
                            
                            nyesteBeliggenhedsadresse = virksomhed['beliggenhedsadresse']

                            if nyesteBeliggenhedsadresse:

                                nyesteBeliggenhedsadresse = nyesteBeliggenhedsadresse[-1]

                                street1 = nyesteBeliggenhedsadresse['vejnavn']

                                if nyesteBeliggenhedsadresse.get('husnummerFra', False):

                                    street1 += " " + str(nyesteBeliggenhedsadresse['husnummerFra'])

                                    if nyesteBeliggenhedsadresse.get("bogstavFra", False):

                                        street1 += str(nyesteBeliggenhedsadresse['bogstavFra'])

                                if nyesteBeliggenhedsadresse.get('husnummerTil', False):

                                    street1 += " - " + str(nyesteBeliggenhedsadresse['husnummerTil'])

                                    if nyesteBeliggenhedsadresse.get("bogstavTil", False):

                                        street1 += str(nyesteBeliggenhedsadresse['bogstavTil'])

                                if nyesteBeliggenhedsadresse.get("etage",False):

                                    street1 += ", " + str(nyesteBeliggenhedsadresse['etage'])

                                    if nyesteBeliggenhedsadresse.get("sidedoer", False):

                                        street1 += str(nyesteBeliggenhedsadresse['sidedoer'])

                                contact_values['street'] = street1
                                contact_values['street2'] = ""

                                if nyesteBeliggenhedsadresse.get("conavn", False):

                                    contact_values['street2'] = str(nyesteBeliggenhedsadresse['conavn'])

                                if nyesteBeliggenhedsadresse.get("postnummer", False):

                                    contact_values['zip'] = str(nyesteBeliggenhedsadresse['postnummer'])
                                
                                if nyesteBeliggenhedsadresse.get("postdistrikt", False):

                                    contact_values['city'] = str(nyesteBeliggenhedsadresse['postdistrikt'])
                                
                                if nyesteBeliggenhedsadresse.get("landekode", False):

                                    exists = self.env['res.country'].search([['code','=',nyesteBeliggenhedsadresse.get("landekode", False)]], limit=1)

                                    if len(exists) == 1:

                                        contact_values['country_id'] = exists[0].id

                        if 'virksomhedSummariskRelation' in virksomhed:

                            deltagerRelationer = virksomhed['virksomhedSummariskRelation']

                            existing_relations = self.env['res.partner.relation.cvr'].search([['regardig_partner_id','=',partner_id]])
                            existing_relations_ids = []

                            for relation in existing_relations:

                                existing_relations_ids.append(relation['cvr_id'])
                                
                            for deltagerRelation in deltagerRelationer:

                                deltager = deltagerRelation['virksomhed']

                                if deltager:
                                    
                                    organisationer = deltagerRelation['organisationer']
                                
                                    if str(deltager['enhedsNummer']) not in existing_relations_ids:

                                        other_partners = self.env['res.partner'].search([['cvr_id','=', str(deltager['enhedsNummer'])]])

                                        if len(other_partners) == 1:

                                            other_partner = other_partners[0].id

                                        else:

                                            other_partner = False

                                        valid_from = False
                                        valid_to = False

                                        if 'livsforloeb' in deltager:

                                            valid_from = deltager['livsforloeb'][-1]['periode']['gyldigFra']
                                            valid_to = deltager['livsforloeb'][-1]['periode']['gyldigTil'] if deltager['livsforloeb'][-1]['periode']['gyldigTil'] != 'None' else False

                                        self.env['res.partner.relation.cvr'].create({
                                            
                                            'cvr_id': deltager['enhedsNummer'],
                                            'having_partner_id': other_partner,
                                            'regardig_partner_id': partner_id,
                                            'type': deltager['enhedstype'],
                                            'name': deltager['navne'][-1]['navn'],
                                            'attributes': str(organisationer),
                                            'valid_from': valid_from,
                                            'valid_to': valid_to,

                                        })
                    contact_values['name'] = virksomhed['navne'][-1]['navn']
                    
                    if virksomhed.get('enhedstype', False):
                        
                        if virksomhed.get('enhedstype', False) == 'VIRKSOMHED':

                            contact_values['company_type'] = 'company'

                        elif virksomhed.get('enhedstype', False) == 'PERSON':

                            contact_values['company_type'] = 'person'
                        
                        else:

                            contact_values['company_type'] = 'company'

                    
                    if not partner.ref:

                        same_vat_or_number = self.env['res.partner'].search([['id','!=',partner_id],'|',['vat','=',partner.vat],['ref','=',cvr]])

                        if not same_vat_or_number:

                            contact_values['ref'] = cvr

                   
                    contact_values['cvr_id'] = virksomhed['enhedsNummer']
                            

                message = self.env['cvr.message'].create({

                    'vat_number': cvr,
                    'valid': True,
                    'request_identifier': cvr + " (" + contact_values['status_cvr'] + ")" if contact_values.get('status_cvr',False) else cvr,
                    'requestDate': date.today(),
                    'partner_id': partner_id,
                    'full_response': json.dumps(json_response, indent=4, sort_keys=True, default=str),
                    'full_request': payload,
                    
                })

                contact_values['last_cvr_message_id'] = message.id

                if vat_obj:

                    return contact_values

                partner.update(contact_values)

                if not silent:

                    try:
                        form_view_id = self.env.ref("cvr.cvr_message_view_form").id
                    except Exception as e:
                        form_view_id = False

                    return {

                        'type': 'ir.actions.act_window',
                        'name': 'CVR Message',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_id': message.id,
                        'res_model': 'cvr.message',
                        'views': [(form_view_id, 'form')],
                        'target': 'current',
                    }
               
            else:
                
                if vat_obj or silent:

                    return None

                else:

                    return {
                            'effect': 
                            {
                                'fadeout': 'slow',
                                'message': "Failed CVR validation for " + partner.name + " | " + str(response.content.decode('utf-8'))
                            }
                        }

    def get_accounting_date_on_cvr(self, searchBy, searchValue):

        for record in self:
              
            url = "http://distribution.virk.dk/offentliggoerelser/_search"

            querystring = {

                "from":"0",
                "size":"100"
                
                }

            if self.env.company.cvr_user_id == False or self.env.company.cvr_password == False:
                
                return {
                        'effect': 
                        {
                            'fadeout': 'slow',
                            'message': "We need informations about your company. Please go to settings and fill-in the neccesary information"
                        }
                    }

            userpass = self.env.company.cvr_user_id + ':' + self.env.company.cvr_password
            base64authorization = base64.b64encode(userpass.encode()).decode()

            headers = {
    
                'authorization': "Basic %s" % base64authorization,
                'content-type': "application/json; charset=UTF-8",
                'cache-control': "no-cache"
            
            }
            
            payload =  {
                
                "query": {
                    
                    "bool": {
                        
                        "must": {
                            
                            "term": {
                                
                                searchBy: searchValue
                                
                            }      
                        
                        }
                    
                    }
                    
                }
                
            }

            payload = json.dumps(payload, indent=4, sort_keys=True, default=str)

            response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
            json_response = json.loads(response.content.decode('utf-8')) 
            contact_values = {}
            
            if response.status_code == 200:

                raise UserError(str(json_response))

            else:

                raise UserError(str(json_response))

    @api.model
    def create(self, vals):
        

        if vals.get('vat', False):

            auto = self.env.company.cvr_run_auto_contacts
            
            if auto:

                response_cvr = self.control_vat_on_cvr(vat_obj=vals['vat'])

                if response_cvr != None:

                    vals['last_cvr_message_id'] = response_cvr['last_cvr_message_id']

        res = super(ContactsInherit, self).create(vals)

        return res
        
    def write(self, data):
        
        if data.get('vat', False):

            auto = self.env.company.cvr_run_auto_contacts

            data['last_cvr_message_id'] = False
            
            if auto:

                response_cvr = self.control_vat_on_cvr(vat_obj=data['vat'])

                if response_cvr != None:

                    data['last_cvr_message_id'] = response_cvr['last_cvr_message_id']
                
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

    @api.onchange('vat')
    def _onchange_vat(self):

        for partner in self:

            if partner.vat:

                if len(partner.vat) in [8,10]:

                    if partner.country_id.name == 'Denmark' or not partner.country_id.id:

                        values = partner.control_vat_on_cvr(silent = True, vat_obj = partner.vat)
                        
                        partner.update(values)


        