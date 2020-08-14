from odoo import fields,models,api
from odoo.tools.translate import _
from odoo import tools
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import time
from odoo import netsvc
from odoo import SUPERUSER_ID
import odoo
from odoo import api
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class cancel_multi_event_wizard(models.TransientModel):
    """ A wizard to cancel event send mail to customer """
    _name = 'cancel.multiple.event.wizard'

    @api.multi
    def multiple_cancel_event(self):
        ''' function to cancel event and cancel Allocation History and send mail'''
        _logger.info('--------------I am in cancel_event()--------------')
        self = self.with_context(interpreter=True)
        res = []
        mod_obj = self.env['ir.model.data']
        cur_obj = self
        # event = cur_obj.event_id
        _logger.info(" >> >> >> multiple_cancel_event >> >> % s >> >> ",cur_obj.event_id)
        for event in cur_obj.event_id:
            if event:
                cancel_state = event.state
                _logger.info('--------------event cancel state ----%s--------------', cancel_state)
                _logger.info('--------------I am in cancelled event with event id%s--------------', event)
                if event.event_type == 'language':
                    if event.history_id:
                        for history in event.history_id:
                            history.write({'state': 'cancel', 'cancel_date': time.strftime('%Y-%m-%d %H:%M:%S')})
                            _logger.info('--------------I am in cancelled event with history%s--------------', history)
                elif event.event_type == 'transport':
                    if event.history_id2:
                        event.history_id2.write({'state': 'cancel'})
                elif event.event_type == 'translation':
                    if event.history_id3:
                        event.history_id3.write({'state': 'cancel'})
                elif event.event_type == 'lang_trans':
                    if event.history_id:
                        for history in event.history_id:
                            history.write({'state': 'cancel'})
                    if event.history_id2:
                        event.history_id2.write({'state': 'cancel'})

                if event.state == 'unbilled':
                    _logger.info('--------------I am in cancelled event in unbilled%s--------------', event.state)
                    pool_obj = odoo.registry(self._cr.dbname)
                    with pool_obj.cursor() as cr:
                        env = api.Environment(cr, SUPERUSER_ID, {})
                        if event.cust_invoice_id:
                            data_inv = env['account.invoice'].browse(event.cust_invoice_id.id).read(['state'])
                            for record in data_inv:
                                if record['state'] in ('cancel', 'paid'):
                                    raise UserError(_(
                                        "Selected invoice(s) cannot be cancelled as they are already in 'Cancelled' or 'Done' state."))
                                self.env['account.invoice'].browse(record['id']).action_invoice_cancel()
                        if event.supp_invoice_ids:
                            for interpreter_invoice in event.supp_invoice_ids:
                                data_inv = env['account.invoice'].browse(interpreter_invoice.id).read(['state'])
                                for record in data_inv:
                                    if record['state'] in ('cancel', 'paid'):
                                        raise UserError(_(
                                            "Selected invoice(s) cannot be cancelled as they are already in 'Cancelled' or 'Done' state."))
                                    self.env['account.invoice'].browse(record['id']).action_invoice_cancel()
                if event.task_id:
                    #                    pool_stage = pool_obj.get('project.task.type').search(cr, uid, [('state','=','cancelled')], context=context)
                    #                    stage_id = pool_stage[0] if pool_stage else 8
                    #                    event.task_id.write({'stage_id': stage_id})
                    event.task_id.sudo().unlink()
                # cancel_state=event.state
                # _logger.info('--------------event cancel state ----%s--------------',cancel_state)
                cancel_event_note=cur_obj.event_note+ '\n\n' +event.event_note
                res = event.write({'cancel_reason_id': cur_obj.cancel_reason_id and cur_obj.cancel_reason_id.id or False,
                                   'state': 'cancel','event_note':cancel_event_note})
                _logger.info('--------------I am in cancelled event in res%s--------------', res)
                template_id = mod_obj.get_object_reference('bista_iugroup', 'cancellation_event')[1]
                _logger.info('--------------I am in cancelled event template---%s--------------', template_id)
                _logger.info('--------------event state ----%s--------------', event.state)
                ############### SMS for event cancellation ##########
                if cancel_state == 'confirmed':
                    try:
                        _logger.info('--------------I am in cancelled event in confirmed%s--------------', event.state)
                        select_template_body = None
                        sms_template_obj = self.env['sms.template.twilio']
                        get_template_event_cancel = sms_template_obj.search([('action_for', '=', 'event_cancel')])
                        get_contact_cust = event.ordering_contact_id.phone
                        get_interp_contact = event.assigned_interpreters[0].phone
                        event_time_start = event.event_start_hr + ':' + event.event_start_min + event.am_pm
                        event_time_end = event.event_end_hr + ':' + event.event_end_min + event.am_pm2
                        select_template_body = get_template_event_cancel.sms_text
                        if event.ordering_contact_id.opt_for_sms:
                            if get_contact_cust:
                                if event.event_start_date:
                                    event_start_date = event.event_start_date.split('-')[1] + '/' + \
                                                       event.event_start_date.split('-')[2] + '/' + \
                                                       event.event_start_date.split('-')[0]
                                else:
                                    event_start_date = event.event_start_date
                                sms_vals = {
                                    'sms_body': select_template_body % (event.name, event_start_date,
                                                                        event_time_start, event_time_end,
                                                                        event.location_id.state_id.name,
                                                                        event.location_id.city,
                                                                        event.location_id.zip),
                                    'sms_to': get_contact_cust
                                }
                                self.env['twilio.sms.send'].create(sms_vals)
                        if event.assigned_interpreters[0].opt_for_sms:
                            if get_cancel_stateinterp_contact:
                                if event.event_start_date:
                                    event_start_date = event.event_start_date.split('-')[1] + '/' + \
                                                       event.event_start_date.split('-')[2] + '/' + \
                                                       event.event_start_date.split('-')[0]
                                else:
                                    event_start_date = event.event_start_date
                                sms_vals = {
                                    'sms_body': select_template_body % (event.name, event_start_date,
                                                                        event_time_start, event_time_end,
                                                                        event.location_id.state_id.name,
                                                                        event.location_id.city,
                                                                        event.location_id.zip),
                                    'sms_to': get_interp_contact
                                }
                                self.env['twilio.sms.send'].create(sms_vals)
                    except Exception:
                        pass
                        _logger.info('--------------I am in going to send cancelled mail--------------')
                        res = event.sudo().action_mail_send(event, 'event', template_id)
                        _logger.info('--------------I have send the cancelled mail%s--------------', res)
                if cancel_state == 'confirmed' or cancel_state == 'allocated':
                    mail_send = self.env['mail.template'].browse(template_id).with_context(
                        recipient_ids=event.ordering_contact_id).cancel_send_mail(event.id, force_send=True)
                    for ass in event.assigned_interpreters:
                        mail_send_1 = self.env['mail.template'].browse(template_id).with_context(
                            recipient_ids=ass.email).cancel_send_mail(event.id, force_send=True)
                        _logger.info('--------------I have send the cancelled mail send---%s--------------', mail_send_1)
            _logger.info('--------------I have returning the res-----%s--------------', res)
        return res

    @api.model
    def default_get(self, fields):
        res = {}
        res = super(cancel_multi_event_wizard, self).default_get(fields)
        print
        self.id
        event_ids = self._context.get('active_ids', [])
        _logger.info(">>>>>>>>>>>>>cancel event %s>>", event_ids)
        event_list = []
        company_id = 0
        if not event_ids:
            return res
        for eve in event_ids:
            event = self.env['event'].browse(eve)
            if company_id == 0:
                company_id = event.company_id.id
            else:
                if company_id != event.company_id.id:
                    raise UserError(
                        'We cannot cancel events of different companies,please selected all event having same company')
            event_list.append(event.id)
            # event_id, = event_ids
        if 'event_id' in fields:
            res.update({'event_id': [(6, 0, event_list)]})
        if 'company_id' in fields:
            res.update(company_id=company_id if company_id else False)
        return res

    cancel_reason_id = fields.Many2one('cancel.reason', 'Cancel Reason')
    event_id = fields.Many2many("event", string="Event Id")
    company_id = fields.Many2one("res.company", "Company Id")
    event_note=fields.Text("Event Note")

class cancel_event_wizard(models.TransientModel):
    """ A wizard to cancel event send mail to customer """
    _name = 'cancel.event.wizard'

    @api.multi
    def cancel_event(self):
        ''' function to cancel event and cancel Allocation History and send mail'''
        _logger.info('--------------I am in cancel_event()--------------')
        self=self.with_context(interpreter=True)
        res= []
        mod_obj = self.env['ir.model.data']
        cur_obj = self
        event = cur_obj.event_id
        if event:
            cancel_state=event.state
            _logger.info('--------------event cancel state ----%s--------------',cancel_state)
            _logger.info('--------------I am in cancelled event with event id%s--------------',event)
            if event.event_type == 'language':
                if event.history_id:
                    for history in event.history_id:
                        history.write({'state':'cancel','cancel_date':time.strftime('%Y-%m-%d %H:%M:%S')})
                        _logger.info('--------------I am in cancelled event with history%s--------------',history)
            elif event.event_type == 'transport':
                if event.history_id2:
                    event.history_id2.write({'state':'cancel'})
            elif event.event_type == 'translation':
                if event.history_id3:
                    event.history_id3.write({'state':'cancel'})
            elif event.event_type == 'lang_trans':
                if event.history_id:
                    for history in event.history_id:
                        history.write({'state':'cancel'})
                if event.history_id2:
                    event.history_id2.write({'state':'cancel'} )

            if event.state == 'unbilled':
                _logger.info('--------------I am in cancelled event in unbilled%s--------------',event.state)
                pool_obj = odoo.registry(self._cr.dbname)
                with pool_obj.cursor() as cr:
                    env = api.Environment(cr, SUPERUSER_ID, {})
                    if event.cust_invoice_id:
                        data_inv = env['account.invoice'].browse(event.cust_invoice_id.id).read(['state'])
                        for record in data_inv:
                            if record['state'] in ('cancel','paid'):
                                raise UserError(_("Selected invoice(s) cannot be cancelled as they are already in 'Cancelled' or 'Done' state."))
                            self.env['account.invoice'].browse(record['id']).action_invoice_cancel()
                    if event.supp_invoice_ids:
                        for interpreter_invoice in event.supp_invoice_ids:
                            data_inv = env['account.invoice'].browse(interpreter_invoice.id).read(['state'])
                            for record in data_inv:
                                if record['state'] in ('cancel','paid'):
                                    raise UserError(_("Selected invoice(s) cannot be cancelled as they are already in 'Cancelled' or 'Done' state."))
                                self.env['account.invoice'].browse(record['id']).action_invoice_cancel()
            if event.task_id:
#                    pool_stage = pool_obj.get('project.task.type').search(cr, uid, [('state','=','cancelled')], context=context)
#                    stage_id = pool_stage[0] if pool_stage else 8
#                    event.task_id.write({'stage_id': stage_id})
                        event.task_id.sudo().unlink()
            #cancel_state=event.state
            #_logger.info('--------------event cancel state ----%s--------------',cancel_state)
            res = event.write({'cancel_reason_id': cur_obj.cancel_reason_id and cur_obj.cancel_reason_id.id or False,
                                'state':'cancel'})
            _logger.info('--------------I am in cancelled event in res%s--------------',res)
            template_id = mod_obj.get_object_reference('bista_iugroup', 'cancellation_event')[1]
            _logger.info('--------------I am in cancelled event template---%s--------------',template_id)
            _logger.info('--------------event state ----%s--------------',event.state) 
            ############### SMS for event cancellation ##########
            if cancel_state == 'confirmed':
                try:
                    _logger.info('--------------I am in cancelled event in confirmed%s--------------',event.state)
                    select_template_body = None
                    sms_template_obj = self.env['sms.template.twilio']
                    get_template_event_cancel = sms_template_obj.search([('action_for','=','event_cancel')])
                    get_contact_cust = event.ordering_contact_id.phone
                    get_interp_contact = event.assigned_interpreters[0].phone
                    event_time_start = event.event_start_hr+':'+event.event_start_min+event.am_pm
                    event_time_end = event.event_end_hr+':'+event.event_end_min+event.am_pm2
                    select_template_body = get_template_event_cancel.sms_text
                    if event.ordering_contact_id.opt_for_sms:
                        if get_contact_cust:
                            if event.event_start_date:
                                event_start_date = event.event_start_date.split('-')[1] + '/' + \
                                                   event.event_start_date.split('-')[2] + '/' + \
                                                   event.event_start_date.split('-')[0]
                            else:
                                event_start_date = event.event_start_date
                            sms_vals = {
                                        'sms_body': select_template_body%(event.name,event_start_date,
                                                                      event_time_start,event_time_end,
                                                                      event.location_id.state_id.name,event.location_id.city,
                                                                      event.location_id.zip),
                                        'sms_to': get_contact_cust
                                    }
                            self.env['twilio.sms.send'].create(sms_vals)
                    if event.assigned_interpreters[0].opt_for_sms:
                        if get_cancel_stateinterp_contact:
                            if event.event_start_date:
                                event_start_date = event.event_start_date.split('-')[1] + '/' + \
                                                   event.event_start_date.split('-')[2] + '/' + \
                                                   event.event_start_date.split('-')[0]
                            else:
                                event_start_date = event.event_start_date
                            sms_vals = {
                                        'sms_body': select_template_body%(event.name,event_start_date,
                                                                      event_time_start,event_time_end,
                                                                      event.location_id.state_id.name,event.location_id.city,
                                                                      event.location_id.zip),
                                        'sms_to': get_interp_contact
                                    }
                            self.env['twilio.sms.send'].create(sms_vals)
                except Exception:
                    pass
                    _logger.info('--------------I am in going to send cancelled mail--------------')
                    res = event.sudo().action_mail_send(event, 'event', template_id)
                    _logger.info('--------------I have send the cancelled mail%s--------------',res)
            if cancel_state == 'confirmed' or  cancel_state == 'allocated':
                mail_send=self.env['mail.template'].browse(template_id).with_context(recipient_ids= event.ordering_contact_id).cancel_send_mail(event.id, force_send=True)
                for ass in event.assigned_interpreters:
                    mail_send_1 = self.env['mail.template'].browse(template_id).with_context(
                        recipient_ids=ass.email).cancel_send_mail(event.id, force_send=True)
                    _logger.info('--------------I have send the cancelled mail send---%s--------------',mail_send_1)  
        _logger.info('--------------I have returning the res-----%s--------------',res)
        return res

    @api.model
    def default_get(self, fields):
        res = {}
        res = super(cancel_event_wizard , self).default_get(fields)
        print self.id
        event_ids = self._context.get('active_ids', [])
        if not event_ids or len(event_ids) != 1:
            return res
        event = self.env['event'].browse(event_ids[0])
        event_id, = event_ids
        if 'event_id' in fields:
            res.update(event_id = event_id)
        if 'company_id' in fields:
            res.update(company_id = event.company_id and event.company_id.id)
        return res


    cancel_reason_id=fields.Many2one('cancel.reason', 'Cancel Reason')
    event_id=fields.Many2one("event", "Event Id" )
    company_id=fields.Many2one("res.company", "Company Id")
