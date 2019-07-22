# -*- coding: utf-8 -*-

from odoo import models, api
from bs_lib.service import warning


class BSCoAInheritanceSummaryReport(models.AbstractModel):

    _name = "report.bs_report.report_bs_coa_inheritance_summary"

    @staticmethod
    def _get_amount(account_list, parent_map, line_data, nonzero):
        data = {}
        for line in line_data:
            if nonzero and line.balance == 0:
                continue
            account_id_str = str(line.account_id.id)
            if not data.get(account_id_str, False):
                data[account_id_str] = {
                    'account_id': line.account_id.id,
                    'amount': 0
                }
            data[account_id_str].update({
                'amount': data[account_id_str].get('amount', 0) + line.balance
            })

        # propagate & add child account amount to parent account amount
        # check parent-child relation recursively
        for account_id in account_list:
            account_id_str = str(account_id)
            while True:
                parent_account_id = parent_map.get(account_id_str, False)
                if parent_account_id:
                    parent_data = data.get(str(parent_account_id), False)
                    if not parent_data:
                        data[str(parent_account_id)] = {
                            'account_id': parent_account_id,
                            'amount': 0
                        }
                        parent_data = data.get(str(parent_account_id), {})
                    child_data = data.get(account_id_str, {})
                    parent_data['amount'] = parent_data.get('amount', 0) + child_data.get('amount', 0)
                    account_id_str = str(parent_account_id)
                else:
                    break
        return data

    def _get_account_move_data(self, **kwargs):
        start_date = kwargs['start_date'] if kwargs['start_date'] else None
        end_date = kwargs['end_date'] if kwargs['end_date'] else None
        move_type = kwargs['move_type'] if kwargs['move_type'] else None
        account_list = kwargs['account_list'] if kwargs['account_list'] else None

        condition = [('account_id', 'in', account_list)]
        if start_date:
            if condition:
                condition.insert(0, '&')
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

    def _get_coa_inheritance_accounts(self, ids):
        coa_inheritance = self.env['bs.coa.inheritance'].browse(ids)
        accounts = []
        account_list = []
        parent_map = {}
        for record in coa_inheritance:
            data = {
                'account_id': record.account_account_id.id,
                'account_name': "(%s) %s" % (record.account_account_id.code, record.account_account_id.name),
                'type': 'parent',
                'child': []
            }
            account_list.append(record.account_account_id.id)
            for account in record.inheritance_lines:
                data['child'].append({
                    'account_id': account.account_account_id.id,
                    'account_name': "(%s) %s" % (account.account_account_id.code, account.account_account_id.name),
                    'type': 'child',
                })
                account_list.append(account.account_account_id.id)
                parent_map[str(account.account_account_id.id)] = record.account_account_id.id
            accounts.append(data)
        return accounts, account_list, parent_map

    @api.model
    def get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise warning.ThrowException(message="Form content is missing, this report cannot be printed.", title="Data Error")

        report = self.env['ir.actions.report']._get_report_from_name('bs_report.report_bs_coa_inheritance_summary')
        start_date = data['form']['start_date'] if 'start_date' in data['form'] else None
        end_date = data['form']['end_date'] if 'end_date' in data['form'] else None
        move_type = data['form']['move_type'] if 'move_type' in data['form'] else None
        coa_inheritance_ids = data['ids']
        selected_model = data['model'] if 'model' in data else "none"

        account_structure, account_list, parent_map = self._get_coa_inheritance_accounts(coa_inheritance_ids)
        financial_data = self._get_account_move_data(start_date=start_date, end_date=end_date, move_type=move_type, account_list=account_list)
        info = {
            'start_date': start_date,
            'end_date': end_date,
            'statement_name': 'Statement of Chart of Account Inheritance',
        }
        return {
            'doc_ids': self.ids,
            'doc_model': report.model,
            'data': account_structure,
            'amount_data': self._get_amount(account_list=account_list, parent_map=parent_map, line_data=financial_data,
                                            nonzero=data['form']['display_type'] == 'nonzero'),
            'info': info,
        }
