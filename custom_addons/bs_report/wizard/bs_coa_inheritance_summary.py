# -*- coding: utf-8 -*-

from odoo import models, fields, api
from bs_lib.service import warning


class BSCoAInheritanceSummary(models.TransientModel):
    _name = "bs.coa.inheritance.summary"
    _description = "Model for COA inheritance summary"

    ## Selection ##
    display_type_selection = [
        ('all', "All"),
        ('nonzero', "With balance is not equal to 0")
    ]
    move_type_selection = [('all', "All"), ('posted', "Posted")]
    ####

    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    move_type = fields.Selection(selection=move_type_selection, string="Move Type", required=True, default="all")
    display_type = fields.Selection(selection=display_type_selection, string="Display", required=True, default="all")

    @api.onchange('start_date', 'end_date')
    def check_date(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            self.update({
                'start_date': fields.Date.today(),
                'end_date': fields.Date.today()
            })
            return warning.ThrowWarning(title="Data Error", message="End Date can not be earlier than Start Date")

    @api.multi
    def _process_data(self):
        self.ensure_one()
        [data] = self.read()
        self.start_date = False
        self.end_date = False

        datas = {
            'ids': self._context.get('active_ids', []),
            'form': data,
            'model': self.__class__.__name__,
        }
        return {
            'data': datas,
            'object': self
        }

    def _print_report(self, process):
        return self.env.ref('bs_report.report_bs_coa_inheritance_summary_action').report_action(process['object'], data=process['data'])

    def _print_html_report(self, process):
        return self.env.ref('bs_report.html_report_bs_coa_inheritance_summary_action').report_action(process['object'], data=process['data'])

    @api.multi
    def check_report(self):
        data = self._process_data()
        return self._print_report(data)

    @api.multi
    def check_html_report(self):
        data = self._process_data()
        return self._print_html_report(data)