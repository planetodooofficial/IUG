# -*- coding: utf-8 -*-

{
    'name': 'Account Invoice Merge Wizard',
    'version': '1.0',
    'category': 'Finance',
    'summary': "Merge invoices in draft",
    'description': """
This module adds an action in the invoices lists to merge of invoices. Here are the condition to allow merge:
- Type should be the same (customer Invoice, supplier invoice, Customer or Supplier Refund)
- Partner should be the same
- Currency should be the same
- Account receivable account should be the same
    """,
    'author': "geetha",
    'website': "http://www.yourcompany.com",
    
    'depends': ['account'],
    'data': [
        'wizard/invoice_merge_view.xml',
    ],
    'installable': True,
    'application': True,
}
