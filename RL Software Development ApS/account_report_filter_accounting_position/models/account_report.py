# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools.misc import format_date

from dateutil.relativedelta import relativedelta
from itertools import chain

class AccountGeneralLedgerReportInherit(models.AbstractModel):
    _inherit = "account.general.ledger"

    @api.model
    def _get_query_amls(self, options, expanded_account, offset=None, limit=None):
        ''' Construct a query retrieving the account.move.lines when expanding a report line with or without the load
        more.
        :param options:             The report options.
        :param expanded_account:    The account.account record corresponding to the expanded line.
        :param offset:              The offset of the query (used by the load more).
        :param limit:               The limit of the query (used by the load more).
        :return:                    (query, params)
        '''

        unfold_all = options.get('unfold_all') or (self._context.get('print_mode') and not options['unfolded_lines'])

        # Get sums for the account move lines.
        # period: [('date' <= options['date_to']), ('date', '>=', options['date_from'])]
        if expanded_account:
            domain = [('account_id', '=', expanded_account.id)]
        elif unfold_all:
            domain = []
        elif options['unfolded_lines']:
            domain = [('account_id', 'in', [int(line[8:]) for line in options['unfolded_lines']])]

        new_options = self._force_strict_range(options)
        tables, where_clause, where_params = self._query_get(new_options, domain=domain)
        ct_query = self.env['res.currency']._get_query_currency_table(options)
        query = f'''
            SELECT
                account_move_line.id,
                account_move_line.date,
                account_move_line.date_maturity,
                account_move_line.name,
                account_move_line.ref,
                account_move_line.company_id,
                account_move_line.account_id,
                account_move_line.payment_id,
                account_move_line.partner_id,
                account_move_line.currency_id,
                account_move_line.amount_currency,
                ROUND(account_move_line.debit * currency_table.rate, currency_table.precision)   AS debit,
                ROUND(account_move_line.credit * currency_table.rate, currency_table.precision)  AS credit,
                ROUND(account_move_line.balance * currency_table.rate, currency_table.precision) AS balance,
                account_move_line__move_id.name         AS move_name,
                company.currency_id                     AS company_currency_id,
                CASE WHEN partner.ref IS NOT NULL THEN CONCAT(partner.name, ' [', partner.ref, ']') ELSE partner.name END AS partner_name,
                account_move_line__move_id.move_type    AS move_type,
                account.code                            AS account_code,
                account.name                            AS account_name,
                journal.code                            AS journal_code,
                journal.name                            AS journal_name,
                full_rec.name                           AS full_rec_name
            FROM {tables}
            LEFT JOIN {ct_query} ON currency_table.company_id = account_move_line.company_id
            LEFT JOIN res_company company               ON company.id = account_move_line.company_id
            LEFT JOIN res_partner partner               ON partner.id = account_move_line.partner_id
            LEFT JOIN account_account account           ON account.id = account_move_line.account_id
            LEFT JOIN account_journal journal           ON journal.id = account_move_line.journal_id
            LEFT JOIN account_full_reconcile full_rec   ON full_rec.id = account_move_line.full_reconcile_id
            WHERE {where_clause}
            ORDER BY account_move_line.date, account_move_line.id
        '''

        if offset:
            query += ' OFFSET %s '
            where_params.append(offset)
        if limit:
            query += ' LIMIT %s '
            where_params.append(limit)

        return query, where_params

class AccountReportInherit(models.AbstractModel):

    _inherit = "account.report"

    filter_account_positions = None
    
    @api.model
    def _init_filter_partner(self, options, previous_options=None):
        
        res = super(AccountReportInherit, self)._init_filter_partner(options, previous_options)
        
        if not self.filter_account_positions:           
            return

        previous_account_positions = (previous_options or {}).get('account_positions', [])  
        
        if str(previous_account_positions).startswith("account.fiscal.position(") == True:
            
            selected_account_positions = None
            options['selected_account_positions_names'] = None

        else:
        
            account_position_ids = [int(x.get('id') if x.get('id') != 'zero' else 0) for x in previous_account_positions if x.get('selected') == True]
            selected_account_positions = self.env['account.fiscal.position'].search([('id', 'in', account_position_ids)])
            
            values = selected_account_positions.mapped('name')
            not_set = False
            
            if 0 in account_position_ids:
                not_set = True
                values +=['Not set']
                                
            options['selected_account_positions_names'] = values
                                  
        options['account_positions'] = self._get_filter_account_positions(selected_account_positions, not_set)

    def _get_filter_account_positions(self, selected_account_positions, not_set=False):

        exists =  self.env['account.fiscal.position'].with_context(active_test=False).search([
            ('company_id', 'in', self.env.user.company_ids.ids or [self.env.company.id])
        ], order="company_id, name")

        list = []

        list.append({

            'id': 'zero',
            'name': "Not set",
            'selected': not_set

        })

        for value in exists:

            list.append(
                {

                    'id': value.id,
                    'name': value.name,
                    'selected': True if value in selected_account_positions else False

                }
            )
          
        return list

    @api.model
    def _get_options_partner_domain(self, options):

        domain = super(AccountReportInherit, self)._get_options_partner_domain(options)

        if options.get('account_positions'):           
            
            account_position_ids = [int(acc.get('id') if acc.get('id') != 'zero' else False) for acc in options['account_positions'] if acc.get('selected') == True]

            if len(account_position_ids) > 0:
                                    
                domain.append(('partner_id.property_account_position_id', 'in', account_position_ids))

        return domain

    # @api.model
    # def _get_query_amls(self, options, expanded_partner=None, offset=None, limit=None):
    #     ''' Construct a query retrieving the account.move.lines when expanding a report line with or without the load
    #     more.
    #     :param options:             The report options.
    #     :param expanded_partner:    The res.partner record corresponding to the expanded line.
    #     :param offset:              The offset of the query (used by the load more).
    #     :param limit:               The limit of the query (used by the load more).
    #     :return:                    (query, params)
    #     '''
    #     unfold_all = options.get('unfold_all') or (self._context.get('print_mode') and not options['unfolded_lines'])

    #     # Get sums for the account move lines.
    #     # period: [('date' <= options['date_to']), ('date', '>=', options['date_from'])]
    #     if expanded_partner is not None:
    #         domain = [('partner_id', '=', expanded_partner.id)]
    #     elif unfold_all:
    #         domain = []
    #     elif options['unfolded_lines']:
    #         domain = [('partner_id', 'in', [int(line[8:]) for line in options['unfolded_lines']])]

    #     new_options = self._get_options_sum_balance(options)
    #     tables, where_clause, where_params = self._query_get(new_options, domain=domain)
    #     ct_query = self.env['res.currency']._get_query_currency_table(options)

    #     query = '''
    #         SELECT
    #             account_move_line.id,
    #             account_move_line.date,
    #             account_move_line.date_maturity,
    #             account_move_line.name,
    #             account_move_line.ref,
    #             account_move_line.company_id,
    #             account_move_line.account_id,
    #             account_move_line.payment_id,
    #             account_move_line.partner_id,
    #             account_move_line.currency_id,
    #             account_move_line.amount_currency,
    #             account_move_line.matching_number,
    #             ROUND(account_move_line.debit * currency_table.rate, currency_table.precision)   AS debit,
    #             ROUND(account_move_line.credit * currency_table.rate, currency_table.precision)  AS credit,
    #             ROUND(account_move_line.balance * currency_table.rate, currency_table.precision) AS balance,
    #             account_move_line__move_id.name         AS move_name,
    #             company.currency_id                     AS company_currency_id,
    #             CASE WHEN partner.ref IS NOT NULL THEN CONCAT(partner.name, ' [', partner.ref, ']') ELSE partner.name END AS partner_name,
    #             account_move_line__move_id.move_type    AS move_type,
    #             account.code                            AS account_code,
    #             account.name                            AS account_name,
    #             journal.code                            AS journal_code,
    #             journal.name                            AS journal_name
    #         FROM %s
    #         LEFT JOIN %s ON currency_table.company_id = account_move_line.company_id
    #         LEFT JOIN res_company company               ON company.id = account_move_line.company_id
    #         LEFT JOIN res_partner partner               ON partner.id = account_move_line.partner_id
    #         LEFT JOIN account_account account           ON account.id = account_move_line.account_id
    #         LEFT JOIN account_journal journal           ON journal.id = account_move_line.journal_id
    #         WHERE %s
    #         ORDER BY account_move_line.date, account_move_line.id
    #     ''' % (tables, ct_query, where_clause)

    #     if offset:
    #         query += ' OFFSET %s '
    #         where_params.append(offset)
    #     if limit:
    #         query += ' LIMIT %s '
    #         where_params.append(limit)

    #     return query, where_params

    # @api.model
    # def _get_report_line_partner(self, options, partner, initial_balance, debit, credit, balance):
    #     company_currency = self.env.company.currency_id
    #     unfold_all = self._context.get('print_mode') and not options.get('unfolded_lines')

    #     columns = [
    #         {'name': self.format_value(initial_balance), 'class': 'number'},
    #         {'name': self.format_value(debit), 'class': 'number'},
    #         {'name': self.format_value(credit), 'class': 'number'},
    #     ]
    #     if self.user_has_groups('base.group_multi_currency'):
    #         columns.append({'name': ''})
    #     columns.append({'name': self.format_value(balance), 'class': 'number'})

    #     return {
    #         'id': 'partner_%s' % (partner.id if partner else 0),
    #         'partner_id': partner.id if partner else None,
    #         'name': partner is not None and ((partner.name + " [" + partner.ref + "]" if partner.ref else partner.name) or '')[:128] or _('Unknown Partner'),
    #         'columns': columns,
    #         'level': 2,
    #         'trust': partner.trust if partner else None,
    #         'unfoldable': not company_currency.is_zero(debit) or not company_currency.is_zero(credit),
    #         'unfolded': 'partner_%s' % (partner.id if partner else 0) in options['unfolded_lines'] or unfold_all,
    #         'colspan': 6,
    #     }

class ReportAccountAgedPartnerInherit(models.AbstractModel):
    
    _inherit = 'account.accounting.report'
   
    filter_account_positions = True
    
class ReportPartnerLedgerInherit(models.AbstractModel):
    
    _inherit = 'account.partner.ledger'
   
    filter_account_positions = True

class AccountAgedPartnerInherit(models.AbstractModel):
    
    _inherit = 'account.aged.partner'
   
    partner_ref = fields.Char(group_operator='max', string='Partner Ref')

    @api.model
    def _get_column_details(self, options):

        # res =  super(AccountAgedPartnerInherit, self)._get_column_details(options)

        columns = [
            self._header_column(),
            self._field_column('partner_ref'),
            self._field_column('report_date'),

            self._field_column('account_name', name=_("Account"), ellipsis=True),
            self._field_column('expected_pay_date'),
            self._field_column('period0', name=_("As of: %s", format_date(self.env, options['date']['date_to']))),
            self._field_column('period1', sortable=True),
            self._field_column('period2', sortable=True),
            self._field_column('period3', sortable=True),
            self._field_column('period4', sortable=True),
            self._field_column('period5', sortable=True),
            self._custom_column(  # Avoid doing twice the sub-select in the view
                name=_('Total'),
                classes=['number'],
                formatter=self.format_value,
                getter=(lambda v: v['period0'] + v['period1'] + v['period2'] + v['period3'] + v['period4'] + v['period5']),
                sortable=True,
            ),
        ]

        if self.user_has_groups('base.group_multi_currency'):
            columns[2:2] = [
                self._field_column('amount_currency'),
                self._field_column('currency_id'),
            ]

        return columns

    @api.model
    def _get_sql(self):
        options = self.env.context['report_options']
        query = ("""
            SELECT
                {move_line_fields},
                account_move_line.amount_currency as amount_currency,
                account_move_line.partner_id AS partner_id,
                CASE WHEN partner.ref IS NOT NULL THEN CONCAT(partner.name, ' [', partner.ref, ']') ELSE partner.name END AS partner_name,
               
                partner.ref AS partner_ref,
                COALESCE(trust_property.value_text, 'normal') AS partner_trust,
                COALESCE(account_move_line.currency_id, journal.currency_id) AS report_currency_id,
                account_move_line.payment_id AS payment_id,
                COALESCE(account_move_line.date_maturity, account_move_line.date) AS report_date,
                account_move_line.expected_pay_date AS expected_pay_date,
                move.move_type AS move_type,
                move.name AS move_name,
                move.ref AS move_ref,
                account.code || ' ' || account.name AS account_name,
                account.code AS account_code,""" + ','.join([("""
                CASE WHEN period_table.period_index = {i}
                THEN %(sign)s * ROUND((
                    account_move_line.balance - COALESCE(SUM(part_debit.amount), 0) + COALESCE(SUM(part_credit.amount), 0)
                ) * currency_table.rate, currency_table.precision)
                ELSE 0 END AS period{i}""").format(i=i) for i in range(6)]) + """
            FROM account_move_line
            JOIN account_move move ON account_move_line.move_id = move.id
            JOIN account_journal journal ON journal.id = account_move_line.journal_id
            JOIN account_account account ON account.id = account_move_line.account_id
            JOIN res_partner partner ON partner.id = account_move_line.partner_id
            LEFT JOIN ir_property trust_property ON (
                trust_property.res_id = 'res.partner,'|| account_move_line.partner_id
                AND trust_property.name = 'trust'
                AND trust_property.company_id = account_move_line.company_id
            )
            JOIN {currency_table} ON currency_table.company_id = account_move_line.company_id
            LEFT JOIN LATERAL (
                SELECT part.amount, part.debit_move_id
                FROM account_partial_reconcile part
                WHERE part.max_date <= %(date)s
            ) part_debit ON part_debit.debit_move_id = account_move_line.id
            LEFT JOIN LATERAL (
                SELECT part.amount, part.credit_move_id
                FROM account_partial_reconcile part
                WHERE part.max_date <= %(date)s
            ) part_credit ON part_credit.credit_move_id = account_move_line.id
            JOIN {period_table} ON (
                period_table.date_start IS NULL
                OR COALESCE(account_move_line.date_maturity, account_move_line.date) <= DATE(period_table.date_start)
            )
            AND (
                period_table.date_stop IS NULL
                OR COALESCE(account_move_line.date_maturity, account_move_line.date) >= DATE(period_table.date_stop)
            )
            WHERE account.internal_type = %(account_type)s
            AND account.exclude_from_aged_reports IS NOT TRUE
            GROUP BY account_move_line.id, partner.id, trust_property.id, journal.id, move.id, account.id,
                     period_table.period_index, currency_table.rate, currency_table.precision
            HAVING ROUND(account_move_line.balance - COALESCE(SUM(part_debit.amount), 0) + COALESCE(SUM(part_credit.amount), 0), currency_table.precision) != 0
        """).format(
            move_line_fields=self._get_move_line_fields('account_move_line'),
            currency_table=self.env['res.currency']._get_query_currency_table(options),
            period_table=self._get_query_period_table(options),
        )
        params = {
            'account_type': options['filter_account_type'],
            'sign': 1 if options['filter_account_type'] == 'receivable' else -1,
            'date': options['date']['date_to'],
        }

        return self.env.cr.mogrify(query, params).decode(self.env.cr.connection.encoding)

# class Partner(models.Model):

#     _inherit = "res.partner"

    # def name_get(self):

    #     result = []

    #     if self._context.get('name_display'):

    #         for partner in self:
    #             name = partner.name
    #             if partner.ref:
    #                 name = str(name) + "-" + str(partner.ref)
    #             result.append((partner.id, name))

    #     else:

    #         result = super().name_get()

    #     return result

    # @api.depends(lambda self: (self._rec_name,) if self._rec_name else ())
    # def _compute_display_name(self):

    #     names = dict(self.name_get())
    #     for record in self:

    #         if record.ref != False and record.ref != '':

    #             record.display_name = "[" + record.ref + "] " + names.get(record.id, '')
            
    #         else:

    #             record.display_name = names.get(record.id, False)
