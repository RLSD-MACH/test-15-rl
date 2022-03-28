# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Project",

    'summary': """
        Project time management system""",

    'description': """
        Long description of module's purpose
    """,

    'author': "RL Software Development ApS",
    'website': "http://rlsd.dk/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Services/Project',
    'version': '15.0.1.0.5',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'mail',
        'hr',
        'hr_contract',
        'sale',
        'purchase',
        'account',
        'rlbooks_imp_sale'
        ],

    # always loaded
    'data': [
        'data/ir_sequence_data.xml',
        'data/project_stage_data.xml',
        'data/project_group_data.xml',
        'data/project_reminder_stage_data.xml',
        'data/mail_activity_type.xml',  

        'views/project_project.xml',
        'views/project_stage.xml',
        'views/project_group.xml',
        'views/project_reminder_stage.xml',
        'views/project_reminder.xml',       
        'views/project_entry.xml',    
        'views/hr_contract.xml', 
        'views/hr_employee.xml',
        'views/mileage_report.xml', 
        'views/account_move.xml',
        'views/sale.xml', 
        'views/res_partner.xml', 
        'views/res_config_settings_views.xml',
        'views/timesheet_timesheet.xml',
        'views/templates.xml',
        'wizard/create_reminder_views.xml',
        'wizard/create_entry_views.xml',

        
          
        'security/groups.xml', 
        'security/security.xml',   
        'security/ir.model.access.csv',   
        
    ],
    
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
}