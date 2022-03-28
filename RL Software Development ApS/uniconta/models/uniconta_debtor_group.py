from odoo import api, fields, models


class UnicontaDebtorGroup(models.Model):
    
    _name = 'uniconta.debtor.group'
    _description = 'Uniconta Debtor Group'
    _order = 'id'
    _check_company_auto = True

    name = fields.Char(required=False,string='Name')
    uniconta_row_id = fields.Integer(string='Row ID')
    uniconta_keystr = fields.Char(string='Key String')    
    uniconta_firm_id = fields.Many2one('uniconta.firm', string='Firm')

    res_partner_group_id = fields.Many2one('res.partner.group', string='Contact group')

    active = fields.Boolean(required=True, string='Active', default=True)
        
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
   

  
    