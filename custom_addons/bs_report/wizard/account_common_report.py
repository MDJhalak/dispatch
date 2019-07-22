# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountCommonReport(models.TransientModel):

    _inherit = "account.common.report"

    def _print_html_report(self, data):
        raise NotImplementedError()

    @api.multi
    def check_html_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang') or 'en_US')
        return self._print_html_report(data)
