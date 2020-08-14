import logging
from datetime import datetime,timedelta
import pytz
import requests
import json
import base64
import xmltodict
import re
from intuitlib.client import AuthClient
from odoo import api, fields, models
from odoo.exceptions import UserError
from quickbooks import Oauth2SessionManager
from quickbooks import QuickBooks
from quickbooks.objects.customer import Customer
from quickbooks.objects.vendor import Vendor
from quickbooks.objects.account import Account
from quickbooks.objects.item import Item
from quickbooks.objects.invoice import Invoice
from quickbooks.objects.bill import Bill
from quickbooks.objects.billpayment import BillPayment
from quickbooks.objects.account import Account
logger = logging.getLogger('quickbook')

class AccountAccount(models.Model):
    _inherit = 'account.account'

    active = fields.Boolean('Active',default=True)

class Event(models.Model):
    _inherit = 'event'



    @api.multi
    def get_check_custom(self):
        if self.view_interpreter_inv:
            logger.warning("----------------------I am i get check invoice======= %s ====-----------------------",self.view_interpreter_inv)
            self.ch_amount = '$ ' + str(self.view_interpreter_inv.amount_total)
            logger.warning("----------------------I am i get check invoice======= %s ====-----------------------",self.ch_amount)
            if self.view_interpreter_inv.check_no:
                self.check_no = self.view_interpreter_inv.check_no
   
    @api.one
    def get_check(self):
        if self.id:
            invoice = self.env['account.invoice'].search([('event_id','=',self.id),('partner_id','=',self.env.user.partner_id.id)],limit=1)
            if invoice:
                self.ch_amount = '$ '+ str(invoice.amount_total)
                if invoice.check_no:
                    self.check_no = invoice.check_no
    ch_amount = fields.Char('Check Amount',compute='get_check')
    check_no = fields.Char('Check Number',compute='get_check')

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    in_qb = fields.Boolean('In-QuickBook',default=False)
    quick_id = fields.Char('QuickBook-Id')
    check_no = fields.Char('Check Number')
    qb_check_id = fields.Char('QB-Check Id')

class ResCompany(models.Model):
    _inherit = 'res.company'

    quick_id = fields.Char('QuickBook-Id')
    quick_name = fields.Char('QuickBook Name')
    rf_token = fields.Char('Refresh Token')
    in_qb = fields.Boolean('In-QuickBook',default=False)

class ProductProduct(models.Model):
    _inherit = 'product.template'

    quick_id = fields.Char('QuickBook-Id')
    in_qb = fields.Boolean('In-QuickBook',default=False)
    for_qb = fields.Boolean('For-QuickBook',default=False)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    quick_id = fields.Char('QuickBook-Id')
    in_qb = fields.Boolean('In-QuickBook',default=False)

class Account_Account(models.Model):
    _inherit = 'account.account'

    quick_id = fields.Char('QuickBook-Id')
    in_qb = fields.Boolean('In-QuickBook',default=False)

class Quick_configuration(models.Model):
    _name = "quick.configuration"

    clientkey =  fields.Char('Client Key', required="1")
    clientsecret = fields.Char('Client Secret', required="1")
    production = fields.Boolean('Production')
    refresh_token = fields.Char('Refresh Token')
    access_token = fields.Char('Access Token')
    from_range = fields.Datetime('From Date')
    to_range = fields.Datetime('To Date')

    @api.multi
    def refresh_api_token(self,company):
        try:
            logger.warning("----------------------I am in refresh_api_token()-----------------------")
            logger.warning("----------------------Company-Id ======= %s ====-----------------------",company.id)
            env = 'sandbox'
            configs = self.sudo().search([],limit=1)
            if configs.production:
                env = 'production'
            callbck_url = self.env['ir.config_parameter'].get_param('web.base.url')
            url = callbck_url + '/page/quickbook'
            client = AuthClient(client_id=configs.clientkey,
                                client_secret=configs.clientsecret,
                                redirect_uri=url, environment=env)
            client.refresh(refresh_token=company.rf_token)
            company.sudo().write({'rf_token': client.refresh_token})
            self._cr.commit()
            return client.access_token
        except Exception as e:
            raise UserError("Got an Issue---:", e)

    @api.multi
    def get_client(self,company):
        try:
            logger.warning("------------------------I am in get_client()------------------------")
            env = 'sandbox'
            configs = self.sudo().search([],limit=1)
            key = configs.clientkey
            secret = configs.clientsecret
            if configs.production:
                env = 'production'
            access_token = self.refresh_api_token(company)
            logger.warning("------------------------I have got access token------------------------")
            session = Oauth2SessionManager(client_id=company.quick_id, client_secret=secret, access_token=access_token)
            logger.warning("------------------------I have got session------------------------")
            if env == 'sandbox':
                client = QuickBooks(sandbox=True, session_manager=session, company_id=company.quick_id)
                logger.warning("------------------------I have got client------------------------")
            else:
                client = QuickBooks(session_manager=session, company_id=company.quick_id)
                logger.warning("------------------------I have got client------------------------")
            return client
        except Exception as e:
            raise UserError("Got an Issue---:", e)

    @api.multi
    def connect(self):
        logger.warning("------------------------I am in connect()---------------------------")
        clientkey = clientsecret = ''
        access_token_url = authorization_base_url = ''
        callbck_url = self.env['ir.config_parameter'].get_param('web.base.url')
        url = callbck_url + '/page/quickbook'
        quick_config_obj = self.env['quick.configuration']
        config_ids = quick_config_obj.sudo().search([])
        clientkey = config_ids.clientkey
        clientsecret = config_ids.clientsecret
        session_manager = Oauth2SessionManager(client_id=clientkey, client_secret=clientsecret, base_url=url, )
        callback_url = url
        authorize_url = session_manager.get_authorize_url(callback_url)
        return [authorize_url, session_manager]

    @api.multi
    def get_access_refresh_token(self):
        logger.warning("---------------------------------I am in get_access_refresh_token()----------------------------")
        cust_date = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
        url = self.connect()
        authorize_url = url[0]
        state_dict = {'date': cust_date, 'status': "Customer_Import"}
        state_json = json.dumps(state_dict)
        encoded_params = base64.urlsafe_b64encode(state_json)
        state_param = str(encoded_params)
        authorize_url = authorize_url.replace('None', state_param)
        if authorize_url:
            return {
                'type': 'ir.actions.act_url',
                'target': 'self',
                'url': authorize_url,
            }
        else:
            raise UserError("Something went Wrong")

    @api.multi
    def create_partners(self,company,partners,temp):
        logger.warning("------------------------I am in create_partners()------------------------")
        for record in partners:
            try:
                mobile = country = state = city = line1 = line2 = zip = email = phone = False
                customer_exist = self.env['res.partner'].sudo().search([('quick_id', '=', record.Id),('company_id','=',company.id)])
                if not record.PrimaryPhone == None:
                    phone = record.PrimaryPhone.FreeFormNumber
                if not record.PrimaryEmailAddr == None:
                    email = record.PrimaryEmailAddr.Address
                if not record.BillAddr == None:
                    city = record.BillAddr.City
                    line1 = record.BillAddr.Line1
                    line2 = record.BillAddr.Line2
                    zip = record.BillAddr.PostalCode
                    country = self.env['res.country'].sudo().search([('name', '=', record.BillAddr.Country)]).id
                    state = self.env['res.country.state'].sudo().search([('name', '=', record.BillAddr.CountrySubDivisionCode)]).id
                if not record.Mobile == None:
                    mobile = record.Mobile.FreeFormNumber
                vals = {'name': record.GivenName,
                        'last_name':record.FamilyName,
                        'city': city,
                        'country_id': country,
                        'state_id': state,
                        'street': line1,
                        'street2': line2,
                        'zip': zip,
                        'email': email,
                        'phone': phone,
                        'mobile': mobile,
                        'in_qb': True,
                        'quick_id': record.Id,
                        'company_id':company.id,
                        }
                if not temp:
                    vals.update({'customer': False, 'supplier': True})
               # if not customer_exist:
                #    customer = self.env['res.partner'].sudo().create(vals)
                 #   self._cr.commit()
                  #  logger.warning('Imported partner %s --- With QB-Id %s ', customer.id, record.Id)
               # else:
	        if customer_exist:
                    customer_exist.sudo().write(vals)
                    self._cr.commit()
                    logger.warning('Updated partner %s --- With QB-Id %s ', customer_exist.id,record.Id)
            except Exception as e:
                logger.error('I am in create_partners() and Error is -- %s --', e)

    @api.multi
    def import_customers_vendors(self):
        logger.warning("------------------------I am in import_customers_vendors()------------------------")
        configs = self.sudo().search([], limit=1)
        if configs:
            companies = self.env['res.company'].sudo().search([])
            for company in companies:
                try:
                    if company.in_qb:
                        client = self.get_client(company)
                        current_day = datetime.today() - timedelta(days=1)
                        # current_day = (datetime.now() - timedelta(minutes=65))
                        tz = pytz.timezone("America/Toronto")
                        aware_dt = tz.localize(current_day)
                        query_date = aware_dt.isoformat()
                        c_query = "SELECT * FROM customer WHERE MetaData.CreateTime >='" + query_date + "' ""STARTPOSITION 1 MAXRESULTS 1000"
                        customers = Customer.query(c_query, qb=client)
                        if customers:
                            customer = self.create_partners(company,customers,True)
                        v_query = "SELECT * FROM vendor WHERE MetaData.CreateTime >='" + query_date + "' ""STARTPOSITION 1 MAXRESULTS 1000"
                        vendors = Vendor.query(v_query, qb=client)
                        if vendors:
                            vendor = self.create_partners(company,vendors,False)
                except Exception as e:
                    logger.error('I am in import_customers_vendors() and Error is---- %s ---- ', e)
        else:
            logger.error("No Credentials found for QuickBook")

    @api.multi
    def export_partners(self,company,access_token):
        logger.warning("------------------------I am in export_partners()------------------------")
        env = 'sandbox'
   	post_url = "https://sandbox-quickbooks.api.intuit.com/v3/company/"
        configs = self.sudo().search([])
        if configs.production:
            env = 'production'
            post_url = "https://quickbooks.api.intuit.com/v3/company/"
        auth_header = 'Bearer {0}'.format(access_token)
        headers = {'Authorization': auth_header, 'content-type': 'application/json'}
        partners=[]
        customer_ids = self.env['res.partner'].sudo().search([('in_qb', '=', False), ('cust_type','=','customer'),('company_id', '=', company.id)])
        partners.extend(customer_ids)
        interpreter_ids = self.env['res.partner'].sudo().search(
            [('in_qb', '=', False), ('cust_type', '=', 'interpreter'), ('is_interpretation_active', '=', True),
             ('company_id', '=', company.id)])
        partners.extend(interpreter_ids)
        translator_ids = self.env['res.partner'].sudo().search(
            [('in_qb', '=', False), ('cust_type', '=', 'translator'), ('is_translation_active', '=', True),
             ('company_id', '=', company.id)])
        partners.extend(translator_ids)
        interp_and_transl_ids = self.env['res.partner'].sudo().search(
            [('in_qb', '=', False), ('cust_type', '=', 'interp_and_transl'), ('is_translation_active', '=', True),
             ('is_interpretation_active', '=', True), ('company_id', '=', company.id)])
        partners.extend(interp_and_transl_ids)

        # partners = self.env['res.partner'].sudo().search([('in_qb', '=', False), ('cust_type','=','translator'),('is_translation_active','=',True),('company_id', '=', company.id)])
       # logger.warning("------------------------The Count of partners is %s------------------------",len(partners))
        time = (datetime.now() - timedelta(minutes=65)).strftime('%Y-%m-%d %H:%M:%S')
        logger.warning("------------------------The write time in partner %s------------------------",time)
        exist_partners = self.env['res.partner'].search([('in_qb', '=', True),('company_id', '=', company.id),('write_date','>=',time)])
        #exist_partners = self.env['res.partner'].search([('company_id', '=', company.id),('id','=',165926)])
        partners.extend(exist_partners)
        logger.warning("------------------------The Count of partners is %s------------------------",len(partners))
	cust_url = post_url + company.quick_id + '/customer?minorversion=4'
        vend_url = post_url + company.quick_id + '/vendor?minorversion=4'
        if partners:
            for record in partners:
                flag = False
                try:
                    state = country = title = ' '
                    if record.state_id:
                        state = record.state_id.name
                    if record.country_id:
                        country = record.country_id.name
                    if record.title:
                        title = record.title.name
                    if record.customer:
                        vals = {
                            "Suffix": record.ref + '-' + str(record.id),
                            "Title": title,
                            "MiddleName": record.middle_name or '',
                            "Notes": "IUG Customer",
                            "FamilyName": record.last_name or '',
                            "PrimaryPhone": {
                                "FreeFormNumber": record.phone
                            },
                            "Mobile": {
                                "FreeFormNumber": record.mobile
                            },
                            "BillAddr": {
                                "CountrySubDivisionCode": state or '',
                                "City": record.city or '',
                                "PostalCode": record.zip or '',
                                "Line1": record.street or '',
                                "Line2": record.street2 or '',
                                "Country": country or ''
                            },
                            "GivenName": record.name
                        }
                        if record.email or record.email2:
                            vals.update({"PrimaryEmailAddr": {
                                "Address": record.email or record.email2
                            }})
		        if record.in_qb:
                            exist_quick_id = record.quick_id
                            logger.warning('quick id in ERP------ %s ---- ', exist_quick_id)
                            exist_post_url = post_url + company.quick_id + "/customer/" + exist_quick_id + "?minorversion=45"
                            read_customer = requests.get(exist_post_url, headers=headers)
                            response_data = json.dumps(xmltodict.parse(read_customer.text))
                            logger.warning('response_data------ %s ---- ',response_data)
                            key_vals = json.loads(response_data)
                            logger.warning('key_vals---- %s ---- ',key_vals)
                            update_synctoken = key_vals['IntuitResponse']['Customer']['SyncToken']
                            logger.warning('update_synctoken---- %s ---- ', update_synctoken)
                            vals.update({"Id": record.quick_id, "SyncToken": update_synctoken})
                            logger.warning('Update Invoice With ID---- %s ---- ', record.id)
                        data = json.dumps(vals)
                        flag = True
                        export = requests.post(cust_url, data=data, headers=headers)
                        response_data = json.dumps(xmltodict.parse(export.text))
                        key_vals = json.loads(response_data)
                        qb_id = key_vals['IntuitResponse']['Customer']['Id']
                    else:
                        name = ''
                        if record.name:
                            name += record.name +' '
                        if record.middle_name:
                            name += record.middle_name+' '
                        if record.last_name:
                            name += record.last_name
                        vals = {
                            "Suffix": record.ref + '-' + str(record.id),
                            "Title": title,
                            "MiddleName": record.middle_name or '',
                            "Notes": "IUG Customer",
                            "FamilyName": record.last_name or '',
                            "PrimaryPhone": {
                                "FreeFormNumber": record.phone
                            },
                            "Mobile": {
                                "FreeFormNumber": record.mobile
                            },
                            "BillAddr": {
                                "CountrySubDivisionCode": state or '',
                                "City": record.city or '',
                                "PostalCode": record.zip or '',
                                "Line1": record.street or '',
                                "Line2": record.street2 or '',
                                "Country": country or ''
                            },
                            "GivenName": record.name,
                            "PrintOnCheckName": name
                        }
                        if record.email or record.email2:
                            vals.update({"PrimaryEmailAddr": {
                                "Address": record.email or record.email2
                            }})
                        if record.in_qb:
                            exist_quick_id = record.quick_id
                            logger.warning('quick id in ERP------ %s ---- ', exist_quick_id)
                            exist_post_url = post_url + company.quick_id + "/vendor/" + exist_quick_id + "?minorversion=45"
                            logger.warning('------i am in exist_post_url ---- ')
                            read_vendor = requests.get(exist_post_url, headers=headers)
                            response_data = json.dumps(xmltodict.parse(read_vendor.text))
                            logger.warning('response_data------ %s ---- ',response_data)
                            key_vals = json.loads(response_data)
                            logger.warning('key_vals---- %s ---- ',key_vals)
                            update_synctoken = key_vals['IntuitResponse']['Vendor']['SyncToken']
                            logger.warning('update_synctoken---- %s ---- ', update_synctoken)
                            vals.update({"Id": record.quick_id, "SyncToken": update_synctoken})
                            logger.warning('Update Invoice With ID---- %s ---- ', record.id)
                        data = json.dumps(vals)
                        flag = True
                        export = requests.post(vend_url, data=data, headers=headers)
                        response_data = json.dumps(xmltodict.parse(export.text))
                        key_vals = json.loads(response_data)
                        qb_id = key_vals['IntuitResponse']['Vendor']['Id']
                    record.sudo().write({'in_qb': True, 'quick_id': qb_id})
                    self._cr.commit()
                    logger.warning('Exported Partner With ID---- %s ---- ', record.id)
                except Exception as e:
                    if flag:
                        issue = export.text
                        if "Email Address does not conform to the syntax rules of RFC 822" in issue:
                            try:
                                logger.warning('------------------Inside Email Exception----------')
                                vals.pop('PrimaryEmailAddr',None)
                                data = json.dumps(vals)
                                if not record.customer:
                                    export = requests.post(vend_url, data=data, headers=headers)
                                    response_data = json.dumps(xmltodict.parse(export.text))
                                    key_vals = json.loads(response_data)
                                    qb_id = key_vals['IntuitResponse']['Vendor']['Id']
                                    record.sudo().write({'in_qb': True, 'quick_id': qb_id})
                                    self._cr.commit()
                                    logger.warning('Exported Partner Without Email and  ID---- %s ---- ', record.id)
                                else:
                                    export = requests.post(cust_url, data=data, headers=headers)
                                    response_data = json.dumps(xmltodict.parse(export.text))
                                    key_vals = json.loads(response_data)
                                    qb_id = key_vals['IntuitResponse']['Customer']['Id']
                                    record.sudo().write({'in_qb': True, 'quick_id': qb_id})
                                    self._cr.commit()
                                    logger.warning('Exported Partner Without Email and ID---- %s ---- ', record.id)
                            except Exception as e:
                                logger.warning('Error in Email Exception---- %s ---- ',e)
                        else:
                            logger.error('I am in export_partners() and Error with %s and the issue is -- %s ',record.id, export.text)
                    else:
                        logger.error('I am in export_partners() and Error with %s and the issue is -- %s ', record.id,export.text)

    @api.multi
    def export_customers_vendors(self):
        logger.warning("------------------------I am in export_customers_vendors()------------------------")
        configs = self.sudo().search([],limit=1)
        if configs:
            companies = self.env['res.company'].sudo().search([])
            for company in companies:
                try:
                    if company.in_qb:
                        access_token = self.refresh_api_token(company)
                        export = self.export_partners(company,access_token)
                except Exception as e:
                     logger.error('I am in export_customers_vendors() and Error is---- %s ---- ', e)
        else:
            logger.error("No Credentials found for QuickBook")

    @api.multi
    def export_accounts(self):
        logger.warning("------------------------I am in export_accounts()------------------------")
        env = 'sandbox'
        post_url = "https://sandbox-quickbooks.api.intuit.com/v3/company/"
        configs = self.sudo().search([])
        if configs.production:
            env = 'production'
            post_url = "https://quickbooks.api.intuit.com/v3/company/"
        companies = self.env['res.company'].sudo().search([])
        for company in companies:
            try:
                if company.in_qb:
                    access_token = self.refresh_api_token(company)
                    auth_header = 'Bearer {0}'.format(access_token)
                    headers = {'Authorization': auth_header, 'content-type': 'application/json'}
                    acc_type = self.env['account.account.type'].sudo().search([('name','=','Prepayments')]).id
                    accounts = self.env['account.account'].sudo().search([('in_qb', '=', False),('company_id','=',company.id),('user_type_id','!=',acc_type)])
                    url = post_url + company.quick_id + "/account?minorversion=4"
                    for account in accounts:
                        try:
                            if account.user_type_id.name == 'Receivable':
                                type = 'Accounts Receivable'
                            if account.user_type_id.name == 'Payable':
                                type = 'Accounts Payable'
                            if account.user_type_id.name == 'Bank and Cash':
                                type = 'Bank'
                            if account.user_type_id.name == 'Credit Card':
                                type = 'Credit Card'
                            if account.user_type_id.name == 'Current Assets':
                                type = 'Other Current Asset'
                            if account.user_type_id.name == 'Non-current Assets':
                                type = 'Other Current Asset'
                            if account.user_type_id.name == 'Prepayments':
                                type = ''
                            if account.user_type_id.name == 'Fixed Assets':
                                type = 'Fixed Asset'
                            if account.user_type_id.name == 'Current Liabilities':
                                type = 'Other Current Liability'
                            if account.user_type_id.name == 'Non-current Liabilities':
                                type = 'Long Term Liability'
                            if account.user_type_id.name == 'Equity':
                                type = 'Equity'
                            if account.user_type_id.name == 'Current Year Earnings':
                                type = 'Income'
                            if account.user_type_id.name == 'Other Income':
                                type = 'Other Income'
                            if account.user_type_id.name == 'Income':
                                type = 'Income'
                            if account.user_type_id.name == 'Depreciation':
                                type = 'Expense'
                            if account.user_type_id.name == 'Expenses':
                                type = 'Other Expense'
                            if account.user_type_id.name == 'Cost of Revenue':
                                type = 'Cost of Goods Sold'
                            code = re.sub('-','', account.code)
                            vals = {"Name": account.code + ' ' + account.name,
                                    "AccountType":type,
                                    "AcctNum": code,
                                    }
                            data = json.dumps(vals)
                            export_account = requests.post(url, data=data, headers=headers)
                            response_data = json.dumps(xmltodict.parse(export_account.text))
                            key_vals = json.loads(response_data)
                            qb_id = key_vals['IntuitResponse']['Account']['Id']
                            account.sudo().write({'in_qb': True, 'quick_id': qb_id})
                            self._cr.commit()
                            logger.warning('Exported Account in QB ---- %s ----',account.id)
                        except Exception as e:
                            logger.error('I am in export_accounts() and Account-Id == %s and Error ---- %s ----',account.id,export_account.text )
            except Exception as e:
                logger.error('I am in export_accounts() and Error is---- %s ---- ', e)

    @api.multi
    def map_accounts(self):
        logger.warning("------------------------I am in map_accounts()------------------------")
        configs = self.sudo().search([], limit=1)
        if configs:
            companies = self.env['res.company'].sudo().search([])
            for company in companies:
                try:
                    if company.in_qb:
                        client = self.get_client(company)
                        current_day = datetime.now()
                        # current_day = (datetime.now() - timedelta(minutes=65))
                        tz = pytz.timezone("America/Toronto")
                        aware_dt = tz.localize(current_day)
                        query_date = aware_dt.isoformat()
                        query = "SELECT * FROM account WHERE MetaData.CreateTime <='" + query_date + "' ""STARTPOSITION 1 MAXRESULTS 1000"
                        accounts = Account.query(query, qb=client)
                        if accounts:
                            for account in accounts:
                                try:
                                    acc_exist = self.env['account.account'].sudo().search([('name','=',account.Name),('company_id','=',company.id)])
                                    if acc_exist:
                                        acc_exist.sudo().write({'in_qb':True,'quick_id':account.Id})
                                        self._cr.commit()
                                        logger.warning("-------------------Updated Account %s with QB-Id === %s  ------------------",acc_exist.id,account.Id)
                                except Exception as e:
                                    logger.error("-----------------In mapping Accoounts ::: %s --------------------",e)
                except Exception as e:
                    logger.error('Error is---- %s ---- ', e)
        else:
            logger.error("No Credentials found for QuickBook")

    @api.multi
    def create_invoices(self,company,invoices):
        logger.warning("------------------------I am in create_invoices()------------------------")
        customer = ['customer','contact','company']
        event = False
        for invoice in invoices:
            a = invoice.CustomField
            logger.warning("------------------------Response of the Invoice object --------%s:- ------------------------",a)
            try:
                invoice_exist = self.env['account.invoice'].sudo().search([('quick_id','=',invoice.Id)])
                lines = []
                partner = self.env['res.partner'].sudo().search([('company_id','=',company.id),('quick_id','=',invoice.CustomerRef.value),('cust_type','in',('customer', 'contact', 'company'))])
                currency = self.env['res.currency'].sudo().search([('name','=','USD')]).id
                if partner.cust_type in customer:
                    journal = self.env['account.journal'].sudo().search([('name','=','Sales Journal'),('company_id','=',company.id)]).id
                else:
                    journal = self.env['account.journal'].sudo().search([('name', '=', 'Purchase Journal'), ('company_id', '=', company.id)]).id
                for fields in invoice.CustomField:
                    if fields.Name == 'Event':
                        event = fields.StringValue
                        # event = self.env['event'].sudo().search([('name', '=',fields.StringValue),('company_id','=',company.id)]).id
                invoice_vals = {'partner_id':partner.id,
                                'currency_id':currency,
                                'journal_id':journal,
                                'event_id':event if event else False,
                                'quick_id': invoice.Id,
                                'in_qb': True,
                                'type': 'out_invoice',
                                'company_id':company.id,
                                }
                for invline in invoice.Line:
                    if invline.DetailType == 'SalesItemLineDetail':
                        pro_name = invline.SalesItemLineDetail.ItemRef.name
                        product = self.env['product.product'].sudo().search([('company_id','=',company.id),('quick_id', '=', invline.SalesItemLineDetail.ItemRef.value)])
                        if partner.cust_type in customer:
                            account = product.property_account_income_id.id
                        else:
                            account = product.property_account_expense_id.id
                        line_vals = {'product_id': product.id,
                                     'name': invline.Description if invline.Description!=None else product.name,
                                     'account_id': account,
                                     'quantity': int(invline.SalesItemLineDetail.Qty),
                                     'price_unit': int(invline.SalesItemLineDetail.UnitPrice),
                                     }
                        if invoice_exist:
                            for all_lines in invoice_exist.invoice_line_ids:
                                if pro_name == all_lines.product_id.name:
                                    invoice_vals.update({'invoice_line_ids':[(1,all_lines.id,line_vals)]})
                                    # invoice_exist.write(invoice_vals)
                        else:
                            if not product.for_qb:
                                lines.append((0,0,line_vals))
                logger.warning("------------------------Response of the Invoice object --------%s:- ------------------------",a)
                # if not invoice_exist:
                #     invoice_vals.update({'invoice_line_ids': lines})
                #     invoice_exist = self.env['account.invoice'].create(invoice_vals)
                # self._cr.commit()
                # logger.warning('Imported Invoice is--%s-- with Qb-ID--%s--', invoice_exist.id, invoice.Id)
            except Exception as e:
                logger.error('Error is---- %s ---- ', e)

    @api.multi
    def import_invoices(self):
        logger.warning("------------------------I am in import_invoices()------------------------")
        configs = self.sudo().search([], limit=1)
        if configs:
            companies = self.env['res.company'].sudo().search([])
            for company in companies:
                try:
                    if company.in_qb:
                        client = self.get_client(company)
                        current_day = datetime.today() - timedelta(days=1)
                        # current_day = (datetime.now() - timedelta(minutes=65))
                        tz = pytz.timezone("America/Toronto")
                        aware_dt = tz.localize(current_day)
                        query_date = aware_dt.isoformat()
                        query = "SELECT * FROM invoice WHERE MetaData.CreateTime >='" + query_date + "' ""STARTPOSITION 1 MAXRESULTS 1000"
                        invoices = Invoice.query(query, qb=client)
                        if invoices:
                            self.create_invoices(company, invoices)
                except Exception as e:
                    logger.error('Error is---- %s ---- ', e)
        else:
            logger.error("No Credentials found for QuickBook")

    @api.multi
    def export_invoice_qb(self,company,access_token):
        logger.warning("------------------------I am in export_invoice_qb()------------------------")
        env = 'sandbox'
        post_url = "https://sandbox-quickbooks.api.intuit.com/v3/company/"+ company.quick_id + "/invoice?minorversion=4"
        configs = self.sudo().search([])
        if configs.production:
            env = 'production'
            post_url = "https://quickbooks.api.intuit.com/v3/company/"+ company.quick_id + "/invoice?minorversion=4"
        auth_header = 'Bearer {0}'.format(access_token)
        headers = {'Authorization': auth_header, 'content-type': 'application/json'}
        #if configs.from_range and configs.to_range:
        #    date_from = configs.from_range[:-8]
        #    from_date = date_from + '00:00:00'
        #    date_to = configs.to_range[:-8]
        #    to_date = date_to + '00:00:00'
        #    invoices = self.env['account.invoice'].sudo().search([
        #        ('company_id','=',company.id),('in_qb','=',False),('state','in',('open','draft')),
        #        ('partner_id.cust_type','in',('customer','contact','company')),
        #        ('create_date','>=',from_date),('create_date','<=',to_date)])
        #else:
        #    invoices = self.env['account.invoice'].sudo().search([('company_id', '=', company.id), ('in_qb', '=', False), ('state', '=', 'paid')])
        # date_from = configs.from_range[:-8]
        # from_date = date_from
        # date_to = configs.to_range[:-8]
        # to_date = date_to
        # logger.warning("------------------------Date From-------------Date To-----------%s----------%s",date_from,date_to)
        #invoices = self.env['account.invoice'].sudo().search([('type','=','out_invoice'),('state','=','open'),('in_qb','=',False),('date_invoice','>','2019-12-31'),('company_id','=',company.id)])
        invoices=[]
        #logger.warning("------------------------Invoices list %s------------------------",invoices)
        ##time = (datetime.now() - timedelta(minutes=65)).strftime('%Y-%m-%d %H:%M:%S')
        invoices_1 = self.env['account.invoice'].sudo().search([('date_invoice','>','2019-12-31'),('state','=','open'),('type','=','out_invoice'),('company_id','=',company.id),('in_qb','=',False)])
        invoices.extend(invoices_1)
        #logger.warning("------------------------Invoices Type (%s)------------------------",type(invoices))
        ##invoice_ids2 = self.env['account.invoice'].sudo().search([('write_date','>=',time),('type','=','out_invoice'),('company_id','=',company.id),('in_qb','=',True)])
        ##invoices.extend(invoice_ids2)
	#invoice=self.env['account.invoice'].browse(560357)
        #invoices.append(invoice)
        logger.warning("------------------------The Count of Invoices to Export is (%s)------------------------",len(invoices))
        post_url_cust = "https://sandbox-quickbooks.api.intuit.com/v3/company/"
        configs = self.sudo().search([])
        if configs.production:
            post_url_cust = "https://quickbooks.api.intuit.com/v3/company/"
        cust_url = post_url_cust + company.quick_id + '/customer?minorversion=4'
        vend_url = post_url_cust + company.quick_id + '/vendor?minorversion=4'
        for invoice in invoices:
            try:
                if not invoice.partner_id.in_qb:
                    record=invoice.partner_id
                    flag = False
                    try:
                        state = country = title = ' '
                        if record.state_id:
                            state = record.state_id.name
                        if record.country_id:
                            country = record.country_id.name
                        if record.title:
                            title = record.title.name

                        vals = {
                            "Suffix": record.ref + '-' + str(record.id),
                            "Title": title,
                            "MiddleName": record.middle_name or '',
                            "Notes": "IUG Customer",
                            "FamilyName": record.last_name or '',
                            "PrimaryPhone": {
                                "FreeFormNumber": record.phone
                            },
                            "Mobile": {
                                "FreeFormNumber": record.mobile
                            },
                            "BillAddr": {
                                "CountrySubDivisionCode": state,
                                "City": record.city,
                                "PostalCode": record.zip,
                                "Line1": record.street,
                                "Line2": record.street2,
                                "Country": country
                            },
                            "GivenName": record.name
                        }
                        if record.email or record.email2:
                            vals.update({"PrimaryEmailAddr": {
                                "Address": record.email or record.email2
                            }})
                        data = json.dumps(vals)
                        flag = True
                        export = requests.post(cust_url, data=data, headers=headers)
                        response_data = json.dumps(xmltodict.parse(export.text))
                        key_vals = json.loads(response_data)
                        qb_id = key_vals['IntuitResponse']['Customer']['Id']
                        record.sudo().write({'in_qb': True, 'quick_id': qb_id})
                        self._cr.commit()
                        logger.warning('Exported Partner With ID---- %s ---- ', record.id)
                    except Exception as e:
                        if flag:
                            issue = export.text
                            if "Email Address does not conform to the syntax rules of RFC 822" in issue:
                                try:
                                    logger.warning('------------------Inside Email Exception----------')
                                    vals.pop('PrimaryEmailAddr', None)
                                    data = json.dumps(vals)
                                    if not record.customer:
                                        export = requests.post(vend_url, data=data, headers=headers)
                                        response_data = json.dumps(xmltodict.parse(export.text))
                                        key_vals = json.loads(response_data)
                                        qb_id = key_vals['IntuitResponse']['Vendor']['Id']
                                        record.sudo().write({'in_qb': True, 'quick_id': qb_id})
                                        self._cr.commit()
                                        logger.warning('Exported Partner Without Email and  ID---- %s ---- ', record.id)
                                    else:
                                        export = requests.post(cust_url, data=data, headers=headers)
                                        response_data = json.dumps(xmltodict.parse(export.text))
                                        key_vals = json.loads(response_data)
                                        qb_id = key_vals['IntuitResponse']['Customer']['Id']
                                        record.sudo().write({'in_qb': True, 'quick_id': qb_id})
                                        self._cr.commit()
                                        logger.warning('Exported Partner Without Email and ID---- %s ---- ', record.id)
                                except Exception as e:
                                    logger.warning('Error in Email Exception---- %s ---- ', e)
                            else:
                                logger.error('I am in export_partners() and Error with %s and the issue is -- %s ',
                                             record.id, export.text)
                        else:
                            logger.error('I am in export_partners() and Error with %s and the issue is -- %s ', record.id,
                                         export.text)
                invoice = self.env['account.invoice'].browse(invoice.id)
                if invoice.partner_id.in_qb:
                    lines = []
                    base = mileage = travel = discount = 0.0
                   # travel_product = self.env['product.product'].sudo().search([('name','=','Travelling ACD'),('company_id','=',company.id)])
                   # mileage_product = self.env['product.product'].sudo().search([('name','=','Mileage ACD'),('company_id','=',company.id)])
                   # edit_product = self.env['product.product'].sudo().search([('name','=','Total Edited ACD'),('company_id','=',company.id)])
                    for line in invoice.invoice_line_ids:
                        if line.product_id.service_type=='interpreter':
                             travel_product = self.env['product.product'].sudo().search([('name','=','Travelling For Interp'),('company_id','=',company.id)])
                             mileage_product = self.env['product.product'].sudo().search([('name','=','Mileage For Interp'),('company_id','=',company.id)])
                             edit_product = self.env['product.product'].sudo().search([('name','=','Total Edited For Interp'),('company_id','=',company.id)])
                             logger.warning("------------------------travel,mileage,edit is (%s,%s,%s)------------------------",travel_product.quick_id,mileage_product.quick_id,edit_product.quick_id)
                        else:
                             travel_product = self.env['product.product'].sudo().search([('name','=','Travelling For Trans'),('company_id','=',company.id)])
                             mileage_product = self.env['product.product'].sudo().search([('name','=','Mileage For Trans'),('company_id','=',company.id)])
                             edit_product = self.env['product.product'].sudo().search([('name','=','Total Edited For Trans'),('company_id','=',company.id)])
                        flag = False
                        base_amount = line.quantity * line.price_unit
                        travel_amount = line.travel_time * line.travelling_rate
                        mileage_amount = line.mileage * line.mileage_rate
                        base += base_amount
                        travel += travel_amount
                        mileage += mileage_amount
                        discount += line.discount
                        product_vals = {"Description": line.name,
                                        "DetailType": "SalesItemLineDetail",
                                        "SalesItemLineDetail": {
                                            "Qty": line.quantity,
                                            "UnitPrice": line.price_unit,
                                            "ItemRef": {
                                                "value": line.product_id.quick_id,
                                            }
                                        },
                                        "Amount": base_amount,
                                        }
                        lines.append(product_vals)
                        if line.total_editable > 0:
                            flag = True
                           # total_edited = line.total_editable-line.price_subtotal
                            #total_edited1 = (base_amount + travel_amount + mileage_amount)
                            #if total_edited1 >line.total_editable:
                             #   total_edited = line.total_editable - (base_amount + travel_amount + mileage_amount)
                           # if total_edited1 < line.total_editable:
                            #    total_edited = line.total_editable - (base_amount + travel_amount + mileage_amount)
                            #flag = True
                            total_edited = line.total_editable - (base_amount + travel_amount + mileage_amount)
                            edit_vals = {"Description": edit_product.name,
                                            "DetailType": "SalesItemLineDetail",
                                            "SalesItemLineDetail": {
                                                "Qty": '1',
                                                "UnitPrice": total_edited,
                                                "ItemRef": {
                                                    "value": edit_product.quick_id,
                                                }
                                            },
                                            "Amount": total_edited,
                                            }
                            lines.append(edit_vals)
                        if travel_amount > 0 and not flag:
                            travel_vals = {"Description": travel_product.name,
                                           "DetailType": "SalesItemLineDetail",
                                           "SalesItemLineDetail": {
                                               "Qty": line.travel_time,
                                               "UnitPrice": line.travelling_rate,
                                               "ItemRef": {
                                                   "value": travel_product.quick_id,
                                               }
                                           },
                                           "Amount": travel_amount,
                                           }
                            lines.append(travel_vals)
                        if mileage_amount > 0 and not flag:
                            mileage_vals = {"Description": mileage_product.name,
                                            "DetailType": "SalesItemLineDetail",
                                            "SalesItemLineDetail": {
                                                "Qty": line.mileage,
                                                "UnitPrice": line.mileage_rate,
                                                "ItemRef": {
                                                    "value": mileage_product.quick_id,
                                                }
                                            },
                                            "Amount": mileage_amount,
                                       }
                            lines.append(mileage_vals)
                    if discount > 0 and not flag:
                        discount_vals = {"DetailType": "DiscountLineDetail",
                                         "DiscountLineDetail":
                                             {
                                                 "PercentBased": True,
                                                 "DiscountPercent": discount
                                             }
                                         }
                        lines.append(discount_vals)
                    interpret = location = service_date = service = ''
                    for interpreter in invoice.event_id.assigned_interpreters:
                        name = str(interpreter.name)
                        interpret += name +', '
                    interpret.replace('and','/')
                    length = len(interpret)
                    if length >31:
                        a = length-31
                        interpret = interpret[:-a]
                    if invoice.event_id:
                        service_date = invoice.event_id.event_start_date
                        service = invoice.event_id.event_purpose
                    if invoice.location_id:
                        if invoice.location_id.street:
                            location += invoice.location_id.street + ','
                        if invoice.location_id.city:
                            location += invoice.location_id.city + ','
                        if invoice.location_id.zip:
                            location += invoice.location_id.zip + ','
                    # incoice_date = invoice.date_invoice
                    memo = 'Base :- '+str(base)+', '+'Mileage :- '+str(mileage)+', '+'Travel :- '+str(travel)+', '+'Date Of Service :- '+service_date+', '
                    memo += 'Service :- '+service+', '+'Location :- '+location
                    vals = {
                        "CustomerRef": {
                            "value": invoice.partner_id.quick_id,
                        },
                        "TxnDate":invoice.date_invoice,
                        "DueDate": invoice.date_due,
                        "DocNumber":invoice.number or '',
                        "TotalAmt": invoice.amount_total,
                        "Line": lines,
                        "CustomerMemo": {
                            "value": memo,
                        },
                        "CustomField": [
                             {
                                 "DefinitionId": "1",
                                 "StringValue": interpret,
                                 "Type": "StringType",
                                 "Name": "Interpreter"
                             },
                             {
                                 "DefinitionId": "2",
                                 "StringValue": invoice.origin,
                                 "Type": "StringType",
                                 "Name": "Event",
                             },
                             {
                                 "DefinitionId": "3",
                                 "StringValue": invoice.language_id.name,
                                 "Type": "StringType",
                                 "Name": "Language"
                             },
                        ],
                    }
                    if invoice.partner_id.email or invoice.partner_id.email2:
                       vals.update({"BillEmail": {
                            "Address": invoice.partner_id.email  or invoice.partner_id.email2,
                        }})
                  #  if invoice.in_qb:
                   #    vals.update({"Id": invoice.quick_id})
		    if invoice.in_qb:
                        exist_quick_id=invoice.quick_id
			logger.warning('quick id in ERP------ %s ---- ',invoice.quick_id)
                        exist_post_url =post_url_cust + company.quick_id + "/invoice/" + exist_quick_id + "?minorversion=45"
                        read_invoice = requests.get(exist_post_url, headers=headers)
                        response_data = json.dumps(xmltodict.parse(read_invoice.text))
                       # logger.warning('response_data------ %s ---- ',response_data)
			key_vals = json.loads(response_data)
		        #logger.warning('key_vals---- %s ---- ',key_vals)
		        update_synctoken=key_vals['IntuitResponse']['Invoice']['SyncToken']
                        logger.warning('update_synctoken---- %s ---- ', update_synctoken)
                        vals.update({"Id": invoice.quick_id,"SyncToken":update_synctoken}) 
		        logger.warning('Update Invoice With ID---- %s ---- ', invoice.id) 
                    data = json.dumps(vals)
                    export_invoice = requests.post(post_url, data=data, headers=headers)
                    response_data = json.dumps(xmltodict.parse(export_invoice.text))
                    key_vals = json.loads(response_data)
                    qb_id = key_vals['IntuitResponse']['Invoice']['Id']
                    invoice.sudo().write({'in_qb': True, 'quick_id': qb_id})
                    self._cr.commit()
                    logger.warning('Exported Invoice With ID---- %s ---- ', invoice.id)
            except Exception as e:
                logger.error('I am in export_invoice_qb() and Error is---- %s ---- ', e)
                logger.error('I am in export_invoice_qb() and Error in Response is---- %s ---- and Partner Quick-Id is ----%s-----', export_invoice.text,invoice.partner_id.quick_id)
   
    @api.multi
    def update_export_invoice_qb(self, company, access_token):
        logger.warning("------------------------I am in update_export_invoice_qb()------------------------")
        env = 'sandbox'
        post_url = "https://sandbox-quickbooks.api.intuit.com/v3/company/" + company.quick_id + "/invoice?minorversion=4"
        configs = self.sudo().search([])
        if configs.production:
            env = 'production'
            post_url = "https://quickbooks.api.intuit.com/v3/company/" + company.quick_id + "/invoice?minorversion=4"
        auth_header = 'Bearer {0}'.format(access_token)
        headers = {'Authorization': auth_header, 'content-type': 'application/json'}
        # if configs.from_range and configs.to_range:
        #    date_from = configs.from_range[:-8]
        #    from_date = date_from + '00:00:00'
        #    date_to = configs.to_range[:-8]
        #    to_date = date_to + '00:00:00'
        #    invoices = self.env['account.invoice'].sudo().search([
        #        ('company_id','=',company.id),('in_qb','=',False),('state','in',('open','draft')),
        #        ('partner_id.cust_type','in',('customer','contact','company')),
        #        ('create_date','>=',from_date),('create_date','<=',to_date)])
        # else:
        #    invoices = self.env['account.invoice'].sudo().search([('company_id', '=', company.id), ('in_qb', '=', False), ('state', '=', 'paid')])
        # date_from = configs.from_range[:-8]
        # from_date = date_from
        # date_to = configs.to_range[:-8]
        # to_date = date_to
        # logger.warning("------------------------Date From-------------Date To-----------%s----------%s",date_from,date_to)
        # invoices = self.env['account.invoice'].sudo().search([('type','=','out_invoice'),('state','=','open'),('in_qb','=',False),('date_invoice','>','2019-12-31'),('company_id','=',company.id)])
        update_invoices = []
        time = (datetime.now() - timedelta(minutes=80)).strftime('%Y-%m-%d %H:%M:%S')
        # invoices_1 = self.env['account.invoice'].sudo().search(
        #     [('date_invoice', '>', '2019-12-31'), ('state', '=', 'open'), ('type', '=', 'out_invoice'),
        #      ('company_id', '=', company.id), ('in_qb', '=', False)])
        # # if invoices_1:
        # #     for invoice in invoices_1:
        # invoices.extend(invoices_1)
        # logger.warning("------------------------Invoices Type (%s)------------------------", type(invoices))
        update_invoice_ids = self.env['account.invoice'].sudo().search(
            [('write_date', '>=', time), ('type', '=', 'out_invoice'), ('company_id', '=', company.id),
             ('in_qb', '=', True)])
        update_invoices.extend(update_invoice_ids)
        logger.warning("------------------------The Count of update Invoices to Export is (%s)------------------------",
                       len(update_invoices))
        post_url_cust = "https://sandbox-quickbooks.api.intuit.com/v3/company/"
        configs = self.sudo().search([])
        if configs.production:
            post_url_cust = "https://quickbooks.api.intuit.com/v3/company/"
        cust_url = post_url_cust + company.quick_id + '/customer?minorversion=4'
        vend_url = post_url_cust + company.quick_id + '/vendor?minorversion=4'
        for invoice in update_invoices:
            try:
                if not invoice.partner_id.in_qb:
                    record = invoice.partner_id
                    flag = False
                    try:
                        state = country = title = ' '
                        if record.state_id:
                            state = record.state_id.name
                        if record.country_id:
                            country = record.country_id.name
                        if record.title:
                            title = record.title.name

                        vals = {
                            "Suffix": record.ref + '-' + str(record.id),
                            "Title": title,
                            "MiddleName": record.middle_name or '',
                            "Notes": "IUG Customer",
                            "FamilyName": record.last_name or '',
                            "PrimaryPhone": {
                                "FreeFormNumber": record.phone
                            },
                            "Mobile": {
                                "FreeFormNumber": record.mobile
                            },
                            "BillAddr": {
                                "CountrySubDivisionCode": state,
                                "City": record.city,
                                "PostalCode": record.zip,
                                "Line1": record.street,
                                "Line2": record.street2,
                                "Country": country
                            },
                            "GivenName": record.name
                        }
                        if record.email or record.email2:
                            vals.update({"PrimaryEmailAddr": {
                                "Address": record.email or record.email2
                            }})
                        data = json.dumps(vals)
                        flag = True
                        export = requests.post(cust_url, data=data, headers=headers)
                        response_data = json.dumps(xmltodict.parse(export.text))
                        key_vals = json.loads(response_data)
                        qb_id = key_vals['IntuitResponse']['Customer']['Id']
                        record.sudo().write({'in_qb': True, 'quick_id': qb_id})
                        self._cr.commit()
                        logger.warning('Exported Partner With ID---- %s ---- ', record.id)
                    except Exception as e:
                        if flag:
                            issue = export.text
                            if "Email Address does not conform to the syntax rules of RFC 822" in issue:
                                try:
                                    logger.warning('------------------Inside Email Exception----------')
                                    vals.pop('PrimaryEmailAddr', None)
                                    data = json.dumps(vals)
                                    if not record.customer:
                                        export = requests.post(vend_url, data=data, headers=headers)
                                        response_data = json.dumps(xmltodict.parse(export.text))
                                        key_vals = json.loads(response_data)
                                        qb_id = key_vals['IntuitResponse']['Vendor']['Id']
                                        record.sudo().write({'in_qb': True, 'quick_id': qb_id})
                                        self._cr.commit()
                                        logger.warning('Exported Partner Without Email and  ID---- %s ---- ', record.id)
                                    else:
                                        export = requests.post(cust_url, data=data, headers=headers)
                                        response_data = json.dumps(xmltodict.parse(export.text))
                                        key_vals = json.loads(response_data)
                                        qb_id = key_vals['IntuitResponse']['Customer']['Id']
                                        record.sudo().write({'in_qb': True, 'quick_id': qb_id})
                                        self._cr.commit()
                                        logger.warning('Exported Partner Without Email and ID---- %s ---- ', record.id)
                                except Exception as e:
                                    logger.warning('Error in Email Exception---- %s ---- ', e)
                            else:
                                logger.error('I am in export_partners() and Error with %s and the issue is -- %s ',
                                             record.id, export.text)
                        else:
                            logger.error('I am in export_partners() and Error with %s and the issue is -- %s ',
                                         record.id,
                                         export.text)
                invoice = self.env['account.invoice'].browse(invoice.id)
                if invoice.partner_id.in_qb:
                    lines = []
                    base = mileage = travel = discount = 0.0
                    # travel_product = self.env['product.product'].sudo().search([('name','=','Travelling ACD'),('company_id','=',company.id)])
                    # mileage_product = self.env['product.product'].sudo().search([('name','=','Mileage ACD'),('company_id','=',company.id)])
                    # edit_product = self.env['product.product'].sudo().search([('name','=','Total Edited ACD'),('company_id','=',company.id)])
                    for line in invoice.invoice_line_ids:
                        if line.product_id.service_type == 'interpreter':
                            travel_product = self.env['product.product'].sudo().search(
                                [('name', '=', 'Travelling For Interp'), ('company_id', '=', company.id)])
                            mileage_product = self.env['product.product'].sudo().search(
                                [('name', '=', 'Mileage For Interp'), ('company_id', '=', company.id)])
                            edit_product = self.env['product.product'].sudo().search(
                                [('name', '=', 'Total Edited For Interp'), ('company_id', '=', company.id)])
                            logger.warning(
                                "------------------------travel,mileage,edit is (%s,%s,%s)------------------------",
                                travel_product.quick_id, mileage_product.quick_id, edit_product.quick_id)
                        else:
                            travel_product = self.env['product.product'].sudo().search(
                                [('name', '=', 'Travelling For Trans'), ('company_id', '=', company.id)])
                            mileage_product = self.env['product.product'].sudo().search(
                                [('name', '=', 'Mileage For Trans'), ('company_id', '=', company.id)])
                            edit_product = self.env['product.product'].sudo().search(
                                [('name', '=', 'Total Edited For Trans'), ('company_id', '=', company.id)])
                        flag = False
                        base_amount = line.quantity * line.price_unit
                        travel_amount = line.travel_time * line.travelling_rate
                        mileage_amount = line.mileage * line.mileage_rate
                        base += base_amount
                        travel += travel_amount
                        mileage += mileage_amount
                        discount += line.discount
                        product_vals = {"Description": line.name,
                                        "DetailType": "SalesItemLineDetail",
                                        "SalesItemLineDetail": {
                                            "Qty": line.quantity,
                                            "UnitPrice": line.price_unit,
                                            "ItemRef": {
                                                "value": line.product_id.quick_id,
                                            }
                                        },
                                        "Amount": base_amount,
                                        }
                        lines.append(product_vals)
                        if line.total_editable > 0:
                            flag = True
                            #total_edited = line.total_editable - line.price_subtotal
                            total_edited = line.total_editable - (base_amount + travel_amount + mileage_amount)
                            # total_edited1 = (base_amount + travel_amount + mileage_amount)
                            # if total_edited1 > line.total_editable:
                            #     total_edited = line.total_editable - (base_amount + travel_amount + mileage_amount)
                            # if total_edited1 < line.total_editable:
                            #     total_edited = line.total_editable - (base_amount + travel_amount + mileage_amount)
                            edit_vals = {"Description": edit_product.name,
                                         "DetailType": "SalesItemLineDetail",
                                         "SalesItemLineDetail": {
                                             "Qty": '1',
                                             "UnitPrice": total_edited,
                                             "ItemRef": {
                                                 "value": edit_product.quick_id,
                                             }
                                         },
                                         "Amount": total_edited,
                                         }
                            lines.append(edit_vals)
                        if travel_amount > 0 and not flag:
                            travel_vals = {"Description": travel_product.name,
                                           "DetailType": "SalesItemLineDetail",
                                           "SalesItemLineDetail": {
                                               "Qty": line.travel_time,
                                               "UnitPrice": line.travelling_rate,
                                               "ItemRef": {
                                                   "value": travel_product.quick_id,
                                               }
                                           },
                                           "Amount": travel_amount,
                                           }
                            lines.append(travel_vals)
                        if mileage_amount > 0 and not flag:
                            mileage_vals = {"Description": mileage_product.name,
                                            "DetailType": "SalesItemLineDetail",
                                            "SalesItemLineDetail": {
                                                "Qty": line.mileage,
                                                "UnitPrice": line.mileage_rate,
                                                "ItemRef": {
                                                    "value": mileage_product.quick_id,
                                                }
                                            },
                                            "Amount": mileage_amount,
                                            }
                            lines.append(mileage_vals)
                    if discount > 0 and not flag:
                        discount_vals = {"DetailType": "DiscountLineDetail",
                                         "DiscountLineDetail":
                                             {
                                                 "PercentBased": True,
                                                 "DiscountPercent": discount
                                             }
                                         }
                        lines.append(discount_vals)
                    interpret = location = service_date = service = ''
                    for interpreter in invoice.event_id.assigned_interpreters:
                        name = str(interpreter.name)
                        interpret += name + ', '
                    interpret.replace('and', '/')
                    length = len(interpret)
                    if length > 31:
                        a = length - 31
                        interpret = interpret[:-a]
                    if invoice.event_id:
                        service_date = invoice.event_id.event_start_date
                        service = invoice.event_id.event_purpose
                    if invoice.location_id:
                        if invoice.location_id.street:
                            location += invoice.location_id.street + ','
                        if invoice.location_id.city:
                            location += invoice.location_id.city + ','
                        if invoice.location_id.zip:
                            location += invoice.location_id.zip + ','
                    # incoice_date = invoice.date_invoice
                    memo = 'Base :- ' + str(base) + ', ' + 'Mileage :- ' + str(mileage) + ', ' + 'Travel :- ' + str(
                        travel) + ', ' + 'Date Of Service :- ' + service_date + ', '
                    memo += 'Service :- ' + service + ', ' + 'Location :- ' + location
                    vals = {
                        "CustomerRef": {
                            "value": invoice.partner_id.quick_id,
                        },
                        "TxnDate": invoice.date_invoice,
                        "DueDate": invoice.date_due,
                        "DocNumber": invoice.number or '',
                        "TotalAmt": invoice.amount_total,
                        "Line": lines,
                        "CustomerMemo": {
                            "value": memo,
                        },
                        "CustomField": [
                            {
                                "DefinitionId": "1",
                                "StringValue": interpret,
                                "Type": "StringType",
                                "Name": "Interpreter"
                            },
                            {
                                "DefinitionId": "2",
                                "StringValue": invoice.origin,
                                "Type": "StringType",
                                "Name": "Event",
                            },
                            {
                                "DefinitionId": "3",
                                "StringValue": invoice.language_id.name,
                                "Type": "StringType",
                                "Name": "Language"
                            },
                        ],
                    }
                    if invoice.partner_id.email or invoice.partner_id.email2:
                        vals.update({"BillEmail": {
                            "Address": invoice.partner_id.email or invoice.partner_id.email2,
                        }})
                    if invoice.in_qb:
                        exist_quick_id = invoice.quick_id
                        logger.warning('quick id in ERP------ %s ---- ', invoice.quick_id)
                        exist_post_url = post_url_cust + company.quick_id + "/invoice/" + exist_quick_id + "?minorversion=45"
                        read_invoice = requests.get(exist_post_url, headers=headers)
                        response_data = json.dumps(xmltodict.parse(read_invoice.text))
                        # logger.warning('response_data------ %s ---- ',response_data)
                        key_vals = json.loads(response_data)
                        # logger.warning('key_vals---- %s ---- ',key_vals)
                        update_synctoken = key_vals['IntuitResponse']['Invoice']['SyncToken']
                        logger.warning('update_synctoken---- %s ---- ', update_synctoken)
                        vals.update({"Id": invoice.quick_id, "SyncToken": update_synctoken})
                        logger.warning('Update Invoice With ID---- %s ---- ', invoice.id)
                    data = json.dumps(vals)
                    export_invoice = requests.post(post_url, data=data, headers=headers)
                    response_data = json.dumps(xmltodict.parse(export_invoice.text))
                    key_vals = json.loads(response_data)
                    qb_id = key_vals['IntuitResponse']['Invoice']['Id']
                    invoice.sudo().write({'in_qb': True, 'quick_id': qb_id})
                    self._cr.commit()
                    logger.warning('Exported Invoice With ID---- %s ---- ', invoice.id)
            except Exception as e:
                logger.error('I am in export_invoice_qb() and Error is---- %s ---- ', e)
                logger.error(
                    'I am in export_invoice_qb() and Error in Response is---- %s ---- and Partner Quick-Id is ----%s-----',
                    export_invoice.text, invoice.partner_id.quick_id)


    @api.multi
    def export_invoices(self):
        logger.warning("------------------------I am in export_invoices()------------------------")
        configs = self.sudo().search([], limit=1)
        if configs:
            companies = self.env['res.company'].sudo().search([])
            for company in companies:
                try:
                    if company.in_qb:
                        access_token = self.refresh_api_token(company)
                        export = self.export_invoice_qb(company, access_token)
                except Exception as e:
                    logger.error('I am in export_invoices() and Error is---- %s ---- ', e)
        else:
            logger.error("No Credentials found for QuickBook")

    @api.multi
    def update_export_invoices(self):
        logger.warning("------------------------I am in updateexport_invoices()------------------------")
        configs = self.sudo().search([], limit=1)
        if configs:
            companies = self.env['res.company'].sudo().search([])
            for company in companies:
                try:
                    if company.in_qb:
                        access_token = self.refresh_api_token(company)
                        export = self.update_export_invoice_qb(company, access_token)
                except Exception as e:
                    logger.error('I am in update_export_invoices() and Error is---- %s ---- ', e)
        else:
            logger.error("No Credentials found for QuickBook")

    @api.multi
    def create_bills(self,company,bills):
        logger.warning("------------------------I am in create_bills()------------------------")
        customer = ['customer', 'contact', 'company']
        event = False
        for bill in bills:
            try:
                bill_exist = self.env['account.invoice'].sudo().search([('quick_id', '=', bill.Id)])
                lines = []
                partner = self.env['res.partner'].sudo().search([('company_id','=',company.id),('quick_id', '=', bill.VendorRef.value),('cust_type','not in',('customer', 'contact', 'company'))])
                currency = self.env['res.currency'].sudo().search([('name', '=', 'USD')]).id
                if partner.cust_type in customer:
                    journal = self.env['account.journal'].sudo().search(
                        [('name', '=', 'Sales Journal'), ('company_id', '=', company.id)]).id
                else:
                    journal = self.env['account.journal'].sudo().search(
                        [('name', '=', 'Purchase Journal'), ('company_id', '=', company.id)]).id
                if bill.PrivateNote:
                    event = self.env['event'].sudo().search([('company_id','=',company.id),('name', '=',bill.PrivateNote.strip())]).id
                bill_vals = {'partner_id': partner.id,
                             'currency_id': currency,
                             'journal_id': journal,
                             'event_id': event if event else False,
                             'quick_id': bill.Id,
                             'in_qb': True,
                             'origin': bill.PrivateNote,
                             'type':'in_invoice',
                             'company_id': company.id,
                             }
                logger.warning("------------------------Bill Vals Ready------------------------")
                for bill_line in bill.Line:
                    if bill_line.DetailType == 'ItemBasedExpenseLineDetail':
                        pro_name = bill_line.ItemBasedExpenseLineDetail.ItemRef.name
                        product = self.env['product.product'].sudo().search([('company_id','=',company.id),('quick_id', '=', bill_line.ItemBasedExpenseLineDetail.ItemRef.value)])
                        logger.warning("------------------------Got the Products------------------------")
                        if partner.cust_type in customer:
                            account = product.property_account_income_id.id
                        else:
                            account = product.property_account_expense_id.id
                        logger.warning("------------------------Got the accounts------------------------")
                        line_vals = {'product_id': product.id,
                                     'name': bill_line.Description if bill_line.Description != None else product.name,
                                     'account_id': account,
                                     'quantity': int(bill_line.ItemBasedExpenseLineDetail.Qty),
                                     'price_unit': int(bill_line.ItemBasedExpenseLineDetail.UnitPrice),
                                     }
                        logger.warning("------------------------Bill lIne Vals Ready------------------------")
                        if bill_exist:
                            for all_lines in bill_exist.invoice_line_ids:
                                if pro_name == all_lines.product_id.name:
                                    bill_vals.update({'invoice_line_ids': [(1, all_lines.id, line_vals)]})
                                    bill_exist.write(bill_vals)
                        else:
                            if not product.for_qb:
                                lines.append((0, 0, line_vals))
                if not bill_exist:
                    logger.warning("------------------------Going to create BIll------------------------")
                    bill_vals.update({'invoice_line_ids': lines})
                    bill_exist = self.env['account.invoice'].create(bill_vals)
                self._cr.commit()
                logger.warning('Imported Bill is--%s-- with Qb-ID--%s--', bill_exist.id, bill.Id)
            except Exception as e:
                logger.error('Error is---- %s ---- ', e)

    @api.multi
    def import_bills(self):
        logger.warning("------------------------I am in import_bills()------------------------")
        configs = self.sudo().search([], limit=1)
        if configs:
            companies = self.env['res.company'].sudo().search([])
            for company in companies:
                try:
                    if company.in_qb:
                        client = self.get_client(company)
                        current_day = datetime.today() - timedelta(days=1)
                        # current_day = (datetime.now() - timedelta(minutes=65))
                        tz = pytz.timezone("America/Toronto")
                        aware_dt = tz.localize(current_day)
                        query_date = aware_dt.isoformat()
                        query = "SELECT * FROM bill WHERE MetaData.CreateTime >='" + query_date + "' ""STARTPOSITION 1 MAXRESULTS 1000"
                        bills = Bill.query(query, qb=client)
                        if bills:
                            self.create_bills(company, bills)
                except Exception as e:
                    logger.error('Error is---- %s ---- ', e)
        else:
            logger.error("No Credentials found for QuickBook")

    @api.multi
    def export_bills_qb(self,company,access_token):
        logger.warning("------------------------I am in export_bills_qb()------------------------")
        bill_category = []
        env = 'sandbox'
        post_url = "https://sandbox-quickbooks.api.intuit.com/v3/company/" + company.quick_id + "/bill?minorversion=4"
        configs = self.sudo().search([])
        if configs.production:
            env = 'production'
            post_url = "https://quickbooks.api.intuit.com/v3/company/" + company.quick_id + "/bill?minorversion=4"
        auth_header = 'Bearer {0}'.format(access_token)
        headers = {'Authorization': auth_header, 'content-type': 'application/json'}
        # if configs.from_range and configs.to_range:
        #     date_from = configs.from_range[:-8]
        #     from_date = date_from + '00:00:00'
        #     date_to = configs.to_range[:-8]
        #     to_date = date_to + '00:00:00'
        #     bills = self.env['account.invoice'].sudo().search(
        #         [('company_id', '=', company.id), ('in_qb', '=', False),('state', 'in', ('open', 'draft')),
        #          ('partner_id.cust_type','in',('interpreter','transporter','translator','interp_and_transl')),
        #          ('create_date', '>=', from_date), ('create_date', '<=', to_date)
        #          ])
        # else:
        #     bills = self.env['account.invoice'].sudo().search([('company_id', '=', company.id), ('in_qb', '=', False), ('state', '=', 'paid')])
        bills=[]
        #time = (datetime.now() - timedelta(minutes=65)).strftime('%Y-%m-%d %H:%M:%S')
        bills_1 = self.env['account.invoice'].sudo().search([('date_invoice', '>', '2019-12-31'),
                                                             ('state', '=', 'open'), ('type', '=', 'in_invoice'),
                                                             ('company_id', '=', company.id), ('in_qb', '=', False),
                                                            ])
        bills.extend(bills_1)
       # bills_2 = self.env['account.invoice'].sudo().search([('type', '=', 'in_invoice'),
        #                                                   ('company_id', '=', company.id), ('in_qb', '=', True),
         #                                                  ('write_date', '>=', time)])
        #bills.extend(bills_2)
        #logger.warning("------------------------The Count of Bills to Export is (%s)------------------------",len(bills))
        # date_from = configs.from_range[:-8]
        # from_date = date_from
        # date_to = configs.to_range[:-8]
        # to_date = date_to
        #bills = self.env['account.invoice'].sudo().search([('type','=','in_invoice'),('state','=','open'),('in_qb','=',False),('date_invoice','>','2019-12-31'),('company_id', '=', company.id)])
        logger.warning("------------------------The Count of Bills to Export is (%s)------------------------",len(bills))
        post_url_cust = "https://sandbox-quickbooks.api.intuit.com/v3/company/"
        configs = self.sudo().search([])
        if configs.production:
            post_url_cust = "https://quickbooks.api.intuit.com/v3/company/"
        cust_url = post_url_cust + company.quick_id + '/customer?minorversion=4'
        vend_url = post_url_cust + company.quick_id + '/vendor?minorversion=4'
        for bill in bills:
            if not bill.partner_id.in_qb:
                    record=bill.partner_id
                    flag = False
                    try:
                        vals={}
                        state = country = title = ' '
                        if record.state_id:
                            state = record.state_id.name
                        if record.country_id:
                            country = record.country_id.name
                        if record.title:
                            title = record.title.name
                        name = ''
                        if record.name:
                            name += record.name + ' '
                        if record.middle_name:
                            name += record.middle_name + ' '
                        if record.last_name:
                            name += record.last_name
                        vals = {
                            "Suffix": record.ref + '-' + str(record.id),
                            "Title": title,
                            "MiddleName": record.middle_name or '',
                            "Notes": "IUG Customer",
                            "FamilyName": record.last_name or '',
                            "PrimaryPhone": {
                                "FreeFormNumber": record.phone
                            },
                            "Mobile": {
                                "FreeFormNumber": record.mobile
                            },
                            "BillAddr": {
                                "CountrySubDivisionCode": state,
                                "City": record.city,
                                "PostalCode": record.zip,
                                "Line1": record.street,
                                "Line2": record.street2,
                                "Country": country
                            },
                            "GivenName": record.name,
                            "PrintOnCheckName": name
                        }
                        if record.email or record.email2:
                            vals.update({"PrimaryEmailAddr": {
                                "Address": record.email or record.email2
                            }})
                        data = json.dumps(vals)
                        flag = True
                        export = requests.post(vend_url, data=data, headers=headers)
                        response_data = json.dumps(xmltodict.parse(export.text))
                        key_vals = json.loads(response_data)
                        qb_id = key_vals['IntuitResponse']['Vendor']['Id']
                        record.sudo().write({'in_qb': True, 'quick_id': qb_id})
                        self._cr.commit()
                        logger.warning('Exported Partner With ID---- %s ---- ', record.id)
                    except Exception as e:
                        if flag:
                            issue = export.text
                            if "Email Address does not conform to the syntax rules of RFC 822" in issue:
                                try:
                                    logger.warning('------------------Inside Email Exception----------')
                                    vals.pop('PrimaryEmailAddr', None)
                                    data = json.dumps(vals)
                                    if not record.customer:
                                        export = requests.post(vend_url, data=data, headers=headers)
                                        response_data = json.dumps(xmltodict.parse(export.text))
                                        key_vals = json.loads(response_data)
                                        qb_id = key_vals['IntuitResponse']['Vendor']['Id']
                                        record.sudo().write({'in_qb': True, 'quick_id': qb_id})
                                        self._cr.commit()
                                        logger.warning('Exported Partner Without Email and  ID---- %s ---- ', record.id)
                                    else:
                                        export = requests.post(cust_url, data=data, headers=headers)
                                        response_data = json.dumps(xmltodict.parse(export.text))
                                        key_vals = json.loads(response_data)
                                        qb_id = key_vals['IntuitResponse']['Customer']['Id']
                                        record.sudo().write({'in_qb': True, 'quick_id': qb_id})
                                        self._cr.commit()
                                        logger.warning('Exported Partner Without Email and ID---- %s ---- ', record.id)
                                except Exception as e:
                                    logger.warning('Error in Email Exception---- %s ---- ', e)
                            else:
                                logger.error('I am in export_partners() and Error with %s and the issue is -- %s ',
                                             record.id, export.text)
                        else:
                            logger.error('I am in export_partners() and Error with %s and the issue is -- %s ',
                                         record.id, export.text)
            try:
                bill=self.env['account.invoice'].browse(bill.id)
                if bill.partner_id.in_qb:
                    vals = {}
                    lines = []
                    base = mileage = travel = discount = 0.0
                    # travel_product = self.env['product.product'].sudo().search([('name', '=', 'Travelling ACD'),('company_id','=',company.id)])
                    # mileage_product = self.env['product.product'].sudo().search([('name', '=', 'Mileage ACD'),('company_id','=',company.id)])
                    # edit_product = self.env['product.product'].sudo().search([('name', '=', 'Total Edited ACD'),('company_id','=',company.id)])
                    for line in bill.invoice_line_ids:
                        logger.warning('Exported Bill With ID---- %s ---- ', bill.id)
                        if line.product_id.service_type=='interpreter':
                             travel_product = self.env['product.product'].sudo().search([('name','=','Travelling For Interp'),('company_id','=',company.id)])
                             mileage_product = self.env['product.product'].sudo().search([('name','=','Mileage For Interp'),('company_id','=',company.id)])
                             edit_product = self.env['product.product'].sudo().search([('name','=','Total Edited For Interp'),('company_id','=',company.id)])
                             logger.warning("------------------------travel,mileage,edit is (%s,%s,%s)------------------------",travel_product.quick_id,mileage_product.quick_id,edit_product.quick_id)
                        else:
                             travel_product = self.env['product.product'].sudo().search([('name','=','Travelling For Trans'),('company_id','=',company.id)])
                             mileage_product = self.env['product.product'].sudo().search([('name','=','Mileage For Trans'),('company_id','=',company.id)])
                             edit_product = self.env['product.product'].sudo().search([('name','=','Total Edited For Trans'),('company_id','=',company.id)])
                        flag = False
                        base_amount = line.quantity * line.price_unit
                        travel_amount = line.travel_time * line.travelling_rate
                        mileage_amount = line.mileage * line.mileage_rate
                        base += base_amount
                        travel += travel_amount
                        mileage += mileage_amount
                        discount += line.discount
                        logger.warning('Exported Bill With product ID---- %s ---- ',line.product_id.id)
                        product_vals = {"Description": line.name,
                                        "DetailType": "ItemBasedExpenseLineDetail",
                                        "ItemBasedExpenseLineDetail": {
                                            "Qty": line.quantity,
                                            "UnitPrice": line.price_unit,
                                            "ItemRef": {
                                                "value": line.product_id.quick_id,
                                            }
                                        },
                                        "Amount": base_amount,
                                        }
                        lines.append(product_vals)
                        if line.total_editable > 0:
                            flag = True
                           # total_edited = line.total_editable-line.price_subtotal
                            total_edited = line.total_editable - (base_amount + travel_amount + mileage_amount)
                           # logger.warning('base_amount + travel_amount + mileage_amount) - line.total_editable----(%s,%s,%s)---- ',base_amount,travel_amount,mileage_amount,line.total_editable)
                            #total_edited1 = (base_amount + travel_amount + mileage_amount)
                            #if total_edited1 >line.total_editable:
                             #   total_edited = line.total_editable - (base_amount + travel_amount + mileage_amount)
                            #if total_edited1 < line.total_editable:
                             #   total_edited = line.total_editable - (base_amount + travel_amount + mileage_amount)
                            logger.warning('total_edited---- %s ---- ',total_edited)
                            edit_vals = {"Description": edit_product.name,
                                         "DetailType": "ItemBasedExpenseLineDetail",
                                         "ItemBasedExpenseLineDetail": {
                                             "Qty": '1',
                                             "UnitPrice": total_edited,
                                             "ItemRef": {
                                                 "value": edit_product.quick_id,
                                             }
                                         },
                                         "Amount": total_edited,
                                         }
                            logger.warning('edit_vals---- %s ---- ',edit_vals)
                            lines.append(edit_vals)
                        if travel_amount > 0 and not flag:
                            travel_vals = {"Description": travel_product.name,
                                           "DetailType": "ItemBasedExpenseLineDetail",
                                           "ItemBasedExpenseLineDetail": {
                                               "Qty": line.travel_time,
                                               "UnitPrice": line.travelling_rate,
                                               "ItemRef": {
                                                   "value": travel_product.quick_id,
                                               }
                                           },
                                           "Amount": travel_amount,
                                           }
                            lines.append(travel_vals)
                        if mileage_amount > 0 and not flag:
                            mileage_vals = {"Description": mileage_product.name,
                                            "DetailType": "ItemBasedExpenseLineDetail",
                                            "ItemBasedExpenseLineDetail": {
                                                "Qty": line.mileage,
                                                "UnitPrice": line.mileage_rate,
                                                "ItemRef": {
                                                    "value": mileage_product.quick_id,
                                                }
                                            },
                                            "Amount": mileage_amount,
                                            }
                            lines.append(mileage_vals)
                    interpret = location = service_date = service = ''
                    for interpreter in bill.event_id.assigned_interpreters:
                        name = str(interpreter.name)
                        interpret += name + ', '
                    if bill.event_id:
                        service_date = bill.event_id.event_start_date
                        service = bill.event_id.event_purpose
                    if bill.location_id:
                        if bill.location_id.street:
                            location += bill.location_id.street + ','
                        if bill.location_id.city:
                            location += bill.location_id.city + ','
                        if bill.location_id.zip:
                            location += bill.location_id.zip + ','
                    memo = 'Interpreters :- ('+interpret+'), '+'Event :- '+bill.origin+', '+'Language :- '+bill.language_id.name+', '
                    memo += 'Base :- ' + str(base) + ', ' + 'Mileage :- ' + str(mileage) + ', ' + 'Travel :- ' + str(travel) + ', ' + 'Date Of Service :- ' + service_date + ', '
                    memo += 'Service :- ' + service + ', ' + 'Location :- ' + location
                    vals = {
                        "VendorRef": {
                            "value": bill.partner_id.quick_id,
                        },
                        "TxnDate":bill.date_invoice,
                        "DocNumber":bill.number or '',
                        "DueDate": bill.date_due,
                        "PrivateNote": memo,
                        "TotalAmt": bill.amount_total,
                        "Line": lines,
                    }
                    if bill.in_qb:
                        exist_quick_id = bill.quick_id
                        logger.warning('quick id in ERP------ %s ---- ', exist_quick_id)
                        exist_post_url = post_url_cust + company.quick_id + "/bill/" + exist_quick_id + "?minorversion=45"
                        read_invoice = requests.get(exist_post_url, headers=headers)
                        response_data = json.dumps(xmltodict.parse(read_invoice.text))
                        # logger.warning('response_data------ %s ---- ',response_data)
                        key_vals = json.loads(response_data)
                        # logger.warning('key_vals---- %s ---- ',key_vals)
                        update_synctoken = key_vals['IntuitResponse']['Bill']['SyncToken']
                        logger.warning('update_synctoken---- %s ---- ', update_synctoken)
                        vals.update({"Id": bill.quick_id,"SyncToken":update_synctoken})
                    logger.warning('BIll vals----------------- With ID---- %s ---- ', vals)
                    data = json.dumps(vals)
                    export_bill = requests.post(post_url, data=data, headers=headers)
                    response_data = json.dumps(xmltodict.parse(export_bill.text))
                    key_vals = json.loads(response_data)
                    qb_id = key_vals['IntuitResponse']['Bill']['Id']
                    bill.sudo().write({'in_qb': True, 'quick_id': qb_id})
                    self._cr.commit()
                    logger.warning('Exported Bill With ID---- %s ---- ', bill.id)
            except Exception as e:
                logger.error('I am in export_bills_qb() and Error is---- %s ---- ', e)
                logger.error(
                    'I am in export_bills_qb() and Error in Response is---- %s ---- and Partner Quick-Id is ----%s-----',
                    export_bill.text, bill.partner_id.quick_id)

    @api.multi
    def export_bills(self):
        logger.warning("------------------------I am in export_bills()------------------------")
        configs = self.sudo().search([], limit=1)
        if configs:
            companies = self.env['res.company'].sudo().search([])
            for company in companies:
                try:
                    if company.in_qb:
                        access_token = self.refresh_api_token(company)
                        export = self.export_bills_qb(company, access_token)
                except Exception as e:
                    logger.error('I am in export_bills() and Error is---- %s ---- ', e)
        else:
            logger.error("No Credentials found for QuickBook")

    @api.multi
    def update_export_bills_qb(self, company, access_token):
        logger.warning("------------------------I am in update_export_bills_qb()------------------------")
        bill_category = []
        env = 'sandbox'
        post_url = "https://sandbox-quickbooks.api.intuit.com/v3/company/" + company.quick_id + "/bill?minorversion=4"
        configs = self.sudo().search([])
        if configs.production:
            env = 'production'
            post_url = "https://quickbooks.api.intuit.com/v3/company/" + company.quick_id + "/bill?minorversion=4"
        auth_header = 'Bearer {0}'.format(access_token)
        headers = {'Authorization': auth_header, 'content-type': 'application/json'}
        # if configs.from_range and configs.to_range:
        #     date_from = configs.from_range[:-8]
        #     from_date = date_from + '00:00:00'
        #     date_to = configs.to_range[:-8]
        #     to_date = date_to + '00:00:00'
        #     bills = self.env['account.invoice'].sudo().search(
        #         [('company_id', '=', company.id), ('in_qb', '=', False),('state', 'in', ('open', 'draft')),
        #          ('partner_id.cust_type','in',('interpreter','transporter','translator','interp_and_transl')),
        #          ('create_date', '>=', from_date), ('create_date', '<=', to_date)
        #          ])
        # else:
        #     bills = self.env['account.invoice'].sudo().search([('company_id', '=', company.id), ('in_qb', '=', False), ('state', '=', 'paid')])
        update_bills = []
        time = (datetime.now() - timedelta(minutes=80)).strftime('%Y-%m-%d %H:%M:%S')
        #bills_1 = self.env['account.invoice'].sudo().search([('date_invoice', '>', '2019-12-31'),
         #                                                    ('state', '=', 'open'), ('type', '=', 'in_invoice'),
          #                                                   ('company_id', '=', company.id), ('in_qb', '=', False),
           #                                                  ])

        #bills.extend(bills_1)
        update_bills_2 = self.env['account.invoice'].sudo().search([('type', '=', 'in_invoice'),
                                                             ('company_id', '=', company.id), ('in_qb', '=', True),
                                                             ('write_date', '>=', time)])
        update_bills.extend(update_bills_2)
        # logger.warning("------------------------The Count of Bills to Export is (%s)------------------------",len(bills))
        # date_from = configs.from_range[:-8]
        # from_date = date_from
        # date_to = configs.to_range[:-8]
        # to_date = date_to
        # bills = self.env['account.invoice'].sudo().search([('type','=','in_invoice'),('state','=','open'),('in_qb','=',False),('date_invoice','>','2019-12-31'),('company_id', '=', company.id)])
        logger.warning("------------------------The Count of update Bills to Export is (%s)------------------------",
                       len(update_bills))
        post_url_cust = "https://sandbox-quickbooks.api.intuit.com/v3/company/"
        configs = self.sudo().search([])
        if configs.production:
            post_url_cust = "https://quickbooks.api.intuit.com/v3/company/"
        cust_url = post_url_cust + company.quick_id + '/customer?minorversion=4'
        vend_url = post_url_cust + company.quick_id + '/vendor?minorversion=4'
        for bill in update_bills:
            if not bill.partner_id.in_qb:
                record = bill.partner_id
                flag = False
                try:
                    vals = {}
                    state = country = title = ' '
                    if record.state_id:
                        state = record.state_id.name
                    if record.country_id:
                        country = record.country_id.name
                    if record.title:
                        title = record.title.name
                    name = ''
                    if record.name:
                        name += record.name + ' '
                    if record.middle_name:
                        name += record.middle_name + ' '
                    if record.last_name:
                        name += record.last_name
                    vals = {
                        "Suffix": record.ref + '-' + str(record.id),
                        "Title": title,
                        "MiddleName": record.middle_name or '',
                        "Notes": "IUG Customer",
                        "FamilyName": record.last_name or '',
                        "PrimaryPhone": {
                            "FreeFormNumber": record.phone
                        },
                        "Mobile": {
                            "FreeFormNumber": record.mobile
                        },
                        "BillAddr": {
                            "CountrySubDivisionCode": state or '',
                            "City": record.city or '',
                            "PostalCode": record.zip or '',
                            "Line1": record.street or '',
                            "Line2": record.street2 or '',
                            "Country": country or ''
                        },
                        "GivenName": record.name,
                        "PrintOnCheckName": name
                    }
                    if record.email or record.email2:
                        vals.update({"PrimaryEmailAddr": {
                            "Address": record.email or record.email2
                        }})
                    data = json.dumps(vals)
                    flag = True
                    export = requests.post(vend_url, data=data, headers=headers)
                    response_data = json.dumps(xmltodict.parse(export.text))
                    key_vals = json.loads(response_data)
                    qb_id = key_vals['IntuitResponse']['Vendor']['Id']
                    record.sudo().write({'in_qb': True, 'quick_id': qb_id})
                    self._cr.commit()
                    logger.warning('Exported Partner With ID---- %s ---- ', record.id)
                except Exception as e:
                    if flag:
                        issue = export.text
                        if "Email Address does not conform to the syntax rules of RFC 822" in issue:
                            try:
                                logger.warning('------------------Inside Email Exception----------')
                                vals.pop('PrimaryEmailAddr', None)
                                data = json.dumps(vals)
                                if not record.customer:
                                    export = requests.post(vend_url, data=data, headers=headers)
                                    response_data = json.dumps(xmltodict.parse(export.text))
                                    key_vals = json.loads(response_data)
                                    qb_id = key_vals['IntuitResponse']['Vendor']['Id']
                                    record.sudo().write({'in_qb': True, 'quick_id': qb_id})
                                    self._cr.commit()
                                    logger.warning('Exported Partner Without Email and  ID---- %s ---- ', record.id)
                                else:
                                    export = requests.post(cust_url, data=data, headers=headers)
                                    response_data = json.dumps(xmltodict.parse(export.text))
                                    key_vals = json.loads(response_data)
                                    qb_id = key_vals['IntuitResponse']['Customer']['Id']
                                    record.sudo().write({'in_qb': True, 'quick_id': qb_id})
                                    self._cr.commit()
                                    logger.warning('Exported Partner Without Email and ID---- %s ---- ', record.id)
                            except Exception as e:
                                logger.warning('Error in Email Exception---- %s ---- ', e)
                        else:
                            logger.error('I am in export_partners() and Error with %s and the issue is -- %s ',
                                         record.id, export.text)
                    else:
                        logger.error('I am in export_partners() and Error with %s and the issue is -- %s ',
                                     record.id, export.text)
            try:
                bill = self.env['account.invoice'].browse(bill.id)
                if bill.partner_id.in_qb:
                    vals = {}
                    lines = []
                    base = mileage = travel = discount = 0.0
                    # travel_product = self.env['product.product'].sudo().search([('name', '=', 'Travelling ACD'),('company_id','=',company.id)])
                    # mileage_product = self.env['product.product'].sudo().search([('name', '=', 'Mileage ACD'),('company_id','=',company.id)])
                    # edit_product = self.env['product.product'].sudo().search([('name', '=', 'Total Edited ACD'),('company_id','=',company.id)])
                    for line in bill.invoice_line_ids:
                        logger.warning('Exported Bill With ID---- %s ---- ', bill.id)
                        if line.product_id.service_type == 'interpreter':
                            travel_product = self.env['product.product'].sudo().search(
                                [('name', '=', 'Travelling For Interp'), ('company_id', '=', company.id)])
                            mileage_product = self.env['product.product'].sudo().search(
                                [('name', '=', 'Mileage For Interp'), ('company_id', '=', company.id)])
                            edit_product = self.env['product.product'].sudo().search(
                                [('name', '=', 'Total Edited For Interp'), ('company_id', '=', company.id)])
                        else:
                            travel_product = self.env['product.product'].sudo().search(
                                [('name', '=', 'Travelling For Trans'), ('company_id', '=', company.id)])
                            mileage_product = self.env['product.product'].sudo().search(
                                [('name', '=', 'Mileage For Trans'), ('company_id', '=', company.id)])
                            edit_product = self.env['product.product'].sudo().search(
                                [('name', '=', 'Total Edited For Trans'), ('company_id', '=', company.id)])
                        flag = False
                        base_amount = line.quantity * line.price_unit
                        travel_amount = line.travel_time * line.travelling_rate
                        mileage_amount = line.mileage * line.mileage_rate
                        base += base_amount
                        travel += travel_amount
                        mileage += mileage_amount
                        discount += line.discount
                        logger.warning('Exported Bill With product ID---- %s ---- ', line.product_id.id)
                        product_vals = {"Description": line.name,
                                        "DetailType": "ItemBasedExpenseLineDetail",
                                        "ItemBasedExpenseLineDetail": {
                                            "Qty": line.quantity,
                                            "UnitPrice": line.price_unit,
                                            "ItemRef": {
                                                "value": line.product_id.quick_id,
                                            }
                                        },
                                        "Amount": base_amount,
                                        }
                        lines.append(product_vals)
                        if line.total_editable > 0:
                            flag = True
                            total_edited = line.total_editable - (base_amount + travel_amount + mileage_amount)
                            #total_edited = line.total_editable - line.price_subtotal
                            # total_edited1 = (base_amount + travel_amount + mileage_amount)
                            # if total_edited1 >line.total_editable:
                            #     total_edited = line.total_editable - (base_amount + travel_amount + mileage_amount)
                            # if total_edited1 < line.total_editable:
                            #     total_edited = line.total_editable - (base_amount + travel_amount + mileage_amount)
                            edit_vals = {"Description": edit_product.name,
                                         "DetailType": "ItemBasedExpenseLineDetail",
                                         "ItemBasedExpenseLineDetail": {
                                             "Qty": '1',
                                             "UnitPrice": total_edited,
                                             "ItemRef": {
                                                 "value": edit_product.quick_id,
                                             }
                                         },
                                         "Amount": total_edited,
                                         }
                            lines.append(edit_vals)
                        if travel_amount > 0 and not flag:
                            travel_vals = {"Description": travel_product.name,
                                           "DetailType": "ItemBasedExpenseLineDetail",
                                           "ItemBasedExpenseLineDetail": {
                                               "Qty": line.travel_time,
                                               "UnitPrice": line.travelling_rate,
                                               "ItemRef": {
                                                   "value": travel_product.quick_id,
                                               }
                                           },
                                           "Amount": travel_amount,
                                           }
                            lines.append(travel_vals)
                        if mileage_amount > 0 and not flag:
                            mileage_vals = {"Description": mileage_product.name,
                                            "DetailType": "ItemBasedExpenseLineDetail",
                                            "ItemBasedExpenseLineDetail": {
                                                "Qty": line.mileage,
                                                "UnitPrice": line.mileage_rate,
                                                "ItemRef": {
                                                    "value": mileage_product.quick_id,
                                                }
                                            },
                                            "Amount": mileage_amount,
                                            }
                            lines.append(mileage_vals)
                    interpret = location = service_date = service = ''
                    for interpreter in bill.event_id.assigned_interpreters:
                        name = str(interpreter.name)
                        interpret += name + ', '
                    if bill.event_id:
                        service_date = bill.event_id.event_start_date
                        service = bill.event_id.event_purpose
                    if bill.location_id:
                        if bill.location_id.street:
                            location += bill.location_id.street + ','
                        if bill.location_id.city:
                            location += bill.location_id.city + ','
                        if bill.location_id.zip:
                            location += bill.location_id.zip + ','
                    memo = 'Interpreters :- (' + interpret + '), ' + 'Event :- ' + bill.origin + ', ' + 'Language :- ' + bill.language_id.name + ', '
                    memo += 'Base :- ' + str(base) + ', ' + 'Mileage :- ' + str(mileage) + ', ' + 'Travel :- ' + str(
                        travel) + ', ' + 'Date Of Service :- ' + service_date + ', '
                    memo += 'Service :- ' + service + ', ' + 'Location :- ' + location
                    vals = {
                        "VendorRef": {
                            "value": bill.partner_id.quick_id,
                        },
                        "TxnDate": bill.date_invoice,
                        "DocNumber": bill.number or '',
                        "DueDate": bill.date_due,
                        "PrivateNote": memo,
                        "TotalAmt": bill.amount_total,
                        "Line": lines,
                    }
                    if bill.in_qb:
                        exist_quick_id = bill.quick_id
                        logger.warning('quick id in ERP------ %s ---- ', exist_quick_id)
                        exist_post_url = post_url_cust + company.quick_id + "/bill/" + exist_quick_id + "?minorversion=45"
                        read_invoice = requests.get(exist_post_url, headers=headers)
                        response_data = json.dumps(xmltodict.parse(read_invoice.text))
                        # logger.warning('response_data------ %s ---- ',response_data)
                        key_vals = json.loads(response_data)
                        # logger.warning('key_vals---- %s ---- ',key_vals)
                        update_synctoken = key_vals['IntuitResponse']['Bill']['SyncToken']
                        logger.warning('update_synctoken---- %s ---- ', update_synctoken)
                        vals.update({"Id": bill.quick_id, "SyncToken": update_synctoken})
                    logger.warning('BIll vals----------------- With ID---- %s ---- ', vals)
                    data = json.dumps(vals)
                    export_bill = requests.post(post_url, data=data, headers=headers)
                    response_data = json.dumps(xmltodict.parse(export_bill.text))
                    key_vals = json.loads(response_data)
                    qb_id = key_vals['IntuitResponse']['Bill']['Id']
                    bill.sudo().write({'in_qb': True, 'quick_id': qb_id})
                    self._cr.commit()
                    logger.warning('Exported Bill With ID---- %s ---- ', bill.id)
            except Exception as e:
                logger.error('I am in update export_bills_qb() and Error is---- %s ---- ', e)
                logger.error(
                    'I am in update export_bills_qb() and Error in Response is---- %s ---- and Partner Quick-Id is ----%s-----',
                    export_bill.text, bill.partner_id.quick_id)


    @api.multi
    def update_export_bills(self):
        logger.warning("------------------------I am in update export_bills()------------------------")
        configs = self.sudo().search([], limit=1)
        if configs:
            companies = self.env['res.company'].sudo().search([])
            for company in companies:
                try:
                    if company.in_qb:
                        access_token = self.refresh_api_token(company)
                        export = self.update_export_bills_qb(company, access_token)
                except Exception as e:
                    logger.error('I am in update  export_bills() and Error is---- %s ---- ', e)
        else:
            logger.error("No Credentials found for QuickBook")

    @api.multi
    def get_products(self):
        logger.warning("------------------------I am in get_products()------------------------")
        configs = self.sudo().search([], limit=1)
        if configs:
            companies = self.env['res.company'].sudo().search([])
            for company in companies:
                try:
                    if company.in_qb:
                        client = self.get_client(company)
                        current_day = datetime.today()
                        tz = pytz.timezone("America/Toronto")
                        aware_dt = tz.localize(current_day)
                        query_date = aware_dt.isoformat()
                        query = "SELECT * FROM item WHERE MetaData.CreateTime <='" + query_date + "' ""STARTPOSITION 1 MAXRESULTS 1000"
                        products = Item.query(query, qb=client)
                        for item in products:
                            product = self.env['product.product'].sudo().search([('name','=',item.Name)])
                            if product:
                                product.sudo().write({'in_qb':True,
                                               'quick_id':item.Id})
                                self._cr.commit()
                except Exception as e:
                    logger.error('I am in get_products() and Error is---- %s ---- ', e)
        else:
            logger.error("No Credentials found for QuickBook")

    @api.multi
    def read_qb_data(self,data,company,temp):
        logger.warning("------------------------I am in read_qb_data()------------------------")
        client = self.get_client(company)
        customers = []
        vendors = []
        invoices = []
        bills = []
        payments = []
        for records in data:
            date = records['lastUpdated']
            logger.warning("------------------------I have got client and the date is %s------------------------",date)
            if temp =='customers':
                c_query = "SELECT * FROM customer WHERE MetaData.LastUpdatedTime='" + date + "' ""STARTPOSITION 1 MAXRESULTS 1000"
                customer = Customer.query(c_query, qb=client)
                if customer:
                    customers.append(customer[0])
            if temp =='vendors':
                v_query = "SELECT * FROM vendor WHERE MetaData.LastUpdatedTime='" + date + "' ""STARTPOSITION 1 MAXRESULTS 1000"
                vendor = Vendor.query(v_query, qb=client)
                if vendor:
                    vendors.append(vendor[0])
            if temp =='invoices':
                i_query = "SELECT * FROM invoice WHERE MetaData.LastUpdatedTime='" + date + "' ""STARTPOSITION 1 MAXRESULTS 1000"
                invoice = Invoice.query(i_query, qb=client)
                if invoice:
                    invoices.append(invoice[0])
            if temp =='bills':
                i_query = "SELECT * FROM bill WHERE MetaData.LastUpdatedTime='" + date + "' ""STARTPOSITION 1 MAXRESULTS 1000"
                bill = Bill.query(i_query, qb=client)
                if bill:
                    bills.append(bill[0])
            if temp == 'payments':
                p_query = "SELECT * FROM billpayment WHERE MetaData.LastUpdatedTime<='" + date + "' ""STARTPOSITION 1 MAXRESULTS 1000"
                billpayments = BillPayment.query(p_query, qb=client)
                if billpayments:
                    payments.append(billpayments[0])
        #if customers:
         #   self.create_partners(company,customers,True)
        #if vendors:
         #   self.create_partners(company,vendors,False)
        if invoices:
            self.create_invoices(company,invoices)
        if bills:
            self.create_bills(company,bills)
        if payments:
            self.set_check_no(company, payments)

    @api.multi
    def set_check_no(self, company, billpayments):
        for billpays in billpayments:
            try:
                check = billpays.DocNumber
                if billpays.Line:
                    for line in billpays.Line:
                        txnline = line.LinkedTxn[0]
                        logger.error("----------------------txnline-- %s------------------------", txnline)
                        vendor_invoice = self.env['account.invoice'].sudo().search([('quick_id', '=', txnline)])
                        logger.error("----------------------Vendor invoice is %s------------------------", vendor_invoice)
                        vendor_invoice.sudo().write({'check_no': check,
                                                     'qb_check_id': billpays.Id})
                        self._cr.commit()
            except Exception as e:
                logger.error("------------------------Error got in set_check_no() is %s------------------------", e)

    @api.multi
    def delete_invoice(self):
        company=self.env['res.company'].search([('id','=',4)])
        access_token = self.refresh_api_token(company)
        post_url = "https://quickbooks.api.intuit.com/v3/company/" + company.quick_id + "/invoice?operation=delete&minorversion=45"
        auth_header = 'Bearer {0}'.format(access_token)
        headers = {'Authorization': auth_header, 'content-type': 'application/json'}
        invoice=self.env['account.invoice'].search([('in_qb','=',True),('type','=','out_invoice'),('company_id','=',4),('date_invoice','<','2020-01-01')])
        for i in invoice:
             logger.warning("------------------------I am in dleet invoice------------------------%s",i)
             vals={'SyncToken':3,'Id':i.quick_id}
             data = json.dumps(vals)
             export_invoice = requests.post(post_url, data=data, headers=headers)
        #companies = self.env['res.company'].search([])
        #for company in companies:
         #   if company.in_qb:
          #      access_token = self.refresh_api_token(company)
           #     cust_url = "https://quickbooks.api.intuit.com/v3/company/" + company.quick_id + "/customer?operation=delete&minorversion=45"
                # vend_url = "https://quickbooks.api.intuit.com/v3/company/" + company.quick_id + "/vendor?operation=delete&minorversion=45"
            #    auth_header = 'Bearer {0}'.format(access_token)
             #   headers = {'Authorization': auth_header, 'content-type': 'application/json'}
                # partners = self.env['res.partner'].search([('in_qb', '=', True),('cust_type','=','interpreter'),('is_interpretation_active','=',False),('company_id', '=',company.id)])
                # partners = self.env['res.partner'].search([('in_qb', '=', True),('cust_type','=','translator'),('is_translation_active','=',False),('company_id', '=',company.id)])
                # partners = self.env['res.partner'].search([('in_qb', '=', True),('cust_type','=','interp_and_transl'),('is_translation_active','=',False),('is_interpretation_active','=',False),('company_id', '=',company.id)])
              #  partners = self.env['res.partner'].search([('in_qb', '=', True),('cust_type','=','contact'),('company_id', '=',company.id)])
               # logger.warning("------------------------The Total count to delete id ======%s=====------------------------", len(partners))
                #for i in partners:
                 #   try:
                  #      vals = {'SyncToken': 3, 'Id': i.quick_id}
                   #     data = json.dumps(vals)
                    #    export_invoice = requests.post(cust_url, data=data, headers=headers)
                     #   logger.warning("------------------------Deleted Partner from QB------------------------%s", i.quick_id)
                     #   i.sudo().write({'in_qb':False,'quick_id':False})
                     #   self._cr.commit()
           #         except Exception as e:
            #            logger.warning("------------------------Issue Got is ------------------------%s",e)

    @api.multi
    def import_accounts(self):
        logger.warning("------------------------I am in map_accounts()------------------------")
        configs = self.sudo().search([], limit=1)
        if configs:
            companies = self.env['res.company'].sudo().search([])
            for company in companies:
                try:
                    if company.in_qb:
                        client = self.get_client(company)
                        current_day = datetime.now()
                        # current_day = (datetime.now() - timedelta(minutes=65))
                        tz = pytz.timezone("America/Toronto")
                        aware_dt = tz.localize(current_day)
                        query_date = aware_dt.isoformat()
                        query = "SELECT * FROM account WHERE MetaData.CreateTime <='" + query_date + "' ""STARTPOSITION 1 MAXRESULTS 1000"
                        accounts = Account.query(query, qb=client)
                        print "accounts",accounts
                        if accounts:
                            account_list = []
                            for account in accounts:
                                try:
                                    acc_exist = self.env['account.account'].sudo().search(
                                        [('name', '=', account.Name), ('company_id', '=', company.id)])
                                    if acc_exist.exists():
                                        acc_exist.sudo().write({'in_qb': True, 'quick_id': account.Id})
                                        # self._cr.commit()
                                        logger.warning(
                                            "-------------------Updated Account %s with QB-Id === %s  ------------------",
                                            acc_exist.id, account.Id)
                                    else:
                                        account_type = False
                                        reconcile = False
                                        if account.AccountType == 'Accounts Receivable':
                                            account_type = 'Receivable'
                                            reconcile = True
                                        if account.AccountType == 'Accounts Payable':
                                            account_type = 'Payable'
                                            reconcile = True
                                        if account.AccountType == 'Bank':
                                            account_type = 'Bank and Cash'
                                        if account.AccountType == 'Credit Card':
                                            account_type = 'Credit Card'
                                        if account.AccountType == 'Other Current Asset':
                                            account_type = 'Current Assets'
                                            reconcile = True
                                        if account.AccountType == 'Other Current Asset':
                                            account_type = 'Non-current Assets'
                                        if account.AccountType == '':
                                            account_type = 'Prepayments'
                                        if account.AccountType == 'Fixed Asset':
                                            account_type = 'Fixed Assets'
                                        if account.AccountType == 'Other Current Liability':
                                            account_type = 'Current Liabilities'
                                            reconcile = True
                                        if account.AccountType == 'Long Term Liability':
                                            account_type = 'Non-current Liabilities'
                                        if account.AccountType == 'Equity':
                                            account_type = 'Equity'
                                        if account.AccountType == 'Income':
                                            account_type = 'Current Year Earnings'
                                        if account.AccountType == 'Other Income':
                                            account_type = 'Other Income'
                                        if account.AccountType == 'Income':
                                            account_type = 'Income'
                                        if account.AccountType == 'Expense':
                                            account_type = 'Depreciation'
                                        if account.AccountType == 'Other Expense':
                                            account_type = 'Expenses'
                                        if account.AccountType == 'Cost of Goods Sold':
                                            account_type = 'Cost of Revenue'

                                        user_type = self.env['account.account.type'].search([("name", "=", account_type)], limit=1)
                                        if user_type.exists() and account.AcctNum:
                                            account_dictionary = {
                                                "name": account.Name,
                                                "user_type_id": user_type.id,
                                                "code": account.AcctNum,
                                                "company_id": company.id,
                                                "reconcile": reconcile,
                                                'in_qb': True,
                                                'quick_id': account.Id
                                            }
                                            account_list.append(account_dictionary)

                                            # self.env['account.account'].sudo().create(account_dictionary)
                                            # self._cr.commit()
                                except Exception as e:
                                    logger.error("-----------------In mapping Accoounts ::: %s --------------------", e)
                            print "account_list", account_list
                            for account_dictionary in account_list:
                                logger.error('account_dictionary is---- %s ---- ', account_dictionary)
                                current_record = self.env['account.account'].sudo().create(account_dictionary)
                                logger.error('current_record is---- %s ---- \n\n', current_record)
                            logger.error('Chart of Account is successfully  created')
                except Exception as e:
                    logger.error('Error is---- %s ---- ', e)
        else:
            logger.error("No Credentials found for QuickBook")

    @api.multi
    def update_partners(self, company, partners, temp):
        logger.warning("------------------------I am in update_partners()------------------------")
        logger.warning("----company,  temp-------parteners-------------Inputs-------%s-----%s- %s " % (str(company), str(temp), str(len(partners))))
        sync_customers_list = []

        missed_qb_customer_list = []
        for record in partners:
            try:
                mobile = country = state = city = line1 = line2 = zip = email = phone = False
                # customer_exist = self.env['res.partner'].sudo().search(
                #     [('quick_id', '=', record.Id), ('company_id', '=', company.id)])
                search_domain = [('company_id', '=', company.id)]
                if temp:
                    search_domain.append(('cust_type', '=', "customer"))
                    search_domain.append(('name', '=ilike', str(record.DisplayName)))
                    name = record.DisplayName
                else:
                    search_domain.append(('cust_type', '=', "interpreter"))
                    search_domain.append(('name', '=ilike', str(record.GivenName)))
                    search_domain.append(('last_name', '=ilike', str(record.FamilyName)))
                    name = record.GivenName + " " + record.FamilyName
                # logger.warning("------------------------search_domain------------------------ %s " % str(search_domain))

                partner_exist = self.env['res.partner'].sudo().search(search_domain)
                # logger.warning("------------------------partner_exist------------------------ %s " % str(partner_exist))
                vals = {
                        'in_qb': True,
                        'quick_id': record.Id,
                        }

                if partner_exist:
                    partner_exist.sudo().write(vals)
                    sync_customers_list.append((partner_exist.id, record.Id, name))
                    self._cr.commit()
                    # logger.warning('Updated partner %s --- With QB-Id %s ', partner_exist.id, record.Id)
                else:
                    missed_qb_customer_list.append((record.Id, name))
            except Exception as e:
                logger.error('I am in update_partners() and Error is -- %s --', e)
        if temp:
            logger.info("\n\n @@@@@@@@@@@@@@@@@@@@@@@@@ Customers @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            logger.info("Total QB Customers Count is %s" % str(len(partners)))
            logger.info("Sync Customer are %s" % str(sync_customers_list))
            logger.info("Sync Customers Count is %s" % str(len(sync_customers_list)))
            logger.info("Missed QB Customer are %s" % str(missed_qb_customer_list))
            logger.info("Missed QB Customer count is %s" % str(len(missed_qb_customer_list)))
            logger.info("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n\n")
        else:
            logger.info("\n\n @@@@@@@@@@@@@@@@@@@@@@@@@ Interpreters @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            logger.info("Total QB Interpreters Count is %s" % str(len(partners)))
            logger.info("Sync Interpreters are %s" % str(sync_customers_list))
            logger.info("Sync Interpreters Count is %s" % str(len(sync_customers_list)))
            logger.info("Missed QB Interpreters are %s" % str(missed_qb_customer_list))
            logger.info("Missed QB Interpreters count is %s" % str(len(missed_qb_customer_list)))
            logger.info("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n\n")


    @api.multi
    def update_customers_vendors(self):
        logger.warning("------------------------I am in update_customers_vendors()------------------------")
        configs = self.sudo().search([], limit=1)
        if configs:
            companies = self.env['res.company'].sudo().search([])
            for company in companies:
                try:
                    if company.in_qb:
                        client = self.get_client(company)
                        current_day = datetime.today() - timedelta(days=1)
                        logger.info("\n\n current_day: %s" % str(current_day))
                        # current_day = (datetime.now() - timedelta(minutes=65))
                        tz = pytz.timezone("America/Toronto")
                        aware_dt = tz.localize(current_day)
                        query_date = aware_dt.isoformat()
                        c_query = "SELECT * FROM customer WHERE MetaData.CreateTime <='" + query_date + "' ""STARTPOSITION 1 MAXRESULTS 1000"
                        customers = Customer.query(c_query, qb=client)
                        # logger.info("customers: %s" % str(customers))
                        if customers:
                            customer = self.update_partners(company, customers, True)
                        v_query = "SELECT * FROM vendor WHERE MetaData.CreateTime <='" + query_date + "' ""STARTPOSITION 1 MAXRESULTS 1000"
                        vendors = Vendor.query(v_query, qb=client)
                        logger.info("vendors: %s" % str(vendors))
                        if vendors:
                            vendor = self.update_partners(company, vendors, False)
                except Exception as e:
                    logger.error('I am in update_customers_vendors() and Error is---- %s ---- ', e)
        else:
            logger.error("No Credentials found for QuickBook")

    @api.multi
    def test_anything(self):
        company = self.env['res.company'].browse(3)
        client = self.get_client(company)
        date = '2019-11-21T02:05:54-08:00'
        query = "SELECT * FROM customer WHERE MetaData.LastUpdatedTime='" + date + "' ""STARTPOSITION 1 MAXRESULTS 1000"
        invoices = Customer.query(query, qb=client)
        content = invoices[0]
        access_token = self.refresh_api_token(company)
        auth_header = 'Bearer {0}'.format(access_token)
        headers = {'Authorization': auth_header, 'content-type': 'application/json'}
        url = "https://sandbox-quickbooks.api.intuit.com/v3/company/"+company.quick_id+"/customer/83?minorversion=41"
        try:
            response = requests.get(url, headers=headers)
            a=1
        except Exception as e:
            pass






  
