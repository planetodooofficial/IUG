# -*- coding: utf-8 -*-
import odoo
from odoo import http
from odoo.tools import config
from odoo import SUPERUSER_ID
from odoo.modules.registry import RegistryManager
from odoo import api
import logging
import requests, json
_logger = logging.getLogger(__name__)

class twilio_sms(http.Controller):
    _cp_path = '/twilio_sms'

    @http.route('/twilio_sms/message_received', type='http', auth='public',csrf=False)
    def message_received(self,**kw):
        print ('============message received============')
        dbname = config.get('db_filter')
        if not dbname:
            return ''
        registry = odoo.registry(dbname)
        with registry.cursor() as cr:
            # find sms account from the account_sid
            try:
                env = api.Environment(cr, SUPERUSER_ID, {})
                TwilioAccounts = env['twilio.accounts']
                account_id = TwilioAccounts.get_account_id(kw.get('AccountSid'))
                vals = {
                    'sms_from': kw.get('From'),
                    'sms_to': kw.get('To'),
                    'sms_body': kw.get('Body', ''),
                    'service_sid': kw.get('MessagingServiceSid'),
                    'account_id': account_id or False,
                    'account_sid': kw.get('AccountSid'),
                    'message_sid': kw.get('MessageSid'),

                    'from_zip': kw.get('FromZip'),
                    'from_city': kw.get('FromCity'),
                    'from_state': kw.get('FromState'),
                    'from_country': kw.get('FromCountry'),

                    'to_zip': kw.get('ToZip'),
                    'to_city': kw.get('ToCity'),
                    'to_state': kw.get('ToState'),
                    'to_country': kw.get('ToCountry'),

                    'status': kw.get('SmsStatus'),
                    'api_version': kw.get('ApiVersion'),
                }

                TwilioSms = env['twilio.sms.received']
                TwilioSms.create(vals)
                cr.commit()
                
            except Exception as e:
                # raise e
                _logger.info('-------------twilio error------------%s',e)
                return 'Insufficient Values'
        return 'Message received Successfully'

    @http.route('/twilio_sms/message_status', type='http', auth='public',csrf=False)
    def message_status(self,**kw):
        print ("=================status======")
        dbname = config.get('db_filter')
        if not dbname:
            return ''
        registry = odoo.registry(dbname)
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            message_sid = kw.get('MessageSid')
            message_send_obj = env['twilio.sms.send']
            send_msg_id = message_send_obj.search([('message_sid', '=', message_sid)])
            if send_msg_id:
                send_msg_id.write({'status': kw.get('MessageStatus')})
                cr.commit()
        return 'Message status is okay'

