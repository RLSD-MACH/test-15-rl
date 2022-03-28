from odoo import models, fields, api, _
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError, UserError
import requests
import json
import urllib.parse

class ProjectEntry(models.Model):

    _name = 'rlbooks.project.entry'
    _description = 'Project entry'
    _order = 'date'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True

    def _get_default_project_id(self):
        default_project_id = self.env.context.get('default_project_id')
        return [default_project_id] if default_project_id else None

    def _get_default_date(self):
        default = self.env.context.get('default_date')
        return [default] if default else datetime.today()

    def _get_default_user_id(self):
        default = self.env.context.get('default_user_id')
        return [default] if default else self.env.uid

    def _get_default_type(self):
        default = self.env.context.get('default_type')
        return [default] if default else 'hours'

    def _get_default_report_id(self):

        report_id = self.env.context.get('default_report_id')
        return report_id if report_id else None
  
    name = fields.Char(required=False,string='Name')

    qty_spent = fields.Float(required=True, string='Qty spent', default=0, tracking=True)
    qty_invoiceable = fields.Float(required=True, string='Qty invoiceable', default=0, tracking=True)

    approved = fields.Boolean(required=True, string='Approved', default=False,tracking=True)
    date = fields.Date(required=True, string='Date', tracking=True, default=_get_default_date)
    deleted = fields.Boolean(required=True, string='Deleted', default=False,tracking=True)
    sales_invoice_id = fields.Many2one("account.move", string='Invoice', ondelete='set null', required=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    sales_invoice_line_id = fields.Many2one("account.move.line", string='Invoice line', ondelete='restrict', required=False, domain="['|', '&', ('company_id', '=', False), ('company_id', '=', company_id),('move_id','=',sales_invoice_id),('exclude_from_invoice_tab','=',False)]")
    
    locked = fields.Boolean(required=True, string='Locked', default=False,tracking=True)
    timesheet_id = fields.Many2one("rlbooks.timesheet.timesheet", string='Timesheet', ondelete='restrict', required=False, readonly=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    move_id = fields.Many2one("account.move", string='Journal entry', ondelete='restrict', required=False, readonly=True, related='move_line_id.move_id', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    move_line_id = fields.Many2one("account.move.line", string='Journal item', ondelete='restrict', required=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    sale_order_id = fields.Many2one("sale.order", string='Sale order', ondelete='set null', required=False, readonly=True, related='sale_order_line_id.order_id', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    sale_order_line_id = fields.Many2one("sale.order.line", string='Sale order line', ondelete='set null', required=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    open = fields.Boolean(required=True, string='Open', default=True, tracking=False)
    product_id = fields.Many2one("product.product", string='Product',ondelete='restrict', required=False, domain="[('type', '=', 'service'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    project_id = fields.Many2one("rlbooks.project.project", 
        string='Project', 
        ondelete='restrict', 
        required=True, 
        default=_get_default_project_id, 
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]"
    )
    work_hours = fields.Float(required=True, string='Work hours', default=0, tracking=True)

    r_costprice = fields.Float(required=True, string='Realised costprice', default=0, tracking=False)
    r_costprice_t = fields.Float(required=False, string='Realised costprice total', compute='_compute_r_costprice_t', tracking=False, readonly=True, store=True, copy= False, default=0)
    r_salesprice = fields.Float(required=True, string='Realised salesprice', default=0, tracking=False)
    r_salesprice_t = fields.Float(required=False, string='Realised salesprice total', compute='_compute_r_salesprice_t', tracking=False, readonly=True, store=True, copy= False, default=0)

    s_costprice = fields.Float(required=True, string='Standard costprice', default=0, tracking=False)
    s_costprice_t = fields.Float(required=False, string='Standard costprice total', compute='_compute_s_costprice_t', tracking=False, readonly=True, store=True, copy= False)
    
    salesprice = fields.Float(required=True, string='Price', default=0, tracking=True, help="Salesprice per quantity")
    discount = fields.Float(required=True, string='Discount %', default=0, tracking=True)
    s_salesprice = fields.Float(required=False, string='Est. salesprice', compute='_compute_s_salesprice', tracking=False, readonly=True, store=True, copy= False, help="Estimated sales price")
    s_salesprice_t = fields.Float(required=False, string='Est. salesprice total', compute='_compute_s_salesprice_t', tracking=False, readonly=True, store=True, copy= False, help="Estimated sales price total")

    description = fields.Text(required=False, string='Description', tracking=False)
    user_id = fields.Many2one("res.users", string='User', default=_get_default_user_id, tracking=True, ondelete='restrict', required=False) 
    type = fields.Selection(selection = [('hours', 'Hours'), ('mileage', 'Mileage'), ('expense', 'Expense'), ('revenue', 'Revenue'), ('manual adjustment', 'Manuel adjustment'), ('system adjustment', 'System adjustment')], required=True,string='Type',default=_get_default_type)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
        
    #mileage

    report_id = fields.Many2one("rlbooks.mileage.report", string='Report', ondelete='restrict', default=_get_default_report_id, required=False, readonly=False)
    # date = fields.Date(required=True, string='Date', tracking=True, default= datetime.today())
    # project_id = fields.Many2one("rlbooks.project.project", string='Project', ondelete='restrict', required=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    partner_id = fields.Many2one("res.partner", string='Customer', ondelete='restrict', required=False, readonly=True, related='project_id.partner_id')
    contact_id = fields.Many2one("res.partner", string='Contact', ondelete='restrict', required=False, readonly=True, related='project_id.contact_id')    
    from_id = fields.Many2one("res.partner", string='From', ondelete='restrict', required=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    to_id = fields.Many2one("res.partner", string='To', ondelete='restrict', required=False, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    start_address = fields.Text(string='Start address', required=False)    
    end_address = fields.Text(string='End address', required=False)
    # description = fields.Text(string='Description', required=True)
    distances_gms = fields.Text(required=False, string='Distance Google Maps')
    distances_gms_no_route = fields.Boolean(string='GMS - no route', default=False)
    # cost = fields.Float(required=True, string='Cost', default=0, readonly=False)
    vehicle_id = fields.Many2one('vehicle', related="report_id.vehicle_id")
    # value = fields.Float(required=False, string='Value', compute='_compute_value', store=True, readonly=True)

    @api.model
    def create(self, values):
        
        if values.get('type') == 'hours':

            project = self.env['rlbooks.project.project'].browse(values.get('project_id'))

            group = self.env['rlbooks.project.group'].browse(project.group_id.id)
        
            contract = self.env['hr.contract'].search([['employee_id.user_id','=',values.get('user_id')],['date_start','<=',values.get('date')],'|',['date_end','=',False],['date_end','>=',values.get('date')]], limit=1, order='date_start')

            if contract:

                if contract.invoiceable_hourrate == 0 or contract.product_id == False:

                    raise UserError("Contract found but product or hourrate is not filled in.")
                
                else:

                    values['s_costprice'] = contract.standard_costprice_hourrate
                    values['r_costprice'] = contract.real_costprice_hourrate
                    values['salesprice'] = contract.invoiceable_hourrate
                    values['product_id'] = contract.product_id.id

            else:

                raise UserError("No contract found for this employee regarding this date.")

            if group.cost_price == False:

                values['s_costprice'] = 0
                values['r_costprice'] = 0
            
            if group.sales_price == False:

                values['salesprice'] = 0

            if group.overtime != False:

                values['work_hours'] = values.get('qty_spent')

            else:

                values['work_hours'] = 0
            
            if group.type == "external":

                values['qty_invoiceable'] = values.get('qty_spent')

            else:

                values['qty_invoiceable'] = 0

            if values.get('project_id', False) != False:

                values['discount'] = project.discount
            
            else:

                values['discount'] = 0

            values['name'] = 'Timeregistration'

            start = date.fromisoformat(str(values.get('date')))
            start = start - timedelta(days=start.weekday())

            timesheets = self.env['rlbooks.timesheet.timesheet'].search([['user_id','=',values.get('user_id')],['start','=',start]])

            if len(timesheets) > 0:

                if len(timesheets) == 1:

                    if timesheets[0].state == 'approved':

                        timesheets[0].state = 'ammented'

                else:

                    raise UserError("There exists more than one timesheet for the selected date?")

            else:

                self.env['rlbooks.timesheet.timesheet'].create({

                    'start': values.get('date'),
                    'user_id': values.get('user_id'),
                    'company_id': values.get('company_id')

                })
        
        elif values.get('type') == 'mileage':

            project = self.env['rlbooks.project.project'].browse(values.get('project_id'))
            cost = self.env['mileage.cost'].search([
                    ['company_id','=',values.get('company_id')],
                    ['project_group_id','=', project.group_id.id],
                    ['date_from','<=',values.get('date')],
                    ['date_to','>=',values.get('date')],
                    ], limit=1)
                
            if cost:

                values['r_costprice'] = cost.cost
            
            else:

                raise UserError("No mileage cost were given for this date. Please add a mileage cost in the settings for this project group for a periode containing the specified date.")

            
            values['s_costprice'] = values['r_costprice']            
            values['salesprice'] = values['r_costprice'] 
            values['qty_invoiceable'] = values['qty_spent'] if project.mileage_invoiced else 0
            values['name'] = 'Mileage'

            report = self.env['rlbooks.mileage.report'].browse(values.get('report_id'))
            values['user_id'] = report.user_id.id
            

        if values.get('product_id', False) == False and  values.get('type', False) != 'mileage':

            raise UserError("You need to specify a product! | " + str(values) )


        return super(ProjectEntry, self).create(values)
    
    # @api.constrains('type')
    # def _check_type(self):

    #     for record in self:

    #         if record.type == 'mileage':

    #             #product_id
    #             test = 1

    #         elif record.type == 'hours':

    #             #product_id
    #             test = 1

    #         else:

    #             raise ValidationError("Select a product!")

    @api.depends('r_costprice', 'qty_spent')
    def _compute_r_costprice_t(self):

        for entry in self:
           
            entry.r_costprice_t = entry.r_costprice * entry.qty_spent

    @api.depends('r_salesprice', 'qty_invoiceable')
    def _compute_r_salesprice_t(self):

        for entry in self:
           
            entry.r_salesprice_t = entry.r_salesprice * entry.qty_invoiceable

    @api.depends('s_costprice', 'qty_spent')
    def _compute_s_costprice_t(self):

        for entry in self:
           
            entry.s_costprice_t = entry.s_costprice * entry.qty_spent

    @api.depends('salesprice', 'discount')
    def _compute_s_salesprice(self):

        for entry in self:
           
            entry.s_salesprice = entry.salesprice * (1 - entry.discount/100)


    @api.depends('s_salesprice', 'qty_invoiceable')
    def _compute_s_salesprice_t(self):

        for entry in self:
           
            entry.s_salesprice_t = entry.s_salesprice * entry.qty_invoiceable

    @api.onchange('project_id', 'date')
    def _onchange_project_id(self):
        
        for record in self:

            if record.project_id and record.type == 'mileage':
    
                cost = self.env['mileage.cost'].search([
                    ['company_id','=',record.company_id.id],
                    ['project_group_id','=', record.project_id.group_id.id],
                    ['date_from','<=',record.date],
                    ['date_to','>=',record.date],
                    ], limit=1)
                
                if cost:

                    record.update({
                        
                        'r_costprice': cost.cost
                    
                    })
                
                else:

                    raise UserError("No mileage cost were given for this date. Please add a mileage cost in the settings for this project group for a periode containing the specified date.")

            elif record.type == 'mileage':

                record.update({
                    
                    'r_costprice': 0
                })

    @api.onchange('from_id')
    def _onchange_from_id(self):
        
        for record in self:

            if record.from_id:
    
                record.update({
                    
                    'start_address': str(record.from_id.contact_address)                   
                })

            else:

                record.update({
                    
                    'start_address': ""
                })

    @api.onchange('to_id')
    def _onchange_to_id(self):
        
        for record in self:

            if record.to_id:
    
                record.update({
                    
                    'end_address': str(record.to_id.contact_address)
                })

            else:

                record.update({
                    
                    'end_address': ""
                })
    
    @api.onchange('end_address', 'start_address')
    def _onchange_address(self):
        
        for record in self:
    
            record.update({
                
                'distances_gms': False,
                'distances_gms_no_route': False

            })

    def action_invoice_entries(self):

        projects = []

        for entry in self:

            if entry.project_id.id not in projects:

                projects.append(entry.project_id.id)

        for project in projects:

            customer = self.env['rlbooks.project.project'].browse(project).partner_id

            order = self.env['sale.order'].create({

                'partner_id': customer.id,
                'rlbooks_project_id': project

            })

            for entry in self:

                if entry.project_id.id == project and entry.sale_order_line_id.id == False:

                    description = "-"

                    if entry.description != False and entry.description != "":

                        description = entry.description


                    order_line = self.env['sale.order.line'].create({

                        'order_id': order.id,
                        'product_id': entry.product_id.id,
                        'product_uom_qty': entry.qty_invoiceable,
                        'discount': entry.discount,
                        'price_unit': entry.salesprice,
                        'name': description,
                        'purchase_price': entry.r_costprice

                    })

                    entry.update({

                        'sale_order_line_id': order_line.id

                    })

        if len(projects) == 1:

            return {

                'type': 'ir.actions.act_window',
                'name': 'Sale order',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'sale.order',
                "res_id": order.id,
                'views': [(self.env.ref("sale.view_order_form").id, 'form')],
                'target': 'current',

            }


        message = 'I dont know if we made any money, but now it\'s done :) Invoices created: ' + len(projects)

        return {
            'effect': {
                'fadeout': 'slow',
                'message': message,
                'img_url': '/web/static/src/img/smile.svg',
                'type': 'rainbow_man',
            }
        }
    
    def action_remove_from_move(self):

        self.write({'sales_invoice_id': False})

    def action_account_invoice_entries(self):

        projects = []
        entries = []

        for entry in self:

            if entry.project_id.id not in projects:

                projects.append(entry.project_id.id)
                entries.append([])

            entries[len(projects)-1] += entry
        
        x = 0

        for project in projects:

            x += 1

            product_val = self.env['rlbooks.project.project'].browse(project)

            invoice_vals = product_val._prepare_invoice()
            invoice_line_vals = []

            entries_project = entries[x-1]

            entry_type = {}

            hours = []
            expense = []
            revenue = []
            manual_adjustment = []
            system_adjustment = []

            for entry in entries_project:

                if entry.type == 'hours':  hours.append(entry)
                elif entry.type == 'expense':  expense.append(entry)
                elif entry.type == 'revenue':  revenue.append(entry)
                elif entry.type == 'manual adjustment':  manual_adjustment.append(entry)
                elif entry.type == 'system adjustment':  system_adjustment.append(entry)
            
            if len(hours) > 0:

                products = []

                for entry in hours:

                    if entry.product_id not in products:

                        products.append(entry.product_id)

                for product in products:

                    quantity = 0
                    total_pris_before_discount = 0
                    total_pris_after_discount = 0

                    for entry in hours:
                    
                        if entry.product_id == product:

                            quantity += entry.qty_invoiceable
                            total_pris_before_discount += entry.qty_invoiceable * entry.salesprice
                            total_pris_after_discount += entry.qty_invoiceable * entry.s_salesprice
                    
                            description = "-"

                            if entry.description != False and entry.description != "":

                                description = entry.description

                    if total_pris_before_discount == 0:

                        discount = 0

                    else:

                        discount = (total_pris_before_discount - total_pris_after_discount) / total_pris_before_discount * 100


                    invoice_line_vals.append(
                        (0, 0, {

                        'product_id': product.id,
                        'product_uom_id': product.uom_id.id,
                        'account_id': product.property_account_income_id.id,
                        'quantity': quantity,
                        'discount': discount,
                        'price_unit': total_pris_before_discount / quantity,
                        'name': product.description_sale,
                        'rlbooks_project_id': project,
                        'exclude_from_invoice_tab': False

                    }),
                    )

            
            elif len(expense) > 0:

                for entry in expense:
                  
                    if entry.project_id.id == project:

                        entries.append(entry)
                
                        description = "-"

                        if entry.description != False and entry.description != "":

                            description = entry.description

                        invoice_line_vals.append(
                            (0, 0, {

                            'product_id': entry.product_id.id,
                            'product_uom_id': entry.product_id.uom_id.id,
                            'account_id': entry.product_id.property_account_income_id.id,
                            'quantity': entry.qty_invoiceable,
                            'discount': entry.discount,
                            'price_unit': entry.salesprice,
                            'name': description,
                            'rlbooks_project_id': project,
                            'exclude_from_invoice_tab': False

                        }),
                        )

            
            elif len(revenue) > 0:

                for entry in revenue:
                  
                    if entry.project_id.id == project:

                        entries.append(entry)
                
                        description = "-"

                        if entry.description != False and entry.description != "":

                            description = entry.description

                        invoice_line_vals.append(
                            (0, 0, {

                            'product_id': entry.product_id.id,
                            'product_uom_id': entry.product_id.uom_id.id,
                            'account_id': entry.product_id.property_account_income_id.id,
                            'quantity': entry.qty_invoiceable,
                            'discount': entry.discount,
                            'price_unit': entry.salesprice,
                            'name': description,
                            'rlbooks_project_id': project,
                            'exclude_from_invoice_tab': False

                        }),
                        )


            # elif proentry_typeject.get('manual adjustment',False) != False:


            # elif entry_type.get('system adjustment',False) != False:
           

            # 'display_type': self.display_type,
            # 'sequence': self.sequence, 
            # 'analytic_account_id': self.order_id.analytic_account_id.id,
            # 'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            
            invoice_vals['invoice_line_ids'] = invoice_line_vals

            move_id = self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(invoice_vals)

            for line in move_id.invoice_line_ids:

                line._onchange_account_id()

            for entry in self:
                
                entry.sales_invoice_id = move_id.id   
                entry.sales_invoice_line_id = False 

        if len(projects) == 1:

            return {

                'type': 'ir.actions.act_window',
                'name': 'Invoice',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.move',
                "res_id": move_id.id,
                'views': [(self.env.ref("account.view_move_form").id, 'form')],
                'target': 'current',

            }


        return {

            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'view_type': 'tree',
            'view_mode': 'tree',
            'res_model': 'account.move',
            "res_id": move_id.id,
            'views': [(self.env.ref("account.view_out_invoice_tree").id, 'tree')],
            'target': 'current',

        }

    def action_calc_distances_gms(self):


        url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins=%s&destinations=%s&departure_time=now&key=%s" % (urllib.parse.quote_plus(self.start_address), urllib.parse.quote_plus(self.end_address), self.env.company.google_maps_api_key)

        payload={}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)

        self.update({

            'distances_gms': "<pre><code>" + response.text + "</code></pre>"

        })

        response_object = json.loads(response.text)

        if response_object['status'] == "OK":

            if len(response_object['rows']) > 0:

                if len(response_object['rows'][0]['elements']) > 0:

                    if response_object['rows'][0]['elements'][0].get('distance', False) != False:

                        self.qty_spent = response_object['rows'][0]['elements'][0]['distance']['value'] / 1000

                    else:

                        if response_object['rows'][0]['elements'][0]['status'] == "ZERO_RESULTS":

                            self.distances_gms_no_route = True
                        
                        else:

                            raise UserError(response.text)

                else:

                    raise UserError(response.text)

            else:

                raise UserError(response.text)

        else:

            raise UserError(response.text)

    def action_show_distances_gms(self):

        raise UserError(self.distances_gms)

    def action_dublicate(self):

        self.copy()



