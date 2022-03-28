from odoo import api, fields, models,  _

class InsuranceCompany(models.Model):
    
    _name = 'insurance.company'
    _description = 'Insurance company'
    _order = 'name asc'

    name = fields.Char(required=True, string='Name')
    homepage = fields.Char(required=True, string='Homepage')    
    country_id = fields.Many2one('res.country', string='Country', required=False,)
    active = fields.Boolean(required=True, string='Active', default=True, copy=False)  

    def action_visit_webpage(self):
        
        return {
            "type": "ir.actions.act_url",
            "url": self.homepage,
            "target": "new",
        }
   
