# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "MySQL",

    'summary': """
       Integration to MySQL""",

    'description': """
        Contact Mads Christensen for more information
    """,

    'author': "RL Software Development ApS",
    'website': "http://rlsd.dk/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '15.0.1.0.2',

    # any module necessary for this one to work correctly
    'depends': [
        ],

    # always loaded
    'data': [      
        'views/mysql_login.xml',
        'views/mysql_table.xml',
        'views/mysql_table_row.xml',
        'views/menuitem.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
    ],
    'external_dependencies': {

        'python' : ['pyodbc'],

    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
}