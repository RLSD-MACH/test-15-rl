# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime, timedelta, date
from odoo.exceptions import AccessError, UserError, ValidationError

import requests

# from pdfplumber import pdfplumber
# pip install pdfplumber
# pip install pyperclip

class PdfRecognize(models.Model):
    
    _name = 'pdf.recognize'
    _description = 'PDF Recognize'
    _order = 'create_date desc'
    _check_company_auto = True

    # def action_extract_text_pdf (self):
        
    #     for pdf_doc in self:

    #         with pdfplumber.open(pdf_doc) as pdf:

    #             page = pdf[0]
    #             text = page.extract_text()

    #             raise UserError(str(text))

    