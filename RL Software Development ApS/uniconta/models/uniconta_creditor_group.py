from odoo import api, fields, models


class UnicontaCreditorGroup(models.Model):
    
    _name = 'uniconta.creditor.group'
    _description = 'Uniconta Creditor Group'
    _order = 'id'
    _check_company_auto = True

    name = fields.Char(required=False,string='Name')
    uniconta_row_id = fields.Integer(string='Row ID')
    uniconta_keystr = fields.Char(string='Key String')    
    uniconta_firm_id = fields.Many2one('uniconta.firm', string='Firm')

    res_partner_group_id = fields.Many2one('res.partner.group', string='Contact group')

    active = fields.Boolean(required=True, string='Active', default=True)
        
    model_id = fields.Many2one('ir.model', 'Model', required=False)

    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
   

  
    