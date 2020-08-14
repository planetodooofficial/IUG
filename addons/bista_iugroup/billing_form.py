# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2004-2012 OpenERP S.A. (<http://openerp.com>).
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
import datetime
import pytz
from odoo import netsvc
from odoo import models, fields,api
from odoo.tools.translate import _
from odoo import SUPERUSER_ID, tools
from odoo.exceptions import UserError, RedirectWarning, ValidationError
import logging
_logger = logging.getLogger(__name__)

class event_lines(models.Model):
    _name="event.lines"

    def get_partner_id(self):
       for rec in self:
          rec.partner_id=rec.event_id.partner_id.id

    @api.multi
    @api.depends('event_start_date')
    def _compute_weekday_billing_form(self):
        for rec in self:
            if rec.event_start_date:
                dt = rec.event_start_date
                _logger.info(">>>>>>>>>>>>>>>>>>>dt dt %s>>>>>", type(dt))
                year, month, day = (int(x) for x in dt.split('-'))
                ans = datetime.date(year, month, day)
                _logger.info(">>>>>ans ans>>>%s>>>", ans)
                rec.weekday = ans.strftime("%A")

    billing_form_id=fields.Many2one('billing.form', "Billing Form Id")
    name=fields.Char('Group Name', size=128, index=True)
    event_id=fields.Many2one('event', "Source Event Id")
    state=fields.Selection(related='event_id.state', string="State" )
    user_id=fields.Many2one(related='event_id.user_id', store=True, string="User Id" )
    partner_id=fields.Many2one('res.partner',compute='get_partner_id', string="Billing Customer" )
    ordering_contact_id=fields.Many2one(related='event_id.ordering_contact_id', string="Ordering Contact" )
    event_start_date=fields.Date(related='event_id.event_start_date', store=True, string="Event Date" )
    event_start_time=fields.Char(related='event_id.event_start_time', store=True, string="Event Start Time" )
    event_end_time=fields.Char(related='event_id.event_end_time', store=True, string="Event End Time" )
#        'view_interpreter': fields.related('event_id','view_interpreter', type='many2one', relation='res.partner', string='Interpreter'),
    assigned_interpreters=fields.Many2many(related='event_id.assigned_interpreters', string='Interpreters')
    doctor_id=fields.Many2one(related='event_id.doctor_id', string='Doctor')
    location_id=fields.Many2one(related='event_id.location_id', string='Location')
    language_id=fields.Many2one(related='event_id.language_id', string='Language')
    patient_id=fields.Many2one(related='event_id.patient_id', string='Claimant')
    event_type=fields.Selection(related='event_id.event_type', store=True, string="Event Type" )
    company_id=fields.Many2one(related='event_id.company_id', string='Company')
    selected=fields.Boolean('Selected?')
    weekday = fields.Char(compute='_compute_weekday_billing_form', string='Weekday', store=True)



    @api.multi
    def select_event(self):
        ''' This Function select Event To be used in invoice flow '''
        mod_obj = self.env['ir.model.data']
        billing_obj = self.env['billing.form']
        int_note = ''
        for line in self:
            if line.event_id and line.billing_form_id:
                for interpreter in line.event_id.assigned_interpreters:
                    int_note = int_note + unicode(interpreter.complete_name) +':'+'<br>'+ (unicode(interpreter.billing_comment) if interpreter.billing_comment else '') +'<br>'
#                for interpreter in line.event_id.assigned_interpreters:
#                    int_note = interpreter.billing_comment or ''
                val = {
                    'cust_invoice_id': line.event_id.cust_invoice_id and line.event_id.cust_invoice_id.id or False,
#                    'supp_invoice_id': line.event_id.supp_invoice_id and line.event_id.supp_invoice_id.id or False,
                    'supp_invoice_id2': line.event_id.supp_invoice_id2 and line.event_id.supp_invoice_id2.id or False,
                    'selected_event_id': line.event_id.id,
                    'job_comment': line.event_id.comment or '',
                    'event_comment': line.event_id.event_note or '',
                    'billing_comment': int_note or '',
                    'customer_comment': line.event_id.partner_id and line.event_id.partner_id.billing_comment or '',
                    'event_line_id': line.id,
                    'event_start_hr': int(line.event_id.event_start_hr),
                    'event_start_min': int(line.event_id.event_start_min),
                    'am_pm': line.event_id.am_pm,
                    'event_end_hr': int(line.event_id.event_end_hr),
                    'event_end_min': int(line.event_id.event_end_min),
                    'am_pm2': line.event_id.am_pm2,
                    'event_start_date': line.event_id.event_start_date,
                    'invoice_date': line.event_id.event_start_date,
                    'emergency_rate': line.event_id.emergency_rate,
                }
                if line.event_id.cust_invoice_id and line.event_id.supp_invoice_ids:
                    val['invoice_exist'] = True
                else:
                    val['invoice_exist'] = False
#                if line.event_id.cust_invoice_id and line.event_id.cust_invoice_id.state in ('draft','open','paid'):
#                    val['cust_invoice_state'] = line.event_id.cust_invoice_id.state
#                if line.event_id.supp_invoice_id and line.event_id.supp_invoice_id.state in ('draft','open','paid'):
#                    val['supp_invoice_state'] = line.event_id.supp_invoice_id.state
                self.write({'selected': True})
                line.billing_form_id.write(val)
#                billing_obj.create_invoices(cr, uid, [line.billing_form_id], context=context)
                view_id = mod_obj.get_object_reference('bista_iugroup', 'view_billing_form')
                res_id = view_id and view_id[1] or False,
                return {
                    'name': _('Billing Form'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': [res_id[0]],
                    'res_model': 'billing.form',
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'current',
                    'res_id': line.billing_form_id.id or False,
                    'flags': {'form': {'action_buttons': True, 'options': {'mode': 'edit'}}},
                }
        return True

class billing_form(models.Model):
    _description = 'Billing form for accounting user'
    _name = "billing.form"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = "name"

    @api.depends('selected_event_id','cust_invoice_state','supp_invoice_state')
    def _check_invoiced_state(self):
        ''' Function to check Invoice State of the selected Event'''
        for bill_form in self:
            if bill_form.selected_event_id and bill_form.selected_event_id.event_type == 'language':
                if bill_form.cust_invoice_state and bill_form.cust_invoice_state == 'paid' \
                    and bill_form.supp_invoice_state and bill_form.supp_invoice_state == 'paid':
                    bill_form.selected_event_id.write({'state': 'done'})
                if bill_form.cust_invoice_state and bill_form.cust_invoice_state == 'open' \
                    and bill_form.supp_invoice_state and bill_form.supp_invoice_state in ('open','paid'):
                    bill_form.selected_event_id.write({'state': 'invoiced'})
                
            if bill_form.selected_event_id and bill_form.selected_event_id.event_type == 'transport':
                if bill_form.cust_invoice_state and bill_form.cust_invoice_state == 'paid' \
                    and bill_form.supp_invoice_state2 and bill_form.supp_invoice_state2 == 'paid':
                    bill_form.selected_event_id.write({'state': 'done'})
#                        print "event transport write state++++++++",write
            if bill_form.selected_event_id and bill_form.selected_event_id.event_type == 'lang_trans':
                if bill_form.cust_invoice_state and bill_form.cust_invoice_state == 'paid' \
                    and bill_form.supp_invoice_state and bill_form.supp_invoice_state == 'paid' \
                    and bill_form.supp_invoice_state2 and bill_form.supp_invoice_state2 == 'paid':
#                    print "in 1st ifffff+++++++++++++"
                    bill_form.selected_event_id.write({'state': 'done'})
            bill_form.all_invoiced=  True

    @api.depends('selected_event_id','supp_invoice_ids')
    def _get_interpreter_invoice_line(self):
        '''Function to get all interpreter invoices's lines '''
        for billing_form in self:
            line_ids = []
            if billing_form.selected_event_id:
                for invoice in billing_form.selected_event_id.supp_invoice_ids:
                    for line in invoice.invoice_line_ids:
                        line_ids.append(line.id)
            billing_form.supp_invoice_lines = line_ids
    
    def _set_interpreter_invoice_line(self):
        ''' Function used to make Interpreter invoice line Editable '''
        pass

    @api.depends('selected_event_id','cust_invoice_id')
    def _get_customer_invoice_line(self):
        '''Function to get customer invoices's lines '''
        for billing_form in self:
            line_ids = []
            if billing_form.selected_event_id:
                if billing_form.selected_event_id.cust_invoice_id:
                   billing_form.cust_invoice_id=billing_form.selected_event_id.cust_invoice_id.id
                for line in billing_form.selected_event_id.cust_invoice_id.invoice_line_ids:
                        line_ids.append(line.id)
            billing_form.cust_invoice_lines = line_ids

    def _set_customer_invoice_line(self):
        ''' Function used to make customer invoice line Editable '''
        pass


    @api.depends('selected_event_id','supp_invoice_id2')
    def _get_transporter_invoice_line(self):
        '''Function to get transporter invoices's lines '''
        for billing_form in self:
            line_ids = []
            if billing_form.selected_event_id:
                for line in billing_form.selected_event_id.supp_invoice_id2.invoice_line_ids:
                        line_ids.append(line.id)
            billing_form.supp_invoice_lines2 = line_ids

    def _set_transporter_invoice_line(self):
        ''' Function used to make transporter invoice line Editable '''
        pass

    @api.depends('selected_event_id','supp_invoice_ids')
    def _get_interpreter_invoice_state(self):
        ''' Function To get the Interpreter invoice State '''
        for billing_form in self:
            state = []
            if billing_form.selected_event_id:
                for invoice in billing_form.selected_event_id.supp_invoice_ids:
                    state.append(invoice.state)
            if 'draft' in state:
                final_state = 'draft'
            elif 'open' in state:
                final_state = 'open'
            elif 'paid' in state:
                final_state = 'paid'
            else:
                final_state = 'Not Exist'
            billing_form.supp_invoice_state = final_state

    @api.depends('selected_event_id', 'cust_invoice_id')
    def _get_customer_invoice_state(self):
        ''' Function To get the Customer invoice State '''
        for billing_form in self:
            state = []
            if billing_form.selected_event_id and billing_form.selected_event_id.cust_invoice_id:
                billing_form.cust_invoice_state = billing_form.selected_event_id.cust_invoice_id.state

    @api.depends('selected_event_id', 'supp_invoice_id2')
    def _get_transporter_invoice_state(self):
        ''' Function To get the Transporter invoice State '''
        for billing_form in self:
            state = []
            if billing_form.selected_event_id and billing_form.selected_event_id.supp_invoice_id2:
                billing_form.supp_invoice_state2 = billing_form.selected_event_id.supp_invoice_id2.state

    @api.depends('cust_invoice_lines','supp_invoice_lines','supp_invoice_lines2')
    def _get_gross_profit(self):
        ''' Function To get the Interpreter invoice State '''
        for billing_form in self:
            profit = 0.0
            for line in billing_form.cust_invoice_lines:
                profit += line.price_subtotal
            for line in billing_form.supp_invoice_lines:
                profit -= line.price_subtotal
            for line in billing_form.supp_invoice_lines2:
                profit -= line.price_subtotal
            billing_form.gross_profit= profit

    @api.depends('cust_invoice_id')
    def _get_invoice_comment(self):
        ''' Function to get invoice additional note '''
        for billing_form in self:
            if billing_form.cust_invoice_id:
                billing_form.invoice_comment = billing_form.cust_invoice_id.comment
            else:
                billing_form.invoice_comment= ''

    def _set_invoice_comment(self):
        ''' Function to make invoice additional note field editable '''
        for billing_form in self:
            if billing_form.cust_invoice_id:
                billing_form.cust_invoice_id.comment=billing_form.invoice_comment

    @api.depends('selected_event_id')
    def _get_customer_comment(self):
        ''' Function to get Customer Billing Note field '''
        for billing_form in self:
            if billing_form.selected_event_id and billing_form.selected_event_id.partner_id:
                billing_form.customer_comment= billing_form.selected_event_id.partner_id.billing_comment
            else:
                billing_form.customer_comment = ''

    def _set_customer_comment(self):
        ''' Function to make Customer Billing Note field editable '''
        for billing_form in self:
            if billing_form.selected_event_id and billing_form.selected_event_id.partner_id:
                billing_form.selected_event_id.partner_id.billing_comment=billing_form.customer_comment


    @api.depends('selected_event_id')
    def _get_rubrik_comment(self):
        ''' Function to get Customer Billing Note field '''
        for billing_form in self:
            if billing_form.selected_event_id and billing_form.selected_event_id.partner_id:
                billing_form.rubrik = billing_form.selected_event_id.partner_id.rubrik
            else:
                billing_form.rubrik = ''


    def _set_rubrik_comment(self):
        ''' Function to make Customer Billing Note field editable '''
        for billing_form in self:
            if billing_form.selected_event_id and billing_form.selected_event_id.partner_id:
                billing_form.selected_event_id.partner_id.rubrik=billing_form.rubrik


    @api.multi
    def approve_event(self):
        for event_ids in self:
            event = event_ids.selected_event_id
            if event:
                if event.partner_id and event.partner_id.order_note != True:
                    raise UserError(_('Selected event does not require verification'))
                elif event.partner_id and event.partner_id.order_note == True:
                    if event.verify_state == 'verified':
                        raise UserError(_('This event is already verified, and can be processed for invoicing'))
                    elif event.verify_state == False or None:
                        event.write({'verify_state':'verified'})
                        # return {
                        #     'type': 'ir.actions.client',
                        #     'tag': 'action_warn',#action_info
                        #     'name': _('Notification'),
                        #     'params': {
                        #         'title': 'Notification!',
                        #         'text': _('Event verified successfully!'),
                        #         'sticky': True,
                        #         }
                        # }
                        return self.env.user.notify_warning(
                            message='Event verified successfully!', title='Notification', sticky=True,
                            show_reload=False, foo="bar")
            
            return True



    name=fields.Char('Group Name', size=128, index=True)
    job_comment=fields.Text('Job Note')
    event_comment=fields.Text('Event Note')
    billing_comment=fields.Text('Billing Note')
    customer_comment=fields.Text(compute='_get_customer_comment', inverse='_set_customer_comment',string="Customer Billing Note")
    rubrik=fields.Text(compute='_get_rubrik_comment', inverse='_set_rubrik_comment',string="Rubrik")
#        'invoice_comment': fields.related('cust_invoice_id','comment', type="text", store=True, string="Invoice Add. Note", readonly=True,),
    invoice_comment=fields.Text(compute='_get_invoice_comment', inverse='_set_invoice_comment',string="Invoice Add. Note")

    invoice_exist=fields.Boolean('Invoice Exist', readonly=True,default=True)
    event_start=fields.Datetime("Event Start Time" )
    event_end=fields.Datetime("Event End Time")
    event_start_date=fields.Date("Event Date", )
    event_start_hr=fields.Integer("Event Start Hours", size=2, )
    event_start_min=fields.Integer("Event Start Minutes", size=2, )
    event_end_hr=fields.Integer("Event End Hours", size=2, )
    event_end_min=fields.Integer("Event End Minutes", size=2, )
    am_pm=fields.Selection([('am','AM'),('pm','PM')],"AM/PM", )
    am_pm2=fields.Selection([('am','AM'),('pm','PM')],"AM/PM", )
    customer_timezone=fields.Selection([('US/Pacific','US/Pacific'),('US/Eastern','US/Eastern'),('US/Alaska','US/Alaska'),('US/Aleutian','US/Aleutian'),('US/Arizona','US/Arizona')
                        ,('US/Central','US/Central'),('US/East-Indiana','US/East-Indiana'),('US/Hawaii','US/Hawaii'),('US/Indiana-Starke','US/Indiana-Starke'),('US/Michigan','US/Michigan')
                        ,('US/Mountain','US/Mountain'),('US/Samoa','US/Samoa')],'Customer TimeZone',)

    user_id=fields.Many2one('res.partner', "Done By")
    event_id=fields.Many2one('event', "Source Event Id")
    selected_event_id=fields.Many2one('event', "Selected Event Id")
    event_type=fields.Selection(related='selected_event_id.event_type',string="Event Type",store=False)
    event_line_id=fields.Many2one('event.lines', "Source Billing Line Id")
    event_lines=fields.One2many('event.lines','billing_form_id', 'Events')
    task_lines=fields.One2many(related='selected_event_id.task_id.work_ids', string='Task Lines')
    event_purpose=fields.Selection(related='selected_event_id.event_purpose', string='Event Purpose')

    cust_invoice_id=fields.Many2one('account.invoice','Customer Invoice')
    cust_invoice_lines=fields.One2many('account.invoice.line',compute='_get_customer_invoice_line',inverse = '_set_customer_invoice_line',string='Customer Invoice Lines')
#        'supp_invoice_lines': fields.related('supp_invoice_ids','invoice_line', type='one2many', relation='account.invoice.line', string='Interpreter Invoice Lines'),
#        'supp_invoice_id':fields.many2one('account.invoice','Interpreter Invoic
    # e'),
    supp_invoice_lines=fields.One2many('account.invoice.line',compute='_get_interpreter_invoice_line',inverse = '_set_interpreter_invoice_line',string = 'Interpreter Invoices')
    supp_invoice_ids=fields.Many2many('account.invoice','billing_inv_rel','bill_form_id','invoice_id','Interpreter Invoices')

    supp_invoice_lines2=fields.One2many('account.invoice.line',compute='_get_transporter_invoice_line',inverse = '_set_transporter_invoice_line', string='Transporter Invoice Lines')
    supp_invoice_id2=fields.Many2one('account.invoice','Transporter Invoice')

    all_invoiced=fields.Boolean(compute='_check_invoiced_state', string = 'All Invoiced',default=False)
    cust_invoice_state=fields.Char(compute=_get_customer_invoice_state,string="Customer Invoice State")
    supp_invoice_state=fields.Char(compute=_get_interpreter_invoice_state,string = 'Interpreter Invoice State')
    supp_invoice_state2=fields.Char(compute=_get_transporter_invoice_state, string="Transporter Invoice State")
    company_id=fields.Many2one('res.company', 'Company', index=1 ,required=True,default=lambda self: self.env['res.company']._company_default_get('billing.form'))
    gross_profit=fields.Float(compute='_get_gross_profit', string='Gross Profit')
    invoices_created=fields.Boolean('Invoices Created')
    invoice_date=fields.Date('Invoice Date')
    emergency_rate=fields.Boolean('Emergency Rate')

    @api.multi
    def update_invoices(self):
        ''' Function to Update Invoices for the selected event. It recalculate the Invoice Lines '''
        line_obj = self.env['account.invoice.line']
        task_obj = self.env['project.task']
        cur_obj = self

#        code start
        cust_invoice_lines=self.cust_invoice_lines
        for each in cust_invoice_lines:
            self._cr.execute('update account_invoice_line set total_editable =%s where id=%s', (0.0, each.id))
            self._cr.commit()

        supp_invoice_lines=self.supp_invoice_lines
        for each in supp_invoice_lines:
            self._cr.execute('update account_invoice_line set total_editable =%s where id =%s', (0.0, each.id))
            self._cr.commit()

#      code end
        if cur_obj.selected_event_id:
            if not cur_obj.selected_event_id.cust_invoice_id or not cur_obj.selected_event_id.supp_invoice_ids:
                raise UserError(_('Invoice are not yet generated for this event!'))
            if cur_obj.selected_event_id.cust_invoice_id:
                for line in cur_obj.selected_event_id.cust_invoice_id.invoice_line_ids:
                    if line.task_line_id:
                        inv_line_data = {}
                        if line.task_line_id.task_for == 'interpreter':
                            if not line.task_line_id.interpreter_id:
                                continue
                            self=self.with_context(interpreter=line.task_line_id.interpreter_id)
                            inv_line_data = task_obj._prepare_inv_line_interpreter_for_customer(line.account_id and line.account_id.id or False, line.task_line_id,line.invoice_id.event_id,
                                                    line.product_id)
                        elif line.task_line_id.task_for == 'transporter':
                            if not line.task_line_id.transporter_id:
                                continue
                            inv_line_data = task_obj._prepare_inv_line_transporter_for_customer(line.account_id and line.account_id.id or False, line.task_line_id,line.invoice_id.event_id,
                                                    line.product_id)
                        line.write(inv_line_data)
            for invoice in cur_obj.selected_event_id.supp_invoice_ids:
                for line in invoice.invoice_line_ids:
                    if line.task_line_id:
                        inv_line_data = {}
                        if line.task_line_id.task_for == 'interpreter':
                            if not line.task_line_id.interpreter_id:
                                continue
                            self = self.with_context(interpreter=line.task_line_id.interpreter_id)
                            inv_line_data = task_obj._prepare_inv_line_interpreter(line.account_id and line.account_id.id or False, line.task_line_id,line.invoice_id.event_id,
                                                    line.product_id)
                        elif line.task_line_id.task_for == 'transporter':
                            if not line.task_line_id.transporter_id:
                                continue
                            inv_line_data = task_obj._prepare_inv_line_transporter(line.account_id and line.account_id.id or False, line.task_line_id,line.invoice_id.event_id,
                                                    line.product_id)
                        line.write(inv_line_data)
            if cur_obj.selected_event_id.supp_invoice_id2:
                for line in cur_obj.selected_event_id.supp_invoice_id2.invoice_line_ids:
                    if line.task_line_id:
                        inv_line_data = {}
                        if line.task_line_id.task_for == 'interpreter':
                            if not line.task_line_id.interpreter_id:
                                continue
                            self = self.with_context(interpreter=line.task_line_id.interpreter_id)
                            inv_line_data = task_obj._prepare_inv_line_interpreter(line.account_id and line.account_id.id or False, line.task_line_id,line.invoice_id.event_id,
                                                    line.product_id)
                        elif line.task_line_id.task_for == 'transporter':
                            if not line.task_line_id.transporter_id:
                                continue
                            inv_line_data = task_obj._prepare_inv_line_transporter(line.account_id and line.account_id.id or False, line.task_line_id,line.invoice_id.event_id,
                                                    line.product_id)
                        line.write(inv_line_data)
        else:
            raise UserError(_('Please Select the event from list first to invoice!'))
        return True

    @api.multi
    def pay_invoice(self):
        ''' Function to Pay Invoice '''
        cur_obj = self
        mod_obj = self.env['ir.model.data']
        res = mod_obj.get_object_reference('bista_iugroup', 'invoice_payment_wizard_view')
        res_id = res and res[1] or False,
        if cur_obj.selected_event_id:
            if cur_obj.selected_event_id.cust_invoice_id :
                if cur_obj.selected_event_id.cust_invoice_id.state == 'open':
                    if self._context.get('invoice_type',False) and self._context.get('invoice_type',False) == 'customer':
                        if cur_obj.invoice_date:
                            cur_obj.selected_event_id.cust_invoice_id.write({'date_invoice':cur_obj.invoice_date})
                        amount = cur_obj.selected_event_id.cust_invoice_id.residual
                        if amount == 0.0:
                            amount = cur_obj.selected_event_id.cust_invoice_id.amount_total
                        val = {
                            'company_id': cur_obj.selected_event_id.cust_invoice_id.company_id and cur_obj.selected_event_id.cust_invoice_id.company_id.id or False,
                            'event_id': cur_obj.selected_event_id.id,
                            'invoice_id': cur_obj.selected_event_id.cust_invoice_id.id,
                            'amount': amount or 0.0,
                            'billing_form_id': self.ids[0],
                        }
                        self=self.with_context(invoice_id=cur_obj.selected_event_id.cust_invoice_id.id)
                        payment_form_id = self.env['invoice.payment.wizard'].create(val).id
                        return {
                            'name': _('Payment Form'),
                            'view_type': 'form',
                            'view_mode': 'form',
                            'view_id': [res_id[0]],
                            'res_model': 'invoice.payment.wizard',
                            'type': 'ir.actions.act_window',
                            'nodestroy': True,
                            'target': 'new',
                            'res_id': payment_form_id or False,
                        }
#                else:
#                    raise osv.except_osv(_('Warning!'),_('Customer Invoice is not in open state !'))

            if cur_obj.selected_event_id.supp_invoice_ids :
                for supp_invoice_id in cur_obj.selected_event_id.supp_invoice_ids:
                    if supp_invoice_id.state == 'open':
                        if self._context.get('invoice_type',False) and self._context.get('invoice_type',False) == 'supplier':
                            if cur_obj.invoice_date:
                                supp_invoice_id.write({'date_invoice':cur_obj.invoice_date})
                            print "residual.......",supp_invoice_id.residual
                            amount = supp_invoice_id.residual
                            if amount == 0.0:
                                amount = supp_invoice_id.amount_total
                            val = {
                                'company_id': supp_invoice_id.company_id and supp_invoice_id.company_id.id or False,
                                'event_id': cur_obj.selected_event_id.id,
                                'invoice_id': supp_invoice_id.id,
                                'amount': amount or 0.0,
                                'billing_form_id': self.ids[0],
                            }
                            self = self.with_context(invoice_id=supp_invoice_id.id)
                            payment_form_id = self.env['invoice.payment.wizard'].create(val).id
                            return {
                                'name': _('Payment Form'),
                                'view_type': 'form',
                                'view_mode': 'form',
                                'view_id': [res_id[0]],
                                'res_model': 'invoice.payment.wizard',
                                'type': 'ir.actions.act_window',
                                'nodestroy': True,
                                'target': 'new',
                                'res_id': payment_form_id or False,
                            }
                    else:
                        continue
#                else:
#                    raise osv.except_osv(_('Warning!'),_('Interpreter Invoice is not in open state !'))
            if cur_obj.selected_event_id.supp_invoice_id2 :
                if cur_obj.selected_event_id.supp_invoice_id2.state == 'open':
                    if self._context.get('invoice_type',False) and self._context.get('invoice_type',False) == 'transporter':
                        if cur_obj.invoice_date:
                            cur_obj.selected_event_id.supp_invoice_id2.write({'date_invoice':cur_obj.invoice_date})
#                        print "residual.......",cur_obj.selected_event_id.supp_invoice_id.residual
                        amount = cur_obj.selected_event_id.supp_invoice_id2.residual
                        if amount == 0.0:
                            amount = cur_obj.selected_event_id.supp_invoice_id2.amount_total
                        val = {
                            'company_id': cur_obj.selected_event_id.supp_invoice_id2.company_id and cur_obj.selected_event_id.supp_invoice_id2.company_id.id or False,
                            'event_id': cur_obj.selected_event_id.id,
                            'invoice_id': cur_obj.selected_event_id.supp_invoice_id2.id,
                            'amount': amount or 0.0,
                            'billing_form_id': self.ids[0],
                        }
                        self=self.with_context(invoice_id=cur_obj.selected_event_id.supp_invoice_id2.id)
                        payment_form_id = self.env['invoice.payment.wizard'].create(val).id
                        return {
                            'name': _('Payment Form'),
                            'view_type': 'form',
                            'view_mode': 'form',
                            'view_id': [res_id[0]],
                            'res_model': 'invoice.payment.wizard',
                            'type': 'ir.actions.act_window',
                            'nodestroy': True,
                            'target': 'new',
                            'res_id': payment_form_id or False,
                        }

#                else:
#                    raise osv.except_osv(_('Warning!'),_('Interpreter Invoice is not in open state !'))
            else:
                raise UserError(_('No Customer Invoice is generated for this event!'))
        else:
            raise UserError(_('Please Select the event from list first to invoice!'))
        return True

    @api.multi
    def pay_customer_invoice(self,journal_id, amount):
        ''' Function to Pay Customer Invoice '''
        cur_obj = self
        if cur_obj.selected_event_id:
            if cur_obj.selected_event_id.cust_invoice_id :
                if cur_obj.selected_event_id.cust_invoice_id.state == 'open':
                    cur_obj.selected_event_id.cust_invoice_id.pay_customer_invoice(journal_id, amount)
#                    self.write(cr, uid, ids, {'cust_invoice_state': 'paid'})
#                    cr.commit()
                else:
                    raise UserError(_('Customer Invoice is not in open state !'))
            else:
                raise UserError(_('No Customer Invoice is generated for this event!'))
        else:
            raise UserError(_('Please Select the event from list first to invoice!'))
        return True

    @api.multi
    def pay_supplier_invoice(self,journal_id, amount):
        ''' Function to Pay Supplier Invoice '''
        cur_obj = self
        if cur_obj.selected_event_id:
            if cur_obj.selected_event_id.supp_invoice_ids :
                for supp_invoice_id in cur_obj.selected_event_id.supp_invoice_ids:
                    if supp_invoice_id.state == 'open' :#and len(cur_obj.selected_event_id.supp_invoice_ids)==1
                        supp_invoice_id.pay_supplier_invoice(journal_id, amount)
                        break
    #                    self.write(cr, uid, ids, {'supp_invoice_state': 'paid'})
    #                    cr.commit()

#                    else:
#                        raise osv.except_osv(_('Warning!'),_('Interpreter Invoice is not in open state !'))
#                    elif supp_invoice_id.state == 'open' and len(cur_obj.selected_event_id.supp_invoice_ids)==2:
#                        self.pool.get('account.invoice').pay_supplier_invoice(cr , uid, [supp_invoice_id.id], journal_id, amount, context)
#                        break
    #                    self.write(cr, uid, ids, {'supp_invoice_state': 'paid'})
    #                    cr.commit()
                    elif supp_invoice_id.state == 'paid' :
                        continue
                    else:
                        raise UserError(_('Interpreter Invoice is not in open state !'))


            else:
                raise UserError(_('No Interpreter Invoice is generated for this event!'))
        else:
            raise UserError(_('Please Select the event from list first to invoice!'))
        return True

    @api.multi
    def pay_transporter_invoice(self,journal_id, amount):
        ''' Function to Pay Transporter Invoice '''
        cur_obj = self
        if cur_obj.selected_event_id:
            if cur_obj.selected_event_id.supp_invoice_id2 :
                if cur_obj.selected_event_id.supp_invoice_id2.state == 'open':
                    cur_obj.selected_event_id.supp_invoice_id2.pay_supplier_invoice(journal_id, amount)
#                    self.write(cr, uid, ids, {'supp_invoice_state': 'paid'})
#                    cr.commit()

                else:
                    raise UserError(_('Transporter Invoice is not in open state !'))
            else:
                raise UserError(_('No Transporter Invoice is generated for this event!'))
        else:
            raise UserError(_('Please Select the event from list first to invoice!'))
        return True

    @api.multi
    def reset_to_draft(self):
        ''' Function to Reset Customer and Supplier Invoices '''
        cur_obj = self
        if cur_obj.selected_event_id:
            if cur_obj.selected_event_id.cust_invoice_id:
                if cur_obj.selected_event_id.cust_invoice_id.state == 'draft':
                    pass
                elif cur_obj.selected_event_id.cust_invoice_id.state == 'open':
                    inv_id = cur_obj.selected_event_id.cust_invoice_id
                    if inv_id.move_id and inv_id.move_id.state == 'posted':
                        journal = inv_id.journal_id
                        journal.write({'update_posted': True})
                        inv_id.action_cancel()
                        inv_id.action_invoice_draft()
                else:
                    raise UserError(_('Customer Invoice is not in open state !'))
            else:
                raise UserError(_('No Customer Invoice is generated for this event!'))
            if not cur_obj.selected_event_id.supp_invoice_ids and cur_obj.selected_event_id.event_type in ('lang_trans','language') :
                raise UserError(_('No Interpreter Invoice is generated for this event!'))

            if cur_obj.selected_event_id.supp_invoice_ids:
                for supp_invoice_id in cur_obj.selected_event_id.supp_invoice_ids:
                    if supp_invoice_id.state == 'draft':
                        raise UserError(_('Interpreter Invoice is not in open state !'))
                    elif supp_invoice_id.state == 'open':
                        inv_id = supp_invoice_id
                        if inv_id.move_id and inv_id.move_id.state == 'posted':
                            journal = inv_id.journal_id
                            journal.write({'update_posted': True})
                            inv_id.action_cancel()
                            inv_id.action_invoice_draft()
            if not cur_obj.selected_event_id.supp_invoice_id2 and cur_obj.selected_event_id.event_type in ('lang_trans','transport') :
                raise UserError(_('No Transporter Invoice is generated for this event!'))
            if cur_obj.selected_event_id.supp_invoice_id2:
                if cur_obj.selected_event_id.supp_invoice_id2.state == 'draft':
                    pass
                elif cur_obj.selected_event_id.supp_invoice_id2.state == 'open':
                    inv_id = cur_obj.selected_event_id.supp_invoice_id2
                    if inv_id.move_id and inv_id.move_id.state == 'posted':
                        journal = inv_id.journal_id
                        journal.write({'update_posted': True})
                        inv_id.action_cancel()
                        inv_id.action_invoice_draft()
                else:
                    raise UserError(_('Transporter Invoice is not in open state !'))

        else:
            raise UserError(_('Please Select the event from list first to invoice!'))
        return True

    @api.multi
    def update_event_time(self):
        ''' Function to Update Actual Event Time '''
        cur_obj = self
        if cur_obj.selected_event_id:
            cur_obj.selected_event_id.write({'actual_event_start': cur_obj.event_start,'actual_event_end': cur_obj.event_end})
#            self.pool.get('event').write(cr, uid, [cur_obj.selected_event_id.id], {'actual_event_start': cur_obj.event_start,'actual_event_end': cur_obj.event_end})
        return True

    @api.multi
    def validate_invoices(self):
        ''' Function to Validate Customer and Supplier Invoice '''
        cur_obj = self
        # wf_service = netsvc.LocalService("workflow")
        if not cur_obj.selected_event_id:
            raise UserError(_('Please Select the event from list first to invoice!'))
        if cur_obj.selected_event_id:
            if cur_obj.selected_event_id.cust_invoice_id :
                if cur_obj.invoice_date:
                    cur_obj.selected_event_id.cust_invoice_id.write({'date_invoice':cur_obj.invoice_date})
                if cur_obj.selected_event_id.cust_invoice_id.state == 'draft':
                    # wf_service.trg_validate(self._uid, 'account.invoice', cur_obj.selected_event_id.cust_invoice_id.id, 'invoice_open', self._cr)
                    cur_obj.selected_event_id.cust_invoice_id.action_invoice_open()
#                    self.write(cr, uid, ids, {'cust_invoice_state': 'open'})
#                else:
#                    raise osv.except_osv(_('Warning!'),_('Customer Invoice is already Validated!'))
            else:
                raise UserError(_('No Customer Invoice is generated for this event!'))
            if not cur_obj.selected_event_id.supp_invoice_id2 and cur_obj.selected_event_id.event_type in ('lang_trans','transport') :
                raise UserError(_('No Transporter Invoice is generated for this event!'))
            if not cur_obj.selected_event_id.supp_invoice_ids and cur_obj.selected_event_id.event_type in ('lang_trans','language') :
                raise UserError(_('No Interpreter Invoice is generated for this event!'))

            if cur_obj.selected_event_id.supp_invoice_ids :
                for supp_invoice_id in cur_obj.selected_event_id.supp_invoice_ids:
                    if cur_obj.invoice_date:
                        supp_invoice_id.write({'date_invoice':cur_obj.invoice_date})
                    if supp_invoice_id.state == 'draft':
                        # wf_service.trg_validate(self._uid, 'account.invoice', supp_invoice_id.id, 'invoice_open', self._cr)
                        supp_invoice_id.action_invoice_open()
#                    self.write(cr, uid, ids, {'supp_invoice_state': 'open'})
#                else:
#                    raise osv.except_osv(_('Warning!'),_('Supplier Invoice is already Validated!'))
#            else:
#                raise osv.except_osv(_('Warning!'),_('No Interpreter Invoice is generated for this event!'))
#            print "cur_obj.selected_event_id.supp_invoice_id2cur_obj.selecte",cur_obj.selected_event_id.supp_invoice_id2
            if cur_obj.selected_event_id.supp_invoice_id2 :
                if cur_obj.invoice_date:
                        cur_obj.selected_event_id.supp_invoice_id2.write({'date_invoice':cur_obj.invoice_date})
                if cur_obj.selected_event_id.supp_invoice_id2.state == 'draft':
                    # wf_service.trg_validate(self._uid, 'account.invoice', cur_obj.selected_event_id.supp_invoice_id2.id, 'invoice_open', self._cr)
                    cur_obj.selected_event_id.supp_invoice_id2.action_invoice_open()
#                    self.write(cr, uid, ids, {'supp_invoice_state': 'open'})
#                else:
#                    raise osv.except_osv(_('Warning!'),_('Supplier Invoice is already Validated!'))
#            else:
#                raise osv.except_osv(_('Warning!'),_('No Supplier Invoice is generated for this event!'))
            cur_obj.selected_event_id.write({'state': 'invoiced'})
        return True

    @api.multi
    def create_invoices(self):
        ''' Function to create Invoices for the selected event '''
        mod_obj = self.env['ir.model.data']
        cur_obj = self
        inv_date = cur_obj.invoice_date if cur_obj.invoice_date else False
        self=self.with_context(invoice_date=inv_date)
        if cur_obj.selected_event_id:
            if cur_obj.selected_event_id.cust_invoice_id or cur_obj.selected_event_id.supp_invoice_ids  or cur_obj.selected_event_id.supp_invoice_id2 or cur_obj.selected_event_id.state == 'invoiced':
                raise UserError(_('Invoices are already generated for this event!'))
            if cur_obj.selected_event_id.task_id:
                if self.ids:
                    self=self.with_context(billing_form=True,billing_form_id=self.ids[0])
                cur_obj.selected_event_id.task_id.send_for_billing()
#                self.write(cr, uid, ids, {'cust_invoice_state': 'draft', 'invoice_exist': True, 'supp_invoice_state': 'draft'})
                self.write({'invoice_exist': True})
#                if cur_obj.event_line_id:
#                    self.pool.get('event.lines').write(cr, uid, [cur_obj.event_line_id.id], {'state': 'invoiced'})
            else:
                raise UserError(_('No Timesheet has been Entered for the selected Event yet!'))
	    for billing_form in cur_obj:
            	if billing_form.selected_event_id.cust_invoice_id:
                  		 billing_form.cust_invoice_id = billing_form.selected_event_id.cust_invoice_id.id
        else:
            raise UserError(_('Please Select the event from list first to invoice!'))
        view_id = mod_obj.get_object_reference('bista_iugroup', 'view_billing_form')
        res_id = view_id and view_id[1] or False,
#        my add
        self.write({'invoices_created': True})
        return {
            'name': _('Billing Form'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res_id[0]],
            'res_model': 'billing.form',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': self.ids and self.ids[0] or False,
        }

    @api.model
    def default_get(self, fields):
        '''Function to auto fill events for the selected event's interpreter '''
        res = {}
        res = super(billing_form , self).default_get(fields)
        event_id = self._context.get('event_id', [])
        if not event_id :
            return res
        event = self.env['event'].browse(event_id)
#        history_obj = self.pool.get('interpreter.alloc.history')
        event_ids, select_ids = [], []
        select_obj = self.env['event.lines']
        event_obj = self.env['event']
        if event_id:
            if event.event_type == 'language':
                if event.assigned_interpreters:#,('event_date','=',event.event_date)
#                    print "assgnd intrptr M2m+++++++++",event.assigned_interpreters
                    for interpreter in event.assigned_interpreters:
                        if self._context.get('search_default_state',False):
                            if self._context.get('search_default_state') == 'unbilled':
                                event_ids.extend(event_obj.search([('assigned_interpreters','in',[interpreter.id]),('state','=','unbilled'),
                                                             ('event_start_date','=',event.event_start_date)],).ids)
                            else:
                                event_ids.extend(event_obj.search([('assigned_interpreters','in',[interpreter.id]),('state','=','invoiced'),
                                                             ('event_start_date','=',event.event_start_date)],).ids)
                        else:
                            event_ids.extend(event_obj.search([('assigned_interpreters','in',[interpreter.id]),('state','in',('invoiced','unbilled')),
                                                             ('event_start_date','=',event.event_start_date)],).ids)
#                        print "in loop+",event_ids
#                    print "out loop+", list(set(event_ids))
                    
                    for event_id in list(set(event_ids)):
                        event_brwsd = event_obj.browse(event_id)
                        select_ids.append(select_obj.create({'event_id': event_id,'name': event_brwsd.name}).id)

            if event.event_type == 'transport':
                if event.transporter_id:#,('event_date','=',event.event_date)
                    if self._context.get('search_default_state',False):
                        if self._context.get('search_default_state') == 'unbilled':
                            event_ids = event_obj.search([('transporter_id','=',event.transporter_id.id),('state','=','unbilled'),('event_start_date','=',event.event_start_date)])
                        else:
                            event_ids = event_obj.search([('transporter_id','=',event.transporter_id.id),('state','=','invoiced'),('event_start_date','=',event.event_start_date)])
                    else:
                            event_ids = event_obj.search([('transporter_id','=',event.transporter_id.id),('state','in',('invoiced','unbilled')),('event_start_date','=',event.event_start_date)])
                    for event_brwsd in event_ids:
                        select_ids.append(select_obj.create({'event_id': event_id,'name': event_brwsd.name}).id)
            if event.event_type == 'translation':
                if event.translator_id:#,('event_date','=',event.event_date)
                    if self._context.get('search_default_state',False):
                        if self._context.get('search_default_state') == 'unbilled':
                            event_ids = event_obj.search([('translator_id','=',event.translator_id.id),('state','=','unbilled'),('event_start_date','=',event.event_start_date)])
                        else:
                            event_ids = event_obj.search([('translator_id','=',event.translator_id.id),('state','=','invoiced'),('event_start_date','=',event.event_start_date)])
                    else:
                        event_ids = event_obj.search([('translator_id','=',event.translator_id.id),('state','in',('invoiced','unbilled')),('event_start_date','=',event.event_start_date)])
                    for event_brwsd in event_ids:
                        select_ids.append(select_obj.create({'event_id': event_id,'name': event_brwsd.name}).id)
            if event.event_type == 'lang_trans' :
#                if event.interpreter_id:#,('event_date','=',event.event_date)
#
#                    event_ids = event_obj.search( cr ,uid ,[('interpreter_id','=',event.interpreter_id.id),('transporter_id','=',event.transporter_id.id),('state','in',('invoiced','unbilled')),('event_start_date','=',event.event_start_date)],)
#                    for event_id in event_ids:
#                        event_brwsd = event_obj.browse(cr, uid,event_id )
#                        select_ids.append(select_obj.create(cr ,uid ,{'event_id': event_id,'name': event_brwsd.name}))
                if event.assigned_interpreters:
                    for interpreter in event.assigned_interpreters:
                        if self._context.get('search_default_state',False):
                            if self._context.get('search_default_state') == 'unbilled':
                                event_ids.extend(event_obj.search([('assigned_interpreters','in',[interpreter.id]),('transporter_id','=',event.transporter_id.id),
                                                ('state','=','unbilled'),('event_start_date','=',event.event_start_date)]).ids)
                            else:
                                event_ids.extend(event_obj.search([('assigned_interpreters','in',[interpreter.id]),('transporter_id','=',event.transporter_id.id),
                                                ('state','=','invoiced'),('event_start_date','=',event.event_start_date)]).ids)
                        else:
                            event_ids.extend(event_obj.search([('assigned_interpreters','in',[interpreter.id]),('transporter_id','=',event.transporter_id.id),
                                                ('state','in',('invoiced','unbilled')),('event_start_date','=',event.event_start_date)],).ids)
#                        print "in loop+",event_ids
#                    print "out loop+", list(set(event_ids))

                    for event_id in list(set(event_ids)):
                        event_brwsd = event_obj.browse(event_id)
                        select_ids.append(select_obj.create({'event_id': event_id,'name': event_brwsd.name}).id)
#                        
#   -------------------- Mehul code-------------------------------------------
        event_obj = self.env['event']
        for event_id in list(set(event_ids)):
            date_new = event_obj.browse(event_id)
            date_chg = date_new.event_start_date
            res['invoice_date'] = date_chg
        res['event_lines']= [(6, 0, select_ids)]
        return res

    @api.model
    def create(self,vals):
        ''' Event_start and event_end fields are prepared and validated for further flow'''
        # Here formatting for Event Start date and Event End Date is done according to timezone of user or server
        if 'event_start_date' in vals or 'event_start_hr' in vals or 'event_start_min' in vals or 'event_end_hr' in vals or \
            'event_end_min' in vals or 'am_pm' in vals or 'am_pm2' in vals or 'customer_timezone' in vals:
            DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            # get user's timezone
            user = self.env.user
            customer_timezone = vals.get('customer_timezone',False)
            if customer_timezone:
                tz = pytz.timezone(customer_timezone) or pytz.utc
            elif user.tz:
                tz = pytz.timezone(user.tz) or pytz.utc
            else:
                tz = pytz.timezone("US/Pacific") or pytz.utc
            
            event_start_date = vals.get('event_start_date',False)
            event_start_hr = int(vals.get('event_start_hr',0.0))
            event_start_min = int(vals.get('event_start_min',0.0))
            event_end_hr = int(vals.get('event_end_hr',0.0))
            event_end_min = int(vals.get('event_end_min',0.0))
            am_pm = vals.get('am_pm',False)
            am_pm2 = vals.get('am_pm2',False)
            #print "event_date ,event_start_hr,event_start_min ,event_end_hr,event_end_min, am_pm,am_pm2........",event_start_date,event_start_hr,event_start_min,event_end_hr,event_end_min,am_pm,am_pm2
            if event_start_hr and event_start_hr > 12:
                raise UserError(_("Event start time hours can't be greater than 12 "))
            if event_start_min and event_start_min > 59:
                raise UserError(_("Event start time minutes can't be greater than 59 "))
            if event_end_hr and event_end_hr > 12:
                raise UserError(_(" Event end time hours can't be greater than 12 "))
            if event_end_min and event_end_min > 59:
                raise UserError(_("Event end time minutes can't be greater than 59 "))
            if event_start_hr < 1 and event_start_min < 1:
                raise UserError(_("Event start time can not be 0 or less than 0"))
            if event_end_hr < 1 and event_end_min < 1:
                raise UserError(_("Event end time can not be 0 or less than 0"))
            if event_start_date:
                if am_pm and am_pm == 'pm':
                    if event_start_hr < 12:
                        event_start_hr += 12
                if am_pm and am_pm == 'am':
                    if event_start_hr == 12:
                        event_start_hr = 0
                #print "event_start_hr...event_start_min......",event_start_hr,event_start_min
                if event_start_hr == 24: # for the 24 hour format
                    event_start_hr = 23
                    event_start_min = 59
                #print "event_start_hr...event_start_min......",event_start_hr,event_start_min
                event_start = str(event_start_date) + ' ' + str(event_start_hr) + ':' + str(event_start_min) + ':00'
                #print 'event_start.......',event_start
                local_dt = tz.localize(datetime.datetime.strptime(event_start,DATETIME_FORMAT), is_dst=None)
                #print "local_dt........",local_dt
                utc_dt = local_dt.astimezone (pytz.utc).strftime (DATETIME_FORMAT)
                #print "utc_dt.........",utc_dt
                vals['event_start'] = utc_dt
                if am_pm2 and am_pm2 == 'pm':
                    if event_end_hr < 12:
                        event_end_hr += 12
                if am_pm2 and am_pm2 == 'am':
                    if event_end_hr == 12:
                        event_end_hr = 0
                #print "event_end_hr...event_end_min......",event_end_hr,event_end_min
                if event_end_hr == 24: # for the 24 hour format
                    event_end_hr = 23
                    event_end_min = 59
                #print "event_end_hr...event_end_min......",event_end_hr,event_end_min
                event_end = str(event_start_date) + ' ' + str(event_end_hr) + ':' + str(event_end_min) + ':00'
                #print 'event_end.......',event_end
                local_dt1 = tz.localize(datetime.datetime.strptime(event_end,DATETIME_FORMAT), is_dst=None)
                #print "local_dt1........",local_dt1
                utc_dt1 = local_dt1.astimezone (pytz.utc).strftime (DATETIME_FORMAT)
                #print "utc_dt1.........",utc_dt1
                vals['event_end'] = utc_dt1

                if datetime.datetime.strptime(event_end,DATETIME_FORMAT) < datetime.datetime.strptime(event_start,DATETIME_FORMAT):
                    raise UserError(_('Event start time cannot be greater than event end time.'))
                elif datetime.datetime.strptime(event_end,DATETIME_FORMAT) == datetime.datetime.strptime(event_start,DATETIME_FORMAT):
                    raise UserError(_('Event start time and end time cannot be identical.'))
        return super(billing_form, self).create(vals)

    @api.multi
    def write(self, vals):
        ''' Event_start and event_end fields are prepared and validated for further flow'''
        #print "vals...",vals
#       Updating Invoice date on Save of Billing Form
        if vals.get('invoice_date',False):
            eve = self.selected_event_id
            if not eve:
                if 'selected_event_id' in vals and vals['selected_event_id']:
                    eve = self.env['event'].browse(vals.get('selected_event_id'))
            invoices = []
            if eve and eve.cust_invoice_id:
                invoices.append(eve.cust_invoice_id)
            if eve:
                invoices.extend([inv_id for inv_id in eve.supp_invoice_ids if inv_id])
            if eve and eve.supp_invoice_id2:
                invoices.append(eve.supp_invoice_id2)
#            print "invices++++++++++=",invoices
            if invoices:
                for each_inv in invoices:
                    if each_inv.state not in ['paid','cancel']:
                        each_inv.write({'date_invoice':vals.get('invoice_date',False)})
#                        raise osv.except_osv(_('Error!'), _("Cannot change Invoice Date as one or more invoices are in Paid or Cancelled state"))
        # Here formatting for Event Start date and Event End Date is done according to timezone of user or server
        if 'event_start_date' in vals or 'event_start_hr' in vals or 'event_start_min' in vals or 'event_end_hr' in vals or \
            'event_end_min' in vals or 'am_pm' in vals or 'am_pm2' in vals or 'customer_timezone' in vals :
            DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            # get user's timezone
            user = self.env.user
            cur_obj = self
            tz = False
            customer_timezone = False
            #print "vals['customer_timezone']........",vals['customer_timezone']
            if 'customer_timezone' in vals and vals['customer_timezone']:
                customer_timezone = vals.get('customer_timezone',False)
            else:
                customer_timezone = cur_obj.customer_timezone
            #print "customer_timezone..........",customer_timezone
            if customer_timezone:
                tz = pytz.timezone(customer_timezone) or pytz.utc
            elif user.tz:
                tz = pytz.timezone(user.tz) or pytz.utc
            else:
                tz = pytz.timezone("US/Pacific") or pytz.utc
            #print "tz...........",tz
            event_start_date ,event_start_hr ,event_start_min = False , 0 ,0
            event_end_hr , event_end_min , am_pm , am_pm2 = 0 , 0 , 'am' , 'pm'
            if 'event_start_date' in vals and vals['event_start_date']:
                event_start_date = vals.get('event_start_date',False)
            else:
                event_start_date = cur_obj.event_start_date
            if 'event_start_hr' in vals :
                event_start_hr = int(vals.get('event_start_hr',0.0))
            else:
                event_start_hr = int(cur_obj.event_start_hr)
            if 'event_start_min' in vals :
                event_start_min = int(vals.get('event_start_min',0.0))
            else:
                event_start_min = int(cur_obj.event_start_min)
            if 'event_end_hr' in vals :
                event_end_hr = int(vals.get('event_end_hr',0.0))
            else:
                event_end_hr = int(cur_obj.event_end_hr)
            if 'event_end_min' in vals :
                event_end_min = int(vals.get('event_end_min',0.0))
            else:
                event_end_min = int(cur_obj.event_end_min)
            if 'am_pm' in vals and vals['am_pm']:
                am_pm = vals.get('am_pm',False)
            else:
                am_pm = cur_obj.am_pm
            if 'am_pm2' in vals and vals['am_pm2']:
                am_pm2 = vals.get('am_pm2',False)
            else:
                am_pm2 = cur_obj.am_pm2
            #print "event_date ,event_start_hr,event_start_min ,event_end_hr,event_end_min, am_pm,am_pm2........",event_start_date,event_start_hr,event_start_min,event_end_hr,event_end_min,am_pm,am_pm2
            if event_start_hr and event_start_hr > 12:
                raise UserError(_("Event start time hours can't be greater than 12 "))
            if event_start_min and event_start_min > 59:
                raise UserError(_("Event start time minutes can't be greater than 59 "))
#            if (event_start_hr and event_start_min) and (event_start_hr == 12 and event_start_min > 0):
#                raise osv.except_osv(_('Check Start time!'), _("Event start time can't be greater than 12 O'clock "))
            if event_end_hr and event_end_hr > 12:
                raise UserError(_(" Event end time hours can't be greater than 12 "))
            if event_end_min and event_end_min > 59:
                raise UserError(_("Event end time minutes can't be greater than 59 "))
#            if (event_end_hr and event_end_min) and (event_end_hr == 12 and event_end_min > 0):
#                raise osv.except_osv(_('Check End time!'), _("Event End time can't be greater than 12 O'clock "))
            if event_start_hr < 1 and event_start_min < 1:
                raise UserError(_("Event start time can not be 0 or less than 0"))
            if event_end_hr < 1 and event_end_min < 1:
                raise UserError(_("Event end time can not be 0 or less than 0"))
            if event_start_date:
                if am_pm and am_pm == 'pm':
                    if event_start_hr < 12:
                        event_start_hr += 12
                if am_pm and am_pm == 'am':
                    if event_start_hr == 12:
                        event_start_hr = 0
                #print "event_start_hr...event_start_min......",event_start_hr,event_start_min
                if event_start_hr == 24: # for the 24 hour format
                    event_start_hr = 23
                    event_start_min = 59
                #print "event_start_hr...event_start_min......",event_start_hr,event_start_min
                event_start = str(event_start_date) + ' ' + str(event_start_hr) + ':' + str(event_start_min) + ':00'
                #print 'event_start.......',event_start
                local_dt = tz.localize(datetime.datetime.strptime(event_start,DATETIME_FORMAT), is_dst=None)
                #print "local_dt........",local_dt
                utc_dt = local_dt.astimezone (pytz.utc).strftime (DATETIME_FORMAT)
                #print "utc_dt.........",utc_dt
                vals['event_start'] = utc_dt
                if am_pm2 and am_pm2 == 'pm':
                    if event_end_hr < 12:
                        event_end_hr += 12
                if am_pm2 and am_pm2 == 'am':
                    if event_end_hr == 12:
                        event_end_hr = 0
                #print "event_end_hr...event_end_min......",event_end_hr,event_end_min
                if event_end_hr == 24: # for the 24 hour format
                    event_end_hr = 23
                    event_end_min = 59
                #print "event_end_hr...event_end_min......",event_end_hr,event_end_min
                event_end = str(event_start_date) + ' ' + str(event_end_hr) + ':' + str(event_end_min) + ':00'
                #print 'event_end.......',event_end
                local_dt1 = tz.localize(datetime.datetime.strptime(event_end,DATETIME_FORMAT), is_dst=None)
                #print "local_dt1........",local_dt1
                utc_dt1 = local_dt1.astimezone (pytz.utc).strftime (DATETIME_FORMAT)
                #print "utc_dt1.........",utc_dt1
                vals['event_end'] = utc_dt1
                if datetime.datetime.strptime(event_end,DATETIME_FORMAT) < datetime.datetime.strptime(event_start,DATETIME_FORMAT):
                    raise UserError(_('Event start time cannot be greater than event end time.'))
                elif datetime.datetime.strptime(event_end,DATETIME_FORMAT) == datetime.datetime.strptime(event_start,DATETIME_FORMAT):
                    raise UserError(_('Event start time and end time cannot be identical.'))
        #print "vals........",vals
        return super(billing_form , self).write(vals)
        
class account_invoice(models.Model):
    _inherit='account.invoice'

    @api.multi
    def pay_customer_invoice(self,journal_id, amount):
        ''' Function to pay Customer Invoices '''
        inv_obj = self
        invoice_number = inv_obj.number
        payment_obj = self.env['account.payment']
        period_obj = self.env['account.period']
#        bank_journal_ids = journal_pool.search(cr, uid, [('type', '=', 'bank'),('company_id', '=', inv_obj.company_id.id)])
#        #print "bank_journal_ids.........",bank_journal_ids
#        if not len(bank_journal_ids):
#            return True
        bank_journal_ids = [journal_id]
        payment_partner_id = inv_obj.partner_id.id
        if inv_obj.partner_id.parent_id:
            payment_partner_id = inv_obj.partner_id.parent_id.id
        self=self.with_context(
                default_partner_id=payment_partner_id or inv_obj.partner_id.id,
                default_amount=amount,
                default_name=inv_obj.name,
                close_after_process=True,
                invoice_type=inv_obj.type,
                invoice_id=inv_obj.id,
                journal_id=bank_journal_ids[0],
                default_type=inv_obj.type in ('out_invoice','out_refund') and 'receipt' or 'payment'
        )
        if inv_obj.type in ('out_refund','in_refund'):
            self=self.with_context(default_amount=-amount)

        date = fields.Date.context_today(self)
        payment_method_id=self.env['account.payment.method'].search([('payment_type','=','inbound')],limit=1).id
        #print "inv_obj.period_id.id.......",inv_obj.period_id.id

        # For using selected move lines only for payment in voucher
#        context['move_line_ids'] = []
#        if inv_obj.move_id:
#            for move_line in inv_obj.move_id.line_id:
#                context['move_line_ids'].append(move_line.id)
#         if inv_obj.type in ('out_refund','in_refund'):
#             amount = -amount
#             res = payment_obj.onchange_partner_id(cr, uid, [], voucher_partner_id or inv_obj.partner_id.id, bank_journal_ids[0], amount, inv_obj.currency_id.id, account_data['value']['type'], date, context=context)
#         else:
#             res = voucher_pool.onchange_partner_id(cr, uid, [], voucher_partner_id or inv_obj.partner_id.id, bank_journal_ids[0], amount, inv_obj.currency_id.id, account_data['value']['type'], date, context=context)
            #print "res.......",res
        payment_data = {
            'period_id': inv_obj.period_id.id,
            'partner_id': payment_partner_id or inv_obj.partner_id.id,
            'journal_id':bank_journal_ids[0],
            'currency_id': inv_obj.currency_id.id,
            'reference': inv_obj.name or '',   #payplan.name +':'+salesname
            'amount': amount,
            'state': 'draft',
            'name': '',
            'payment_date': inv_obj.date_invoice or fields.Date.context_today(self),
            'company_id': inv_obj.company_id and inv_obj.company_id.id or False,
            'payment_method_id':payment_method_id,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'invoice_ids': [(4, inv_obj.id, None)]
        }
        if self._context.get('check_number',False):
            payment_data['check_number'] = self._context.get('check_number')
        if not payment_data['period_id']:
            self=self.with_context(company_id=inv_obj.company_id and inv_obj.company_id.id )
            period_ids = period_obj.find(inv_obj.date_invoice)
            period_id = period_ids and period_ids[0] or False
            payment_data.update({'period_id':period_id})
        #print "context......",context
#        print "voucher_data........",voucher_data
        payment_id = payment_obj.create(payment_data)
        logger = logging.getLogger('test2')
        logger.info("This is invoice ids------->%s " % str(payment_id.invoice_ids))
        logger.info("This is payment type------->%s " % str(payment_id.payment_type))
        logger.info("This is dest account id------->%s " % str(payment_id.destination_account_id))
        logger.info("This is partner id------->%s " % str(payment_id.partner_id))
        payment_id.post()
#        print "voucher_id..........",voucher_id
        return payment_id.id

    @api.model
    def get_accounts_supplier(self,partner_id=False, journal_id=False):
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
        
        partner_pool = self.env['res.partner']
        journal_pool = self.env['account.journal']
        
        journal = journal_pool.browse(journal_id)
        partner = partner_pool.browse(partner_id)
        account_id = False
        tr_type = False
        if journal.type =='sale':
            account_id = partner.property_account_receivable_id.id
            tr_type = 'inbound'
        elif journal.type == 'purchase':
            account_id = partner.property_account_payable_id.id
            tr_type = 'outbound'
        default['value']['account_id'] = account_id
        default['value']['type'] = tr_type

        return default

    @api.multi
    def pay_supplier_invoice(self,journal_id, amount):
        ''' Function to pay Supplier Invoice '''
        res, voucher_id = {}, False
        inv_obj = self
        invoice_number = inv_obj.number
        payment_obj = self.env['account.payment']
        period_obj = self.env['account.period']
#        bank_journal_ids = journal_pool.search(cr, uid, [('type', '=', 'bank'),('company_id', '=', inv_obj.company_id.id)])
#        #print "bank_journal_ids.........",bank_journal_ids
#        if not len(bank_journal_ids):
#            return True
        bank_journal_ids = [journal_id]
        payment_partner_id = inv_obj.partner_id.id
        if inv_obj.partner_id.parent_id:
            payment_partner_id = inv_obj.partner_id.parent_id.id
        self=self.with_context(
            default_partner_id=payment_partner_id or inv_obj.partner_id.id,
            default_amount=amount,
            default_name=inv_obj.name,
            close_after_process=True,
            invoice_type=inv_obj.type,
            invoice_id=inv_obj.id,
            journal_id=bank_journal_ids[0],
            default_type='payment'
        )
#        print "context.......",context
        date = fields.Date.context_today(self)
        payment_method_id = self.env['account.payment.method'].search([('payment_type', '=', 'outbound')], limit=1).id
        # For using payment of customer instead of contact
        payment_data = {
                'period_id': inv_obj.period_id.id,
                'partner_id': payment_partner_id,
                'journal_id': bank_journal_ids[0],
                'currency_id': inv_obj.currency_id.id,
                'reference': inv_obj.name or '',   #payplan.name +':'+salesname
                'amount': amount,
                'payment_type': 'outbound',
                'state': 'draft',
                'name': '',
                'date': inv_obj.date_invoice or fields.Date.context_today(self),
                'company_id': inv_obj.company_id and inv_obj.company_id.id or False,
                'payment_method_id':payment_method_id,
                'partner_type':'supplier',
                'invoice_ids': [(4, inv_obj.id, None)],
        }
        
        if not payment_data['period_id']:
            self=self.with_context(company_id=inv_obj.company_id and inv_obj.company_id.id or False)
            period_ids = period_obj.find(inv_obj.date_invoice)
            period_id = period_ids and period_ids[0] or False
            payment_data.update({'period_id':period_id})
        #print "context......",context
#        print "voucher_data.aaa.......",voucher_data
        payment_id = payment_obj.create(payment_data)
#        print "voucher_id......",voucher_id

        payment_id.post()
        #aaa
        return payment_id.id






