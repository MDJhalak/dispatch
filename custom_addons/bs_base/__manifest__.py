# -*- coding: utf-8 -*-
{
    'name': "Base Add-on",

    'summary': """
        Base Add-on for Brain Station 23's Odoo Application""",

    'description': """
    """,

    'author': "Brain Station-23 LTD",

    'website': "http://www.brainstation-23.com",

    'category': 'Base',

    'version': '1.0.1',

    'license': 'OPL-1',

    'depends': ['base', 'web'],

    'data': [
        'security/bs_base_security.xml',

        'views/webclient_templates.xml',
    ],

    'auto_install': True
}