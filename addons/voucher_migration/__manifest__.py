# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Voucher Migration',
    'version' : '1.1',
    'category': 'Accounting',
    'depends' : ['base_setup','account','product', 'analytic', 'report', 'web_planner'],
    'data': [
        'views/voucher.xml',
        'wizard/migration.xml'

    ],
    'demo': [
    ],
    'qweb': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
