# -*- coding: utf-8 -*-

from ast import literal_eval
import time
from odoo import models, _
from custom_addons.bs_base.static.format.xls_format import get_xlsx_formats
from bs_lib.service import common


class ReportXlsBsGeneralLedger(models.AbstractModel):
    _name = 'report.bs_report.report_generalledger_xls'
    _inherit = ['report.report_xlsx.abstract', 'report.account.report_generalledger']

    def _get_account_move_entry(self, accounts, init_balance, sortby, display_account):
        """
        :param:
                accounts: the recordset of accounts
                init_balance: boolean value of initial_balance
                sortby: sorting by date or partner and journal
                display_account: type of account(receivable, payable and both)

        Returns a dictionary of accounts with following key and value {
                'code': account code,
                'name': account name,
                'debit': sum of total debit amount,
                'credit': sum of total credit amount,
                'balance': total balance,
                'amount_currency': sum of amount_currency,
                'move_lines': list of move line
        }
        """
        cr = self.env.cr
        MoveLine = self.env['account.move.line']
        move_lines = {x: [] for x in accounts.ids}

        # Prepare initial sql query and Get the initial move lines
        if init_balance:
            init_tables, init_where_clause, init_where_params = MoveLine.with_context(date_from=self.env.context.get('date_from'), date_to=False, initial_bal=True)._query_get()
            init_wheres = [""]
            if init_where_clause.strip():
                init_wheres.append(init_where_clause.strip())
            init_filters = " AND ".join(init_wheres)
            filters = init_filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')
            sql = ("""SELECT 0 AS lid, l.account_id AS account_id, '' AS ldate, '' AS lcode, NULL AS amount_currency, '' AS lref, 'Initial Balance' AS lname, COALESCE(SUM(l.debit),0.0) AS debit, COALESCE(SUM(l.credit),0.0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance, '' AS lpartner_id,\
                    '' AS move_name, '' AS mmove_id, '' AS currency_code,\
                    NULL AS currency_id,\
                    '' AS invoice_id, '' AS invoice_type, '' AS invoice_number,\
                    '' AS partner_name, '' AS partner_code\
                    FROM account_move_line l\
                    LEFT JOIN account_move m ON (l.move_id=m.id)\
                    LEFT JOIN res_currency c ON (l.currency_id=c.id)\
                    LEFT JOIN res_partner p ON (l.partner_id=p.id)\
                    LEFT JOIN account_invoice i ON (m.id =i.move_id)\
                    JOIN account_journal j ON (l.journal_id=j.id)\
                    WHERE l.account_id IN %s""" + filters + ' GROUP BY l.account_id')
            params = (tuple(accounts.ids),) + tuple(init_where_params)
            cr.execute(sql, params)
            for row in cr.dictfetchall():
                move_lines[row.pop('account_id')].append(row)

        sql_sort = 'l.date, l.move_id'
        if sortby == 'sort_journal_partner':
            sql_sort = 'j.code, p.name, l.move_id'

        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = MoveLine._query_get()
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        filters = filters.replace('account_move_line__move_id', 'm').replace('account_move_line', 'l')

        # Get move lines base on sql query and Calculate the total balance of move lines
        sql = ('''SELECT l.id AS lid, l.account_id AS account_id, l.date AS ldate, j.code AS lcode, l.currency_id, l.amount_currency, l.ref AS lref, l.name AS lname, COALESCE(l.debit,0) AS debit, \
                         COALESCE(l.credit,0) AS credit, COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) AS balance, \
                         l.manual_entry, m.name AS move_name, m.date AS posted_date, m.date_account AS account_date, m.business_unit AS bunit, m.description AS jvl_description, m.inv_ref AS inv_ref, \
                         c.symbol AS currency_code, p.name AS partner_name, p.partner_code AS partner_code, i.date_invoice_hard_cpy AS date_inv_hard_cpy, \
                         i.challan_no AS challan_no, i.po_no AS po_no, pm.cheque_no AS cheque_no \
                FROM account_move_line l \
                JOIN account_move m ON (l.move_id=m.id) \
                LEFT JOIN account_invoice i ON (m.id =i.move_id) \
                LEFT JOIN account_payment pm ON (l.payment_id = pm.id)
                LEFT JOIN res_currency c ON (l.currency_id=c.id) \
                LEFT JOIN res_partner p ON (l.partner_id=p.id) \
                JOIN account_journal j ON (l.journal_id=j.id) \
                JOIN account_account acc ON (l.account_id = acc.id) \
                WHERE l.account_id IN %s ''' + filters + ''' GROUP BY l.id, l.account_id, l.date, j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.name, m.date, m.date_account, m.business_unit, m.description, m.inv_ref, c.symbol, p.name, p.partner_code, i.business_unit, i.date_invoice_hard_cpy, i.date_invoice, i.description, i.challan_no, i.po_no, i.inv_no, pm.cheque_no ORDER BY ''' + sql_sort)
        params = (tuple(accounts.ids),) + tuple(where_params)
        cr.execute(sql, params)

        for row in cr.dictfetchall():
            balance = 0
            for line in move_lines.get(row['account_id']):
                balance += line['debit'] - line['credit']
            row['balance'] += balance
            move_lines[row.pop('account_id')].append(row)

        # Calculate the debit, credit and balance for Accounts
        account_res = []
        for account in accounts:
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            res['code'] = account.code
            res['name'] = account.name
            res['move_lines'] = move_lines[account.id]
            for line in res.get('move_lines'):
                res['debit'] += line['debit']
                res['credit'] += line['credit']
                res['balance'] = line['balance']
            if display_account == 'all':
                account_res.append(res)
            if display_account == 'movement' and res.get('move_lines'):
                account_res.append(res)
            if display_account == 'not_zero' and not currency.is_zero(res['balance']):
                account_res.append(res)

        return account_res

    def _build_contexts(self, data):
        result = {}
        result['journal_ids'] = 'journal_ids' in data and data['journal_ids'] or False
        result['state'] = 'target_move' in data and data['target_move'] or ''
        result['date_from'] = data['date_from'] or False
        result['date_to'] = data['date_to'] or False
        result['strict_range'] = True if result['date_from'] else False
        result['lang'] = self.env.get('lang') or 'en_US'
        result['state'] = data['target_move'] or False
        return result

    def _process_data(self, data):
        self.model = self.env.context.get('active_model')
        account_ids = data['account_ids']
        init_balance = data.get('initial_balance', True)
        sortby = data.get('sortby', 'sort_date')
        display_account = data['display_account']

        if data.get('initial_balance', False):
            if not data.get('date_from', False) or data.get('date_to', False):
                print("You must define a Start Date")

        codes = []
        if data.get('journal_ids', False):
            codes = [journal.code for journal in self.env['account.journal'].search([('id', 'in', data['journal_ids'])])]

        accounts = self.env['account.account'].browse(account_ids)
        accounts_res = self.with_context(self._build_contexts(data))._get_account_move_entry(accounts,
                                                                                             init_balance,
                                                                                             sortby,
                                                                                             display_account)

        return {
            'doc_model': self.model,
            'data': data,
            'docs': account_ids,
            'time': time,
            'Accounts': accounts_res,
            'print_journal': codes,
        }

    def generate_xlsx_report(self, workbook, data, objects):
        if not objects or not self.env.context.get('active_model'):
            raise common.ThrowException(message=_("Form content is missing, this report cannot be printed."), title=_("Data Error"))

        sheet = workbook.add_worksheet('General Ledger')
        formats = get_xlsx_formats(workbook)

        formats['big_header'].set_font_color('#b000bc')
        formats['header_left'].set_font_color('#b000bc')
        formats['header_right'].set_font_color('#b000bc')

        [data] = objects.read()
        objects.mo_id = False

        if data.get('initial_balance', False):
            if not data.get('date_from'):
                sheet.write('A1:D1', 'You must define a Start Date', formats['body_left'])
                return

        result = self._process_data(data)

        data = result['data']
        accounts = result['Accounts']
        print_journal = result['print_journal']

        company = self.env['res.company'].search([('id', '=', self._uid)])
        sheet.set_column('A:I', 17)

        sheet.merge_range('A1:I1',
                          '{}: General Ledger'.format(company.name),
                          formats['big_header'])
        sheet.merge_range('A2:E2', 'Journals:',
                          formats['header_left'])
        sheet.write(2, 5,
                    'Display Account',
                    formats['header_left'])
        sheet.write(2, 6,
                    'Target Moves',
                    formats['header_left'])

        sheet.merge_range('A3:E3', ', '.join([lt or '' for lt in print_journal]))
        sheet.write(3, 5, 'All accounts' if data['display_account'] == 'all' \
            else 'With movements' if data['display_account'] == 'movement' \
            else 'With balance not equal to zero' if data['display_account'] == 'not_zero' else '')
        sheet.write(3, 6, 'All Entries' if data['target_move'] == 'all' \
            else 'All Posted Entries' if data['target_move'] == 'posted' else '')

        sheet.write(4, 0, 'Sorted By:', formats['header_left'])
        sheet.write(4, 1, 'Date From', formats['header_left'])
        sheet.write(4, 2, 'Date To', formats['header_left'])

        sheet.write(5, 0, 'Date' if data['sortby'] == 'sort_date' \
            else 'Journal and Partner' if data['sortby'] == 'sort_journal_partner' else '', formats['header_left'])
        sheet.write(5, 1, data['date_from'] if data['date_from'] else '', formats['date_format_bold'])
        sheet.write(5, 2, data['date_to'] if data['date_to'] else '', formats['date_format_bold'])

        sheet.write(7, 0, 'Business Unit', formats['header_right'])
        sheet.write(7, 1, 'Account Code', formats['header_right'])
        sheet.write(7, 2, 'Accounting Date', formats['header_right'])
        sheet.write(7, 3, 'Invoice Date', formats['header_right'])
        sheet.write(7, 4, 'JV Header Description', formats['header_right'])
        sheet.write(7, 5, 'Vendor Name', formats['header_right'])
        sheet.write(7, 6, 'Vendor Code', formats['header_right'])
        sheet.write(7, 7, 'Cheque No.', formats['header_right'])
        sheet.write(7, 8, 'Invoice No.', formats['header_right'])
        sheet.write(7, 9, 'Reference No.', formats['header_right'])
        sheet.write(7, 10, 'Challan No.', formats['header_right'])
        sheet.write(7, 11, 'PO No.', formats['header_right'])
        sheet.write(7, 12, 'Currency', formats['header_right'])
        sheet.write(7, 13, 'Debit', formats['header_right'])
        sheet.write(7, 14, 'Credit', formats['header_right'])
        sheet.write(7, 15, 'Posted Date', formats['header_right'])
        sheet.write(7, 16, 'Balance', formats['header_right'])

        row = 8
        for account in accounts:
            for line in account['move_lines']:
                sheet.write(row, 0, line['bunit'], formats['body_right'])
                sheet.write(row, 1, account['code'], formats['body_right'])
                sheet.write(row, 2, line['account_date'], formats['body_right'])
                sheet.write(row, 3, line['date_inv_hard_cpy'], formats['body_right'])
                sheet.write(row, 4, line['jvl_description'], formats['body_right'])
                sheet.write(row, 5, line['partner_name'], formats['body_right'])
                sheet.write(row, 6, line['partner_code'], formats['body_right'])
                sheet.write(row, 7, line['cheque_no'], formats['body_right'])
                sheet.write(row, 8, line['lref'], formats['body_right'])
                sheet.write(row, 9, line['inv_ref'], formats['body_right'])
                sheet.write(row, 10, line['challan_no'], formats['body_right'])
                sheet.write(row, 11, line['po_no'], formats['body_right'])
                sheet.write(row, 12, line['currency_code'], formats['body_right'])
                sheet.write(row, 13, line['debit'], formats['money_format'])
                sheet.write(row, 14, line['credit'], formats['money_format'])
                sheet.write(row, 15, line['posted_date'], formats['body_right'])
                sheet.write(row, 16, line['balance'], formats['money_format'])
                row += 1
