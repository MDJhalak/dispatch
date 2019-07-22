# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountAccount(models.Model):
    _inherit = "account.account"

    is_view = fields.Boolean(string="View", required=True, default=False)