
import os
import tools
import xlrd
import time
import datetime
import base64
import netsvc
from tools.translate import _
from osv import osv, fields
from openerp.tools import flatten
import openerp.addons.decimal_precision as dp

class create_voucher(osv.osv_memory):
    """ Create voucher for selected invoices """
    _name = "create.voucher"
    _description = "Create Voucher"
    _columns={
        'amount': fields.float('Amount', digits_compute=dp.get_precision('Account')),
        'date_checkprint':fields.date('Date'),
        'journal_id':fields.many2one('account.journal','Payment Method'),
        'company_id': fields.many2one('res.company', 'Company', required=True),
    }
    
    _defaults = {
        'date_checkprint': fields.date.context_today,
        'company_id': lambda self, cr, uid, ctx: self.pool.get('res.company')._company_default_get(cr, uid, 'create.voucher', context=ctx),
    }
    
    def create_invoice_voucher(self, cr, uid, ids, context=None):
        ''' Function to create vouchers for selected customer Invoices '''
        if context is None: context = {}
        cust_inv, voucher_ids, check_count = {}, [], 0
#        wf_service = netsvc.LocalService("workflow")
        invoice_obj = self.pool.get('account.invoice')
        account_voucher = self.pool.get('account.voucher')
        move_obj = self.pool.get('account.move.line')
        customer_grouped, customer_invoice_grouped = [], [] 
        for payment_obj in self.browse(cr, uid, ids):
            journal = payment_obj.journal_id
            company_id = payment_obj.company_id.id or false
            context.update({'company_id': company_id})
            for invoice in invoice_obj.browse(cr, uid, context.get('active_ids',[])):
                partner_id = self.pool.get('res.partner')._find_accounting_partner(invoice.partner_id).id
                if invoice.partner_id.id not in customer_grouped:
                    customer_grouped.append(invoice.partner_id.id)
                    customer_invoice_grouped.append(invoice.id)
                if not cust_inv.get(invoice.partner_id.id):
                    partner_list = []
                    partner_list.append(invoice.id)
                    cust_inv[invoice.partner_id.id] = partner_list
                else:
                    cust_inv[invoice.partner_id.id].append(invoice.id)
            voucher_values = {
                'close_after_process': True,
                'invoice_type': 'in_invoice',
                'type': 'payment',
            }
            
            for cust, invoices in cust_inv.iteritems():
                move_lines = []
                part = self.pool.get('res.partner').browse(cr, uid, cust)
                if invoices:
                    invoice_browse = invoice_obj.browse(cr, uid, invoices[0])
                    voucher_values = {
                        'payment_expected_currency': invoice_browse.currency_id.id,
                        'default_reference': invoice_browse.name,
                        'invoice_id': invoice_browse.id,
                }
                amount, voucher_values, move_lines, context['move_line_ids'] = 0.0, {}, [], []
                for inv in invoice_obj.browse(cr, uid, invoices):
                    voucher_wizard_values = invoice_obj.invoice_pay_customer(cr, uid, [inv.id], context)
#                    print "voucher_wizard_values.......",voucher_wizard_values
                    if voucher_wizard_values and voucher_wizard_values.get('context'):
                        voucher_values = voucher_wizard_values.get('context')
                        amount += inv.residual or 0.0
                    if inv.move_id:
                        for line in inv.move_id.line_id:
                            move_lines.append(line.id)
                if round(amount,6) != round(payment_obj.amount,6):
                    raise osv.except_osv(_('Mismatch Amount!!'), _('The amount pending for selected invoices and entered amount is mismatching!'))
                context['move_line_ids'] = move_lines
                if voucher_values.get('type') and voucher_values.get('default_amount'):
                    onchange_voucher_values = account_voucher.onchange_journal(cr, uid, [], journal.id, [], [], cust, payment_obj.date_checkprint, amount, voucher_values.get('type'),company_id, context=context)
                    if onchange_voucher_values and onchange_voucher_values.get('value'):
                        new_voucher_values = onchange_voucher_values.get('value')
                        if new_voucher_values and new_voucher_values.get('account_id'):
                            dr_lines, cr_lines= [], []
#                            if new_voucher_values.get('line_dr_ids'):
#                                line_dr_ids = new_voucher_values.get('line_dr_ids')
#                                for line_dr_id in line_dr_ids:
#    #                                        print "line_dr_id........",line_dr_id
#                                    if line_dr_id.get('move_line_id', False) and line_dr_id.get('move_line_id') in move_lines:
##                                        line_dr_id['reconcile'] = True
#                                        line_dr_id['amount'] = line_dr_id.get('amount_unreconciled',0.0)
#                                        dr_lines.append([0, False, line_dr_id])
#        For using getting move lines of Selected invoices only 
#                            if inv.move_id:
#                                for move_line in inv.move_id.line_id:
#                            print "move_lines............",move_lines
#                            context['move_line_ids'] = move_lines
                            if new_voucher_values.get('line_cr_ids'):
                                line_cr_ids = new_voucher_values.get('line_cr_ids')
                                for line_cr_id in line_cr_ids:
                                    if line_cr_id.get('move_line_id'):
                                        move_line = move_obj.browse(cr, uid, line_cr_id.get('move_line_id'))
                                        if move_line.invoice:
    #                                        print "invoice......",move_line.invoice
                                            
                                            line_cr_id['amount'] = line_cr_id.get('amount_unreconciled', 0.0)
                                            
#                                    print "line_cr_id['amount']........",line_cr_id['amount']
                                    cr_lines.append([0, False, line_cr_id])
                            partner_id = self.pool.get('res.partner')._find_accounting_partner(part).id
                            account_data = invoice_obj.get_accounts(cr, uid, partner_id, journal.id)
#                                date_today = fields.date.context_today(self, cr, uid, context=context)
                            period_ids = self.pool.get('account.period').find(cr, uid, payment_obj.date_checkprint, context=context)
                            period_id = period_ids and period_ids[0] or False
                            vals = {
                                'company_id': company_id,
                                'journal_id': journal.id,
                                'reference': '',
                                'partner_id': partner_id,
                                'amount': payment_obj.amount or 0.0,
                                'type': voucher_values.get('type'),
                                'account_id': account_data['value']['account_id'],
                                'date': payment_obj.date_checkprint,
                                'line_cr_ids': cr_lines,
                                'line_dr_ids': dr_lines,
                                'payment_rate': new_voucher_values.get('payment_rate'),
                                'pre_line': new_voucher_values.get('pre_line'),'currency_id':new_voucher_values.get('currency_id'),
                                'currency_help_label': new_voucher_values.get('currency_help_label'),
                                'paid_amount_in_company_currency': new_voucher_values.get('paid_amount_in_company_currency'),
#                                'is_check':True,
                                'period_id': period_id,
                            }
#                            if payment_obj.check_number:
#                                if check_count == 0:
#                                    vals['check_number'] = payment_obj.check_number or ''
#                                else:
#                                    vals['check_number'] = str(payment_obj.check_number) + '_' + str(check_count) or ''
                            account_voucher_id = account_voucher.create(cr, uid, vals)
                            voucher_ids.append(account_voucher_id)
#                            account_voucher.button_proforma_voucher(cr, uid, [account_voucher_id], context)
#                            wf_service.trg_validate(uid, 'account.invoice', invoice_brw.id, 'confirm_paid', cr)
#                check_count += 1
            voucher_ids = list(set(flatten(voucher_ids)))
            print "voucher_ids print......",len(voucher_ids)
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account_voucher', 'view_vendor_receipt_form')
        res_id = res and res[1] or False,
        return {
#            'domain': str([('id','in',voucher_ids)]),
            'name': 'Customer Payment',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.voucher',
            'view_id': [res_id[0]],
            'target': 'current',
            'type': 'ir.actions.act_window',
            'res_id': voucher_ids and voucher_ids[0] or False,
        }
    
    def default_get(self, cr, uid, fields, context=None):
        res = {}
        if context is None: context = {}
        res = super(create_voucher , self).default_get(cr, uid, fields, context=context)
        if not context.get('active_ids', []):
            return res
        partner_list, amount = [], 0.0
        invoice_obj = self.pool.get('account.invoice')
        for invoice_brw in invoice_obj.browse(cr, uid, context.get('active_ids',[])):
            partner_list.append(invoice_brw.partner_id.id)
            if invoice_brw.type == 'in_invoice':
                raise osv.except_osv(_('Payment Warning!!'), _('You can only generate Payment for the Customer Invoices!'))
            if invoice_brw.state != 'open':
                raise osv.except_osv(_('Payment Warning!!'), _('You can only generate Payment for open invoices only!'))
            amount += invoice_brw.residual or 0.0
        if 'amount' in fields:
            res.update(amount = amount)
        partner_list = list(set(flatten(partner_list)))
        if len(partner_list) > 1:
            raise osv.except_osv(_('Payment Warning!!'), _('You can only generate Payment for one Customer at one time!'))
        return res
    
create_voucher()

