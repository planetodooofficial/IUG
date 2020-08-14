import time
from openerp.report import report_sxw
from openerp.osv import osv
from datetime import datetime, timedelta, date

class sale_invoice_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(sale_invoice_report, self).__init__(cr, uid, name, context=context)
        active_model = context.get('active_model',False)
        active_ids = context.get('active_ids',False)
        if active_ids:
            actives = self.pool.get(active_model).browse(self.cr,self.uid,active_ids)
            for active in actives:
                if active.type == 'out_invoice':
                    raise osv.except_osv(('Supplier Invoice !!!'),('You cannot generate supplier invoice report in supplier invoice'))
        self.localcontext.update({
            'time': time,
        })


report_sxw.report_sxw(
    'report.account.invoice.sfi.inherit',
    'account.invoice',
    'custom_addons/bista_check/report/account_print_invoice.rml',
    parser=sale_invoice_report,header=False
)
