# -*- encoding: utf-8 -*-
{
    'name' : 'Database Auto-Backup',
    'version' : '10.0',
    'author' : 'Teckzilla',
    'category' : 'Generic Modules',
    'summary': 'Backups',
    'description': """This Application allows you to take backup of database and send it to a remote
server""",
    'depends' : ['base'],
    'data': [
      'views/bkp_conf_view.xml',
      'data/backup_data.xml',
    ],
    'auto_install': False,
    'installable': True
}
