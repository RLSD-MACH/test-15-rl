# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CVRMessage(models.Model):
    
    _name = 'cvr.message'
    _description = 'CVR message'
    _order = 'create_date desc'
    _check_company_auto = True

    vat_number = fields.Char(required=True,string='VAT number')
    valid = fields.Boolean(required=True, string='Valid')
    request_identifier = fields.Char(required=True,string='Request Identifier')
    # countryCode = fields.Char(required=True,string='Country Code')
    # vatNumber = fields.Char(required=True,string='VAT Number')
    requestDate = fields.Char(required=True,string='Request Date')
    partner_id = fields.Many2one("res.partner", string='Partner', ondelete='set null', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")    
    full_response = fields.Text(required=True, string="Full response", store=True )
    full_request = fields.Text(required=True, string="Full request", store=True )
    
    company_id = fields.Many2one('res.company', 'Company', required=False, index=True, default=lambda self: self.env.company)
    active = fields.Boolean(required=True, string='Active', default=True, copy=False)
        
    @api.depends(lambda self: (self._rec_name,) if self._rec_name else ())
    def _compute_display_name(self):

        names = dict(self.name_get())
        for record in self:

            if record.request_identifier:

                record.display_name = record.request_identifier
            
            else:

                record.display_name = "Invalid"