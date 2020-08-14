from odoo import models, fields, api,_
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, RedirectWarning, ValidationError

class invoice_payment_wizard(models.TransientModel):
    """ A wizard to do payment of invoice """
    _name = 'invoice.payment.wizard'

    @api.multi
    def pay_invoice(self):
        ''' Function to pay invoice '''
        cur_obj = self
        if cur_obj.billing_form_id:
            if not (cur_obj.amount > 0):
                raise UserError(_('Please enter a valid amount to pay!'))
            if cur_obj.invoice_type:
                if cur_obj.invoice_type == 'customer':
                    if cur_obj.check_no:
                        self=self.with_context(check_number=cur_obj.check_no)
                    cur_obj.billing_form_id.pay_customer_invoice(cur_obj.journal_id.id, cur_obj.amount)
                elif cur_obj.invoice_type == 'supplier':
                    cur_obj.billing_form_id.pay_supplier_invoice(cur_obj.journal_id.id, cur_obj.amount)
                elif cur_obj.invoice_type == 'transporter':
                    print "in transporter++++++++++"
                    cur_obj.billing_form_id.pay_transporter_invoice(cur_obj.journal_id.id, cur_obj.amount)
        return True

    @api.model
    def default_get(self,fields):
        res = {}
        res = super(invoice_payment_wizard , self).default_get(fields)
        invoice_type = self._context.get('invoice_type', False)
        if 'invoice_type' in fields:
            res.update(invoice_type = invoice_type)
        return res

#    def _make_journal_search(self, cr, uid, ttype, context=None):
#        journal_pool = self.pool.get('account.journal')
#        return journal_pool.search(cr, uid, [('type', '=', ttype)], limit=1)
#
#    def _get_journal(self, cr, uid, context=None):
#        if context is None: context = {}
#        invoice_pool = self.pool.get('account.invoice')
#        journal_pool = self.pool.get('account.journal')
#        if context.get('invoice_id', False):
#            print "invoice......",context.get('invoice_id', False)
#            currency_id = invoice_pool.browse(cr, uid, context['invoice_id'], context=context).currency_id.id
#            journal_id = journal_pool.search(cr, uid, [('currency', '=', currency_id),('type','in',('cash','bank'))], limit=1)
#            print "journal_id..........",journal_id
#            return journal_id and journal_id[0] or False
#        if context.get('journal_id', False):
#            return context.get('journal_id')
#        if not context.get('journal_id', False) and context.get('search_default_journal_id', False):
#            return context.get('search_default_journal_id')
#
#        ttype = context.get('type', 'bank')
#        if ttype in ('payment', 'receipt'):
#            ttype = 'bank'
#        res = self._make_journal_search(cr, uid, ttype, context=context)
#        return res and res[0] or False


    company_id=fields.Many2one('res.company', 'Company')
    journal_id=fields.Many2one('account.journal', 'Journal')
    event_id=fields.Many2one('event', 'Event')
    billing_form_id=fields.Many2one('billing.form','Billing Form')
    invoice_id=fields.Many2one('account.invoice', 'Invoice')
    amount=fields.Float('Amount', digits=dp.get_precision('Account'))
    invoice_type=fields.Selection([('customer','Customer'),('supplier','Supplier'),('transporter','Transporter')], 'Invoice Type')
    check_no=fields.Char('Check No', size=32)

#    _defaults={
#        'journal_id':_get_journal,
#
#    }


