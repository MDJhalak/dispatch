# -*- coding: utf-8 -*-

from custom_addons.bs_base.static.format.xls_format import get_xlsx_formats
from odoo import models
from ast import literal_eval


class ReportXlsIncomeBalanceStatement(models.AbstractModel):
    _name = 'report.bs_report.report_xls_bs_income_balance_statement'
    _inherit = ['report.report_xlsx.abstract', 'report.bs_report.report_bs_income_balance_statement']

    def _process_data(self, data):
        analytic_account_ids = literal_eval(data['analytic_account_ids'] if 'analytic_account_ids' in data\
                                                                            and data['analytic_account_ids'] else "[]")
        start_date = data['start_date'] if data['start_date'] else None
        end_date = data['end_date'] if data['end_date'] else None
        move_type = data['move_type'] if 'move_type' in data and data['move_type'] else None

        financial_data = self._get_analytic_line_data(account_ids=analytic_account_ids,
                                                      start_date=start_date,
                                                      end_date=end_date) if len(analytic_account_ids) > 0 \
            else self._get_account_move_data(start_date=start_date, end_date=end_date, move_type=move_type)

        analytic_account_data = None
        if len(analytic_account_ids) == 1:
            analytic_account_data = self.env['account.analytic.account'].browse(analytic_account_ids[0])

        info = {
            'start_date': start_date,
            'end_date': end_date,
            'statement_name': 'Statement of Comprehensive Income' \
                if data['statement_type'] == 'income' else 'Statement of Financial Position',
            'statement_type': data['statement_type'],
            'analytic_account_name': analytic_account_data.name if analytic_account_data else None
        }
        return {
            'data': self._generate_data_list(financial_data, nonzero=data['display_type'] == 'nonzero'),
            'info': info,
            'is_compact': data['report_type'] == 'compact'
        }

    def generate_xlsx_report(self, workbook, data, objects):
        sheet = workbook.add_worksheet('Financial Statements')
        formats = get_xlsx_formats(workbook)

        formats['big_header'].set_font_color('#b000bc')
        formats['header_left'].set_font_color('#b000bc')
        formats['header_right'].set_font_color('#b000bc')

        [data] = objects.read()
        objects.mo_id = False
        result = self._process_data(data)

        data = result['data']
        info = result['info']
        is_compact = result['is_compact']

        sheet.set_column('A:F', 17)
        sheet.merge_range('A1:F1', info['statement_name'], formats['big_header'])

        sheet.write(2, 0, 'Start Date', formats['header_left'])
        sheet.write(3, 0, info['start_date'] if info['start_date'] else "", formats['date_format'])
        sheet.write(2, 1, 'End Date', formats['header_left'])
        sheet.write(3, 1, info['end_date'] if info['end_date'] else "", formats['date_format'])
        if info['analytic_account_name']:
            sheet.write(2, 2, 'Analytic Account', formats['header_left'])
            sheet.write(3, 2, info['analytic_account_name'], formats['body_left'])

        row = 5

        if info['statement_type'] == 'income':
            self._write_sheet_income_statement(data, is_compact, sheet, formats, row)

        if info['statement_type'] == 'balance':
            self._write_sheet_balance_statement(data, is_compact, sheet, formats, row)

    @staticmethod
    def _write_entries(data, is_compact, sheet, formats, row):
        total_amount = 0

        for entry in data:
            total_amount += entry['amount']

            if not is_compact:
                sheet.merge_range('B{}:D{}'.format(row + 1, row + 1), entry['name'], formats['body_left'])
                sheet.write(row, 4, entry['amount'], formats['money_format'])
                row += 1

        if is_compact:
            sheet.merge_range('B{}:D{}'.format(row + 1, row + 1), 'Total', formats['header_left'])
            sheet.write(row, 4, total_amount, formats['money_format_bold'])
            row += 1
        return row

    def _write_sheet_income_statement(self, data, is_compact, sheet, formats, row):

        sheet.merge_range('A{}:F{}'.format(row + 1, row + 1), 'Revenue(+)', formats['header_left'])
        row += 1

        if 'income' in data:
            row = self._write_entries(data['income'], is_compact, sheet, formats, row)

        sheet.merge_range('A{}:F{}'.format(row + 1, row + 1), 'Cost of Sales(-)', formats['header_left'])
        row += 1

        if 'cost of revenue' in data:
            row = self._write_entries(data['cost of revenue'], is_compact, sheet, formats, row)

        sheet.merge_range('A{}:D{}'.format(row + 1, row + 1), 'GROSS PROFIT', formats['header_left'])
        sheet.write(row, 4, data['gross_profit'], formats['money_format_bold'])

        row += 1
        sheet.merge_range('A{}:F{}'.format(row + 1, row + 1), 'Other Income(+)', formats['header_left'])
        row += 1

        if 'other income' in data:
            row = self._write_entries(data['other income'], is_compact, sheet, formats, row)

        sheet.merge_range('A{}:F{}'.format(row + 1, row + 1), 'Selling and Distribution Expenses(-)',
                          formats['header_left'])
        row += 1

        if 'selling and distribution expenses' in data:
            row = self._write_entries(data['selling and distribution expenses'], is_compact, sheet, formats, row)

        sheet.merge_range('A{}:F{}'.format(row + 1, row + 1), 'Administrative Expenses(-)', formats['header_left'])
        row += 1

        if 'administrative expenses' in data:
            row = self._write_entries(data['administrative expenses'], is_compact, sheet, formats, row)

        sheet.merge_range('A{}:F{}'.format(row + 1, row + 1), 'Expenses(-)', formats['header_left'])
        row += 1

        if 'expenses' in data:
            row = self._write_entries(data['expenses'], is_compact, sheet, formats, row)

        sheet.merge_range('A{}:F{}'.format(row + 1, row + 1), 'Depreciation(-)', formats['header_left'])
        row += 1

        if 'depreciation' in data:
            row = self._write_entries(data['depreciation'], is_compact, sheet, formats, row)

        sheet.merge_range('A{}:D{}'.format(row + 1, row + 1), 'RESULT FROM OPERATING ACTIVITIES (PBIT)',
                          formats['header_left'])
        sheet.write(row, 4, data['pbit'], formats['money_format_bold'])

        row += 1
        sheet.merge_range('A{}:F{}'.format(row + 1, row + 1), 'Financial Income(+)', formats['header_left'])
        row += 1

        if 'financial income' in data:
            row = self._write_entries(data['financial_income'], is_compact, sheet, formats, row)

        sheet.merge_range('A{}:F{}'.format(row + 1, row + 1), 'Financial Cost(-)', formats['header_left'])
        row += 1

        if 'financial costs' in data:
            row = self._write_entries(data['financial costs'], is_compact, sheet, formats, row)

        sheet.merge_range('A{}:D{}'.format(row + 1, row + 1), 'PROFIT BEFORE TAX (PBT)', formats['header_left'])
        sheet.write(row, 4, data['pbt'], formats['money_format_bold'])

        row += 1
        sheet.merge_range('A{}:F{}'.format(row + 1, row + 1), 'Tax Expense(-)', formats['header_left'])
        row += 1

        if 'tax expense' in data:
            row = self._write_entries(data['tax_expense'], is_compact, sheet, formats, row)

        sheet.merge_range('A{}:D{}'.format(row + 1, row + 1), 'NET PROFIT', formats['header_left'])
        sheet.write(row, 4, data['net_profit'], formats['money_format_bold'])
        row += 1

    def _write_sheet_balance_statement(self, data, is_compact, sheet, formats, row):

        sheet.merge_range('A{}:F{}'.format(row + 1, row + 1), 'Current Assets(+)', formats['header_left'])
        row += 1

        if 'current assets' in data:
            row = self._write_entries(data['current assets'], is_compact, sheet, formats, row)

        sheet.merge_range('A{}:F{}'.format(row + 1, row + 1), 'Receivable Accounts(+)', formats['header_left'])
        row += 1

        if 'receivable' in data:
            row = self._write_entries(data['receivable'], is_compact, sheet, formats, row)

        sheet.merge_range('A{}:F{}'.format(row + 1, row + 1), 'Prepayments(+)', formats['header_left'])
        sheet.write(row, 4, data['gross_profit'], formats['money_format_bold'])
        row += 1

        if 'prepayments' in data:
            row = self._write_entries(data['prepayments'], is_compact, sheet, formats, row)

        sheet.merge_range('A{}:F{}'.format(row + 1, row + 1), 'Bank and Cash(+)', formats['header_left'])
        row += 1

        if 'bank and cash' in data:
            row = self._write_entries(data['bank and cash'], is_compact, sheet, formats, row)

        sheet.merge_range('A{}:F{}'.format(row + 1, row + 1), 'Fixed Assets(+)', formats['header_left'])
        row += 1

        if 'fixed assets' in data:
            row = self._write_entries(data['fixed assets'], is_compact, sheet, formats, row)

        sheet.merge_range('A{}:F{}'.format(row + 1, row + 1), 'Non-Current Assets(+)', formats['header_left'])
        row += 1

        if 'non-current assets' in data:
            row = self._write_entries(data['non-current assets'], is_compact, sheet, formats, row)

        sheet.merge_range('A{}:D{}'.format(row + 1, row + 1), 'TOTAL ASSETS', formats['header_left'])
        sheet.write(row, 4, data['total_assets'], formats['money_format_bold'])

        row += 1
        sheet.merge_range('A{}:F{}'.format(row + 1, row + 1), 'Current Liabilities(-)', formats['header_left'])
        row += 1

        if 'current liabilities' in data:
            row = self._write_entries(data['current liabilities'], is_compact, sheet, formats, row)

        sheet.merge_range('A{}:F{}'.format(row + 1, row + 1), 'Credit Card(-)', formats['header_left'])
        row += 1

        if 'credit card' in data:
            row = self._write_entries(data['credit card'], is_compact, sheet, formats, row)

        sheet.merge_range('A{}:F{}'.format(row + 1, row + 1), 'Payable(-)', formats['header_left'])
        row += 1

        if 'payable' in data:
            row = self._write_entries(data['payable'], is_compact, sheet, formats, row)

        sheet.merge_range('A{}:F{}'.format(row + 1, row + 1), 'Non-Current Liabilities(-)', formats['header_left'])
        row += 1

        if 'non-current liabilities' in data:
            row = self._write_entries(data['non-current liabilities'], is_compact, sheet, formats, row)

        sheet.merge_range('A{}:D{}'.format(row + 1, row + 1), 'NET ASSETS', formats['header_left'])
        sheet.write(row, 4, data['net_assets'], formats['money_format_bold'])

        row += 1
        sheet.merge_range('A{}:F{}'.format(row + 1, row + 1), 'Equity(+)', formats['header_left'])
        row += 1

        if 'equity' in data:
            row = self._write_entries(data['equity'], is_compact, sheet, formats, row)

        sheet.merge_range('B{}:D{}'.format(row + 1, row + 1), 'Net Profit(+)', formats['body_left'])
        sheet.write(row, 4, data['net_profit'], formats['money_format'])

        row += 1
        sheet.merge_range('A{}:D{}'.format(row + 1, row + 1), 'TOTAL EQUITY', formats['header_left'])
        sheet.write(row, 4, data['total_equity'], formats['money_format_bold'])
        row += 1
