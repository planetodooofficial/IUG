{
    'name': 'Bista Check',
    'version': '1.0',
    'category': 'Bista Check',
    "sequence": 16,
    'description': """
        Bista Check Custimization
        For Bulk Check Printing
        """,
        'author': 'Bista Solutions Pvt. Ltd.',

    'depends': ['bista_iugroup','l10n_us_check_printing'],
    'init_xml': [],
    'data': [
        'wizard/account_check_print_view.xml',
        
    ],
    'demo_xml': [],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
