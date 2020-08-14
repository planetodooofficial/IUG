import time
from odoo.report import report_sxw
from openerp.tools import amount_to_text_en

from datetime import datetime, timedelta
from odoo.tools import amount_to_text_en

class report_account_print_check(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_account_print_check, self).__init__(cr, uid, name, context)
        self.number_lines = 0
        self.number_add = 0
        self.context = context
        self.localcontext.update({
                                 'time': time,
                                 'get_check_details':self.get_check_details
                                 })

    def get_check_details(self,invoice):
        if self._context and self._context.get('check_no'):
            res ={}
            for check_no in self._context['check_no']:
                for invoice_checkno_id in invoice.invoice_checkno_ids:
                    if invoice_checkno_id.check_no == check_no:
                        amt_paid_date = datetime.strptime(invoice_checkno_id.paid_date,"%Y-%m-%d").strftime('%m/%d/%Y')
                        res['total_amt'] = invoice_checkno_id.amt_paid
                        res['date_paid'] = amt_paid_date
                        res['amount_in_word'] = amount_to_text_en.amount_to_text(invoice_checkno_id.amt_paid,'en','USD')
                        res['check_no']=check_no
            res['invoice_date'] = datetime.strptime(invoice.date_invoice,"%Y-%m-%d").strftime('%m/%d/%Y')
            return res

report_sxw.report_sxw('report.account.check.print', 'account.invoice', 'custom_addons/bista_check/report/check_print.rml',
                      parser=report_account_print_check, header=False)