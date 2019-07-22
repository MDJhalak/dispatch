# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BSIncomeBalanceGeneral(models.TransientModel):
    _name = "bs.income.balance.general"
    _description = "Common model for both General Income statement & Balance sheet"
    _inherit = "bs.income.balance.common"

    move_type_selection = [('all', "All"),('posted', "Posted")]

    move_type = fields.Selection(selection=move_type_selection, string="Move Type", required=True, default="all")

    def _print_report(self, process):
        return self.env.ref('bs_report.report_bs_income_balance_statement_general_action').report_action(process['object'], data=process['data'])

    def _print_html_report(self, process):
        return self.env.ref('bs_report.html_report_bs_income_balance_statement_general_action').report_action(process['object'], data=process['data'])

    @api.multi
    def print_xls_report(self):
        self.ensure_one()
        return self.env.ref('bs_report.xls_report_bs_income_balance_statement_general_action').report_action(self)
