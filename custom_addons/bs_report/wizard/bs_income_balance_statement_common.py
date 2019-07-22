# -*- coding: utf-8 -*-

from odoo import models, fields, api
from bs_lib.service import warning
from abc import abstractmethod
from ast import literal_eval


class BSIncomeBalanceCommon(models.TransientModel):
    _name = "bs.income.balance.common"
    _description = "Common model for both Income statement & Balance sheet"

    ## Selection ##
    report_type_selection = [
        ('compact', "Compact"),
        ('expand', "Expanded")
    ]
    display_type_selection = [
        ('all', "All"),
        ('nonzero', "With balance is not equal to 0")
    ]
    ####

    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    report_type = fields.Selection(selection=report_type_selection, string="Report Type", required=True, default="expand")
    display_type = fields.Selection(selection=display_type_selection, string="Display", required=True, default="all")
    statement_type = fields.Char(string="Statement Type")

    @api.onchange('start_date', 'end_date')
    def check_date(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            self.update({
                'start_date': fields.Date.today(),
                'end_date': fields.Date.today()
            })
            return warning.ThrowWarning(title="Data Error", message="End Date can not be earlier than Start Date")

    @api.model
    def default_get(self, fields_list):
        res = super(BSIncomeBalanceCommon, self).default_get(fields_list)
        context = self.env.context.copy()
        model_name = context.get('active_model', False)
        if model_name == 'account.analytic.account':
            res['analytic_account_ids'] = str(context.get("active_ids", []))
        res['statement_type'] = context.get("statement_type", None)
        return res

    @api.multi
    def _process_data(self):
        self.ensure_one()
        [data] = self.read()
        self.start_date = False
        self.end_date = False
        analytic_account_ids = literal_eval(data['analytic_account_ids'] if 'analytic_account_ids' in data else "[]")

        analytic_account_data = None
        if len(analytic_account_ids) == 1:
            analytic_account_data = self.env['account.analytic.account'].browse(analytic_account_ids[0])
        datas = {
            'ids': self._context.get('active_ids', []),
            'form': data,
            'model': self.__class__.__name__,
            'analytic_account_name': analytic_account_data.name if analytic_account_data else None
        }
        return {
            'data': datas,
            'object': analytic_account_data or self
        }

    @abstractmethod
    def _print_report(self, process):
        raise NotImplementedError("Not implemented in base class, Override method in child class")

    @abstractmethod
    def _print_html_report(self, process):
        raise NotImplementedError("Not implemented in base class, Override method in child class")

    @api.multi
    def check_report(self):
        data = self._process_data()
        return self._print_report(data)

    @api.multi
    def check_html_report(self):
        data = self._process_data()
        return self._print_html_report(data)

    @api.multi
    @abstractmethod
    def print_xls_report(self):
        raise NotImplementedError("Not implemented in base class, Override method in child class")
