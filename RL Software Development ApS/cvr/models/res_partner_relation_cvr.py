# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError
import requests
import base64
import json

class ResPartnerRelationCVR(models.Model):
    
    _name = 'res.partner.relation.cvr'
    _description = 'Partner Relation CVR'
    _order = 'type desc'
    _check_company_auto = True

    cvr_id = fields.Char(string='Entity number',readonly=False)
    having_partner_id = fields.Many2one('res.partner', string='Partner')
    regardig_partner_id = fields.Many2one('res.partner', string='Partner')
    type = fields.Char(required=True,string='Type')    
    name = fields.Char(required=True,string='Name')   
    attributes = fields.Text('Attributes',help='')
    valid_from = fields.Date(string='Valid from')
    valid_to = fields.Date(string='Valid to')

    def action_create_from_cvr(self):

        for record in self:

            if record.type == "VIRKSOMHED":
                
                term = 'Vrvirksomhed.enhedsNummer'
                value = record.cvr_id
            
            else:

                term = 'Vrdeltagerperson.enhedsNummer'
                value = record.cvr_id

            relations = self.env['res.partner.relation.cvr'].search([['cvr_id','=',record.cvr_id],['having_partner_id','!=',False]])

            if len(relations) == 0:

                obj = record.regardig_partner_id.control_vat_on_cvr(silent=False, vat_obj = value, term = term)
                
                new = self.env['res.partner'].create(obj)

                relations = self.env['res.partner.relation.cvr'].search([['cvr_id','=',record.cvr_id]])

                relations.write({

                    'having_partner_id': new.id

                })

                if len(self) == 1:

                    try:
                        form_view_id = self.env.ref("base.view_partner_form").id
                    except Exception as e:
                        form_view_id = False


                    return {

                        'type': 'ir.actions.act_window',
                        'name': 'Partner',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_id': new.id,
                        'res_model': 'res.partner',
                        'views': [(form_view_id, 'form')],
                        'target': 'current',
                    }

            else:

                partners = []
                partner_names = []

                for relation in relations:

                    if relation.having_partner_id.id not in partners:

                        partners.append(relation.having_partner_id.id)
                        partner_names.append(relation.name)

                if len(partners) == 1:

                    relations = self.env['res.partner.relation.cvr'].search([['cvr_id','=',record.cvr_id],['having_partner_id','=',False]])

                    relations.write({

                        'having_partner_id': partners[0]

                    })

                else:

                    raise UserError("%s contact(s) already fit the ID from CVR and exists in your system. Please take a look at these: %s") % (len(partners), ", ".join(partner_names))


                if len(self) == 1:

                    try:
                        form_view_id = self.env.ref("base.view_partner_form").id
                    except Exception as e:
                        form_view_id = False


                    return {

                        'type': 'ir.actions.act_window',
                        'name': 'Partner',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_id': partners[0],
                        'res_model': 'res.partner',
                        'views': [(form_view_id, 'form')],
                        'target': 'current',
                    }


    
