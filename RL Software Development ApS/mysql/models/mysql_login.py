from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError
import pyodbc #pip install pyodbc

class MySQLLogin(models.Model):
    
    _name = 'mysql.login'
    _description = 'MySQL login'
    _order = 'id'
    _check_company_auto = True

    name = fields.Char(required=False,string='Name')
    user = fields.Char(required=False,string='User')
    password = fields.Char(required=True,string='Password') 
    host = fields.Char(required=True,string='Host') 
    database = fields.Char(required=True,string='Database') 
    active = fields.Boolean(required=True, string='Active', default=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)  
    
    def _login(self):

        self.ensure_one()
        
        try:
            
            server = self.host
            database = self.database
            username = self.user
            password = '{%s}'  % self.password 
            driver= '{ODBC Driver 17 for SQL Server}'

            cnx = pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
            # cnx = pymssql.connect(
            #     # driver=driver,
            #     server=server, 
            #     port=1433,
            #     user=username, 
            #     password=password, 
            #     database=database,
            #     tds_version='7.2')
           
        except Exception as e:
            
                raise UserError("Failed connection - " + str(e))

        else:

            return cnx

    def _close_connection(self, cnx):

        self.ensure_one()

        cnx.close()

    def action_get_tables(self):

        self.ensure_one()

        cnx = self._login()
        cursor = cnx.cursor()

        cursor.execute("SELECT table_name FROM information_schema.tables;")

        result = cursor.fetchall()

        new_tables = []
        existing = self.env['mysql.table'].search([['login_id','=',self.id]])

        for row in result:

            if not any(row[0] == item.name for item in existing):

                new_tables.append({

                    'name': row[0],
                    'login_id': self.id

                })

        self.env['mysql.table'].create(new_tables)
            

        self._close_connection(cnx)