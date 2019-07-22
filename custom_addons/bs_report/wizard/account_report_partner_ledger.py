# -*- coding: utf-8 -*-

from odoo import fields, models, _, api


class AccountReportPartnerLedger(models.TransientModel):

    _inherit = "account.report.partner.ledger"

    def _print_html_report(self, data):
        data = self.pre_print_report(data)
        data['form'].update({'reconciled': self.reconciled, 'amount_currency': self.amount_currency})
        return self.env.ref('bs_report.action_html_report_partnerledger').report_action(self, data=data)

    @api.multi
    def print_xls_report(self):
        self.ensure_one()
        return self.env.ref('bs_report.action_xls_report_partnerledger').report_action(self)
