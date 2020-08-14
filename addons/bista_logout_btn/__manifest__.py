# -*- coding: utf-8 -*-
{
    'name': 'Custom logout button module for OpenERP 7',
    'version': '1.1',
    'description': """
		Custom logout button module
	""",
    'author': 'Bista Solutions Pvt. Ltd',
    'website': 'http://www.openerp.com',
    'depends': ['web'],
    'category': 'Bista Solutions',
    'data':['bista_logout_view.xml'],
    'qweb': ['static/src/xml/base.xml'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
