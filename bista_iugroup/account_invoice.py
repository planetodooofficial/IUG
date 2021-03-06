# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import odoo.netsvc
import time
import datetime
from odoo import models, fields, api,_
from odoo.addons import decimal_precision as dp
from dateutil import relativedelta
from odoo import SUPERUSER_ID
import pytz
from odoo.exceptions import UserError, RedirectWarning, ValidationError
import logging
_logger = logging.getLogger(__name__)

EVENT_TYPES = [
    ('language','Language'),
    ('transport','Transport'),
    ('translation','Translation'),
    ('lang_trans','Lang And Transport')
]

class account_invoice_line(models.Model):
    ''' Fields added for the IUX system Fields '''
    _inherit = "account.invoice.line"

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
                 'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
                 'invoice_id.date_invoice','travelling_rate','travel_time','mileage_rate','mileage','pickup_fee')
    def _compute_price(self):
        if self.total_editable:
            self.price_subtotal = price_subtotal_signed= self.total_editable
            if self.invoice_id.currency_id and self.invoice_id.company_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
                price_subtotal_signed = self.invoice_id.currency_id.with_context(
                    date=self.invoice_id.date_invoice).compute(
                    price_subtotal_signed, self.invoice_id.company_id.currency_id)
            sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
            self.price_subtotal_signed = price_subtotal_signed * sign
        else:
            currency = self.invoice_id and self.invoice_id.currency_id or None
            price = self.price_unit 
            taxes = False
            if self.invoice_line_tax_ids:
                taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id,
                                                              partner=self.invoice_id.partner_id)
            self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
            if self.invoice_id.currency_id and self.invoice_id.company_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
                price_subtotal_signed = self.invoice_id.currency_id.with_context(date=self.invoice_id.date_invoice).compute(
                    price_subtotal_signed, self.invoice_id.company_id.currency_id)
            sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
            self.price_subtotal_signed = price_subtotal_signed * sign
            tax_obj = self.env['account.tax']
            cur_obj = self.env['res.currency']
            total1, total2, qty = 0.0, 0.0, 0.0
            new_min, hrs = 0.0, 0.0
            travel_calc = 0.0
            qty = self.quantity
            if self.invoice_id and self.invoice_id.event_id and self.invoice_id.event_id.event_purpose == 'conf_call':
                rate = False
                for rate_id in self.invoice_id.partner_id and self.invoice_id.partner_id.rate_ids:
                    if rate_id.rate_type == 'conf_call':
                        rate = rate_id
            if self.travel_time and self.travelling_rate:
                travel_calc = self.travel_time * self.travelling_rate * (1 - (self.discount or 0.0) / 100.0)

            price2 = self.mileage_rate
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id,
                                                              partner=self.invoice_id.partner_id)

            total1 = taxes['total_excluded'] * (1 - (self.discount or 0.0) / 100.0)
            taxes = self.invoice_line_tax_ids.compute_all(price2, currency, self.mileage, product=self.product_id,
                                                              partner=self.invoice_id.partner_id)

            total2 = taxes['total_excluded']

            sum = self.after_hours + self.wait_time - self.gratuity
            final_sum = sum * (1 - (self.discount or 0.0) / 100.0)

            taxes = self.invoice_line_tax_ids.compute_all(final_sum, currency, 1.0, product=self.product_id,
                                                              partner=self.invoice_id.partner_id)

            total3 = taxes['total_excluded']

            pickup_fee = self.pickup_fee
            pickup_fee_tot = pickup_fee * (1 - (self.discount or 0.0) / 100.0)
            taxes = self.invoice_line_tax_ids.compute_all(pickup_fee_tot, currency, 1.0, product=self.product_id,
                                                              partner=self.invoice_id.partner_id)
            total4 = taxes['total_excluded']
            self.price_subtotal = price_subtotal_signed = total1 + total2 + total3 + total4 + travel_calc
            if self.invoice_id.currency_id and self.invoice_id.company_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
                price_subtotal_signed = self.invoice_id.currency_id.with_context(
                    date=self.invoice_id.date_invoice).compute(
                    price_subtotal_signed, self.invoice_id.company_id.currency_id)
            sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
            self.price_subtotal_signed = price_subtotal_signed * sign

    # @api.depends('event_type')
    # def _get_evnt_type(self):
    #     for line in self:
    #         if line.event_type:
    #             if line.event_type == 'translation':
    #                 line.is_language = True
    #                 line.is_hr_miles = False
    #             else:
    #                 line.is_language = False
    #                 line.is_hr_miles=True

    travel_time=fields.Float(store=True, string="Travel Time")
    travelling_rate=fields.Float('Travelling Rate')
    miles_driven=fields.Float('Miles Driven')
    mileage=fields.Float('Mileage')
    mileage_rate=fields.Float('Mileage Rate',digits=(12,3))
    miscellaneous_bill=fields.Float("Miscellaneous Bill")
    wait_time=fields.Float("Wait Time")
    pickup_fee=fields.Float("Pickup Fee")
    gratuity=fields.Float("Deduction")
    after_hours=fields.Float("After Hours")
    event_out_come_id=fields.Many2one('event.out.come', 'Event Outcome')
    task_line_id=fields.Many2one('project.task.work', 'Task Line Id')
    inc_min=fields.Selection([('15min','15 Min'),('30min','30 Min'),('1min','1 Min'),('no_inc','NO Increment')],'Inc Min')
    total_editable=fields.Float("Final total")
    price_subtotal = fields.Monetary(string='Amount',store=True, readonly=True, compute='_compute_price',digits= dp.get_precision('Account'))
    # event_type = fields.Selection(related='invoice_id.event_type', store=True, string="Event Type", readonly=True,
    #                               selection=EVENT_TYPES)
    # word_count=fields.Float("words Count")
    # is_language=fields.Boolean(compute='_get_evnt_type', string='Is Lanuage', store=True)
    # is_hr_miles=fields.Boolean(compute='_get_evnt_type', string='Is Type', store=True)


class account_invoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def invoice_line_move_line_get(self):
        res = []
        for line in self.invoice_line_ids:
            #if line.quantity==0:
            #    continue
            tax_ids = []
            for tax in line.invoice_line_tax_ids:
                tax_ids.append((4, tax.id, None))
                for child in tax.children_tax_ids:
                    if child.type_tax_use != 'none':
                        tax_ids.append((4, child.id, None))
            analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]

            move_line_dict = {
                'invl_id': line.id,
                'type': 'src',
                'name': line.name.split('\n')[0][:64],
                'price_unit': line.price_unit,
                'quantity': line.quantity,
                'price': line.price_subtotal,
                'account_id': line.account_id.id,
                'product_id': line.product_id.id,
                'uom_id': line.uom_id.id,
                'account_analytic_id': line.account_analytic_id.id,
                'tax_ids': tax_ids,
                'invoice_id': self.id,
                'analytic_tag_ids': analytic_tag_ids
            }
            if line['account_analytic_id']:
                move_line_dict['analytic_line_ids'] = [(0, 0, line._get_analytic_line())]
            res.append(move_line_dict)
        return res

    @api.multi
    def _message_auto_subscribe_notify(self, partner_ids):
        # Do not notify user it has been marked as follower of its employee.
        return

    @api.depends('event_start_date','date_invoice','create_date')
    def _get_year(self):
        """ get year from date """
        for rec in self:
            if rec.event_start_date:
                    new_date = rec.event_start_date +  ' 00:00:00'
                    rec.year = datetime.datetime.strptime(new_date, "%Y-%m-%d %H:%M:%S").timetuple().tm_year
            elif rec.date_invoice:
                    new_date = rec.date_invoice +  ' 00:00:00'
                    rec.year = datetime.datetime.strptime(new_date, "%Y-%m-%d %H:%M:%S").timetuple().tm_year
            elif rec.create_date:
                    rec.year = datetime.datetime.strptime(self.create_date, "%Y-%m-%d %H:%M:%S").timetuple().tm_year

    @api.depends('event_start_date', 'date_invoice', 'create_date')
    def _get_month(self):
        """ get month from date """
        for rec in self:
            if rec.event_start_date:
                new_date = rec.event_start_date +  ' 00:00:00'
                rec.month = str(datetime.datetime.strptime(new_date, "%Y-%m-%d %H:%M:%S").timetuple().tm_mon)
            elif rec.date_invoice:
                new_date = rec.date_invoice +  ' 00:00:00'
                rec.month = str(datetime.datetime.strptime(new_date, "%Y-%m-%d %H:%M:%S").timetuple().tm_mon)
            elif rec.create_date:
                rec.month = str(datetime.datetime.strptime(rec.create_date, "%Y-%m-%d %H:%M:%S").timetuple().tm_mon)

    @api.depends('event_id.cust_gpuid','event_id.cust_csid')
    def _get_event_glcode(self):
        ''' Function to get Event GL code and NUPID code from event '''
        for rec in self:
            if rec.event_id:
                rec.cust_gpuid = rec.event_id.cust_gpuid
                rec.cust_csid = rec.event_id.cust_csid

    # @api.one
    # def _set_event_glcode(self):
    #     ''' Function to set Event GL Code if changed in event '''
    #     result = []
    #     for event in self.pool.get('event').browse(cr, uid, ids):
    #         if event.cust_invoice_id:
    #             result.append(event.cust_invoice_id.id)
    #         for inv in event.supp_invoice_ids:
    #             result.append(inv.id)
    #     return result
    
    def get_event_view(self):
        account_obj = self
        mod_obj = self.env['ir.model.data']
        if account_obj.event_id.event_type == 'translation':
            res=self.sudo().env.ref('bista_iugroup.view_translation_event_form')
        else:
            res = self.sudo().env.ref('bista_iugroup.view_event_form')
        return {
                'name': _('View Event'),
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': res.id,
                'res_model': 'event',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'res_id': account_obj and account_obj.event_id.id or False,
        }       
        

    event_id=fields.Many2one('event','Related Event')
    doctor_id=fields.Many2one("doctor",'Doctor')
    location_id=fields.Many2one("location",'Location')
    language_id=fields.Many2one("language" ,"Language")
    language_id2=fields.Many2many("language" ,'lang_inv_rel','invoice_id','language_id',"To Language", track_visibility='onchange')
    invoice_id=fields.Integer("IU Invoice ID", readonly=True)
    is_monthly=fields.Boolean("Is Monthly")
    is_mailed=fields.Boolean("Is Mailed")
    is_emailed=fields.Boolean("Is Emailed")
    is_printed=fields.Boolean("Is Printed")
    is_faxed=fields.Boolean("Is Faxed")
    event_start_date=fields.Date(related='event_id.event_start_date',store=True, string="Event Date", readonly=True)
    event_start=fields.Datetime(related='event_id.event_start',store=True, string="Event Start", readonly=True)
    quickbooks_id=fields.Char("Quickbooks Id", size=64, readonly=True)
    contact_id=fields.Many2one('res.partner',"Contact" , domain="[('cust_type','=','contact')]", readonly=True, states={'draft':[('readonly',False)]})
    ordering_partner_id=fields.Many2one('res.partner',"Ordering Customer" ,domain="[('cust_type','=','customer')]", readonly=True, states={'draft':[('readonly',False)]})
    ordering_contact_id=fields.Many2one('res.partner',"Ordering Contact" ,  domain="[('cust_type','=','contact')]", readonly=True, states={'draft':[('readonly',False)]})
    cust_gpuid=fields.Char(compute='_get_event_glcode',string='Gl Code')
    cust_csid=fields.Char(compute='_get_event_glcode',string='NUID/GPUID Code')
    invoice_ref=fields.Many2one('account.invoice','Invoice Ref', readonly=True)
    check_no=fields.Char("Check No", size=64)
    claim_no=fields.Char("Claim No", size=64)
    patient_id=fields.Many2one(related='event_id.patient_id',relation="patient", store=True, string="Patient Name",readonly=True)
    project_name_id=fields.Many2one(related='event_id.project_name_id',relation="project", store=True, string="Project",readonly=True)
    ref=fields.Char(related='event_id.ref',store=True, string="Reference",readonly=True)
    event_type=fields.Selection(related='event_id.event_type',store=True, string="Event Type",readonly=True,
                                selection=EVENT_TYPES)
    invoice_id2=fields.Integer("IU Invoice ID2", readonly=True)
    sales_representative_id=fields.Many2one('res.users','Sales Representative', readonly=True)
    scheduler_id=fields.Many2one(related='event_id.scheduler_id',relation="res.users", store=True, string="Scheduler", readonly=True)
    invoice_for=fields.Selection([('transporter','Transporter'),('other','Other')],"Invoice For",default='other')
    comment=fields.Text("Comment", size=500,readonly=False,states={})
    year=fields.Char(compute='_get_year', string='Year' , store=True)
    month=fields.Selection(compute='_get_month', selection=[('1','January'), ('2','February'), ('3','March'), ('4','April'), ('5','May'), ('6','June'),('7','July'), ('8','August'), ('9','September'), ('10','October'), ('11','November'), ('12','December')], string='Month', readonly=True, index=True , store=True)
    create_date=fields.Datetime('Create Date')
    internal_comment=fields.Text("Internal Comment", size=300)
    state_name_related=fields.Many2one(related='partner_id.state_id', string='State Name',readonly=True, store=True)
    period_id=fields.Many2one('account.period', 'Force Period', domain=[('state', '<>', 'done')],
                                 help="Keep empty to use the period of the validation(invoice) date.", readonly=True,
                                 states={'draft': [('readonly', False)]})


    @api.multi
    def write(self,vals):
        for inv_data in self:
            event_obj = self.env['event']
            if vals.get('date_invoice',False):
                date = vals.get('date_invoice')
                # if vals.get('payment_term_id',False):
                #     payment_term_id = vals.get('payment_term_id',False)
                # else: payment_term_id = inv_data.payment_term_id and inv_data.payment_term_id.id or False
                # if payment_term_id:
                #     res = self.onchange_date_invoice(date, payment_term_id)
                #     vals['date_due'] = res['value']['date_due']
                # else:
                #     vals['date_due'] = False
                period_ids = self.env['account.period'].with_context(company_id=inv_data.company_id and inv_data.company_id.id or False).find(date).ids
                if period_ids:
                    vals['period_id'] = period_ids[0]
            if inv_data.event_id and inv_data.type == 'out_invoice':
                if 'state' in vals and vals['state'] == 'open':
                    if 'partner_id' in vals and vals['partner_id']:
                        if inv_data.event_id.partner_id.id <> vals['partner_id']:
                            inv_data.event_id.write({'partner_id': vals['partner_id']})

                    elif inv_data.event_id.partner_id.id <> inv_data.partner_id.id:
                        inv_data.event_id.write({'partner_id': inv_data.partner_id.id})

                    if 'ordering_partner_id' in vals and vals['ordering_partner_id']:
                        if inv_data.event_id.ordering_partner_id.id <> vals['ordering_partner_id']:
                            inv_data.event_id.write({'ordering_partner_id':vals['ordering_partner_id']})

                    elif inv_data.event_id.ordering_partner_id.id <> inv_data.ordering_partner_id.id:
                        inv_data.event_id.write({'ordering_partner_id':inv_data.ordering_partner_id.id})

                    if 'contact_id' in vals and vals['contact_id']:
                        if inv_data.event_id.contact_id.id <> vals['contact_id']:
                            inv_data.event_id.write({'contact_id':vals['contact_id']})

                    elif inv_data.event_id.contact_id.id <> inv_data.contact_id.id:
                        inv_data.event_id.write({'contact_id':inv_data.contact_id.id})

                    if 'ordering_contact_id' in vals and vals['ordering_contact_id']:
                        if inv_data.event_id.ordering_contact_id.id <> vals['ordering_contact_id']:
                            inv_data.event_id.write({'ordering_contact_id':vals['ordering_contact_id']})

                    elif inv_data.event_id.ordering_contact_id.id <> inv_data.ordering_contact_id.id:
                        inv_data.event_id.write({'ordering_contact_id':inv_data.ordering_contact_id.id})
        return super(account_invoice,self).write(vals)

    @api.multi
    def onchange_date_invoice(self,date_invoice,payment_term_id):
        result = {'value':{}}
        if not date_invoice:
            return result
        if date_invoice and payment_term_id :
            self._onchange_payment_term_date_invoice()
            result['value'].update({'date_due':self.date_due})
        else:
            result['value']['date_due'] = False
        return result
    
#     def correct_move_date_period(self, cr, uid, ids, context=None):
#         ''' For Correcting Date and Maturity Date and Period of Invoices '''
#         if context is None: context = {}
#         inv_obj = self.pool.get('account.invoice')
#         period_obj = self.pool.get('account.period')
#         invoice_ids = inv_obj.search(cr, uid, [])
#         print "invoice_ids......",len(invoice_ids)
# #        invoice_ids = ids
#         count = 0
#         for invoice in inv_obj.browse(cr, uid, invoice_ids):
#             count += 1
#             context.update({'company_id': invoice.company_id and invoice.company_id.id or False})
#             period_ids = period_obj.find(cr, uid, invoice.date_invoice, context=context)
#             period_id = period_ids and period_ids[0] or False
#
#             invoice.write({'period_id': period_id})
#             if invoice.move_id:
#                 move = invoice.move_id
#                 move.write({'date': invoice.date_invoice, 'period_id': period_id})
#                 move_line_ids = map(lambda x: x.id, move.line_id)
# #                print "datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d') + relativedelta.relativedelta(days=33).........",datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d') + relativedelta.relativedelta(days=33)
#                 cr.execute('''update account_move_line set period_id = %s, date_maturity = %s where id in %s ''', (period_id, invoice.date_due or datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d') + relativedelta.relativedelta(days=33) or 'False', tuple(move_line_ids)))
#             if count % 500 == 0:
#                 print "count.......",count
#                 cr.commit()
# #                for line in move.line_id:
# #                    print "line......",line
# #                    if line.credit:
# #                        line.write({'period_id': period_id})
# #                    else:
# #                        line.write({'period_id': period_id, 'date_maturity': invoice.date_due})
#         return True
#
#     def correct_translation_invoices(self, cr, uid, ids, context=None):
#         ''' For Corecting Translation Invoices'''
#         if context is None: context = {}
# #        wf_service = netsvc.LocalService("workflow")
#         inv_obj = self.pool.get('account.invoice')
#         event_obj = self.pool.get('event')
#         invoice_ids = inv_obj.search(cr, uid, [('event_type','=','translation'),('company_id','=',6)])
#         print "invoice_ids......",len(invoice_ids)
#         for invoice in inv_obj.browse(cr, uid, invoice_ids):
#             if invoice.partner_id.supplier:
#                 invoice.write({'journal_id':11,'account_id':39,'type':'in_invoice','date_invoice':invoice.event_start_date})
#                 event_obj.write(cr , uid, [invoice.event_id.id], {'supp_invoice_ids': [(6, 0, [invoice.id])]})
#             else:
#                 invoice.write({'journal_id':10,'account_id':34,'type':'out_invoice','date_invoice':invoice.event_start_date})
#                 event_obj.write(cr , uid, [invoice.event_id.id], {'cust_invoice_id': invoice.id})
#         invoice_ids = inv_obj.search(cr, uid, [('event_type','=','translation'),('company_id','=',4)])
#         print "invoice_ids......",len(invoice_ids)
#         for invoice in inv_obj.browse(cr, uid, invoice_ids):
#             if invoice.partner_id.supplier:
#                 invoice.write({'journal_id':35,'account_id':117,'type':'in_invoice','date_invoice':invoice.event_start_date})
#                 event_obj.write(cr , uid, [invoice.event_id.id], {'supp_invoice_ids': [(6, 0, [invoice.id])]})
#             else:
#                 invoice.write({'journal_id':34,'account_id':112,'type':'out_invoice','date_invoice':invoice.event_start_date})
#                 event_obj.write(cr , uid, [invoice.event_id.id], {'cust_invoice_id': invoice.id})
#         return True

    @api.multi
    def copy(self,default=None):
        ''' Function overridden to attach this supplier Invoice to the Event'''
        if default is None:
            default = {}
        default.update({
            'number': '',
            'internal_number': '',
            'quick_id':'',
            'in_qb':False
        })
        cur_obj =super(account_invoice, self).copy(default)
        if cur_obj.type == 'in_invoice':
            if cur_obj.event_id:
                cur_obj.event_id.write({'supp_invoice_ids': [(4, cur_obj.id)]})
        return cur_obj

    @api.model
    def line_get_convert(self,x, part):
        return {
            'date_maturity': x.get('date_maturity', False),
            'event_date': x.get('event_date', False),
            'patient_id': x.get('patient_id', False),
            'reference': x.get('reference', False),
            'project_name_id': x.get('project_name_id', False),
            'partner_id': part,
            'name': x['name'][:64],
            'debit': x['price']>0 and x['price'],
            'credit': x['price']<0 and -x['price'],
            'account_id': x['account_id'],
            'analytic_line_ids': x.get('analytic_line_ids', []),
            'amount_currency': x['price']>0 and abs(x.get('amount_currency', False)) or -abs(x.get('amount_currency', False)),
            'currency_id': x.get('currency_id', False),
            'tax_ids': x.get('tax_ids', False),
            'tax_line_id': x.get('tax_line_id', False),
            'ref': x.get('ref', False),
            'quantity': x.get('quantity',1.00),
            'product_id': x.get('product_id', False),
            'product_uom_id': x.get('uom_id', False),
            'analytic_account_id': x.get('account_analytic_id', False),
            'invoice_id': x.get('invoice_id', False),
            'analytic_tag_ids': x.get('analytic_tag_ids', False),
        }

    @api.model
    def _get_tax(self):
        journal_pool = self.env['account.journal']
        journal_id = self._context.get('journal_id', False)
        if not journal_id:
            ttype = self._context.get('type', 'bank')
            res = journal_pool.search([('type', '=', ttype)], limit=1)
            if not res:
                return False
            journal_id = res[0].id

        if not journal_id:
            return False
        journal = journal_pool.browse(journal_id)
        account_id = journal.default_credit_account_id or journal.default_debit_account_id
        if account_id and account_id.tax_ids:
            tax_id = account_id.tax_ids[0].id
            return tax_id
        return False

    @api.model
    def get_accounts(self, partner_id=False, journal_id=False):
        """price
        Returns a dict that contains new values and context
        @param partner_id: latest value from user input for field partner_id
        @param args: other arguments
        @param context: context arguments, like lang, time zone

        @return: Returns a dict which contains new values, and context
        """
        default = {
            'value':{},
        }

        if not partner_id or not journal_id:
            return default

        partner_obj = self.env['res.partner']
        journal_obj = self.env['account.journal']

        journal = journal_obj.browse(journal_id)
        partner = partner_obj.browse(partner_id)
        account_id = False
        tr_type = False
        if journal.type =='sale':
            account_id = partner.property_account_receivable_id.id
            tr_type = 'inbound'
        elif journal.type =='purchase':
            account_id = partner.property_account_payable_id.id
            tr_type = 'outbound'

        default['value']['account_id'] = account_id
        default['value']['type'] = tr_type

        return default

    @api.model
    def action_bulk_invoice_email(self):
        mod_obj = self.env['ir.model.data']
        template_id = mod_obj.get_object_reference('bista_iugroup', 'email_template_edi_invoice_sd')[1]

        for line in self:
            email=False
            if line.partner_id:
                email=line.partner_id.email or line.partner_id.email2
            mail_send = self.env['mail.template'].browse(template_id).with_context(
                recipient_ids=email).cancel_send_mail(line.id, force_send=True)
            _logger.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>mail_sendmail_send>>>%s>>>>>>>>",mail_send)
            line.write({'is_emailed':True})

    @api.multi
    def action_move_create(self):
        """
        This function is overriden to write event date from account.invoice to account.move.line on validate 
        Creates invoice related analytics and financial move lines
        """
        account_move = self.env['account.move']

        for inv in self:
            if not inv.journal_id.sequence_id:
                raise UserError(_('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line_ids:
                raise UserError(_('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)

            if not inv.date_invoice:
                inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
            company_currency = inv.company_id.currency_id

            # create move lines (one per invoice line + eventual taxes and analytic lines)
            iml = inv.invoice_line_move_line_get()
            iml += inv.tax_line_move_line_get()

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, iml)

            name = inv.name or '/'
            if inv.payment_term_id:
                totlines = \
                inv.with_context(ctx).payment_term_id.with_context(currency_id=company_currency.id).compute(total,
                                                                                                            inv.date_invoice)[
                    0]
                res_amount_currency = total_currency
                ctx['date'] = inv.date or inv.date_invoice
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id,
                        'event_date': inv.event_id and inv.event_id.event_start_date or False,
                        'patient_id': inv.event_id and inv.event_id.patient_id.id or False,
                        'project_name_id': inv.event_id and inv.event_id.project_name_id.id or False,
                        'reference': inv.event_id and inv.event_id.ref or False,
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'invoice_id': inv.id,
                    'event_date': inv.event_id and inv.event_id.event_start_date or False,
                    'patient_id': inv.event_id and inv.event_id.patient_id.id or False,
                    'project_name_id': inv.event_id and inv.event_id.project_name_id.id or False,
                    'reference': inv.event_id and inv.event_id.ref or False,
                })
            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
            line = inv.group_lines(iml, line)

            journal = inv.journal_id.with_context(ctx)
            line = inv.finalize_invoice_move_lines(line)

            date = inv.date or inv.date_invoice
            move_vals = {
                'ref': inv.reference,
                'line_ids': line,
                'journal_id': journal.id,
                'date': date,
                'narration': inv.comment,
            }
            ctx['company_id'] = inv.company_id.id
            ctx['invoice'] = inv
            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)
            move = account_move.with_context(ctx_nolang).create(move_vals)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'date': date,
                'move_name': move.name,
            }
            inv.with_context(ctx).write(vals)
        return True

    @api.multi
    def action_invoice_sent(self):
        ''' This Function is overridden to choose the default template as SD.
        This function opens a window to compose an email, with the edi invoice template message loaded by default
        '''
        self.ensure_one()
        template = self.env.ref('bista_iugroup.email_template_edi_invoice_sd', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model='account.invoice',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
            mark_invoice_emailed=True,
            custom_layout="account.mail_template_data_notification_email_account_invoice"
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def reset_to_draft_iu(self):
        ''' Function to Reset Invoice in open state only '''
        for invoice in self:
            if invoice.state == 'open':
                if invoice.move_id and invoice.move_id.state == 'posted':
                    journal = self.env['account.invoice'].browse(invoice.id).journal_id
                    journal.write({'update_posted': True})
                    invoice.action_cancel()
                    invoice.action_invoice_draft()
                    self.write({'state': 'draft'})
                else:
                    self.write({'state': 'draft'})
        return True
    
    # def set_amount_due(self, cr, uid, ids, context=None):
    #     ''' Function to set amount due for Invoice '''
    #     if context is None: context = {}
    #     if isinstance(ids, (int,long)): ids = [ids]
    #     invoice_ids = self.search(cr, uid, [])
    #     for invoice in self.browse(cr , uid, invoice_ids):
    #         if invoice.date_invoice:
    #             date_due = (datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d') + relativedelta.relativedelta(days=30)).strftime('%Y-%m-%d')
    #             self.write(cr , uid, [invoice.id], {'date_due': date_due})
    #     return True

    @api.multi
    def action_date_assign(self):
        self.compute_taxes()
        res = super(account_invoice, self).action_date_assign()
        return res

    # @api.multi
    # def invoice_pay_customer(self):
    #     ''' Overidden for company wise payment on Voucher wizard '''
    #     if not self.ids: return []
    #     dummy, view_id = self.env['ir.model.data'].get_object_reference('account_voucher', 'view_vendor_receipt_dialog_form')
    #     return {
    #         'name':_("Pay Invoice"),
    #         'view_mode': 'form',
    #         'view_id': view_id,
    #         'view_type': 'form',
    #         'res_model': 'account.voucher',
    #         'type': 'ir.actions.act_window',
    #         'nodestroy': True,
    #         'target': 'new',
    #         'domain': '[]',
    #         'context': {
    #             'default_company_id': self.company_id.id,
    #             'payment_expected_currency': self.currency_id.id,
    #             'default_partner_id': self.env['res.partner']._find_accounting_partner(self.partner_id).id,
    #             'default_amount': self.type in ('out_refund', 'in_refund') and -self.residual or self.residual,
    #             'default_reference': self.name,
    #             'close_after_process': True,
    #             'invoice_type': self.type,
    #             'invoice_id': self.id,
    #             'default_type': self.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
    #             'type': self.type in ('out_invoice','out_refund') and 'receipt' or 'payment'
    #         }
    #     }

#     @api.model
#     def make_payment_of_invoice_iu_supplier(self):
#         ''' For posting of Supplier Invoices '''
#         if isinstance(self.ids, (int,long)):
#             ids = [self.ids]
#         else:
#             ids = self.ids
#         res = {}
#         voucher_id = False
#         invoice_number = self.number
#         voucher_pool = self.env['account.voucher']
#         journal_pool = self.env['account.journal']
#         period_obj = self.env['account.period']
#         bank_journal_ids = journal_pool.search(cr, uid, [('type', '=', 'bank'),('company_id', '=', inv_obj.company_id.id)])
#         #print "bank_journal_ids.........",bank_journal_ids
#         if not len(bank_journal_ids):
#             return True
#         voucher_partner_id = inv_obj.partner_id.id
#         if inv_obj.partner_id.parent_id:
#             voucher_partner_id = inv_obj.partner_id.parent_id.id
#         context.update({
#                 'default_partner_id': voucher_partner_id or inv_obj.partner_id.id,
#                 'default_amount': inv_obj.amount_total,
#                 'default_name':inv_obj.name,
#                 'close_after_process': True,
#                 'invoice_type':inv_obj.type,
#                 'invoice_id':inv_obj.id,
#                 'journal_id':bank_journal_ids[0],
#                 'default_type': inv_obj.type in ('out_invoice','out_refund') and 'receipt' or 'payment'
#         })
#         if inv_obj.type in ('out_refund','in_refund'):
#             context.update({'default_amount':-inv_obj.amount_total})
#         tax_id = self._get_tax(cr, uid, context)
#         account_data = self.get_accounts(cr, uid, voucher_partner_id or inv_obj.partner_id.id,bank_journal_ids[0])
#         #print "account_data........",account_data
#         date = fields.date.context_today(self,cr,uid,context=context)
#         #print "inv_obj.period_id.id.......",inv_obj.period_id.id
#
#         # For using payment of customer instead of contact
#         voucher_data = {
#                 'period_id': inv_obj.period_id.id,
#                 'account_id': account_data['value']['account_id'],
#                 'partner_id': voucher_partner_id or inv_obj.partner_id.id,
#                 'journal_id':bank_journal_ids[0],
#                 'currency_id': inv_obj.currency_id.id,
#                 'reference': inv_obj.name or inv_obj.auth_transaction_id,   #payplan.name +':'+salesname
#                 'amount': inv_obj.amount_total,
#                 'type': account_data['value']['type'],
#                 'state': 'draft',
#                 'pay_now': 'pay_later',
#                 'name': '',
#                 'date': inv_obj.date_invoice or fields.date.context_today(self,cr,uid,context=context),
#                 'company_id': inv_obj.company_id and inv_obj.company_id.id or self.pool.get('res.company')._company_default_get(cr, uid, 'account.voucher',context=None),
#                 'tax_id': tax_id,
#                 'payment_option': 'without_writeoff',
#                 'comment': _('Write-Off'),
#             }
#         if inv_obj.type in ('out_refund','in_refund'):
#             voucher_data.update({'amount':-inv_obj.amount_total})
#         if not voucher_data['period_id']:
#             context.update({'company_id':inv_obj.company_id and inv_obj.company_id.id or self.pool.get('res.company')._company_default_get(cr, uid, 'account.voucher',context=None)})
#             period_ids = period_obj.find(cr, uid, inv_obj.date_invoice, context=context)
#             period_id = period_ids and period_ids[0] or False
#             voucher_data.update({'period_id':period_id})
#         voucher_id = voucher_pool.create(cr,uid,voucher_data)
#         if voucher_id:
#             #Get all the Documents for a Partner
#             if inv_obj.type in ('out_refund','in_refund'):
#                 amount=-inv_obj.amount_total
#                 res = voucher_pool.onchange_partner_id(cr, uid, [voucher_id], voucher_partner_id or inv_obj.partner_id.id, bank_journal_ids[0], amount, inv_obj.currency_id.id, account_data['value']['type'], date, context=context)
# #                print "res........",res
#             else:
#                 res = voucher_pool.onchange_partner_id(cr, uid, [voucher_id], voucher_partner_id or inv_obj.partner_id.id, bank_journal_ids[0], inv_obj.amount_total, inv_obj.currency_id.id, account_data['value']['type'], date, context=context)
# #                print "res.......",res
#             #Loop through each document and Pay only selected documents and create a single receipt
#             for line_data in res['value']['line_cr_ids']:
#                 if not line_data['amount']:
#                     continue
#                 if line_data['name'] in [invoice_number]:
#                     voucher_lines = {
#                         'move_line_id': line_data['move_line_id'],
#                         'amount': inv_obj.amount_total,
#                         'name': line_data['name'],
#                         'amount_unreconciled': line_data['amount_unreconciled'],
#                         'type': line_data['type'],
#                         'amount_original': line_data['amount_original'],
#                         'account_id': line_data['account_id'],
#                         'voucher_id': voucher_id,
#                     }
#                     #print "cr voucher line create",voucher_lines
#                     voucher_line_id = self.pool.get('account.voucher.line').create(cr,uid,voucher_lines)
#             for line_data in res['value']['line_dr_ids']:
#                 if not line_data['amount']:
#                     continue
#                 if line_data['name'] in [invoice_number]:
#                     voucher_lines = {
#                         'move_line_id': line_data['move_line_id'],
#                         'amount': inv_obj.amount_total,
#                         'name': line_data['name'],
#                         'amount_unreconciled': line_data['amount_unreconciled'],
#                         'type': line_data['type'],
#                         'amount_original': line_data['amount_original'],
#                         'account_id': line_data['account_id'],
#                         'voucher_id': voucher_id,
#                     }
#                     voucher_line_id = self.pool.get('account.voucher.line').create(cr,uid,voucher_lines)
#             voucher_pool.action_move_line_create(cr,uid,[voucher_id])
#         return voucher_id
#
#     def post_invoice_supplier(self, cr, uid, ids, context=None):
#         ''' For posting of Supplier Invoices '''
#         if context is None: context = {}
#         wf_service = netsvc.LocalService("workflow")
#         acc_obj = self.pool.get('account.invoice')
#         #invoice_ids=acc_obj.search(cr,uid,[('type','=','out_invoice'),('is_posted','=',True),('state','not in',['paid','cancel'])], order='id')
#         invoice_ids = ids
#         count = 0
#         for invoice in invoice_ids:
#             count += 1
#             wf_service.trg_delete(uid, 'account.invoice', invoice, cr)
#             wf_service.trg_create(uid, 'account.invoice', invoice, cr)
#             wf_service.trg_validate(uid, 'account.invoice', invoice, 'invoice_open', cr)
#             voucher_id = acc_obj.make_payment_of_invoice_iu_supplier(cr, uid, [invoice], context=context)
#             if count % 200 == 0:
#                 print "count.....",count
#                 cr.commit()
#         #self._log_event(cr, uid, ids, -1.0, 'Invoice Validated')
#         return True
#
#     def make_payment_of_invoice_iu(self, cr, uid, ids, context):
#         ''' For posting of Customer Invoices '''
#         if not context: context = {}
#         if isinstance(ids, (int,long)): ids = [ids]
#         res = {}
#         inv_obj = self.browse(cr,uid,ids[0])
#         voucher_id = False
#         invoice_number = inv_obj.number
#         voucher_pool = self.pool.get('account.voucher')
#         journal_pool = self.pool.get('account.journal')
#         period_obj = self.pool.get('account.period')
#         bank_journal_ids = journal_pool.search(cr, uid, [('type', '=', 'bank'),('company_id', '=', inv_obj.company_id.id)])
#         #print "bank_journal_ids.........",bank_journal_ids
#         if not len(bank_journal_ids):
#             return True
#         voucher_partner_id = inv_obj.partner_id.id
#         if inv_obj.partner_id.parent_id:
#             voucher_partner_id = inv_obj.partner_id.parent_id.id
#         context.update({
#                 'default_partner_id': voucher_partner_id or inv_obj.partner_id.id,
#                 'default_amount': inv_obj.amount_total,
#                 'default_name':inv_obj.name,
#                 'close_after_process': True,
#                 'invoice_type':inv_obj.type,
#                 'invoice_id':inv_obj.id,
#                 'journal_id':bank_journal_ids[0],
#                 'default_type': inv_obj.type in ('out_invoice','out_refund') and 'receipt' or 'payment'
#         })
#         if inv_obj.type in ('out_refund','in_refund'):
#             context.update({'default_amount':-inv_obj.amount_total})
#         tax_id = self._get_tax(cr, uid, context)
#         account_data = self.get_accounts(cr, uid, voucher_partner_id or inv_obj.partner_id.id,bank_journal_ids[0])
#         #print "account_data........",account_data
#         date = fields.date.context_today(self,cr,uid,context=context)
#         #print "inv_obj.period_id.id.......",inv_obj.period_id.id
#
#         # For using payment of customer instead of contact
#         if inv_obj.type in ('out_refund','in_refund'):
#             amount=-inv_obj.amount_total
#             res = voucher_pool.onchange_partner_id(cr, uid, [], voucher_partner_id or inv_obj.partner_id.id, bank_journal_ids[0], amount, inv_obj.currency_id.id, account_data['value']['type'], date, context=context)
#         else:
#             res = voucher_pool.onchange_partner_id(cr, uid, [], voucher_partner_id or inv_obj.partner_id.id, bank_journal_ids[0], inv_obj.amount_total, inv_obj.currency_id.id, account_data['value']['type'], date, context=context)
#             #print "res.......",res
#         voucher_data = {
#                 'period_id': inv_obj.period_id.id,
#                 'account_id': account_data['value']['account_id'],
#                 'partner_id': voucher_partner_id or inv_obj.partner_id.id,
#                 'journal_id':bank_journal_ids[0],
#                 'currency_id': inv_obj.currency_id.id,
#                 'reference': inv_obj.name or inv_obj.auth_transaction_id,   #payplan.name +':'+salesname
#                 'amount': inv_obj.amount_total,
#                 'type': account_data['value']['type'],
#                 'state': 'draft',
#                 'pay_now': 'pay_later',
#                 'name': '',
#                 'date': inv_obj.date_invoice or fields.date.context_today(self,cr,uid,context=context),
#                 'company_id': inv_obj.company_id and inv_obj.company_id.id or self.pool.get('res.company')._company_default_get(cr, uid, 'account.voucher',context=None),
#                 'tax_id': tax_id,
#                 'payment_option': 'without_writeoff',
#                 'comment': _('Write-Off'),
#             }
#         if inv_obj.type in ('out_refund','in_refund'):
#             voucher_data.update({'amount':-inv_obj.amount_total})
#         if not voucher_data['period_id']:
#             context.update({'company_id':inv_obj.company_id and inv_obj.company_id.id or self.pool.get('res.company')._company_default_get(cr, uid, 'account.voucher',context=None)})
#             period_ids = period_obj.find(cr, uid, inv_obj.date_invoice, context=context)
#             period_id = period_ids and period_ids[0] or False
#             voucher_data.update({'period_id':period_id})
#         #print "context......",context
#         #print "voucher_data........",voucher_data
#         voucher_id = voucher_pool.create(cr,uid,voucher_data)
#         if voucher_id:
#             #Get all the Documents for a Partner
#             #Loop through each document and Pay only selected documents and create a single receipt
#             for line_data in res['value']['line_cr_ids']:
#                 if not line_data['amount']:
#                     continue
#                 if line_data['name'] in [invoice_number]:
#                     voucher_lines = {
#                         'move_line_id': line_data['move_line_id'],
#                         'amount': inv_obj.amount_total,
#                         'name': line_data['name'],
#                         'amount_unreconciled': line_data['amount_unreconciled'],
#                         'type': line_data['type'],
#                         'amount_original': line_data['amount_original'],
#                         'account_id': line_data['account_id'],
#                         'voucher_id': voucher_id,
#                     }
#                     #print "cr voucher line create",voucher_lines
#                     voucher_line_id = self.pool.get('account.voucher.line').create(cr,uid,voucher_lines)
#             for line_data in res['value']['line_dr_ids']:
#                 if not line_data['amount']:
#                     continue
#                 if line_data['name'] in [invoice_number]:
#                     voucher_lines = {
#                         'move_line_id': line_data['move_line_id'],
#                         'amount': inv_obj.amount_total,
#                         'name': line_data['name'],
#                         'amount_unreconciled': line_data['amount_unreconciled'],
#                         'type': line_data['type'],
#                         'amount_original': line_data['amount_original'],
#                         'account_id': line_data['account_id'],
#                         'voucher_id': voucher_id,
#                     }
#                     #print "dr voucher line create-------------drrrrrrrrrrr",voucher_lines
#                     voucher_line_id = self.pool.get('account.voucher.line').create(cr,uid,voucher_lines)
#             #Add Journal Entries
#             #print "create lines",voucher_id
#             voucher_pool.action_move_line_create(cr,uid,[voucher_id])
#         return voucher_id
#
#     def post_invoice(self, cr, uid, ids, context=None):
#         ''' For posting of Customer Invoices '''
#         if context is None:
#             context = {}
#         wf_service = netsvc.LocalService("workflow")
#         acc_obj = self.pool.get('account.invoice')
#         invoice_ids=acc_obj.search(cr,uid,[('type','=','out_invoice'),('is_posted','=',True),('state','not in',['paid','cancel'])], order='id')
#         #invoice_ids = ids
# #        print "invoice_ids.........",len(invoice_ids)
#         count = 0
#         for invoice in invoice_ids:
#             count += 1
# #            print "count====-----------------",count
#             wf_service.trg_delete(uid, 'account.invoice', invoice, cr)
#             wf_service.trg_create(uid, 'account.invoice', invoice, cr)
#             wf_service.trg_validate(uid, 'account.invoice', invoice, 'invoice_open', cr)
#             voucher_id = acc_obj.make_payment_of_invoice_iu(cr, uid, [invoice], context=context)
#             if count % 200 == 0:
#                 print "count.....",count
#                 cr.commit()
#         #self._log_event(cr, uid, ids, -1.0, 'Invoice Validated')
#         return True

    @api.multi
    def reset_to_draft(self):
        self.write({'state':'draft'})
        return True

#     def make_payment_of_invoice(self, cr, uid, ids, context):
#         ''' For posting of Invoices From autorize.net '''
#         #print"context",context
#         if not context: context = {}
#         if isinstance(ids, (int,long)): ids = [ids]
#         inv_obj = self.browse(cr,uid,ids[0])
#         voucher_id = False
#         invoice_number = inv_obj.number
#         voucher_pool = self.pool.get('account.voucher')
#         journal_pool = self.pool.get('account.journal')
#         period_obj = self.pool.get('account.period')
#         bank_journal_ids = journal_pool.search(cr, uid, [('type', '=', 'bank')])
#
#         if not len(bank_journal_ids):
#             return True
#         for each in bank_journal_ids:
#             journal_name=journal_pool.browse(cr,uid,each).name
#             if journal_name=='Credit Card':
#                 credit_card=each
#             else:
#                 bank=each
#         if context.get('authorize',False)==True:
#             bank_journal_ids=credit_card
#         else:
#             bank_journal_ids=bank
#         context.update({
#                 'default_partner_id': inv_obj.partner_id.id,
#                 'default_amount': inv_obj.amount_total,
#                 'default_name':inv_obj.name,
#                 'close_after_process': True,
#                 'invoice_type':inv_obj.type,
#                 'invoice_id':inv_obj.id,
#                 'journal_id':bank_journal_ids,
#                 #'journal_id': 12,
#                 'default_type': inv_obj.type in ('out_invoice','out_refund') and 'receipt' or 'payment'
#         })
#         if inv_obj.type in ('out_refund','in_refund'):
#             context.update({'default_amount':-inv_obj.amount_total})
#         tax_id = self._get_tax(cr, uid, context)
#         account_data = self.get_accounts(cr,uid,inv_obj.partner_id.id,bank_journal_ids)
#         date = fields.date.context_today(self, cr, uid, context=context)
#         voucher_data = {
#             'period_id': inv_obj.period_id.id,
#             'account_id': account_data['value']['account_id'],
#             'partner_id': inv_obj.partner_id.id,
#             'journal_id':bank_journal_ids,
#             'currency_id': inv_obj.currency_id.id,
#             'reference': inv_obj.name or inv_obj.auth_transaction_id,   #payplan.name +':'+salesname
#             #'narration': data[0]['narration'],
#             'amount': inv_obj.amount_total,
#             'type':account_data['value']['type'],
#             'state': 'draft',
#             'pay_now': 'pay_later',
#             'name': '',
#             'date': fields.date.context_today(self,cr,uid,context=context),
# #                'date': inv_obj.date_invoice,
#             'company_id': inv_obj.company_id and inv_obj.company_id.id or self.pool.get('res.company')._company_default_get(cr, uid, 'account.voucher',context=None),
#             'tax_id': tax_id,
#             'payment_option': 'without_writeoff',
#             'comment': _('Write-Off'),
#         }
#         if inv_obj.type in ('out_refund','in_refund'):
#             voucher_data.update({'amount':-inv_obj.amount_total})
#         if not voucher_data['period_id']:
#             context.update({'company_id':inv_obj.company_id and inv_obj.company_id.id or self.pool.get('res.company')._company_default_get(cr, uid, 'account.voucher',context=None)})
#             period_ids = period_obj.find(cr, uid, inv_obj.date_invoice, context=context)
#             period_id = period_ids and period_ids[0] or False
#             voucher_data.update({'period_id':period_id})
#         voucher_id = voucher_pool.create(cr,uid,voucher_data)
#
#         if voucher_id:
#             #Get all the Documents for a Partner
#             if inv_obj.type in ('out_refund','in_refund'):
#                 amount=-inv_obj.amount_total
#                 res = voucher_pool.onchange_partner_id(cr, uid, [voucher_id], inv_obj.partner_id.id, bank_journal_ids, amount, inv_obj.currency_id.id, account_data['value']['type'], date, context=context)
#             else:
#                 res = voucher_pool.onchange_partner_id(cr, uid, [voucher_id], inv_obj.partner_id.id, bank_journal_ids, inv_obj.amount_total, inv_obj.currency_id.id, account_data['value']['type'], date, context=context)
#             #Loop through each document and Pay only selected documents and create a single receipt
#             for line_data in res['value']['line_cr_ids']:
#                 if not line_data['amount']:
#                     continue
#                 name = line_data['name']
#                 if line_data['name'] in [invoice_number]:
#                     voucher_lines = {
#                         'move_line_id': line_data['move_line_id'],
#                         'amount': inv_obj.amount_total,
#                         'name': line_data['name'],
#                         'amount_unreconciled': line_data['amount_unreconciled'],
#                         'type': line_data['type'],
#                         'amount_original': line_data['amount_original'],
#                         'account_id': line_data['account_id'],
#                         'voucher_id': voucher_id,
#                     }
# #                    print "cr voucher line create",voucher_lines
#                     voucher_line_id = self.pool.get('account.voucher.line').create(cr,uid,voucher_lines)
#
#             for line_data in res['value']['line_dr_ids']:
#
#                 if not line_data['amount']:
#                     continue
#                 name = line_data['name']
#                 if line_data['name'] in [invoice_number]:
#                     voucher_lines = {
#                         'move_line_id': line_data['move_line_id'],
#                         'amount': inv_obj.amount_total,
#                         'name': line_data['name'],
#                         'amount_unreconciled': line_data['amount_unreconciled'],
#                         'type': line_data['type'],
#                         'amount_original': line_data['amount_original'],
#                         'account_id': line_data['account_id'],
#                         'voucher_id': voucher_id,
#                     }
# #                    print "dr voucher line create-------------drrrrrrrrrrr",voucher_lines
#                     voucher_line_id = self.pool.get('account.voucher.line').create(cr,uid,voucher_lines)
#
#             #Add Journal Entries
# #            print "create lines",voucher_id
#             voucher_pool.action_move_line_create(cr,uid,[voucher_id])
#
#         return voucher_id
#
# account_invoice()

# class charge_customer(osv.osv_memory):
#     _inherit = "charge.customer"
#
#     def charge_customer(self,cr,uid,ids,context={}):
#         if context is None:
#             context = {}
#         act_model = context.get('active_model',False)
#         active_id = context.get('active_id',False)
#         customer_profile_id,cc_number,obj_all,transaction_id,transaction_response = False,'',False,'',''
#         authorize_net_config = self.pool.get('authorize.net.config')
#         if context.get('authorize',False)==True:
#             current_obj = self.pool.get('account.voucher').browse(cr,uid,ids[0])
#         else:
#             current_obj = self.browse(cr,uid,ids[0])
#         invoice_obj = self.pool.get('account.invoice')
#         wf_service = netsvc.LocalService("workflow")
#         if active_id:
#             if act_model == 'sale.order':
#                 obj = self.pool.get('sale.order')
#                 obj_all = obj.browse(cr,uid,active_id)
#                 customer_profile_id = obj_all.partner_id.customer_profile_id
#                 amount = obj_all.amount_total
#             elif act_model == 'account.invoice':
#                 obj = self.pool.get('account.invoice')
#                 obj_all = obj.browse(cr,uid,active_id)
# #                print"obj_all--------",obj_all
#                 if context.get('authorize',False)==True:
#                     charge_amount= current_obj.amount
#                 else:
#                     charge_amount=current_obj.charge_amount
#                 amount = obj_all.amount_total
#                 customer_profile_id = obj_all.partner_id.customer_profile_id
#                 if charge_amount <=0 or round((charge_amount + obj_all.amount_charged),2)  > obj_all.amount_total:
#                     raise osv.except_osv(_('Warning!'), _('You\'re charging an invalid amount,the chargeable amount is either invalid or greater than the Invoice amount !'))
#                 else:
#                     amount = charge_amount
#             ### additional code to check the active model from the customer voucher
#             elif act_model == 'account.voucher':
#                 obj = self.pool.get('account.voucher')
#                 obj_all = obj.browse(cr,uid,active_id)
#
#                 amount = obj_all.amount
#                 customer_profile_id = obj_all.partner_id.customer_profile_id
#                 if round(current_obj.charge_amount,2) <> amount:
#                     raise osv.except_osv(_('Warning!'), _('You\'re charging an invalid amount,the chargeable amount should be only the voucher amount !'))
#             #### code ends here
#
# #                cr.execute("SELECT order_id FROM sale_order_invoice_rel WHERE invoice_id=%s",(active_id[0],))
# #                id1 = cr.fetchone()
# #                if id1:
# #                    cr.execute("SELECT auth_transaction_id,authorization_code,customer_payment_profile_id,auth_respmsg FROM sale_order WHERE id = %s",(id1,))
# #                    result = cr.fetchall()
# #                    if result[0][1]:
# #                        cr.execute("UPDATE account_invoice SET auth_transaction_id='%s', authorization_code='%s', customer_payment_profile_id='%s',auth_respmsg='%s' where id=%s"%(result[0][0],result[0][1],result[0][2],result[0][3],active_id[0],))
# #                        cr.commit()
# #                        raise osv.except_osv(_('Warning!'), _('This record has already been authorize !'))
# #            if not obj_all.auth_transaction_id:
#             config_ids = authorize_net_config.search(cr,uid,[])
#             if config_ids and customer_profile_id:
#                 config_obj = authorize_net_config.browse(cr,uid,config_ids[0])
#                 if context.get('authorize',False)==True:
#                    cust_payment_profile_id=  obj_all.partner_id.profile_ids
#                    cust_payment_profile_id= cust_payment_profile_id[0].profile_id
#                 else:
#                     cust_payment_profile_id = current_obj.cust_payment_profile_id
#                 if context.get('authorize',False)==True:
#                     transaction_type='profileTransAuthCapture'
#                 else:
#                     transaction_type = current_obj.transaction_type
#
#                 if act_model in ('account.invoice','sale.order'):
#                     if obj_all.auth_transaction_id:
#                         transaction_id = obj_all.auth_transaction_id
#
#                 transaction_details =authorize_net_config.call(cr,uid,config_obj,'CreateCustomerProfileTransaction',active_id,transaction_type,amount,customer_profile_id,cust_payment_profile_id,transaction_id,act_model,'',context)
#
#                 cr.execute("select credit_card_no from custmer_payment_profile where profile_id='%s'"%(cust_payment_profile_id))
#                 cc_number = filter(None, map(lambda x:x[0], cr.fetchall()))
#                 if cc_number:
#                     cc_number = cc_number[0]
#
#                 transaction_response = transaction_details
#                 if transaction_details and obj._name=='sale.order':
#                     obj.api_response(cr,uid,active_id,transaction_response,customer_profile_id,cust_payment_profile_id,transaction_type,'XXXX'+cc_number,context)
#                 if transaction_details and obj._name=='account.invoice':
#                     obj.api_response(cr,uid,active_id,transaction_response,cust_payment_profile_id,transaction_type,context)
#
#                     split = transaction_details.split(',')
# #                    if obj_all.state =='open' and transaction_type == 'profileTransAuthCapture' and int(split[0]) == 1:
# #                        invoice_obj.make_payment_of_invoice(cr, uid, [obj_all.id],context)
#
#                     ### code to check the state of the Invoice and transaction type
# #                    print "obj all statre",obj_all.state
# #                    print "amount",(charge_amount + obj_all.amount_charged)
# #                    print "obj_all.amount_total",obj_all.amount_total
#                     if obj_all.state == 'draft' and round((charge_amount + obj_all.amount_charged),2) >= obj_all.amount_total  and  transaction_type == 'profileTransAuthCapture' and int(split[0]) == 1:
#                         wf_service.trg_validate(uid, 'account.invoice', obj_all.id, 'invoice_open', cr)
#                         invoice_obj.make_payment_of_invoice(cr, uid, [obj_all.id],context)
#                         obj_all.write({'amount_charged' :charge_amount + obj_all.amount_charged})
#                     elif obj_all.state == 'open' and round((charge_amount + obj_all.amount_charged),2) >= obj_all.amount_total and  transaction_type == 'profileTransAuthCapture' and int(split[0]) == 1:
#                         invoice_obj.make_payment_of_invoice(cr, uid, [obj_all.id],context)
#                         obj_all.write({'amount_charged' : charge_amount + obj_all.amount_charged})
#                     elif transaction_type == 'profileTransAuthCapture' and int(split[0]) == 1:
#                         obj_all.write({'amount_charged' : charge_amount + obj_all.amount_charged})
#                     view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'invoice_form')
#                     view_id = view_ref and view_ref[1] or False,
#                     return {
#                         'type': 'ir.actions.act_window',
#                         'name': _('Customer Invoices'),
#                         'res_model': 'account.invoice',
#                         'res_id': obj_all.id,
#                         'view_type': 'form',
#                         'view_mode': 'form',
#                         'view_id': view_id,
#                         'target': 'current',
#                         'nodestroy': True,
#                     }
#                 ### code to check for active model as account voucher and then validate the voucher
#                 if transaction_details and obj._name=='account.voucher':
#                     obj.api_response(cr,uid,active_id,transaction_response,cust_payment_profile_id,transaction_type,context)
#                     split = transaction_details.split(',')
#
#                     ### code to check the transaction details and voucher type of the transaction
#                     if obj_all.state == 'draft' and transaction_type == 'profileTransAuthCapture' and int(split[0]) == 1:
#                         wf_service.trg_validate(uid, 'account.voucher', obj_all.id, 'proforma_voucher', cr)
#                         view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account_voucher', 'view_voucher_form')
#                         view_id = view_ref and view_ref[1] or False,
#                         return {
#                             'type': 'ir.actions.act_window',
#                             'name': _('Customer Payments'),
#                             'res_model': 'account.voucher',
#                             'res_id': obj_all.id,
#                             'view_type': 'form',
#                             'view_mode': 'form',
#                             'view_id': view_id,
#                             'target': 'current',
#                             'nodestroy': True,
#                         }
#
#                     ### code ends here
#
#                 return transaction_details
#
# #                    if context.get('recurring_billing'):
#
# #                        wf_service = netsvc.LocalService("workflow")
# #                        wf_service.trg_validate(uid, 'sale.order', active_id[0], 'order_confirm', cr)
# #                        cr.execute('select invoice_id from sale_order_invoice_rel where order_id=%s'%(active_id[0]))
# #                        invoice_id=cr.fetchone()
# #                        if invoice_id:
# #                            self.pool.get('account.invoice').capture_payment(cr,uid,[invoice_id[0]],context)
#             else:
#                 raise osv.except_osv('Define Authorize.Net Configuration!', 'Warning:Define Authorize.Net Configuration!')
#         return {'type': 'ir.actions.act_window_close'}
# charge_customer()

class account_move_line(models.Model):
    _inherit = "account.move.line"
    
#    def _event_date(self, cursor, user, ids, name, arg, context=None):
#        ''' Function to get Event Date (Date of service) '''
#        invoice_obj = self.pool.get('account.invoice')
##        print "event_date ids.......",ids
#        res = {}
#        for line_id in ids:
#            res[line_id] = False
#        cursor.execute('SELECT l.id, i.id FROM account_move_line l, account_invoice i ' \
#                        'WHERE l.move_id = i.move_id AND l.id IN %s', (tuple(ids),))
#        invoice_ids, event_dates = [], {False: ''}
#        for line_id, invoice_id in cursor.fetchall():
#            res[line_id] = invoice_id
#            invoice_ids.append(invoice_id)
#            inv = invoice_obj.browse(cursor, user, invoice_id, context=context)
#            event_dates[inv.id] = inv.event_start_date or False
#        for line_id in res.keys():
#            invoice_id = res[line_id]
#            res[line_id] = event_dates[invoice_id] or False
##        print "returning res......",res
#        return res
    
#     def _event_date(self, cursor, user, ids, name, arg, context=None):
#         ''' Function to get Event Date (Date of service) '''
#         invoice_obj = self.pool.get('account.invoice')
# #        print "event_date ids.......",len(ids)
#         res = {}
#         for line_id in ids:
#             res[line_id] = False
#             cursor.execute('SELECT l.id, i.id FROM account_move_line l, account_invoice i ' \
#                             'WHERE l.move_id = i.move_id AND l.id IN %s', (tuple(ids),))
# #             invoice_ids, event_dates = [], {False: ''}
#             for line_id1, invoice_id in cursor.fetchall():
# #                print "invoice_id...line_id1....",invoice_id,line_id1
# #                 res[line_id] = invoice_id
# #                 invoice_ids.append(invoice_id)
# #                print "date,,,,,,",invoice_obj.browse(cursor, user, invoice_id, context=context).event_start_date
#                 res[line_id1] = invoice_obj.browse(cursor, user, invoice_id, context=context).event_start_date or False
# #                res[line_id1] = inv.event_start_date or False
# #             for line_id in res.keys():
# #                 invoice_id = res[line_id]
# #                 res[line_id] = event_dates[invoice_id] or False
# #        print "returning res......",res
#         return res
    

    event_date=fields.Date('Event Date')
    patient_id=fields.Many2one('patient', 'Patient/Client',)
    reference=fields.Char('Reference', size=64, index=True)
    project_name_id=fields.Many2one('project','Project')
    check_number=fields.Char('Check Number', size=32)


class account_period(models.Model):
    _inherit = "account.period"

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.company_id:
                name += " (%s)" %(record.company_id.name)
            res.append((record.id, name))
        return res

    @api.model
    def name_search(self,name, args=None, operator='ilike',limit=100):
        args = args or []
        ids=False
        if name:
            ids = self.search([('code', 'ilike', name)] + args, limit=limit)
        if not ids:
            ids = self.search([('name', operator, name)] + args, limit=limit)
        if not ids:
            ids = self.search([('company_id', operator, name)] + args, limit=limit)
        if ids:
            return ids.name_get()
        else:
            return self.name_get()

class account_account(models.Model):
    _inherit='account.account'

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.code:
                name = record.code + ' ' + name
            if record.company_id:
                name += " (%s)" %(record.company_id.name)
            res.append((record.id, name))
        return res

class account_journal(models.Model):
    _inherit='account.journal'

    @api.multi
    def name_get(self):
        res = []
        currency = False
        for record in self:
            name = record.name
            if record.currency_id:
                currency = record.currency_id
            else:
                currency = record.company_id.currency_id
            if currency:
                name += " (%s)" %(currency.name)
            if record.company_id:
                name += " (%s)" %(record.company_id.name)
            res.append((record.id, name))
        return res
