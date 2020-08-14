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
#    You should have received a copy ofPlease enter valid 10 digits Phone No the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time
import datetime
import re

from odoo import SUPERUSER_ID
from odoo import tools
from odoo import models, fields,api
from odoo.tools.translate import _
from odoo.tools import flatten
from odoo.addons.base.res.res_partner import FormatAddress as format_address
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from bss_phonumbers_fields import bss_phonenumbers_converter as phonumbers_converter
import phonenumbers
from pygeocoder import Geocoder
import pytz
from odoo.exceptions import UserError, RedirectWarning, ValidationError

ADDRESS_FIELDS = ('street', 'street2', 'zip', 'city', 'state_id', 'country_id')
POSTAL_ADDRESS_FIELDS = ADDRESS_FIELDS # deprecated, to remove after 7.0

def geo_find(addr , api_key=False):
    '''Function to Geo Localise Patient location '''
    #link = 'https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key=API_KEY'
#    url = 'https://maps.googleapis.com/maps/api/geocode/json?sensor=false&address='
#    url += urllib.quote(addr.encode('utf8'))
#    if api_key:
#        url += '&key='
#        url += urllib.quote(api_key.encode('utf8'))
    res = []
    api_key = 'AIzaSyDAPZqsalpxu0T5SPRBXSG8K2ZVnngmmUo'
    try:
        gcoder = Geocoder(api_key)
        results = gcoder.geocode(addr)
        print results[0].latitude
        print results[0].longitude
        res.append(results[0].latitude)
        res.append(results[0].longitude)
    except Exception, e:
        print "Exception.....",e.args
        pass
    try:
        if res:
            return res
    except (KeyError, ValueError):
        return None

def geo_query_address(street=None, zip=None, city=None, state=None, country=None):
    if country and ',' in country and (country.endswith(' of') or country.endswith(' of the')):
        # put country qualifier in front, otherwise GMap gives wrong results,
        # e.g. 'Congo, Democratic Republic of the' => 'Democratic Republic of the Congo'
        country = '{1} {0}'.format(*country.split(',',1))
    return tools.ustr(', '.join(filter(None, [street,
                                              ("%s %s" % (zip or '', city or '')).strip(),
                                              state,
                                              country])))
# fields copy if 'use_parent_address' is checked
ADDRESS_FIELDS = ('street', 'street2', 'zip', 'city', 'state_id', 'country_id')
POSTAL_ADDRESS_FIELDS = ADDRESS_FIELDS # deprecated, to remove after 7.0

class patient_history(models.Model):
    '''Patient  History , keeps record of Patient injury History'''
    _name = "patient.history"

    name=fields.Many2one('patient',"Patient", required=True)
    event_id=fields.Many2one('event','Event', required=True)
    event_date=fields.Date("Event Date")
    injury_date=fields.Date('Injury Date',)
    claim_no=fields.Char("Claim No", size=64)
    company_id=fields.Many2one(related='name.company_id', string='Related Company',store=True)


class patient_auth_history(models.Model):
    '''Patient  History , keeps record of Patient injury History'''
    _name = "patient.auth.history"

    name=fields.Many2one('patient',"Patient", required=True)
    event_id=fields.Many2one('event','Event', required=True)
    partner_id=fields.Many2one('res.partner','Customer')
    auth_for=fields.Selection([('language','language'),('transport','Transport')],'Auth For')
    date_from=fields.Date('Date From')
    date_to=fields.Date('Date To')
    company_id=fields.Many2one(related='name.company_id', string='Related Company',store=True)


class patient(models.Model, format_address):
    _description = 'Patient'
    _name = "patient"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = "name"

    @api.multi
    def create_event(self):
        obj=self
        event_obj=self.env['event']
        print"obj",obj

        event_data = {
                'partner_id': self.ids[0] ,
                'ordering_partner_id':self.ids[0],
                'event_type':'language',
               }
        evt_id = event_obj.create(event_data).id
        mod_obj = self.env['ir.model.data']
        res = mod_obj.get_object_reference('bista_iugroup', 'view_event_form')
        res_id = res and res[1] or False,
        return {
            'name': _('Event'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res_id[0]],
            'res_model': 'event',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': evt_id or False,
            'context':{"search_default_event_type":'language',"search_event_type":'language',
            "default_event_type":'language'}
        }

    @api.model
    def default_get(self, fields):
        ''' This function auto fill ordering_partner_id related to Patient'''
        res = super(patient, self).default_get(fields)
        if self._context.get('company_id',False):
            if 'company_id' in fields:
                res.update({'company_id': self._context.get('company_id',False)})
        if self._context.get('ordering_partner_id',False):
            if 'ordering_partner_id' in fields:
                res.update({'ordering_partner_id': self._context.get('ordering_partner_id',False)})
        return res

    @api.depends('last_name', 'name')
    def _name_get_fnc(self):
        for line in self:
            complete_name = ""
            if line.last_name and line.name:
                complete_name = line.name.encode('utf-8', 'ignore').strip() + " " + line.last_name.encode('utf-8', 'ignore').strip()
            else:
                if line.name:
                    complete_name = line.name.encode('utf-8', 'ignore').strip()
            line.complete_name = complete_name.replace('  ',' ')

    

    name=fields.Char('Name', size=128, required=True, index=True ,track_visibility='onchange')
    last_name=fields.Char('Last Name', size=128, index=True ,track_visibility='onchange')
    complete_name=fields.Char(compute=_name_get_fnc, string='Complete Name',store=True)
    ref=fields.Char('Reference', size=64, index=1)
    user_id=fields.Many2one('res.users', 'Salesperson', help='The internal user that is in charge of communicating with this contact if any.',default=lambda self: self.env.user.id)
    comment=fields.Text('Notes' ,track_visibility='onchange')
    active=fields.Boolean('Active' ,track_visibility='onchange',default=True)
    street=fields.Char('Street', size=128)
    street2=fields.Char('Street2', size=128)
    zip=fields.Char('Zip', change_default=True, size=24)
    city=fields.Char('City', size=128)
    state_id=fields.Many2one("res.country.state", 'State',)
    country_id=fields.Many2one('res.country', 'Country',)
    email=fields.Char('Email', size=240)
    email2=fields.Char('Email 2', size=240)
    phone=fields.Char('Phone', size=64)
    phone2=fields.Char('Phone 2', size=64)
    phone3=fields.Char('Phone 3', size=64)
    phone4=fields.Char('Phone 4', size=64)
    fax=fields.Char('Fax', size=64)
    mobile=fields.Char('Mobile', size=64)
    company_id=fields.Many2one('res.company', 'Company', index=1,default=lambda self: self.env['res.company']._company_default_get('patient'))
    is_alert=fields.Boolean('Alert', help="Select if on alert")
    ssnid=fields.Char('SSN/MRN', size=34, help='Social Security Number' ,track_visibility='onchange')
    sinid=fields.Char('Social Insurance Number', size=34, help="Social Insurance Number" ,track_visibility='onchange')
    latitude=fields.Float('Geo Latitude' , digits = (16,6))
    longitude=fields.Float('Geo Longitude' , digits = (16,6))
    gender=fields.Selection([('male','Male'),('female','Female')],"Gender")
    company_name=fields.Char('Company Name', size=70)
    function=fields.Char('Job Position', size=64)
    birthdate=fields.Date('Birthdate',)
    injury_date=fields.Date('Injury Date',)
    patient_id=fields.Integer("IU Patient Id")
#        'location_ids': fields.many2many('location','patient_location_rel','patient_id','location_id','Locations'),
    location_ids=fields.One2many('location','patient_id','Locations')
    # ssn_mrn_birth=fields.Date("SSN/MRN/Birthdate")

#-------------------Claimant-----------------------------
    website=fields.Char('Website', size=64, help="Website of Partner or Company")
    date=fields.Date('Date',)
    last_update_date=fields.Date("Last Update Date")
    employer=fields.Char('Employer',size=256)
    employer_contact=fields.Char('Employer Contact',size=128)
    case_manager_id=fields.Many2one('hr.employee','Case Manager')
    claim_number=fields.Char('Claim No3',size=128)
    claim_no=fields.Char("Claim No", size=64)
    claim_no2=fields.Char("Claim No2", size=64)
    field_case_mgr_id=fields.Many2one('hr.employee','Field Case Manager',size=128)
    referrer=fields.Char('Referrer',size=64)
    billing_partner_id=fields.Many2one('res.partner',"Billing Customer" , domain="[('cust_type','=','customer')]")
    billing_contact_id=fields.Many2one('res.partner',"Billing Contact" , domain="[('cust_type','=','contact')]")
    patient_history=fields.One2many('patient.history', 'name','Patient History')
    patient_auth_history=fields.One2many('patient.auth.history', 'name','Patient Auth History')
    interpreter_id=fields.Many2one('res.partner',"Preferred Interpreter")
    interpreter_history=fields.One2many('interpreter.alloc.history', 'patient_id', 'Interpreter History',readonly=True , )
    ordering_partner_id=fields.Many2one('res.partner',"Related Customer", domain="[('cust_type','=','customer')]")
    p_block_inter_ids = fields.Many2many('res.partner', 'patient_part_cust_rel', 'part_id', 'patient_id', 'Does Not Vist')
# ------------------EDI------------------------------------------------------------
#        'add_change_flag':fields.boolean('Add/Change flag'),
#        'claimant_id':fields.char('Claimant Id',size=8),
#        'create_date':fields.date('Claimant Entry date'),
#        'write_date':fields.date('Claimant Update date'),
#        'claim_id':fields.integer('Claim Id'),
#        'claim_date':fields.date('Claim Date',help="Claim Date of accident"),
#        'claim_number':fields.char('Claim Number',size=64),
#        'claim_diagcode1':fields.char('Claim Diagcode1',size=8),
#        'claim_diagcode2':fields.char('Claim Diagcode2',size=8),
#        'claim_diagcode3':fields.char('Claim Diagcode3',size=8),
#        'claim_status':fields.selection([('open','Open'),('closed','Closed'),('reopen','Re-Opened'),('pending','Pending'),('denied','Denied'),('uninsured','Uninsured')],'Claim Status'),
#        'employer_country':fields.char('Employer Country',size=64),
#        'adjuster_last_name':fields.char('Adjuster Last Name',size=64),
#        'adjuster_first_name':fields.char('Adjuster First Name',size=64),
#        'consult_last_name':fields.char('Consult Last Name',size=64),
#        'consult_first_name':fields.char('Consult First Name',size=64),
#        'amerisys_payer_indicator':fields.char('Amerisys Payer Indicator',size=4),
#        'controverted':fields.char('Controverted',size=1,help="Y/N flag to identify if the claim has been controverted and would not be eligible for payment"),
#        'mmi_date':fields.date('MMI date'),
#        'db_id':fields.char('DB ID',size=1,help="Amerisys Database ID"),

    @api.model
    def _generate_order_by(self, order_spec, query):
        '''correctly orders Location field in many2one'''
        order_by = super(patient, self)._generate_order_by(order_spec, query)
        #print "order_by..........",order_by
#        if order_by:
#            order_by = str(order_by) + ' desc'
        if order_by:
            temp = order_by.upper()
            count = temp.count('DESC')
            count2 = temp.count('ASC')
            if count >= 1 or count2 >= 1:
                return order_by
            else:
                order_by = str(order_by) + ' desc'
#            count = 0
#            count = temp.count('ASC')
#            if count >= 1:
#                order_by = order_by.replace("desc", " ", 1)
#            count = 0
#            count = temp.count('DESC')
#            count2 = temp.count('ASC')
#            if count >= 1 and count2 >= 1:
#                order_by = order_by.replace("ASC", " ", 1)
        #order_by = ''' ORDER BY "res_partner"."last_update_date" desc '''
        #print "order_by..........",order_by
        return order_by

    @api.model
    def create(self,vals):
#        Code to have validation on Phone fields
        if vals.get('phone', False):
            final_phone=''
            count=0
            chck_phone=str(vals.get('phone'))
            for each in chck_phone:
                if each.isdigit():
                    count +=1
                    final_phone+=each
#            final_phone=final_phone.lstrip('1')
#            if count != 10 :
 #               raise UserError(_('Please enter valid 10 digits Phone No.'))
            phone2='+1-'+final_phone[-10:-7]+'-'+final_phone[-7:-4]+'-'+final_phone[-4:]
            vals['phone'] = phone2
            print "phone in write 2---------",chck_phone, type(chck_phone), final_phone, type(final_phone), count
        if vals.get('phone2', False):
            final_phone2=''
            count2=0
            chck_phone2=str(vals.get('phone2'))
            for each in chck_phone2:
                if each.isdigit():
                    count2 +=1
                    final_phone2+=each
  #          if count2 != 10 :
   #             raise UserError(_('Please enter valid 10 digits Phone No.'))
            phone2='+1-'+final_phone2[-10:-7]+'-'+final_phone2[-7:-4]+'-'+final_phone2[-4:]
            vals['phone2'] = phone2
        if vals.get('phone3', False):
            print "in 3rd if--------------"
            final_phone3=''
            count3=0
            chck_phone3=str(vals.get('phone3'))
            for each in chck_phone3:
                if each.isdigit():
                    count3 +=1
                    final_phone3+=each
    #        if count3 != 10 :
     #           raise UserError(_('Please enter valid 10 digits Phone No.'))
            phone3='+1-'+final_phone3[-10:-7]+'-'+final_phone3[-7:-4]+'-'+final_phone3[-4:]
            vals['phone3'] = phone3
        if vals.get('phone4', False):
            final_phone4=''
            count4=0
            chck_phone4=str(vals.get('phone4'))
            for each in chck_phone4:
                if each.isdigit():
                    count4 +=1
                    final_phone4+=each
      #      if count4 != 10 :
       #         raise UserError(_('Please enter valid 10 digits Phone No.'))
            phone4='+1-'+final_phone4[-10:-7]+'-'+final_phone4[-7:-4]+'-'+final_phone4[-4:]
            vals['phone4'] = phone4
        return super(patient, self).create(vals)

    @api.multi
    def write(self, vals):
        #        Code to have validation on Phone fields
        if vals.get('phone', False):
            final_phone=''
            count=0
            chck_phone=str(vals.get('phone'))
            for each in chck_phone:
                if each.isdigit():
                    count +=1
                    final_phone+=each
#            final_phone=final_phone.lstrip('1')
            if count != 10 :
                raise UserError(_('Please enter valid 10 digits Phone No.'))
            phone2='+1-'+final_phone[-10:-7]+'-'+final_phone[-7:-4]+'-'+final_phone[-4:]
            vals['phone'] = phone2
            print "phone in write 2---------",chck_phone, type(chck_phone), final_phone, type(final_phone), count
        if vals.get('phone2', False):
            final_phone2=''
            count2=0
            chck_phone2=str(vals.get('phone2'))
            for each in chck_phone2:
                if each.isdigit():
                    count2 +=1
                    final_phone2+=each
        #    if count2 != 10 :
         #       raise UserError(_('Please enter valid 10 digits Phone No.'))
            phone2='+1-'+final_phone2[-10:-7]+'-'+final_phone2[-7:-4]+'-'+final_phone2[-4:]
            vals['phone2'] = phone2
        if vals.get('phone3', False):
            print "in 3rd if--------------"
            final_phone3=''
            count3=0
            chck_phone3=str(vals.get('phone3'))
            for each in chck_phone3:
                if each.isdigit():
                    count3 +=1
                    final_phone3+=each
          #  if count3 != 10 :
           #     raise UserError(_('Please enter valid 10 digits Phone No.'))
            phone3='+1-'+final_phone3[-10:-7]+'-'+final_phone3[-7:-4]+'-'+final_phone3[-4:]
            vals['phone3'] = phone3
        if vals.get('phone4', False):
            final_phone4=''
            count4=0
            chck_phone4=str(vals.get('phone4'))
            for each in chck_phone4:
                if each.isdigit():
                    count4 +=1
                    final_phone4+=each
            #if count4 != 10 :
             #   raise UserError(_('Please enter valid 10 digits Phone No.'))
            phone4='+1-'+final_phone4[-10:-7]+'-'+final_phone4[-7:-4]+'-'+final_phone4[-4:]
            vals['phone4'] = phone4
#           phone in write 2--------- +1234567899 <type 'str'> 1234567899 <type 'str'> 10
        return super(patient, self).write(vals)

    @api.multi
    def view_past_appointments(self):
        ''' This function returns an action that display past Appointments corresponding to the Patient. '''
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']
        result = mod_obj.get_object_reference('bista_iugroup', 'action_event_all_type')#view_order_tree
        id = result and result[1] or False
        result = act_obj.browse(id).read()[0]
        user = self.env.user
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.utc
        local_date = tz.localize(datetime.datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),DATETIME_FORMAT), is_dst=None)
        local_date = datetime.datetime.strptime(local_date.astimezone (tz).strftime(DATETIME_FORMAT), DATETIME_FORMAT).strftime('%Y-%m-%d') 
        
        history_ids = []
        for part in self:
            history_ids = self.env['event'].search([('patient_id','=',part.id),('event_start_date','<',local_date)]).ids
        if not history_ids:
            raise UserError(_('No Past Appointments for this Patient.'))
        result['domain'] = "[('id','in',["+','.join(map(str, history_ids))+"])]"
        return result

    @api.multi
    def view_today_appointments(self):
        ''' This function returns an action that display future Appointments corresponding to the Patient. '''
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']
        result = mod_obj.get_object_reference('bista_iugroup', 'action_event_all_type')#view_quotation_tree,view_order_tree
        id = result and result[1] or False
        result = act_obj.browse(id).read()[0]
        user = self.env.user
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.utc
        local_date = tz.localize(datetime.datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),DATETIME_FORMAT), is_dst=None)
        local_date = datetime.datetime.strptime(local_date.astimezone (tz).strftime(DATETIME_FORMAT), DATETIME_FORMAT).strftime('%Y-%m-%d')
        history_ids = []
        for part in self:
            history_ids = self.env['event'].search([('patient_id','=',part.id),('event_start_date','=',local_date)]).ids
        if not history_ids:
            raise UserError(_('No Future Appointments for this patient.'))
        result['domain'] = "[('id','in',["+','.join(map(str, history_ids))+"])]"
        return result

    @api.multi
    def view_future_appointments(self):
        ''' This function returns an action that display future Appointments corresponding to the Patient. '''
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']
        result = mod_obj.get_object_reference('bista_iugroup', 'action_event_all_type')#view_quotation_tree,view_order_tree
        id = result and result[1] or False
        result = act_obj.browse(id).read()[0]
        user = self.env.user
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.utc
        local_date = tz.localize(datetime.datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),DATETIME_FORMAT), is_dst=None)
        local_date = datetime.datetime.strptime(local_date.astimezone (tz).strftime(DATETIME_FORMAT), DATETIME_FORMAT).strftime('%Y-%m-%d') 
        history_ids = []
        for part in self:
            history_ids = self.env['event'].search([('patient_id','=',part.id),('event_start_date','>',local_date)]).ids
        if not history_ids:
            raise UserError(_('No Future Appointments for this patient.'))
        result['domain'] = "[('id','in',["+','.join(map(str, history_ids))+"])]"
        return result

    @api.multi
    def open_map_new(self):
        ''' Function to Show Claiment on google '''
        partner = self
        url="http://maps.google.com/maps?oi=map&q="
        if partner.street:
            url+=partner.street.replace(' ','+')
        if partner.city:
            url+='+'+partner.city.replace(' ','+')
        if partner.state_id:
            url+='+'+partner.state_id.name.replace(' ','+')
        if partner.country_id:
            url+='+'+partner.country_id.name.replace(' ','+')
        if partner.zip:
            url+='+'+partner.zip.replace(' ','+')
        return {
        'type': 'ir.actions.act_url',
        'url':url,
        'nodestroy': True,
        'target': 'new'
        }

    @api.onchange('zip')
    def onchange_zip(self):
        '''Function to auto Fill Zone '''
        if self.zip:
            zip = self.zip.strip()
            query = "select id from zip_code where zip_code_id = %s and company_id = %s "%( zip,self.company_id.id)
            self._cr.execute(query)
            zip_ids = map(lambda x: x[0], self._cr.fetchall())
            if zip_ids:
                query = "select zone_id from zipcode_to_zone_rel where zip_code_id = %s"%( zip_ids[0])
                self._cr.execute(query)
                zone_ids = map(lambda x: x[0], self._cr.fetchall())
                if zone_ids:
                    return {'value':{'zone_id': zone_ids[0] or False}}
        return {'value':{'zone_id': False}}

    @api.model
    def get_default_country(self):
        """Return the Default Country """
        proxy = self.env['ir.config_parameter']
        default_country = proxy.sudo().get_param('default_country')
        if not default_country:
            raise UserError(_('Please Default Country as US in config parameters.'))
        return default_country.strip()

    @api.onchange('phone','phone2','phone3','phone4')
    def onchange_phone(self):
        ''' function to change in the format of selected default country '''
        result = {}
        result['value'] = {}
        def_country = self.get_default_country()
        new_phone = ''
        if self.phone:
            try:
                pn = phonumbers_converter._parse(self.phone, def_country)
                if pn:
                    new_phone = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.E164)
                else:
                    new_phone = None
            except phonenumbers.NumberParseException:
                phone = None
                pass
            result['value']['phone'] = new_phone
        new_phone = ''
        if self.phone2:
            try:
                pn = phonumbers_converter._parse(self.phone2, def_country)
                if pn:
                    new_phone = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.E164)
                else:
                    new_phone = None
            except phonenumbers.NumberParseException:
                phone2 = None
                pass
            result['value']['phone2'] = new_phone
        return result

################### Default Functions copied from res.partner ####################
    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        name = self.read(['name'])[0]['name']
        default.update({'name': _('%s (copy)') % name})
        return super(patient, self).copy(default)

    @api.onchange('state_id')
    def onchange_state(self):
        if self.state_id:
            country_id = self.state_id.country_id.id
            return {'value':{'country_id':country_id}}
        return {}

    @api.model
    def _display_address(self, address, without_company=False):
        ''' The purpose of this function is to build and return an address formatted accordingly to the
        standards of the country where it belongs.
        :param address: browse record of the res.partner to format
        :returns: the address formatted in a display that fit its country habits (or the default ones
            if not country is specified)
        :rtype: string
        '''
        # get the information that will be injected into the display format
        # get the address format
        address_format = address.country_id and address.country_id.address_format or \
                         "%(street)s\n%(street2)s\n%(city)s %(state_code)s %(zip)s\n%(country_name)s"
        args = {
            'state_code': address.state_id and address.state_id.code or '',
            'state_name': address.state_id and address.state_id.name or '',
            'country_code': address.country_id and address.country_id.code or '',
            'country_name': address.country_id and address.country_id.name or '',
            'company_name': address.parent_id and address.parent_id.name or '',
        }
        for field in self._address_fields():
            args[field] = getattr(address, field) or ''
        if without_company:
            args['company_name'] = ''
        elif address.parent_id:
            address_format = '%(company_name)s\n' + address_format
        return address_format % args

    @api.multi
    @api.depends('name', 'last_name')
    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.last_name:
                name = name + ' ' + (record.last_name or '')
#            if record.claim_no:
#                name =  "[%s] %s " % (record.claim_no ,name )
#            if record.billing_partner_id:
#                name =  "%s [%s] " % (name , record.billing_partner_id.name)
            res.append((record.id, name))
        return res

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        #print " patient name_search..name...",name,args,operator
        if not args: args = []
        ids = []
        if name:
            ids = self.search([('complete_name',operator,name)]+ args, limit=limit)
            if not ids:
                ids = self.search([('name',operator,name)]+ args, limit=limit)
            if not ids:
                ids = self.search( args + [('last_name',operator,name)], limit=limit)
            if not ids:
                ids = self.search([('billing_partner_id.name',operator,name)]+ args, limit=limit)
            if not ids:
                ids = self.search([('claim_no',operator,name)]+ args, limit=limit)
            if not ids:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    ids = self.search([('name','=', res.group(2))] + args, limit=limit)
        else:
            ids = self.search([] + args, limit=limit)
        result = ids.name_get()
        return result

class patient_location_rel(models.Model):
    _description = 'Many2many Relation , Added company_id field'
    _name = "patient.location.rel"

    patient_id=fields.Many2one('patient', 'Patient')
    location_id= fields.Many2one('location', 'Location')
    company_id=fields.Many2one(related='patient_id.company_id', store=True, string="Company",readonly=True,)

    _sql_constraints = [
        ('patient_id_location_id_company_id_uniq', 'unique (patient_id,location_id,company_id)', 'The Patient and Location must be unique per company !')
    ]


