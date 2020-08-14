import time
from openerp.report import report_sxw
from openerp.tools import amount_to_text_en
from openerp.tools.amount_to_text_en import amount_to_text
from datetime import datetime, timedelta
from openerp.osv import osv

class report_account_print_check_group(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_account_print_check_group, self).__init__(cr, uid, name, context)
        self.number_lines = 0
        self.number_add = 0
        self.context = context
        self.localcontext.update({
            'time': time,
            'get_check_details':self.get_check_details,
            'get_individual_data':self.get_individual_data,
            'get_invoice_date':self.get_invoice_date,
        })

    def get_individual_data(self,invoice):
        if self.context.get('Customer Invoice Data'):
            partner_id = str(invoice.partner_id.id)
            if self.context['Customer Invoice Data'].get(partner_id):
                invoice_browse = self.pool.get('account.invoice').browse(self.cr,self.uid,self.context['Customer Invoice Data'][partner_id])
        return invoice_browse

    def get_check_details(self,invoice):
        if self.context and self.context.get('check_no'):
            res ={}
            amt_paid_date, total_amt, amt_paid_date = False, 0.0, ''
            customer_id = invoice.partner_id.id
            for invoice_checkno_id in invoice.invoice_checkno_ids:
                    amt_paid_date = datetime.strptime(invoice_checkno_id.paid_date,"%Y-%m-%d").strftime('%m/%d/%Y')
            for each_data in self.context['Invoice Data']:
                if each_data[1] == customer_id:
                    total_amt = each_data[0]
            res['total_amt'] = total_amt
            res['date_paid'] = amt_paid_date
            res['amount_in_word'] = amount_to_text(total_amt,'en','USD')
            for check_no in self.context['check_no']:
                for invoice_checkno_id in invoice.invoice_checkno_ids:
                    if invoice_checkno_id.check_no == check_no:
                        res['check_no'] = check_no
            return res

    def get_invoice_date(self,line):
        return datetime.strptime(line.date_invoice,"%Y-%m-%d").strftime('%m/%d/%Y')
report_sxw.report_sxw('report.account.invoice.check.print.group', 'account.invoice', 'custom_addons/bista_check/report/check_print_group.rml',
                      parser=report_account_print_check_group, header=False)