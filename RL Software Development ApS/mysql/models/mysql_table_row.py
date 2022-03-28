from odoo import api, fields, models


class MySQLTableRow(models.Model):
    
    _name = 'mysql.table.row'
    _description = 'MySQL table row'
    _order = 'id'
    _check_company_auto = True
    
    table_id = fields.Many2one('mysql.table', string='Table', required=True)
    name = fields.Char(required=True,string='Name')    
    model = fields.Char(required=True,string='Model')  
    old_id = fields.Integer(string='Old ID')
    new_id = fields.Integer(string='New ID')
    data = fields.Text('Data')
     
    active = fields.Boolean(required=True, string='Active', default=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
   