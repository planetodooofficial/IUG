# -*- coding: utf-8 -*-
{
    'name': 'Document lines sequences',
    'version': '10.0.2.1.0',
    'category': 'Accounting,Purchase',
    'author': 'Geetha',
    'description': """ 
    Module adds sequence field on purchase order and invoice lines.
    Sequence can be set with line dragging.
    """,
    'website': 'http://www.kastechssg.com/',
    'depends': ['account','purchase'],
    'data': [
        'account_invoice_view.xml',
        'purchase_order_view.xml',
    ],
}
