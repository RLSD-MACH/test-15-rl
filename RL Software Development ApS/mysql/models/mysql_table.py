from datetime import date, datetime
from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError
# import requests
import json


class MySQLTable(models.Model):
    
    _name = 'mysql.table'
    _description = 'MySQL table'
    _order = 'id'
    _check_company_auto = True
    
    login_id = fields.Many2one('mysql.login', string='Login', required=True)
    name = fields.Char(required=True,string='Name')    
    convertion_model_id = fields.Many2one('ir.model', string='Converts to Model', required=False) 
    field_ids = fields.One2many('mysql.table.column', 'table_id', string='Fields')
    row_ids = fields.One2many('mysql.table.row', 'table_id', string='Rows')
    active = fields.Boolean(required=True, string='Active', default=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
   

    def action_get_columns(self):

        for record in self:

            cnx = record.login_id._login()
            cursor = cnx.cursor()

            cursor.execute("SELECT COLUMN_NAME, ORDINAL_POSITION, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '" + record.name + "' ORDER BY 2;")

            result = cursor.fetchall()

            new = []
            existing = self.env['mysql.table.column'].search([['table_id','=',record.id]])

            # raise UserError(str(result))

            for row in result:

                if not any(row[0] == item.name for item in existing):

                    new.append({

                        'name': row[0],
                        'position': row[1],
                        'data_type': row[2],
                        'table_id': record.id

                    })

            self.env['mysql.table.column'].create(new)
                
            record.login_id._close_connection(cnx)

    def action_get_records(self):

        for record in self:

            cnx = record.login_id._login()
            cursor = cnx.cursor()

            cursor.execute("SELECT * FROM " + record.name + ";")

            result = cursor.fetchall()

            record.login_id._close_connection(cnx)

            for row in result:

                obj = record._get_obj_values(row)

                new_id = self.env[record.convertion_model_id.model].create(obj)
                
                data = list(row)
                
                self.env['mysql.table.row'].create({

                    'name': record.name + " - " + str(row[0]),
                    'model': record.convertion_model_id.model,
                    'old_id': row[0],
                    'new_id': new_id.id,
                    'data': json.dumps(data, indent=4, sort_keys=True, default=str),
                    'table_id': record.id

                })  

    def action_update_records(self):
            
        self.ensure_one()

        for row in self.row_ids:
            
            values = json.load(row.data)
            
            obj = self._get_obj_values(values)
            
            new_id = self.env[row.model].browse(row.new_id)

            new_id.update(obj)         

    def _get_obj_values(self, row):

        obj = {}

        for column in self.field_ids:
                
            if column.related_table_id and column.convertion_field_id and row[column.position-1]:

                fitting = self.env['mysql.table.row'].search([['old_id','=', row[column.position-1]],['table_id','=',column.related_table_id.id]])

                if len(fitting) == 1:

                    new_record = self.env[fitting[0].model].browse(fitting[0].new_id)
                    
                    obj[column.convertion_field_id.name] = new_record.id

                elif len(fitting > 1):

                    raise UserError("Multiple answers returned for related table: " + str(fitting) + " | search: table_id = " + str(column.related_table_id.id) + " /// old_id = " + str(row[column.position-1]))

                else:

                    raise UserError("No answers returned for related table: " + str(fitting) + " | search: table_id = " + str(column.related_table_id.id) + " /// old_id = " + str(row[column.position-1]))

            elif column.convertion_field_id:
                
                if self.name == 'tblProjectGroup' and column.convertion_field_id.name == 'type':

                    if row[column.position-1] == 'External':

                        obj[column.convertion_field_id.name] = 'external'
                    
                    elif row[column.position-1] == 'Internal':

                        obj[column.convertion_field_id.name] = 'internal'
                    
                    elif row[column.position-1] == 'No salary':

                        obj[column.convertion_field_id.name] = 'free work'

                else:

                    obj[column.convertion_field_id.name] = row[column.position-1]

                    if column.convertion_field_id.ttype in ['date','datetime']:

                        if obj[column.convertion_field_id.name] < date(1900,1,1):

                            obj[column.convertion_field_id.name] = date(1900,1,1)
                            
                    
            else:

                continue

        if self.name in ['tblProject','tblSubproject'] and 'stage_id' not in obj:

            if 'active' in obj:

                if obj['active']:

                    stages = self.env['rlbooks.project.stage'].search([['is_closed','=',False]])

                    if len(stages) > 0:

                        obj['stage_id'] = stages[0].id

                else:

                    stages = self.env['rlbooks.project.stage'].search([['is_closed','=',True]])

                    if len(stages) > 0:

                        obj['stage_id'] = stages[0].id

            else:

                obj['active'] = True 
            
        return obj