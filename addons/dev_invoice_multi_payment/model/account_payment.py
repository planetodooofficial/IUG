# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://devintellecs.com>).
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger('sale')
    
class account_payment(models.Model):
    _name='account.payment'
    _inherit = ['account.payment','mail.thread']
    
    line_ids = fields.One2many('advance.payment.line','account_payment_id')
    check_number = fields.Integer(string="Check Number", readonly=False, copy=False,
        help="The selected journal is configured to print check numbers. If your pre-printed check paper already has numbers "
             "or if the current numbering is wrong, you can change it in the journal configuration page.")
    
    def _get_counterpart_move_line_vals(self, invoice=False):
        res = super(account_payment,self)._get_counterpart_move_line_vals(invoice)
        if self.payment_type == 'outbound' and self.partner_type == 'supplier':
            if invoice:
                name = ''
                for inv in invoice:
                    if inv.reference:
                        if name :
                            name = name + ','+inv.reference
                        else:
                            name = inv.reference
                res.update({
                    'name':name,
                })
        return res


    
    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        acc_invoice = []
        account_inv_obj = self.env['account.invoice']
        invoice_ids=[]
        self.amount=0.0
        if self.partner_type == 'customer':
            invoice_ids = account_inv_obj.search([('partner_id', 'in', [self.partner_id.id]),('state', '=','open'),('type','in',['out_invoice','out_refund'])],order='date_invoice asc')
        else:
            invoice_ids = account_inv_obj.search([('partner_id', 'in', [self.partner_id.id]),('state', '=','open'),('type','in',['in_invoice','in_refund'])],order='date_invoice asc')
        curr_pool=self.env['res.currency']
        for vals in invoice_ids:
            ref = vals.origin or ''
            original_amount = vals.amount_total
            balance_amount = vals.residual
            allocation = vals.residual
            if vals.currency_id.id != self.currency_id.id:
                currency_id = self.currency_id.with_context(date=self.payment_date)
                original_amount = curr_pool._compute(vals.currency_id, currency_id, original_amount, round=True)
                balance_amount = curr_pool._compute(vals.currency_id, currency_id, balance_amount, round=True)
                allocation = curr_pool._compute(vals.currency_id, currency_id, allocation, round=True)
            event_id=vals.event_id and vals.event_id.id or False
            patient_id=vals.patient_id and vals.patient_id.id or False
            invoice_old_number=vals.invoice_old_number or ''
            acc_invoice.append({'invoice_id':vals.id,'account_id':vals.account_id.id,'invoice_old_number':invoice_old_number,
            'date':vals.date_invoice,'due_date':vals.date_due,'patient_id':patient_id,
            'original_amount':original_amount,'balance_amount':balance_amount,'event_id':event_id,
            'allocation':0.0,'full_reconclle':False,'reference':ref,'currency_id':self.currency_id.id})
        self.line_ids = acc_invoice
        
    
    @api.onchange('currency_id')
    def onchange_currency(self):
        curr_pool=self.env['res.currency']
        if self.currency_id and self.line_ids:
            for line in self.line_ids:
                if line.currency_id.id != self.currency_id.id:
                    currency_id = self.currency_id.with_context(date=self.payment_date)
                    line.original_amount = curr_pool._compute(line.currency_id, currency_id, line.original_amount, round=True)
                    line.balance_amount = curr_pool._compute(line.currency_id, currency_id, line.balance_amount, round=True)
                    line.allocation = curr_pool._compute(line.currency_id, currency_id, line.allocation, round=True)
                    line.currency_id = self.currency_id and self.currency_id.id or False

    @api.onchange('amount')
    def onchange_amount(self):
        amount=self.amount
        if amount:
            allocated=False
            for line in self.line_ids:
                if line.allocation !=0.0:
                    allocated=True
            if not allocated:
               for line in self.line_ids:
                  line.allocation=0.0
                  line.full_reconclle=False
               full_allocation=False
               for line in self.line_ids:
                   if line.balance_amount == amount:
                        line.allocation=amount
                        full_allocation =True
                        break
               if not full_allocation:
                     for line in self.line_ids:
                        if amount == 0:
            	            break
                        allocated_amount=min(abs(amount), line.balance_amount)
                        line.allocation = allocated_amount
                        amount -= allocated_amount
        else:
            for line in self.line_ids:
                line.allocation=amount
                line.full_reconclle=False
    
    @api.depends('line_ids.allocation')
    def _compute_total_lines_amount(self):
        total=0.0
        for line in self.line_ids:
            if line.allocation > 0.01:
                total+=line.balance_amount
        return total
	
    @api.multi
    def uncheck_line_ids(self):
       for line in self.line_ids:
          line.allocation=0.0
          line.full_reconclle=False


    @api.one
    @api.depends('invoice_ids', 'amount', 'payment_date', 'currency_id','line_ids','line_ids.allocation')
    def _compute_payment_difference(self):
       
        if len(self.invoice_ids) == 0 and len(self.line_ids) == 0:
            return
        if self.line_ids and self.line_ids[0].invoice_id.type in ['in_invoice', 'out_refund']:
            self.payment_difference = self._compute_total_lines_amount() - self.amount
        elif self.line_ids and self.line_ids[0].invoice_id.type not in ['in_invoice', 'out_refund']:
            self.payment_difference = self.amount - self._compute_total_lines_amount()
        elif self.invoice_ids and self.invoice_ids[0].type in ['in_invoice', 'out_refund']:
            self.payment_difference = self.amount - self._compute_total_invoices_amount()
        else:
            self.payment_difference = self._compute_total_invoices_amount() - self.amount
        
    # @api.model
    # def create(self,vals):
    #     if vals.get('line_ids'):
    #         inv_ids = []
    #         for line in vals.get('line_ids'):
    #             inv_ids.append(line[2].get('invoice_id'))
    #
    #         vals.update({
    #         'invoice_ids':[(6,0,inv_ids)]
    #         })
    #     payment_ids=super(account_payment,self).create(vals)
    #     return payment_ids
    #
    # @api.multi
    # def write(self, vals):
    #     for rec in self:
    #         if vals.get('line_ids'):
    #             inv_ids = []
    #             for line in vals.get('line_ids'):
    #                 if line[2]:
    #                     inv_ids.append(line[2].get('invoice_id'))
    #             if inv_ids:
    #                 vals.update({
    #                     'invoice_ids': [(4, 0, inv_ids)]
    #                 })
    #     payment_ids = super(account_payment, self).write(vals)
    #     return payment_ids


    
    @api.multi
    def post(self):     
        for rec in self:
          if rec.line_ids:
            amt=0.0
            for line in rec.line_ids:
                amt += line.allocation
            
            #amount=self.amount
            #if not float(amount) >= float(amt):
            #    _logger.error('--------in init------%s-------%s',amt,self.amount)
            #    raise ValidationError(("Amount must be greater or equal '%s'") %(amt))
            #if self.amount > amt:
            #    for line in self.line_ids:
            #        line.allocation = line.allocation + (self.amount - amt)
            #        break
        return  super(account_payment,self).post()
    
    @api.multi
    def _create_payment_entry(self, amount):
        """ Create a journal entry corresponding to a payment, if the payment
            references invoice(s) they are reconciled.
            Return the journal entry.
        """
        # If group data
        _logger.info('---------------amount---------------%s',amount)
        if self.invoice_ids and self.line_ids:
            aml_obj = self.env['account.move.line'].\
                with_context(check_move_validity=False)
            invoice_currency = False
            if self.invoice_ids and\
                    all([x.currency_id == self.invoice_ids[0].currency_id
                         for x in self.invoice_ids]):
                # If all the invoices selected share the same currency,
                # record the paiement in that currency too
                invoice_currency = self.invoice_ids[0].currency_id
            self._cr.commit()
            move = self.env['account.move'].create(self._get_move_vals())
            p_id = str(self.partner_id.id)
            pd=self.payment_difference
            total_allocation=0.0
            for line in self.line_ids:
               total_allocation+=line.allocation
            for inv in self.invoice_ids:
                amt = 0
                if self.partner_type == 'customer':
                    for line in self.line_ids:
                        if line.invoice_id.id == inv.id:
                            if inv.type == 'out_invoice':
                                amt = -(line.allocation)
                            else:
                                amt = line.allocation
                else:
                    for line in self.line_ids:
                        if line.invoice_id.id == inv.id:
                            if inv.type == 'in_invoice':
                                amt = line.allocation
                            else:
                                amt = -(line.allocation)
                _logger.info('-----------1st amt%s',amt)
                if abs(amt) > 0.01:
                    _logger.info('--------------amt-------------%s',amt)
                    debit, credit, amount_currency, currency_id =\
                        aml_obj.with_context(date=self.payment_date).\
                        compute_amount_fields(amt, self.currency_id,
                                              self.company_id.currency_id,
                                              invoice_currency)
                    # Write line corresponding to invoice payment
                    counterpart_aml_dict =\
                        self._get_shared_move_line_vals(debit,
                                                        credit, amount_currency,
                                                        move.id, False)
                    if self.payment_difference_handling == 'open' and pd:
                         if pd > 0.0:
                           if amt > 0.0:
                               counterpart_aml_dict['debit']=counterpart_aml_dict['debit']+pd

                           else:
                               counterpart_aml_dict['credit']=counterpart_aml_dict['credit']+pd
                    counterpart_aml_dict.update(
                        self._get_counterpart_move_line_vals(inv))
                    counterpart_aml_dict.update({'currency_id': currency_id})
                    counterpart_aml = aml_obj.create(counterpart_aml_dict)
                    _logger.info('------------------------aml--------------%s',counterpart_aml)
                    # Reconcile with the invoices and write off
                    if self.partner_type == 'customer':
                        handling = 'open'  # noqa
                        for line in self.line_ids:
                            if line.invoice_id.id == inv.id:
                                payment_difference = line.balance_amount - line.allocation  # noqa
                        # writeoff_account_id = self.journal_id and self.journal_id.id or False  # noqa
                        if self.payment_difference_handling == 'reconcile' and self.payment_difference:
                            writeoff_line =\
                                self._get_shared_move_line_vals(0, 0, 0, move.id,
                                                                False)
                            debit_wo, credit_wo, amount_currency_wo, currency_id =\
                                aml_obj.with_context(date=self.payment_date).\
                                compute_amount_fields(
                                    payment_difference,
                                    self.currency_id,
                                    self.company_id.currency_id,
                                    invoice_currency)
                            writeoff_line['name'] = _('Counterpart')
                            writeoff_line['account_id'] = self.writeoff_account_id.id
                            writeoff_line['debit'] = debit_wo
                            writeoff_line['credit'] = credit_wo
                            writeoff_line['amount_currency'] = amount_currency_wo
                            writeoff_line['currency_id'] = currency_id
                            writeoff_line = aml_obj.create(writeoff_line)
                            if counterpart_aml['debit']:
                                counterpart_aml['debit'] += credit_wo - debit_wo
                            if counterpart_aml['credit']:
                                counterpart_aml['credit'] += debit_wo - credit_wo
                            counterpart_aml['amount_currency'] -=\
                                amount_currency_wo
                    inv.register_payment(counterpart_aml)
                    # Write counterpart lines
                    if not self.currency_id != self.company_id.currency_id:
                        amount_currency = 0
                    liquidity_aml_dict =\
                        self._get_shared_move_line_vals(credit, debit,
                                                        -amount_currency, move.id,
                                                        False)
                    if self.payment_difference_handling == 'open' and pd:
                         if pd > 0.0:
                           if amt > 0.0:
                               liquidity_aml_dict['credit']=liquidity_aml_dict['credit']+pd
                               pd=0.0
                           else:
                               liquidity_aml_dict['debit']=liquidity_aml_dict['debit']+pd
                               pd=0.0
                    liquidity_aml_dict.update(
                        self._get_liquidity_move_line_vals(-amount))
                    aml_obj.create(liquidity_aml_dict)
            move.post()
            return move

        return super(account_payment, self)._create_payment_entry(amount)
    
class account_abstract_payment(models.AbstractModel):
    _inherit = 'account.abstract.payment'    

    @api.onchange('journal_id')
    def _onchange_journal(self):
        if self.journal_id:
            self.currency_id = self.journal_id.currency_id or self.company_id.currency_id
            # Set default payment method (we consider the first to be the default one)
            payment_methods = self.payment_type == 'inbound' and self.journal_id.inbound_payment_method_ids or self.journal_id.outbound_payment_method_ids
            self.payment_method_id = payment_methods and payment_methods[0] or False
            # Set payment method domain (restrict to methods enabled for the journal and to selected payment type)
            payment_type = self.payment_type in ('outbound', 'transfer') and 'outbound' or 'inbound'
            if self.payment_type=='outbound' and self.journal_id.outbound_payment_method_ids:
                for rec in self.journal_id.outbound_payment_method_ids:
                     if rec.code=='check_printing':
                        self.payment_method_id=rec
            return {'domain': {'payment_method_id': [('payment_type', '=', payment_type), ('id', 'in', payment_methods.ids)]}}
        return {}


class AccountRegisterPayments(models.TransientModel):
    _inherit = "account.register.payments"

    check_number_string=fields.Char('Check Number')

    def get_payment_vals(self):
        res = super(AccountRegisterPayments, self).get_payment_vals()
        line_ids=[]
        curr_pool=self.env['res.currency']
        for vals in self._get_invoices():
           ref = vals.origin or ''
           original_amount = vals.amount_total
           balance_amount = vals.residual
           allocation = vals.residual
           if vals.currency_id.id != self.currency_id.id:
                currency_id = self.currency_id.with_context(date=self.payment_date)
                original_amount = curr_pool._compute(vals.currency_id, currency_id, original_amount, round=True)
                balance_amount = curr_pool._compute(vals.currency_id, currency_id, balance_amount, round=True)
                allocation = curr_pool._compute(vals.currency_id, currency_id, allocation, round=True)
           event_id=vals.event_id and vals.event_id.id or False
           patient_id=vals.patient_id and vals.patient_id.id or False
           invoice_old_number=vals.invoice_old_number or ''
           line_ids.append((0,0, {
             'invoice_id':vals.id,'account_id':vals.account_id.id,'invoice_old_number':invoice_old_number,
            'date':vals.date_invoice,'due_date':vals.date_due,'patient_id':patient_id,
            'original_amount':original_amount,'balance_amount':balance_amount,'event_id':event_id,
            'allocation':allocation,'full_reconclle':True,'reference':ref,'currency_id':self.currency_id.id
                                 }))
        res.update({'line_ids':line_ids})
        if self.check_number_string:
           res.update({'check_number_string':self.check_number_string})
        return res

