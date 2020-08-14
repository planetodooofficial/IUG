import xlrd
import base64
from odoo.tools.translate import _
from odoo import models, fields,api
from odoo.tools import flatten
from odoo.addons import decimal_precision as dp
import logging
logger = logging.getLogger('IUG')
from odoo.exceptions import UserError

class invoice_import_excel(models.TransientModel):
    """ Import Account Invoice Excel sheet and pay Account invoices """
    _name = "invoice.import.excel"
    _description = "Import Order"

    excel_file=fields.Binary('Excel file', required=True , filters='*.xls,*.xlsx')
    state=fields.Selection([('init','init'),('done','done')], 'state', readonly=True,default='init')
    check_number=fields.Char('Check Number', size=16)
    amount=fields.Float('Amount', digits=dp.get_precision('Account'))
    date_checkprint=fields.Date('Date',default=fields.Date.context_today)
    journal_id=fields.Many2one('account.journal','Payment Method')
    company_id=fields.Many2one('res.company', 'Company', required=True,default=lambda self: self.env['res.company']._company_default_get('invoice.import.excel'))
    reference=fields.Char('Payment Ref', size=64)
    file_name = fields.Char('Attachment Name', size=64)

    @api.multi
    def pay_invoices(self,inv_ids, invoice_amount):
        ''' Function to create customer wise vouchers and pay them from xls '''
        cust_inv, payment_ids, check_count = {}, [], 0
        invoice_obj = self.env['account.invoice']
        account_payment = self.env['account.payment']
        curr_pool = self.env['res.currency']
        customer_grouped, customer_invoice_grouped = [], [] 
        for payment_obj in self:
            journal = payment_obj.journal_id
            company_id = payment_obj.company_id.id or False
            reference = payment_obj.reference
            self=self.with_context(company_id=company_id)
            for invoice in invoice_obj.browse(inv_ids):
                if invoice.partner_id.id not in customer_grouped:
                    customer_grouped.append(invoice.partner_id.id)
                    customer_invoice_grouped.append(invoice.id)
                if not cust_inv.get(invoice.partner_id.id):
                    cust_inv[invoice.partner_id.id] = [invoice.id]
                else:
                    cust_inv[invoice.partner_id.id].append(invoice.id)
            for cust, invoices in cust_inv.iteritems():
                if not invoices or not cust:
                    return
                amount, inv_ids,line_ids= 0.0, [],[]
                for vals in invoice_obj.browse(invoices):
                    amount += invoice_amount.get(vals.id) or 0.0
                    inv_ids.append([(4, vals.id, None)])
                    ref = vals.origin or ''
                    original_amount = vals.amount_total
                    balance_amount = vals.residual
                    allocation = vals.residual
                    # if vals.currency_id.id != self.currency_id.id:
                    #     currency_id = self.currency_id.with_context(date=self.payment_date)
                    #     original_amount = curr_pool._compute(vals.currency_id, currency_id, original_amount, round=True)
                    #     balance_amount = curr_pool._compute(vals.currency_id, currency_id, balance_amount, round=True)
                    #     allocation = curr_pool._compute(vals.currency_id, currency_id, allocation, round=True)
                    event_id = vals.event_id and vals.event_id.id or False
                    patient_id = vals.patient_id and vals.patient_id.id or False
                    invoice_old_number = vals.invoice_old_number or ''
                    line_ids.append((0, 0, {
                        'invoice_id': vals.id, 'account_id': vals.account_id.id,
                        'invoice_old_number': invoice_old_number,
                        'date': vals.date_invoice, 'due_date': vals.date_due, 'patient_id': patient_id,
                        'original_amount': original_amount, 'balance_amount': balance_amount, 'event_id': event_id,
                        'allocation': allocation, 'full_reconclle': True, 'reference': ref,
                    }))

                payment_vals={
                    'journal_id': payment_obj.journal_id.id,
                    'payment_method_id': payment_obj.journal_id.outbound_payment_method_ids[0].id or False,
                    'payment_date': payment_obj.date_checkprint,
                    'reference': payment_obj.reference,
                    'invoice_ids': inv_ids,
                    'payment_type': 'outbound',
                    'amount': amount,
                    'partner_id': cust,
                    'partner_type': 'customer',
                    'line_ids':line_ids
                }
                if payment_obj.check_number:
                    if check_count == 0:
                        payment_vals['check_number_string'] = payment_obj.check_number or ''
                    else:
                        payment_vals['check_number_string'] = str(payment_obj.check_number) + '_' + str(check_count) or ''
                account_payment_id = account_payment.create(payment_vals)
                payment_ids.append(account_payment_id.id)
                account_payment_id.post()
                check_count += 1
        return payment_ids

    @api.model
    def get_test_file_path(self):
        """Return the test file path"""
        proxy = self.env['ir.config_parameter']
        file_path = proxy.sudo().get_param('test_file_path')
        if not file_path:
            raise UserError(_('Please configure test_file_path as "/home/openerp/" in config parameters.'))
        if file_path.endswith('/'):
            file_path += 'test.xls'
        else:
            file_path += '/test.xls'
        return file_path
    
    def import_excel(self):
        '''Code to import excel and generate a Voucher ,confirm the Voucher , and Validate that.'''
        data = self
        if not data.excel_file:
            raise UserError(_('Please select a Excel file'))
        if data.file_name:
            if not data.file_name.lower().endswith(('.xls', '.xlsx')):
                raise UserError(_('Unsupported File Format.'))
        if not data.company_id:
            raise UserError(_('You must select Company First.'))
        file = base64.decodestring(data.excel_file)
        invoice_no, amount = 0, 1
        file_path = self.get_test_file_path()
        fp = open(file_path,'wb')
        fp.write(file)
        fp.close()
        book = xlrd.open_workbook(file_path)
        sh = book.sheet_by_index(0)
#        logger.info(' row count : %d',sh.nrows)
#        print "sh.nrows..........",sh.nrows
        inv_ids, total_amount, invoice_amount, inv_amount, invoice_num_list = [], 0.0, {}, {}, ['0']
        for line in range (1, sh.nrows):
            try:
                row = sh.row_values(line)
#                print "row............",row
                if row != '':
                    if not row[invoice_no]:
                        continue
                    amt = row[amount] or 0.0
                    if amt < 0.0:
                        continue
                    total_amount += float(amt)
                    inv_no = str(row[invoice_no]).strip().split('.')[0]
                    if row[invoice_no] in inv_amount:
                        inv_amount[inv_no] += amt or 0.0
                    else:
                        inv_amount[inv_no] = amt or 0.0
                        invoice_num_list.append(inv_no)
            except Exception , e:
                logger.info(' Exception : %s',e.args)
        if round(total_amount,6) != round(data.amount,6):
            raise UserError(_('Total Invoice amount and paid amount is mismatching!'))
        if invoice_num_list:
            self._cr.execute("select id, number from account_invoice where state = 'open' and company_id = %d and  number in %s"%(data.company_id.id, tuple(invoice_num_list)))
            result = self._cr.fetchall()
            if result:
                for rs in result:
                    if len(rs) == 2:
                        inv_ids.append(rs[0])
                        if rs[0] in invoice_amount:
                            invoice_amount[rs[0]] += inv_amount[str(rs[1])] or 0.0
                        else:
                            invoice_amount[rs[0]] = inv_amount[str(rs[1])] or 0.0

#        print "inv_ids.............",len(inv_ids)
#        inv_ids = list(set(flatten(inv_ids)))
        payment_ids = self.pay_invoices(list(set(flatten(inv_ids))), invoice_amount)
        view_ref = self.env['ir.model.data'].sudo().get_object_reference('account', 'view_account_payment_tree')
        view_id = view_ref[1] if view_ref else False

        return {
            'name': _("Customer Payments"),
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'domain': "[('id','in',["+','.join(map(str, payment_ids))+"])]",
        }



