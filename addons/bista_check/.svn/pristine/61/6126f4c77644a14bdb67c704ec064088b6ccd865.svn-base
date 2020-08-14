import time
from openerp.report import report_sxw
from datetime import datetime, timedelta, date

class check_report_print(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(check_report_print, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
	    'check_report_details': self.check_report_details,
	    'current_date': self.current_date,
            'current_time': self.current_time,
            'current_user': self.current_user,
        })

    def check_report_details(self,check_report_id):
        invoice_checkobj = self.pool.get('invoice.checkno')
        for check_report_brw in self.pool.get('check.report').browse(self.cr,self.uid,[check_report_id.id]):
            start_date,end_date = check_report_brw.check_paid_start_date,check_report_brw.check_paid_end_date
        search_check = invoice_checkobj.search(self.cr,self.uid,[('id','>',0)])
        #print "QQQQQQQQQQQQQQQQQQQQQQQQQQQ",search_check
        search_check_new = search_check
        for each_check in invoice_checkobj.browse(self.cr,self.uid,search_check):
            start_date_new=datetime.strptime(start_date, "%Y-%m-%d")
            end_date_new=datetime.strptime(end_date, "%Y-%m-%d")
            check_date = each_check.paid_date
            check_date_new = datetime.strptime(check_date, "%Y-%m-%d")
            if check_date_new >= start_date_new and check_date_new <= end_date_new:
                print ""
            else:
                search_check_new.remove(each_check.id)
        check_browse = self.pool.get('invoice.checkno').browse(self.cr,self.uid,search_check_new)
        return check_browse

    def current_date(self,current_check):
        current_date=date.today()
        return current_date

    def current_time(self,current_check):
        current_time= datetime.now().strftime("%H:%M:%S")
        return current_time

    def current_user(self,current_check):
        for user_brw in self.pool.get('res.users').browse(self.cr,self.uid,[self.uid]):
            user_name = user_brw.name
        return user_name
    
report_sxw.report_sxw(
    'report.check.report.print',
    'check.report',
    'custom_addons/bista_check/report/check_print_report.rml',
    parser=check_report_print
)