{
    'name': 'GlobeLinks Data Migration',
    'version': '1.1',
    'category': 'Data Migration',
    'author':'Kastech',

    'summary': 'Migrate data from Globelinks to IUG',
    'description': """

    """,
    'website': 'https://www.kastech.com',

    'depends': [
        'base',
        "bista_iugroup",
        "globlinks_migration_fields"
    ],
    'data': [
        #'views/partner_view.xml',
        'views/upload_script.xml',
        'security/ir.model.access.csv'
    ],


    'installable': True,
    'application': True,
    'auto_install': False,

}