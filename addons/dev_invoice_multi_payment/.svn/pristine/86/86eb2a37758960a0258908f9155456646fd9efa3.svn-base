# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://devintellecs.com>).
#
##############################################################################

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

    
class advance_payment_line(models.Model):
    _name = 'advance.payment.line'
    
    
    invoice_id = fields.Many2one('account.invoice',string='Invoice')
    invoice_old_number=fields.Char(related="invoice_id.invoice_old_number",string="Old Invoice Number")
    reference = fields.Char(related="invoice_id.origin",string='Reference')
    account_id = fields.Many2one('account.account', string="Account")
    date = fields.Date(related="invoice_id.event_start_date",string="Date of Service")
    due_date = fields.Date(string="Due Date")
    original_amount = fields.Float(string="Original Amount")
    balance_amount = fields.Float(string="Balance Amount")
    full_reconclle = fields.Boolean(string="Full Reconcile")
    allocation = fields.Float(string="Allocation")
    patient_id=fields.Many2one('patient',related="invoice_id.patient_id")
    account_payment_id = fields.Many2one('account.payment')
    diff_amt = fields.Float('Remaining Amount',compute='get_diff_amount',)
    currency_id = fields.Many2one('res.currency',string='Currency')
    event_id=fields.Many2one('event',related="invoice_id.event_id",string='Event')
    
    @api.multi
    @api.depends('balance_amount','allocation')
    def get_diff_amount(self):
        for line in self: 
            line.diff_amt = line.balance_amount - line.allocation
    
    @api.onchange('full_reconclle')
    def onchange_full_reconclle(self):
        if self.full_reconclle:
            self.allocation = self.balance_amount
            
    @api.onchange('allocation')
    def onchange_allocation(self):
        if self.allocation:
            if self.allocation >= self.balance_amount:
                self.full_reconclle = True
            else:
                self.full_reconclle = False
            
            
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.invoice_id and rec.account_payment_id:
                rec.account_payment_id.write({'invoice_ids':[(3,rec.invoice_id.id)]})
        return super(advance_payment_line, self).unlink()

    @api.model
    def create(self,vals):
        if vals.get('invoice_id',False) and vals.get('account_payment_id',False):
                self.env['account.payment'].browse(vals.get('account_payment_id')).write({'invoice_ids': [(4,vals.get('invoice_id'))]})
        return super(advance_payment_line, self).create(vals)
    
             
