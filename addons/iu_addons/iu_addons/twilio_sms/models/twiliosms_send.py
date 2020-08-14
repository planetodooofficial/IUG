from twilio import *
from odoo import SUPERUSER_ID
from odoo import models, fields, api
from twilio.rest import TwilioRestClient
from odoo.exceptions import *
import datetime
import re
import odoo.osv.osv
from datetime import datetime
import time
from twilio import TwilioRestException


class twilio_accounts(models.Model):
    _name = 'twilio.accounts'
    _description = 'Twilio Configuration'

    name = fields.Char(string='Name', required=True)
    account_sid = fields.Char(string='Account SID', required=True)
    auth_token = fields.Char(string='Auth Token', required=True)
    from_number = fields.Char(string='From Number', required=True)
    priority = fields.Integer(string='Priority',default=10)
    active = fields.Boolean(string="Active",default=True)
    callback_status_url = fields.Char(string='Callback Server', required=True)

    @api.depends('account_id')
    def get_twilio_client(self):
        # select hightest priority account
        if  account_id:
            account_id = self.search(order='priority', limit=1)#([('order', '=', priority)]), limit=1)
        if not account_id:
            raise Exception("There is no Twilio account configured.")
        sms_account = self.browse(account_id)
        return TwilioRestClient(sms_account.account_sid, sms_account.auth_token)

    @api.depends('account_sid')
    def get_account_id(self):
        if account_sid:
            return self.search([('account_sid', '=', account_sid)], limit=1)
        data = self.search(
            [], limit=1, context=context)
        return data

class twilio_sms_send(models.Model):
    _name = 'twilio.sms.send'
    _inherit = ['mail.thread']
    _description = 'Twilio SMS send'

    sms_from = fields.Related('account_id','from_number', type='char', string='From', store=True)
    sms_to = fields.Char(string="To",  required=True, track_visibility='always', help="Pls, provide your twilio number")
    sms_body = fields.Text(string='Body',size=160, track_visibility='always')
    message_sid = fields.Char(string="Message SID", readonly=True,oldname='message_id')
    direction = fields.Char(string="Direction", readonly=True)
    price = fields.Char(string="Price", readonly=True)
    price_unit = fields.Char(string="Price Unit",)
    error_msg = fields.Text(string='Error', readonly=True)
    error_code = fields.Char(string="Error Code", readonly=True)
    account_id = fields.Many2one('twilio.accounts', 'Account', select=True)
    account_sid = fields.Char(string="Account SID", readonly=True)
    status = fields.Selection([
            ('accepted', 'Accepted'),
            ('queued', 'Queued'),
            ('sending', 'Sending'),
            ('sent', 'Sent'),
            ('receiving', 'Receiving'),
            ('received', 'Received'),
            ('delivered', 'Delivered'),
            ('undelivered', 'Undelivered'),
            ('failed', 'Failed')], string = 'SMS Status',
            readonly=True, track_visibility='onchange')

    @api.onchange('account_id')
    def onchange_account_id(self):
        sms_account = self.env['twilio.accounts'].browse(account_id)
        values = {
            'sms_from': sms_account.from_number
        }
        return {'value': values}

    @api.depends('from_', 'to', 'body')
    def send_sms(self):
        twilio_account_obj = self.env['twilio.accounts']
        if not account_id:
            account_id = twilio_account_obj.get_account_id()
        if not from_ and not account_id:
            raise odoo.osv.osv.except_osv(_('Error!'), _("Missing from number."))
        if account_id and not from_:
            account = twilio_account_obj.browse(account_id)
            from_ = account.from_number
        try:
            client = twilio_account_obj.get_twilio_client()
            callback_url = account.callback_status_url + '/twilio_sms/message_status'
            message = client.messages.create(
                body=body,
                to=to,
                from_=from_,
                StatusCallback=callback_url)
            return message
        except TwilioRestException as e:
            raise osv.except_osv(_('Warning!'), _('Error Code: ' + str(e.code) + '\n Error Message: ' + e.msg))

    @api.model
    def create(self,vals):
        """ create sms and send to twilio
        """
        try:
            account_id = vals.get('account_id')
            sms_body = vals.get('sms_body', '')
            sms_to = vals.get('sms_to')
            sms_from = vals.get('sms_from')
            if not account_id:
                twilio_account_obj = self.env['twilio.accounts']
                account_id = twilio_account_obj.get_account_id()[0]
            message = self.send_sms()
            msg_send_id = super(twilio_sms_send, self).create(vals)
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
            res = super(twilio_sms_send, self).write(msg_send_id,update_vals)
            return msg_send_id
        except TwilioRestException as e:
            raise osv.except_osv(_('Warning!'), _('Error Code: ' + str(e.code) + '\n Error Message: ' + e.msg))

class Partner(models.Model):
    _inherit = 'res.partner'

    opt_for_sms = fields.Boolean(string="Opt for SMS service", default=False)



# class twilio_sms_received(models.Model):
#     _name = 'twilio.sms.received'
#     _inherit = ['mail.thread']
#     _description = 'Twilio SMS Received'
#
#     sms_from = fields.Related(string='From', track_visibility='always')
#     sms_to = fields.Char(string="To", required=True,default ='+16193041829', track_visibility='always')
#     sms_body = fields.Text(string='Body',track_visibility='always')
#     account_sid = fields.Char(string="Account SID")
#     account_id = fields.Many2one('twilio.accounts', 'Account')
#     service_sid = fields.Char(string="Service SID", oldname='service_id')
#     message_sid = fields.Char(string="Message SID", oldname='message_id' )
#     status = fields.Selection([
#         ('accepted', 'Accepted'),
#         ('queued', 'Queued'),
#         ('sending', 'Sending'),
#         ('sent', 'Sent'),
#         ('receiving', 'Receiving'),
#         ('received', 'Received'),
#         ('delivered', 'Delivered'),
#         ('undelivered', 'Undelivered'),
#         ('failed', 'Failed')], string='SMS Status',
#         readonly=True, track_visibility='onchange')
#     from_zip = fields.Char(string="From Zip", readonly=True)
#     from_city = fields.Char(string="From City", readonly=True)
#     from_state = fields.Char(string="From State", readonly=True)
#     from_country = fields.Char(string="From Country", readonly=True)
#     to_zip = fields.Char(string="To Zip", readonly=True)
#     to_city = fields.Char(string="To City", readonly=True)
#     to_state = fields.Char(string="To State", readonly=True)
#     to_country = fields.Char(string="To County", readonly=True)
#     api_version = fields.Char(string="Api Version", readonly=True)
#
#     def send_sms_to_interp_scheduled_job(self,ids, context={}):
#         interp_template_body_ = None
#         get_interp_template = None
#         sms_template_obj = self.env['sms.template.twilio']
#         event_obj = self.env['event']
#
#         if context.get('scheduled_interp', False):
#             get_interp_template = sms_template_obj.search([('action_for', '=', 'interp_scheduled')])
#         for template_ids in sms_template_obj.browse(get_interp_template):
#             interp_template_body_ = template_ids.sms_text
#         event_data = event_obj.browse(ids)
#         event_time_start = event_data.event_start_hr + ':' + event_data.event_start_min + event_data.am_pm
#         event_time_end = event_data.event_end_hr + ':' + event_data.event_end_min + event_data.am_pm2
#         if context.get('scheduled_interp', False):
#             get_interp_contact = context.get('interpreter_phone', False)
#             if get_interp_contact:
#                 sms_interp_vals = {
#                     'sms_body': interp_template_body_ % (event_data.name, event_data.event_start_date,
#                                                                event_time_start, event_time_end,
#                                                                event_data.location_id.state_id.name,
#                                                                event_data.location_id.city,
#                                                                event_data.location_id.zip),
#                     'sms_to': get_interp_contact
#                 }
#                 self.env['twilio.sms.send'].create(sms_interp_vals)
#             else:
#                 pass
#
#     def create(self,vals):
#
#         event_obj = self.env['event']
#         interp_line = self.env['select.interpreter.line']
#         partner_obj = self.env['res.partner']
#         interp_contact_browsed = []
#         interp_contact_delayed = []
#         res = super(twilio_sms_received, self).create(vals)
#         get_content = self.browse(res)
#
#         content = re.sub(r'\s+', '', get_content.sms_body)
#         l_sms = content.upper()
#
#         if 'Y' in l_sms or 'N' in l_sms:
#             if 'Y' in l_sms:
#                 char = 'Y'
#             elif 'N' in l_sms:
#                 char = 'N'
#             if l_sms.find(char) == len(l_sms) - 1:
#                 l_sms = char + l_sms[:-1]
#
#         body = l_sms[0] + " " + l_sms[1:]
#
#         fetched = body.split()
#         update_format = map(int, re.findall(r'\d+', get_content.sms_from))
#         num = ''.join(str(form) for form in update_format)
#         updated_num = "+" + num
#         num_split = updated_num[:2] + '-' + updated_num[2:5] + '-' + updated_num[5:8] + '-' + updated_num[8:]
#         interpreter = partner_obj.search([('cust_type', '=', 'interpreter'), '|', ('phone', '=', num_split),
#                                                    ('phone', '=', updated_num)])
#
#         if len(fetched) == 2:
#             reply = fetched[0]
#             event_name = fetched[1]
#             if len(interpreter) == 1:
#                 interp_company = partner_obj.browse(interpreter[0]).company_id.id
#                 event_id = event_obj.search([('name', '=', event_name), ('company_id', '=', interp_company)])
#             else:
#                 for interp in interpreter:
#                     interp_company = partner_obj.browse(interp).company_id.id
#                     check_event = event_obj.search([('name', '=', event_name), ('company_id', '=', interp_company)])
#                     if check_event:
#                         interp_exist = interp_line.search([('event_id', '=', check_event[0]),('interpreter_id', '=', interp)])
#                         if interp_exist:
#                             event_id = []
#                             event_id.append(interp_line.browse(interp_exist[0]).event_id.id)
#
#             event_rec = event_obj.browse(event_id[0])
#             if event_rec.state == 'scheduled' and not event_rec.assigned_interpreters:
#                 event_obj.write(event_id[0], {'no_editable': True})
#                 job_offered_interp_lines = interp_line.search([('event_id', '=', event_id), ('state', '!=', 'cancel'),
#                                                                ('state', '=', 'voicemailsent')])
#                 for line_id in job_offered_interp_lines:
#                     interp_contact_browsed.append(
#                         {'phone': interp_line.browse(line_id).interpreter_id.phone or False,
#                          'line_id': line_id})
#                     # Need to add condition for more then one contact
#             elif len(event_rec.assigned_interpreters) != 0:
#                 job_offered_interp_lines = interp_line.search([('event_id', '=', event_id), ('state', '!=', 'cancel'),
#                                                                ('state', '=', 'voicemailsent')])
#                 for line_id in job_offered_interp_lines:
#                     interp_contact_delayed.append(
#                         {'phone': interp_line.browse(line_id).interpreter_id.phone or False,
#                          'line_id': line_id})
#             if interp_contact_browsed:
#                 if reply == 'Y':
#                     for data in interp_contact_browsed:
#                         if data['phone']:
#                             update_format_interp_mob = map(int, re.findall(r'\d+', str(data['phone'])))
#                             str1 = ''.join(str(e) for e in update_format_interp_mob)
#                             updated_num_interp_mob = "+" + str1
#                             if updated_num_interp_mob.startswith('+1'):
#                                 pass
#                             else:
#                                 updated_num_interp_mob = updated_num_interp_mob[0] + "1" + updated_num_interp_mob[1:]
#                         if updated_num_interp_mob == updated_num:
#                             fields = ['event_id', 'history_id', 'interpreter_id', 'interpreter_ids']
#                             context = {'lang': 'en_US', 'active_ids': [data['line_id']], 'tz': 'US/Pacific', 'uid': 1}
#                             assign_interp = self.pool.get('assign.interp.wizard').default_get(cr, uid, fields=fields,
#                                                                                               context=context)
#                             wiz = self.pool.get('assign.interp.wizard').create(cr, uid, assign_interp, context=None)
#                             context.update(
#                                 {'active_id': data['line_id'], 'accepted_from': 'sms', 'event_id': event_id[0]})
#                             self.env['assign.interp.wizard'].update_interpreter([wiz],context)
#                             try:
#                                 if interp_line.browse(data['line_id']).interpreter_id.opt_for_sms:
#                                     self.send_sms_to_interp_scheduled_job(event_id[0],
#                                                                           context={'scheduled_interp': True,
#                                                                                    'interpreter_phone': updated_num})
#                             except Exception:
#                                 pass
#
#                 if reply == 'N':
#                     for data in interp_contact_browsed:
#                         if data['phone']:
#                             update_format_interp_mob = map(int, re.findall(r'\d+', str(data['phone'])))
#                             str1 = ''.join(str(e) for e in update_format_interp_mob)
#                             updated_num_interp_mob = "+" + str1
#                             if updated_num_interp_mob.startswith('+1'):
#                                 pass
#                             else:
#                                 updated_num_interp_mob = updated_num_interp_mob[0] + "1" + updated_num_interp_mob[1:]
#                         if updated_num_interp_mob == updated_num:
#                             mod_obj = self.env['ir.model.data']
#                             interp_line_obj = self.env['select.interpreter.line']
#                             cur_obj = interp_line_obj.browse(data['line_id'])
#                             lines_state = []
#                             event = event_obj.browse(event_id[0])
#                             user = self.pool.get('res.users').browse(SUPERUSER_ID)
#                             if not event.history_id:
#                                 self.env['interpreter.alloc.history'].create({
#                                     'partner_id': event.partner_id and event.partner_id.id or False,
#                                     'name': cur_obj.interpreter_id and cur_obj.interpreter_id.id or False,
#                                     'event_id': event.id, 'event_date': event.event_date,
#                                     'event_start': event.event_start, 'event_end': event.event_end, 'state': 'cancel',
#                                     'company_id': event.company_id and event.company_id.id or False,
#                                     'cancel_date': time.strftime('%Y-%m-%d %H:%M:%S')})
#                             else:
#                                 for history in event.history_id:
#                                     if history.name.id == cur_obj.interpreter_id.id and history.state == 'allocated':
#                                         self.env['interpreter.alloc.history'].write( history.id, {
#                                             'partner_id': event.partner_id and event.partner_id.id or False,
#                                             'name': cur_obj.interpreter_id and cur_obj.interpreter_id.id or False,
#                                             'event_id': event.id, 'event_date': event.event_date,
#                                             'event_start': event.event_start, 'event_end': event.event_end,
#                                             'state': 'cancel',
#                                             'company_id': event.company_id and event.company_id.id or False,
#                                             'cancel_date': time.strftime('%Y-%m-%d %H:%M:%S')})
#                             interp_line_obj.write(data['line_id'], {'state': 'cancel'})
#                             event_obj.write( SUPERUSER_ID, event_id,
#                                             {'event_follower_ids': [(3, cur_obj.interpreter_id.user_id.id)]})
#                             subject = ""
#                             if cur_obj.interpreter_id and cur_obj.interpreter_id.user_id:
#                                 if cur_obj.interpreter_id.has_login:
#                                     subject = "Interpreter Declined"
#                             details = "Interpreter %s has declined job." % (
#                                         cur_obj.interpreter_id and cur_obj.interpreter_id.complete_name or False)
#                             if user.user_type not in ('staff', 'admin'):
#                                 event_obj.message_post(SUPERUSER_ID, event_id, body=details, subject=subject,
#                                                        context=context)
#                             else:
#                                 event_obj.message_post([event.id], body=details, subject=subject,
#                                                        context=context)
#                             if not event.assigned_interpreters:
#                                 for each_line in event.interpreter_ids2:
#                                     lines_state.append(each_line.state)
#                                 if lines_state and len(list(set(lines_state))) == 1 and list(set(lines_state))[
#                                     0] == 'cancel':
#                                     event_obj.write(SUPERUSER_ID, event_id, {'state': 'draft'})
#                             if user.user_type and user.user_type == 'vendor':
#                                 res = mod_obj.get_object_reference(cr, SUPERUSER_ID, 'bista_iugroup',
#                                                                    'view_event_user_tree')
#                                 res_id = res and res[1] or False,
#                                 context.update({'event_id': event_id[0]})
#                                 event_obj.write(event_id[0], {'no_editable': False})
#                                 return res
#             if interp_contact_delayed:
#                 if reply == 'Y':
#                     for data_delay in interp_contact_delayed:
#                         if data_delay['phone']:
#                             update_format_interp_mob = map(int, re.findall(r'\d+', str(data_delay['phone'])))
#                             str1 = ''.join(str(e) for e in update_format_interp_mob)
#                             updated_num_interp_mob = "+" + str1
#                             if updated_num_interp_mob.startswith('+1'):
#                                 pass
#                             else:
#                                 updated_num_interp_mob = updated_num_interp_mob[0] + "1" + updated_num_interp_mob[1:]
#                         if updated_num_interp_mob == updated_num:
#                             if interp_line.browse(data_delay['line_id']).interpreter_id.opt_for_sms:
#                                 select_template_body = None
#                                 sms_template_obj = self.env['sms.template.twilio']
#                                 get_template_delayed_reply = sms_template_obj.search([
#                                     ('action_for', '=', 'delayed_reply')])
#                                 for template_ids in sms_template_obj.browse( get_template_delayed_reply):
#                                     select_template_body = template_ids.sms_text
#                                 event_data = event_obj.browse(event_id[0])
#                                 event_time_start = event_data.event_start_hr + ':' + event_data.event_start_min + event_data.am_pm
#                                 event_time_end = event_data.event_end_hr + ':' + event_data.event_end_min + event_data.am_pm2
#                                 sms_vals = {
#                                     'sms_body': select_template_body % (event_data.name, event_data.event_start_date,
#                                                                         event_time_start, event_time_end,
#                                                                         event_data.location_id.state_id.name,
#                                                                         event_data.location_id.city,
#                                                                         event_data.location_id.zip),
#                                     'sms_to': updated_num
#                                 }
#                                 self.env['twilio.sms.send'].create(sms_vals)
#
#         event_obj.write(event_id[0], {'no_editable': False})
#         return res
#
#
# class sms_template_twilio(models.Model):
#     _name = 'sms.template.twilio'
#     _inherit = ['mail.thread']
#     _description = 'IUG SMS Template'
#     _rec_name = 'action_for'
#
#     action_for = fields.Selection([
#         ('job_offer', 'Job Offer'),
#         ('assigned_interp', 'Allocated Interpreter'),
#         ('assigned_customer', 'Customer Confirmation'),
#         ('event_cancel', 'Event Cancellation'),
#         ('delayed_reply', 'Event Unavailable'),
#         ('interp_scheduled', 'Interpreter Scheduled'),
#     ], 'Template For', required=True),
#     sms_text = fields.Text(string='Template Content', required=True)
#
#     @api.model
#     def create(self, vals):
#         return super(sms_template_twilio, self).create( vals)