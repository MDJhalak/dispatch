# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BSIncomeBalanceAnalytic(models.TransientModel):
    _name = "bs.income.balance.analytic"
    _description = "Common model for both Analytic Account Income statement & Balance sheet"
    _inherit = "bs.income.balance.common"

    analytic_account_ids = fields.Char(string="List of selected analytic accounts")

    def _print_report(self, process):
        return self.env.ref('bs_report.report_bs_income_balance_statement_analytic_action').report_action(process['object'], data=process['data'])

    def _print_html_report(self, process):
        return self.env.ref('bs_report.html_report_bs_income_balance_statement_analytic_action').report_action(process['object'], data=process['data'])

    @api.multi
    def print_xls_report(self):
        self.ensure_one()
        return self.env.ref('bs_report.xls_report_bs_income_balance_statement_analytic_action').report_action(self)
