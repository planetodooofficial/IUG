#  -*- coding: utf-8 -*-
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

import time
import odoo
from odoo import fields,models,api,_
from odoo import SUPERUSER_ID, tools
from bss_phonumbers_fields import bss_phonenumbers_converter as phonumbers_converter
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta
from dateutil import parser
from odoo.tools import flatten
import phonenumbers
import re
import pytz
import urllib
import random
import math
import logging
logger = logging.getLogger('IUG')
_logger = logging.getLogger(__name__)
#try:
#    import simplejson as json
#except ImportError:
#    import json     # noqa
from pygeocoder import Geocoder
import xmlrpclib
from odoo.exceptions import UserError, RedirectWarning, ValidationError
_timezone_event = {-11: 'US/Samoa', -10: 'US/Hawaii',
                        -9: 'US/Alaska', -8: 'US/Pacific',
                        -7: 'US/Mountain', -6: 'US/Central',
                        -5: 'US/Eastern'}

def geo_find(addr , api_key=False):
    #link = 'https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key=API_KEY'
#    url = 'https://maps.googleapis.com/maps/api/geocode/json?sensor=false&address='
#    url += urllib.quote(addr.encode('utf8'))
#    print "api_key.........",api_key,type(api_key)
    res = []
#    if api_key:
#        url += '&key='
#        url += urllib.quote(api_key.encode('utf8'))
#    print "url........",url
#    u = urllib.urlopen(url)
#    print "u.......", u
#    result = json.load(u)
#    print "result......",result
    api_key='AIzaSyDAPZqsalpxu0T5SPRBXSG8K2ZVnngmmUo'
    try:
        gcoder = Geocoder(api_key)
        results = gcoder.geocode(addr)
        res.append(results[0].latitude)
        res.append(results[0].longitude)
    except Exception, e:
        logger.info(' Error : %s',e.args)
        pass
#        raise osv.except_osv(_('Network error'),
#                             _('Cannot contact geolocation servers. Please make sure that your internet connection is up and running (%s).') % (e.args))
    
#    try:
#        u = urllib.urlopen(url)
#        print "u.......", u
#        result = json.load(u)
#        print "result......",result
#    except Exception, e:
#        raise osv.except_osv(_('Network error'),
#                             _('Cannot contact geolocation servers. Please make sure that your internet connection is up and running (%s).') % (e.args))
#
#    #print "result.......",result
#    if result['status'] != 'OK':
#        return None

#    try:
#        geo = result['results'][0]['geometry']['location']
#        return float(geo['lat']), float(geo['lng'])
#    except (KeyError, ValueError):
#        return None
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
    try:
        if street:
            street = street.encode('utf-8', 'ignore')
            try:
                street = unicode(street, "ascii",'ignore')
            except UnicodeError:
                street = unicode(street, "utf-8", 'ignore').decode('ascii')
        if zip:
            zip = zip.encode('utf-8', 'ignore')
            try:
                zip = unicode(zip, "ascii",'ignore')
            except UnicodeError:
                zip = unicode(zip, "utf-8", 'ignore').decode('ascii')
        if city:
            city = city.encode('utf-8', 'ignore')
            try:
                city = unicode(city, "ascii",'ignore')
            except UnicodeError:
                city = unicode(city, "utf-8", 'ignore').decode('ascii')
        if state:
            state = state.encode('utf-8', 'ignore')
        if country:
            country = country.encode('utf-8', 'ignore')
    except Exception:
        pass
    return tools.ustr(', '.join(filter(None, [street, ("%s %s" % (zip or '', city or '')).strip(),
                                              state, country])))

# fields copy if 'use_parent_address' is checked
ADDRESS_FIELDS = ('street', 'street2', 'zip', 'city', 'state_id', 'country_id')
POSTAL_ADDRESS_FIELDS = ADDRESS_FIELDS # deprecated, to remove after 7.0


class res_partner(models.Model):
    ''' Add fields to existing partner class for IU System '''
    _inherit = "res.partner"
    #    _order = "last_update_date desc"
    _order = "name asc"

    @api.multi
    def get_direction(self):
        ''' Function used to get direction from assigned interpreter many2many to the location of the event '''
        event_id = self._context.get('event_id', False)
        if not event_id:
            return True
        event = self.env['event'].browse(event_id)
        location = event.location_id
        interpreter = self
        if not location:
            raise UserError(_('You must enter location first.'))

        url = "http://maps.google.com/maps?mode=driving&saddr="
        location_address = ''
        location_address = geo_query_address(location.street or False, location.zip or False, location.city or False, \
                                             location.state_id and location.state_id.name or False,
                                             location.country_id and location.country_id.name or False)
        interp_address = ''
        interp_address = geo_query_address(interpreter.street or False, interpreter.zip or False,
                                           interpreter.city or False, \
                                           interpreter.state_id and interpreter.state_id.name or False,
                                           interpreter.country_id and interpreter.country_id.name or False)
        url += interp_address + '&daddr=' + location_address
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'nodestroy': True,
            'target': 'new'
        }

    @api.multi
    def unassign_interpreter(self):
        ''' Function to unassign interpreter from assigned interpreter many2many '''
        to_del_int = self
        user = self.env.user
        if user.user_type not in ['staff', 'admin']:
            if to_del_int.user_id.id != self.env.uid:
                raise UserError(_('You cannot unassign another Interpreter'))
        event_state = self._context.get('event_state', False)
        if event_state in ('unbilled', 'invoiced', 'cancel', 'done'):
            raise UserError(_('Interpreter cannot be unassigned, since the event have already been taken place.'))
        event_id = self._context.get('event_id', False)
        sel_lines = self.env['select.interpreter.line'].sudo().search(
            [('event_id', '=', event_id), ('interpreter_id', '=', to_del_int.id), ('state', '=', 'assigned')],
            order='write_date').ids

        title = "Remove Interpreter"
        message = "Do you want to remove this Interpreter?"
        self = self.with_context(event_id=event_id, history_id=sel_lines[0] if sel_lines else False,
                                 interpreter_id=self.ids[0])
        return self.env['warning'].warning(title, message)

    @api.model
    def geo_localize_all(self):
        ''' This function Brings Langitude and Longitude for all Partners '''
        res, count, api_key = [], 0, False
        api_key_list = ['AIzaSyDAPZqsalpxu0T5SPRBXSG8K2ZVnngmmUo']
        partner_ids = self.env['res.partner'].search(
            [('is_geo', '=', False), ('cust_type', 'in', ('interpreter', 'interp_and_transl')),
             ('is_interpretation_active', '=', True)])
        logger.info(' partner_ids : %d', len(partner_ids))
        for partner_id in partner_ids:
            count += 1
            if count <= 2500:
                api_key = api_key_list[0]
            elif count > 2500 and count <= 5000:
                api_key = api_key_list[1]
            elif count > 5000 and count <= 7500:
                api_key = api_key_list[2]
            elif count > 7500 and count <= 10000:
                api_key = api_key_list[3]
            elif count > 10000 and count <= 12500:
                api_key = api_key_list[4]
            elif count > 12500 and count <= 15000:
                api_key = api_key_list[5]
            elif count > 15000 and count <= 17500:
                api_key = api_key_list[6]
            else:
                api_key = False
            res = partner_id.geo_localize2(api_key)
            if count % 500 == 0:
                #                print "count.....",count
                logger.info(' count : %d', count)
                self._cr.commit()
        return res

    @api.model
    def geo_localize2(self, api_key=False):
        # Don't pass context to browse()! We need country names in english below
        for partner in self:
            if not partner:
                continue
            result = geo_find(geo_query_address(street=partner.street, zip=partner.zip, city=partner.city,
                                                state=partner.state_id.name, country=partner.country_id.name), api_key)
            # print "result........",result
            if result:
                partner.write({
                    'latitude': result[0],
                    'longitude': result[1],
                    'date_localization': fields.Date.context_today(self),
                    'is_geo': True,
                })
        return True

    @api.multi
    def geo_localize(self):
        '''Function Used to geo localise partner '''
        # Don't pass context to browse()! We need country names in english below
        for partner in self:
            if not partner:
                continue
            result = geo_find(geo_query_address(street=partner.street, zip=partner.zip, city=partner.city,
                                                state=partner.state_id.name, country=partner.country_id.name))
            # print "result........",result
            if result:
                partner.write({
                    'latitude': result[0],
                    'longitude': result[1],
                    'date_localization': fields.Date.context_today(self),
                    'is_geo': True,
                })
        return True

    @api.model
    def get_sequence_for_partner(self, cust_type, company_name):
        ''' Function to get company wise sequence for all partners '''
        ref = '/'
        sequence_obj = self.env['ir.sequence']
        if company_name:
            if company_name.strip().upper() == 'IUG-SD' and cust_type:
                if cust_type == 'customer':
                    ref = sequence_obj.next_by_code('res.partner.iug.sd') or '/'
                elif cust_type == 'contact':
                    ref = sequence_obj.next_by_code('contact.iug.sd') or '/'
                elif cust_type == 'interpreter':
                    ref = sequence_obj.next_by_code('interpreter.iug.sd') or '/'
                elif cust_type == 'transporter':
                    ref = sequence_obj.next_by_code('transporter.iug.sd') or '/'
                elif cust_type == 'translator':
                    ref = sequence_obj.next_by_code('translator.iug.sd') or '/'
                elif cust_type == 'interp_and_transl':
                    ref = sequence_obj.next_by_code('interpreter_translator') or '/'
            elif company_name.strip().upper() == 'ASIT' and cust_type:
                if cust_type == 'customer':
                    ref = sequence_obj.next_by_code('res.partner.asit') or '/'
                elif cust_type == 'contact':
                    ref = sequence_obj.next_by_code('contact.asit') or '/'
                elif cust_type == 'interpreter':
                    ref = sequence_obj.next_by_code('interpreter.asit') or '/'
                elif cust_type == 'transporter':
                    ref = sequence_obj.next_by_code('transporter.asit') or '/'
                elif cust_type == 'translator':
                    ref = sequence_obj.next_by_code('translator.asit') or '/'
                elif cust_type == 'interp_and_transl':
                    ref = sequence_obj.next_by_code('interpreter_translator') or '/'
            elif company_name.strip().upper() == 'ACD' and cust_type:
                if cust_type == 'customer':
                    ref = sequence_obj.next_by_code('res.partner.acd') or '/'
                elif cust_type == 'contact':
                    ref = sequence_obj.next_by_code('contact.acd') or '/'
                elif cust_type == 'interpreter':
                    ref = sequence_obj.next_by_code('interpreter.acd') or '/'
                elif cust_type == 'transporter':
                    ref = sequence_obj.next_by_code('transporter.acd') or '/'
                elif cust_type == 'translator':
                    ref = sequence_obj.next_by_code('translator.acd') or '/'
                elif cust_type == 'interp_and_transl':
                    ref = sequence_obj.next_by_code('interpreter_translator') or '/'
            elif company_name.strip().upper() == 'ALBORS AND ALNET' and cust_type:
                if cust_type == 'customer':
                    ref = sequence_obj.next_by_code('res.partner.aa') or '/'
                elif cust_type == 'contact':
                    ref = sequence_obj.next_by_code('contact.aa') or '/'
                elif cust_type == 'interpreter':
                    ref = sequence_obj.next_by_code('interpreter.aa') or '/'
                elif cust_type == 'transporter':
                    ref = sequence_obj.next_by_code('transporter.aa') or '/'
                elif cust_type == 'translator':
                    ref = sequence_obj.next_by_code('translator.aa') or '/'
                elif cust_type == 'interp_and_transl':
                    ref = sequence_obj.next_by_code('interpreter_translator') or '/'
            elif company_name.strip().upper() == 'GLOBELINK FOREGIN LANGUAGE CENTER' and cust_type:
                if cust_type == 'customer':
                    ref = sequence_obj.next_by_code('res.partner.gl') or '/'
                elif cust_type == 'contact':
                    ref = sequence_obj.next_by_code('contact.gl') or '/'
                elif cust_type == 'interpreter':
                    ref = sequence_obj.next_by_code('interpreter.gl') or '/'
                elif cust_type == 'transporter':
                    ref = sequence_obj.next_by_code('transporter.gl') or '/'
                elif cust_type == 'translator':
                    ref = sequence_obj.next_by_code('translator.gl') or '/'
                elif cust_type == 'interp_and_transl':
                    ref = sequence_obj.next_by_code('interpreter_translator') or '/'

            else:
                ref = sequence_obj.next_by_code('res.partner.iug') or '/'
        elif cust_type:
            if cust_type == 'customer':
                ref = sequence_obj.next_by_code('res.partner.iug') or '/'
            elif cust_type == 'contact':
                ref = sequence_obj.next_by_code('contact.iug') or '/'
            elif cust_type == 'interpreter':
                ref = sequence_obj.next_by_code('interpreter.iug') or '/'
            elif cust_type == 'transporter':
                ref = sequence_obj.next_by_code('transporter.iug') or '/'
            elif cust_type == 'translator':
                ref = sequence_obj.next_by_code('translator.iug') or '/'
            elif cust_type == 'interp_and_transl':
                ref = sequence_obj.next_by_code('interpreter_translator') or '/'

        return ref

    @api.model
    def _check_phone_alpha(self, phone):
#        if phone:
 #           if not phone.strip().replace("+", "").replace("-", "").isdigit():
  #              raise UserError(
   #                 _(' You can only enter numbers, no alphabets or spaces \n E.g: 328-181-3700, 3281813700'))
        return {}

    @api.model
    def check_phone(self, vals):
        '''Function Used to Check and format all phone fields '''
        if vals.get('phone', False):
            final_phone, count, extension, ext = '', 0, '', ''
            chck_phone = vals.get('phone').encode("ascii", "ignore")
            try:
                chck_phone.decode('ascii')
                self._check_phone_alpha(chck_phone)
                if 'x' in chck_phone:
                    ext = chck_phone.split('x')[1]
                    chck_phone = chck_phone.split('x')[0]
                    for x in ext:
                        if x.isdigit():
                            extension += x
                chck_phone = chck_phone.lstrip('+1')
                for each in chck_phone:
                    if each.isdigit():
                        count += 1
                        final_phone += each
                # if count != 10:
                #     raise UserError(_('Please enter valid 10 digits Phone No.'))
                phone = '+1-' + final_phone[-10:-7] + '-' + final_phone[-7:-4] + '-' + final_phone[-4:]
                if extension:
                    phone = phone + ' ext.' + extension
                vals['phone'] = phone
            except UnicodeDecodeError:
                pass
        if vals.get('phone2', False):
            final_phone2, count2, extension2, ext2 = '', 0, '', ''
            chck_phone2 = vals.get('phone2').encode("ascii", "ignore")
            try:
                chck_phone2.decode('ascii')
                self._check_phone_alpha(chck_phone2)
                if 'x' in chck_phone2:
                    ext2 = chck_phone2.split('x')[1]
                    chck_phone2 = chck_phone2.split('x')[0]
                    for x2 in ext2:
                        if x2.isdigit():
                            extension2 += x2
                chck_phone2 = chck_phone2.lstrip('+1')
                for each2 in chck_phone2:
                    if each2.isdigit():
                        count2 += 1
                        final_phone2 += each2
                # if count2 != 10:
                #     raise UserError(_('Please enter valid 10 digits Phone No.'))
                phone2 = '+1-' + final_phone2[-10:-7] + '-' + final_phone2[-7:-4] + '-' + final_phone2[-4:]
                if extension2:
                    phone2 = phone2 + ' ext.' + extension2
                vals['phone2'] = phone2
            except UnicodeDecodeError:
                pass

        if vals.get('phone3', False):
            final_phone3, count3, extension3, ext3 = '', 0, '', ''
            chck_phone3 = vals.get('phone3').encode("ascii", "ignore")
            try:
                chck_phone3.decode('ascii')
                self._check_phone_alpha(chck_phone3)
                if 'x' in chck_phone3:
                    ext3 = chck_phone3.split('x')[1]
                    chck_phone3 = chck_phone3.split('x')[0]
                    for x3 in ext3:
                        if x3.isdigit():
                            extension3 += x3
                chck_phone3 = chck_phone3.lstrip('+1')
                for each3 in chck_phone3:
                    if each3.isdigit():
                        count3 += 1
                        final_phone3 += each3
                # if count3 != 10:
                #     raise UserError(_('Please enter valid 10 digits Phone No.'))
                phone3 = '+1-' + final_phone3[-10:-7] + '-' + final_phone3[-7:-4] + '-' + final_phone3[-4:]
                if extension3:
                    phone3 = phone3 + ' ext.' + extension3
                vals['phone3'] = phone3
            except UnicodeDecodeError:
                pass

        if vals.get('phone4', False):
            final_phone4, count4, extension4, ext4 = '', 0, '', ''
            chck_phone4 = vals.get('phone4').encode("ascii", "ignore")
            try:
                chck_phone4.decode('ascii')
                self._check_phone_alpha(chck_phone4)
                if 'x' in chck_phone4:
                    ext4 = chck_phone4.split('x')[1]
                    chck_phone4 = chck_phone4.split('x')[0]
                    for x4 in ext4:
                        if x4.isdigit():
                            extension4 += x4
                chck_phone4 = chck_phone4.lstrip('+1')
                for each4 in chck_phone4:
                    if each4.isdigit():
                        count4 += 1
                        final_phone4 += each4
                # if count4 != 10:
                #     raise UserError(_('Please enter valid 10 digits Phone No.'))
                phone4 = '+1-' + final_phone4[-10:-7] + '-' + final_phone4[-7:-4] + '-' + final_phone4[-4:]
                if extension4:
                    phone4 = phone4 + ' ext.' + extension4
                vals['phone4'] = phone4
            except UnicodeDecodeError:
                pass
        return vals

    @api.model
    def create(self, vals):
        '''Function Overridden to give company wise sequence and geo localize partner '''
        vals = self.check_phone(vals)
        if 'dob' in vals and vals['dob']:
            birth_date = datetime.strptime(vals['dob'], DEFAULT_SERVER_DATE_FORMAT)
            if birth_date.year > datetime.now().year:
                raise UserError(_('Birth Date can not be greater than current year.Please check '
                                  'Date of Birth'))
            vals['age'] = datetime.now().year - birth_date.year
        else:
            vals['age'] = ''
        new_id = super(res_partner, self).create(vals)
        if 'parent_id' in vals and vals['parent_id']:
            parent_type = self.env['res.partner'].browse(vals.get('parent_id')).cust_type
            if parent_type == 'customer':
                cust_type = 'contact'
            else:
                cust_type = parent_type
        else:
            cust_type = new_id.cust_type or False
        if vals.get('credit_limit', 0) < 0:
            raise UserError(_("Invalid Value! Input should be greater than Zero. "))
        company_name = new_id.company_id and new_id.company_id.name or False
        ref = new_id.get_sequence_for_partner(cust_type, company_name)
        new_id.write({'ref': ref, 'cust_type': cust_type})
        new_id.message_unsubscribe_users(user_ids=[self.env.uid])
        if cust_type:
            if cust_type == 'interpreter' or cust_type == 'transporter' or cust_type == 'customer':
                 new_id.geo_localize()
            if cust_type == 'interpreter':
                 try:
                     new_id.create_interpreter_login()
                 except Exception, e:
                     logger.info(' Error : %s', e.args)
        return new_id

    @api.multi
    def write(self, vals):
        '''Function Over ridden to geo localise partner on change of address '''
        cur_obj = self
        cust_type = False
        if vals.get('name', False) or vals.get('last_name', False):
            name, last_name, complete_name = '', '', ''
            name = vals.get('name', False)
            if not name:
                name = cur_obj.name
            last_name = vals.get('last_name', False)
            if not last_name:
                last_name = cur_obj.last_name
            complete_name = unicode(name) + ' ' if name else '' + unicode(last_name)
            vals['complete_name'] = complete_name
        if 'cust_type' in vals and vals['cust_type']:
            cust_type = vals.get('cust_type', False)

        if vals.get('credit_limit', 0) < 0:
            raise UserError(_("Invalid Value! Input should be greater than Zero. "))
        if cust_type in ('interpreter', 'transporter', 'interp_and_transp'):
            if 'street' in vals or 'street2' in vals or 'city' in vals or 'state_id' in vals or 'country_id' in vals or 'zip' in vals:
                 street, street2, city, state_id, country_id, zip = False, False, False, False, False, False
                 if 'street' in vals and vals['street']:
                     street = vals.get('street', False)
                 else:
                     street = cur_obj.street
                 if 'street2' in vals and vals['street2']:
                     street2 = vals.get('street2', False)
                 else:
                     street2 = cur_obj.street2
                 if 'city' in vals and vals['city']:
                     city = vals.get('city', False)
                 else:
                     city = cur_obj.city
                 if 'state_id' in vals and vals['state_id']:
                     state_id = vals.get('state_id', False)
                 else:
                     state_id = cur_obj.state_id and cur_obj.state_id.id or False
                 if 'country_id' in vals and vals['country_id']:
                     country_id = vals.get('country_id', False)
                 else:
                     country_id = cur_obj.country_id and cur_obj.country_id.id or False
                 if 'zip' in vals and vals['zip']:
                     zip = vals.get('zip', False)
                 else:
                     zip = cur_obj.zip
                 state = False
                 if state_id:
                     state = self.env['res.country.state'].browse(state_id)
                 country = False
                 if country_id:
                     country = self.env['res.country'].browse(country_id)
                 if street2:
                     if street:
                         street += ' ' + unicode(street2)
                     else:
                         street = street2
                 try:
                     result = geo_find(
                         geo_query_address(street or False, zip or False, city or False, state and state.name or False,
                                           country and country.name or False))
                     if result:
                         vals['latitude'] = result[0]
                         vals['longitude'] = result[1]
                         vals['is_geo'] = True
                         vals['date_localization'] = fields.Date.context_today(self)
                 except Exception:
                     pass
        if 'phone' in vals or 'phone2' in vals or 'phone3' in vals or 'phone4' in vals:
            vals = self.check_phone(vals)
        if 'dob' in vals and vals['dob']:
            birth_date = datetime.strptime(vals['dob'], DEFAULT_SERVER_DATE_FORMAT)
            if birth_date.year > datetime.now().year:
                raise UserError(_('Birth Date can not be greater than current year.Please check Date of Birth'))
            vals['age'] = datetime.now().year - birth_date.year
        else:
            vals['age'] = ''
        return super(res_partner, self).write(vals)
        


    @api.model
    def default_get(self, fields):
        ''' This function auto fill company_id related to interpreter '''
        res = super(res_partner, self).default_get(fields)
        if self._context.get('company_id', False):
            if 'company_id' in fields:
                res.update({'company_id': self._context.get('company_id', False)})
        return res
   
   # @api.multi
   # def update_complete_name(self):
    #   
#	res = {}
#	v1= self.env['res.partner'].search([])
 #       _logger.info('--------v1--------(%s)',len(v1))
  #3      for line in self.env['res.partner'].search([]):
#	    complete_name = ""
#	    if line.last_name:
#	        complete_name = line.name.encode('utf-8', 'ignore').strip() + " " + line.last_name.encode('utf-8',
#	                                                                                                  'ignore').strip()
#	    if line.contract_no:
#	        if complete_name:
#	           complete_name += " "+ line.contract_no.encode('utf-8','ignore').strip()
#	           _logger.info('line.contract_no%s',complete_name)
#	        else:
#	            complete_name = line.name.encode('utf-8', 'ignore').strip() + " " + line.contract_no.encode('utf-8','ignore').strip()
#	    if line.opi_no:
#	        if complete_name:
#	            complete_name += " " + line.opi_no.encode('utf-8', 'ignore').strip()
#	        else:
#	            complete_name = line.name.encode('utf-8', 'ignore').strip() + " " + line.opi_no.encode('utf-8','ignore').strip()
#	    else:
#	        complete_name = line.name.encode('utf-8', 'ignore').strip()
#	    complete_name = complete_name.replace('   ', ' ')
#	    line.complete_name= complete_name.replace('  ', ' ')
#	    _logger.info('complete_name%s',complete_name)
#	    _logger.info('line.complete_name%s',line.complete_name)
 
    @api.depends('last_name', 'name','contract_no','opi_no')
    def _name_get_fnc(self):
        ''' Function to store complete Partner name to be used in search '''
	res = {}
	for line in self:
	    complete_name = ""
	    if line.last_name:
	        complete_name = line.name.encode('utf-8', 'ignore').strip() + " " + line.last_name.encode('utf-8','ignore').strip()
                _logger.info('line.last name last name%s',complete_name)
	    if line.contract_no:
	        if complete_name:
	           complete_name += " "+ line.contract_no.encode('utf-8','ignore').strip()
	           _logger.info('line.contract_no%s',complete_name)
	        else:
	            complete_name = line.name.encode('utf-8', 'ignore').strip() + " " + line.contract_no.encode('utf-8','ignore').strip()
	    if line.opi_no:
	        if complete_name:
	            complete_name += " " + line.opi_no.encode('utf-8', 'ignore').strip()
	        else:
	            complete_name = line.name.encode('utf-8', 'ignore').strip() + " " + line.opi_no.encode('utf-8','ignore').strip()
	    if not complete_name:
	        complete_name = line.name.encode('utf-8', 'ignore').strip()
	    complete_name = complete_name.replace('   ', ' ')
	    line.complete_name= complete_name.replace('  ', ' ')
	    _logger.info('complete_name%s',complete_name)
	    _logger.info('line.complete_name%s',line.complete_name)

    @api.depends('phone', 'phone2', 'phone3', 'phone4')
    def _get_cell_phone(self):
        '''Function to get Cellphone of the partner '''
        res, phone = {}, ''
        for partner in self:
            if partner.phone_type_id1 and partner.phone_type_id1.name and 'cell' in partner.phone_type_id1.name.lower():
                phone = partner.phone
            elif partner.phone_type_id2 and partner.phone_type_id2.name and 'cell' in partner.phone_type_id2.name.lower():
                phone = partner.phone2
            elif partner.phone_type_id3 and partner.phone_type_id3.name and 'cell' in partner.phone_type_id3.name.lower():
                phone = partner.phone3
            elif partner.phone_type_id4 and partner.phone_type_id4.name and 'cell' in partner.phone_type_id4.name.lower():
                phone = partner.phone4
            if not phone:
                phone = partner.phone or ''
            a = str(phone)
            a = a.lstrip('+1')
            #            phone2=a[-10:-7]+'-'+a[-7:-4]+'-'+a[-4:]
            final_phone = ''
            for dig in a:
                if dig.isdigit():
                    final_phone += dig
            phone2 = final_phone[0:3] + '-' + final_phone[3:6] + '-' + final_phone[6:]
            partner.cell_phone = phone2


    # def _get_user_ids(self, cr, uid, ids, field_id, args,context=None):
    #     ''' Function to get user_ids related to this partner '''
    #     result, user_ids = {}, []
    #     user_obj = self.pool.get('res.users')
    #     for partner in self.browse(cr, uid, ids, context=context):
    #         user_ids = []
    #         if partner.company_id:
    #             user_ids = user_obj.search(cr, uid, [('partner_id','=',partner.id),('company_ids','in',partner.company_id.id)])
    #         else:
    #             user_ids = user_obj.search(cr, uid, [('partner_id','=',partner.id)])
    #         user_ids = list(set(flatten(user_ids)))
    #         if user_ids:
    #             result[partner.id] = user_ids[0]
    #         else:
    #             result[partner.id] = False
    #     return result

    # def _get_user_id(self, cr, uid, ids, context=None):
    #     result = {}
    #     for line in self.pool.get('res.users').browse(cr, uid, ids, context=context):
    #         result[line.partner_id.id] = True
    #     return result.keys()

    @api.depends('interpreter_history2')
    def _get_job_offered_ids(self):
        ''' Function to get Future and current Job Offers '''
        result, history_ids = {}, []
        user = self.env.user
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.utc
        local_date = tz.localize(datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), DATETIME_FORMAT),
                                 is_dst=None)
        local_date = datetime.strptime(local_date.astimezone(tz).strftime(DATETIME_FORMAT), DATETIME_FORMAT).strftime(
            '%Y-%m-%d')

        for partner in self:
            history_ids = []
            for history in partner.interpreter_history2:
                if history.state == 'voicemailsent' and history.event_date >= local_date:
                    if history.event_id:
                        if history.event_id.state == 'scheduled':
                            history_ids.append(history.id)
                    else:
                        history_ids.append(history.id)
            partner.interpreter_work_ids = history_ids

    @api.depends('language_lines.certification_level_id')
    def _get_certification_level_id(self):
        #        _logger.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>self>>>%s>>>>>>",self._origin)
        for line in self:
            # if line.interpreter_id:
            certification_name = ''
            for lang in line.language_lines:
                if lang.certification_level_id:
                    certification_name = certification_name + " " + lang.certification_level_id.name
            if certification_name:
                _logger.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>certification_name>>>%s>>>", certification_name)
                line.certification_comp_name = certification_name
                _logger.info(">>>>>>>>>>>>>>>>>>>>>line.interpreter_id.certification_comp_name>>>%s>>>",
                             line.certification_comp_name)



    name = fields.Char('Name', size=128, required=True, index=True, track_visibility='onchange')
    ref = fields.Char('Reference', size=64, index=1, readonly=True, track_visibility='onchange', default='/')
    active = fields.Boolean('Active', track_visibility='onchange')
    parent_id = fields.Many2one('res.partner', 'Related Company', track_visibility='onchange')
    comment = fields.Text('Notes', track_visibility='onchange')
    vaccine = fields.Text('Vaccines')
    street = fields.Char('Street', size=128, track_visibility='onchange')
    street2 = fields.Char('Street2', size=128, track_visibility='onchange')
    zip = fields.Char('Zip', change_default=True, size=24, track_visibility='onchange')
    city = fields.Char('City', size=128, track_visibility='onchange')
    state_id = fields.Many2one("res.country.state", 'State', track_visibility='onchange')
    ssnid = fields.Char('SSN No', size=34, help='Social Security Number', track_visibility='onchange')
    sinid = fields.Char('Social Insurance Number', size=34, help="Social Insurance Number", track_visibility='onchange')
    country_id = fields.Many2one('res.country', 'Country', track_visibility='onchange')
    company_id = fields.Many2one('res.company', 'Company', index=1, track_visibility='onchange', required=True)
    project_part_ids = fields.Many2many('project', 'partner_project_group_rel', 'project_id', 'partner_id', 'Projects')
    is_interpretation_active = fields.Boolean('Is Interpretation Active?', default=False)
    is_translation_active = fields.Boolean('Is Translation Active?', default=False)
    is_transportation_active = fields.Boolean('Is Transportation Active?', default=False)
    cell_phone = fields.Char(compute=_get_cell_phone, string='Cell Phone')
    email2 = fields.Char('Email 2', size=240, track_visibility='onchange')
    phone2 = fields.Char('Phone 2', size=64, track_visibility='onchange')
    is_alert = fields.Boolean('Alert', help="Select if on alert")
    confirmation_email = fields.Boolean('Confirmation Email', help="")
    middle_name = fields.Char('Middle Name', size=128, index=True, track_visibility='onchange')
    last_name = fields.Char('Last Name', size=128, index=True, track_visibility='onchange')
    short_name = fields.Char('DBA', size=100, index=True)
    department = fields.Char('Department', size=64, index=True)
    call_date = fields.Date('Free Confrence Call', index=1)
    extension1 = fields.Char('Extension 1', size=32)
    extension2 = fields.Char('Extension 2', size=32)
    ext_phone1 = fields.Char('Ext Phone1')
    ext_phone2 = fields.Char('Ext Phone2')
    ext_phone3 = fields.Char('Ext Phone3')
    ext_phone4 = fields.Char('Ext Phone4')
    phone_type_id1 = fields.Many2one('phone.type', "Phone Type 1")
    phone_type_id2 = fields.Many2one('phone.type', "Phone Type 2")
    customer_type = fields.Many2one('customer.type', 'Type', track_visibility='onchange')
    telephone_interpretation = fields.Boolean("Telephone Interpretation", help="")
    billing_comment = fields.Text('Billing Notes', track_visibility='onchange')
    rubrik = fields.Text('Rubrik', track_visibility='onchange')
    billing_contact = fields.Boolean("Billing Contact", )
    ordering_contact = fields.Boolean("Ordering Contact", )

    billing_partner_id = fields.Many2one('res.partner', "Billing Customer", domain="[('cust_type','=','customer')]",
                                         track_visibility='onchange')
    billing_contact_id = fields.Many2one('res.partner', "Billing Contact", domain="[('cust_type','=','contact')]",
                                         track_visibility='onchange')
    head_contact_id = fields.Many2one('res.partner', "Head Contact", domain="[('cust_type','=','contact')]",
                                      track_visibility='onchange')
    opt_out_of_feedback_emails = fields.Boolean(string='Opt out of feedback emails')
    interpreter_history = fields.One2many('interpreter.alloc.history', 'partner_id', 'Interpreter History',
                                          readonly=True, )
    transporter_history = fields.One2many('transporter.alloc.history', 'name', 'Transporter History', readonly=True)
    translator_history = fields.One2many('translator.alloc.history', 'name', 'Translator History', readonly=True)
    block_inter_ids = fields.Many2many('res.partner', 'part_cust_rel', 'part_id', 'cust_id', 'Does Not Vist')
    is_adjuster = fields.Boolean('Adjuster?')
    is_payee = fields.Boolean('Payee?')
    company_name = fields.Char('Company Name', size=64, index=True)
    location = fields.Char('Location', size=64)
    mental_prog = fields.Selection([('child', 'Child'), ('adult', 'Adult')], 'Mental health prg.')

    #        'street3': fields.char('Street', size=128),
    #        'street4': fields.char('Street2', size=128),
    #        'zip2': fields.char('Zip', change_default=True, size=24),
    #        'city2': fields.char('City', size=128),
    #        'state_id2': fields.many2one("res.country.state", 'State',),
    #        'country_id2': fields.many2one('res.country', 'Country',),
    #        'country2': fields.related('country_id2', type='many2one', relation='res.country', string='Country',
    #                                  deprecated="This field will be removed as of OpenERP 7.1, use country_id instead"),
    phone2 = fields.Char('Phone 2', size=64)
    email2 = fields.Char('Email 2', size=240)
    fax2 = fields.Char('Fax', size=64)
    user_id = fields.Many2one('res.users', "Related Users", default=lambda self: self.env.user.id)
    scheduler_id = fields.Many2one('res.users', 'Scheduler', domain="[('user_type','=','staff')]")
    sales_representative_id = fields.Many2one('res.users', 'Sales Representative', domain="[('user_type','=','staff')]",
                                              default=lambda self: self.env.user.id)
    # 'res_user_id': fields.many2one('res.users', "Sales person Resp:"),
    #        'created_by': fields.many2one('res.users', "Created By"),
    #        'updated_by': fields.many2one('res.users', "Updated By"),
    ext = fields.Char('Ext:', size=32)
    credit_card_lines = fields.One2many('credit.card', 'customer_id', "Credit Cards")
    auth_cc_number = fields.Char('Credit Card Number', size=20, help="Credit Card Number")
    auth_cc_expiration_date = fields.Char('CC Exp Date [MMYYYY]', size=6, help="Credit Card Expiration Date")
    #        'billing_addr': fields.many2one('res.partner','Billing Address'),
    #        'shipping_addr': fields.many2one('res.partner','Shipping Address'),
    customer_profile = fields.Boolean('Customer Profile')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], "Gender", track_visibility='onchange')
    customer_id = fields.Integer("IU Customer ID")
    contact_id = fields.Integer("IU Contact ID")
    provider_id = fields.Integer("IU Provider ID")
    expiry_date = fields.Date('IU Credit Card Expiry Date', index=1)
    login_id = fields.Integer("IU Login Id")
    fee_note = fields.Boolean('Fee Note*', track_visibility='onchange')
    order_note = fields.Boolean('SAF', track_visibility='onchange')
    need_glcode = fields.Boolean("Need GLCode/GLUID/Approving MGR", )
    gsa = fields.Boolean("GSA", )
    is_csid = fields.Boolean('CSID')
    customer_basis = fields.Boolean('Customer Basis?', help="Customer Basis Scheduler in the Event Form")
    gpuid = fields.Char('Gl Code', size=256)
    csid = fields.Char('CSID', size=256)
    cust_type = fields.Selection([('customer', 'Customer'), ('contact', 'Contact'), ('interpreter', 'Interpreter'),
                                  ('translator', 'Translator'), ('transporter', 'Transporter'),
                                  ('interp_and_transl', 'Interpreter & Translator'),
                                  ('company', 'Company'), ('other', 'Other')],
                                 "Type", required=True, help="This categorizes ,what kind of partner it is ",
                                 default='other')
    billing_rule_ids = fields.Many2many('billing.rule', 'customer_billing_rule_rel', 'customer_id', 'billing_rule_id',
                                        'Billing Rule')
    #        'duplicate_partner':fields.boolean('Duplicate Partner'),
    special_customer = fields.Boolean('Special Customer', default=False)
    complete_name = fields.Char(compute=_name_get_fnc, string='Complete Name',store=True)
    parent_cust_id = fields.Many2one('res.partner', 'Parent Customer')

    # --------------------------------------- Interpreter -----------------------------
    contract_on_file = fields.Boolean('Contract On File')
    contract_no = fields.Char('Contract#', size=20, help="Contract number")
    opi_no= fields.Char('OPI#')
    rating_id = fields.Many2one('rating', "Rating")
    due_days = fields.Integer("Due Days")
    resume_on_file = fields.Boolean('Resume On File', help="")
    wb_on_file = fields.Boolean('W9 On File', help="")
    rate = fields.Float("Per Mile Bill Rate", digits=(16, 3))
    discount = fields.Float("Discount", digits=(16, 2))
    #        'distribution': fields.many2one("distribution","Distribution",),
    zone_id = fields.Many2one("zone", "Zone", )
    modem = fields.Char('Modem', size=64, )
    phone3 = fields.Char('Phone 3', size=64)
    phone4 = fields.Char('Phone 4', size=64)
    phone_type_id3 = fields.Many2one('phone.type', "Phone Type 3")
    phone_type_id4 = fields.Many2one('phone.type', "Phone Type 4")
    language_lines = fields.One2many("interpreter.language", 'interpreter_id', 'Language')
    interpreter_alloc_history = fields.One2many('interpreter.alloc.history', 'name', 'Interpreter Alloc History',
                                                readonly=True)
    interpreter_history2 = fields.One2many('interpreter.history', 'name', 'Job Offered History', )
    interpreter_work_ids = fields.Many2many('interpreter.history', compute=_get_job_offered_ids,
                                            string="Job Offered History")
    interaction_ids = fields.One2many(comodel_name="interaction", inverse_name="interpreter_id", string="Interactions", required=False, )
    interpreter_id = fields.Many2one(comodel_name="res.partner", string="Interpreter", required=False, )


    #        'interpreter_affiliation_ids': fields.many2many('affiliation','interpreter_affiliation_rel','interprter_id','affiliation_id',
    #                                    'Interpreter Affiliation',readonly=True ),
    meta_zone_id = fields.Many2one('meta.zone', "Meta Zone")
    vendor_id = fields.Integer("IU Vendor ID")
    quickbooks_id = fields.Char("IU QuickBooks ID", size=32)
    is_schedular = fields.Boolean('Is Schedular', help="")
    is_monthly = fields.Boolean("Is Monthly", help='Is monthly invoiced', default=False)
    extension = fields.Char('Extension', size=64, )
    end_date = fields.Date('End Date', )
    #        'degree_type_id1': fields.many2one('degree.type','Degree Type 1'),
    #        'degree_subject_id1': fields.many2one('degree.subject','Degree Subject 1'),
    #        'degree_country_id1': fields.many2one('res.country','Degree Country 1'),
    #        'degree_type_id2': fields.many2one('degree.type','Degree Type 2'),
    #        'degree_subject_id2': fields.many2one('degree.subject','Degree Subject 2'),
    #        'degree_country_id2': fields.many2one('res.country','Degree Country 2'),

    bill_miles_after = fields.Float('Bill After Miles', digits=(16, 3))
    language_id = fields.Many2one(related='language_lines.name', string="Language", store=True)
    latitude = fields.Float('Geo Latitude', digits=(16, 6), readonly=True)
    longitude = fields.Float('Geo Longitude', digits=(16, 6), readonly=True)
    date_localization = fields.Date('Geo Localization Date')
    is_geo = fields.Boolean("IS Geo", default=False)
    #        'base_hour': fields.selection([('1hour','1 Hour'),('2hour','2 Hour'),('3hour','3 Hour')],'Normal Base Hour'),
    #        'inc_min': fields.selection([('15min','15 Min'),('30min','30 Min')],'Normal Inc Min'),
    #        'base_hour_med': fields.selection([('1hour','1 Hour'),('2hour','2 Hour'),('3hour','3 Hour')],'Med Base Hour'),
    #        'inc_min_med': fields.selection([('15min','15 Min'),('30min','30 Min')],'Med Inc Min'),
    #        'base_hour_depos': fields.selection([('1hour','1 Hour'),('2hour','2 Hour'),('3hour','3 Hour')],'Depos Base Hour'),
    #        'inc_min_depos': fields.selection([('15min','15 Min'),('30min','30 Min')],'Depos Inc Min'),
    #        'base_hour_conf': fields.selection([('1hour','1 Hour'),('2hour','2 Hour'),('3hour','3 Hour')],'Conf. Base Hour'),
    #        'inc_min_conf': fields.selection([('15min','15 Min'),('30min','30 Min')],'Conf. Inc Min'),
    rate_ids = fields.One2many('rate', 'partner_id', 'Rate')
    #        'normal_rate_ids': fields.one2many('rate', 'interpreter_id',"Normal Interpreter Rate",),
    #        'medical_rate_ids': fields.one2many('rate', 'interpreter_id2',"Medical Interpreter Rate",),
    #        'deposition_rate_ids': fields.one2many('rate', 'interpreter_id3',"Deposition Interpreter Rate",),
    #        'conf_call_rate_ids': fields.one2many('rate', 'interpreter_id4',"Conf. Interpreter Rate",),
    #        'interpreter_assign_history':fields.one2many('assign.interpreter.history','name','Interpreter Assign History',readonly=True),
    dob = fields.Date('Date of Birth')
    age = fields.Char('Age', readonly=True)
    # ------------------------------Translator----------------------------------------------
    do_editing = fields.Boolean('Do Editing?', help="")
    is_agency = fields.Boolean('Is Agency', help="")
    minimum_rate = fields.Float("Minimum Rate")
    min_editing_rate = fields.Float("Minimum Editing Rate")
    translator_software_ids = fields.Many2many('software', 'translator_software_rel', 'translator_id', 'software_id',
                                               'Translator Software')
    trans_language_lines = fields.One2many("translator.language", 'translator_id', 'Language')
    translator_affiliation_ids = fields.Many2many('affiliation', 'translator_affiliation_rel', 'translator_id',
                                                  'affiliation_id', 'Translator Affiliation')
    last_update_date = fields.Date("Last Update Date", default=lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT))
    translator_assign_history = fields.One2many('assign.translator.history', 'name', 'Translator Assign History',
                                                readonly=True)
    ##------------------------------Translator----------------------------------------------
    transporter_rate_lines = fields.One2many('transporter.rate', 'transporter_id', 'Transporter Rate')
    #        'transporter_assign_history':fields.one2many('assign.transporter.history','name','Transporter Assign History',readonly=True),
    has_login = fields.Boolean('Has Login', default=False)
    #        'event_approval': fields.boolean('Event Approval Required'),
    #        'event_verification': fields.boolean('Event Verification Required'),
    suppress_email = fields.Boolean('Suppress Email')
    location_lines = fields.One2many('location', 'ordering_partner_id', 'Related locations')
    #        'company_ids':fields.many2many('res.company','res_company_users_rel','user_id','cid','Companies'),
    #        'allowed_comp_ids': fields.related('company_ids','id', type='many2many', relation="res.company",  string="All Allowed Companies",select=True),
    #        'related_user_id': fields.function(_get_user_ids, type='many2one', obj="res.users", string="Related User", store=True, select=True
    ##                                    store={
    ##                                        'res.users': (_get_user_id, ['company_ids'], 20),}
    #                                    ),
    #        'allowed_comp_ids': fields.related('related_user_id','company_ids', type='many2many', relation="res.company", string="Allowed Companies", select=True),
    customer_group_id = fields.Many2one('customer.group', 'Customer Group', track_visibility='onchange')
    interpreter_id = fields.Many2one('res.partner', "Preferred Interpreter")
    is_sync = fields.Boolean('Is Synced')
    albors_id = fields.Integer('Albors ID', readonly=True)
    is_project_required = fields.Boolean('Is Project Required?')
    is_reference_required = fields.Boolean('Is Reference Required?')
    mon_time_from = fields.Char("Monday", size=2, default='12')
    mon_time_from_min = fields.Char("Min", size=2, default='00')
    mon_am_pm1 = fields.Selection([('am', 'AM'), ('pm', 'PM')], "AM/PM", default='am')
    mon_time_to = fields.Char("Monday", size=2, default='11')
    mon_time_to_min = fields.Char("Min", size=2, default='59')
    mon_am_pm2 = fields.Selection([('am', 'AM'), ('pm', 'PM')], "AM/PM", default='pm')
    mon_check = fields.Boolean("Monday Available")
    tue_time_from = fields.Char("Tuesday", size=2, default='12')
    tue_time_from_min = fields.Char("Min", size=2, default='00')
    tue_am_pm1 = fields.Selection([('am', 'AM'), ('pm', 'PM')], "AM/PM", default='am')
    tue_time_to = fields.Char("Tuesday", size=2, default='11')
    tue_time_to_min = fields.Char("Min", size=2, default='59')
    tue_am_pm2 = fields.Selection([('am', 'AM'), ('pm', 'PM')], "AM/PM", default='pm')
    tue_check = fields.Boolean("Tuesday Available")
    wed_time_from = fields.Char("Wednesday", size=2, default='12')
    wed_time_from_min = fields.Char("Min", size=2, default='00')
    wed_am_pm1 = fields.Selection([('am', 'AM'), ('pm', 'PM')], "AM/PM", default='am')
    wed_time_to = fields.Char("Wednesday", size=2, default='11')
    wed_time_to_min = fields.Char("Min", size=2, default='59')
    wed_am_pm2 = fields.Selection([('am', 'AM'), ('pm', 'PM')], "AM/PM", default='pm')
    wed_check = fields.Boolean("Wednesday Available")
    thur_time_from = fields.Char("Thursday", size=2, default='12')
    thur_time_from_min = fields.Char("Min", size=2, default='00')
    thur_am_pm1 = fields.Selection([('am', 'AM'), ('pm', 'PM')], "AM/PM", default='am')
    thur_time_to = fields.Char("Thursday", size=2, default='11')
    thur_time_to_min = fields.Char("Min", size=2, default='59')
    thur_am_pm2 = fields.Selection([('am', 'AM'), ('pm', 'PM')], "AM/PM", default='pm')
    thur_check = fields.Boolean("Thursday Available")
    fri_time_from = fields.Char("Friday", size=2, default='12')
    fri_time_from_min = fields.Char("Min", size=2, default='00')
    fri_am_pm1 = fields.Selection([('am', 'AM'), ('pm', 'PM')], "AM/PM", default='am')
    fri_time_to = fields.Char("Friday", size=2, default='11')
    fri_time_to_min = fields.Char("Min", size=2, default='59')
    fri_am_pm2 = fields.Selection([('am', 'AM'), ('pm', 'PM')], "AM/PM", default='pm')
    fri_check = fields.Boolean("Friday Available")
    sat_time_from = fields.Char("Saturday", size=2, default='12')
    sat_time_from_min = fields.Char("Min", size=2, default='00')
    sat_am_pm1 = fields.Selection([('am', 'AM'), ('pm', 'PM')], "AM/PM", default='am')
    sat_time_to = fields.Char("Saturday", size=2, default='11')
    sat_time_to_min = fields.Char("Saturday", size=2, default='59')
    sat_am_pm2 = fields.Selection([('am', 'AM'), ('pm', 'PM')], "AM/PM", default='pm')
    sat_check = fields.Boolean("Saturday Available")
    sun_time_from = fields.Char("Sunday", size=2, default='12')
    sun_time_from_min = fields.Char("Min", size=2, default='00')
    sun_am_pm1 = fields.Selection([('am', 'AM'), ('pm', 'PM')], "AM/PM", default='am')
    sun_time_to = fields.Char("sunday", size=2, default='11')
    sun_time_to_min = fields.Char("Min", size=2, default='59')
    sun_am_pm2 = fields.Selection([('am', 'AM'), ('pm', 'PM')], "AM/PM", default='pm')
    sun_check = fields.Boolean("Sunday Available")
    holiday_from = fields.Date("Holiday From")
    holiday_to = fields.Date("Holiday To")
    vaccine_lines = fields.One2many("vaccines", 'interpreter_id', 'Vaccines')
    w_start_time = fields.Char("start Time", size=2, default='00')
    w_am_pm1 = fields.Selection([('am', 'AM'), ('pm', 'PM')], "AM/PM", default='am')
    w_end_time = fields.Char("End Time", size=2, default='00')
    w_am_pm2 = fields.Selection([('am', 'AM'), ('pm', 'PM')], "AM/PM", default='pm')
    even_start_time = fields.Char("start Time", size=2, default='00')
    even_am_pm1 = fields.Selection([('am', 'AM'), ('pm', 'PM')], "AM/PM", default='am')
    even_end_time = fields.Char("End Time", size=2, default='00')
    even_am_pm2 = fields.Selection([('am', 'AM'), ('pm', 'PM')], "AM/PM", default='pm')
    certification_comp_name = fields.Char("Certification Name", compute=_get_certification_level_id, store=True)

    @api.onchange('parent_cust_id')
    def onchange_parent_customer(self):
        ''' Function to check whether customer is Kaiser and set Need Glcode '''
        val = {}
        if self.parent_cust_id:
            val = {
                'sales_representative_id': self.parent_cust_id.sales_representative_id.id,
            }
        return {'value': val}
 
    @api.multi
    def _check_rate_ids(self):
        ''' validates Rate lines . You can not add Rate in more than 4 lines '''
        for partner in self:
            if partner.cust_type in ('interpreter', 'customer'):
                lines_ids = partner.rate_ids
                if len(lines_ids) > 5:
                    raise UserError(_(' You can enter max four line in Rate Lines .'))
        return True

    @api.multi
    def _check_language(self):
        ''' validates Interpreter and Translator for , atleast one language should be entered while creating'''
        for partner in self:
            if partner.cust_type == 'interpreter':
                lines = partner.language_lines
                if len(lines) < 1:
                    raise UserError(_(' Please enter atleast one language for Interpreter .'))
            elif partner.cust_type == 'translator':
                lines = partner.trans_language_lines
                if len(lines) < 1:
                    raise UserError(_(' Please enter atleast one language for Translator .'))
        return True

    @api.multi
    def _check_phone(self):
        ''' validates all phone number fields on the form '''
        for partner in self:
            if partner.rate < 0:
                raise UserError(_('Rate Can not be less than zero !'))
            if partner.bill_miles_after < 0:
                raise UserError(_('Bill Miles After Can not be less than zero !'))
        return True

    @api.multi
    def _check_rates(self):
        ''' validates rates  for less than zero on the partner form '''
        for partner in self:
            if partner.rate < 0:
                raise UserError(_('Rate Can not be less than zero !'))
            if partner.bill_miles_after < 0:
                raise UserError(_('Bill Miles After Can not be less than zero !'))
        return True

    @api.multi
    def _check_zip(self):
        ''' validates zip for only integer number allowed '''
        for partner in self:
            zip = partner.zip
            if zip:
                try:
                    input = int(zip)
                except ValueError:
                    return False
        return True

    _constraints = [(models.BaseModel._check_recursion, 'You cannot create recursive hierarchies.', ['parent_id']),
                    #                    (_check_language, ' """ {  Please enter atleast one language. }""" ',['language_lines']),
                    (_check_rate_ids, '', []),
                    (_check_rates, '', [])
                    ]

    @api.onchange('name')
    def onchange_name(self):
        ''' Function to check whether customer is Kaiser and set Need Glcode '''
        val = {}
        if not self.name:
            return {'value': {'need_glcode': False, }}
        if 'kaiser' in (self.name).lower():
            val['need_glcode'] = True
        return {'value': val}

    #    def onchange_order_note(self, cr, uid, ids, field,context={}):
    #        val = {}
    #        if field:
    #            val = {'event_approval':True,
    #                   'event_verification':True,}
    #        else:
    #            val= {'event_approval':False,
    #                  'event_verification':False,}
    #        return {'value': val}

    # def script_correct_names(self,cr,uid,ids,context=None):
    #     ''' Script to correct Partner names on live server.'''
    #     part_ids = self.search(cr,uid,[('has_login','=',True)])
    #     count = 0
    #     for partner in self.browse(cr,uid,part_ids):
    #         count+=1
    #         last_name ,  name = '',''
    #         if partner.last_name:
    #             last_name = ' '+partner.last_name
    #             name = partner.name.replace(last_name,'') if partner.name else ''
    #             if name:
    #                 partner.write({'name':unicode(name)})
    #         if count%1000 == 0:
    #             cr.commit()
    #             _logger.info('partner count%s',count)
    #     return True

    @api.multi
    def upload_attachment(self):
        ''' function to Upload Attachment with Document type '''
        self = self.with_context(active_ids=self.ids, active_model=self._name)
        wizard_id = self.env['upload.attachment.wizard'].create({}).id
        view_ref = self.env['ir.model.data'].sudo().get_object_reference('bista_iugroup', 'upload_attachments_wizard')
        view_id = view_ref[1] if view_ref else False
        return {
            'name': _("Upload Attachment"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'upload.attachment.wizard',
            'res_id': wizard_id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': self._context,
        }

    @api.model
    def validate_email(self, email):
        '''Function to validate email '''
        if email:
            if not re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,4}|[0-9]{1,3})(\\]?)$", email):
                raise UserError(_('Please enter valid Email to be used as login for the user.'))
        return True

    @api.multi
    def get_timezone_for_partner(self):
        '''Function to get timezone while creating logins'''
        zip_ids, time_zone = False, False
        zip_time_zone = self.env['zip.time.zone']
        for partner in self:
            if partner.zip:
                zip_ids = zip_time_zone.search([('name', '=', partner.zip)])
                if not zip_ids and partner.state_id and partner.state_id.code:
                    zip_ids = zip_time_zone.search([('state_code', '=', partner.state_id.code)])
            if zip_ids:
                time_zone = zip_ids[0].time_zone
            if time_zone:
                time_zone = _timezone_event.get(int(time_zone), False)
        return time_zone

    @api.multi
    def resend_login_mail(self):
        user_id = self.user_id
        if user_id:
            user_id.sudo().action_reset_password()
        return True

    @api.multi
    def create_interpreter_login_all(self):
        '''Function to Create user login for all active interpreters who have email to be used as Login'''
        count = 0
        part_obj = self.env['res.partner']
        interpreter_ids = part_obj.search(
            [('cust_type', 'in', ('interpreter', 'interp_and_transl')), ('is_interpretation_active', '=', True),
             ('email', '!=', ''),
             ('company_id', 'in', (6, 4)), ('has_login', '=', False)])
        for interpreter_id in interpreter_ids:
            count += 1
            try:
                interpreter_id.create_interpreter_login()
            except Exception:
                pass
            if count % 500 == 0:
                self._cr.commit()
        return True

    @api.multi
    def create_interpreter_login(self):
        '''Function to create interpreter Login, with their groups auto assigned and login as email id and pass as  '''
        login, company, user_ids_asit, user_ids_sd = '', False, [], []
        user = self.env['res.users']
        dataobj = self.env['ir.model.data']
        for partner in self:
            #            if partner.company_id.id != current_user.company_id.id:
            #                raise osv.except_osv(_('Warning !'), _('Cannot Create Login for user of another Company.'))
            if not partner.email:
                raise UserError(_('Please enter Email Id1 to be used as login for the interpreter.'))
            user_ids = user.search([('login', '=', partner.email.strip().lower())])
            if user_ids:
                for user_id in user_ids:
                    # Getting the company for which user is created
                    company = user_id.company_id.name or ''
                if partner.company_id.name == 'ASIT':
                    login = 'asit_' + str(partner.email.strip())
                if company == 'IUG-SD' and partner.company_id.name == 'IUG-SD':
                    raise UserError(
                        _('There are users with the same Email Id for this company, Please use another Email Id.'))
                elif company == 'IUG-SD' and partner.company_id.name == 'ASIT':
                    login = 'asit_' + str(partner.email.strip())
                if company == 'ASIT' and partner.company_id.name == 'ASIT':
                    raise UserError(
                        _('There are users with the same Email Id for this company, Please use another Email Id.'))
                elif company == 'ASIT' and partner.company_id.name == 'IUG-SD':
                    login = 'sd_' + str(partner.email.strip())
                if company == 'ACD' and partner.company_id.name == 'ACD':
                    raise UserError(
                        _('There are users with the same Email Id for this company, Please use another Email Id.'))
                elif company == 'IUG-SD' and partner.company_id.name == 'ACD':
                    login = 'acd_' + str(partner.email.strip())
                elif company == 'ACD' and partner.company_id.name == 'IUG-SD':
                    login = 'sd_' + str(partner.email.strip())
                elif company == 'ASIT' and partner.company_id.name == 'ACD':
                    login = 'acd_' + str(partner.email.strip())
            else:
                login = str(partner.email.strip())
            if not login:
                login = str(partner.email.strip())
            self.sudo().validate_email(partner.email)
            group_ids = []
            try:
                dummy, group_id = dataobj.sudo().get_object_reference('bista_iugroup', 'group_iu_portal')
                group_ids.append(group_id)
            except ValueError:
                pass
            menu_id = False
            #try:
            #    model, menu_id = dataobj.get_object_reference('base', 'action_menu_admin')
            #    if model != 'ir.actions.act_window':
            #        menu_id = False
            #except ValueError:
            #    pass
            user_name = ''
            if partner.name:
                user_name = partner.name.strip() or ''
            if partner.last_name:
                user_name += ' ' + partner.last_name.strip()
            logger.info('in step 3')
            vals = {
                'login': login.lower(),
                'password': 'iux@pass',
                'state': 'active',
                'user_type': 'vendor',
                'require_to_reset': True,
                'groups_id': [(6, 0, group_ids)],
                'company_ids': [(6, 0, [partner.company_id.id])],
                'company_id': partner.company_id and partner.company_id.id or False,
              #  'action_id': menu_id,
                'partner_id': partner.id
            }
            user_id = user.sudo().create(vals)
            time_zone = self.sudo().get_timezone_for_partner()
            partner.sudo().write({'user_id': user_id.id, 'has_login': True, 'tz': time_zone})
            self = self.with_context(create_user=True)
            user_id.sudo().action_reset_password()
            subject = ('''New User has been created - %s''') % (user_name)
            details = ('''User has been created . Login Id is -- "%s" ''') % (login)
            partner.message_post(body=details, subject=subject)
        return True

    @api.multi
    def create_transporter_login(self):
        '''Function to create transporter Login, with their groups auto assigned and login as email id and pass as  '''
        user = self.env['res.users']
        dataobj = self.env['ir.model.data']
        for partner in self:
            if not partner.email:
                raise UserError(_('Please enter Email Id1 to be used as login for the Transporter.'))
            user_ids = user.search([('login', '=', partner.email.strip())])
            if user_ids:
                raise UserError(_('There are users with the same Email Id, Please use another Email Id.'))
            self.sudo().validate_email(partner.email)
            group_ids = []
            try:
                dummy, group_id = dataobj.sudo().get_object_reference('bista_iugroup', 'group_iu_portal_transporter')
                group_ids.append(group_id)
            except ValueError:
                pass
            menu_id = False
            try:
                model, menu_id = dataobj.get_object_reference('base', 'action_menu_admin')
                if model != 'ir.actions.act_window':
                    menu_id = False
            except ValueError:
                pass
            user_name = ''
            if partner.name:
                user_name = partner.name.strip() or ''
            if partner.last_name:
                user_name += ' ' + partner.last_name.strip()
            vals = {
                'login': partner.email.strip(),
                'password': 'iux@pass',
                'state': 'active',
                'user_type': 'transporter',
                'require_to_reset': True,
                'groups_id': [(6, 0, group_ids)],
                'company_ids': [(6, 0, [partner.company_id.id])],
                'company_id': partner.company_id and partner.company_id.id or False,
                'action_id': menu_id,
                'partner_id': self.ids[0]
            }
            user_id = user.sudo().create(vals)
            time_zone = self.sudo().get_timezone_for_partner()
            partner.sudo().write({'user_id': user_id.id, 'has_login': True, 'tz': time_zone})
            self = self.with_context(create_user=True)
            user_id.sudo().action_reset_password()
            subject = ('''New User has been created - %s''') % (user_name)
            details = ('''User has been created . Login Id is -- "%s" ''') % (partner.email.strip())
            partner.message_post(body=details, subject=subject)
        return True

    @api.model
    def create_contact_login_asit(self):
        '''Function to Create user login for all active contacts who have email to be used as Login'''
        count = 0
        part_obj = self.pool.get('res.partner')
        self = self.with_context(cust_type='contact')

        self._cr.execute('''select res_partner.id from res_partner where res_partner.active is True and res_partner.company_id = 4 and res_partner.cust_type = 'contact' \
                and res_partner.id in (select contact.id from res_partner contact inner join res_partner customer on (contact.parent_id =  customer.id) where \
                customer.active is True and customer.company_id = 4 and customer.mental_prog is null and contact.email != '' and customer.cust_type = 'customer' \
                and contact.parent_id is not null)''')
        contact_ids = map(lambda x: x[0], self._cr.fetchall())
        print "contact_ids.........", len(contact_ids)
        for contact_id in self.browse(contact_ids):
            count += 1
            try:
                contact_id.create_customer_login()
            except Exception:
                pass
            if count % 100 == 0:
                print "count .......", count
                self._cr.commit()
        return True

    @api.multi
    def create_customer_login_asit(self):
        '''Function to create Customer Login, with their groups auto assigned and login as email id and pass as "iux@pass"  '''
        user = self.env['res.users']
        dataobj = self.env['ir.model.data']
        company_ids = []
        if not self._context.get('cust_type', False):
            return True
        for partner in self:
            if not partner.company_id:
                raise UserError(_('Please select company for this customer!'))
            if self._context.get('cust_type') == 'contact':
                if not partner.parent_id:
                    raise UserError(_('No Related Customer found for this contact, Please select Customer first!'))
            if not partner.email:
                raise UserError(_('Please enter Email Id to be used as login for the Customer.'))
            if partner.has_login and partner.user_id:
                partner.user_id.sudo().action_reset_password()
                continue
            user_ids = user.search([('login', '=', partner.email.strip().lower())])
            if user_ids:
                raise UserError(_('There are users with the same Email Id, Please use another Email Id.'))
            self.sudo().validate_email(partner.email)
            group_ids = []
            try:
                dummy, group_id = dataobj.sudo().get_object_reference('bista_iugroup', 'group_iu_customer')
                group_ids.append(group_id)
            except ValueError:
                pass
            menu_id = False
            try:
                model, menu_id = dataobj.get_object_reference('base', 'action_menu_admin')
                if model != 'ir.actions.act_window':
                    menu_id = False
            except ValueError:
                pass
            #        Workaround for Scheduler access rights error for customer portal for IUG-SD and ASIT
            if 'IUG-SD' in partner.company_id.name.upper() or 'ASIT' in partner.company_id.name.upper():
                company_ids = self.env['res.company'].search(
                    ['|', ('name', 'ilike', 'IUG-SD'), ('name', 'ilike', 'ASIT')]).ids
            company_ids.append(partner.company_id.id)
            company_ids = list(set(flatten(company_ids)))
            vals = {
                'login': 'asit_' + str(partner.email).strip().lower(),
                'password': 'iux@pass',
                'state': 'active',
                'user_type': self._context.get('cust_type'),
                'require_to_reset': True,
                'groups_id': [(6, 0, group_ids)],
                'company_ids': [(6, 0, company_ids)],
                'company_id': partner.company_id and partner.company_id.id or False,
                'action_id': menu_id,
                'partner_id': self.ids[0]
            }
            user_id = user.sudo().create(vals)
            time_zone = self.sudo().get_timezone_for_partner()
            partner.sudo().write({'user_id': user_id.id, 'has_login': True, 'tz': time_zone})
            self = self.with_context(create_user=True)
            user_id.sudo().action_reset_password()
            subject = ('''New User has been created - %s''') % (partner.name)
            details = ('''User has been created . Login Id is -- "%s" ''') % (partner.email.strip())
            partner.message_post(body=details, subject=subject)
        return True

    @api.multi
    def create_contact_login_all(self):
        '''Function to Create user login for all active contacts who have email to be used as Login'''
        count = 0
        part_obj = self.env['res.partner']
        self = self.with_context(cust_type='contact')
        #        contact_ids = part_obj.search(cr, uid, [('cust_type','=','contact'),('active','=',True),('company_id','in',(6,4)),('mental_prog','=',False)])
        print "context.get('has_login',False).........", self._context.get('has_login', False)
        if not self._context.get('has_login', False):
            self._cr.execute('''select res_partner.id from res_partner where res_partner.has_login is not True and res_partner.active is True and res_partner.company_id in (6,4) and res_partner.cust_type = 'contact' \
                and res_partner.id in (select contact.id from res_partner contact inner join res_partner customer on (contact.parent_id =  customer.id) where \
                customer.active is True and customer.company_id in (6,4) and customer.mental_prog is null and contact.email != '' and customer.cust_type = 'customer' \
                and contact.parent_id is not null)''')
        else:
            self._cr.execute('''select res_partner.id from res_partner where res_partner.active is True and res_partner.company_id = 6 and res_partner.cust_type = 'contact' \
                and res_partner.id in (select contact.id from res_partner contact inner join res_partner customer on (contact.parent_id =  customer.id) where \
                customer.active is True and customer.company_id = 6 and customer.mental_prog is null and contact.email != '' and customer.cust_type = 'customer' \
                and contact.parent_id is not null)''')
        contact_ids = map(lambda x: x[0], self._cr.fetchall())
        print "contact_ids.........", len(contact_ids)
        for contact_id in contact_ids:
            count += 1
            try:
                contact_id.create_customer_login()
            except Exception:
                pass
            if count % 100 == 0:
                print "count .......", count
                self._cr.commit()
        return True

    @api.multi
    def create_customer_login(self):
        '''Function to create Customer Login, with their groups auto assigned and login as email id and pass as "iux@pass"  '''
        user = self.env['res.users']
        dataobj = self.env['ir.model.data']
        company_ids = []
        if not self._context.get('cust_type', False):
            return True
        for partner in self:
            if not partner.company_id:
                raise UserError(_('Please select company for this customer!'))
            if self._context.get('cust_type') == 'contact':
                if not partner.parent_id:
                    raise UserError(_('No Related Customer found for this contact, Please select Customer first!'))
            if not partner.email:
                raise UserError(_('Please enter Email Id to be used as login for the Customer.'))
            try:
                if partner.has_login and partner.user_id:
                    partner.user_id.sudo().action_reset_password()
                    continue
            except:
                pass
            user_ids = user.search([('login', '=', partner.email.strip().lower())])
            if user_ids:
                raise UserError(_('There are users with the same Email Id, Please use another Email Id.'))
            self.sudo().validate_email(partner.email)
            group_ids = []
            try:
                dummy, group_id = dataobj.sudo().get_object_reference('bista_iugroup', 'group_iu_customer')
                group_ids.append(group_id)
            except ValueError:
                pass
            menu_id = False
            try:
                model, menu_id = dataobj.get_object_reference('base', 'action_menu_admin')
                if model != 'ir.actions.act_window':
                    menu_id = False
            except ValueError:
                pass
            user_name = ''
            if partner.name:
                user_name = partner.name.strip() or ''
            if partner.last_name:
                user_name += ' ' + partner.last_name.strip()
            #        Workaround for Scheduler access rights error for customer portal for IUG-SD and ASIT
            if 'IUG-SD' in partner.company_id.name.upper() or 'ASIT' in partner.company_id.name.upper():
                company_ids = self.env['res.company'].search(
                    ['|', ('name', 'ilike', 'IUG-SD'), ('name', 'ilike', 'ASIT')]).ids
            company_ids.append(partner.company_id.id)
            company_ids = list(set(flatten(company_ids)))
            vals = {
                'login': partner.email.strip().lower(),
                'password': 'iux@pass',
                'state': 'active',
                'user_type': self._context.get('cust_type'),
                'require_to_reset': True,
                'groups_id': [(6, 0, group_ids)],
                'company_ids': [(6, 0, company_ids)],
                'company_id': partner.company_id and partner.company_id.id or False,
                'action_id': menu_id,
                'partner_id': self.ids[0]
            }
            user_id = user.sudo().create(vals)
            time_zone = self.sudo().get_timezone_for_partner()
            partner.sudo().write({'user_id': user_id.id, 'has_login': True, 'tz': time_zone})
            self = self.with_context(create_user=True)
            try:
                user_id.sudo().action_reset_password()
            except Exception:
                pass
            subject = ('''New User has been created - %s''') % (user_name)
            details = ('''User has been created . Login Id is -- "%s" ''') % (partner.email.strip())
            partner.message_post(body=details, subject=subject)
        return True

    @api.multi
    def unlink(self):
        '''Function overridden to restrict Deletion of Partners '''
        raise UserError(_('You are not allowed to delete this record.Alternatively you can mark it as inactive.'))
        # return super(res_partner, self).unlink()

    @api.multi
    def create_event(self):
        ''' Function to create Event from the partner Form only '''
        event_obj = self.env['event']
        event_data = {
            'partner_id': self.ids[0],
            'ordering_partner_id': self.ids[0],
            'event_type': 'language',
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
            'context': {"search_default_event_type": 'language', "search_event_type": 'language',
                        "default_event_type": 'language'}
        }

    @api.multi
    def view_past_appointments_contact(self):
        ''' This function returns an action that display past Appointments corresponding to the Contact. '''
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']
        result = mod_obj.get_object_reference('bista_iugroup', 'action_event_all_type')  # view_order_tree
        id = result and result[1] or False
        result = act_obj.browse(id).read()[0]
        user = self.env.user
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.utc
        local_date = tz.localize(datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), DATETIME_FORMAT),
                                 is_dst=None)
        local_date = datetime.strptime(local_date.astimezone(tz).strftime(DATETIME_FORMAT), DATETIME_FORMAT).strftime(
            '%Y-%m-%d')
        history_ids = []
        for part in self:
            history_ids = self.env['event'].search(
                ['|', ('contact_id', '=', part.id), ('ordering_contact_id', '=', part.id), \
                 ('event_start_date', '<', local_date)]).ids
        if not history_ids:
            raise UserError(_('No Past Appointments for this Contact.'))
        result['domain'] = "[('id','in',[" + ','.join(map(str, history_ids)) + "])]"
        return result

    @api.multi
    def view_today_events_for_contact(self):
        ''' This function returns an action that display Todays events created for this Contact. '''
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']
        result = mod_obj.get_object_reference('bista_iugroup',
                                              'action_event_all_type')  # view_quotation_tree,view_order_tree
        id = result and result[1] or False
        result = act_obj.browse(id).read()[0]
        user = self.env.user
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.utc
        local_date = tz.localize(datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), DATETIME_FORMAT),
                                 is_dst=None)
        local_date = datetime.strptime(local_date.astimezone(tz).strftime(DATETIME_FORMAT), DATETIME_FORMAT).strftime(
            '%Y-%m-%d')
        history_ids = []
        for part in self:
            history_ids = self.env['event'].search(
                ['|', ('contact_id', '=', part.id), ('ordering_contact_id', '=', part.id), \
                 ('event_start_date', '=', local_date)]).ids
        if not history_ids:
            raise UserError(_('No Today Appointments for this Contact.'))
        result['domain'] = "[('id','in',[" + ','.join(map(str, history_ids)) + "])]"
        return result

    @api.multi
    def view_future_events_for_contact(self):
        ''' This function returns an action that display Future events created for this Contact. '''
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']
        result = mod_obj.get_object_reference('bista_iugroup',
                                              'action_event_all_type')  # view_quotation_tree,view_order_tree
        id = result and result[1] or False
        result = act_obj.browse(id).read()[0]
        user = self.env.user
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.utc
        local_date = tz.localize(datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), DATETIME_FORMAT),
                                 is_dst=None)
        local_date = datetime.strptime(local_date.astimezone(tz).strftime(DATETIME_FORMAT), DATETIME_FORMAT).strftime(
            '%Y-%m-%d')
        history_ids = []
        for part in self:
            history_ids = self.env['event'].search(
                ['|', ('contact_id', '=', part.id), ('ordering_contact_id', '=', part.id), \
                 ('event_start_date', '>', local_date)]).ids
        if not history_ids:
            raise UserError(_('No Future Appointments for this Contact.'))
        result['domain'] = "[('id','in',[" + ','.join(map(str, history_ids)) + "])]"
        return result

    @api.multi
    def view_past_appointments_customer(self):
        ''' This function returns an action that display past Appointments corresponding to the Customer. '''
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']
        result = mod_obj.get_object_reference('bista_iugroup', 'action_event_all_type')  # view_order_tree
        id = result and result[1] or False
        result = act_obj.browse(id).read()[0]
        user = self.env.user
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.utc
        local_date = tz.localize(datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), DATETIME_FORMAT),
                                 is_dst=None)
        local_date = datetime.strptime(local_date.astimezone(tz).strftime(DATETIME_FORMAT), DATETIME_FORMAT).strftime(
            '%Y-%m-%d')
        history_ids = []
        for part in self:
            history_ids = self.env['event'].search(
                ['|', ('partner_id', '=', part.id), ('ordering_partner_id', '=', part.id), \
                 ('event_start_date', '<', local_date)]).ids
        if not history_ids:
            raise UserError(_('No Past Appointments for this Customer.'))
        result['domain'] = "[('id','in',[" + ','.join(map(str, history_ids)) + "])]"
        return result

    @api.multi
    def view_today_events_for_customer(self):
        ''' This function returns an action that display Todays events created for this customer. '''
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']
        result = mod_obj.get_object_reference('bista_iugroup', 'action_event_all_type')
        id = result and result[1] or False
        result = act_obj.browse(id).read()[0]
        user = self.env.user
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.utc
        local_date = tz.localize(datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), DATETIME_FORMAT),
                                 is_dst=None)
        local_date = datetime.strptime(local_date.astimezone(tz).strftime(DATETIME_FORMAT), DATETIME_FORMAT).strftime(
            '%Y-%m-%d')
        history_ids = []
        for part in self:
            history_ids = self.env['event'].search(
                ['|', ('partner_id', '=', part.id), ('ordering_partner_id', '=', part.id), \
                 ('event_start_date', '=', local_date)]).ids
        if not history_ids:
            raise UserError(_('No Todays Appointments for this Customer.'))
        result['domain'] = "[('id','in',[" + ','.join(map(str, history_ids)) + "])]"
        return result

    @api.multi
    def view_future_events_for_customer(self):
        ''' This function returns an action that display Future events created for this customer. '''
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']
        result = mod_obj.get_object_reference('bista_iugroup',
                                              'action_event_all_type')  # view_quotation_tree,view_order_tree
        id = result and result[1] or False
        result = act_obj.browse(id).read()[0]
        user = self.env.user
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.utc
        local_date = tz.localize(datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), DATETIME_FORMAT),
                                 is_dst=None)
        local_date = datetime.strptime(local_date.astimezone(tz).strftime(DATETIME_FORMAT), DATETIME_FORMAT).strftime(
            '%Y-%m-%d')
        history_ids = []
        for part in self:
            history_ids = self.env['event'].search(
                ['|', ('partner_id', '=', part.id), ('ordering_partner_id', '=', part.id), \
                 ('event_start_date', '>', local_date)]).ids
        if not history_ids:
            raise UserError(_('No Future Appointments for this Customer.'))
        result['domain'] = "[('id','in',[" + ','.join(map(str, history_ids)) + "])]"
        return result

    @api.multi
    def view_past_appointments(self):
        ''' This function returns an action that display past Appointments corresponding to the interpreter. '''
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']
        result = mod_obj.get_object_reference('bista_iugroup', 'action_event_all_type')  # view_order_tree
        id = result and result[1] or False
        result = act_obj.browse(id).read()[0]
        user = self.env.user
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.utc
        local_date = tz.localize(datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), DATETIME_FORMAT),
                                 is_dst=None)
        local_date = datetime.strptime(local_date.astimezone(tz).strftime(DATETIME_FORMAT), DATETIME_FORMAT).strftime(
            '%Y-%m-%d')
        # compute the number of Sales to display
        history_ids = []
        for part in self:
            history_ids = self.env['event'].search([('assigned_interpreters', '=', part.id), \
                                                    ('event_start_date', '<', local_date)]).ids
        if not history_ids:
            raise UserError(_('No Past Appointments for this Interpreter.'))
        result['domain'] = "[('id','in',[" + ','.join(map(str, history_ids)) + "])]"
        return result

    @api.multi
    def view_todays_appointments(self):
        ''' This function returns an action that display todays Appointments corresponding to the interpreter. '''
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']
        result = mod_obj.get_object_reference('bista_iugroup',
                                              'action_event_all_type')  # view_quotation_tree,view_order_tree
        id = result and result[1] or False
        result = act_obj.browse(id).read()[0]
        user = self.env.user
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.utc
        local_date = tz.localize(datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), DATETIME_FORMAT),
                                 is_dst=None)
        local_date = datetime.strptime(local_date.astimezone(tz).strftime(DATETIME_FORMAT), DATETIME_FORMAT).strftime(
            '%Y-%m-%d')
        history_ids = []
        for part in self:
            history_ids = self.env['event'].search([('assigned_interpreters', '=', part.id), \
                                                    ('event_start_date', '=', local_date)]).ids
        if not history_ids:
            raise UserError(_('No Todays Appointments for this Interpreter.'))
        result['domain'] = "[('id','in',[" + ','.join(map(str, history_ids)) + "])]"
        return result

    @api.multi
    def view_future_appointments(self):
        ''' This function returns an action that display future Appointments corresponding to the interpreter. '''
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']
        result = mod_obj.get_object_reference('bista_iugroup',
                                              'action_event_all_type')  # view_quotation_tree,view_order_tree
        id = result and result[1] or False
        result = act_obj.browse(id).read()[0]
        user = self.env.user
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.utc
        local_date = tz.localize(datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), DATETIME_FORMAT),
                                 is_dst=None)
        local_date = datetime.strptime(local_date.astimezone(tz).strftime(DATETIME_FORMAT), DATETIME_FORMAT).strftime(
            '%Y-%m-%d')
        history_ids = []
        for part in self:
            history_ids = self.env['event'].search([('assigned_interpreters', '=', part.id), \
                                                    ('event_start_date', '>', local_date)]).ids
        if not history_ids:
            raise UserError(_('No Future Appointments for this Interpreter.'))
        result['domain'] = "[('id','in',[" + ','.join(map(str, history_ids)) + "])]"
        return result

    @api.multi
    def view_past_appointments_transporter(self):
        ''' This function returns an action that display past Appointments corresponding to the Transporter. '''
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']
        result = mod_obj.get_object_reference('bista_iugroup', 'action_event_all_type')  # view_order_tree
        id = result and result[1] or False
        result = act_obj.browse(id).read()[0]
        user = self.env.user
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.utc
        local_date = tz.localize(datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), DATETIME_FORMAT),
                                 is_dst=None)
        local_date = datetime.strptime(local_date.astimezone(tz).strftime(DATETIME_FORMAT), DATETIME_FORMAT).strftime(
            '%Y-%m-%d')
        # compute the number of Sales to display
        history_ids = []
        for part in self:
            history_ids = self.env['event'].search([('transporter_id', '=', part.id), \
                                                    ('event_start_date', '<', local_date)]).ids
        if not history_ids:
            raise UserError(_('No Past Appointments for this Transporter.'))
        result['domain'] = "[('id','in',[" + ','.join(map(str, history_ids)) + "])]"
        return result

    @api.multi
    def view_today_appointments_transporter(self):
        ''' This function returns an action that display Todays Appointments corresponding to the Transporter. '''
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']
        result = mod_obj.get_object_reference('bista_iugroup',
                                              'action_event_all_type')  # view_quotation_tree,view_order_tree
        id = result and result[1] or False
        result = act_obj.browse(id).read()[0]
        user = self.env.user
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.utc
        local_date = tz.localize(datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), DATETIME_FORMAT),
                                 is_dst=None)
        local_date = datetime.strptime(local_date.astimezone(tz).strftime(DATETIME_FORMAT), DATETIME_FORMAT).strftime(
            '%Y-%m-%d')
        history_ids = []
        for part in self:
            history_ids = self.env['event'].search([('transporter_id', '=', part.id), \
                                                    ('event_start_date', '=', local_date)]).ids
        if not history_ids:
            raise UserError(_('No Todays Appointments for this Transporter.'))
        result['domain'] = "[('id','in',[" + ','.join(map(str, history_ids)) + "])]"
        return result

    @api.multi
    def view_future_appointments_transporter(self):
        ''' This function returns an action that display future Appointments corresponding to the Transporter. '''
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']
        result = mod_obj.get_object_reference('bista_iugroup',
                                              'action_event_all_type')  # view_quotation_tree,view_order_tree
        id = result and result[1] or False
        result = act_obj.browse(id).read()[0]
        user = self.env.user
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.utc
        local_date = tz.localize(datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), DATETIME_FORMAT),
                                 is_dst=None)
        local_date = datetime.strptime(local_date.astimezone(tz).strftime(DATETIME_FORMAT), DATETIME_FORMAT).strftime(
            '%Y-%m-%d')
        history_ids = []
        for part in self:
            history_ids = self.env['event'].search([('transporter_id', '=', part.id), \
                                                    ('event_start_date', '>', local_date)]).ids
        if not history_ids:
            raise UserError(_('No Future Appointments for this Transporter.'))
        result['domain'] = "[('id','in',[" + ','.join(map(str, history_ids)) + "])]"
        return result

    #     @api.model
    #     def customer_profile(self):
    #         numberstring,cust_profile_Id = '',''
    #         current_obj = self
    #         authorize_net_config = self.pool.get('authorize.net.config')
    #         act_model = 'res.partner'#context.get('active_model',False)
    #
    #         if current_obj:
    #             if not current_obj.auth_cc_number:
    #                 raise UserError(_('Please Enter firstly Credit Card Number to Validate!'))
    #             if not current_obj.auth_cc_expiration_date:
    #                 raise UserError(_('Please Enter Expiration Date in integer Format First!'))
    #             billing_address = current_obj.billing_addr
    #             shipping_address = current_obj.shipping_addr
    #             address_get = current_obj.address_get(['default','invoice','delivery'])
    #             billing_address = address_get.get('invoice',False) or address_get.get('contact',False)
    #             billing_address = self.browse(billing_address)
    #             shipping_address = address_get.get('delivery',False) or address_get.get('contact',False)
    #             shipping_address = self.browse( cr , uid ,shipping_address)
    # #            check_box = self.browse(cr,uid,ids[0]).customer_profile
    # ##            if check_box == True:
    # #                shipping_address = billing_address
    # #            if billing_address:
    # #                email = billing_address.email
    #             email = partner_id_obj.email
    #             ccn = current_obj.auth_cc_number
    #             exp_date = current_obj.auth_cc_expiration_date
    # #            exp_date = exp_date[:4] + '-' + exp_date[4:]
    #             exp_date = exp_date[-4:] + '-' + exp_date[:2]
    #             config_ids =authorize_net_config.search(cr,uid,[])
    #             if config_ids:
    #                 config_obj = authorize_net_config.browse(cr,uid,config_ids[0])
    #                 cust_profile_Id = partner_id_obj.customer_profile_id
    #                 if not cust_profile_Id:
    #                     response = authorize_net_config.call(cr,uid,config_obj,'CreateCustomerProfile',False,partner_id[0],billing_address,shipping_address,email,ccn,exp_date)
    #                     cust_profile_Id = response.get('customerProfileId',False)
    #                     cust_payment_profile_Id = response.get('customerPaymentProfileIdList',False)
    #                     numberstring = cust_payment_profile_Id.get('numericString',False)
    #                 else:
    #                     if cust_profile_Id:
    #                         response = authorize_net_config.call(cr,uid,config_obj,'CreateCustomerPaymentProfile',False,partner_id[0],billing_address,shipping_address,cust_profile_Id,ccn,exp_date,act_model)
    #                         numberstring = response.get('customerPaymentProfileId',False)
    #                 if response:
    #                     if numberstring:
    #                         payment_profile = {ccn[-4:]: numberstring}
    #                         self.pool.get('res.partner').cust_profile_payment(cr,uid,partner_id[0],cust_profile_Id,payment_profile,context)
    #             else:
    #                 raise osv.except_osv('Define Authorize.Net Configuration!', 'Warning:Define Authorize.Net Configuration!')
    #         return True

    @api.onchange('customer_basis')
    def onchange_customer_basis(self):
        ''' Empty Scheduler if Customer Basis Scheduler option is unchecked '''
        val = {}
        if not self.customer_basis:
            val = {
                'scheduler_id': False,
            }
        return {'value': val}

    @api.onchange('email','email2')
    def onchange_validate_email(self):
        '''Function to validate email and email2 on onchange event'''
        res, res['value'], res['warning'] = {}, {}, {}
        if self.email:
            if not re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,10}|[0-9]{1,3})(\\]?)$", self.email):
                warning = {
                    'title': _('Invalid Email'),
                    'message': _('Please enter a valid email address')
                }
                res['warning'] = warning
                res['value']['email'] = ''
        if self.email2:
            if not re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,10}|[0-9]{1,3})(\\]?)$", self.email2):
                warning = {
                    'title': _('Invalid Email2'),
                    'message': _('Please enter a valid email address')
                }
                res['warning'] = warning
                res['value']['email2'] = ''
        return res

    @api.onchange('zip')
    def onchange_zip(self):
        '''Function to auto Fill Zone '''
        res = {}
        res['value'], res['warning'] = {}, {}
        if self.zip:
            try:
                input = int(self.zip)
            except ValueError:
                warning = {
                    'title': _('Invalid Email2'),
                    'message': _('Please enter integer values only in zip !')
                }
                res['warning'] = warning
                res['value']['zip'] = ''
                return res
            zip = self.zip.strip()
            zip_ids = self.env['zip.code'].search([('name', '=', zip), ('company_id', '=', self.company_id.id)]).ids
            #            print "zip_ids........",zip_ids
            if zip_ids:
                self._cr.execute(
                    "select zone_id from zipcode_to_zone_rel where zip_code_id = %s" % (
                    zip_ids[0]))
                zone_ids = map(lambda x: x[0], self._cr.fetchall())
                print "zone_ids........", zone_ids
                if zone_ids:
                    return {'value': {'zone_id': zone_ids[0] or False}}
                else:
                    out_of_state_ids = []
                    if self.company_id:
                        out_of_state_ids = self.env['zone'].search(
                            [('name', '=', 'Out of state'), ('company_id', '=', self.company_id.id)]).ids
                    else:
                        out_of_state_ids = self.env['zone'].search([('name', '=', 'Out of state')]).ids
                    if out_of_state_ids:
                        return {'value': {'zone_id': out_of_state_ids and out_of_state_ids[0]}}
            else:
                out_of_state_ids = []
                if self.company_id:
                    out_of_state_ids = self.env['zone'].search(
                        [('name', '=', 'Out of state'), ('company_id', '=', self.company_id.id)]).ids
                else:
                    out_of_state_ids = self.env['zone'].search([('name', '=', 'Out of state')]).ids
                if out_of_state_ids:
                    return {'value': {'zone_id': out_of_state_ids and out_of_state_ids[0]}}
        return {'value': {'zone_id': False}}

    @api.onchange('zone_id')
    def onchange_zone_id(self):
        if self.zone_id:
            zone = self.env['zone'].browse(self.zone_id.id)
            zone_id = zone.meta_zone_id and zone.meta_zone_id.id or False
            return {'value': {'meta_zone_id': zone_id or False}}
        return {'value': {'meta_zone_id': False}}

    @api.model
    def _generate_order_by(self, order_spec, query):
        '''correctly orders Partner field '''
        order_by = super(res_partner, self)._generate_order_by(order_spec, query)
        if order_by:
            temp = order_by.upper()
            count = temp.count('DESC')
            count2 = temp.count('ASC')
            if count >= 1 or count2 >= 1:
                return order_by
            else:
                order_by = str(order_by) + ' desc'
        return order_by

    @api.model
    def get_default_country(self):
        """Return the Default Country """
        proxy = self.env['ir.config_parameter']
        default_country = proxy.sudo().get_param('default_country')
        if not default_country:
            raise UserError(_('Please Default Country as US in config parameters.'))
        return default_country.strip()

    @api.onchange('phone', 'phone2', 'phone3', 'phone4')
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
        if self.phone3:
            try:
                pn = phonumbers_converter._parse(self.phone3, def_country)
                if pn:
                    new_phone = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.E164)
                else:
                    new_phone = None
            except phonenumbers.NumberParseException:
                phone3 = None
                pass
            result['value']['phone3'] = new_phone
        if self.phone4:
            try:
                pn = phonumbers_converter._parse(self.phone4, def_country)
                if pn:
                    new_phone = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.E164)
                else:
                    new_phone = None
            except phonenumbers.NumberParseException:
                phone4 = None
                pass
            result['value']['phone4'] = new_phone
        # print "result.......",result
        return result

    @api.onchange('billing_partner_id')
    def onchange_billing_partner_id(self):
        ''' bring contact info from customer '''
        if not self.billing_partner_id:
            return {'value': {}}
        part = self.billing_partner_id
        val = {}
        def_contact = False
        if part.child_ids:
            for contact in part.child_ids:
                def_contact = contact.id
                if contact.billing_contact:
                    def_contact = contact.id
                    break
        if def_contact:
            val.update({'billing_contact_id': def_contact})
        else:
            val.update({'billing_contact_id': False})
        return {'value': val}

    @api.multi
    def open_map_new(self):
        ''' Shows Partner on google maps '''
        partner = self
        url = "http://maps.google.com/maps?oi=map&q="
        if partner.street:
            url += partner.street.replace(' ', '+')
        if partner.city:
            url += '+' + partner.city.replace(' ', '+')
        if partner.state_id:
            url += '+' + partner.state_id.name.replace(' ', '+')
        if partner.country_id:
            url += '+' + partner.country_id.name.replace(' ', '+')
        if partner.zip:
            url += '+' + partner.zip.replace(' ', '+')
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'nodestroy': True,
            'target': 'new'
        }

    ################### Default Functions copied from res.partner ####################
    @api.multi
    def copy(self, default=None):
        partner_obj = self
        attachment_ids = self.env['ir.attachment'].search([('partner_id', '=', partner_obj.id)])
        ''' Function overridden to blank data for different type of duplication '''
        if default is None: default = {}
        default.update({
            'user_id': SUPERUSER_ID,
            'has_login': False,
            #            'company_id': False,
            #             'phone_type_id1': False,
            #             'phone_type_id2': False,
            #             'phone_type_id3': False,
            #             'phone_type_id4': False,
            'billing_partner_id': False,
            'billing_contact_id': False,
            'head_contact_id': False,
            'scheduler_id': False,
            'sales_representative_id': False,
            #             'rating_id': False,
            'meta_zone_id': False,
            #             'language_lines': [],
            'translator_software_ids': [],
            'trans_language_lines': [],
            'translator_affiliation_ids': [],
            'translator_assign_history': [],
            'interpreter_history2': [],
            'interpreter_alloc_history': [],
            'billing_rule_ids': [],
            'credit_card_lines': [],
            'interpreter_history': [],
            'transporter_history': [],
            'translator_history': [],
            'block_inter_ids': [],
            'interpreter_id': False,
            'dob': False,

        })
        partner_id = super(res_partner, self).copy(default)
        if partner_obj.cust_type == 'interpreter':
            partner_id.write({'name': partner_obj.name})
            if attachment_ids:
                for attach_ids in attachment_ids:
                    attach_ids.sudo().copy(default={'partner_id': partner_id.id, 'res_id': partner_id.id})
        else:
            return partner_id

    @api.model
    def name_create(self, name):
        """ +++++++ Overridden for the Case of Multicompany +++++++
        Override of orm's name_create method for partners. The purpose is
            to handle some basic formats to create partners using the
            name_create.
            If only an email address is received and that the regex cannot find
            a name, the name will have the email value.
            If 'force_email' key in context: must find the email address. """
        rec_id = False
        name, email = self._parse_partner_name(name)
        if self._context.get('force_email') and not email:
            raise UserError(_("Couldn't create contact without email address!"))
        if not name and email:
            name = email
        company_id = self._context.get('company_id', False)
        if company_id:
            rec_id = self.create({self._rec_name: name or email, 'email': email or False, 'company_id': company_id})
        else:
            rec_id = self.create({self._rec_name: name or email, 'email': email or False})
        return rec_id.name_get()[0]

    @api.model
    def find_or_create(self, email):
        """ ++++++ Overridden for the Case of Multicompany +++++++
            Find a partner with the given ``email`` or use :py:method:`~.name_create`
            to create one

            :param str email: email-like string, which should contain at least one email,
                e.g. ``"Raoul Grosbedon <r.g@grosbedon.fr>"``"""
        assert email, 'an email is required for find_or_create to work'
        ids = []
        emails = tools.email_split(email)
        if emails:
            email = emails[0]
        company_id = self._context.get('company_id', False)
        if company_id:
            ids = self.search([('email', 'ilike', email), ('company_id', '=', company_id)]).ids
        else:
            ids = self.search([('email', 'ilike', email)]).ids
        if not ids:
            return self.name_create(email)[0]
        return ids[0]

    @api.model
    def _address_fields(self):
        """ Returns the list of address fields that are synced from the parent
        when the `use_parent_address` flag is set. """
        return list(ADDRESS_FIELDS)

    @api.multi
    @api.depends('name', 'last_name', 'parent_id', 'email')
    def name_get(self):
        res = []
        for record in self:
            name = record.name
            #             if record.middle_name:
            #                 name = name + ' ' + (record.middle_name or '')
            if record.last_name:
                name = name + ' ' + (record.last_name or '')
            #            if record.ref:
            #                name = "[%s] %s" % (record.ref, name)
            #            print "name2.......",name
            if record.parent_id and not record.is_company:
                name = "%s, %s" % (name, record.parent_id.name)
            if self._context.get('show_address'):
                name = name + "\n" + self.sudo()._display_address(record, without_company=True)
                name = name.replace('\n\n', '\n')
                name = name.replace('\n\n', '\n')

            if self._context.get('show_email') and record.email:
                name = "%s <%s>" % (name, record.email)
            res.append((record.id, name))
        return res

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if not args: args = []
        result = []
        if name:
            ids = self.search([('complete_name', operator, name)] + args, limit=limit)
            if not ids:
                ids = self.search([('ref', operator, name)] + args, order='last_update_date desc', limit=limit)
            if not ids:
                ids = self.search([('name', operator, name)] + args, order='last_update_date desc', limit=limit)
            ##            if not ids:
            ##                ids = self.search(cr, user, [('middle_name',operator,name)]+ args,order='last_update_date desc' , limit=limit, context=context)
            #            if not ids:
            #                ids = self.search(cr, user, [('last_name',operator,name)]+ args, order='last_update_date desc',limit=limit, context=context)
            #            if not ids:
            #                ids = self.search(cr, user, [('zip',operator,name)]+ args, order='last_update_date desc', limit=limit, context=context)
            #            if not ids:
            #                ids = set()
            #                ids.update(self.search(cr, user, args + [('complete_name',operator,name)],order='last_update_date desc', limit=limit, context=context))
            #                ids.update(self.search(cr, user, args + [('name',operator,name)], order='last_update_date desc',limit=limit, context=context))
            #                ids.update(self.search(cr, user, args + [('last_name',operator,name)],order='last_update_date desc', limit=limit, context=context))
            ##                ids.update(self.search(cr, user, args + [('zip',operator,name)],order='last_update_date desc' , limit=limit, context=context))
            ##                if not limit or len(ids) < limit:
            ##                    # we may underrun the limit because of dupes in the results, that's fine
            ##                    ids.update(self.search(cr, user, args + [('name',operator,name)],order='last_update_date desc', limit=(limit and (limit-len(ids)) or False) , context=context))
            #                ids = list(ids)
            if not ids:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    ids = self.search([('complete_name', '=', res.group(2))] + args, limit=limit)
        else:
            ids = self.search([] + args, order='last_update_date', limit=limit)
        result = ids.name_get()
        return result

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

    #
    #     def change_number_format(self, cr, uid, ids, context):
    #         partner_obj=self.pool.get('res.partner')
    #         partner_srch=partner_obj.search(cr, uid, [])
    # #        partner_srch=partner_obj.search(cr, uid, [('cust_type', '=', 'customer')])
    #         for each in self.browse(cr, uid, partner_srch):
    # #            print "each----------", each, each.phone, each.phone2, each.phone3, each.phone4
    #             try:
    #                 if each.phone:
    #                     ph=each.phone
    #                     ph = ph.encode('utf-8', 'ignore')
    #                     try:
    #                         ph = unicode(ph, "ascii",'ignore')
    #                     except UnicodeError:
    #                         ph = unicode(ph, "utf-8", 'ignore').decode('ascii')
    #                     final_phone=''
    #                     count=0
    # #                    each.phone.encode('utf-8', 'ignore')
    # #                    chck_phone=str(each.phone)
    #                     chck_phone=ph.lstrip('+1')
    #                     for every in chck_phone:
    #                         if every.isdigit():
    #                             count +=1
    #                             final_phone+=every
    #         #            final_phone=final_phone.lstrip('1')
    #                     if count == 10 :
    #                         phone='+1-'+final_phone[-10:-7]+'-'+final_phone[-7:-4]+'-'+final_phone[-4:]
    # #                        print "phoneeee-------", phone
    #                         self.write(cr, uid, each.id, {'phone':phone})
    #
    #                 if each.phone2:
    #                     ph2=each.phone2
    #                     ph2 = ph2.encode('utf-8', 'ignore')
    #                     try:
    #                         ph2 = unicode(ph2, "ascii",'ignore')
    #                     except UnicodeError:
    #                         ph2 = unicode(ph2, "utf-8", 'ignore').decode('ascii')
    #                     final_phone2=''
    #                     count2=0
    # #                    print "each.phone1111----",each.phone2, type(each.phone2)
    # #                    each.phone2.encode('utf-8', 'ignore')
    # #                    print "each.phone222222----",each.phone2, type(each.phone2)
    # #                    chck_phone2=str(each.phone2)
    # #                    print "each.phone3333----",each.phone2, type(each.phone2)
    #                     chck_phone2=ph2.lstrip('+1')
    #                     for every2 in chck_phone2:
    #                         if every2.isdigit():
    #                             count2 +=1
    #                             final_phone2+=every2
    #         #            final_phone=final_phone.lstrip('1')
    #                     if count2 == 10 :
    #                         phone2='+1-'+final_phone2[-10:-7]+'-'+final_phone2[-7:-4]+'-'+final_phone2[-4:]
    # #                        print "phoneeee22-------", phone2
    #                         self.write(cr, uid, each.id, {'phone2':phone2})
    #
    #                 if each.phone3:
    #                     ph3=each.phone3
    #                     ph3 = ph3.encode('utf-8', 'ignore')
    #                     try:
    #                         ph3 = unicode(ph3, "ascii",'ignore')
    #                     except UnicodeError:
    #                         ph3 = unicode(ph3, "utf-8", 'ignore').decode('ascii')
    #                     final_phone3=''
    #                     count3=0
    # #                    each.phone3.encode('utf-8', 'ignore')
    # #                    chck_phone3=str(each.phone3)
    #                     chck_phone3=ph3.lstrip('+1')
    #                     for every3 in chck_phone3:
    #                         if every3.isdigit():
    #                             count3 +=1
    #                             final_phone3+=every3
    #         #            final_phone=final_phone.lstrip('1')
    #                     if count3 == 10 :
    #                         phone3='+1-'+final_phone3[-10:-7]+'-'+final_phone3[-7:-4]+'-'+final_phone3[-4:]
    #                         self.write(cr, uid, each.id, {'phone3':phone3})
    #
    #                 if each.phone4:
    #                     ph4=each.phone4
    #                     ph4 = ph4.encode('utf-8', 'ignore')
    #                     try:
    #                         ph4 = unicode(ph4, "ascii",'ignore')
    #                     except UnicodeError:
    #                         ph4 = unicode(ph4, "utf-8", 'ignore').decode('ascii')
    #                     final_phone4=''
    #                     count4=0
    # #                    each.phone4.encode('utf-8', 'ignore')
    # #                    chck_phone4=str(each.phone4)
    #                     chck_phone4=ph4.lstrip('+1')
    #                     for every4 in chck_phone4:
    #                         if every4.isdigit():
    #                             count4 +=1
    #                             final_phone4+=every4
    #         #            final_phone=final_phone.lstrip('1')
    #                     if count4 == 10 :
    #                         phone4='+1-'+final_phone4[-10:-7]+'-'+final_phone4[-7:-4]+'-'+final_phone4[-4:]
    #                         self.write(cr, uid, each.id, {'phone4':phone4})
    #             except Exception:
    #                 pass
    # #        print "in query format----------"
    #         cr.execute("select id from res_partner where phone like '%x%' or phone2 like '%x%' or phone3 like '%x%' or phone4 like '%x%'")
    #         partnr_ids=map(lambda x: x[0], cr.fetchall())
    # #        print "partner_ids---------", partnr_ids, len(partnr_ids)
    #         for rec in self.browse(cr, uid, partnr_ids):
    # #            print "rec------------", rec
    #             if rec.phone:
    # #                print "rec.phone------", rec.phone
    #                 ph5=rec.phone
    #                 ph5 = ph5.encode('utf-8', 'ignore')
    #                 try:
    #                     ph5 = unicode(ph5, "ascii",'ignore')
    #                 except UnicodeError:
    #                     ph5 = unicode(ph5, "utf-8", 'ignore').decode('ascii')
    # #                print "ph5-----------", ph5, type(ph5)
    #                 final_phone5=''
    #                 extension=''
    #                 count5=0
    #                 if 'x' in ph5:
    # #                    print 'xxxxxxxxxxxxx'
    #                     chck_phone5=ph5.lstrip('+1')
    #                     ext=chck_phone5.split('x')[1]
    #                     for x in ext:
    # #                        print "x in for---------", x
    #                         if x.isdigit():
    #                             extension += x
    # #                        print "extension---", extension
    #                     for dig in chck_phone5:
    # #                        print "dig-----", dig, chck_phone5
    #                         if dig.isdigit() and count5<10:                   #+1-301-658-8965 ext 256
    #                             count5 +=1
    #                             final_phone5+=dig
    # #                        print "final_phone5----", final_phone5
    # #                    bhbh
    # #                    if count5 == 10 :
    #                     phone5='+1-'+final_phone5[-10:-7]+'-'+final_phone5[-7:-4]+'-'+final_phone5[-4:]
    #                     phone5=phone5 + ' ext.' + extension
    # #                    print "phone5-----------", phone5
    #                     self.write(cr, uid, rec.id, {'phone':phone5})
    #         return True

    @api.multi
    def sync_interpreter(self):
        ''' Function to sync this Interpreter to Albors and Alnet '''
        partner_ids, region_ids = [], []
        partner_obj = self.env['res.partner']
        rate_obj = self.env['rate']
        lang_lines_obj = self.env['interpreter.language']
        config_obj = self.env['server.config']
        config_ids = config_obj.search([])
        if not config_ids:
            raise UserError(_('No Active server config found!'))
        config = config_ids[0]
        ip = config.host  # Host
        port = config.port  # Port
        username = config.username  # the userl
        pwd = config.password  # the password of the user
        dbname = config.dbname  # the db name
        sock_common = xmlrpclib.ServerProxy('http://' + ip + ':' + port + '/xmlrpc/common')
        d_uid = sock_common.login(dbname, username, pwd)
        sock = xmlrpclib.ServerProxy('http://' + ip + ':' + port + '/xmlrpc/object')
        for partner in self:
            dest_part_ids = sock.execute(dbname, self.env.uid, pwd, 'res.partner', 'search',
                                         [('sd_id', '=', partner.id)])
            if dest_part_ids:
                raise UserError(_('This Interpreter is already Synced!'))
            read_list = ['name', 'middle_name', 'last_name', 'lang', 'date_localization', 'is_agency', 'email',
                         'email2',
                         'street', 'street2', 'city', 'state_id', 'country_id', 'is_translation_active',
                         'is_interpretation_active',
                         'cust_type', 'wb_on_file', 'gender', 'short_name', 'phone', 'phone2', 'phone3', 'phone4',
                         'mobile', 'comment',
                         'billing_comment', 'ref', 'telephone_interpretation', 'is_company', 'gsa', 'credit_limit',
                         'is_geo',
                         'latitude', 'longitude', 'fax', 'fax2', 'date', 'quickbooks_id', 'last_update_date', 'sinid',
                         'bill_miles_after'
                         'rubrik', 'is_alert', 'suppress_email', 'website', 'vendor_id', 'vendor_id2', 'active', 'rate',
                         ]
            read_data = partner.read(read_list)[0]
            #            print "read_data..........",read_data
            read_data['tz'] = 'US/Eastern'
            read_data['sd_id'] = partner.id
            read_data['company_id'] = 3
            read_data['state_id'] = partner.state_id and partner.state_id.id or False
            read_data['country_id'] = partner.country_id and partner.country_id.id or False
            #            context['do_create_user'], context['is_sync'] = False, True
            partner_id = sock.execute(dbname, d_uid, pwd, 'res.partner', 'create', read_data)
            print "partner_id........", partner_id
            partner_ids.append(partner_id)
            if partner.state_id:
                region_ids = sock.execute(dbname, self.env.uid, pwd, 'region', 'search',
                                          [('name', '=', partner.state_id.name)])
            # For Syncing up of rates
            for rate in partner.rate_ids:
                rate_data = rate.read([])[0]
                rate_data['partner_id'] = partner_id
                rate_data['company_id'] = 3
                if region_ids:
                    rate_data['region_id'] = region_ids[0]
                #                print "rate_data........",rate_data
                rate_id = sock.execute(dbname, d_uid, pwd, 'rate', 'create', rate_data)
            #                print "rate_id......",rate_id
            # For Syncing up of languages
            for language_line in partner.language_lines:
                if language_line.name:
                    lang_ids = sock.execute(dbname, self.env.uid, pwd, 'language', 'search',
                                            [('name', '=', language_line.name.name.upper())])
                    #                    print "lang_ids.......",lang_ids
                    if lang_ids:
                        lang_data = language_line.read(['sort_order', 'certification_code'])[0]
                        lang_data['interpreter_id'] = partner_id
                        lang_data['company_id'] = 3
                        lang_data['name'] = lang_ids[0]
                        #                        print "lang_data..........",lang_data
                        lang_id = sock.execute(dbname, d_uid, pwd, 'interpreter.language', 'create', lang_data)
                        print "lang_id......", lang_id
            partner.write({'is_sync': True, 'albors_id': partner_id})
            print "partner_ids.......", partner_ids
        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'action_warn',  # action_info
        #     'name': _('Information'),
        #     'params': {
        #         'title': 'Information!',
        #         'text': _('Interpreter is Synced.'),
        #         'sticky': True
        #     }
        # }
        return self.env.user.notify_warning(
            message='Interpreter is Synced.', title='Information!', sticky=True,
            show_reload=False, foo="bar")


class res_partner_title(models.Model):
    _inherit="res.partner.title"

    company_id=fields.Many2one("res.company","Company Id",default=lambda self: self.env['res.company']._company_default_get('res.partner.title'))


class assign_translator_history(models.Model):
    _name='assign.translator.history'

    name=fields.Many2one("res.partner","Translator",required = True ,ondelete='cascade')
    partner_id=fields.Many2one("res.partner","Billing Contact",  required=True ,ondelete='cascade')
    patient_id=fields.Many2one(related='event_id.patient_id', string='Patient Name')
    event_date=fields.Date("Event Date")
    event_start_date=fields.Date(related='event_id.event_start_date', string='Event Start Date')
    event_id=fields.Many2one("event", "Event Id" )
    language_id=fields.Many2one(related='event_id.language_id',string='Language')
    state=fields.Selection([
            ('assign', 'Assigned'),
            ('removed', 'Removed'),
            ('cancel','Cancelled'),
            ],
            'Status', readonly=True, required=True,default='assign')
    event_start=fields.Datetime(related='event_id.event_start', string='Event Start')
    event_end=fields.Datetime(related='event_id.event_end', string='Event End')
    company_id=fields.Many2one(related='event_id.company_id', string="Event State" ,readonly=True,)
    schedule_translator_event_time=fields.Datetime('Schedule Event Time')


class interpreter_alloc_history(models.Model):
    '''Interpreter Alloc History , keeps record of interpreters allocated for Events'''
    _name = "interpreter.alloc.history"

    @api.depends('event_id','event_id.event_start_date')
    def _get_event_start_date(self):
        ''' Function to get Event Start date from event form '''
        for history in self:
            history.event_start_date = history.event_id and history.event_id.event_start_date or False

    @api.depends('event_id','event_id.event_start')
    def _get_event_start(self):
        ''' Function to get Event Start from event form '''
        for history in self:
            history.event_start = history.event_id and history.event_id.event_start or False

    @api.depends('event_id','event_id.event_end')
    def _get_event_end(self):
        ''' Function to get Event End from event form '''
        for history in self:
            history.event_end = history.event_id and history.event_id.event_end or False




    name=fields.Many2one("res.partner","Interpreter",required = True,index=True)
    partner_id=fields.Many2one(related='event_id.partner_id', string='Billing Customer')
    ordering_partner_id=fields.Many2one(related='event_id.ordering_partner_id', string='Ordering Customer')
    patient_id=fields.Many2one(related='event_id.patient_id', string='Patient Name' )
    city=fields.Char(related='name.city',string='City', size=50 ,store=True)
    rate=fields.Float(related='name.rate',string='Rate',store=True)
    event_date=fields.Date("Event Date")
    event_id=fields.Many2one("event", "Event Id")
    event_id1=fields.Many2one(related='task_id.event_id', type='many2one', string='Event',store=True)
    language_id=fields.Many2one(related='event_id.language_id',string='Language')
    task_id=fields.Many2one(related='event_id.task_id', string='Related Task')
    voicemail_msg=fields.Char("Voicemail Message" , size=128)
    state=fields.Selection([
          ('draft', 'Unscheduled'),
          ('allocated', 'Scheduled'),
          ('confirm', 'Confirmed'),
          ('cancel','Cancelled'),
          ],
          'Status', readonly=True, required=True,default='draft',index=True)
    event_start_date=fields.Date(compute=_get_event_start_date, string='Event Start Date',store=True,index=True)
    event_start=fields.Datetime(compute=_get_event_start, string='Event Start',store=True)
    event_end=fields.Datetime(compute=_get_event_end, string='Event End',store=True)
    company_id=fields.Many2one(related='event_id.company_id', string="Company", readonly=True)
    allocate_date=fields.Datetime("Interpreter Allocation Time")
    confirm_date=fields.Datetime("Interpreter Confirmation Time")
    cancel_date=fields.Datetime("Interpreter Cancellation Time")




class transporter_alloc_history(models.Model):
    '''Transporter Alloc History , keeps record of transporters allocated for customers'''
    _name = "transporter.alloc.history"

    name=fields.Many2one('res.partner',"Transporter", required=True )
    partner_id=fields.Many2one(related='event_id.partner_id', string='Billing Customer')
    ordering_partner_id=fields.Many2one(related='event_id.ordering_partner_id', string='Ordering Customer')
    patient_id=fields.Many2one(related='event_id.patient_id', string='Patient Name')
    city=fields.Char(related='name.city', string='City', size=54 ,store=True)
    rate=fields.Float(related='name.rate', type='float', string='Rate',store=True)
    event_date=fields.Date("Event Date")
    event_id=fields.Many2one("event", "Event Id" )
    language_id=fields.Many2one(related='event_id.language_id', string='Language', relation='language')
    task_id=fields.Many2one(related='event_id.task_id', string='Related Task')
    event_start_date= fields.Date(related='event_id.event_start_date', string='Event Start Date')
    voicemail_msg=fields.Char("Voicemail Message" , size=128)
    state=fields.Selection([
          ('draft', 'Unscheduled'),
          ('allocated', 'Scheduled'),
          ('confirm', 'Confirmed'),
          ('cancel','Cancelled'),
          ],
          'Status', readonly=True, required=True,default='draft')
    event_start=fields.Datetime(related='event_id.event_start', string='Event Start')
    event_end=fields.Datetime(related='event_id.event_end', string='Event End')
    company_id=fields.Many2one(related='event_id.company_id', string="Company",
       readonly=True,default=lambda self: self.env['res.company']._company_default_get('transporter.alloc.history'))
    allocate_date=fields.Datetime("Interpreter Allocation Time")
    confirm_date=fields.Datetime("Interpreter Confirmation Time")
    cancel_date=fields.Datetime("Interpreter Cancellation Time")


    @api.multi
    def reset_event(self):
        for history in self:
            history.write({'state':'draft',})
            if history.event_id:
                history.event_id.write({'state':'draft'})
        return True

class translator_alloc_history(models.Model):
    '''Translator Alloc History , keeps record of transporters allocated for customers'''
    _name = "translator.alloc.history"

    name=fields.Many2one('res.partner',"Translator", required=True )
    partner_id=fields.Many2one(related='event_id.partner_id', string='Billing Customer')
    ordering_partner_id=fields.Many2one(related='event_id.ordering_partner_id', string='Ordering Customer')
    rating=fields.Char('Rating' , size=30)
    certification=fields.Char('Certification' , size=64)
    patient_id=fields.Many2one(related='event_id.patient_id', string='Patient Name',store=True)
    city=fields.Char(related='name.city', string='City', size=54 ,store=True)
    rate=fields.Float(related='name.rate', string='Rate',store=True)
    event_date=fields.Date("Event Date")
    event_start_date=fields.Date(related='event_id.event_start_date', string='Event Start Date',store=True)
    event_id=fields.Many2one("event", "Event Id")
    language_id=fields.Many2one(related='event_id.language_id', string='Language')
    task_id=fields.Many2one(related='event_id.task_id', string='Related Task')
    voicemail_msg=fields.Char("Voicemail Message" , size=128)
    state=fields.Selection([
          ('draft', 'Unscheduled'),
          ('confirm', 'Confirmed'),
          ('allocated', 'Scheduled'),
          ('cancel','Cancelled'),
          ],
          'Status', readonly=True, required=True,default='draft')
    event_start=fields.Datetime(related='event_id.event_start', string='Event Start')
    event_end=fields.Datetime(related='event_id.event_end', string='Event End')
    company_id=fields.Many2one(related='event_id.company_id', string="Company" ,
                                readonly=True,default=lambda self: self.env['res.company']._company_default_get('translator.alloc.history'))
    allocate_date=fields.Datetime("Interpreter Allocation Time")
    confirm_date=fields.Datetime("Interpreter Confirmation Time")
    cancel_date=fields.Datetime("Interpreter Cancellation Time")


class interpreter_history(models.Model):
    '''Interpreter  History , keeps record of interpreters allocated for customers'''
    _name = "interpreter.history"
    _order='event_date'

    name=fields.Many2one("res.partner","Interpreter",)
    partner_id=fields.Many2one(related='event_id.partner_id', string='Billing Customer')
    event_date=fields.Date(related='event_id.event_start_date', string='Event Date', store=True)
    event_id=fields.Many2one("event", "Event Id")
    language_id=fields.Many2one(related='event_id.language_id', string='Language',store=True)
    task_id=fields.Many2one(related='event_id.task_id', string='Related Task',store=True)
    voicemail_msg=fields.Char("Voicemail Message" , size=128)
    event_start_time=fields.Datetime(related='event_id.event_start', string='Event Start Time', store=True)
    event_end_time=fields.Datetime(related='event_id.event_end', string='Event End Time', store=True)
    state=fields.Selection([
        ('draft', 'Unscheduled'),
        ('voicemailsent', 'Voicemail Sent'),
        ('scheduled', 'Scheduled'),
        ('allocated', 'Allocated'),
        ('confirmed', 'Confirmed'),
        ('unbilled', 'Unbilled'),
        ('cancel','Cancelled'),
        ('done', 'Done')],'Status', readonly=True, required=True,)
    company_id=fields.Many2one('res.company', 'Company', index=1,default=lambda self: self.env['res.company']._company_default_get('interpreter.history'))

    @api.multi
    def direct_to_event(self):
        ''' function to redirect over to the related Event'''
        event = self.event_id
        if event:
            mod_obj = self.env['ir.model.data']
            res = mod_obj.get_object_reference('bista_iugroup', 'view_event_form')
            res_id = res and res[1] or False
            return {
                'name': _('Events'),
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': [res_id[0]],
                'res_model': 'event',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'res_id': event and event.id or False,
            }
        else:
            return True

class transporter_history(models.Model):
    '''Transporter  History , keeps record of Transporter allocated for customers'''
    _name = "transporter.history"

    name=fields.Many2one("res.partner","Transporter",)
    event_id = fields.Many2one("event", "Event Id", )
    partner_id=fields.Many2one('res.partner',related='event_id.partner_id', string='Billing Customer')
    event_date=fields.Date(related='event_id.event_start_date', string='Event Date', store=True)
    language_id=fields.Many2one(related='event_id.language_id', string='Language',store=True)
    task_id=fields.Many2one(related='event_id.task_id', string='Related Task',store=True)
    voicemail_msg=fields.Char("Voicemail Message" , size=128)
    state=fields.Selection([
      ('draft', 'Unscheduled'),
      ('voicemailsent', 'Voicemail Sent'),
      ('scheduled', 'Scheduled'),
      ('allocated', 'Allocated'),
      ('confirmed', 'Confirmed'),
      ('unbilled', 'Unbilled'),
      ('cancel','Cancelled'),
      ('done', 'Done')],
      'Status', readonly=True, required=True,)
    company_id=fields.Many2one('res.company', 'Company', index=1,default=lambda self: self.env['res.company']._company_default_get('transporter.history'))

    @api.multi
    def direct_to_event(self):
        ''' function to redirect over to the related Event'''
        event = self.event_id
        if event:
            mod_obj = self.env['ir.model.data']
            res = mod_obj.get_object_reference('bista_iugroup', 'view_event_form')
            res_id = res and res[1] or False,
            #print "res_id.......",res_id
            return {
                'name': _('Events'),
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': [res_id[0]],
                'res_model': 'event',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'res_id': event and event.id or False,
            }
        else:
            return True



