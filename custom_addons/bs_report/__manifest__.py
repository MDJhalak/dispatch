# -*- coding: utf-8 -*-
{
    'name': "Financial Reports",

    'summary': """
        Add custom reports and Customize/update existing reports of Odoo""",

    'description': """
    """,

    'author': "Brain Station-23 LTD",

    'website': "http://www.brainstation-23.com",

    'category': 'Reporting',

    'version': '1.0',

    'license': 'OPL-1',

    'depends': [
        'base',
        'bs_base',
        'account',
        'analytic',
        'report_xlsx'
    ],

    'data': [
        'data/report_paperformat.xml',

        # 'security/ir.model.access.csv',

        'template/report/bs_income_balance_statement_analytic_template.xml',
        'template/report/bs_income_balance_statement_general_template.xml',
        'template/report/bs_coa_inheritance_summary_template.xml',
        'template/report/report_partnerledger.xml',
        'template/report/external_layout_background.xml',

        'views/resources.xml',
        'views/bs_account_type_views.xml',
        'views/account_views.xml',
        'views/bs_coa_inheritance_views.xml',

        'wizard/accounting_report_views.xml',
        'wizard/account_report_general_ledger_views.xml',
        'wizard/account_report_partner_ledger_views.xml',
        'wizard/bs_income_balance_statement_common_views.xml',
        'wizard/bs_income_balance_statement_analytic_views.xml',
        'wizard/bs_income_balance_statement_general_views.xml',
        'wizard/bs_coa_inheritance_summary_views.xml',

        'report/bs_report_reports.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}