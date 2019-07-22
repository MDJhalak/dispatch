# -*- coding: utf-8 -*-

from odoo import models


class BSIncomeBalanceStatementGeneralInterface(models.AbstractModel):

    _name = "report.bs_report.report_bs_income_balance_general"
    _inherit = "report.bs_report.report_bs_income_balance_statement"
