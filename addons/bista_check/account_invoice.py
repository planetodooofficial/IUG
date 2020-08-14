from openerp.osv import fields,osv
from openerp.osv import osv
from dateutil.relativedelta import relativedelta
from datetime import datetime,timedelta
import openerp.addons.decimal_precision as dp
import time
from openerp.tools.translate import _

class invoice_checkno(osv.osv):
    _name = "invoice.checkno"
    _columns = {

    'amt_paid':fields.float('Amount Paid'),
    'paid_date':fields.date('Paid Date'),
    'check_no': fields.integer('Check No.',size=124),
    'invoice_id': fields.many2one('account.invoice','Supplier Invoice'),
    'voucher_id': fields.many2one('account.voucher','Journal Item'),
    }

    ###----TODO---TO Reprint the check----###
    def reprint_check(self, cr, uid, ids, context=None):
        check_nos = []
        for payment_check in self.browse(cr,uid,ids):
            check_nos.append(payment_check.check_no)
            context.update({'invoice_id':payment_check.invoice_id.id,'check_no':check_nos})

            return {'type': 'ir.actions.report.xml',
                    'report_name':'account.check.print',
                    'context':context,
                    'datas': {
                        'model':'account.invoice',
                        'ids': [payment_check.invoice_id.id],
                        'report_type': 'pdf'
                            },
                    'nodestroy': True
                }


invoice_checkno()

class account_invoice(osv.osv):
    _inherit = "account.invoice"

    _columns = {
                'invoice_checkno_ids':fields.one2many('invoice.checkno', 'invoice_id','Invoices and Checks'),
                }

account_invoice()

