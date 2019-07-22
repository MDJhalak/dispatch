# -*- coding: utf-8 -*-

from custom_addons.bs_base.static.format.xls_format import get_xlsx_formats
from datetime import datetime
import time
from odoo import models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class ReportXlsBsPartnerLedger(models.AbstractModel):
    _name = 'report.bs_report.report_partnerledger_xls'
    _inherit = 'report.report_xlsx.abstract'

    def _lines(self, data, partner):
        full_account = []
        currency = self.env['res.currency']
        query_get_data = self.env['account.move.line'].with_context(self._build_contexts(data))._query_get()
        reconcile_clause = "" if data['reconciled'] else ' AND "account_move_line".reconciled = false '
        params = [partner.id, tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        query = """
            SELECT "account_move_line".id, "account_move_line".date, j.code, acc.code as a_code, acc.name as a_name, "account_move_line".ref, m.name as move_name, "account_move_line".name, "account_move_line".debit, "account_move_line".credit, "account_move_line".amount_currency,"account_move_line".currency_id, c.symbol AS currency_code
            FROM """ + query_get_data[0] + """
            LEFT JOIN account_journal j ON ("account_move_line".journal_id = j.id)
            LEFT JOIN account_account acc ON ("account_move_line".account_id = acc.id)
            LEFT JOIN res_currency c ON ("account_move_line".currency_id=c.id)
            LEFT JOIN account_move m ON (m.id="account_move_line".move_id)
            WHERE "account_move_line".partner_id = %s
                AND m.state IN %s
                AND "account_move_line".account_id IN %s AND """ + query_get_data[1] + reconcile_clause + """
                ORDER BY "account_move_line".date"""
        self.env.cr.execute(query, tuple(params))
        res = self.env.cr.dictfetchall()
        sum = 0.0
        lang_code = self.env.context.get('lang') or 'en_US'
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        for r in res:
            r['date'] = datetime.strptime(r['date'], DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            r['displayed_name'] = '-'.join(
                r[field_name] for field_name in ('move_name', 'ref', 'name')
                if r[field_name] not in (None, '', '/')
            )
            sum += r['debit'] - r['credit']
            r['progress'] = sum
            r['currency_id'] = currency.browse(r.get('currency_id'))
            full_account.append(r)
        return full_account

    def _sum_partner(self, data, partner, field):
        if field not in ['debit', 'credit', 'debit - credit']:
            return
        result = 0.0
        query_get_data = self.env['account.move.line'].with_context(self._build_contexts(data))._query_get()
        reconcile_clause = "" if data['reconciled'] else ' AND "account_move_line".reconciled = false '

        params = [partner.id, tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        query = """SELECT sum(""" + field + """)
                FROM """ + query_get_data[0] + """, account_move AS m
                WHERE "account_move_line".partner_id = %s
                    AND m.id = "account_move_line".move_id
                    AND m.state IN %s
                    AND account_id IN %s
                    AND """ + query_get_data[1] + reconcile_clause
        self.env.cr.execute(query, tuple(params))

        contemp = self.env.cr.fetchone()
        if contemp is not None:
            result = contemp[0] or 0.0
        return result

    def _build_contexts(self, data):
        result = {}
        result['journal_ids'] = 'journal_ids' in data and data['journal_ids'] or False
        result['state'] = 'target_move' in data and data['target_move'] or ''
        result['date_from'] = data['date_from'] or False
        result['date_to'] = data['date_to'] or False
        result['strict_range'] = True if result['date_from'] else False
        return result

    def _process_data(self, data):
        data['computed'] = {}
        obj_partner = self.env['res.partner']
        query_get_data = self.env['account.move.line'].with_context(self._build_contexts(data))._query_get()
        data['computed']['move_state'] = ['draft', 'posted']
        if data.get('target_move', 'all') == 'posted':
            data['computed']['move_state'] = ['posted']
        result_selection = data.get('result_selection', 'customer')
        if result_selection == 'supplier':
            data['computed']['ACCOUNT_TYPE'] = ['payable']
        elif result_selection == 'customer':
            data['computed']['ACCOUNT_TYPE'] = ['receivable']
        else:
            data['computed']['ACCOUNT_TYPE'] = ['payable', 'receivable']

        self.env.cr.execute("""
            SELECT a.id
            FROM account_account a
            WHERE a.internal_type IN %s
            AND NOT a.deprecated""", (tuple(data['computed']['ACCOUNT_TYPE']),))
        data['computed']['account_ids'] = [a for (a,) in self.env.cr.fetchall()]
        params = [tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        reconcile_clause = "" if data['reconciled'] else ' AND "account_move_line".reconciled = false '
        query = """
            SELECT DISTINCT "account_move_line".partner_id
            FROM """ + query_get_data[0] + """, account_account AS account, account_move AS am
            WHERE "account_move_line".partner_id IS NOT NULL
                AND "account_move_line".account_id = account.id
                AND am.id = "account_move_line".move_id
                AND am.state IN %s
                AND "account_move_line".account_id IN %s
                AND NOT account.deprecated
                AND """ + query_get_data[1] + reconcile_clause
        self.env.cr.execute(query, tuple(params))
        partner_ids = [res['partner_id'] for res in self.env.cr.dictfetchall()]
        partners = obj_partner.browse(partner_ids)
        partners = sorted(partners, key=lambda x: (x.ref or '', x.name or ''))
        return {
            'doc_ids': partner_ids,
            'doc_model': self.env['res.partner'],
            'data': data,
            'docs': partners,
            'time': time,
            'lines': self._lines,
            'sum_partner': self._sum_partner,
        }

    def generate_xlsx_report(self, workbook, data, objects):
        sheet = workbook.add_worksheet('Partner Ledger')
        formats = get_xlsx_formats(workbook)

        formats['big_header'].set_font_color('#b000bc')
        formats['header_left'].set_font_color('#b000bc')
        formats['header_right'].set_font_color('#b000bc')

        [data] = objects.read()
        objects.mo_id = False
        result = self._process_data(data)

        data = result['data']
        docs = result['docs']
        lines = result['lines']
        sum_partner = result['sum_partner']

        sheet.set_column('A:G', 17)

        sheet.merge_range('A1:G1', 'Partner Ledger', formats['big_header'])
        sheet.write(2, 0, 'Company:', formats['header_left'])
        sheet.write(2, 1, 'Date From:', formats['header_left'])
        sheet.write(2, 2, 'Date To:', formats['header_left'])
        sheet.write(2, 3, 'Target Moves', formats['header_left'])

        sheet.write(3, 0, data['company_id'][1])
        sheet.write(3, 1, data['date_from'])
        sheet.write(3, 2, data['date_to'])
        sheet.write(3, 3, 'All Entries' if data['target_move'] == 'all' \
            else 'All Posted Entries' if data['target_move'] == 'posted' else '')

        sheet.write(5, 0, 'Partner', formats['header_left'])
        sheet.write(5, 1, 'Date', formats['header_left'])
        sheet.write(5, 2, 'JRNL', formats['header_left'])
        sheet.write(5, 3, 'Account', formats['header_left'])
        sheet.write(5, 4, 'Ref', formats['header_left'])
        sheet.write(5, 5, 'Debit', formats['header_right'])
        sheet.write(5, 6, 'Credit', formats['header_right'])
        sheet.write(5, 7, 'Balance', formats['header_right'])

        row = 6
        for doc in docs:
            # sheet.merge_range('A{}:D{}'.format(row + 1, row + 1), doc.ref if doc.ref else ' ' + ' - ' + doc.name, formats['header_left'])sheet.merge_range('A{}:D{}'.format(row + 1, row + 1), doc.ref if doc.ref else ' ' + ' - ' + doc.name, formats['header_left'])
            sheet.write(row, 4, sum_partner(data, doc, 'debit'), formats['money_format_bold'])
            sheet.write(row, 5, sum_partner(data, doc, 'credit'), formats['money_format_bold'])
            sheet.write(row, 6, sum_partner(data, doc, 'debit - credit'), formats['money_format_bold'])
            row += 1
            for line in lines(data, doc):
                sheet.write(row, 0, doc.name, formats['body_left'])
                sheet.write(row, 1, line['date'], formats['body_left'])
                sheet.write(row, 2, line['code'], formats['body_left'])
                sheet.write(row, 3, line['a_code'], formats['body_left'])
                sheet.write(row, 4, line['displayed_name'], formats['body_left'])
                sheet.write(row, 5, line['debit'], formats['money_format'])
                sheet.write(row, 6, line['credit'], formats['money_format'])
                sheet.write(row, 7, line['progress'], formats['money_format'])
                row += 1

