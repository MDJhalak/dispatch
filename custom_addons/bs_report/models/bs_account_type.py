# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BSAccountType(models.TransientModel):

    _name = "bs.account.type"
    _description = "Create new/extra account type for model 'account.account.type'"

    def _is_record_exist(self, account):
        """
        Check if account type already exist

        :param account: dict
        :return: bool
        """
        accountAccountType = self.env['account.account.type']
        if accountAccountType.search_count(['&', ('name', '=', account['name']), ('type', '=', account['type'])]):
            return True
        return False

    @api.model
    def _generate_new_account_type(self):
        """
        Create new/extra account type for model 'account.account.type'
        """
        accountAccountType = self.env['account.account.type']
        account_list = [
            {'name': "Selling and Distribution expenses", 'type': "other"},
            {'name': "Administrative expenses", 'type': "other"},
            {'name': "Financial Income", 'type': "other"},
            {'name': "Financial Costs", 'type': "other"},
            {'name': "Tax expense", 'type': "other"}
        ]
        for account in account_list:
            if not self._is_record_exist(account):
                accountAccountType.create({
                    'name': account['name'],
                    'type': account['type']
                })
