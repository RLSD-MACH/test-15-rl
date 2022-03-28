from odoo import models, fields, api
from datetime import datetime

class CreateEntryWizard(models.TransientModel):

    _name = 'rlbooks.project.entry.create.wizard'
    _description = 'Create project entry'

    def _get_default_project_id(self):
        default_project_id = self.env.context.get('default_project_id')
        return [default_project_id] if default_project_id else None
  
    description = fields.Text(string='Description')
    amount = fields.Float(required=True, string='Amount')
    user_id = fields.Many2one("res.users", string='Responsible', default=lambda self: self.env.uid, ondelete='restrict')    
    project_id = fields.Many2one("rlbooks.project.project", string='Project', ondelete='restrict', required=True, default=_get_default_project_id, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    date = fields.Date(required=True, string='Date', default= datetime.today())    
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)

    def action_create_time_entry(self):
                
        group = self.env['rlbooks.project.group'].browse(self.project_id.group_id.id)
        product_id = False

        if group.cost_price != False or group.sales_price != False:

            contract = self.env['hr.contract'].search([['employee_id.user_id','=',self.user_id.id],['date_start','<=',self.date],'|',['date_end','=',False],['date_end','>=',self.date]], limit=1, order='date_start')

            if contract == False:

                s_costprice = 0
                r_costprice = 0
                salesprice = 0

            else:

                s_costprice = contract.standard_costprice_hourrate
                r_costprice = contract.real_costprice_hourrate
                salesprice = contract.invoiceable_hourrate
                product_id = contract.product_id.id
        

        if group.cost_price == False:

            s_costprice = 0
            r_costprice = 0
        
        if group.sales_price == False:

            salesprice = 0

        if group.overtime != False:

            work = self.amount

        else:

            work = 0
        
        if group.type == "external":

            qty_invoiceable = self.amount

        else:

            qty_invoiceable = 0

        if self.project_id.id != False:

            discount = self.project_id.discount
        
        else:

            discount = 0

        vals = {

            'name': 'Timeregistration',          
            'description': self.description,
            'project_id': self.project_id.id,
            'user_id': self.user_id.id,
            'company_id': self.company_id.id,
            'r_costprice': r_costprice,
            's_costprice': s_costprice,
            'salesprice': salesprice,
            'qty_spent': self.amount,
            'qty_invoiceable': qty_invoiceable,
            'work_hours': work,
            'date': self.date,
            'product_id': product_id,
            'discount': discount,
            'type': 'hours'          

        }

        self.env['rlbooks.project.entry'].create(vals)
        pass
        



    

