from odoo import http, tools, _
from quickbooks import Oauth2SessionManager
from quickbooks import QuickBooks
from quickbooks.objects.customer import Customer
from datetime import datetime
from odoo.http import request
from dateutil.parser import parse
import json
import base64
import pytz
import logging
logger = logging.getLogger('quickbook')

class QuickbooksData(http.Controller):

    def connect(self):
        logger.warning("--------------- I am in connect of controller() ---------------")
        clientkey = clientsecret = reconfig_idsquest_token_url = ''
        access_token_url = authorization_base_url = ''
        callbck_url = request.env['ir.config_parameter'].get_param('web.base.url')
        url = callbck_url + '/page/quickbook'
        logger.warning("This the the callback url %s",url)
        quick_config_obj = request.env['quick.configuration']
        config_ids = quick_config_obj.search([])
        clientkey = config_ids.clientkey
        clientsecret = config_ids.clientsecret
        session_manager = Oauth2SessionManager(client_id=clientkey, client_secret=clientsecret, base_url=url, )
        callback_url = url
        authorize_url = session_manager.get_authorize_url(callback_url)
        return [authorize_url, session_manager]

    def get_qb_data(self,content,temp):
        logger.warning("--------------- I am in get_qb_data() ---------------")
        quickbook_obj = request.env['quick.configuration']
        companies = request.env['res.company'].search([])
        for company in companies:
            records = [i for i in content if (i['company'] == company.quick_id)]
            if records:
                quickbook_obj.read_qb_data(records,company,temp)


    @http.route('/page/quickbook', auth='public', type='http', website=True)
    def quickbookpage(self, **kwargs):
        logger.warning("--------------- I am in quickbookpage() ---------------")
        session_man = self.connect()
        code = kwargs.get('code')
        company = kwargs.get('realmId')
        session_manager = session_man[1]
        token = session_manager.get_access_tokens(code)
        access_token = session_manager.access_token
        company = request.env['res.company'].search([('quick_id','=',company)])
        if company:
            company.write({'rf_token':session_manager.refresh_token})
            request._cr.commit()
        callbck_url = request.env['ir.config_parameter'].get_param('web.base.url')
        return request.redirect(callbck_url)

    @http.route('/page/webhook_qb', auth='public', type='json', website=True)
    def webhook_qb(self,req):
        logger.warning("--------------- I am in webhook_qb() ----------------")
        response = json.dumps(req.jsonrequest)
        response_data = json.loads(response)
        if response_data:
            customers = []
            vendors = []
            invoices = []
            bills = []
            payments=[]
            events = response_data['eventNotifications']
            for data in events:
                company = data['realmId']
                for entity in data['dataChangeEvent']['entities']:
                    entity.update({'company': company})
                    if entity['name']=='Customer':
                        customers.append(entity)
                    if entity['name']=='Vendor':
                        vendors.append(entity)
                    if entity['name']=='Invoice':
                        invoices.append(entity)
                    if entity['name']=='Bill':
                        bills.append(entity)
                    if entity['name'] == 'BillPayment':
                        payments.append(entity)
            if customers:
                self.get_qb_data(customers,'customers')
            if vendors:
                self.get_qb_data(vendors,'vendors')
            if invoices:
                self.get_qb_data(invoices,'invoices')
            if bills:
                self.get_qb_data(bills,'bills')
            if payments:
                self.get_qb_data(payments, 'payments')




