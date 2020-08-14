# -*- coding: utf-8 -*-
import odoo
import web.http as http
import tools.config as config
from odoo import SUPERUSER_ID
from openerp.modules.registry import RegistryManager


class twilio_sms(http.Controller):
    _cp_path = '/twilio_sms'

    @http.httprequest
    def message_received(self, req, **kw):
        print '============message received============'
        dbname = config.options.get('dbfilter')
        if not dbname:
            return ''
        registry = RegistryManager.get(dbname)

        with registry.cursor() as cr:
            # find sms account from the account_sid
            try:
                TwilioAccounts = registry.models.get('twilio.accounts')
                account_id = TwilioAccounts.get_account_id(cr, SUPERUSER_ID, kw.get('AccountSid'))
                vals = {
                    'sms_from': kw.get('From'),
                    'sms_to': kw.get('To'),
                    'sms_body': kw.get('Body', ''),
                    'service_sid': kw.get('MessagingServiceSid'),
                    'account_id': account_id and account_id[0] or False,
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

                TwilioSms = registry.models.get('twilio.sms.received')
                TwilioSms.create(cr, SUPERUSER_ID, vals,context={'web':True})
                cr.commit()
                
            except Exception as e:
                # raise e
                return 'Insufficient Values'
        return 'Message received Successfully'

    @http.httprequest
    def message_status(self, req, **kw):
        print "=================status======"
        dbname = config.options.get('dbfilter')
        if not dbname:
            return ''
        registry = RegistryManager.get(dbname)

        with registry.cursor() as cr:
            message_sid = kw.get('MessageSid')
            message_send_obj = registry.models.get('twilio.sms.send')
            send_msg_id = message_send_obj.search(cr, SUPERUSER_ID, [('message_sid', '=', message_sid)])
            if send_msg_id:
                message_send_obj.write(cr, SUPERUSER_ID, send_msg_id,
                    {'status': kw.get('MessageStatus')})
                cr.commit()
        return 'Message status is okay'

