
{
    'name': 'SMSClient',
    'version': '1.0',
    'category': 'Tools',
    'description': """This module Provides SMS Gateway to odoo""",
    'author': '',
    'website': '',
    'depends': ['base','mail'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/smsclient_view.xml',
        'views/serveraction_view.xml',
        'views/smsclient_data.xml',
        'wizard/mass_sms_view.xml',
        'views/partner_sms_send_view.xml',
    ],
	'active': False,
    'installable': True,
    'auto_install': False,
}