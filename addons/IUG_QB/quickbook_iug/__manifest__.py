{
    'name': 'QuickBooks Odoo Connector',
    'version': '10.0',
    'category': 'Generic Modules',
    'description': """ Import QuickBook Data to Odoo and Export Odoo Data to QuickBook""",
    'author': 'Planet-odoo',
    'website': 'http://www.planet-odoo.com',
    'depends': ['base','sale','web','account','bista_iugroup'],
    'data': [
        'views/data_crons.xml',
        'views/quick_configuration.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
