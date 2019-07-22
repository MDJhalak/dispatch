# -*- coding: utf-8 -*-

from odoo import models


class ReportXlsIncomeBalanceStatementAnalytic(models.AbstractModel):
    _name = 'report.bs_report.report_xls_bs_income_balance_analytic'
    _inherit = 'report.bs_report.report_xls_bs_income_balance_statement'
