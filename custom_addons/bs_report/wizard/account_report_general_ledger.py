# -*- coding: utf-8 -*-

from odoo import api, fields, models
from bs_lib.service import warning


class AccountReportGeneralLedger(models.TransientModel):

    _inherit = "account.report.general.ledger"
    
    account_ids = fields.Many2many('account.account', string='Accounts', required=True,
                                   default=lambda self: self._context.get('active_ids') if self._context.get('active_ids', False) else self.env['account.account'].search([]))

    def _print_html_report(self, data):
        data = self.pre_print_report(data)
        data['form'].update(self.read(['initial_balance', 'sortby', 'account_ids'])[0])
        if data['form'].get('initial_balance') and not data['form'].get('date_from'):
            raise warning.ThrowException(msg="You must define a Start Date", title="User Error")
        records = self.env[data['model']].browse(data.get('ids', []))
        return self.env.ref('bs_report.action_html_report_general_ledger').with_context(landscape=True).report_action(records, data=data)

    def _print_report(self, data):
        res = super(AccountReportGeneralLedger, self)._print_report(data)
        res['data']['form'].update(self.read(['account_ids'])[0])
        return res

    @api.multi
    def print_xls_report(self):
        self.ensure_one()
        self.account_ids = self._context.get('active_ids', [])
        return self.env.ref('bs_report.action_xls_report_general_ledger').report_action(self)
