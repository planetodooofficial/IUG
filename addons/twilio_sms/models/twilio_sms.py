# -*- coding: utf-8 -*-
from twilio.rest.exceptions import TwilioRestException
from twilio.rest import TwilioRestClient

from odoo.exceptions import UserError, RedirectWarning, ValidationError
from odoo import fields, models,api,_
import time
from odoo import SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)

class sms_configuration(models.Model):
    _name = 'twilio.accounts'
    _description = 'Twilio Configuration'

    name=fields.Char('Name', required=True)
    account_sid=fields.Char('Account SID', required=True)
    auth_token=fields.Char('Auth Token', required=True)
    from_number=fields.Char('From Number', required=True)
    priority=fields.Integer('Priority',default=10)
    active=fields.Boolean('Active',default=True)
    callback_status_url=fields.Char('Callback Server', required=True)

    @api.model
    def get_twilio_client(self, account_id=None):
        # select hightest priority account
        if not account_id:
            account_id = self.search([], order='priority', limit=1)
        if not account_id:
            raise UserError(_("There is no Twilio account configured."))
            # pass    # NOTE: raise error
        return TwilioRestClient(account_id.account_sid, account_id.auth_token)

    @api.model
    def get_account_id(self,account_sid=None):
        if account_sid:
            return self.search([('account_sid', '=', account_sid)], limit=1).id
        data = self.search([], limit=1)
        return data.id


class twilio_sms_send(models.Model):
    _name = 'twilio.sms.send'
    _inherit = ['mail.thread']
    _description = 'Twilio SMS send'

    sms_from=fields.Char(related='account_id.from_number', string='From', store=True,)
    sms_to=fields.Char('To', required=True, track_visibility='always')
    sms_body=fields.Text('Body', track_visibility='always')
    message_sid=fields.Char('Message SID', readonly=True, oldname='message_id')
    direction=fields.Char('Direction', readonly=True)
    price=fields.Char('Price', readonly=True)
    price_unit=fields.Char('Price Unit', readonly=True)
    error_msg=fields.Char('Error', readonly=True)
    error_code=fields.Char('Error Code', readonly=True)
    # twilio configuration fields
    account_id=fields.Many2one('twilio.accounts', 'Account', index=True)
    account_sid=fields.Char('Account SID', readonly=True)
    # 'status': fields.char('Status', readonly=True, track_visibility='onchange')
    status=fields.Selection([
        ('accepted', 'Accepted'),
        ('queued', 'Queued'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('receiving', 'Receiving'),
        ('received', 'Received'),
        ('delivered', 'Delivered'),
        ('undelivered', 'Undelivered'),
        ('failed', 'Failed')], 'SMS Status',
        readonly=True, track_visibility='onchange')


    @api.onchange('account_id')
    def onchange_account_id(self):
        if self.account_id:
            values = {
                'sms_from': self.account_id.from_number
            }
        else:
            values = {
                'sms_from': False
            }
        return {'value': values}

    @api.model
    def send_sms(self,body, to, from_=None, account_id=None):
        twilio_account_obj = self.env['twilio.accounts']
        if not account_id:
            account_id = twilio_account_obj.get_account_id(False)
        if not from_ and not account_id:
            raise UserError(_("Missing from number."))
        #if account_id and not from_:
        account = twilio_account_obj.browse(account_id)
        from_ = account.from_number
        try:
            client = twilio_account_obj.get_twilio_client(account)
            callback_url = account.callback_status_url + '/twilio_sms/message_status'
            # message = client.messages.create(
            #     body=body,
            #     to=to,
            #     from_=from_,
            #     StatusCallback='http://a8feba80.ngrok.io/twilio_sms/message_status')
            message = client.messages.create(
                body=body,
                to=to,
                from_=from_,
                StatusCallback=callback_url)
            return message
            # except Exception as e:
            #     raise e
        except TwilioRestException as e:
            raise UserError(_('Error Code: ' + str(e.code) + '\n Error Message: ' + e.msg))
        # TODO: track error logs if message is not sent to twilio
        # return message

    @api.model
    def create(self, vals):
        """ create sms and send to twilio
        """
        try:
            account_id = vals.get('account_id',None)
            sms_body = vals.get('sms_body', '')
            sms_to = vals.get('sms_to',None)
            sms_from = vals.get('sms_from',None)
            if not account_id:
                twilio_account_obj = self.env['twilio.accounts']
                account_id = twilio_account_obj.get_account_id(False)
            message = self.send_sms(sms_body, sms_to, sms_from, account_id)
            msg_send_id = super(twilio_sms_send, self).create(vals)
            self._cr.commit()
          #  if type(message) is not bool and message.exists():
            # NOTE: prepare vals for successful send sms
            update_vals = {
                'message_sid': message.sid,
                'account_id': account_id,
                'account_sid': message.account_sid,
                'direction': message.direction,
                'status': message.status,
                'price': message.price,
                'price_unit': message.price_unit,
                'error_msg': message.error_message,
                'error_code': message.error_code,
            }
            msg_send_id.write(update_vals)
            self._cr.commit()
            return msg_send_id
        except TwilioRestException as e:
            #raise e
            raise UserError(_('Error Code: ' + str(e.code) + '\n Error Message: ' + e.msg))


class twilio_sms_received(models.Model):
    _name = 'twilio.sms.received'
    _inherit = ['mail.thread']
    _description = 'Twilio SMS Received'

    sms_from=fields.Char('From', track_visibility='always')
    sms_to=fields.Char('To', required=True, readonly=False, track_visibility='always',default='+16193041829')
    sms_body=fields.Text('Body', readonly=False, track_visibility='always')
    # account id should be many2one
    account_sid=fields.Char('Account SID', readonly=False)
    account_id=fields.Many2one('twilio.accounts', 'Account', readonly=False)
    service_sid=fields.Char('Service SID', readonly=False, oldname='service_id')
    message_sid=fields.Char('Message SID', readonly=False, oldname='message_id')
    status=fields.Selection([
        ('accepted', 'Accepted'),
        ('queued', 'Queued'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('receiving', 'Receiving'),
        ('received', 'Received'),
        ('delivered', 'Delivered'),
        ('undelivered', 'Undelivered'),
        ('failed', 'Failed')], 'SMS Status',
        readonly=True, track_visibility='onchange')
    # sender identity fields
    from_zip=fields.Char('From Zip', readonly=True)
    from_city=fields.Char('From City', readonly=True)
    from_state=fields.Char('From State', readonly=True)
    from_country=fields.Char('From Country', readonly=True)
    # received identity fields
    to_zip=fields.Char('To Zip', readonly=True)
    to_city=fields.Char('To City', readonly=True)
    to_state= fields.Char('To State', readonly=True)
    to_country=fields.Char('To Country', readonly=True)
    # extra fields for the API
    api_version=fields.Char('Api Version', readonly=True)

    @api.multi
    def send_sms_to_interp_scheduled_job(self,event_id):
        interp_template_body_ = None
        get_interp_template = None
        sms_template_obj = self.env['sms.template.twilio']
        event_obj = self.env['event']
        if self._context.get('scheduled_interp', False):
            get_interp_template = sms_template_obj.search([('action_for', '=', 'interp_scheduled')])
        for template_ids in get_interp_template:
            interp_template_body_ = template_ids.sms_text
        event_data = event_obj.browse(event_id)
        event_time_start = event_data.event_start_hr + ':' + event_data.event_start_min + event_data.am_pm
        event_time_end = event_data.event_end_hr + ':' + event_data.event_end_min + event_data.am_pm2
        if self._context.get('scheduled_interp', False):
            get_interp_contact = self._context.get('interpreter_phone', False)
            if get_interp_contact:
                if event_data.event_start_date:
                    event_start_date = event_data.event_start_date.split('-')[1] + '/' + \
                                       event_data.event_start_date.split('-')[2] + '/' + \
                                       event_data.event_start_date.split('-')[0]
                else:
                    event_start_date = event_data.event_start_date
                sms_interp_vals = {
                    'sms_body': interp_template_body_ % (event_data.name, event_start_date,
                                                         event_time_start, event_time_end,
                                                         event_data.location_id.state_id.name,
                                                         event_data.location_id.city,
                                                         event_data.location_id.zip),
                    'sms_to': get_interp_contact
                }
                self.env['twilio.sms.send'].create(sms_interp_vals)
            else:
                pass

    @api.model
    def create(self,vals):
        import re
        event_obj = self.env['event']
        interp_line = self.env['select.interpreter.line']
        partner_obj = self.env['res.partner']
        interp_contact_browsed = []
        interp_contact_delayed = []
        res = super(twilio_sms_received, self).create(vals)
        self._cr.commit()
        get_content = res
        content = re.sub(r'\s+', '', get_content.sms_body)
        l_sms = content.upper()

        if 'Y' in l_sms or 'N' in l_sms:
            if 'Y' in l_sms:
                char = 'Y'
            elif 'N' in l_sms:
                char = 'N'
            if l_sms.find(char) == len(l_sms)-1:
                l_sms = char + l_sms[:-1]

        body = l_sms[0]+" "+l_sms[1:]

        fetched = body.split()
        incorrect_reply = False
        if len(fetched) != 2:
            incorrect_reply = True
        elif "Y" != fetched[0] and 'N' != fetched[0]:
            incorrect_reply = True
        else:
            valideventname = re.findall(r'[A-Z]+|\d+', fetched[1])
            if len(valideventname) != 2:
                incorrect_reply = True
            else:
                if 'E' != valideventname[0]:
                    incorrect_reply = True
                elif not valideventname[1].isdigit():
                    incorrect_reply = True
        if incorrect_reply:
            sms_interp_vals = {
                'sms_body': """We received a message from you in an incorrect format.The correct format is for eg-'Y E987687' to accept the job offer for the event E987687 and 'N E987687' to reject the job offer for the event E987687""",
                'sms_to': get_content.sms_from
            }
            self.env['twilio.sms.send'].create(sms_interp_vals)
            return res
        update_format = map(int, re.findall(r'\d+', get_content.sms_from))
        num = ''.join(str(form) for form in update_format)
        updated_num = "+"+num
        num_split = updated_num[:2]+'-'+updated_num[2:5]+'-'+updated_num[5:8]+'-'+updated_num[8:]
        interpreter = partner_obj.search([('cust_type', '=', 'interpreter'), '|', ('phone', '=', num_split), ('phone', '=', updated_num)])
        if len(fetched) == 2:
            _logger.info("------------------------I am in fetched------------------------%s",len(fetched))
	    reply = fetched[0]
            event_name = fetched[1]
            if len(interpreter) == 1:
                interp_company = interpreter[0].company_id.id
                event_id = event_obj.search([('name', '=', event_name), ('company_id', '=', interp_company)],limit=1)
            else:
                for interp in interpreter:
                    interp_company = interp.company_id.id
                    check_event = event_obj.search([('name', '=', event_name), ('company_id', '=', interp_company)],limit=1)
                    if check_event:
                        interp_exist = interp_line.search([('event_id', '=', check_event.id), ('interpreter_id', '=', interp.id)],limit=1)
                        if interp_exist:
                            event_id=check_event

            event_rec = event_id
            if event_rec.state == 'scheduled' and not event_rec.assigned_interpreters:
                event_rec.write({'no_editable': True})
                self._cr.commit()
                job_offered_interp_lines = interp_line.search([('event_id', '=', event_id.id), ('state', '!=', 'cancel'), ('state', '=', 'voicemailsent')])
                for line_id in job_offered_interp_lines:
                    interp_contact_browsed.append({'phone': line_id.interpreter_id.phone or False,
                                                    'line_id': line_id.id})
                    # Need to add condition for more then one contact
            elif len(event_rec.assigned_interpreters) != 0:
                job_offered_interp_lines = interp_line.search([('event_id', '=', event_id.id), ('state', '!=', 'cancel'), ('state', '=', 'voicemailsent')])
                for line_id in job_offered_interp_lines:
                    interp_contact_delayed.append({'phone': line_id.interpreter_id.phone or False,
                                                   'line_id': line_id.id})
            if interp_contact_browsed:
                if reply == 'Y':
                    for data in interp_contact_browsed:
                        _logger.info('------------------twilio data-------------------%s',data)
                        if data['phone']:
                            update_format_interp_mob = map(int, re.findall(r'\d+', str(data['phone'])))
                            str1 = ''.join(str(e) for e in update_format_interp_mob)
                            updated_num_interp_mob = "+"+str1
                            if updated_num_interp_mob.startswith('+1'):
                                pass
                            else:
                                updated_num_interp_mob = updated_num_interp_mob[0] + "1" + updated_num_interp_mob[1:]
                            if updated_num_interp_mob == updated_num:
                                fields = ['event_id', 'history_id', 'interpreter_id', 'interpreter_ids']
                                
                                assign_interp = self.env['assign.interp.wizard'].with_context(lang='en_US',active_ids=[data['line_id']], tz='US/Pacific', uid=1).default_get(fields=fields)
                                wiz = self.env['assign.interp.wizard'].create(assign_interp)
                                

                                wiz.with_context(active_id=data['line_id'], accepted_from='sms', event_id=event_id[0]).update_interpreter()
                                try:
                                    if interp_line.browse(data['line_id']).interpreter_id.opt_for_sms:
                                        
                                        self.with_context(scheduled_interp=True, interpreter_phone=updated_num).send_sms_to_interp_scheduled_job(event_id.id)
                                except Exception:
                                    pass

                if reply == 'N':
                    for data in interp_contact_browsed:
                        if data['phone']:
                            update_format_interp_mob = map(int, re.findall(r'\d+', str(data['phone'])))
                            str1 = ''.join(str(e) for e in update_format_interp_mob)
                            updated_num_interp_mob = "+"+str1
                            if updated_num_interp_mob.startswith('+1'):
                                pass
                            else:
                                updated_num_interp_mob = updated_num_interp_mob[0] + "1" + updated_num_interp_mob[1:]
                            if updated_num_interp_mob == updated_num:
                                mod_obj = self.env['ir.model.data']
                                interp_line_obj = self.env['select.interpreter.line']
                                cur_obj = interp_line_obj.browse(data['line_id'])
                                lines_state = []
                                event = event_rec
                                user = self.env.user
                                if not event.history_id:
                                    self.env['interpreter.alloc.history'].create({'partner_id': event.partner_id and event.partner_id.id or False, 'name': cur_obj.interpreter_id and cur_obj.interpreter_id.id or False,
                                            'event_id':event.id, 'event_date': event.event_date, 'event_start': event.event_start, 'event_end': event.event_end, 'state': 'cancel', 'company_id': event.company_id and event.company_id.id or False,
                                            'cancel_date': time.strftime('%Y-%m-%d %H:%M:%S')})
                                else:
                                    for history in event.history_id:
                                        if history.name.id == cur_obj.interpreter_id.id and history.state == 'allocated':
                                            history.write({'partner_id':event.partner_id and event.partner_id.id or False,'name': cur_obj.interpreter_id and cur_obj.interpreter_id.id or False,
                                                    'event_id':event.id, 'event_date': event.event_date, 'event_start':event.event_start,'event_end':event.event_end,'state':'cancel','company_id': event.company_id and event.company_id.id or False,
                                                    'cancel_date':time.strftime('%Y-%m-%d %H:%M:%S')})
                                cur_obj.write({'state': 'cancel'})
                                event.sudo().write({'event_follower_ids': [(3, cur_obj.interpreter_id.user_id.id)]})
                                subject = ""
                                if cur_obj.interpreter_id and cur_obj.interpreter_id.user_id:
                                    if cur_obj.interpreter_id.has_login:
                                        subject = "Interpreter Declined"
                                details = "Interpreter %s has declined job." % (cur_obj.interpreter_id and cur_obj.interpreter_id.complete_name or False)
                                if user.user_type not in ('staff', 'admin'):
                                    event.sudo().message_post(body=details, subject=subject)
                                else:
                                    event.message_post(body=details, subject=subject)
                                if not event.assigned_interpreters:
                                    for each_line in event.interpreter_ids2:
                                        lines_state.append(each_line.state)
                                    if lines_state and len(list(set(lines_state))) == 1 and list(set(lines_state))[0] == 'cancel':
                                        event_id.sudo().write({'state': 'draft'})
                                if user.user_type and user.user_type == 'vendor':
                                    res = mod_obj.sudo().get_object_reference('bista_iugroup', 'view_event_user_tree')
                                    res_id = res and res[1] or False,
                                    self=self.with_context(event_id=event_id.id)
                                    event_id.write({'no_editable': False})
                                    self._cr.commit()
                                    return res
                                    # To be fix
                                    # return {
                                    #     'name': _('Event'),
                                    #     'view_type': 'form',
                                    #     'view_mode': 'tree',
                                    #     'view_id': [res_id[0]],
                                    #     'res_model': 'event',
                                    #     'type': 'ir.actions.act_window',
                                    #     'nodestroy': True,
                                    #     'target': 'current',
                                    # }

            if interp_contact_delayed:
		 _logger.info("------------------------I am in interp_contact_delayed------------------------%s",interp_contact_delayed)
		 if reply == 'Y':
                    for data_delay in interp_contact_delayed:
                        if data_delay['phone']:
                            _logger.info("------------------------I am in data_delay------------------------%s",data_delay['phone'])
			   # update_format_interp_mob = map(int, re.findall(r'\d+', str(data_delay['phone'])))
                            #str1 = ''.join(str(e) for e in update_format_interp_mob)
                            #updated_num_interp_mob = "+"+str1
                            updated_num_interp_mob=data_delay['phone'].replace("-","")
                            _logger.info("------------------------I am updated_num_interp_mob------------------------%s",updated_num_interp_mob)
                            if updated_num_interp_mob.startswith('+1'):
                                _logger.info("------------------------I am in if updated_num_interp_mob------------------------")
		                pass
                            else:
                                updated_num_interp_mob = updated_num_interp_mob[0] + "1" + updated_num_interp_mob[1:]
                                _logger.info("------------------------I am in else updated_num_interp_mob------------------------%s",updated_num_interp_mob)
                            if updated_num_interp_mob == updated_num:
                                _logger.info("------------------------I am in updated_num_interp_mob == updated_num------------------------")
                                if interp_line.browse(data_delay['line_id']).interpreter_id.opt_for_sms:
				    _logger.info("---------------------I am in interpreter_id.opt_for_sms------------------------%s",interp_line.browse(data_delay['line_id']).interpreter_id.opt_for_sms)
                                    select_template_body = None
                                    sms_template_obj = self.env['sms.template.twilio']
                                    get_template_delayed_reply = sms_template_obj.search([('action_for', '=', 'delayed_reply')])
                                    for template_ids in get_template_delayed_reply:
                                        select_template_body = template_ids.sms_text
                                    event_data = event_id
                                    event_time_start = event_data.event_start_hr+':'+event_data.event_start_min+event_data.am_pm
                                    event_time_end = event_data.event_end_hr+':'+event_data.event_end_min+event_data.am_pm2
                                    sms_vals = {
                                                'sms_body': select_template_body %(event_data.name, event_data.event_start_date,
                                                                              event_time_start, event_time_end,
                                                                              event_data.location_id.state_id.name, event_data.location_id.city,
                                                                              event_data.location_id.zip),
                                                'sms_to': updated_num
                                            }
                                    self.env['twilio.sms.send'].create(sms_vals)
                                    _logger.info("------------------------I am create twilio------------------------")

        event_id.write({'no_editable':False})
        _logger.warning("------------------------I have write create twilio%s------------------------",event_id.id)
        self._cr.commit()
        return res
                                 
        
class sms_template_twilio(models.Model):
    _name = 'sms.template.twilio'
    _inherit = ['mail.thread']
    _description = 'IUG SMS Template'
    _rec_name = 'action_for'

    action_for=fields.Selection([
        ('job_offer', 'Job Offer'),
        ('assigned_interp', 'Allocated Interpreter'),
        ('assigned_customer', 'Customer Confirmation'),
        ('event_cancel', 'Event Cancellation'),
        ('delayed_reply', 'Event Unavailable'),
        ('interp_scheduled', 'Interpreter Scheduled'),
        ], 'Template For', required=True,)
    sms_text=fields.Text('Template Content', required=True,)
                


    

