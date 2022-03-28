
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from odoo.exceptions import ValidationError, UserError

class Contacts(models.Model):
    
    _name = "res.partner"
    _inherit = 'res.partner'

    def _compute_statements_count(self):

        statements = self.env['rlbooks_statement.report.print']
        for partner in self:
            partner.statements_count = statements.search_count([('partner_id','=', partner.id)])
    
    def _compute_bonus_statements_count(self):

        statements = self.env['rlbooks_statement.bonus_report.print']
        for partner in self:
            partner.bonus_statements_count = statements.search_count([('partner_id','=', partner.id)])

    statements_count = fields.Integer(compute='_compute_statements_count', string="Statements Count")
    bonus_statements_count = fields.Integer(compute='_compute_bonus_statements_count', string="Bonus Statements Count")

    property_bonus_schema = fields.Boolean(company_dependent=True, required=False, string='Earns bonus', default=False, tracking=True)

    property_bonus_goods = fields.Float( 
        company_dependent=True,
        string='Bonus % goods',
        help="", 
        required=False, 
        default=0, tracking=True)

    property_bonus_consus = fields.Float( 
        company_dependent=True,
        string='Bonus % consus',
        help="", 
        required=False, 
        default=0, tracking=True)
    
    property_bonus_services = fields.Float( 
        company_dependent=True,
        string='Bonus % services',
        help="", 
        required=False, 
        default=0, tracking=True)

    @api.constrains('property_bonus_goods')
    def _check_property_bonus_goods(self):

        for record in self:

            if record.property_bonus_goods:

                if record.property_bonus_goods > 1 or record.property_bonus_goods < -1:

                    record.property_bonus_goods = 0

                    raise ValidationError("A bonus can only be between -100% and 100%")

    @api.constrains('property_bonus_consus')
    def _check_property_bonus_consus(self):

        for record in self:

            if record.property_bonus_consus:

                if record.property_bonus_consus > 1 or record.property_bonus_consus < -1:

                    record.property_bonus_consus = 0

                    raise ValidationError("A bonus can only be between -100% and 100%")
    
    @api.constrains('property_bonus_services')
    def _check_property_bonus_services(self):

        for record in self:

            if record.property_bonus_services:

                if record.property_bonus_services > 1 or record.property_bonus_services < -1:

                    record.property_bonus_services = 0

                    raise ValidationError("A bonus can only be between -100% and 100%")

class StatementReport(models.AbstractModel):

    _name = 'report.rlbooks_statement.report_partner_statement'
    _description = 'Partner Statement Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        
        docs = []

        for doc in docids:

            doc = self.env['rlbooks_statement.report.print'].browse(doc)

            if len(doc.account_ids.ids) == 0:

                raise UserError("Please go to setting and add the necessary accounts for the report!")

            lines = self.env['account.move.line'].search([['company_id','=',doc.company_id.id],['date','>=',doc.date_start],['date','<=',doc.date_end],['partner_id','=',doc.partner_id.id],['account_id.id','in',doc.account_ids.ids],['parent_state', 'in', ['posted']]], order='date desc')
            
            self.env.cr.execute(
                "SELECT l.partner_id, SUM(l.amount_currency) AS AmountTotal, SUM(l.amount_residual_currency) AS ResidualTotal, l.currency_id "
                "FROM account_move_line l "
                "WHERE l.account_id IN %s AND l.partner_id = %s AND l.date < %s AND l.parent_state IN ('posted') "
                "GROUP BY l.partner_id, l.currency_id ORDER BY l.partner_id", (((tuple(doc.account_ids.ids), ) + (doc.partner_id.id,) + (doc.date_start, ))))
                
            docs.append({

                'partner_id': doc.partner_id,
                'move_line_ids': lines.ids,
                'company_id': doc.company_id,
                'prior': self.env.cr.dictfetchall()

            })

        return {

            'doc_ids':docids,
            'doc_model': 'rlbooks_statement.report.print',
            'date_start': doc.date_start,
            'date_end': doc.date_end,
            'company_id': doc.company_id.id,
            'type': doc.type,
            'account_ids': doc.account_ids.ids,
            'docs': docs,
        }
    
class BonusStatementReport(models.AbstractModel):

    _name = 'report.rlbooks_statement.bonus_report_partner_statement'
    _description = 'Partner Statement Bonus Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        
        docs = []

        for doc in docids:

            doc = self.env['rlbooks_statement.bonus_report.print'].browse(doc)

            types = []

            for type in doc.type_ids:

                types.append(type.type)

            lines = self.env['account.move'].search([['company_id','=',doc.company_id.id],['date','>=',doc.date_start],['date','<=',doc.date_end],['partner_id','=',doc.partner_id.id],['move_type','in',types],['state', 'in', ['posted']]], order='date desc')
            
            docs.append({

                'partner_id': doc.partner_id,
                'move_line_ids': lines.ids,
                'company_id': doc.company_id

            })

        return {

            'doc_ids':docids,
            'doc_model': 'rlbooks_statement.bonus_report.print',
            'date_start': doc.date_start,
            'date_end': doc.date_end,
            'bonus_goods': doc.bonus_goods,
            'bonus_consus': doc.bonus_consus,
            'bonus_services': doc.bonus_services,
            'company_id': doc.company_id.id,
            'type': doc.type,
            'type_ids': doc.type_ids.ids,
            'docs': docs,
        }

class SalesStatementReport(models.AbstractModel):

    _name = 'report.rlbooks_statement.sales_report_statement'
    _description = 'Sales Statement Report'

    @api.model
    def _get_report_values(self, docids, data=None):
                
        docs = []
        company_ids = self.env['res.company'].browse(self._context.get('allowed_company_ids'))

        for doc in docids:

            doc = self.env['rlbooks_statement.sales_report.wizard'].browse(doc)            

            tag = self.env['account.account.tag'].search([['name','=','Revenue']], limit=1)

            account_ids = self.env['account.account'].search([['tag_ids','ilike',tag.id]])

            selected_companies = self.env['res.company'].browse(self._context.get('allowed_company_ids'))

            companies_array = []

            for company in selected_companies.sorted(key=lambda r: r.name):
                
                sql_list =  []
                groups = []
                open_orders_list = []

                if doc.type == 'normal':

                    open_order_states = []

                    for open_order_state in doc.open_order_state_ids:

                        open_order_states.append(open_order_state.state)

                    user_company = self.env.company
                    user_currency = user_company.currency_id
                    sql_list = []                    
                    months = []

                    date_start = doc.date_start
                    date_end = doc.date_start + timedelta(days=-1)
                    
                    count_months = doc.date_end.year * 12 - doc.date_start.year * 12 + doc.date_end.month - doc.date_start.month + 1

                    # Find realised sales values:

                    for month in range(count_months):
                        
                        date_start = date_end + timedelta(days=1)
                        date_end = date_start + relativedelta(day=31) 
                        
                        months.append(date_start)     

                        if date_end > doc.date_end:

                            date_end = doc.date_end

                        if len(company_ids) > 1:

                            companies = self.env.companies
                            conversion_date = date_end
                            currency_rates = companies.mapped('currency_id')._get_rates(user_company, conversion_date)

                        else:

                            companies = user_company
                            currency_rates = {user_currency.id: 1.0}

                        conversion_rates = []

                        for company_in_list in companies:

                            conversion_rates.extend((
                                company_in_list.id,
                                # currency_rates[user_company.currency_id.id] / currency_rates[company_in_list.currency_id.id],
                                currency_rates[doc.currency_id.id] / currency_rates[company_in_list.currency_id.id],
                                user_currency.decimal_places,
                            ))

                        query = '(VALUES %s) AS currency_table(company_id, rate, precision)' % ','.join('(%s, %s, %s)' for i in companies)
                        
                        self.env.cr.execute('''
                            SELECT COALESCE(SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)), 0.0) AS balance, COALESCE(SUM(account_move_line.balance), 0.0) AS balance_in_lcy, extract(year from account_move_line.date) AS Year, extract(month from account_move_line.date) AS Month
                            FROM account_move_line
                            JOIN ''' + self.env.cr.mogrify(query, conversion_rates).decode(self.env.cr.connection.encoding) + ''' ON currency_table.company_id = account_move_line.company_id
                            WHERE account_move_line.company_id = %s AND account_move_line.date >= %s AND account_move_line.date < %s AND account_move_line.partner_id not in %s AND account_move_line.account_id IN %s AND account_move_line.parent_state = 'posted'
                            GROUP BY Year, Month
                            
                            ''', (((company.id,) + (date_start, ) +  (date_end + timedelta(days=1), ) + (tuple(doc.exclude_partner_ids.ids), ) + (tuple(account_ids.ids), ) )))

                        sql = self.env.cr.dictfetchall()

                        if sql:

                            sql_list += sql

                        else:                        

                            sql_list.append({

                                'year': date_start.year,
                                'month': date_start.month,
                                'balance': 0,
                                'balance_in_lcy': 0 

                            })

                        
                        #Get open sales order values
                        
                        if len(company_ids) > 1:

                            companies = self.env.companies
                            conversion_date = datetime.today()
                            currency_rates = companies.mapped('currency_id')._get_rates(user_company, conversion_date)

                        else:

                            companies = user_company
                            currency_rates = {user_currency.id: 1.0}

                        conversion_rates = []

                        for company_in_list in companies:

                            conversion_rates.extend((
                                company_in_list.id,
                                currency_rates[doc.currency_id.id] / currency_rates[company_in_list.currency_id.id],
                                user_currency.decimal_places,
                            ))

                        query = '(VALUES %s) AS currency_table(company_id, rate, precision)' % ','.join('(%s, %s, %s)' for i in companies)
                                                
                        self.env.cr.execute('''
                            SELECT COALESCE(SUM(sale_order_line.open_salesvalue * currency_table.rate), 0.0) AS balance, COALESCE(SUM(sale_order_line.open_salesvalue), 0.0) AS balance_in_lcy, extract(year from sale_order_line.order_delivery_date) AS Year, extract(month from sale_order_line.order_delivery_date) AS Month
                            FROM sale_order_line
                            JOIN ''' + self.env.cr.mogrify(query, conversion_rates).decode(self.env.cr.connection.encoding) + ''' ON currency_table.company_id = sale_order_line.company_id
                            WHERE sale_order_line.company_id = %s AND sale_order_line.order_delivery_date >= %s AND sale_order_line.order_delivery_date < %s AND sale_order_line.order_partner_id not in %s AND sale_order_line.state IN %s 
                            GROUP BY Year, Month
                            
                            ''', (((company.id,) + (date_start, ) +  (date_end +  timedelta(days=1), ) + (tuple(doc.exclude_partner_ids.ids), ) + (tuple(open_order_states), ) )))

                        sql = self.env.cr.dictfetchall()

                        if sql:

                            open_orders_list += sql

                        else:                        

                            open_orders_list.append({

                                'year': date_start.year,
                                'month': date_start.month,
                                'balance': 0,
                                'balance_in_lcy': 0 

                            })
                                                

                elif doc.type == 'detailed':

                    groups = self.env['account.move.line'].read_group([['account_id','in',account_ids.ids],['partner_id','not in',doc.exclude_partner_ids.ids],['date','<=',doc.date_end],['date','>=',doc.date_start],['company_id','=',company.id],['parent_state','in',['posted']]], ['date', 'balance'], ['date:month']) #, 'company_id'
                   
                company_group = {

                    'id':company.id,
                    'name': company.name,
                    'groups': groups,
                    'sql': sql_list,
                    'open_orders': open_orders_list,
                    'months': months

                }

                companies_array.append(company_group)

            docs.append({

                'id': doc.id,     
                'companies': companies_array

            })

        return {

            'doc_ids':docids,
            'doc_model': 'rlbooks_statement.sales_report.wizard',
            'date_start': doc.date_start,
            'date_end': doc.date_end,            
            'company_ids': company_ids.ids,
            'docs': docs,
        }