from odoo import api, fields, models


class MySQLTableColumn(models.Model):
    
    _name = 'mysql.table.column'
    _description = 'MySQL table column'
    _order = 'id'
    _check_company_auto = True
    
    table_id = fields.Many2one('mysql.table', string='Table', required=True)
    name = fields.Char(required=True,string='Name')    
    position = fields.Integer(string='Position')
    data_type = fields.Char(required=True,string='Data Type') 
    convertion_model_id = fields.Many2one('ir.model', related="table_id.convertion_model_id") 
    convertion_field_id = fields.Many2one('ir.model.fields', string='Converts to Field', required=False, domain="[('model_id', '=', convertion_model_id)]")
    
    related_table_id = fields.Many2one('mysql.table', string='Related table')
   
    active = fields.Boolean(required=True, string='Active', default=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
   