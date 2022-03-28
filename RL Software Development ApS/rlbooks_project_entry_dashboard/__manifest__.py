# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Project - Dashboards",

    'summary': """
       Install Dashboards""",

    'description': """
        Contact Mads Christensen for more information
    """,

    'author': "RL Software Development ApS",
    'website': "http://rlsd.dk/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Services/Project',
    'version': '15.0.1.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'rlbooks_project',
        ],

    # always loaded
    'data': [
        
        'views/project_entry.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
}