# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime, timedelta, date
from odoo.exceptions import AccessError, UserError, ValidationError

class FormCollection(models.Model):
    
    _name = 'form.collection'
    _description = 'Form Collection'
    _check_company_auto = True

    name = fields.Char(required=True,string='Name')    
    convertion_model_id = fields.Many2one('ir.model', string='Converts to Model', required=False) 
    key_ids = fields.One2many('form.key', 'collection_id', string='Keys')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    active = fields.Boolean(required=True, string='Active', default=True, copy=False)

class FormKey(models.Model):
    
    _name = 'form.key'
    _description = 'Form Key'
    _order = 'sequence desc'
    _check_company_auto = True

    def _get_default_collection_id(self):
        default_collection_id = self.env.context.get('default_collection_id')
        return [default_collection_id] if default_collection_id else None

    sequence = fields.Integer(string='Sequence')
    collection_id = fields.Many2one('form.collection', string='Collection', required=True, default=_get_default_collection_id)
    convertion_model_id = fields.Many2one('ir.model', related="collection_id.convertion_model_id") 
    convertion_field_id = fields.Many2one('ir.model.fields', string='Converts to Field', required=True, ondelete="cascade", domain="[('model_id', '=', convertion_model_id)]")
    
    type = fields.Selection(selection=[
        ('date', 'Date'),
        ('char', 'Text'),
        ('float', 'Float'),
        ('regex', 'RegEx'),
        ('vat-number', 'Vat-number'),
        ('web', 'Webpage'),
        ('phone', 'Phone'),
        ('email', 'Email'),

    ],string='Type',  required=True)
    split = fields.Boolean('Split', default=False)
    split_type = fields.Selection(selection=[
        ('word', 'Words'),
        ('char', 'Characters'),

    ],string='Split Type',  required=False)
    use_word_number = fields.Integer(string='Use word number', default=0)
    
    search_for = fields.Char(string='Search for', required=True)
    allow_partial = fields.Boolean('Allow partial', default=False)
    regex = fields.Char(string='Regex', required=False)
    language = fields.Selection(selection=[
        ('DA', 'Danish'),
        ('EN', 'English'),
        ('DE', 'German'),
        ],string='Language',  required=True)
    
    ('Date', 'date', 'date', 'EN'),
    ('Date of issue:', 'date', 'date', 'EN'),   

    company_id = fields.Many2one('res.company', readonly=True, related="collection_id.company_id")
    active = fields.Boolean(readonly=True, related="collection_id.active")
