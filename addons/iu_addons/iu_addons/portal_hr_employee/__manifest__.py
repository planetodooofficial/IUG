# -*- coding: utf-8 -*-
{
    'name': "Portal HR employees",
    'description': """
This module adds a list of employees to your portal's contact page if hr and portal_crm (which creates the contact page) are installed.
=======================================================================================================================================
    """,
    'author': "Geetha",
    'website': "http://www.yourcompany.com",
    'category': 'Tools',
    'version': '0.1',
    'depends': ['hr','website_crm','crm','base','portal','website_hr'],
    'data': [
	    'views/hr_templates.xml',
        #'views/views.xml',
    ],
    'css': ['static/src/css/portal_hr_employees.css'],
    'installable': True,
    "active": False,
    'application':False,
}