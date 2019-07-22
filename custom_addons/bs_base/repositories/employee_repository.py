# -*- coding: utf-8 -*-

from odoo import fields, models, api, SUPERUSER_ID
from bs_lib.service import common


class EmployeeRepository(models.TransientModel):
    _name = "bs.employee.repository"

    @api.multi
    def get_employee(self, user):
        return self.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
