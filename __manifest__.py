# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'To-Do List',
    'version' : '1.0',
    'summary': 'Todo list management',
    'sequence': 10,
    'description': '"To-Do list management software"',
    'category': 'Productivity',
    'website': 'https://www.proosoftcloud.com/',
    'depends' : [],
    'data': ['security/ir.model.access.csv',
             'data/data.xml',
             'views/menu.xml',
             'views/task_view.xml',
             'views/project_view.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
}