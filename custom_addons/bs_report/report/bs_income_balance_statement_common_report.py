# -*- coding: utf-8 -*-

from odoo import models, fields, api
from bs_lib.service import warning
from bs_lib.application import constant
import re


class BSIncomeBalanceStatementReport(models.AbstractModel):

    _name = "report.bs_report.report_bs_income_balance_statement"

    gross_profit = 0.0
    net_profit = 0.0
    total_assets = 0.0
    net_assets = 0.0
    total_equity = 0.0
    pbit = 0.0
    pbt = 0.0

    @staticmethod
    def dict_to_list(data):
        res = []
        for key, value in data.items():
            res.append(value)
        return res

    def _process_analytic_data(self, line_data, data, nonzero):
        for line in line_data:
            if nonzero and line.amount == 0:
                continue
            line_type = line.general_account_id.user_type_id.name.lower() if line.general_account_id else "undefined"
            if not data.get(line_type, False):
                data[line_type] = []
            data[line_type].append({
                'name': line.name,
                'amount': line.amount
            })
            self._set_total_amount(line.amount, line_type)
    
    def _process_move_data(self, line_data, data, nonzero):
        temp_data = {}
        for line in line_data:
            if nonzero and line.balance == 0:
                continue
            line_type = line.account_id.user_type_id.name.lower() if line.account_id else "undefined"
            line_name = "(%s) %s" % (line.account_id.code, line.account_id.name)
            if not temp_data.get(line_name, False):
                temp_data[line_name] = {
                    'name': line_name,
                    'type': line_type,
                    'amount': 0
                }
            temp_data[line_name].update({
                'amount': temp_data[line_name].get('amount', 0) + line.balance
            })

        for entry in self.dict_to_list(temp_data):
            if nonzero and entry['amount'] == 0:
                continue
            if not data.get(entry['type'], False):
                data[entry['type']] = []
            data[entry['type']].append({
                'name': entry['name'],
                'amount': entry['amount']
            })
            self._set_total_amount(entry['amount'], entry['type'])

    def _generate_data_list(self, line_data, nonzero=False):
        data = {}
        self.gross_profit = 0.0
        self.net_profit = 0.0
        self.total_assets = 0.0
        self.net_assets = 0.0
        self.total_equity = 0.0
        self.pbit = 0.0
        self.pbt = 0.0

        class_name = line_data.__class__.__name__
        if class_name == 'account.move.line':
            self._process_move_data(line_data, data, nonzero)
        elif class_name == 'account.analytic.line':
            self._process_analytic_data(line_data, data, nonzero)
            
        self.pbit += self.gross_profit
        self.pbt += self.pbit
        self.net_profit += self.pbt
        self.net_assets += self.total_assets
        self.total_equity += self.net_profit
        data.update({
            'gross_profit': self.gross_profit,
            'net_profit': self.net_profit,
            'total_assets': self.total_assets,
            'net_assets': self.net_assets,
            'total_equity': self.total_equity,
            'pbit': self.pbit,
            'pbt': self.pbt
        })
        return data

    def _set_total_amount(self, amount, entry_type):
        types = constant.BSReport.StatementEntryType
        if entry_type in types.gross_profit_type:
            self.gross_profit += amount
        if entry_type in types.pbit_type:
            self.pbit += amount
        if entry_type in types.pbt_type:
            self.pbt += amount
        if entry_type == 'tax expense':
            self.net_profit += amount
        if entry_type in types.asset_type:
            self.total_assets += amount
        if entry_type in types.liability_type:
            self.net_assets += amount
        if entry_type == 'equity':
            self.total_equity += amount

    def _get_analytic_line_data(self, **kwargs):
        start_date = kwargs['start_date'] if kwargs['start_date'] else None
        end_date = kwargs['end_date'] if kwargs['end_date'] else None
        account_ids = kwargs['account_ids'] if kwargs['account_ids'] else None

        condition = []
        if start_date:
            condition = [('date', '>=', start_date)]
        if end_date:
            if condition:
                condition.insert(0, '&')
            condition += [('date', '<=', end_date)]
        if condition:
            condition.insert(0, '&')
        condition += [('account_id', 'in', account_ids)]
        return self.env['account.analytic.line'].search(condition)

    def _get_account_move_data(self, **kwargs):
        start_date = kwargs['start_date'] if kwargs['start_date'] else None
        end_date = kwargs['end_date'] if kwargs['end_date'] else None
        move_type = kwargs['move_type'] if kwargs['move_type'] else None

        condition = []
        if start_date:
            condition = [('date', '>=', start_date)]
        if end_date:
            if condition:
                condition.insert(0, '&')
            condition += [('date', '<=', end_date)]
        if move_type == 'posted':
            if condition:
                condition.insert(0, '&')
            condition += [('move_id.state', '=', 'posted')]
        return self.env['account.move.line'].search(condition)

    def _get_report_name(self):
        result = re.search('(report.(.*))', self.__class__.__name__)
        return result.group(2)

    @api.model
    def get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise warning.ThrowException(msg="Form content is missing, this report cannot be printed.", title="Data Error")

        report = self.env['ir.actions.report']._get_report_from_name(self._get_report_name())
        start_date = data['form']['start_date'] if 'start_date' in data['form'] else None
        end_date = data['form']['end_date'] if 'end_date' in data['form'] else None
        move_type = data['form']['move_type'] if 'move_type' in data['form'] else None
        account_ids = data['ids']
        selected_model = data['model'] if 'model' in data else "none"

        financial_data = self._get_analytic_line_data(account_ids=account_ids, start_date=start_date, end_date=end_date) if selected_model == 'bs.income.balance.analytic' \
            else self._get_account_move_data(start_date=start_date, end_date=end_date, move_type=move_type)

        info = {
            'start_date': start_date,
            'end_date': end_date,
            'statement_name': 'Statement of Comprehensive Income' if data['form']['statement_type'] == 'income' else 'Statement of Financial Position',
            'statement_type': data['form']['statement_type'],
            'analytic_account_name': data['analytic_account_name'] if 'analytic_account_name' in data else ""
        }
        return {
            'doc_ids': self.ids,
            'doc_model': report.model,
            'data': self._generate_data_list(financial_data, nonzero=data['form']['display_type'] == 'nonzero'),
            'info': info,
            'is_compact': data['form']['report_type'] == 'compact'
        }
