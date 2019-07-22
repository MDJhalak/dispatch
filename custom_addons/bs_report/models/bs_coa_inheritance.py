# -*- coding: utf-8 -*-

from odoo import models, fields, api
from bs_lib.service import warning


class BSCoAInheritance(models.Model):
    _name = "bs.coa.inheritance"
    _description = "Create inheritance in COA"
    _order = "id, account_account_id"

    name = fields.Char(string="Name", required=True)
    account_account_id = fields.Many2one(comodel_name="account.account", required=True, domain=[('is_view', '=', True)], string="Chart of Account", index=True)
    user_type_id = fields.Many2one(comodel_name="account.account.type", related='account_account_id.user_type_id')
    inheritance_lines = fields.One2many(comodel_name="bs.coa.inheritance.line", inverse_name="coa_inheritance_id", string="Inheritance Lines",
                                        required=True)

    @api.onchange("account_account_id")
    def _onchange_account_id(self):
        if self.account_account_id:
            count = self.search_count([('account_account_id', '=', self.account_account_id.id)])
            if count > 0:
                raise warning.ThrowException(message="This chart of account is already assigned, please select another.", title="Data Error")


class BSCoAInheritanceLine(models.Model):
    _name = "bs.coa.inheritance.line"
    _description = "Child COA for View Type COA"
    _order = "coa_inheritance_id"

    coa_inheritance_id = fields.Many2one(comodel_name="bs.coa.inheritance", string="COA inheritance reference", index=True, ondelete='cascade')
    account_account_id = fields.Many2one(comodel_name="account.account", required=True, string="Child COA", index=True)

    @api.onchange("account_account_id")
    def _onchange_parent_user_type(self):
        if self.account_account_id:
            record = self.search([('account_account_id', '=', self.account_account_id.id)])
            if len(record) > 0:
                raise warning.ThrowException(message=("This chart of account is already assigned as child in (%s), please select another."
                                                     % record.coa_inheritance_id.name),
                                            title="Data Error")
        user_type_id = self._context.get('user_type_id', False)
        if user_type_id:
            return {'domain':
                        {
                            'account_account_id': [('user_type_id', '=', user_type_id)]
                        }
                    }
