# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Profile - function",

    'summary': """
       Extends portal profile with function""",

    'description': """
        
    """,

    'author': "RL Software Development ApS",
    'website': "http://rlsd.dk/",

    'category': 'Website',
    'version': '15.0.1.0.2',

    'depends': [
        'website', 
        'portal'
        ],

    'data': [
        'data/data.xml',
        'views/portal_profile.xml', 
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
}