# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime, timedelta, date
from odoo.exceptions import AccessError, UserError, ValidationError
from base64 import b64decode
import requests
# import pandas as pd
import re
from dateutil.parser import parse
import pdfplumber, io
# pip install pdfplumber

class IrAttachmentInherit(models.Model):
    
    _inherit = 'ir.attachment'

    def _compute_form_recognizers_count(self):

        reports = self.env['form.recognizer']

        for record in self:

            items_list = reports.search([('ir_attachment_id','=', record.id)])
             
            record.form_recognizers_count = len(items_list)
   
    form_recognizers_count = fields.Integer(string="FR", help="Form Recognizers", compute='_compute_form_recognizers_count', default=0, store=False)

    form_recognizer_ids = fields.One2many('form.recognizer', 'ir_attachment_id', string='Form Recognizer')
    
    ms_doc_type = fields.Selection(string='MS Doc Type', selection=[('receipt', 'receipt'), ('invoice', 'invoice'), ('businessCard', 'businessCard'), ('idDocument', 'idDocument'),], default='receipt')
    

    def action_extract_text_pdf (self):

        response = self.extract_text_pdf(docs = self)

        raise UserError(str(response))

    def extract_text_pdf (self, docs):

        doc = []
        collections =  []

        order_details_re = re.compile(r'(\d{6}.*) ([A-Z].*) ([A-Z].*) (\d{2}\-\d{2}\-\d{2}) ([\d.].*) ([A-Z].*) ([\d.]+\,\d{2}) ([\d.]+\,\d{2})' )
        EC_STANDARD_INVOICE_DETAILS_re = re.compile(r'([A-Z].*) ([A-Z].*) ([\d.]+\,\d) ([A-Z].*) ([\d.]+\,\d) ([\d.]+\,\d)' )
        float_in_string = re.compile(r'(\d{6}.*) ([A-Z].*) ([A-Z].*) (\d{2}\-\d{2}\-\d{2}) ([\d.].*) ([A-Z].*) ([\d.]+\,\d{2}) ([\d.]+\,\d{2})' )
        date_in_string = re.compile(r'(\d{2}\-\d{2}\-\d{2})' )
        payment_code_71 = re.compile(r'(\+\d{2}\<\d{15}\+\d{8}\<.*)' )

        search_keys = [

                    ('Date', 'date', 'date', 'EN'),
                    ('Date of issue:', 'date', 'date', 'EN'),                     
                    ('Invoice Date', 'date', 'date', 'EN'),
                    ('Fakturadato', 'date', 'date', 'DA'),
                    ('Fakturadato............:', 'date', 'date', 'DA'),
                    ('Bogføringsdato', 'date', 'date', 'DA'),
                    ('Dato', 'date', 'date', 'DA'),

                    ('Payment due on:', 'due_date', 'date', 'EN'),
                    ('due date', 'due_date', 'date', 'EN'),
                    ('Forfaldsdato', 'due_date', 'date', 'DA'),
                    ('forfaldsdato', 'due_date', 'date', 'DA'),
                    ('Forfalder', 'due_date', 'date', 'DA'),
                    ('Betalingsdato', 'due_date', 'date', 'DA'),
                    

                    ('Balance Due', 'balance_due', 'float', 'EN'),

                    ('Subtotal', 'subtotal', 'float', False),
                    ('I alt DKK ekskl. moms', 'subtotal', 'float'),
                    ('Netto DKK', 'subtotal', 'float', 'DA'),
                    ('Total Pre-Tax Charges', 'subtotal', 'float', 'EN'),

                    ('I alt DKK inkl. moms', 'total', 'float', 'DA'),
                    ('I alt DKK', 'total', 'float', 'DA'),
                    ('I alt USD', 'total', 'float', 'DA'),
                    ('I alt EUR', 'total', 'float', 'DA'),
                    ('total', 'total', 'float', False),
                    ('Total Amount', 'total', 'float', 'EN'),
                    ('Total Due', 'total', 'float', 'EN'),

                    ('25% moms', 'vat', 'float', 1, 'word', 'DA'),
                    ('25% Moms', 'vat', 'float', 1, 'word', 'DA'),
                    ('VAT (0.000%) Reverse Charge', 'vat', 'float', 1, 'word', 'EN'),
                    ('VAT', 'vat', 'float', 1, 'word', 'EN'),
                    ('VAT (0%)', 'vat', 'float', 1, 'word', 'EN'),
                    

                    ('Notes', 'Notes', 'char', 'EN'),

                    ('Leverandørnr', 'supplier_ref', 'char', 1, 'word', 'DA'),

                    ('VAT Regn No.', 'supplier_vat', 'vat-number', 1, 'word', 'EN'),
                    ('VAT ID:', 'supplier_vat', 'vat-number', 1, 'word', 'EN'),
                    ('VAT:', 'supplier_vat', 'vat-number', 1, 'word', 'EN'),
                    ('VAT number:', 'supplier_vat', 'vat-number', 1, 'word', 'EN'),
                    ('VAT number', 'supplier_vat', 'vat-number', 1, 'word', 'EN'),
                    ('VAT ID', 'supplier_vat', 'vat-number', 1, 'word', 'EN'),
                    ('CVR-nummer:', 'supplier_vat', 'vat-number', 1, 'word', 'DA'),
                    ('CVR-nummer.', 'supplier_vat', 'vat-number', 1, 'word', 'DA'),
                    ('CVR-nummer', 'supplier_vat', 'vat-number', 1, 'word', 'DA'),
                    ('CVR-nr.', 'supplier_vat', 'vat-number', 1, 'word', 'DA'),
                    ('CVR-nr :', 'supplier_vat', 'vat-number', 1, 'word', 'DA'),
                    ('CVR-nr .', 'supplier_vat', 'vat-number', 1, 'word', 'DA'),
                    ('CVR-nr ', 'supplier_vat', 'vat-number', 1, 'word', 'DA'),
                    ('VAT-no', 'supplier_vat', 'vat-number', 1, 'word', 'EN'),
                    ('VAT-no.', 'supplier_vat', 'vat-number', 1, 'word', 'EN'),
                    ('MOMS NR:', 'supplier_vat', 'vat-number', 1, 'word', 'DA'),

                    ('Indkøber', 'supplier_purchaser', 'char', 'DA'),

                    ('Telefon', 'supplier_phone', 'char', 'DA'),

                    ('Telefax', 'supplier_fax', 'char', 'DA'),

                    ('Bank', 'supplier_bank', 'char', 'DA'),

                    ('Regnr.:', 'supplier_bank_account_registration_number', 'float', 4, 'char', 'DA'),
                    ('Kontonr.', 'supplier_bank_account_number', 'float', 1, 'word', 'DA'),
                    ('Kontonr.:', 'supplier_bank_account_number', 'float', 1, 'word', 'DA'),
                    ('IBAN-nr.:', 'supplier_iban', 'char', 1, 'word', 'DA'),

                    

                    ('Ordrenr', 'order_no', 'char', 1, 'word', 'DA'),
                    ('Order ID', 'order_no', 'char', 1, 'word', 'DA'),
                                        
                    ('Betalingsbetingelser:', 'payment_instructions', 'char', 'DA'),
                    ('Betalingsbetingelser', 'payment_instructions', 'char', 'DA'),
                    ('Betalingsbetingelse:', 'payment_instructions', 'char', 'DA'),
                    ('Betalingsbetingelse', 'payment_instructions', 'char', 'DA'),

                    ('Invoice number:', 'invoice_no', 'char', 1, 'word', 'EN'),
                    ('Invoice No.', 'invoice_no', 'char', 1, 'word', 'EN'),
                    ('Invoice No', 'invoice_no', 'char', 1, 'word', 'EN'),
                    ('Fakturanr.', 'invoice_no', 'char', 1, 'word', 'DA'),
                    ('Fakturanummer', 'invoice_no', 'char', 1, 'word', 'DA'),
                    ('Fakturanr...............:', 'invoice_no', 'char', 1, 'word', 'DA'),

                    ('Billing Cycle', 'billing_periode', 'char', 'EN'),
                    ('This invoice covers the following period:', 'billing_periode', 'char', 'EN'),
                    ('Summary for ', 'billing_periode', 'char', 'EN'),
                    
                
                    ('Payment Method', 'payment_method', 'char', 'EN'),
                    ('Payment Instructions', 'payment_instructions', 'char', 'EN'),
                    ('Betalings-ID', 'payment_instructions', '+71 code', 'DA'),
                    ('Subscription ID', 'subscription_id', 'char', 1, 'word', 'EN'),
                                                
                
                ]
                                    
                

        model = self.env['ir.model'].search([('name','=','account.move')])
        use_collection = False

        if len(model) == 1:

            collections = self.env['form.collection'].search([('convertion_model_id','=', model[0].id)])

        if len(collections) > 0:

            use_collection = True
            search_keys = collections[0].key_ids

        for pdf_doc in docs:

            bytes = b64decode(pdf_doc.datas, validate=True)

            reserve_pdf_on_memory = io.BytesIO(bytes)

            with pdfplumber.load(reserve_pdf_on_memory) as pdf:
                                
                for page in pdf.pages:

                    obj = {}
                    
                    text = page.extract_text()
                    table_rows = []
                    found_values = []
                    found = []

                    if text:

                        obj['full_text'] = text.split('\n')

                        for row in text.split('\n'):

                            if order_details_re.match(row):

                                line = order_details_re.search(row)

                                obj_rows = {}

                                obj_rows['product'] = line.group(1)
                                obj_rows['product_supplier'] = line.group(2)
                                obj_rows['description'] = line.group(3)
                                obj_rows['recieve_date'] = line.group(4)
                                obj_rows['quantity'] = line.group(5)
                                obj_rows['unit'] = line.group(6)
                                obj_rows['unit_price'] = line.group(7)
                                obj_rows['price'] = line.group(8)

                                table_rows.append(obj_rows)

                            elif EC_STANDARD_INVOICE_DETAILS_re.match(row):

                                line = EC_STANDARD_INVOICE_DETAILS_re.search(row)

                                obj_rows = {}

                                obj_rows['product'] = line.group(1)
                                obj_rows['description'] = line.group(2)
                                obj_rows['quantity'] = line.group(3)
                                obj_rows['unit'] = line.group(4)
                                obj_rows['unit_price'] = line.group(5)
                                obj_rows['price'] = line.group(6)

                                table_rows.append(obj_rows)

                            elif payment_code_71.match(row):

                                obj['payment_instructions'] = row
                                found_values.append([('+71 kode', 'payment_instructions', obj[key.convertion_field_id.name] )])
                                found += [key.convertion_field_id.id]

                            else:
                                
                                if use_collection:

                                    for key in search_keys:

                                        if key.convertion_field_id.id not in found:

                                            if key.type == 'date':

                                                if key.search_for.lower() + " " in row.lower():
                                                
                                                    date_string = row[row.lower().index(key.search_for.lower()) + len(key.search_for):]

                                                    if date_string.startswith('...'):

                                                        for char in date_in_string:

                                                            if char == ".":

                                                                date_in_string = date_in_string[1:]
                                                            
                                                            else:
                                                                break
                                                                                                                                            
                                                    failed = False

                                                    try:

                                                        for char in date_in_string:

                                                            if char == " ":

                                                                date_in_string = date_in_string[1:]
                                                            
                                                            else:
                                                                break
                                                    
                                                    except:

                                                        pass
                                                    
                                                    if key.language == 'DA':

                                                        try:
                                                            obj[key.convertion_field_id.name] = datetime.strptime(date_string, '%d-%m-%Y') 
                                                            found_values.append([(key.search_for.lower(), key.convertion_field_id.name, obj[key.convertion_field_id.name] )])
                                                            found += [key.convertion_field_id.id]

                                                        except:
                                                            failed = True

                                                    if failed:                                                
                                                        try:                                                    
                                                            obj[key.convertion_field_id.name] = parse(date_string, fuzzy_with_tokens=True)[0]
                                                            found_values.append([(key.search_for.lower(), key.convertion_field_id.name, obj[key.convertion_field_id.name] )])
                                                            found += [key.convertion_field_id.id]

                                                        except:
                                                            failed = True
                                                    
                                                    if failed:

                                                        if "," in date_string:

                                                                # raise UserError(str(date_string))

                                                            if len(date_string.split()[0]) > 3:

                                                                obj[key.convertion_field_id.name] = datetime.strptime(date_string, '%B %d, %Y')
                                                                found_values.append([(key.search_for.lower(), key.convertion_field_id.name, obj[key.convertion_field_id.name] )])
                                                                found += [key.convertion_field_id.id]

                                                            elif len(date_string.split()[0]) == 3:

                                                                obj[key.convertion_field_id.name] = datetime.strptime(date_string, '%b %d, %Y')
                                                                found_values.append([(key.search_for.lower(), key.convertion_field_id.name, obj[key.convertion_field_id.name] )])
                                                                found += [key.convertion_field_id.id]

                                            elif key.type == 'char':

                                                if key.search_for.lower() + " " in row.lower():

                                                    if key.split:

                                                        if key.split_type == 'word':

                                                            value = " ".join(" ".join(row[row.lower().index(key.search_for.lower()) + len(key.search_for):].split()).split()[:key.use_word_number])

                                                            if value.startswith('...'):

                                                                for char in value:

                                                                    if char == ".":

                                                                        value = value[1:]
                                                                    
                                                                    else:
                                                                        break
                                                            
                                                            obj[key.convertion_field_id.name] = value
                                                            found_values.append([(key.search_for.lower(), key.convertion_field_id.name, obj[key.convertion_field_id.name] )])
                                                            found += [key.convertion_field_id.id]
                                                        
                                                        elif key.split_type == 'char':

                                                            value = "".join(row[row.lower().index(key.search_for.lower()) + len(key.search_for):].split())

                                                            if value.startswith('...'):

                                                                for char in value:

                                                                    if char == ".":

                                                                        value = value[1:]
                                                                    
                                                                    else:
                                                                        break
                                                            
                                                            obj[key.convertion_field_id.name] = value[:key.use_word_number]
                                                            found_values.append([(key.search_for.lower(), key.convertion_field_id.name, obj[key.convertion_field_id.name] )])
                                                            found += [key.convertion_field_id.id]
                                                        
                                                    else:

                                                        value = " ".join(row[row.lower().index(key.search_for.lower()) + len(key.search_for):].split())

                                                        if value.startswith('...'):

                                                            for char in value:

                                                                if char == ".":

                                                                    value = value[1:]
                                                                
                                                                else:
                                                                    break
                                                        
                                                        obj[key.convertion_field_id.name] = value
                                                        
                                                        found_values.append([(key.search_for.lower(), key.convertion_field_id.name, obj[key.convertion_field_id.name] )])
                                                        found += [key.convertion_field_id.id]

                                            elif key.type == 'float':

                                                if row.lower().startswith(key.search_for.lower()):
                                                
                                                    obj[key.convertion_field_id.name] = re.findall("\d+\.\d+", " ".join(row.split()[len(key.search_for.split()):])) if re.findall("[\d,]+\.\d+", " ".join(row.split()[len(key.search_for.split()):])) else re.findall("[\d.]+\,\d+", " ".join(row.split()[len(key.search_for.split()):]))
                                                    found_values.append([(key.search_for.lower(), key.convertion_field_id.name, obj[key.convertion_field_id.name] )])
                                                    found += [key.convertion_field_id.id]


                                            elif key.type == 'regex':

                                                None

                                            elif key.type == 'vat-number':

                                                if key.search_for.lower() + " " in row.lower():
                                                    
                                                    if not obj.get(key.convertion_field_id.name, False):
                                                        
                                                        found_number = " ".join(row[row.lower().index(key.search_for.lower()) + len(key.search_for):].split())
                                                        our_vat = self.env.company.vat.lower() if self.env.company.vat else ""
                                                        our_registry = self.env.company.company_registry.lower() if self.env.company.company_registry else ""
                                                        skip = False

                                                        if our_vat != "":

                                                            if found_number.lower() in our_vat or our_vat in found_number.lower():

                                                                skip = True

                                                        if our_registry != "":
                                                            
                                                            if found_number.lower() in our_registry or our_registry in found_number.lower():

                                                                skip = True
                                                        
                                                        if skip == False:

                                                            if len(found_number.split()[0]) >= 8:

                                                                obj[key.convertion_field_id.name] = found_number.split()[0]
                                                                found_values.append([(key.search_for.lower(), key.convertion_field_id.name, obj[key.convertion_field_id.name] )])
                                                                found += [key.convertion_field_id.id]
                                                            
                                                            else:

                                                                obj[key.convertion_field_id.name] = found_number
                                                                found_values.append([(key.search_for.lower(), key.convertion_field_id.name, obj[key.convertion_field_id.name] )])
                                                                found += [key.convertion_field_id.id]

                                                    # break

                                            elif key.type == 'web':

                                                None

                                            elif key.type == 'phone':

                                                None

                                            elif key.type == 'email':

                                                None

                                else:

                                    for key in search_keys:

                                        # if key[2] == '+71 code':

                                        #     if row.lower().startswith(key[0].lower()):
                                                
                                        #         obj[key[1].lower()] = re.findall("\d+\.\d+", " ".join(row.split()[len(key[0].split()):])) if re.findall("[\d,]+\.\d+", " ".join(row.split()[len(key[0].split()):])) else re.findall("[\d.]+\,\d+", " ".join(row.split()[len(key[0].split()):]))
                                        #         found_values.append([(key[0].lower(), key[1].lower(), obj[key[1].lower()] )])

                                                # break

                                        if key[2] == 'date':

                                            if key[0].lower() + " " in row.lower():
                                                
                                                date_string = row[row.lower().index(key[0].lower()) + len(key[0]):]

                                                if date_string.startswith('...'):

                                                    for char in date_in_string:

                                                        if char == ".":

                                                            date_in_string = date_in_string[1:]
                                                        
                                                        else:
                                                            break
                                                                                                                                        
                                                failed = False

                                                try:

                                                    for char in date_in_string:

                                                        if char == " ":

                                                            date_in_string = date_in_string[1:]
                                                        
                                                        else:
                                                            break
                                                
                                                except:

                                                    pass
                                                
                                                if key[3] == 'DA':

                                                    try:
                                                        obj[key[1].lower()] = datetime.strptime(date_string, '%d-%m-%Y') 
                                                        found_values.append([(key[0].lower(), key[1].lower(), obj[key[1].lower()] )])
                                                        
                                                    except:
                                                        failed = True

                                                if failed:                                                
                                                    try:                                                    
                                                        obj[key[1].lower()] = parse(date_string, fuzzy_with_tokens=True)[0]
                                                        found_values.append([(key[0].lower(), key[1].lower(), obj[key[1].lower()] )])
                                                        
                                                    except:
                                                        failed = True
                                                
                                                if failed:

                                                    if "," in date_string:

                                                            # raise UserError(str(date_string))

                                                        if len(date_string.split()[0]) > 3:

                                                            obj[key[1].lower()] = datetime.strptime(date_string, '%B %d, %Y')
                                                            found_values.append([(key[0].lower(), key[1].lower(), obj[key[1].lower()] )])
                                                        
                                                        elif len(date_string.split()[0]) == 3:

                                                            obj[key[1].lower()] = datetime.strptime(date_string, '%b %d, %Y')
                                                            found_values.append([(key[0].lower(), key[1].lower(), obj[key[1].lower()] )])

                                        elif key[2] == 'float':

                                            if row.lower().startswith(key[0].lower()):
                                                
                                                obj[key[1].lower()] = re.findall("\d+\.\d+", " ".join(row.split()[len(key[0].split()):])) if re.findall("[\d,]+\.\d+", " ".join(row.split()[len(key[0].split()):])) else re.findall("[\d.]+\,\d+", " ".join(row.split()[len(key[0].split()):]))
                                                found_values.append([(key[0].lower(), key[1].lower(), obj[key[1].lower()] )])

                                                # break

                                        elif key[2] == 'char':

                                            if key[0].lower() + " " in row.lower():

                                                if len(key) == 5:

                                                    if key[4] == 'word':

                                                        value = " ".join(" ".join(row[row.lower().index(key[0].lower()) + len(key[0]):].split()).split()[:key[3]])

                                                        if value.startswith('...'):

                                                            for char in value:

                                                                if char == ".":

                                                                    value = value[1:]
                                                                
                                                                else:
                                                                    break
                                                        
                                                        obj[key[1].lower()] = value
                                                        found_values.append([(key[0].lower(), key[1].lower(), obj[key[1].lower()] )])
                                                    
                                                    elif key[4] == 'char':

                                                        value = "".join(row[row.lower().index(key[0].lower()) + len(key[0]):].split())

                                                        if value.startswith('...'):

                                                            for char in value:

                                                                if char == ".":

                                                                    value = value[1:]
                                                                
                                                                else:
                                                                    break
                                                        
                                                        obj[key[1].lower()] = value[:key[3]]
                                                        found_values.append([(key[0].lower(), key[1].lower(), obj[key[1].lower()] )])
                                                    
                                                else:

                                                    value = " ".join(row[row.lower().index(key[0].lower()) + len(key[0]):].split())

                                                    if value.startswith('...'):

                                                        for char in value:

                                                            if char == ".":

                                                                value = value[1:]
                                                            
                                                            else:
                                                                break
                                                    
                                                    obj[key[1].lower()] = value
                                                    
                                                    found_values.append([(key[0].lower(), key[1].lower(), obj[key[1].lower()] )])

                                                # break
                                        
                                        elif key[2] == 'vat-number':

                                            if key[0].lower() + " " in row.lower():
                                                    
                                                if not obj.get(key[1].lower(), False):
                                                    
                                                    found_number = " ".join(row[row.lower().index(key[0].lower()) + len(key[0]):].split())
                                                    our_vat = self.env.company.vat.lower() if self.env.company.vat else ""
                                                    our_registry = self.env.company.company_registry.lower() if self.env.company.company_registry else ""
                                                    skip = False

                                                    if our_vat != "":

                                                        if found_number.lower() in our_vat or our_vat in found_number.lower():

                                                            skip = True

                                                    if our_registry != "":
                                                        
                                                        if found_number.lower() in our_registry or our_registry in found_number.lower():

                                                            skip = True
                                                    
                                                    if skip == False:

                                                        if len(found_number.split()[0]) >= 8:

                                                            obj[key[1].lower()] = found_number.split()[0]
                                                            found_values.append([(key[0].lower(), key[1].lower(), obj[key[1].lower()] )])
                                                        
                                                        else:

                                                            obj[key[1].lower()] = found_number
                                                            found_values.append([(key[0].lower(), key[1].lower(), obj[key[1].lower()] )])

                                                # break


                        obj['found_values'] = found_values           

                        obj['table_lines'] = table_rows
                        
                    # table = page.extract_table()

                    obj['tables'] = page.extract_tables()

                    # if table:
                        
                    #     header=0
                    #     columns=list()
                    #     for column in table[header]:
                    #         if column!=None and len(column)>1:
                    #             columns.append(column)
                        # raise UserError(str(table))

                    doc.append(obj)

                pdf.close()

                # raise UserError(str(doc) + " | " + str(print(doc)) + " | " + str(obj))

        return doc



    def extract_text_pdf_danloen_bookkeeping_employee (self):

        doc = []

        for pdf_doc in self:

            bytes = b64decode(pdf_doc.datas, validate=True)

            reserve_pdf_on_memory = io.BytesIO(bytes)

            with pdfplumber.load(reserve_pdf_on_memory) as pdf:
                
                search_keys = [

                    ('Date', 'date'),
                    ('due date', 'due date'),
                    ('Balance Due', 'balance due'),
                    ('Subtotal', 'Subtotal'),
                    ('total', 'total'),
                    ('Notes', 'Notes'),
                    ('Leverandørnr', 'supplier_ref'),
                    ('Indkøber', 'supplier_purchaser'),
                    ('Telefon', 'supplier_phone'),
                    ('Telefax', 'supplier_fax'),
                    ('Bank', 'supplier_bank'),
                    ('Kontonr.', 'supplier_bank_account'),
                    ('Ordrenr', 'name'),
                    ('I alt DKK ekskl. moms', 'Subtotal'),
                    ('I alt DKK inkl. moms', 'total'),
                    ('25% moms', 'vat'),
                    ('Betalingsbetingelser', 'terms'),
                                
                
                ]
                

                order_details_re = re.compile(r'(\d.*) ([A-Z].*) ([\d.]+\,\d{2})' )
                name_line = re.compile(r'([A-Z].*)' )
                account_and_text_line = re.compile(r'([\d.]+\d{1}) ([A-Z].*)' )
                
                # ([\d.]+\,\d{2})  ([A-Z].*)

                for page in pdf.pages:

                    obj = {}
                    
                    text = page.extract_text()
                    
                    # raise UserError(str(text))

                    table_rows = []

                    employee_name = text.split('\n')[3]
                    obj['periode'] = text.split('\n')[2]
                    obj['name'] = text.split('\n')[1]

                    # for row in text.split('\n'):

                        # if name_line.match(row) and row != "Bogføringsgruppe: E-conomic":
                            
                        #     line = name_line.search(row)

                        #     employee_name = line.group(1)

                        # elif order_details_re.match(row):

                        #     line = order_details_re.search(row)

                        #     obj_rows = {}

                        #     obj_rows['employee'] = employee_name
                        #     obj_rows['account'] = line.group(1)
                        #     obj_rows['text'] = line.group(2)
                        #     obj_rows['debit'] = line.group(3)
                        #     obj_rows['credit'] = line.group(4)

                        #     table_rows.append(obj_rows)

                        # else:

                        #     for key in search_keys:

                        #         if row.lower().startswith(key[0].lower()):

                        #             obj[key[1].lower()] = " ".join(row.split()[len(key[0].split()):])

                        #             break
                    
                    tables = page.extract_table({
                        "vertical_strategy": "text",
                        "horizontal_strategy": "text",
                        "intersection_x_tolerance": 15
                    })

                    for row in tables:

                        obj_rows = {}

                        # raise UserError(str(row))
                        # try:

                        if order_details_re.match(' '.join(row)):

                            if len(row) == 4:

                                line = account_and_text_line.search(row[0] + ' ' + row[1])

                                if len(line.groups()) > 1:

                                    obj_rows['control'] = "Her 1"
                                    obj_rows['employee'] = employee_name
                                    obj_rows['account'] = line.group(1)
                                    obj_rows['text'] = line.group(2)
                                    obj_rows['debit'] = row[2]
                                    obj_rows['credit'] = row[3]

                                else:

                                    obj_rows['control'] = "Her 2"
                                    obj_rows['employee'] = employee_name
                                    obj_rows['account'] = row[0]
                                    obj_rows['text'] = row[1]
                                    obj_rows['debit'] = row[2]
                                    obj_rows['credit'] = row[3]
                            
                                table_rows.append(obj_rows)

                            elif len(row) == 3 and row[0]:

                                line = account_and_text_line.search(row[0])
                                
                                obj_rows['control'] = "Her 3"
                                obj_rows['employee'] = employee_name
                                obj_rows['account'] = line.group(1)
                                obj_rows['text'] = line.group(2)
                                obj_rows['debit'] = row[1]
                                obj_rows['credit'] = row[2]

                                table_rows.append(obj_rows)  

                        # except:

                            # continue                        
                    
                    obj['table_lines'] = table_rows

                    doc.append(obj)

                pdf.close()

                # raise UserError(str(doc) + " | " + str(print(doc)) + " | " + str(obj))

        return doc

    def action_analyse_ms_form_reciept(self, return_response = False):

        type = 'receipt'

        return self.analyse_ms_form(type,return_response)

    def action_analyse_ms_form_invoice(self, return_response = False):

        type = 'invoice'

        return self.analyse_ms_form(type,return_response)

    def action_analyse_ms_form_idDocument(self, return_response = False):

        type = 'idDocument'

        return self.analyse_ms_form(type,return_response)
    
    def action_analyse_ms_form_businessCard(self, return_response = False):

        type = 'businessCard'

        return self.analyse_ms_form(type,return_response)

    def action_analyse_ms_form(self, return_response = False):

        if self.ms_doc_type:

            return self.analyse_ms_form(self.ms_doc_type,return_response)

        return False

    def analyse_ms_form(self, type, return_response = False):

        existing = self.env['form.recognizer'].sudo().search([('status_code','=',200),('ir_attachment_id','=',self.id),('type','=',type),('response_data','!=',False)], order="id")

        if len(existing) == 0:

            file = b64decode(self.datas, validate=True)

            company = self.company_id

            subscription_key = company.ms_form_recognizer_subscription_key
            end_point = company.ms_form_recognizer_endpoint

            new_record = self.env['form.recognizer'].analyze_request_attached_pdf(subscription_key, end_point, file, type, self.id)
            
            if new_record.status_code in [200,202]:

                new_record_2 =  new_record.analyze_get_analyze_reciept_result(subscription_key, new_record.operation_location)
                
                if return_response:
                    return new_record_2.response_data

                else:

                    try:
                        form_view_id = self.env.ref("").id
                    except Exception as e:
                        form_view_id = False

                    return {

                        'type': 'ir.actions.act_window',
                        'name': 'From Recognizer',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_id': new_record_2.id,
                        'res_model': 'form.recognizer',
                        'views': [(form_view_id, 'form')],
                        'target': 'current',
                    }
                    
            else:

                if return_response:
                    return False

                else:
                        
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

        else:
            
            if return_response:
                return existing[-1].response_data

            else:

                try:
                    form_view_id = self.env.ref("").id
                except Exception as e:
                    form_view_id = False

                return {

                    'type': 'ir.actions.act_window',
                    'name': 'From Recognizer',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_id': existing[0].id,
                    'res_model': 'form.recognizer',
                    'views': [(form_view_id, 'form')],
                    'target': 'current',
                }


