# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime, timedelta, date
import json
from odoo.exceptions import AccessError, UserError, ValidationError

class AccountMoveInherit(models.Model):
    
    _inherit = 'account.move'

    def action_extract_text_pdf (self):

        for record in self:

            if record.message_main_attachment_id.id:

                attachment = record.message_main_attachment_id
                response = attachment.extract_text_pdf(docs = attachment)

                corrections = {}

                for page in response:

                    for key, value in page.items():

                        if key == 'invoice_no':

                            corrections['ref'] = value
                        
                        elif key == 'payment_instructions':

                            corrections['payment_reference'] = value
                        
                        elif key == 'date':

                            corrections['invoice_date'] = value
                            corrections['date'] = value
                        
                        elif key == 'due_date':

                            corrections['invoice_date_due'] = value
                        
                        elif key == 'supplier_vat' and record.move_type in ['in_invoice','in_refund','entry']:

                            potential_partners = self.env['res.partner'].search([['vat','ilike',value]])

                            if len(potential_partners) == 1:
                                
                                corrections['partner_id'] = potential_partners[0].id
                                corrections['fiscal_position_id'] = potential_partners[0].property_account_position_id.id



                
                record.write(corrections)

                record.message_post(body=str(response))
                record.message_post(body="corrections: " + str(corrections))
                # raise UserError(str(response))

    def action_analyse_ms_form_invoice (self):

        for record in self:

            if record.message_main_attachment_id.id:

                data = record.message_main_attachment_id.action_analyse_ms_form_invoice(return_response=True)

                if data != False:

                    corrections = {}

                    jsondata = json.loads(data)
                    # raise UserError(str(data))
                    if jsondata.get('analyzeResult', False):
                        analyzeResult = jsondata.get('analyzeResult', False)

                        if analyzeResult.get('documentResults',False):
                            documentResults = analyzeResult.get('documentResults',False)

                            if documentResults[0].get('fields',False):
                                fields = documentResults[0].get('fields',False)

                                found_partner = False

                                if fields.get('VendorTaxId', False) and fields.get('VendorTaxId', False) != self.company_id.vat and not found_partner:

                                    potential_partners = self.env['res.partner'].search([['vat','ilike',fields.get('VendorTaxId', False)['valueString']]])

                                    if len(potential_partners) == 1:
                                        
                                        corrections['partner_id'] = potential_partners[0].id
                                        corrections['fiscal_position_id'] = potential_partners[0].property_account_position_id.id

                                        found_partner = True

                                if fields.get('VendorName', False) and fields.get('VendorName', False) != self.company_id.name and not found_partner:

                                    potential_partners = self.env['res.partner'].search([['name','ilike',fields.get('VendorName', False)['valueString']]])

                                    if len(potential_partners) == 1:
                                        
                                        corrections['partner_id'] = potential_partners[0].id
                                        corrections['fiscal_position_id'] = potential_partners[0].property_account_position_id.id

                                        found_partner = True
                                                               
                                if fields.get('CustomerTaxId', False) and fields.get('CustomerTaxId', False) != self.company_id.vat and not found_partner:

                                    potential_partners = self.env['res.partner'].search([['vat','ilike',fields.get('CustomerTaxId', False)['valueString']]])

                                    if len(potential_partners) == 1:
                                        
                                        corrections['partner_id'] = potential_partners[0].id
                                        corrections['fiscal_position_id'] = potential_partners[0].property_account_position_id.id

                                        found_partner = True

                                if fields.get('CustomerName', False) and fields.get('CustomerName', False) != self.company_id.name and not found_partner:

                                    potential_partners = self.env['res.partner'].search([['name','ilike',fields.get('CustomerName', False)['valueString']]])

                                    if len(potential_partners) == 1:
                                        
                                        corrections['partner_id'] = potential_partners[0].id
                                        corrections['fiscal_position_id'] = potential_partners[0].property_account_position_id.id

                                        found_partner = True

                                if fields.get('CustomerId', False) and not found_partner:

                                    potential_partners = self.env['res.partner'].search([['ref','=',fields.get('CustomerId', False)['valueString']]])

                                    if len(potential_partners) == 1:                                        
                                        corrections['partner_id'] = potential_partners[0].id
                                        corrections['fiscal_position_id'] = potential_partners[0].property_account_position_id.id

                                        found_partner = True

                                
                                if fields.get('InvoiceId', False):
                                    corrections['ref'] = fields.get('InvoiceId', False)['valueString']
                                
                                if fields.get('PaymentTerm', False):
                                    corrections['payment_reference'] = fields.get('PaymentTerm', False)['valueString']
                                
                                if fields.get('InvoiceDate', False):
                                    corrections['invoice_date'] = datetime.strptime(fields.get('InvoiceDate', False)['text'], '%Y-%m-%d') #yyyy-mm-dd
                                    corrections['date'] = datetime.strptime(fields.get('InvoiceDate', False)['text'], '%Y-%m-%d')

                                if fields.get('DueDate', False):
                                    corrections['invoice_date_due'] = datetime.strptime(fields.get('DueDate', False)['text'], '%Y-%m-%d') #yyyy-mm-dd


                                #PurchaseOrder
                                #VendorAddress
                                #VendorAddressRecipient
                                #CustomerAddress
                                #CustomerAddressRecipient
                                #BillingAddress
                                #BillingAddressRecipient
                                #ShippingAddress
                                #ShippingAddressRecipient
                                #SubTotal - Integer
                                #TotalTax - Integer
                                #TotalVAT - Integer
                                #InvoiceTotal - Integer
                                #AmountDue - Integer
                                #ServiceAddress
                                #ServiceAddressRecipient
                                #RemittanceAddress
                                #RemittanceAddressRecipient
                                #ServiceStartDate #yyyy-mm-dd
                                #ServiceEndDate #yyyy-mm-dd
                                #PreviousUnpaidBalance - Integer

                                record.write(corrections)

                                record.message_post(body=str(data))
                                record.message_post(body="corrections: " + str(corrections))
                    
