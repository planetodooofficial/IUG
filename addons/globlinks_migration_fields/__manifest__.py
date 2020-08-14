{
    'name': 'GlobeLinks  Migration fields',
    'version': '1.1',
    'category': 'Data Migration',
    'author': 'Kastech',

    'summary': 'Add Fields for Migrate data from Globelinks to IUG',
    'description': """

    """,
    'website': 'https://www.kastech.com',

    'depends': [
        'base','bista_iugroup'
    ],
    'data': [
        'views/partner_view.xml',
        'views/event_view.xml',
        'views/interactions_view.xml'
    ],


    'installable': True,
    'application': True,
    'auto_install': False,

}