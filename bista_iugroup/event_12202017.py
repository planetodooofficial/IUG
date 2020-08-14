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
import time
import datetime
from dateutil import relativedelta
import re
from openerp.tools import flatten
import urllib
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp.addons.bss_phonenumbers.bss_phonumbers_fields import bss_phonenumbers_converter as phonumbers_converter #@UnresolvedImport
import phonenumbers
import pytz
from pytz import timezone
from openerp import SUPERUSER_ID, tools
from google_maps_distance_duration.google_maps import GoogleMaps
import netsvc
from osv import fields, osv
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import pygmaps
import webbrowser
import urllib, random
import requests
import base64
import math
from lxml import etree
from math import radians, cos, sin, asin, sqrt
from openerp.addons.bista_iugroup.google_distance import google_maps_distance
import logging
import requests, json
_logger = logging.getLogger(__name__)
#import threading
#import custom_thread
#import openerp.pooler as pooler
#from psycopg2.extensions import ISOLATION_LEVEL_READ_COMMITTED
try:
    from pygeocoder import Geocoder
except Exception , e:
     raise osv.except_osv(_('Warning!'),_('Please install pygeocoder - pip install pygeocoder'))

api_count = 0
api_key = False
api_keys_dict = {'AIzaSyDN16TAIFWQGAS06tDflAA3BbjSnrcYm40': {'count':0 , 'active':False},
                    'AIzaSyD_EIqYodP161OcXIRhfd-949wPn8Yk8QY': {'count':0 , 'active':False},
                    'AIzaSyCLqA8mKoXAEYyGMUBbiO2JjSx_KSwvdI8': {'count':0 , 'active':False},
                    'AIzaSyDgYJl6EqQk3ou07TKcxXN2TAFzyAJTrzY': {'count':0 , 'active':False},
                    'AIzaSyATAqHzxn53tdnzHtneCIi03nSo3Wlq5O4': {'count':0 , 'active':False},
                    'AIzaSyBqv-QIdWOc9vcW3aGsANRmoDXAjHJEHCA': {'count':0 , 'active':False},
                    'AIzaSyAb7OP4Apz1i9cwoh4gdtaofomlnBgeuOg': {'count':0 , 'active':False},
                    'AIzaSyAB5jMpGmC0t3kodrwHeih4yJQ5w1oanxk': {'count':0 , 'active':False},
                    'AIzaSyAW8Nl1wKaiKqPTyiSBc0iyS7B4kxQQhgo': {'count':0 , 'active':False},
                    'AIzaSyDAH8KzjEQyij7kl4oGuaV53Yhio3CAs_Y': {'count':0 , 'active':False},
                    'AIzaSyB7r557VDCEG1YCTx1jkYr4r1k2uACsQqU': {'count':0 , 'active':False},}

current_date = False
EVENT_STATES = [
    ('draft', 'Unscheduled'),
    ('scheduled', 'Scheduled'),
    ('allocated', 'Allocated'),
    ('unauthorize','Unauthorize'),
    ('confirmed', 'Confirmed'),
    ('unbilled', 'Unbilled'),
    ('cancel','Cancelled'),
    ('done', 'Done'),
    ('unapproved', 'Unappoved'),
    ('rejected', 'Rejected'),
]
_timezone_event = { -11: 'US/Samoa', -10: 'US/Hawaii',
                    -9: 'US/Alaska', -8: 'US/Pacific',
                    -7: 'US/Mountain', -6: 'US/Central',
                    -5: 'US/Eastern'
                }
                        
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
    return tools.ustr(' '.join(filter(None, [street, ("%s %s" % (zip or '', city or '')).strip(),
                                              state, country])))

class select_interpreter_line(osv.osv):
    _name = 'select.interpreter.line'
    _order = 'distance,rate'
    _inherit = ['mail.thread']
    _columns = {
        'name': fields.related('interpreter_id', 'name', type='char', string='Name',store=True),
        'middle_name': fields.related('interpreter_id', 'middle_name', type='char', string='Middle Name',store=True),
        'last_name': fields.related('interpreter_id', 'last_name', type='char', string='Last Name',store=True),
        'zip': fields.related('interpreter_id', 'zip', type='char', string='Zip',store=True),
        'phone': fields.related('interpreter_id', 'cell_phone', type='char', string='Phone',store=True),
        'rate': fields.float('Rate'),
        'interpreter_id': fields.many2one("res.partner",'Interpreter', ),
        'preferred': fields.boolean("Preffered?"),
        'event_id': fields.many2one('event',"Event Id", ),
        'visited':fields.boolean("Visited"),
        'visited_date':fields.date("Visited Date"),
        'voicemail_msg': fields.char("Voicemail Message" , size=128),
        'duration' : fields.char("Duration" , size=42),
        'distance' : fields.float('Distance' , digits = (16,2)),
        'state': fields.selection([
            ('draft', 'Unscheduled'),
            ('voicemailsent', 'Voicemail Sent'),
            ('assigned', 'Assigned'),
            ('cancel','Cancelled'),
            ],
            'Status', readonly=True, required=True,),
        'parent_state': fields.related('event_id','state', type="char", store=True, string="Event State" ,selection=EVENT_STATES,
                 readonly=True,),
        'company_id': fields.related('event_id','company_id', type="many2one", relation="res.company", store=True, string="Company" ,
                 readonly=True,),
    }
    _defaults={
        'voicemail_msg':'',
        }
    
    def leave_voicemail(self , cr ,uid , ids , context= None):
        ''' This function updates or assigns interpreter in the event form '''
        cur_obj = self.browse(cr , uid, ids[0])
        ir_model_data = self.pool.get('ir.model.data')
        warning_obj = self.pool.get('warning')
	history_obj = self.pool.get('interpreter.alloc.history')
        event = cur_obj.event_id
        res, template_id, overlap = [], False, False
        if not cur_obj.interpreter_id:
            return
        if event.partner_id.fee_note == True and event.fee_note_test == False:
            raise osv.except_osv(_("Unauthorised Event"),_("Please attach Event Fee Note!"))
        if event.partner_id.order_note == True and event.order_note_test == False:
            raise osv.except_osv(_("Unauthorised Event"),_("Please attach SAF!"))
        for select_line in event.interpreter_ids2:
            if select_line.interpreter_id:
                if select_line.state == 'voicemailsent' and select_line.interpreter_id.id == cur_obj.interpreter_id.id :
                    raise osv.except_osv(_('Warning!'),_('Selected interpreter is already present in the Job offered list!'))
        if event.multi_type == '1':
            if (event.state not in ('unapproved','draft','scheduled')) and len(event.assigned_interpreters) >= 1:
                raise osv.except_osv(_('Warning!'),_('Interpreter is already assigned to this event.'))
        if event.multi_type == '2':
            if event.state not in ('unapproved','draft','scheduled') and len(event.assigned_interpreters) >= 2:
                raise osv.except_osv(_('Warning!'),_('Interpreters are already assigned to this event.'))
        
        if not cur_obj.interpreter_id.is_agency:
            history_ids2 = history_obj.search(cr , SUPERUSER_ID, [('name','=',cur_obj.interpreter_id.id),('state','in',('confirm','allocated')),('company_id','=',event.company_id.id),('cancel_date','=',False),
                                   ('event_date','=',(datetime.datetime.strptime(str(datetime.datetime.strptime(str(event.event_start),"%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')),"%Y-%m-%d %H:%M:%S")).strftime('%Y-%m-%d'))])
            for history_id in history_ids2:
                history_browse = history_obj.browse( cr , SUPERUSER_ID, history_id)
                if (event.event_start > history_browse.event_start and event.event_end < history_browse.event_end) :
                    overlap = True
                    
                elif (event.event_start > history_browse.event_start and event.event_start < history_browse.event_end) :
                    overlap = True
                elif (event.event_end > history_browse.event_start and event.event_end < history_browse.event_end) :
                    overlap = True
                elif (event.event_start == history_browse.event_start or event.event_end == history_browse.event_end) :
                    overlap = True
                elif (history_browse.event_start > event.event_start and history_browse.event_start < event.event_end) :
                    overlap = True
                elif (history_browse.event_end < event.event_end and history_browse.event_end > event.event_start) :
                    overlap = True
    #            elif (event.event_start == history_browse.event_end ):
    #                overlap = True
                if overlap:
                    raise osv.except_osv(_('Warning!'),_('This Interpreter is already appointed for another Event!'))

        if event.state == 'draft':
            res = self.pool.get('event').write(cr , uid, [event.id],{'state':'scheduled'})
        context.update({'job_offer':True})
        if self.browse(cr, uid, ids[0]).interpreter_id.opt_for_sms:
            self.send_sms_to_interpreters_job_offer(cr,uid,ids,context)
        event_start = datetime.datetime.strptime(event.event_start, tools.DEFAULT_SERVER_DATETIME_FORMAT)
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        from_dt = datetime.datetime.strptime(str(event_start), DATETIME_FORMAT)
        voicemail_msg = cur_obj.voicemail_msg
        voicemail_msg = "Voicemail Message left for " + str(cur_obj.interpreter_id.name) + "for Event " + str(event.name) + \
                        " on the date " + str(from_dt.strftime('%Y-%m-%d'))
        self.pool.get('interpreter.history').create(cr , uid, {'partner_id':event.partner_id and event.partner_id.id or False,
                    'name':cur_obj.interpreter_id and cur_obj.interpreter_id.id or False,'event_id':event.id,#'event_date': from_dt.strftime('%Y-%m-%d'),
                    'state':'voicemailsent' , 'voicemail_msg':voicemail_msg})
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'bista_iugroup', 'send_interpreter_job_offered_event')[1]
        except ValueError:
            template_id = False
        if template_id:
            context={'interpreter_id': cur_obj.interpreter_id}
            try:
                self.pool.get('email.template').send_mail( cr, uid, template_id, ids[0], True, context)
            except Exception:
                pass
        self.write(cr ,uid , ids, {'state':'voicemailsent'})
        if cur_obj.interpreter_id.user_id and cur_obj.interpreter_id.user_id != SUPERUSER_ID:
            if cur_obj.interpreter_id.user_id and event.state in ['draft', 'scheduled']:
                self.pool.get('event').write(cr , uid, [event.id] , {'event_follower_ids':[(4, cur_obj.interpreter_id.user_id.id)]})

        # Check interpreter for TIN field and state is California
        interpreter_id = self.browse(cr, uid, ids[0]).interpreter_id
        if interpreter_id.cust_type == 'interpreter':
            state_id = self.pool.get('res.country.state').search(cr, uid, [('name', 'ilike', 'California')])
            if not interpreter_id.vat and interpreter_id.state_id.id == state_id[0]:
                wiz_address_id = warning_obj.create(cr, uid, {
                    'title': 'Warning!',
                    'message': 'Mentioned Interpreter does not contain TIN No.(Interpreter\'s Form) filled, please have a look.',
                })
                res = ir_model_data.get_object_reference(cr, uid, 'bista_iugroup', 'warning_vat')
                res_id = res and res[1] or False
                return {'name': 'Warning',
                        'type': 'ir.actions.act_window',
                        'res_model': 'warning',
                        'res_id': wiz_address_id,
                        'view_id': [res_id],
                        'view_mode': 'form',
                        'view_type': 'form',
                        'target': 'new',
                        }
        return res

    def schedule_interpreter(self , cr ,uid , ids , context= None):
        ''' This function updates or assigns interpreter in the event form '''
        cur_obj = self.browse(cr , uid, ids[0])
        mod_obj = self.pool.get('ir.model.data')
        history_obj = self.pool.get('interpreter.alloc.history')
        event = cur_obj.event_id
        overlap = False
        if not cur_obj.interpreter_id:
            return
        if not cur_obj.interpreter_id.is_agency:
            history_ids2 = history_obj.search(cr , SUPERUSER_ID, [('name','=',cur_obj.interpreter_id.id),('state','in',('confirm','allocated')),('company_id','=',event.company_id.id),
                                   ('event_date','=',(datetime.datetime.strptime(str(datetime.datetime.strptime(str(event.event_start),"%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')),"%Y-%m-%d %H:%M:%S")).strftime('%Y-%m-%d'))])
            for history_id in history_ids2:
                history_browse = history_obj.browse( cr , SUPERUSER_ID, history_id)
                if (event.event_start > history_browse.event_start and event.event_end < history_browse.event_end) :
                    overlap = True
                elif (event.event_start > history_browse.event_start and event.event_start < history_browse.event_end) :
                    overlap = True
                elif (event.event_end > history_browse.event_start and event.event_end < history_browse.event_end) :
                    overlap = True
                elif (event.event_start == history_browse.event_start or event.event_end == history_browse.event_end) :
                    overlap = True
                elif (history_browse.event_start > event.event_start and history_browse.event_start < event.event_end) :
                    overlap = True
                elif (history_browse.event_end < event.event_end and history_browse.event_end > event.event_start) :
                    overlap = True
    #            elif (event.event_start == history_browse.event_end ):
    #                overlap = True
                if overlap:
                    raise osv.except_osv(_('Warning!'),_('This Interpreter is already appointed for another Event!'))
        res = mod_obj.get_object_reference(cr, uid, 'bista_iugroup', 'assign_interpreter_wizard_view1')
        res_id = res and res[1] or False,
        context.update({'active_ids':ids})
        assign_interpreter_form_id = self.pool.get('assign.interp.wizard').create(cr, uid,{}, context=context)
        return {
            'name': _('Assign Interpreter'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res_id[0]],
            'res_model': 'assign.interp.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'res_id': assign_interpreter_form_id or False,
        }
        
    def send_sms_to_interpreters_job_offer(self,cr,uid,ids,context={}):
        select_template_body = None
        get_template = None
        sms_template_obj = self.pool.get('sms.template.twilio')

        if context.get('job_offer',False):
            get_template = sms_template_obj.search(cr, uid, [('action_for','=','job_offer')])
        if context.get('assigned_interp',False):
            get_template = sms_template_obj.search(cr, uid, [('action_for','=','assigned_interp')])
        if context.get('assigned_customer',False):
            get_template = sms_template_obj.search(cr, uid, [('action_for','=','assigned_customer')])
        if context.get('event_cancel',False):
            get_template = sms_template_obj.search(cr, uid, [('action_for','=','event_cancel')])
        for template_ids in sms_template_obj.browse(cr,uid,get_template):
            select_template_body = template_ids.sms_text

        if context.get('job_offer',False):
            event_data = self.browse(cr,uid,ids[0]).event_id
            event_time_start = event_data.event_start_hr+':'+event_data.event_start_min+event_data.am_pm
            event_time_end = event_data.event_end_hr+':'+event_data.event_end_min+event_data.am_pm2
            get_contact = self.browse(cr , uid, ids[0]).interpreter_id.phone
            if get_contact:
                sms_vals = {
                            'sms_body': select_template_body%(event_data.name,event_data.event_start_date,
                                                              event_time_start,event_time_end,
                                                              event_data.location_id.state_id.name,event_data.location_id.city,
                                                              event_data.location_id.zip,event_data.name,event_data.name),
                            'sms_to': get_contact
                        }
                self.pool.get('twilio.sms.send').create(cr,uid,sms_vals)
            else:
                pass
        
    
    def update_interpreter(self, cr, uid, ids, context):
        ''' This function updates or assigns interpreter in the event form '''
        res= []
        cur_obj = self.browse(cr ,uid ,ids[0])
        event = cur_obj.event_id
        res = self.pool.get('event').write(cr ,uid , [event.id],{'interpreter_id':cur_obj.interpreter_id and cur_obj.interpreter_id.id or False,
                                                                'state':'allocated'})
        res = self.unlink(cr ,uid , ids)
        return res
    
    def cancel_appointment(self, cr, uid, ids, context=None):
        ''' function to cancel assignment for interpreter  '''
        if isinstance(ids, (int,long)): ids = [ids]
        if context is None: context = {}
        mod_obj = self.pool.get('ir.model.data')
        event_obj = self.pool.get('event')
        cur_obj = self.browse(cr , uid, ids[0])
        event = cur_obj.event_id
        lines_state = []
        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid)
        interp_hist_obj = self.pool.get('interpreter.history')
        interp_hist_id = interp_hist_obj.search(cr, uid, [('event_id', '=', event.id),('name', '=', cur_obj.interpreter_id.id), ('state','=', 'voicemailsent')])
        interp_hist_obj.write(cr, uid, interp_hist_id,{'state': 'cancel'})

        if not event.history_id:
            self.pool.get('interpreter.alloc.history').create(cr ,uid ,{'partner_id':event.partner_id and event.partner_id.id or False,'name': cur_obj.interpreter_id and cur_obj.interpreter_id.id or False,
                    'event_id':event.id,'event_date': event.event_date ,'event_start':event.event_start,'event_end':event.event_end,'state':'cancel','company_id': event.company_id and event.company_id.id or False,
                    'cancel_date':time.strftime('%Y-%m-%d %H:%M:%S')})
        else:
            for history in event.history_id:
                if history.name.id == cur_obj.interpreter_id.id and history.state == 'allocated':
                    self.pool.get('interpreter.alloc.history').write(cr ,uid ,history.id,{'partner_id':event.partner_id and event.partner_id.id or False,'name': cur_obj.interpreter_id and cur_obj.interpreter_id.id or False,
                            'event_id':event.id,'event_date': event.event_date ,'event_start':event.event_start,'event_end':event.event_end,'state':'cancel','company_id': event.company_id and event.company_id.id or False,
                            'cancel_date':time.strftime('%Y-%m-%d %H:%M:%S')})
        
        self.write(cr ,uid ,ids , {'state':'cancel'})
        event_obj.write(cr , SUPERUSER_ID, [event.id],{'event_follower_ids':[(3, cur_obj.interpreter_id.user_id.id)]})
        event_new = event_obj.browse(cr, SUPERUSER_ID, event.id)
        subject = "System Rejected Interpreter's Job offer"
        if cur_obj.interpreter_id and cur_obj.interpreter_id.user_id:
            if cur_obj.interpreter_id.has_login and cur_obj.interpreter_id.user_id.id == uid:
                subject = "Interpreter Declined"
        details = "Interpreter %s has declined job."%(cur_obj.interpreter_id and cur_obj.interpreter_id.complete_name or False)
        if user.user_type not in ('staff','admin'):
            event_obj.message_post(cr, SUPERUSER_ID, [event.id], body=details, subject=subject, context=context)
        else:
            event_obj.message_post(cr, uid, [event.id], body=details, subject=subject, context=context)
        if not event_new.assigned_interpreters:
            for each_line in event_new.interpreter_ids2:
                lines_state.append(each_line.state)
            if lines_state and len(list(set(lines_state))) == 1 and list(set(lines_state))[0] == 'cancel':
                event_obj.write(cr , SUPERUSER_ID, [event.id], {'state':'draft'})
        if user.user_type and user.user_type == 'vendor':
            res = mod_obj.get_object_reference(cr, SUPERUSER_ID, 'bista_iugroup', 'view_event_user_tree')
            res_id = res and res[1] or False,
            context.update({'event_id' : ids[0] })
            return {
                'name': _('Event'),
                'view_type': 'form',
                'view_mode': 'tree',
                'view_id': [res_id[0]],
                'res_model': 'event',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
            }
        return True
    
    def get_direction(self, cr, uid, ids, context=None):
        ''' Shows path between Interpreter and Doctor/Location  '''
        cur_obj = self.browse(cr, uid, ids, context=context)[0]
        location = False
        interpreter = cur_obj.interpreter_id
        if cur_obj.event_id:
            location = cur_obj.event_id.location_id
        else:
            return True
        if not interpreter:
            return True
        if not location:
            raise osv.except_osv(_('Warning!'),_('You must enter location first.'))
        url="http://maps.google.com/maps?mode=driving&saddr="
        location_address = geo_query_address(location.street or False , location.zip or False ,location.city or False, \
                                location.state_id and location.state_id.name or False, location.country_id and location.country_id.name or False)
        interp_address = geo_query_address(interpreter.street or False , interpreter.zip or False ,interpreter.city or False, \
                                interpreter.state_id and interpreter.state_id.name or False, interpreter.country_id and interpreter.country_id.name or False)
        url += interp_address + '&daddr=' + location_address + '&mode=driving'
        return {
        'type': 'ir.actions.act_url',
        'url':url,
        'nodestroy': True,
        'target': 'new'
        }

class select_transporter_line(osv.osv):
    _name = 'select.transporter.line'
    _order = 'distance ,rate'
    _columns = {
        'name': fields.related('transporter_id', 'name', type='char', string='Name',store=True),
        'middle_name': fields.related('transporter_id', 'middle_name', type='char', string='Middle Name',store=True),
        'last_name': fields.related('transporter_id', 'last_name', type='char', string='Last Name',store=True),
        'zip': fields.related('transporter_id', 'zip', type='char', string='Zip',store=True),
        'phone': fields.related('transporter_id', 'cell_phone', type='char', string='Phone',store=True),
        'rate': fields.related('transporter_id', 'rate', type='float', string='Rate',store=True),
        'transporter_id': fields.many2one("res.partner",'Transporter', ),
        'select': fields.boolean("Select"),
        'event_id': fields.many2one('event',"Event Id", ),
        'visited':fields.boolean("Visited"),
        'visited_date':fields.date("Visited Date"),
        'voicemail_msg': fields.char("Voicemail Message" , size=128),
        'duration' : fields.char("Duration" , size=42),
        'distance' : fields.float('Distance' ,),
        'state': fields.selection([
            ('draft', 'Unscheduled'),
            ('voicemailsent', 'Voicemail Sent'),
            ('assigned', 'Assigned'),
            ('cancel','Cancelled'),
            ],'Status', readonly=True, required=True,),
        'parent_state': fields.related('event_id','state', type="char", store=True, string="Event State" ,selection=EVENT_STATES,
                 readonly=True,),
        'company_id': fields.related('event_id','company_id', type="many2one", relation="res.company", store=True, string="Company" ,
                 readonly=True,),
    }
    _defaults={
        'voicemail_msg':'',
        }
    
    def leave_voicemail(self , cr ,uid , ids , context= None):
        ''' This function updates or assigns transporter in the event form '''
        cur_obj = self.browse(cr ,uid ,ids[0])
        res, event = cur_obj.event_id, []
        if event.state == 'draft':
            res = self.pool.get('event').write(cr ,uid , [event.id],{'state':'scheduled'})
        self.pool.get('transporter.history').create(cr ,uid ,{'partner_id':event.partner_id and event.partner_id.id or False,
                    'name':cur_obj.transporter_id and cur_obj.transporter_id.id or False,'event_id':event.id,#'event_date': from_dt.strftime('%Y-%m-%d'),
                    'state':'voicemailsent'})
        if cur_obj.transporter_id.user_id and cur_obj.transporter_id.user_id != SUPERUSER_ID:
            if cur_obj.transporter_id.user_id.partner_id  :
                self.pool.get('event').write(cr , uid, [event.id], {'event_follower_ids':[(4, cur_obj.transporter_id.user_id.id)]})
        self.write(cr ,uid , ids, {'state':'voicemailsent'})
        return res
    
    def update_transporter(self, cr, uid, ids, context):
        ''' This function updates or assigns transporter in the event form '''
        cur_obj = self.browse(cr ,uid ,ids[0])
        res, event = cur_obj.event_id, []
        res = self.pool.get('event').write(cr ,uid , [event.id],{'transporter_id':cur_obj.transporter_id and cur_obj.transporter_id.id or False,
                                                                'state':'allocated'})
        
        res = self.unlink(cr ,uid , ids)
        return res

    def cancel_appointment(self, cr, uid, ids, context=None):
        ''' function to cancel assignment for transporter  '''
        if isinstance(ids, (int,long)): ids = [ids]
        if context is None: context = {}
        cur_obj = self.browse(cr , uid, ids[0])
        event = cur_obj.event_id
        if not event.history_id2:
            self.pool.get('transporter.alloc.history').create(cr ,uid ,{'partner_id':event.partner_id and event.partner_id.id or False,'name': cur_obj.interpreter_id and cur_obj.interpreter_id.id or False,
                    'event_id':event.id,'event_date': event.event_date ,'event_start':event.event_start,'event_end':event.event_end,'state':'cancel','company_id': event.company_id and event.company_id.id or False,
                    'cancel_date':time.strftime('%Y-%m-%d %H:%M:%S')})
        else:
            self.pool.get('transporter.alloc.history').write(cr ,uid ,ids[0],{'partner_id':event.partner_id and event.partner_id.id or False,'name': cur_obj.interpreter_id and cur_obj.interpreter_id.id or False,
                    'event_id':event.id,'event_date': event.event_date ,'event_start':event.event_start,'event_end':event.event_end,'state':'cancel','company_id': event.company_id and event.company_id.id or False,
                    'cancel_date':time.strftime('%Y-%m-%d %H:%M:%S')})
        self.write(cr ,uid ,ids , {'state':'cancel'})
        return True
    
    def get_direction(self, cr, uid, ids, context=None):
        ''' Shows path between Transporter and Doctor/Location  '''
        cur_obj = self.browse(cr, uid, ids, context=context)[0]
        location = False
        transporter = cur_obj.transporter_id
        if cur_obj.event_id:
            location = cur_obj.event_id.location_id
        else:
            return True
        if not transporter:
            return True
        if not location:
            raise osv.except_osv(_('Warning!'),_('You must enter location first.'))
        url="http://maps.google.com/maps?mode=driving&saddr="
        location_address = ''
        location_address = geo_query_address(location.street or False , location.zip or False ,location.city or False, \
                                location.state_id and location.state_id.name or False, location.country_id and location.country_id.name or False)
        transporter_address = ''
        transporter_address = geo_query_address(transporter.street or False , transporter.zip or False ,transporter.city or False, \
                                transporter.state_id and transporter.state_id.name or False, transporter.country_id and transporter.country_id.name or False)
        url += transporter_address + '&daddr=' + location_address + '&mode=driving'
        return {
        'type': 'ir.actions.act_url',
        'url':url,
        'nodestroy': True,
        'target': 'new'
        }

class select_translator_line(osv.osv):
    _name = 'select.translator.line'
    _order = 'rate ,distance '
    _columns = {
        'name': fields.related('translator_id', 'name', type='char', string='Name',store=True , domain=[('cust_type','in',('translator','interp_and_transl'))]),
        'middle_name': fields.related('translator_id', 'middle_name', type='char', string='Middle Name',store=True),
        'last_name': fields.related('translator_id', 'last_name', type='char', string='Last Name',store=True),
        'zip': fields.related('translator_id', 'zip', type='char', string='Zip',store=True),
        'phone': fields.related('translator_id', 'cell_phone', type='char', string='Phone',store=True),
        'rate': fields.related('translator_id', 'rate', type='float', string='Rate',store=True),
        'translator_id': fields.many2one("res.partner",'Translator' ,domain=[('cust_type','in',('translator','interp_and_transl'))]),
        'select': fields.boolean("Select"),
        'event_id': fields.many2one('event',"Event Id", ),
        'visited':fields.boolean("Visited"),
        'visited_date':fields.date("Visited Date"),
        'voicemail_msg': fields.char("Voicemail Message" , size=128),
        'duration' : fields.char("Duration" , size=42),
        'distance' : fields.float('Distance' ,),
        'state': fields.selection([
            ('draft', 'Unscheduled'),
            ('voicemailsent', 'Voicemail Sent'),
            ('assigned', 'Assigned'),
            ('cancel','Cancelled'),
            ], 'Status', readonly=True, required=True,),
        'parent_state': fields.related('event_id','state', type="char", store=True, string="Event State" ,selection=EVENT_STATES,
                 readonly=True,),
        'company_id': fields.related('event_id','company_id', type="many2one", relation="res.company", store=True, string="Event State" ,
                 readonly=True,),
    }
    _defaults={
        'voicemail_msg':'',
    }
    
    def leave_voicemail(self , cr ,uid , ids , context= None):
        ''' This function updates or assigns translator in the event form '''
        cur_obj = self.browse(cr , SUPERUSER_ID, ids[0])
        ir_model_data = self.pool.get('ir.model.data')
        event = cur_obj.event_id
        res, template_id = [], False
        for select_line in event.translator_ids2:
            if select_line.translator_id:
                if select_line.state in ('draft','voicemailsent') and select_line.translator_id.id == cur_obj.translator_id.id :
                    raise osv.except_osv(_('Warning!'),_('Selected Translator is already present in the Job offered list!'))
        if event.state == 'draft':
            res = self.pool.get('event').write(cr , SUPERUSER_ID, [event.id], {'state':'scheduled'})
        try:
            template_id = ir_model_data.get_object_reference(cr, SUPERUSER_ID, 'bista_iugroup', 'send_translator_job_offered_event')[1]
        except ValueError:
            template_id = False
        if template_id:
            context={'translator_id': cur_obj.translator_id}
            try:
                self.pool.get('email.template').send_mail( cr, uid, template_id, ids[0], True, context)
            except Exception:
                pass
        if cur_obj.translator_id.user_id and cur_obj.translator_id.user_id != SUPERUSER_ID:
            if cur_obj.translator_id.user_id.partner_id:
                self.pool.get('event').write(cr , SUPERUSER_ID, [event.id] , {'event_follower_ids':[(4, cur_obj.translator_id.user_id.partner_id.id)]})
        self.write(cr ,uid , ids,{'state':'voicemailsent'})
        return res
    
    def update_translator(self, cr, uid, ids, context):
        ''' This function updates or assigns translator in the event form '''
        res= []
        cur_obj = self.browse(cr ,uid ,ids[0])
        event = cur_obj.event_id
        res = self.pool.get('event').write(cr ,uid , [event.id],{'translator_id':cur_obj.translator_id and cur_obj.translator_id.id or False,
                                                                'state':'allocated'})
        res = self.unlink(cr ,uid , ids)
        return res
    
    def cancel_appointment(self, cr, uid, ids, context=None):
        ''' function to cancel assignment for translator  '''
        if isinstance(ids, (int,long)): ids = [ids]
        if context is None: context = {}
        self.write(cr ,uid ,ids , {'state':'cancel'})
        return True
        
    def assign_translator(self ,cr ,uid ,ids ,context):
        obj=self.browse(cr ,uid , ids[0])
        mod_obj = self.pool.get('ir.model.data')
        event = obj.event_id
        assign_history_id = self.pool.get('assign.translator.history').create(cr ,uid ,{'partner_id':event.partner_id and event.partner_id.id or False,'name':obj.translator_id and obj.translator_id.id or False,
                    'event_id':event.id,'event_date':event.event_date ,'event_start':event.event_start,'event_end':event.event_end,'state':'assign','company_id': event.company_id and event.company_id.id or False,
                    'schedule_translator_event_time':time.strftime('%Y-%m-%d %H:%M:%S'),'schedule_event_time':time.strftime('%Y-%m-%d %H:%M:%S')})
        
        res = self.pool.get('event').write(cr ,uid , [event.id],{'translator_id':obj.translator_id and obj.translator_id.id or False,
                                    'state':'allocated','translation_assignment_history_id':assign_history_id})
        res = self.unlink(cr ,uid , ids)
        template_id1 = mod_obj.get_object_reference(cr, uid, 'bista_iugroup', 'event_allocation_translator')[1]
        print"template_id1",template_id1
        res = self.pool.get('event').action_mail_send( cr, uid, ids , event, 'event', template_id1, context=context)
        
        return res
    
    def get_direction(self, cr, uid, ids, context=None):
        ''' Shows path between Interpreter and Doctor/Location  '''
        cur_obj = self.browse(cr, uid, ids, context=context)[0]
        location = False
        translator = cur_obj.translator_id
        if cur_obj.event_id:
            location = cur_obj.event_id.location_id
        else:
            return True
        if not translator:
            return True
        if not location:
            raise osv.except_osv(_('Warning!'),_('You must enter location first.'))
        url="http://maps.google.com/maps?mode=driving&saddr="
        location_address = ''
        location_address = geo_query_address(location.street or False , location.zip or False ,location.city or False, \
                                location.state_id and location.state_id.name or False, location.country_id and location.country_id.name or False)
        trans_address = ''
        trans_address = geo_query_address(translator.street or False , translator.zip or False ,translator.city or False, \
                                translator.state_id and translator.state_id.name or False, translator.country_id and translator.country_id.name or False)
        url += trans_address + '&daddr=' + location_address + '&mode=driving'
        return {
        'type': 'ir.actions.act_url',
        'url':url,
        'nodestroy': True,
        'target': 'new'
        }

class event(osv.osv):
    _description = 'Event'
    _name = "event"
    _order = "event_start desc"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

#    def recancel_appointment(self, cr, uid, ids, context=None):
#        '''Function to allow interpreters or transpoerters to cancel events assigned to them'''
#        if isinstance(ids, (int,long)): ids = [ids]
#        event = self.browse(cr ,uid ,ids[0])
#        ir_model_data = self.pool.get('ir.model.data')
#        if event and event.interpreter_id and event.interpreter_id.user_id.id != uid :
#            raise osv.except_osv(_('Error!'), _('You cannot Cancel this Appointment as you were not allocated to this event.'))
#        history_id = event.history_id
#        if history_id:
#            self.pool.get('interpreter.alloc.history').write(cr, uid, [history_id.id], {'state':'cancel','cancel_date':time.strftime('%Y-%m-%d %H:%M:%S')})
#        template = 'event_reject_after_scheduled_interpreter' if event.state == 'allocated' else \
#                    'event_reject_after_confirmed_interpreter'
#        try:
#            template_id = ir_model_data.get_object_reference(cr, uid, 'bista_iugroup', template)[1]
#        except ValueError:
#            template_id = False
#        if template_id:
#            context={'interpreter_id':event.interpreter_id}
#            self.pool.get('email.template').send_mail( cr, uid, template_id, event.id, True, context)
#        if event.interpreter_id and event.state == 'allocated':
#            self.pool.get('event').write(cr ,uid , [event.id],{'interpreter_id':False,
#            'state':'scheduled'})
#        return True
    
    def onchange_time(self, cr, uid, ids, event_start_time, event_end_time, context=None):
        ''' Not used now '''
        res,warning = {},{}
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        res = {}
        if event_start_time and not event_end_time:
            return True
        else:
            if event_start_time and event_end_time:
                start=datetime.datetime.strptime(str(event_start_time), DATETIME_FORMAT)
                if event_end_time:
                    end=datetime.datetime.strptime(str(event_end_time), DATETIME_FORMAT)
                    if start > end:
                        res.update({'event_end': False})
                        warning = {
                            'title': _('Warning!'),
                            'message' : _('Event start time cannot be greater than event end time')
                            }
        return {'value': res,'warning':warning}
    
#    schedule function to send create event request to mobile app 
    def event_sync_to_mobile(self, cr, user, context={}):
        print'schedular start======================='
        event_ids= self.search(cr, user, [('mobile_event','=',True),('mobile_sync','=',False)])
        print'event_ids=======================',event_ids
        for event_data in self.browse(cr,user,event_ids):
            
            duration=False
            if event_data.location_id:
                
                tz = pytz.timezone('US/Pacific') or pytz.utc
                start = tz.localize(datetime.datetime.strptime(event_data.event_start,"%Y-%m-%d %H:%M:%S"), is_dst=None)
                end = tz.localize(datetime.datetime.strptime(event_data.event_end,"%Y-%m-%d %H:%M:%S"), is_dst=None)

                duration=((end - start).seconds)/60
                print'duration===========',duration
                url = "https://iuconnectapp.com/job_schedules/create_event"
                headers = {'Content-type': 'application/json','Accept': 'application/json'}
                data = {"job_schedule" : 
                            {
                            "title"          :"Need an Interpreter",
                            "description"    :event_data.event_purpose or '',
                            "event_id"       :str(event_data.id),
                            "address_name"   : "Home",
                            "address_street1":event_data.location_id.street or '',
                            "address_street2":event_data.location_id.street2 or '',
                            "address_state"  :event_data.location_id.state_id and event_data.location_id.state_id.name or '' ,
                            "address_zipcode":event_data.location_id.zip,
                            "scheduled_at"   :event_data.event_start or ' ',
                            "language"	     :event_data.language_id and event_data.language_id.name or '',
                            "duration"	     :duration or 0 ,
                            "client_email"   :event_data.ordering_contact_id and event_data.ordering_contact_id.email or '' ,    #email or ''
			   "longitude"	     :event_data.location_id.longitude ,
                           "latitude"	     :event_data.location_id.latitude, 

                            }
                        }
                print data
                try:
                    r = requests.post(url, data=json.dumps(data),headers=headers,auth=('client','secret'))
                    result=r.json()
                    print'result==================',result
                    if result['status']=='true':
                        event_data.write({'job_schedule_id':result['job_schedule']['job_schedule_id'],'mobile_sync':True})
                except:
                    pass
    #        code end here
        return True
            
    def create(self, cr, uid, vals, context=None):
        ''' Event_start and event_end fields are prepared and validated for further flow'''
        if context is None: context = {}
        future_date = datetime.datetime.now() + datetime.timedelta(minutes=10)
        future_date = future_date.strftime('%Y-%m-%d %H:%M:%S')
        if vals.get('injury_date') > future_date:
            raise osv.except_osv(_('Error!'), _("Injury Date should not be in future date "))
        # Here formatting for Event Start date and Event End Date is done according to timezone of user or server 
        if 'event_start_date' in vals or 'event_start_hr' in vals or 'event_start_min' in vals or 'event_end_hr' in vals or \
            'event_end_min' in vals or 'am_pm' in vals or 'am_pm2' in vals or 'customer_timezone' in vals or 'customer_timezone2' in vals:
            DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            # get user's timezone
            user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid)
            customer_timezone = vals.get('customer_timezone',False)
            if customer_timezone:
                tz = pytz.timezone(customer_timezone) or pytz.utc
            elif user.tz:
                tz = pytz.timezone(user.tz) or pytz.utc
            else:
                tz = pytz.timezone('US/Pacific') or pytz.utc
            tz2 = tz
            customer_timezone2 = vals.get('customer_timezone2',False)
            if customer_timezone2:
                tz2 = pytz.timezone(customer_timezone2) or pytz.utc
            elif customer_timezone:
                tz2 = pytz.timezone(customer_timezone) or pytz.utc
            elif user.tz:
                tz2 = pytz.timezone(user.tz) or pytz.utc
            else:
                tz2 = pytz.timezone('US/Pacific') or pytz.utc
            event_start_date = vals.get('event_start_date',False)
            event_start_hr = int(vals.get('event_start_hr',0.0))
            event_start_min = int(vals.get('event_start_min',0.0))
            event_end_hr = int(vals.get('event_end_hr',0.0))
            event_end_min = int(vals.get('event_end_min',0.0))
            am_pm = vals.get('am_pm',False)
            am_pm2 = vals.get('am_pm2',False)
            #print "event_date ,event_start_hr,event_start_min ,event_end_hr,event_end_min, am_pm,am_pm2........",event_start_date,event_start_hr,event_start_min,event_end_hr,event_end_min,am_pm,am_pm2
            if event_start_hr and event_start_hr > 12:
                raise osv.except_osv(_('Error!'), _("Event start time hours can't be greater than 12 "))
            if event_start_min and event_start_min > 59:
                raise osv.except_osv(_('Error!'), _("Event start time minutes can't be greater than 59 "))
#            if (event_start_hr and event_start_min) and (event_start_hr == 12 and event_start_min > 0):
#                raise osv.except_osv(_('Check Start time!'), _("Event start time can't be greater than 12 O'clock "))
            if event_end_hr and event_end_hr > 12:
                raise osv.except_osv(_('Error!'), _(" Event end time hours can't be greater than 12 "))
            if event_end_min and event_end_min > 59:
                raise osv.except_osv(_('Error!'), _("Event end time minutes can't be greater than 59 "))
#            if (event_end_hr and event_end_min) and (event_end_hr == 12 and event_end_min > 0):
#                raise osv.except_osv(_('Check End time!'), _("Event End time can't be greater than 12 O'clock "))
            if event_start_hr < 1 and event_start_min < 1:
                raise osv.except_osv(_('Check Start time!'), _("Event start time can not be 0 or less than 0"))
            if event_end_hr < 1 and event_end_min < 1:
                raise osv.except_osv(_('Check End time!'), _("Event end time can not be 0 or less than 0"))
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
                # get localized dates
    #            localized_datetime = pytz.utc.localize(datetime.datetime.strptime(event_start,DATETIME_FORMAT)).astimezone(tz)
    #            print "localized_datetime.......",localized_datetime
                local_dt = tz.localize(datetime.datetime.strptime(event_start,DATETIME_FORMAT), is_dst=None)
                #print "local_dt........",local_dt
                utc_dt = local_dt.astimezone (pytz.utc).strftime (DATETIME_FORMAT)
#                print "utc_dt.........",utc_dt
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
                local_dt1 = tz2.localize(datetime.datetime.strptime(event_end,DATETIME_FORMAT), is_dst=None)
                #print "local_dt1........",local_dt1
                utc_dt1 = local_dt1.astimezone (pytz.utc).strftime (DATETIME_FORMAT)
#                print "utc_dt1. ........",utc_dt1
                vals['event_end'] = utc_dt1
                
                if datetime.datetime.strptime(event_end,DATETIME_FORMAT) < datetime.datetime.strptime(event_start,DATETIME_FORMAT):
                    raise osv.except_osv(_('Warning!'),_('Event start time cannot be greater than event end time.'))
                elif datetime.datetime.strptime(event_end,DATETIME_FORMAT) == datetime.datetime.strptime(event_start,DATETIME_FORMAT):
                    raise osv.except_osv(_('Warning!'),_('Event start time and end time cannot be identical .'))
        event_id = super(event, self).create(cr, uid, vals, context=context)
        cur_obj = self.browse(cr , SUPERUSER_ID,event_id)
        company_name = cur_obj.company_id and cur_obj.company_id.name or False
        if company_name:
            if company_name.strip().upper() == 'IUG-SD':
                vals['name'] = self.pool.get('ir.sequence').get(cr, SUPERUSER_ID, 'event.iug.sd') or '/'
            elif company_name.strip().upper() == 'ASIT':
                vals['name'] = self.pool.get('ir.sequence').get(cr, SUPERUSER_ID, 'event.asit') or '/'
            elif company_name.strip().upper() == 'ACD':
                vals['name'] = self.pool.get('ir.sequence').get(cr, SUPERUSER_ID, 'event.acd') or '/'
            elif company_name.strip().upper() == 'ALBORS AND ALNET':
                vals['name'] = self.pool.get('ir.sequence').get(cr, SUPERUSER_ID, 'event.aa') or '/'
            else:
                vals['name'] = self.pool.get('ir.sequence').get(cr, SUPERUSER_ID, 'event.iug') or '/'
        else:
            vals['name'] = self.pool.get('ir.sequence').get(cr, SUPERUSER_ID, 'event.iug') or '/'
        self.write(cr , uid, [event_id], {'name': vals['name']})
        
        for translate_attach_id in cur_obj.translate_attach_ids:
            self.pool.get('ir.attachment').write(cr , uid, translate_attach_id.id, {'res_model': 'event','res_id':event_id})
        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid)
        if user.user_type and user.user_type in ('customer','contact'):
            if cur_obj.order_note:
                self.send_approval_mail(cr , SUPERUSER_ID, [event_id])
            else:
                self.write(cr, SUPERUSER_ID, [event_id], {'state': 'draft'})
# code to send request to mobile app when create event:
        event_data = self.browse(cr,uid,event_id,context)
        print event_data,'CREATE'
        duration=False
        utc_dt = local_dt.astimezone (pytz.utc).strftime (DATETIME_FORMAT)
#         if event_data.mobile_event and event_data.location_id:
#             duration=((local_dt1-local_dt).seconds)/60
#             print'duration===========',duration
#             url = "https://iuconnectapp.com/job_schedules/create_event"
#             headers = {'Content-type': 'application/json','Accept': 'application/json'}
#             data = {"job_schedule" : 
#                         {
#                         "title"          :"Need an Interpreter",
#                         "description"    :event_data.event_purpose or '',
#                         "event_id"       :str(event_id),
#                         "address_name"   : "Home",
#                         "address_street1":event_data.location_id.street or '',
#                         "address_street2":event_data.location_id.street2 or '',
#                         "address_state"  :event_data.location_id.state_id and event_data.location_id.state_id.name or '' ,
#                         "address_zipcode":event_data.location_id.zip,
#                         "scheduled_at"   :utc_dt or ' ',
#                         "language"	     :event_data.language_id and event_data.language_id.name or '',
#                         "duration"	     :duration or 0 ,
#                         "client_email"   :event_data.ordering_contact_id and event_data.ordering_contact_id.email or '' ,   #email or ''
# 			"longitude":event_data.location_id.longitude ,
#                         "latitude":event_data.location_id.latitude, 
#                         }
#                     }
#             print data
#             try:
#                 r = requests.post(url, data=json.dumps(data),headers=headers,auth=('client','secret'))
#                 result=r.json()
#                 print'result==================',result
#                 if result['status']=='true':
#                     self.write(cr,uid,event_id,{'job_schedule_id':result['job_schedule']['job_schedule_id'],'mobile_sync':True})
#             except:
#                 pass
#        code end here
        

        return event_id
    
    def write(self, cr, uid, ids, vals, context=None):
        ''' Event_start and event_end fields are prepared and validated for further flow'''
        if isinstance(ids, (int,long)): ids = [ids]
        if context is None: context = {}
        vals['cust_edit'] = True
        res = []
#        print "ids........",ids
        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid)
        if 'multi_type' in vals:
            eve = self.pool.get('event').browse(cr, uid, ids[0], context = context)
            type = vals.get('multi_type')
            if eve and (eve.state == 'draft' or eve.state == 'scheduled'):
                if int(type) == len(eve.assigned_interpreters):
                    vals['state'] = 'allocated'
                    int_line_obj = self.pool.get('select.interpreter.line')
                    for interpreter_line in eve.interpreter_ids2:
                        int_line_obj.cancel_appointment(cr, uid, interpreter_line.id, context=context)
            if eve and eve.state == 'allocated':
                if int(type) > len(eve.assigned_interpreters) and len(eve.assigned_interpreters) != 0:
                    vals['state'] = 'scheduled'
        future_date=datetime.datetime.now() + datetime.timedelta(minutes=10)
        future_date=future_date.strftime('%Y-%m-%d %H:%M:%S')
        if vals.get('injury_date')>future_date:
            raise osv.except_osv(_('Error!'), _("Injury Date should not be in future date "))
                
        if 'event_start_date' in vals or 'event_start_hr' in vals or 'event_start_min' in vals or 'event_end_hr' in vals or \
            'event_end_min' in vals or 'am_pm' in vals or 'am_pm2' in vals or 'customer_timezone' in vals or 'customer_timezone2' in vals:
            DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            # get user's timezone
            cur_obj = self.browse(cr , SUPERUSER_ID, ids[0])
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
                tz = pytz.timezone('US/Pacific') or pytz.utc
            #print "tz...........",tz
            tz2 = tz
            customer_timezone2 = vals.get('customer_timezone2',False)
            if customer_timezone2:
                tz2 = pytz.timezone(customer_timezone2) or pytz.utc
            elif customer_timezone:
                tz2 = pytz.timezone(customer_timezone) or pytz.utc
            elif user.tz:
                tz2 = pytz.timezone(user.tz) or pytz.utc
            else:
                tz2 = pytz.timezone('US/Pacific') or pytz.utc
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
                raise osv.except_osv(_('Error!'), _("Event start time hours can't be greater than 12 "))
            if event_start_min and event_start_min > 59:
                raise osv.except_osv(_('Error!'), _("Event start time minutes can't be greater than 59 "))
#            if (event_start_hr and event_start_min) and (event_start_hr == 12 and event_start_min > 0):
#                raise osv.except_osv(_('Check Start time!'), _("Event start time can't be greater than 12 O'clock "))
            if event_end_hr and event_end_hr > 12:
                raise osv.except_osv(_('Error!'), _(" Event end time hours can't be greater than 12 "))
            if event_end_min and event_end_min > 59:
                raise osv.except_osv(_('Error!'), _("Event end time minutes can't be greater than 59 "))
#            if (event_end_hr and event_end_min) and (event_end_hr == 12 and event_end_min > 0):
#                raise osv.except_osv(_('Check End time!'), _("Event End time can't be greater than 12 O'clock "))
            if event_start_hr < 1 and event_start_min < 1:
                raise osv.except_osv(_('Check Start time!'), _("Event start time can not be 0 or less than 0"))
            if event_end_hr < 1 and event_end_min < 1:
                raise osv.except_osv(_('Check End time!'), _("Event end time can not be 0 or less than 0"))
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
                # get localized dates
                local_dt = tz.localize(datetime.datetime.strptime(event_start,DATETIME_FORMAT), is_dst=None)
                #print "local_dt........",local_dt
                utc_dt = local_dt.astimezone (pytz.utc).strftime (DATETIME_FORMAT)
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
                local_dt1 = tz2.localize(datetime.datetime.strptime(event_end,DATETIME_FORMAT), is_dst=None)
                #print "local_dt1........",local_dt1
                utc_dt1 = local_dt1.astimezone (pytz.utc).strftime (DATETIME_FORMAT)
                #print "utc_dt1.........",utc_dt1
                vals['event_end'] = utc_dt1
                
                if datetime.datetime.strptime(event_end, DATETIME_FORMAT) < datetime.datetime.strptime(event_start,DATETIME_FORMAT):
                    raise osv.except_osv(_('Warning!'),_('Event start time cannot be greater than event end time.'))
                elif datetime.datetime.strptime(event_end, DATETIME_FORMAT) == datetime.datetime.strptime(event_start,DATETIME_FORMAT):
                    raise osv.except_osv(_('Warning!'),_('Event start time and end time cannot be identical .'))
        evnt = self.pool.get('event').browse(cr, SUPERUSER_ID, ids[0], context=context)
        intp_name = []
        for each in evnt.interpreter_ids2:
            if each.state != 'cancel':
                intp_name.append(str(each.name))
        if intp_name:
            ','.join(intp_name)
        
        else: intp_name = ''
        vals['job_offered_interpreters_name'] = intp_name
        if evnt.state in ('allocated', 'unauthorize', 'confirmed', 'unbilled', 'invoiced', 'done'):
            assigned_interp = self._get_interpreter_user_ids(cr, uid, ids, field_id=None, args=None, context=context)
            if assigned_interp:
                for each in assigned_interp:
                    assigned_interp = assigned_interp[each]
                followr = [follower.id for follower in evnt.event_follower_ids]
                common_interp = set(assigned_interp).intersection(followr)
                final_interp = [interpreter for interpreter in common_interp]
            vals['event_follower_ids'] = [(6, 0, final_interp)]
        if user.user_type and user.user_type in ('vendor','customer','contact'):
            res = super(event , self).write( cr , SUPERUSER_ID, ids, vals, context = context)
        else:
            res = super(event , self).write( cr, uid, ids, vals, context = context)
        for translate_attach_id in self.browse(cr , SUPERUSER_ID, ids[0]).translate_attach_ids:
            self.pool.get('ir.attachment').write(cr , uid, translate_attach_id.id, {'res_model': 'event','res_id':ids[0]})
        return res
    
    def open_map_interpreter(self, cr, uid, ids, context=None):
        ''' Shows path between Interpreter and Doctor/Location on Google Map '''
        event = self.browse(cr, uid, ids, context=context)[0]
        location = event.location_id
        interpreter = event.single_interpreter
        if not interpreter:
            raise osv.except_osv(_('Warning!'),_('You must assign interpreter first.'))
        if not location:
            raise osv.except_osv(_('Warning!'),_('You must enter location first.'))
        url="http://maps.google.com/maps?mode=driving&saddr="
        location_address = ''
        location_address = geo_query_address(location.street or False , location.zip or False ,location.city or False, \
                                location.state_id and location.state_id.name or False, location.country_id and location.country_id.name or False)
        interp_address = ''
        interp_address = geo_query_address(interpreter.street or False , interpreter.zip or False ,interpreter.city or False, \
                                interpreter.state_id and interpreter.state_id.name or False, interpreter.country_id and interpreter.country_id.name or False)
        #url="http://maps.google.com/maps?oi=map&q="
        #url = "https://www.google.com/search?q=distance+from+"
        #url += interp_address + '+to+' + location_address
        #url = "https://www.google.com/search?q=distance from mumbai malad to goregaon"
        url += interp_address + '&daddr=' + location_address
        return {
        'type': 'ir.actions.act_url',
        'url':url,
        'nodestroy': True,
        'target': 'new'
        }

    def open_map_transporter(self, cr, uid, ids, context=None):
        ''' Shows path between Transporter and Doctor/Location on Google Map '''
        event = self.browse(cr, uid, ids, context=context)[0]
        location = event.location_id
        transporter = event.transporter_id
        if not transporter:
            raise osv.except_osv(_('Warning!'),_('You must assign Transporter first.'))
        if not location:
            raise osv.except_osv(_('Warning!'),_('You must enter location first.'))
        url="http://maps.google.com/maps?mode=driving&saddr="
        location_address = geo_query_address(location.street or False , location.zip or False ,location.city or False, \
                                location.state_id and location.state_id.name or False, location.country_id and location.country_id.name or False)
        transp_address = geo_query_address(transporter.street or False , transporter.zip or False ,transporter.city or False, \
                                transporter.state_id and transporter.state_id.name or False, transporter.country_id and transporter.country_id.name or False)
        url += transp_address + '&daddr=' + location_address
        return {
        'type': 'ir.actions.act_url',
        'url':url,
        'nodestroy': True,
        'target': 'new'
        }

    def open_map_translator(self, cr, uid, ids, context=None):
        ''' Shows path between Translator and Doctor/Location on Google Map '''
        event = self.browse(cr, uid, ids, context=context)[0]
        location = event.location_id
        translator = event.translator_id
        if not translator:
            raise osv.except_osv(_('Warning!'),_('You must assign translator first.'))
        if not location:
            raise osv.except_osv(_('Warning!'),_('You must enter location first.'))
        url="http://maps.google.com/maps?mode=driving&saddr="
        location_address = geo_query_address(location.street or False , location.zip or False ,location.city or False, \
                                location.state_id and location.state_id.name or False, location.country_id and location.country_id.name or False)
        transl_address = geo_query_address(translator.street or False , translator.zip or False ,translator.city or False, \
                                translator.state_id and translator.state_id.name or False, translator.country_id and translator.country_id.name or False)
        url += transl_address + '&daddr=' + location_address
        return {
        'type': 'ir.actions.act_url',
        'url':url,
        'nodestroy': True,
        'target': 'new'
        }

    def _get_year(self, cr, uid, ids, name, args, context=None):
        """ get year from date """
        res = dict.fromkeys(ids, False)
        for event in self.browse(cr, uid, ids, context=context):
            DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            from_dt = datetime.datetime.strptime(str(event.event_start), DATETIME_FORMAT)
            tm_tuple = from_dt.timetuple()
            year = tm_tuple.tm_year
            res[event.id] = year
        return res
    
    def _get_month(self, cr, uid, ids, name, args, context=None):
        """ get month from date """
        res = dict.fromkeys(ids, False)
        for event in self.browse(cr, uid, ids, context=context):
            DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            from_dt = datetime.datetime.strptime(str(event.event_start), DATETIME_FORMAT)
            tm_tuple = from_dt.timetuple()
            month = tm_tuple.tm_mon
            res[event.id] = month
        return res

    def _get_date(self, cr, uid, ids, name, args, context=None):
        """ get event date from event """
        res = dict.fromkeys(ids, False)
        for event in self.browse(cr, uid, ids, context=context):
            res[event.id] = datetime.datetime.strptime(str(event.event_start), "%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d')
        return res
    
    def _default_get_gateway(self, cr, uid, ids, context=None):
        '''  get deafult gateway for sms '''
        if context is None:
            context = {}
        sms_obj = self.pool.get('sms.smsclient')
        gateway_ids = sms_obj.search(cr, uid, [('state','=','confirm')], limit=1, context=context)
        return 7#gateway_ids and gateway_ids[0] or False

    def _get_event_start(self, cr, uid, ids, name, arg, context=None):
        res={}
        event_time=''
        for line in self.browse(cr, uid, ids):
            event_time=''
            if line.event_start_hr:
                event_time += str(line.event_start_hr) + ":"
            if line.event_start_min:
                if len(str(line.event_start_min)) > 1:
                    event_time += str(line.event_start_min) + " "
                else:
                    event_time += "0" + str(line.event_start_min) + " "
            else:
                event_time += '00' + " "
            if line.am_pm:
                event_time += str(line.am_pm).upper()
            #print"event_time",event_time
            res[line.id]=event_time
        return res

    def _get_event_end(self, cr, uid, ids, name, arg, context=None):
        res={}
        event_time=''
        for line in self.browse(cr, uid, ids):
            event_time=''
            if line.event_end_hr:
                event_time += str(line.event_end_hr) + ":"
            if line.event_end_min:
                if len(str(line.event_end_min)) > 1:
                    event_time += str(line.event_end_min) + " "
                else:
                    event_time += "0" + str(line.event_end_min) + " "
            else:
                event_time += '00' + " "
            if line.am_pm2:
                event_time += str(line.am_pm2).upper()
            #print"event_time",event_time
            res[line.id]=event_time
        return res
    
    def _get_zone(self, cr, uid, context=None):
        ''' Get Zone from user. User have Meta Zone selected . So getting Zone from meta Zone '''
        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid, context=context)
        return user.zone_id and user.zone_id.id or False
    
    def _get_customer(self, cr, uid, context=None):
        ''' Function gets default Billing Customer on the basis of user, in case of Customer creates Event'''
        partner_ids = []
        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid)
        partner_obj = self.pool.get('res.partner')
        if user.user_type in ('customer','contact'):
            if user.user_type=='customer':
            #partner_ids = partner_obj.search(cr , SUPERUSER_ID , [('user_id','=',uid),('cust_type','=','customer'),('company_id','=',user.company_id.id)])
                partner_ids = partner_obj.search(cr , SUPERUSER_ID , [('user_id','=',uid),('cust_type','=','customer'),('company_id','=',user.company_id.id)])
            else:
                partner_ids = partner_obj.search(cr , SUPERUSER_ID , [('user_id','=',uid),('cust_type','=','contact'),('company_id','=',user.company_id.id)])
            if partner_ids:
                partner = partner_obj.browse(cr , SUPERUSER_ID, partner_ids[0] )
                if partner.parent_id:
                    return partner.parent_id.id
                else:
                    return partner_ids[0]
            return partner_ids and partner_ids[0] or False
        return False
    
    def _get_contact(self, cr, uid, context=None):
        ''' Function gets default Billing Contact on the basis of user, in case of Contact creates Event'''
        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid)
        partner_obj = self.pool.get('res.partner')
        if user.user_type and user.user_type in ('customer','contact'):
            partner_ids = partner_obj.search(cr , SUPERUSER_ID , [('user_id','=',uid),('cust_type','=','contact'),('company_id','=',user.company_id.id)])
            return partner_ids and partner_ids[0] or False
        return False
    
    def _arch_preprocessing(self, cr, user, arch, context=None):
        from lxml import etree
        def remove_unauthorized_children(node):
            for child in node.iterchildren():
                if child.tag == 'action' and child.get('invisible'):
                    node.remove(child)
                else:
                    child = remove_unauthorized_children(child)
            return node
        def encode(s):
            if isinstance(s, unicode):
                return s.encode('utf8')
            return s

        archnode = etree.fromstring(encode(arch))
        return etree.tostring(remove_unauthorized_children(archnode), pretty_print=True)
    
    def _search(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False, access_rights_uid=None):
        """ Override search() to put zone wise events filter"""
        if context is None: context = {}
        user_obj = self.pool.get('res.users').browse(cr , SUPERUSER_ID, user)
        if context.get('zone',False) and user_obj.zone_id:
            args.append(eval('[' + "'zone_id'," + "'='," + str(user_obj.zone_id.id) + ']'))
        if not order:
            if context.get('order',False):
                order = context.get('order',False)
        return super(event, self)._search(cr, user, args, offset=offset, limit=limit, order=order, context=context,
                                                count=count, access_rights_uid=access_rights_uid)
    
    def fields_view_get(self, cr, user, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        """ Overrides orm field_view_get.
        @return: Dictionary of Fields, arch and toolbar.
        Overriding  """
        res = super(event, self).fields_view_get(cr, user, view_id, view_type, context, toolbar=toolbar, submenu=submenu)
        CustView = self.pool.get('ir.ui.view.custom')
        user_obj = self.pool.get('res.users').browse(cr, SUPERUSER_ID, user)
        if user_obj.user_type not in ('admin','staff'):
            vids = CustView.search(cr, user, [('user_id', '=', user), ('ref_id', '=', view_id)], context=context)
            if vids:
                view_id = vids[0]
                arch = CustView.browse(cr, user, view_id, context=context)
                res['custom_view_id'] = view_id
                res['arch'] = arch.arch
            res['arch'] = self._arch_preprocessing(cr, user, res['arch'], context=context)
            res['toolbar'] = {'print': [], 'action': [], 'relate': []}
        return res

    def _get_verify_url(self, cr, uid, ids, action='login', view_type=None, menu_id=None, context=None):
        """ generate a Verify url for the given Event, which will be sent to the Verifier . """
        server_ip = self.pool.get('ir.config_parameter').get_param(cr, SUPERUSER_ID, 'server_ip')
        if not server_ip:
            raise osv.except_osv(_('Warning!'),_(' Please Configure the config paramenter "server_ip" as 72.11.224.244 !'))
        res={}
        for event in self.browse(cr, SUPERUSER_ID, ids):
            url = '''/verify.html?id=%s&db=%s'''%(event.id, cr.dbname)
            res[event.id] = url
        return res
    
    def _get_approval_url(self, cr, uid, ids, action='login', view_type=None, menu_id=None, context=None):
        """ generate a Approval url for the given Event, which will be sent to the manager of the customer. """
        server_ip = self.pool.get('ir.config_parameter').get_param(cr, SUPERUSER_ID, 'server_ip')
        if not server_ip:
            raise osv.except_osv(_('Warning!'),_(' Please Configure the config paramenter "server_ip" as 72.11.224.244 !'))
        res={}
        for event in self.browse(cr, SUPERUSER_ID, ids):
            url = '''/approval.html?id=%s&db=%s'''%(event.id, cr.dbname)
            res[event.id] = url
        return res
    
    def _get_intake_notice(self, cr, uid, ids, field_name, arg, context=None):
        ''' Function to return whether less than 24 hour notice or not '''
        if context is None: context = {}
        result = {}
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        for event in self.browse(cr, uid, ids, context=context):
            event_start = datetime.datetime.strptime(str(event.event_start[:19]), DATETIME_FORMAT)
            event_create = datetime.datetime.strptime(str(event.create_date[:19]), DATETIME_FORMAT)
            diff = event_start - event_create
            hours = diff.seconds / 3600 + diff.days * 24
            if hours < 24:
                result[event.id] = 'Yes'
            else:
                result[event.id] = 'No'
        return result
        
    def _get_zone_user_id(self, cr, uid, ids, field_name, arg, context=None):
        ''' Function to get all user ids for this event zone. '''
        if context is None: context = {}
        result, user_ids = {}, []
        for event in self.browse(cr, uid, ids, context=context):
            result[event.id] = SUPERUSER_ID
        return result
    
    def _search_zone_events(self, cr, uid, obj, name, args, context):
        '''Function to search events on the basis of zone of the searching user. '''
        res, event_ids = [], []
        for field, operator, value in args:
            if field == 'zone_wise':
                user = self.pool.get('res.users').browse(cr , SUPERUSER_ID, value)
                if user.zone_id:
                    event_ids = self.pool.get('event').search(cr, SUPERUSER_ID, [('zone_id',operator, user.zone_id and user.zone_id.id or False )])
                res.append(('id', 'in', event_ids))
        return res
    
    def _is_authorized(self, cr, uid, ids, action='login', view_type=None, menu_id=None, context=None):
        """ Check for the event if it is authorized. """
        auth_flag, res = False, {}
        for event in self.browse(cr, uid, ids):
            if event.partner_id:
                if not event.partner_id.fee_note and not event.partner_id.order_note:
                    auth_flag = True
                if event.partner_id.fee_note and not event.fee_note_test:
                    auth_flag = False
                if event.partner_id.order_note and not event.order_note_test:
                    auth_flag = False
            res[event.id] = auth_flag or False
        return res
    
    def _set_is_authorized(self, cr, uid, ids, action='login', view_type=None, menu_id=None, context=None):
        """ Check for the event if it is authorized. """
        auth_flag, res = False, {}
        for event in self.browse(cr, uid, ids):
            if event.partner_id:
                if not event.partner_id.fee_note and not event.partner_id.order_note:
                    auth_flag = True
                if event.partner_id.fee_note and not event.fee_note_test:
                    auth_flag = False
                if event.partner_id.order_note and not event.order_note_test:
                    auth_flag = False
            res[event.id] = auth_flag or False
        return res
    
    def _get_interpreter_inv(self,cr,uid,ids,field_id,args,context=None):
        ''' Function to get Interpreter invoice generated for this event '''
        result, inv = {}, []
        for event in self.browse(cr, uid, ids, context=context):
            result[event.id]={'view_interpreter_inv':False,
                                'view_interpreter_inv2':False,}
            interpreter_invoices = event.supp_invoice_ids
            for invoice in interpreter_invoices:
                inv.append(invoice.id)
            if inv:
                result[event.id]['view_interpreter_inv'] = inv[0]
                result[event.id]['view_interpreter_inv2'] = inv[1] if len(inv)==2 else inv[0]
        return result
    
    def get_rate_info(self, cr, uid, ids, context=None): 
        res, rate = {}, []
        for event in self.browse(cr,uid,ids,context=context):
            res['min_fee'], res['per_hour'], res['qtr_hour'], res['base_hour'] = '0.00', '0.00', '0.00', '0.00'
            int_rate = [interpreter_rate for interpreter_rate in event.partner_id.rate_ids if event.event_purpose == interpreter_rate.rate_type]
            int_rate_id = int_rate[0] if int_rate else False
            if int_rate_id:
                group_rate, base_hour, int_base_hour, per_hour = False, False, False, False
                lang_group = event.language_id and event.language_id.lang_group or False
                if lang_group:
                    if lang_group == 'spanish_regular':
                        group_rate = int_rate_id and int_rate_id.spanish_regular or 0.0
                    if lang_group == 'spanish_licenced':
                        group_rate = int_rate_id and int_rate_id.spanish_licenced or 0.0
                    if lang_group == 'spanish_certified':
                        group_rate = int_rate_id and int_rate_id.spanish_certified or 0.0
                    if lang_group == 'exotic_regular':
                        group_rate = int_rate_id and int_rate_id.exotic_regular or 0.0
                    if lang_group == 'exotic_certified':
                        group_rate = int_rate_id and int_rate_id.exotic_certified or 0.0
                    if lang_group == 'exotic_middle':
                        group_rate = int_rate_id and int_rate_id.exotic_middle or 0.0
                    if lang_group == 'exotic_high':
                        group_rate = int_rate_id and int_rate_id.exotic_high or 0.0
                else:
                    group_rate = int_rate_id and int_rate_id.default_rate or 0.0
                min_fee = str(round(group_rate))+'0' if group_rate else False
                index =  min_fee.find('.') if min_fee else False
                if index >= 0:
                    min_fee = min_fee[:index+3] if len(min_fee[index+1 :]) > 2 else min_fee
                base_hour = int_rate_id.base_hour if int_rate_id else False
                if base_hour:
                    if base_hour=='1hour':
                        int_base_hour = 1
                    elif base_hour=='2hour':
                        int_base_hour = 2
                    elif base_hour=='3hour':
                        int_base_hour = 3
                    else:
                        int_base_hour = 1
                
                per_hour = int_base_hour and group_rate/int_base_hour or group_rate
                per_hour = str(round(per_hour))+'0' if per_hour else False
                index_per =  per_hour.find('.') if per_hour else False
                if index_per >= 0:
                    per_hour = per_hour[:index_per+3] if len(per_hour[index_per+1 :]) > 2 else per_hour

                qtr_hour = int_base_hour and group_rate/(int_base_hour*4) or group_rate/4
                qtr_hour = str(qtr_hour) if qtr_hour else False
                index_qtr =  qtr_hour.find('.') if qtr_hour else False
                if index_qtr >= 0:
                    qtr_hour = qtr_hour[:index_qtr+3] if len(qtr_hour[index_qtr+1 :]) > 2 else qtr_hour

                trans_rate_id = [trans_rate.id for trans_rate in event.partner_id.transporter_rate_lines if event.transportation_type==trans_rate.type]
                trans_rate_id = trans_rate_id[0] if trans_rate_id else False
                res['min_fee'] = min_fee
                res['per_hour'] = per_hour
                res['qtr_hour'] = qtr_hour
                res['base_hour'] = int_base_hour
        return res
    
    def onchange_time_char(self,cr,uid,ids,time,context={}):
        res = {'value':{},'warning':{}}
        if not time:
            return res
        time = time.strip()
        field = context.get('field',False)
        try:
            int(time)
        except:
            warning = {
                'title': _('Invalid Time'),
                'message' : _('Please enter valid time value.(Do not use Characters)')
                }
            res['warning'] = warning
            res['value'][field] =''
            return res
        if len(time) == 1:
            res['value'][field] = '0'+time
        return res
    
    def _tz_get(self,cr,uid, context=None):
        # put POSIX 'Etc/*' entries at the end to avoid confusing users - see bug 1086728
        return [(tz,tz) for tz in sorted(pytz.all_timezones, key=lambda tz: tz if not tz.startswith('Etc/') else '_')]

    def _get_interpreter_user_ids(self, cr, uid, ids, field_id, args,context=None):
        ''' Function to get user_ids of all assigned Interpreters to this event '''
        result, user_ids = {}, []
        for event in self.browse(cr, uid, ids, context=context):
            user_ids = []
            for interpreter in event.assigned_interpreters:
                if interpreter.user_id:
                    user_ids.append(interpreter.user_id.id)
            user_ids = list(set(flatten(user_ids)))
#            print "user_ids......",user_ids
            result[event.id] = user_ids
        return result
    
    def _get_interpreter_user_id(self, cr, uid, ids, context=None):
        result, event_ids = {}, []
        for line in self.pool.get('res.partner').browse(cr, uid, ids, context=context):
            result[line.id] = True
            cr.execute("""SELECT event_id FROM event_partner_rel where interpreter_id = %s"""%(line.id,))
            event_ids = map(lambda x: x[0], cr.fetchall())
        return event_ids
    
    def _get_task_state(self, cr, uid, ids, field_id, args,context=None):
        result = {}
        for event in self.browse(cr, uid, ids, context=context):
            task = event.task_id if event.task_id else False
            result[event.id] = task and task.stage_id and task.stage_id.state or False
        return result
    
    def _get_task_state_edit(self, cr, uid, ids, context=None):
        if isinstance(ids, (int,long)): ids = [ids]
        result = {}
        for task in self.pool.get('project.task').browse(cr, uid, ids):
            result[task.event_id.id] = True
        return result.keys()
    
    def onchange_multi_type(self, cr, uid, ids,type, context=None):
        res = {'value':{} , 'warning':{}}
        if not type:
            return res
        if ids:
            if isinstance(ids,list): ids = ids[0] 
            event = self.pool.get('event').browse(cr,uid,ids,context = context)
            if event.state == 'allocated':
                if  int(type) < len(event.assigned_interpreters) and len(event.assigned_interpreters) != 0:
                    warning = {
                        'title': _('Warning!'),
                        'message' : _('Please Unassign atleast one interpreter first')
                    }
                    res['warning'] = warning
                    res['value']['multi_type'] = '2'
        return res

    def _get_interpreter_email(self, cr, uid, ids, field_id, args,context=None):
        ''' Function to get Interpreter assigned to this event '''
        result, email = {}, ''
        for event in self.browse(cr, uid, ids, context=context):
            email = ''
            for interpreter in event.assigned_interpreters:
                if interpreter.email:
                    if not email:
                        email = interpreter.email
                    else:
                        email += ', ' + interpreter.email
            result[event.id] = email
        return result
    
    def _get_suppress_email(self, cr, uid, ids, field_id, args,context=None):
        ''' Function to get mark Supress Email on the basis of Ordering Customer'''
        result = {}
        for event in self.browse(cr, uid, ids, context=context):
            if (event.ordering_partner_id and event.ordering_partner_id.suppress_email) or (event.ordering_contact_id and event.ordering_contact_id.suppress_email):
                result[event.id] = True
            else:
                result[event.id] = False
        return result
    
    def _save_suppress_email(self, cr, uid, event_id, field_name, field_value, arg, context=None):
        field_value = field_value or 'none'
        event_obj = self.pool.get('event')
        if field_value != 'none':
            return event_obj.write(cr, uid, [event_id], {'suppress_email': field_value})

    
    def _set_suppress_email_edit(self, cr, uid, ids, context=None):
        if isinstance(ids, (int,long)): ids = [ids]
        result = {}
        for partner in self.pool.get('res.partner').browse(cr, uid, ids, context=context):
            result[partner.id] = True
        return result.keys()
    
    def _set_interpreter_email(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('res.partner').browse(cr, uid, ids, context=context):
            result[line.id] = True
        return result.keys()
    
    def _set_interpreter_email_edit(self, cr, uid, ids, context=None):
        if isinstance(ids, (int,long)): ids = [ids]
        result = {}
        for line in self.pool.get('res.partner').browse(cr, uid, ids, context=context):
            result[line.id] = True
        return result.keys()
    
    def _interpreters_phone(self, cr, uid, ids, fields, args, context=None):
        res, phone = {}, ''
        for event in self.browse(cr, uid, ids):
            phone = ''
            for interpreter in event.assigned_interpreters:
                if interpreter.cell_phone:
                    if not phone:
                        phone = interpreter.cell_phone
                    else:
                        phone += ', ' + interpreter.cell_phone
            res[event.id] = phone
        return res
    
    def _set_interpreter_phone(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('res.partner').browse(cr, uid, ids, context=context):
            result[line.id] = True
        return result.keys()
    
    def _single_interpreter(self, cr, uid, ids, fields, args, context=None):
        res = {}
        for event in self.browse(cr, uid, ids):
            res[event.id], interpreter = False, False
            for line in event.assigned_interpreters:
                if not interpreter:
                    res[event.id] = line.id
        return res

    def _check_attachment_timesheet(self, cr, uid, ids, fields, args, context=None):
        attachment_obj = self.pool.get('ir.attachment')
        res = {}
        for record in self.browse(cr, uid, ids):
            attachment_search = attachment_obj.search(cr, uid, [('res_id', '=', record.id), ('name', 'ilike', '%_timesheet')])
            if attachment_search:
                res[record.id] = True
            else:
                res[record.id] = False
        return res

    _columns = {
        'name': fields.char('Event Id', size=128,  select=True),
        'no_editable': fields.boolean('No Editable'),
        'patient_id': fields.many2one('patient', 'Patient/Client', track_visibility='onchange', ),
        'partner_id': fields.many2one('res.partner',"Customer" , track_visibility='onchange'),
        'ordering_partner_id': fields.many2one('res.partner',"Ordering Customer" , track_visibility='onchange'),
        'authorize_partner_id': fields.many2one('res.partner',"Authorized Customer" , track_visibility='onchange', domain="[('cust_type','=','customer')]"),
        'authorize_contact_id': fields.many2one('res.partner',"Authorized Contact" , domain="[('cust_type','=','contact')]" ,track_visibility='onchange'),
        'ordering_contact_id': fields.many2one('res.partner',"Ordering Contact" , domain="[('cust_type','=','contact')]",track_visibility='onchange'),
        'contact_id': fields.many2one('res.partner',"Contact" , domain="[('cust_type','=','contact')]" ,track_visibility='onchange'),
        'date': fields.date('Date', select=1),
        'ref': fields.char('Reference', size=64, select=1),
        'user_id': fields.many2one('res.users', 'Created By', readonly=True, domain="[('user_type','=','staff')]"),
        'created_by': fields.related('user_id', 'user_type', type='char', readonly=True, store=True, string="Created User Type"),
        
#        'active': fields.boolean('Active'),
        'function': fields.char('Job Position', size=128),
        'company_id': fields.many2one('res.company', 'Company', select=1 ,required=True,track_visibility='onchange'),
        'claim_no': fields.char("Claim#" , size=64),
        'medical_no': fields.char("Medical#", size=20),
        'po_no': fields.char("PO#", size=16),
        'claim_date': fields.date('Claim Date'),
        'suppress_email': fields.boolean('Suppress Email'),
#        'suppress_email': fields.function(_get_suppress_email, type='boolean', string="Suppress Email", fnct_inv=_save_suppress_email, store=True),
#                                    store={
#                                        'event': (lambda self, cr, uid, ids, c={}: ids, ['ordering_contact_id','ordering_partner_id'], 50),
#                                        'res.partner': (_set_suppress_email_edit, ['suppress_email'], 51),
#                                    }),
        'is_authorized': fields.function(_is_authorized, type='boolean', string='Is Authorized?', store=True),
        'employer': fields.char("Employer" , size=64),
        'language_id': fields.many2one("language" ,"Language", track_visibility='onchange'),
        'language_id2': fields.many2one("language" ,"Language 2", track_visibility='onchange'),
        'special_discount': fields.float("Special Discount(%)"),
        'zone_id': fields.many2one('meta.zone',"Zone" ,track_visibility='onchange'),
        'event_type': fields.selection([('language','Language'),('transport','Transport'),('translation','Translation'),('lang_trans','Lang And Transport')],"Event Type"),
        
        'event_start': fields.datetime("Event Start Time" , required=True ,track_visibility='onchange'),
        'event_end': fields.datetime("Event End Time",required=True ,track_visibility='onchange'),
        'actual_event_start': fields.datetime("Actual Event Start Time"),
        'actual_event_end': fields.datetime(" Actual Event End Time"),
        'verified_event_start': fields.datetime("Actual Event Start Time"),
        'verified_event_end': fields.datetime(" Actual Event End Time"),
        'customer_timezone': fields.selection(_tz_get,'Customer TimeZone',),
#        'customer_timezone': fields.selection([('US/Pacific','US/Pacific'),('US/Eastern','US/Eastern'),('US/Alaska','US/Alaska'),('US/Aleutian','US/Aleutian'),('US/Arizona','US/Arizona')
#                            ,('US/Central','US/Central'),('US/East-Indiana','US/East-Indiana'),('US/Hawaii','US/Hawaii'),('US/Indiana-Starke','US/Indiana-Starke'),('US/Michigan','US/Michigan')
#                            ,('US/Mountain','US/Mountain'),('US/Samoa','US/Samoa')],'Customer TimeZone',),
        'customer_timezone2': fields.selection([('US/Pacific','US/Pacific'),('US/Eastern','US/Eastern'),('US/Alaska','US/Alaska'),('US/Aleutian','US/Aleutian'),('US/Arizona','US/Arizona')
                            ,('US/Central','US/Central'),('US/East-Indiana','US/East-Indiana'),('US/Hawaii','US/Hawaii'),('US/Indiana-Starke','US/Indiana-Starke'),('US/Michigan','US/Michigan')
                            ,('US/Mountain','US/Mountain'),('US/Samoa','US/Samoa')],'Customer TimeZone',),
        'event_start_date': fields.date("Event Date", required=True),
        'event_start_hr': fields.char("Event Start Hours", size=2, required=True),
        'event_start_min': fields.char("Event Start Minutes", size=2, required=True),
        'event_end_hr': fields.char("Event End Hours", size=2, required=True),
        'event_end_min': fields.char("Event End Minutes", size=2, required=True),
        'am_pm': fields.selection([('am','AM'),('pm','PM')],"AM/PM", required=True),
        'am_pm2': fields.selection([('am','AM'),('pm','PM')],"AM/PM", required=True),
        'event_start_time':fields.function(_get_event_start, type='char', string='Event start time' ,store=True),
        'event_end_time':fields.function(_get_event_end, type='char', string='Event End time' ,store=True),
        
        'cancel_reason_id': fields.many2one('cancel.reason', 'Cancel Reason', track_visibility='onchange'),
        'event_out_come_id': fields.many2one('event.out.come', 'Event Outcome', track_visibility='onchange'),
        'appointment_type_id': fields.many2one("appointment.type",'Appointment Type', ),
        'interpreter_id': fields.many2one('res.partner','Interpreter' ,track_visibility='onchange'),
        'doctor_id': fields.many2one("doctor",'Doctor', track_visibility='onchange'),
        'certification_level_id': fields.many2one("certification.level","Certification Level" ,track_visibility='onchange'),
        # needs to be commented
        
        'comment': fields.text('Notes', track_visibility='onchange'), 
        'event_note': fields.text('Event Notes', track_visibility='onchange'),
        'interpreter_note': fields.text('Interpreter Notes', track_visibility='onchange'),
        'cust_note':fields.text('Customer Note', track_visibility='onchange'),
        
        'authorize_date':fields.date('Authorize Date'),
        'fee_note_status_id': fields.many2one('fee.note.status',"Fee Note Status"),
        
#        'pay_miles_after': fields.float("Pay Miles After"),
#        'bill_miles_after': fields.float("Bill Miles After"),
#        'special_pay': fields.boolean("Special/Bill Pay"),
#        'bill_for_setup': fields.boolean("Bill For Setup?"),
#        'require_credit_card': fields.boolean("Require Credit Card"),
#        'credit_card': fields.many2one("credit.card","Credit Card" ),
#        'security_only':fields.boolean("Security Only?"),
#        'amount':fields.float("Amount"),
#        'code':fields.char("Code",size=64),
        'state': fields.selection([
            ('unapproved', 'Unappoved'),
            ('rejected', 'Rejected'),
            ('draft', 'Unscheduled'),
            ('scheduled', 'Job Offered'),
            ('allocated', 'Scheduled'),
            ('unauthorize','Unauthorize'),
            ('confirmed', 'Confirmed'),
            ('unbilled', 'Unbilled'),
            ('invoiced','Invoiced'),
            ('cancel','Cancelled'),
            ('done', 'Done'),
            ],'Status', readonly=True, required=True, track_visibility='onchange'),
        'attachment_present': fields.function(_check_attachment_timesheet, type='boolean', string='Timesheet Present'),
#       ++++++++++ Tracking Fields +++++++++++
        'project_id': fields.many2one('project.project',"Related Project"),
        'task_id': fields.many2one('project.task',"Related Task"),
#        'task_state':fields.related('task_id','stage_id','state', type='char', string='Task State',store=True),
        'task_state':fields.function(_get_task_state, type='char', string='Task State' , store={
                                'project.task': (_get_task_state_edit, ['stage_id'], 20),
                                }),
        'invoice_state': fields.related('cust_invoice_id','state', type='char', string='Invoice State'),
        'history_id': fields.one2many('interpreter.alloc.history','event_id','Interpreter\'s History'),
        'history_id2': fields.many2one('transporter.alloc.history',"Related History" ),
        'history_id3': fields.many2one('translator.alloc.history',"Related History" ),
        'history_id4': fields.many2one('patient.auth.history',"Related History" ),
        'cust_invoice_id':fields.many2one('account.invoice','Customer Invoice'),
#        'supp_invoice_id':fields.many2one('account.invoice','Supplier Invoice'),
        'supp_invoice_ids':fields.many2many('account.invoice','task_inv_rel','event_id','invoice_id','Interpreter Invoices'),
        'supp_invoice_id2':fields.many2one('account.invoice','Supplier Invoice2'),
        
        'interpreter_id2': fields.many2one('res.partner','Select Interpreter', domain=[('is_interpretation_active','=',True)] ),
        'translator_id2': fields.many2one('res.partner','Select Translator', domain=[('is_translation_active','=',True)] ),
        'transporter_id2': fields.many2one('res.partner','Select Transporter' ),
        
        'interpreter_ids': fields.many2many('select.interpreter.line', 'select_assign_rel2', 'wiz_id','interp_id',"Interpreters",
                                            domain=[('state','in', ('draft',))]),
        'interpreter_ids2': fields.many2many('select.interpreter.line', 'select_assign_rel2', 'wiz_id','interp_id',"Interpreters",
                                            domain=[('state','in', ('voicemailsent','cancel'))] ),
#       ++++++++++++++ Filter Fields ++++++++++++++++
#        'day': fields.function(_get_day, type='char', string='Day' ,store=True),
        'year': fields.function(_get_year, type='char', string='Year' , store=True),
        'month':fields.function(_get_month, type='selection', selection=[('01','January'), ('02','February'), ('03','March'), ('04','April'), ('05','May'), ('06','June'),
                ('07','July'), ('08','August'), ('09','September'), ('10','October'), ('11','November'), ('12','December')], string='Month', readonly=True, select=True , store=True),
        #'gateway': fields.many2one('sms.smsclient', 'SMS Gateway', required=True),
#        'event_date_from':fields.function(lambda *a,**k:{}, method=True, type='date',string="Event date from"),
#        'event_date_to':fields.function(lambda *a,**k:{}, method=True, type='date',string="Event date to"),
        'event_date': fields.function(_get_date, type='date', string='Event Date' ,store=True),
        
#      ++++++++++++++ Transport Events ++++++++++++++++
        'transporter_id':fields.many2one('res.partner',"Transporter" ,track_visibility='onchange'),
        'transporter_ids': fields.many2many('select.transporter.line', 'select_transporter_rel', 'wiz_id','transp_id',"Transporters",
            domain=[('state','in', ('draft',))] ,),
        'transporter_ids2': fields.many2many('select.transporter.line', 'select_transporter_rel', 'wiz_id','transp_id',"Transporters",
            domain=[('state','in', ('voicemailsent','cancel'))] ,),
        'km': fields.float('Kms'),
        'phone_cust': fields.char('Phone', size=15),
        'event_follower_ids': fields.many2many('res.users', 'event_followers_rel1', 'event_id','user_id','Interpreter Followers',help='Used for interpreter Portal, to show events , job offered to them',track_visibility='onchange'),
        'event_id' : fields.integer("Event ID"),
        # needs to be removed
        'is_follow_up':fields.boolean("Is Follow Up"),
        'source_event_id': fields.many2one('event',"Source Event"),
#        'is_ivr_event':fields.boolean("Is IVR Event "),
        'approving_mgr':fields.char('Approving Manager'),
        'approving_mgr_email':fields.char('Approving Mgr Email'),
#        'is_archieved': fields.boolean('Is Archieved'),
        
        'location_id': fields.many2one("location",'Location Id' ,track_visibility='onchange'),
        'translator_id':fields.many2one('res.partner',"Translator" ,domain=[('cust_type','in',('translator','interp_and_transl'))],track_visibility='onchange'),
        'translator_ids': fields.many2many('select.translator.line', 'select_translator_rel', 'wiz_id','translator_id',"Translators",
                            domain=[('state','in', ('draft',))] ,),
        'translator_ids2': fields.many2many('select.translator.line', 'select_translator_rel', 'wiz_id','translator_id',"Translators",
                            domain=[('state','in', ('voicemailsent','cancel'))] ,),
        'translate_attach_ids':fields.one2many('ir.attachment','event_id','Attachments'),
        'total_cost':fields.float('Total Cost',digits=(16,2)),
#        'is_insurance_claim': fields.boolean('Is Insurance Claim'),
        'dob': fields.date("Date Of Birth"),
        'ssnid': fields.char("Social Security" , size= 40),
        'quickbooks_id': fields.text('QuiockBook Id'),
#        'job_sequence': fields.char('Job Sequence' , size=40),
#        'doi': fields.date("DOI"),
        'gender': fields.selection([('male','Male'),('female','Female')],"Gender"),
        
#        'duplicate_active':fields.boolean('Duplication Event Active'),
#        'duplicate_end_month':fields.date('Duplicate Event End Month'),
#        'recurring_next_date':fields.date('Next Date To run the schedular'),
#        'recurring_type':fields.char('Recurring Type'),
        
        'cust_gpuid': fields.char('GL Code',size=64),
        'cust_csid': fields.char('GPUID',size=64),
        'event_purpose': fields.selection([('normal','Legal'),('medical','Medical'),('deposition','depositions'),('conf_call','Conf Call'),('other','Other')],"Event Purpose",
                                            required=True ,track_visibility='onchange'),
#        ++++++++ Transport events +++++++++++
#        'billing_partner_id': fields.many2one('res.partner',"Payer" , domain="[('cust_type','=','customer')]"),
#        'billing_contact_id': fields.many2one('res.partner',"Adjuster" , domain="[('cust_type','=','contact')]"),
        'injury_date': fields.datetime('Injury Date'),
#        'injury_desc': fields.char('Injury Description',size=100),
#        'employer_contact': fields.char('Employer Contact',size=64),
#        'case_manager_id': fields.many2one('hr.employee','Case Manager'),
#        'provider': fields.char('Provider Name'),
        'transportation_type': fields.selection([('ambulatory','Ambulatory'),('wheelchair','Wheelchair'),('stretcher','Stretcher')],"Transportation Type"),
        
        ####Maintaining the history for assignment of event#####333
        'translation_assignment_history_id': fields.many2one('assign.translator.history','Translator Assignment ID'),
        #### Test Boolean from res_partner
        'fee_note_test':fields.boolean('Fee Note'),
        'order_note_test':fields.boolean('SAF'),
#        'need_glcode': fields.boolean("Need GLCode/GLUID/Approving MGR",),
#        'is_csid': fields.boolean('CSID'),
#        'is_kaiser': fields.boolean('IS Kaiser'),
#        'is_hh': fields.boolean('Is Health & Human'),
#        'is_john_muir': fields.boolean('Is John Muir'),
        'customer_group': fields.char('Customer Group'),
        'customer_basis':fields.boolean('Customer Basis?', help="Customer Basis Scheduler in the Event Form"),
        
        'department': fields.char('Department',size=64),
        'schedule_event_time': fields.datetime('Schedule Event Time' ,readonly=True),
        'sales_representative_id': fields.many2one('res.users','Sales Representative', domain="[('user_type','=','staff')]"),
        'scheduler_id': fields.many2one('res.users','Scheduler', domain="[('user_type','=','staff')]"),
        
        'project_name_id':fields.many2one('project','Project'),
        'approval_url': fields.function(_get_approval_url, type="char", string='Approval Url'),
        'verify_url': fields.function(_get_verify_url, type="char", string='Verify Url'),
        'order_note': fields.boolean('SAF?'),
#        'event_approval': fields.boolean('Event Approval Required?'),
#        'event_verification': fields.boolean('Event Verification Required?'),
        'verifying_mgr': fields.char('Verifying Manager'),
        'verifying_mgr_email': fields.char('Verifying Mgr Email'),
        'verify_state': fields.selection([('verified','Verified'),('not_verified','Not Verified')],'Event Verify State',track_visibility='onchange'),
        'fax': fields.char("Fax"),
        'approve_time': fields.date('Approved Date'),
        'verify_time': fields.date('Verify Date'),
        'mental_prog': fields.selection([('child','Child'),('adult','Adult')],'Mental health prg.'),
        'interpreter_line_ids': fields.many2many('res.partner', 'event_interpreter_rel', 'event_id','interpreter_id',"Interpreters"),
	'assigned_interpreters': fields.many2many('res.partner','event_partner_rel','event_id','interpreter_id','Interpreters'),
        'multi_type': fields.selection([
                                        ('1', 'Single Interpreter'),
                                        ('2', 'Two Interpreters'),
                                        ], 'Interpreters Type', track_visibility='onchange'),
        'all_interpreter_email': fields.function(_get_interpreter_email, type='char', string="All Interpreter Email",
                                        store={
                                        'event': (lambda self, cr, uid, ids, c={}: ids, ['assigned_interpreters'], 50),
                                        'res.partner': (_set_interpreter_email, ['email'], 20),
                                    }),
        'interpreters_phone': fields.function(_interpreters_phone, type='char', string="Cell phone",
                                        store={
                                        'event': (lambda self, cr, uid, ids, c={}: ids, ['assigned_interpreters'], 50),
                                        'res.partner': (_set_interpreter_phone, ['cell_phone'], 20),}
                                    ),
        
#        'all_interpreter_user_ids': fields.function(_get_interpreter_user_ids, type='char',  string="All Interpreter Userid",
#                                    store={
#                                        'event': (lambda self, cr, uid, ids, c={}: ids, ['assigned_interpreters'], 50),
#                                        'res.partner': (_get_interpreter_user_id, ['user_id'], 20),
#                                    }),
        # Used in Interpreter Portal , to show interpreters events assigned to them 
        'interpreter_user_id': fields.related('assigned_interpreters','user_id', type='many2many', relation="res.users", string="All Interpreter Userid"),
        'job_offered_interpreters': fields.related('interpreter_ids2','interpreter_id', type='many2many', relation="res.partner", string="All Job Offred Interpreter"),
        'job_offered_interpreters_name':fields.char('Job Offered'),
        'single_interpreter': fields.function(_single_interpreter, type='many2one', relation='res.partner', string="Interpreter",
                                    store={
                                    'event': (lambda self, cr, uid, ids, c={}: ids, ['assigned_interpreters'], 50),
                                }),
#        'view_interpreter': fields.function(_get_interpreter,type ='many2one',obj='res.partner', multi="interpreter",string="Interpreter"),
#        'view_interpreter2': fields.function(_get_interpreter,type ='many2one',obj='res.partner',multi="interpreter",string="Interpreter2"),
        'view_interpreter_inv': fields.function(_get_interpreter_inv,type = 'many2one',obj='account.invoice', multi="interpreter_inv",string='Interpreter Invoice'),
        'view_interpreter_inv2': fields.function(_get_interpreter_inv,type = 'many2one',obj='account.invoice',multi="interpreter_inv",string='Interpreter Invoice2'),
#        'interpreter_rate_line': fields.function(_get_int_trans_rate,type = 'many2one',obj='rate',multi="int_trans_rate",string  = "Interpreter Rate Line"),
#        'transporter_rate_line': fields.function(_get_int_trans_rate,type = 'many2one',obj='transporter_rate',multi="int_trans_rate",string  = "Transporter Rate Line"),
#        'language_group_rate': fields.function(_get_int_trans_rate,type = 'float',multi="int_trans_rate",string  = "Language Group Rate"),
#        'int_base_hour': fields.function(_get_int_trans_rate,type = 'integer',multi="int_trans_rate",string  = "Base Hour"),
        'dr_name': fields.char('Doctor Name'),
        'cost_center': fields.char('Cost Center'),
#        'social_worker': fields.char('Social Worker'),
        'emergency_rate': fields.boolean('Emergency Rate'),
        'create_date': fields.date("Create Date"),
        'job_schedule_id':fields.char('Mobile Event ID',size=128),
        'mobile_event':fields.boolean('Send Event To Mobile App'),
        'mobile_sync':fields.boolean('Sync'),
        'intake_notice': fields.function(_get_intake_notice, type="char", string='Intake Notice'),
        'cust_edit': fields.boolean('Customer Edit'),
        'stat': fields.boolean('Stat'),
        'verified_by' : fields.char('Verified By'),
        'verified_dt' : fields.datetime('Verifying Time'),
    }
    _defaults = {
        'name':'/',
        'no_editable': False,
        'event_type': 'language',
        'state': 'draft',
        'is_follow_up': False,
#        'is_insurance_claim': False,
        'event_start': lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
        'event_end': lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
        'company_id': lambda self, cr, uid, ctx: self.pool.get('res.company')._company_default_get(cr, uid, 'event', context=ctx),
        'user_id': lambda obj, cr, uid, context: uid,
#        'scheduler_id': lambda obj, cr, uid, context: uid,
        'event_purpose': 'medical',
        'am_pm': 'am',#_get_am_pm,
        'am_pm2': 'am',#_get_am_pm,
#        'event_start_date': lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT),
        'event_start_hr': '00',#_get_hour,
        'event_start_min': '00',#_get_minute,
        'event_end_hr': '00',#_get_hour,
        'event_end_min': '00',#_get_minute,
        'transportation_type': 'ambulatory',
#        'partner_id': _get_customer,
        'ordering_partner_id': _get_customer,
#         'contact_id': _get_contact,
        'ordering_contact_id':_get_contact,
        'is_authorized': False,
        'mental_prog':'adult',
#        'injury_date': fields.datetime.now,
        'order_note': False,
        'multi_type': '1',
    }
    
    def _check_start_end_date(self, cr, uid, ids, forced_user_id=False, context=None):
        ''' validates Start and End Date in Event Form . Event End Date should be greater than start Date'''
        for event in self.browse(cr, uid, ids, context=context):
            DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            if event.event_start and event.event_end:
                start = datetime.datetime.strptime(str(event.event_start[:19]), DATETIME_FORMAT)
                end = datetime.datetime.strptime(str(event.event_end[:19]), DATETIME_FORMAT)
#                self.write(cr , uid, ids, {'event_start':event_start, 'event_end':event_end})
                if start > end:
                    raise osv.except_osv(_('Warning!'),_('  Event start date can not be greater than event end Date.'))
                    return False
        return True
    
    def _check_special_discount(self, cr, uid, ids, forced_user_id=False, context=None):
        ''' validates Special Discount '''
        for event in self.browse(cr, uid, ids, context=context):
            if event.special_discount > 100:
                raise osv.except_osv(_('Warning!'),_('Special Discount Can not be greater than 100 % !'))
                return False
        return True
    
    def _check_patient_ref(self, cr, uid, ids, forced_user_id=False, context=None):
        ''' Check that one of the patient or ref is entered atleast for Language Event '''
        for event in self.browse(cr, uid, ids, context=context):
            if event.event_type and  event.event_type == 'language':
                if (not event.patient_id) and (not event.ref): 
                    raise osv.except_osv(_('Warning!'),_('Please select patient or enter Referance!'))
        return True
    
    _constraints = [(osv.osv._check_recursion, 'You cannot create recursive Event hierarchies.', ['parent_id']),
                    (_check_start_end_date, ' """  { Event start date can not be greater than event end Date. }""" ', ['event_start','event_end']),
                    (_check_special_discount, ' """  { Special Discount Can not be greater than 100 % !}""" ', ['special_discount']),
                    (_check_patient_ref, ' """  { Please select patient or enter Referance! }""" ', ['patient_id','ref'])]
    
    def assign_meta_zone_to_event(self, cr, uid, ids, context):
        ''' Function to Assign the Meta Zone to Events '''
#        cr.execute("""SELECT id FROM event where company_id in (6,4) and event_start_date <= '2015-01-01' and event_start_date >= '2014-11-01'""")
#        event_ids = map(lambda x: x[0], cr.fetchall())
        event_obj = self.pool.get('event')
        user_obj = self.pool.get('res.users')
        count = 0
        event_ids = event_obj.search(cr, uid, [('company_id','in',(6,4))])
#        print "event_ids.........",len(event_ids)
        if event_ids:
            for event_id in event_ids:
                count += 1
                event = event_obj.browse(cr, uid, event_id)
                if event.location_id:
                    meta_zone_id = event.location_id.zone_id and event.location_id.zone_id.meta_zone_id and event.location_id.zone_id.meta_zone_id.id or False
                    if meta_zone_id:
                        user_ids = user_obj.search(cr, uid, [('zone_id','=',meta_zone_id)])
                        event_obj.write(cr , uid, [event_id], {'zone_id': meta_zone_id, 'scheduler_id': user_ids and user_ids[0] or False})
                if count % 1000 == 0:
#                    print "count .......",count
                    cr.commit()
        return True
    
    def assign_timezone_to_event(self, cr, uid, ids, context):
        ''' Function to Assign the timezone to Events '''
        event_obj = self.pool.get('event')
        zip_code = self.pool.get('zip.code')
        count, zone, tz = 0, False, False
        event_ids = event_obj.search(cr, uid, [('company_id','in',(6,4)),('event_date','>=','2015-02-24')])
#        print "event_ids.........",len(event_ids)
        if event_ids:
            for event in event_obj.browse(cr, uid, event_ids):
                count += 1
                if event.location_id and event.location_id.zip:
                    zip_ids = zip_code.search(cr, uid, [('name', '=', event.location_id.zip.strip())])
                    if zip_ids:
                        time_zone = zip_code.browse(cr, uid, zip_ids[0]).time_zone
                        tz = _timezone_event.get(int(time_zone),False) if time_zone else False
                        if tz:
                            try:
                                event_obj.write(cr, uid, [event.id], {'customer_timezone': tz})
                            except Exception:
                                pass
                        else:
                            time_zone = self.pool.get('location').get_timezone(cr, uid, [loc.id], context=context)
                            if time_zone:
                                try:
                                    event_obj.write(cr, uid, [event.id], {'customer_timezone': time_zone})
                                except Exception:
                                    pass
                if count % 10 == 0:
#                    print "count .......",count
                    cr.commit()
        return True
    
    def format_interpreter_customer_note(self, cr, uid, ids, context):
        ''' Function to Remove html tags from interpreter and customer Note in Events '''
        event_obj = self.pool.get('event')
        count = 0
        tag_re = re.compile(r'<[^>]+>')
        event_ids = event_obj.search(cr, uid, [])
        if event_ids:
            for event in event_obj.browse(cr, uid, event_ids):
                count += 1
                interpreter_note, cust_note = '', ''
                if event.interpreter_note:
                    interpreter_note = tag_re.sub(' ', event.interpreter_note.encode('utf-8', 'ignore')).replace('&nbsp;','')
                if event.cust_note:
                    cust_note = tag_re.sub(' ', event.cust_note.encode('utf-8', 'ignore')).replace('&nbsp;','')
                event_obj.write(cr, uid, [event.id], {'interpreter_note': interpreter_note, 'cust_note': cust_note})
                if count % 1000 == 0:
#                    print "count .......",count
                    cr.commit()
        return True
    
#    def flow_for_unbilled_manually(self, cr, uid, ids, context=None):
#        '''Function to assign mark unbilled the events for a range of dates. '''
#        cr.execute("select id from event where company_id = 6 and event_start_date <= '2015-01-04' and state !='cancel' and event_start_date >= '2014-11-01'")
#        event_list = cr.fetchall()
#        print "event_list++++++++",len(event_list)
#        count1 = 1
#        start_fault = False
#        end_fault = False
#        fault = False
#        min_fault = False
#        event_obj = self.pool.get('event')
##        for event_tup1 in event_list:
##            event_obj.write(cr,uid,event_tup1[0],{'event_end':'2015-01-30 10:00:00'})
#        for event_tup in event_list:
#            event_rec = self.browse(cr, uid, event_tup[0])
#            if event_rec.event_end < event_rec.event_start:
#                event_obj.write(cr, uid, [event_tup[0]],{'event_end':event_rec.event_start})
#            if int(event_rec.event_start_hr) > 12:
#                start = int(event_rec.event_start_hr)-12
#                start_fault = True
#                fault = True
#            if int(event_rec.event_end_hr) > 12:
#                end = int(event_rec.event_end_hr)-12
#                end_fault = True
#                fault = True
#            if fault:
#                if int(event_rec.event_start_hr) == end or start == end :
#                    if int(event_rec.event_start_min)==int(event_rec.event_end_min):
#                        event_end_min = int(event_rec.event_end_min) + 1
#                        min_fault = True
#                if int(event_rec.event_end_hr) == start :
#                    if int(event_rec.event_start_min)==int(event_rec.event_end_min):
#                        event_end_min = int(event_rec.event_end_min) + 1
#                        min_fault = True
#            event_obj.write(cr,uid,event_tup[0],{'event_start_hr':event_rec.event_start_hr if not start_fault else start,'am_pm':event_rec.am_pm if not start_fault else 'pm',
#                                'event_end_hr':event_rec.event_end_hr if not end_fault else end,'am_pm2':event_rec.am_pm2 if not end_fault else 'pm',
#                                'event_end_min':event_rec.event_end_min if not min_fault else event_end_min})
#
#            count1 +=1
#        count = 1
#        for event_tup in event_list:
#            event_obj = self.pool.get('event')
#            event_rec = self.browse(cr,uid,event_tup[0])
#            if event_rec.interpreter_id:
##                print "event_id+++++++++",event.id,event
#                confirm = event_obj.confirm_event(cr, uid, event_tup[0], context=None)
##                print "confirm++++++",count,confirm
#                timesheet = event_obj.enter_timesheet(cr, uid, event_tup[0], context=None)
##                print "timesheet======+++++",count,timesheet
#                count += 1
#        return True
    
    def search_nearby_interpreter(self,cr,uid,ids,context):
#        print "in searchhhhh++++++++++="
        res, dist_dict = [], {}
        interpreter = self.pool.get('res.partner')
        select_obj = self.pool.get('select.interpreter.line')
        history_obj = self.pool.get('interpreter.alloc.history')
        interpreter_ids , visit_ids, categ_rate= [], [], False

        for event in self.browse(cr ,uid ,ids ):
#            print "in event loop++++++++++="
            for interpreter_id in event.interpreter_ids:
                select_obj.unlink(cr ,uid , [interpreter_id.id])
            overlap = False
            history_ids2 = history_obj.search(cr , uid , [('state','in',('confirm','allocated')),('company_id','=',event.company_id.id),
                        ('event_date','=',(datetime.datetime.strptime(str(datetime.datetime.strptime(str(event.event_start),"%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')),"%Y-%m-%d %H:%M:%S")).strftime('%Y-%m-%d'))])
            for history_id in history_ids2:
                history_browse = history_obj.browse( cr ,uid , history_id)
                if (event.event_start > history_browse.event_start and event.event_end < history_browse.event_end) :
                    overlap = True
                elif (event.event_start > history_browse.event_start and event.event_start < history_browse.event_end) :
                    overlap = True
                elif (event.event_end > history_browse.event_start and event.event_end < history_browse.event_end) :
                    overlap = True
                elif event.event_start == history_browse.event_start : #or event.event_end == history_browse.event_end)
                    overlap = True
                elif (history_browse.event_start > event.event_start and history_browse.event_start < event.event_end) :
                    overlap = True
                elif (history_browse.event_end < event.event_end and history_browse.event_end > event.event_start) :
                    overlap = True
#                        elif (event.event_start == history_browse.event_end )or (event.event_end == history_browse.event_start) :
#                            overlap = True
                if overlap:
                    history_ids2.remove(history_id)
                    continue
            location = event.location_id
            event_address = geo_query_address(location.street or False , location.zip or False ,location.city or False, \
                                        location.state_id and location.state_id.name or False, location.country_id and \
                                        location.country_id.name or False)
            int_list=[]
            for history in self.pool.get('interpreter.alloc.history').browse(cr,uid,history_ids2):
                interp_id = history.name
                int_location = history.event_id.location_id
                interp_address = geo_query_address(int_location.street or False , int_location.zip or False ,int_location.city or False, \
                                        int_location.state_id and int_location.state_id.name or False, int_location.country_id and \
                                        int_location.country_id.name or False)
                try:
                    dist_dict = self.get_distance(cr, uid, ids, interp_address ,event_address , context=context)
                except Exception, e :
                    dist_dict['duration'] = ''
                    dist_dict['distance'] = 0
                    pass
                int_list.append((0, 0, {'interpreter_id':interp_id.id ,'event_id':ids[0] ,'state':'draft',
                                                        'duration': dist_dict['duration'] or '','rate':categ_rate,
                                                        'distance':float(float(dist_dict['distance']) * 0.000621371) or 0}))
        return self.write(cr ,uid ,ids , {'interpreter_ids': int_list},context=context)
    
    def send_approval_mail(self, cr, uid, ids, context=None):
        ''' Function to send Approval Mail to Manager '''
        ir_model_data = self.pool.get('ir.model.data')
        if context is None: context = {}
        for event in self.browse(cr, SUPERUSER_ID, ids):
            template_id = ir_model_data.get_object_reference(cr, SUPERUSER_ID, 'bista_iugroup', 'event_approval')[1]
            if template_id:
                self.pool.get('email.template').send_mail(cr, SUPERUSER_ID, template_id, event.id)
        return True
    
    def cover_print(self, cr, uid, ids, context):
        ''' Function to attach the report as attachment from portal '''
        attachment_obj = self.pool.get('ir.attachment')
        for record in self.browse(cr, uid, ids, context=context):
            ir_actions_report = self.pool.get('ir.actions.report.xml')
            #import ipdb;ipdb.set_trace()
            matching_reports = ir_actions_report.search(cr, uid, [('name','=',context.get('report_name'))])
            if matching_reports:
                report = ir_actions_report.browse(cr, uid, matching_reports[0])
                report_service = 'report.' + report.report_name
                service = netsvc.LocalService(report_service)
                (result, format) = service.create(cr, uid, [record.id], {'model': self._name}, context=context)
                eval_context = {'time': time, 'object': record}
                if not report.attachment or not eval(report.attachment, eval_context):
                    # no auto-saving of report as attachment, need to do it manually
                    result = base64.b64encode(result)
                    if context.get('report_name') =='Event Approval Report':
                        file_name='Approval SAF'
                    else:
                        file_name='Verfiying SAF'        
                    #file_name = re.sub(r'[^a-zA-Z0-9_-]', '_', 'Your Report Name')
                    file_name += ".pdf"
                    attachment_id = attachment_obj.create(cr, SUPERUSER_ID,
                        {
                            'name': file_name,
                            'datas': result,
                            'datas_fname': file_name,
                            'res_model': self._name,
                            'res_id': record.id,
                            'type': 'binary'
                        }, context=context)
        return True
    
    def event_confirmation(self, cr, uid, event_id):
        '''Function to approve the event from customer portal '''
        event_ids = self.search(cr, SUPERUSER_ID, [('id','=',event_id),('state','=','unapproved')])
#        import ipdb;ipdb.set_trace()
        if event_ids:
            time = datetime.date.today().strftime('%Y-%m-%d')
            self.write(cr , SUPERUSER_ID, [event_ids[0]], {'state': 'draft','order_note_test':True,'approve_time':time})
            self.cover_print(cr, SUPERUSER_ID,event_ids,context={'report_name':'Event Approval Report'})
            return True
        else:
            return False
        return False

    def event_cancellation(self, cr, uid, event_id):
        '''Function to Cancel the event from customer portal '''
#        print "event_id.....",event_id
        event_ids = self.search(cr, SUPERUSER_ID, [('id','=',event_id),('state','=','unapproved')])
        if event_ids:
            self.write(cr , SUPERUSER_ID, [event_ids[0]], {'state': 'rejected'})
            return True
        else:
#            print "This event is not in Unapproved state"
            return False
        return False
    
    def event_update(self, cr, uid, event_id, date1=False, time1=False, date2=False, time2=False):
        '''Function to update in enter the verified event Time '''
#        print "event_id...date1...time1..date2, time2........",event_id,date1,time1,date2,time2
        if event_id:
            event_ids = self.search(cr, SUPERUSER_ID, [('id','=',event_id)])#,('state','=','non_verified')
            user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid)
            tz, DATETIME_FORMAT = False, "%m-%d-%Y %H:%M:%S"
            if user.tz:
                tz = pytz.timezone(user.tz) or pytz.utc
            else:
                tz = pytz.timezone("US/Pacific") or pytz.utc
            if event_ids:
                date1 = str(date1).replace("/", "-")
                date2 = str(date2).replace("/", "-")
                am_pm = time1[-2:]
                time_str = time1[:-2]
                event_start_hr = str(time_str).split(':')[0]
                event_start_min = str(time_str).split(':')[1]
                if am_pm and am_pm == 'pm':
                    if event_start_hr < 12:
                        event_start_hr += 12
                if am_pm and am_pm == 'am':
                    if event_start_hr == 12:
                        event_start_hr = 0
                if event_start_hr == 24: # for the 24 hour format
                    event_start_hr = 23
                    event_start_min = 59
                event_start = str(date1) + ' ' + str(event_start_hr) + ':' + str(event_start_min) + ':00'
                # get localized dates
                
                local_dt = tz.localize(datetime.datetime.strptime(event_start,DATETIME_FORMAT), is_dst=None)
                event_start = local_dt.astimezone (pytz.utc).strftime (DATETIME_FORMAT)
                am_pm2 = time2[-2:]
                time_str2 = time2[:-2]
                event_end_hr = str(time_str2).split(':')[0]
                event_end_min = str(time_str2).split(':')[1]
                if am_pm2 and am_pm2 == 'pm':
                    if event_end_hr < 12:
                        event_end_hr += 12
                if am_pm2 and am_pm2 == 'am':
                    if event_end_hr == 12:
                        event_end_hr = 0
                if event_end_hr == 24: # for the 24 hour format
                    event_end_hr = 23
                    event_end_min = 59
                event_end = str(date2) + ' ' + str(event_end_hr) + ':' + str(event_end_min) + ':' + '00'
                # get localized dates
                local_dt2 = tz.localize(datetime.datetime.strptime(event_end,DATETIME_FORMAT), is_dst=None)
                event_end = local_dt2.astimezone (pytz.utc).strftime (DATETIME_FORMAT)
                time=datetime.date.today().strftime('%Y-%m-%d')
                self.write(cr , uid, [event_ids[0]], {'verify_state': 'verified','verified_event_start': event_start,'verified_event_end': event_end,'verify_time':time})
                self.cover_print(cr, SUPERUSER_ID, [event_ids[0]] ,context={'report_name':'Event completion Report'})
                return True
            else:
                return False
        else:
            return False
        return False
    
    def event_verify(self, cr, uid, event_id):
        '''Function to verify the event Time '''
        event_ids = self.search(cr, SUPERUSER_ID, [('id','=',event_id)])#,('state','=','non_verified')
        if event_ids:
            self.write(cr , SUPERUSER_ID, event_ids[0], {'verify_state': 'verified'})
            return True
        else:
#            print "This event is not in Non Verified state"
            return False
        return False

    def view_event_billing_form(self, cr, uid, ids, context=None):
        '''Function to jump onto billing Form Screen for accounting user '''
        if context is None: context = {}
        if isinstance(ids, (int,long)): ids = [ids]
        cur_obj = self.browse( cr , uid, ids[0])
        mod_obj = self.pool.get('ir.model.data')
        res = mod_obj.get_object_reference(cr, uid, 'bista_iugroup', 'view_billing_form')
        res_id = res and res[1] or False,
        context.update({'event_id' : ids[0] })
        val = {
            'company_id': cur_obj.company_id and cur_obj.company_id.id or False,
            'name':'Billing Form for '+ str(cur_obj.name),
            'event_id': ids[0],
        }
        billing_form_id = self.pool.get('billing.form').create(cr, uid, val, context=context)
        return {
            'name': _('Billing Form'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res_id[0]],
            'res_model': 'billing.form',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': billing_form_id or False,
        }

    def action_mail_send(self, cr, uid, ids, obj , model, template_id, context=None):
        ''' This function opens a window to compose an email, with the edi event template message loaded by default '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        if not template_id:
            template_id = False
        ir_model_data = self.pool.get('ir.model.data')
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(context)
        ctx.update({
            'default_model': model,
            'default_res_id': obj.id,
            'event_id' : obj.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
    
    def assign_interpeter_manual(self, cr, uid, ids, context):
        ''' Function to offer job to interpreter manually '''
        res, dist_dict, overlap, int_line_id = [], {}, False, False
        block_inter_ids , visit_ids, categ_rate, rate = [], [], 0.0, False
        history_obj = self.pool.get('interpreter.alloc.history')
        select_obj = self.pool.get('select.interpreter.line')
        event = self.browse(cr ,uid ,ids[0])
        if event.no_editable:
            print "****************************************************",event,event.no_editable
            raise osv.except_osv(_('Error!'), _("Operation is going on current event! \n Please wait for a moment..."))
        category = event.language_id and event.language_id.lang_group or False
        if event.multi_type == '1':
            if event.state not in ['unapproved','draft','scheduled'] and len(event.assigned_interpreters) >= 1:
                raise osv.except_osv(_('Warning!'),_('Interpreter is already assigned to this event.'))
        if event.multi_type == '2':
            if event.state not in ['unapproved','draft','scheduled'] and len(event.assigned_interpreters) >= 2:
                raise osv.except_osv(_('Warning!'),_('Interpreters are already assigned to this event.'))
        
        if event.state in ('unbilled','invoiced','confirmed','done','cancel'):
            raise osv.except_osv(_('Warning!'),_('You can not assign interpreter at this stage of event'))
        if not event.interpreter_id2:
            raise osv.except_osv(_('Warning!'),_('Interpreter is not selected to assign!'))
        if not category:
            raise osv.except_osv(_('Warning!'),_('Please select Language Group in language form.'))
        lang_flag = False
        for lang in event.interpreter_id2.language_lines:
            if lang.name and lang.name.id == event.language_id.id:
                lang_flag = True
        if lang_flag == False:
            raise osv.except_osv(_('Warning!'),_("Selected interpreter does not interprete this language,Please add this languge to Interpreter's record first."))
        if event.partner_id.block_inter_ids:
            for inter in event.partner_id.block_inter_ids:
                block_inter_ids.append(inter.id)
        if event.interpreter_id2.id in block_inter_ids:
            raise osv.except_osv(_('Warning!'),_('This Interpreters is in Blocklist for this Customer.'))
        all_interpreter_list = event.interpreter_ids + event.interpreter_ids2
        for select_line in all_interpreter_list:
            if select_line.interpreter_id:
                if select_line.state in ('draft','voicemailsent') and select_line.interpreter_id.id == event.interpreter_id2.id:
                    raise osv.except_osv(_('Warning!'),_('Selected interpreter is already present in the list of interpreters, Please process from there!'))
        overlap = False
        if not event.interpreter_id2.is_agency:
#            history_ids2 = history_obj.search(cr , SUPERUSER_ID, [('name','=',event.interpreter_id2.id),('state','in',('confirm','allocated')),('company_id','=',event.company_id.id),
#                                   ('event_date','=',(datetime.datetime.strptime(str(datetime.datetime.strptime(str(event.event_start),"%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')),"%Y-%m-%d %H:%M:%S")).strftime('%Y-%m-%d'))])
#            history_ids2 = self.search(cr , SUPERUSER_ID, [('name','=',event.interpreter_id2.id),('state','in',('confirm','allocated')),('company_id','=',event.company_id.id),('event_start_date','=',event.event_start_date)])
#            if event.id in history_ids2:
#                history_ids2.remove(event.id)
            history_ids2 = history_obj.search(cr , SUPERUSER_ID, [('name','=',event.interpreter_id2.id),('state','in',('confirm','allocated')),('company_id','=',event.company_id.id),('cancel_date','=',False),
                                   ('event_start_date','=',event.event_start_date)])
            for history_browse in history_obj.browse( cr , SUPERUSER_ID, history_ids2):
                if (event.event_start > history_browse.event_start and event.event_end < history_browse.event_end) :
                    overlap = True
                elif (event.event_start > history_browse.event_start and event.event_start < history_browse.event_end) :
                    overlap = True
                elif (event.event_end > history_browse.event_start and event.event_end < history_browse.event_end) :
                    overlap = True
                elif (event.event_start == history_browse.event_start or event.event_end == history_browse.event_end) :
                    overlap = True
                elif (history_browse.event_start > event.event_start and history_browse.event_start < event.event_end) :
                    overlap = True
                elif (history_browse.event_end < event.event_end and history_browse.event_end > event.event_start) :
                    overlap = True
    #            elif (event.event_start == history_browse.event_end ):
    #                overlap = True
                if overlap:
                    raise osv.except_osv(_('Warning!'),_('This Interpreter is already appointed for another Event!'))
        if event.event_purpose:
            for rate_id in event.interpreter_id2.rate_ids:
                if rate_id.rate_type == event.event_purpose:
                    rate = rate_id
            if category and rate:
                if category == 'spanish_regular':
                    categ_rate = rate.spanish_regular
                elif category == 'spanish_licenced':
                    categ_rate = rate.spanish_licenced
                elif category == 'spanish_certified':
                    categ_rate = rate.spanish_certified
                elif category == 'exotic_regular':
                    categ_rate = rate.exotic_regular
                elif category == 'exotic_certified':
                    categ_rate = rate.exotic_certified
                elif category == 'exotic_middle':
                    categ_rate = rate.exotic_middle
                elif category == 'exotic_high':
                    categ_rate = rate.exotic_high
            if rate and categ_rate == 0.0:
                categ_rate = rate.default_rate
        int_line_id = select_obj.create(cr ,uid ,{'interpreter_id': event.interpreter_id2.id,'rate':categ_rate,'event_id':ids[0],'visited':False,'visited_date':False,
                                                'state': 'draft' ,'voicemail_msg':''})
        res = self.pool.get('event').write(cr , uid, [event.id], {'state': 'scheduled','interpreter_ids2': [(4, int_line_id)]})
        self.pool.get('event').write(cr , uid, [event.id],{'interpreter_id2': False})
        voicemail_result = select_obj.leave_voicemail(cr, uid, [int_line_id], context)
#         self.pool.get('event').send_sms_to_interpreters(cr,uid,ids,context={'job_offer': True})
        return voicemail_result
    
    def assign_translator_manual(self, cr, uid, ids, context):
        ''' This function updates or assigns translator manually in the event form and send mail'''
        if context is None: context = {} 
        context['translator'] = True
        res= []
        mod_obj = self.pool.get('ir.model.data')
        event = self.browse(cr ,uid ,ids[0])
        if event.state in ('unbilled','invoiced','confirmed','done','cancel'):
            raise osv.except_osv(_('Warning!'),_('You can not assign Translator at this stage of event'))
        if event.translator_id2:
            for select_line in event.translator_ids:
                if select_line.translator_id:
                    if select_line.state in ('draft','voicemailsent') and select_line.translator_id.id == event.translator_id2.id:
                        raise osv.except_osv(_('Warning!'),_('Selected translator is already present in the list of translators, Please process from there!'))
            assign_history_id = event.translation_assignment_history_id
            if assign_history_id:
                self.pool.get('assign.translator.history').write(cr,uid,[assign_history_id.id],{'state':'removed'})
            res = self.pool.get('event').write(cr ,uid , [event.id],{'translator_id': event.translator_id2 and event.translator_id2.id or False,
                                'state': 'allocated','interpreter_id2': False,'schedule_event_time':time.strftime('%Y-%m-%d %H:%M:%S')})
            history_id = self.pool.get('assign.translator.history').create(cr ,uid ,{'partner_id': event.partner_id and event.partner_id.id or False,'name':event.translator_id2 and event.translator_id2.id or False,
                'event_id': event.id,'event_date': event.event_date ,'event_start': event.event_start,'event_end':event.event_end,'state':'assign','company_id': event.company_id and event.company_id.id or False,
                'schedule_event_time': time.strftime('%Y-%m-%d %H:%M:%S')})
            self.pool.get('event').write(cr, uid, [event.id], {'translation_assignment_history_id':history_id})
            template_id = mod_obj.get_object_reference(cr, uid, 'bista_iugroup', 'event_allocation_translator')[1]
            if template_id:
                res = self.action_mail_send( cr, uid, ids , event, 'event', template_id, context=context)
            self.pool.get('event').write(cr ,uid , [event.id],{'translator_id2': False})
        else:
            raise osv.except_osv(_('Warning!'),_('Please select translator to assign!'))
        return res

    def assign_transporter_manual(self, cr, uid, ids, context):
        ''' This function updates or assigns transporter manually in the event form and send mail'''
        if context is None: context = {}
        context['transporter'] = True
        res = []
        mod_obj = self.pool.get('ir.model.data')
        event = self.browse(cr ,uid ,ids[0])
        if event.state in ('unbilled','invoiced','confirmed','done','cancel'):
            raise osv.except_osv(_('Warning!'),_('You can not assign Transporter at this stage of event'))
        if event.transporter_id2:
            for select_line in event.transporter_ids:
                if select_line.transporter_id:
                    if select_line.state in ('draft','voicemailsent') and select_line.transporter_id.id == event.transporter_id2.id:
                        raise osv.except_osv(_('Warning!'),_('Selected Transporter is already present in the list of Transporters, Please process from there!'))
            history_id2 = event.history_id2
            if history_id2:
                self.pool.get('transporter.alloc.history').write(cr,uid,[history_id2.id],{'state':'cancel','cancel_date':time.strftime('%Y-%m-%d %H:%M:%S')})
            res = self.pool.get('event').write(cr ,uid , [event.id],{'transporter_id':event.transporter_id2 and event.transporter_id2.id or False,
                                'state':'allocated','transporter_id2': False,'schedule_event_time':time.strftime('%Y-%m-%d %H:%M:%S')})
            history_id=self.pool.get('transporter.alloc.history').create(cr ,uid ,{'partner_id':event.partner_id and event.partner_id.id or False,'name':event.transporter_id2 and event.transporter_id2.id or False,
                'event_id':event.id,'event_date':event.event_date ,'event_start':event.event_start,'event_end':event.event_end,'state':'allocated','company_id': event.company_id and event.company_id.id or False,
                'allocate_date':time.strftime('%Y-%m-%d %H:%M:%S')})
            self.pool.get('event').write(cr,uid,[event.id],{'history_id2':history_id})
            template_id = mod_obj.get_object_reference(cr, uid, 'bista_iugroup', 'event_allocation_transporter')[1]
            if template_id:
                res = self.action_mail_send( cr, uid, ids , event, 'event', template_id, context=context)
            self.pool.get('event').write(cr ,uid , [event.id],{'transporter_id2': False})
        else:
            raise osv.except_osv(_('Warning!'),_('You must select a Transporter to be assigned!'))
        return res
    
    def open_events_for_interpreter(self, cr, uid, ids, context=None):
        ''' Function used in server action to show Language events for customer and interpreter portal'''
        event = self.pool.get('event')
        if context is None: context = {}
        context.update({'state':'unapproved'})
        day_type , result ,event_ids = '', False , []
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        day_type = context.get('day_type',False)
        partner_type = context.get('partner_type',False)
	result, tz = False, False
        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid)
        if partner_type == 'customer':
            result = mod_obj.get_object_reference(cr, uid, 'bista_iugroup', 'action_event_customer_form_language')
        else:
            result = mod_obj.get_object_reference(cr, uid, 'bista_iugroup', 'action_event_user_form_language')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.utc
        date = pytz.utc.localize(datetime.datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),DATETIME_FORMAT), is_dst=None)
        local_date = datetime.datetime.strptime(date.astimezone(tz).strftime(DATETIME_FORMAT), DATETIME_FORMAT).strftime('%Y-%m-%d')
        if partner_type == 'customer':
            if day_type == 'today':
                event_ids = event.search(cr, uid, [('event_type','in', ['language','lang_trans']) ,\
                                ('event_start_date','=',local_date)], context=context)
            if day_type == 'past':
                event_ids = event.search(cr, uid, [('event_type','in', ['language','lang_trans']) ,\
                                ('event_start_date','<',local_date)], context=context)
            if day_type == 'future':
                event_ids = event.search(cr, uid, [('event_type','in', ['language','lang_trans']) ,\
                                ('event_start_date','>',local_date)], context=context)
        else:
#            print "Today time.........",time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
#            print "today Date...",(datetime.datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),DATETIME_FORMAT)).strftime('%Y-%m-%d')
            if day_type == 'today':
                event_ids = event.search(cr, uid, [('event_type','in', ['language','lang_trans']) ,('state','in', ('allocated','unauthorize','confirmed')) ,\
                                ('event_start_date','=',local_date)], context=context)
            if day_type == 'past':
                event_ids = event.search(cr, uid, [('event_type','in', ['language','lang_trans']) ,('state','not in', ('draft','unauthorize','scheduled')) ,\
                                ('event_start_date','<', local_date), ('state', '!=', 'cancel')], context=context)
            if day_type == 'future':
                event_ids = event.search(cr, uid, [('event_type','in', ['language','lang_trans']) ,('state','in', ('allocated','unauthorize','confirmed')) ,\
                                ('event_start_date','>',local_date)], context=context)
#        else:
#            event_ids = event.search(cr, uid, [('zone_id','in', zone_ids),('event_type','=',event_type),  \
#                                            ('event_start_date','=',(datetime.datetime.now()).strftime('%Y-%m-%d'))], context=context)
        #print "event_ids...........",len(event_ids)
        result['context'] = context
        result['domain'] = "[('id','in',["+','.join(map(str, event_ids))+"])]"
        return result
    
    def open_current_year_events(self, cr, uid, ids, context=None):
        '''Function used in server action to open current year language Events '''
        event = self.pool.get('event')
        if context is None: context = {}
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        result = False
        event_type = context.get('event_type',False)
        if event_type == 'language':
            result = mod_obj.get_object_reference(cr, uid, 'bista_iugroup', 'action_lang_event_form_all')
        elif event_type == 'transport':
            result = mod_obj.get_object_reference(cr, uid, 'bista_lang_transport', 'action_event_form_transport')
        elif event_type == 'translation':
            result = mod_obj.get_object_reference(cr, uid, 'bista_iugroup', 'action_translation_form')
        elif event_type == 'lang_trans':
            result = mod_obj.get_object_reference(cr, uid, 'bista_lang_transport', 'action_event_form_referral')
        else :
            result = mod_obj.get_object_reference(cr, uid, 'bista_iugroup', 'action_lang_event_form_all')

        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        now = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        tm_tuple = datetime.datetime.strptime(now,'%Y-%m-%d').timetuple()
        year = tm_tuple.tm_year
        start_date = str(year) + '-01-01'
        end_date = str(year) + '-12-31'
        event_ids = []
        event_ids = event.search(cr, uid, [('event_type','=', 'language'),('event_date','>=',start_date),  \
                                        ('event_date','<=',end_date)], context=context)

        result['context'] = context
        result['domain'] = "[('id','in',["+','.join(map(str, event_ids))+"])]"
        return result

    def open_three_day_events(self, cr, uid, ids, context=None):
        ''' Function to show next 72 hour unscheduled  and Job Offered Events using Server Action '''
        event = self.pool.get('event')
        if context is None: context = {}
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        event_type = context.get('event_type',False)
	result = False
        if event_type == 'language':
            result = mod_obj.get_object_reference(cr, uid, 'bista_iugroup', 'action_lang_event_form_all')
        elif event_type == 'transport':
            result = mod_obj.get_object_reference(cr, uid, 'bista_lang_transport', 'action_event_form_transport')
        elif event_type == 'translation':
            result = mod_obj.get_object_reference(cr, uid, 'bista_iugroup', 'action_translation_form')
        elif event_type == 'lang_trans':
            result = mod_obj.get_object_reference(cr, uid, 'bista_lang_transport', 'action_event_form_referral')
        else :
            result = mod_obj.get_object_reference(cr, uid, 'bista_iugroup', 'action_event_all_type')
        
        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid)
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.utc
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        oneday_events = (datetime.datetime.now() + relativedelta.relativedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')
        oneday_events = datetime.datetime.strptime(str(datetime.datetime.strptime(str(oneday_events),"%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')),"%Y-%m-%d %H:%M:%S")
        sunday_date = (datetime.datetime.today() + relativedelta.relativedelta(days=6 - datetime.datetime.date(datetime.datetime.today()).weekday())).strftime('%Y-%m-%d %H:%M:%S')
        sunday_date = datetime.datetime.strptime(str(datetime.datetime.strptime(str(sunday_date),"%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')),"%Y-%m-%d %H:%M:%S")
        saturday_date = (sunday_date - datetime.timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
        saturday_date = datetime.datetime.strptime(str(datetime.datetime.strptime(str(saturday_date),"%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')),"%Y-%m-%d %H:%M:%S")
        if  oneday_events.strftime('%Y-%m-%d') == saturday_date.strftime('%Y-%m-%d') or  oneday_events.strftime('%Y-%m-%d') == sunday_date.strftime('%Y-%m-%d'):
            start_date = (oneday_events + relativedelta.relativedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')
        else:
            start_date = (datetime.datetime.now() + datetime.timedelta(hours=48)).strftime('%Y-%m-%d %H:%M:%S')
#        print"start_date",start_date
        start_date1 = datetime.datetime.strptime(str(datetime.datetime.strptime(str(start_date),"%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')),"%Y-%m-%d %H:%M:%S")
        twoday  = (start_date1 + relativedelta.relativedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        twoday = datetime.datetime.strptime(str(datetime.datetime.strptime(str(twoday),"%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')),"%Y-%m-%d %H:%M:%S")
        end_sunday_date  = (oneday_events + relativedelta.relativedelta(days=6 - datetime.datetime.date(datetime.datetime.today()).weekday())).strftime('%Y-%m-%d %H:%M:%S')
        end_sunday_date = datetime.datetime.strptime(str(datetime.datetime.strptime(str(end_sunday_date),"%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')),"%Y-%m-%d %H:%M:%S")
        end_saturday_date = (end_sunday_date - datetime.timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
        end_saturday_date = datetime.datetime.strptime(str(datetime.datetime.strptime(str(end_saturday_date),"%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')),"%Y-%m-%d %H:%M:%S")
        
        if  twoday.strftime('%Y-%m-%d') in  (end_saturday_date.strftime('%Y-%m-%d') , end_sunday_date.strftime('%Y-%m-%d')):
            end_date = ( twoday + relativedelta.relativedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')
        else:
            end_date  = ( start_date1 + relativedelta.relativedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        event_ids = event.search(cr, uid, [('state','in', ('draft','scheduled')),('event_type','=', event_type),('event_start','>=',start_date),  \
                                            ('event_start','<=',end_date)], context=context)
        
        result['context'] = context
        result['domain'] = "[('id','in',["+','.join(map(str, event_ids))+"])]"
        return result
    
    def open_two_day_events(self, cr, uid, ids, context=None):
        ''' Function to show next 48 hour unscheduled  and Job Offered Events using Server Action '''
        event = self.pool.get('event')
        if context is None:
            context = {}
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        event_type=context.get('event_type',False)
	result = False
        if event_type == 'language':
            result = mod_obj.get_object_reference(cr, uid, 'bista_iugroup', 'action_lang_event_form_all')
        elif event_type == 'transport':
            result = mod_obj.get_object_reference(cr, uid, 'bista_lang_transport', 'action_event_form_transport')
        elif event_type == 'translation':
            result = mod_obj.get_object_reference(cr, uid, 'bista_iugroup', 'action_translation_form')
        elif event_type == 'lang_trans':
            result = mod_obj.get_object_reference(cr, uid, 'bista_lang_transport', 'action_event_form_referral')
        else :
            result = mod_obj.get_object_reference(cr, uid, 'bista_iugroup', 'action_event_all_type')

        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        
        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid)
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.utc
        event_ids = []
        oneday_events = (datetime.datetime.now() + relativedelta.relativedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        oneday_events = datetime.datetime.strptime(str(datetime.datetime.strptime(str(oneday_events),"%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')),"%Y-%m-%d %H:%M:%S")
        sunday_date = (datetime.datetime.today() + relativedelta.relativedelta(days=6 - datetime.datetime.date(datetime.datetime.today()).weekday())).strftime('%Y-%m-%d %H:%M:%S')
        sunday_date = datetime.datetime.strptime(str(datetime.datetime.strptime(str(sunday_date),"%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')),"%Y-%m-%d %H:%M:%S")
        saturday_date = (sunday_date - datetime.timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
        saturday_date = datetime.datetime.strptime(str(datetime.datetime.strptime(str(saturday_date),"%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')),"%Y-%m-%d %H:%M:%S")
        
        if  oneday_events.strftime('%Y-%m-%d') == saturday_date.strftime('%Y-%m-%d') or  oneday_events.strftime('%Y-%m-%d') == sunday_date.strftime('%Y-%m-%d'):
            start_date = (oneday_events + relativedelta.relativedelta(hours=48)).strftime('%Y-%m-%d %H:%M:%S')
        else:
            start_date = (datetime.datetime.now() + datetime.timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
#        print"start_date",start_date
        start_date1 = datetime.datetime.strptime(str(datetime.datetime.strptime(str(start_date),"%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')),"%Y-%m-%d %H:%M:%S")
        twoday  = (start_date1 + relativedelta.relativedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        twoday = datetime.datetime.strptime(str(datetime.datetime.strptime(str(twoday),"%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')),"%Y-%m-%d %H:%M:%S")
        end_sunday_date  = (oneday_events + relativedelta.relativedelta(days=6 - datetime.datetime.date(datetime.datetime.today()).weekday())).strftime('%Y-%m-%d %H:%M:%S')
        end_sunday_date = datetime.datetime.strptime(str(datetime.datetime.strptime(str(end_sunday_date),"%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')),"%Y-%m-%d %H:%M:%S")
        end_saturday_date = (end_sunday_date - datetime.timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
        end_saturday_date = datetime.datetime.strptime(str(datetime.datetime.strptime(str(end_saturday_date),"%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')),"%Y-%m-%d %H:%M:%S")
        if  twoday.strftime('%Y-%m-%d') in  (end_saturday_date.strftime('%Y-%m-%d') , end_sunday_date.strftime('%Y-%m-%d')):
            end_date = ( twoday + relativedelta.relativedelta(hours=48)).strftime('%Y-%m-%d %H:%M:%S')
        else:
            end_date  = ( start_date1 + relativedelta.relativedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
        event_ids = event.search(cr, uid, [('state','in', ('draft','scheduled')),('event_type','=', event_type),('event_start','>=',start_date),  \
                                            ('event_start','<=',end_date)], context=context)

        result['context'] = context
        result['domain'] = "[('id','in',["+','.join(map(str, event_ids))+"])]"
        return result

    def open_current_day_events(self, cr, uid, ids, context=None):
        ''' Function to show next 24 hour unscheduled  and Job Offered Events using Server Action '''
        event = self.pool.get('event')
        if context is None:
            context = {}
        event_type=context.get('event_type',False)
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        result = False
        if event_type == 'language':
            result = mod_obj.get_object_reference(cr, uid, 'bista_iugroup', 'action_lang_event_form_all')
        elif event_type == 'transport':
            result = mod_obj.get_object_reference(cr, uid, 'bista_lang_transport', 'action_event_form_transport')
        elif event_type == 'translation':
            result = mod_obj.get_object_reference(cr, uid, 'bista_iugroup', 'action_translation_form')
        elif event_type == 'lang_trans':
            result = mod_obj.get_object_reference(cr, uid, 'bista_lang_transport', 'action_event_form_referral')
        else :
            result = mod_obj.get_object_reference(cr, uid, 'bista_iugroup', 'action_event_all_type')

        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        event_ids = []
        
        # Changes for day-light
        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid)
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.utc
        oneday_events = (datetime.datetime.now() + relativedelta.relativedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        oneday_events = datetime.datetime.strptime(str(datetime.datetime.strptime(str(oneday_events),"%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')),"%Y-%m-%d %H:%M:%S")
        sunday_date = (datetime.datetime.now() + relativedelta.relativedelta(days=6 - datetime.datetime.date(datetime.datetime.today()).weekday())).strftime('%Y-%m-%d %H:%M:%S')
        sunday_date = datetime.datetime.strptime(str(datetime.datetime.strptime(str(sunday_date),"%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')),"%Y-%m-%d %H:%M:%S")
        saturday_date = (sunday_date - datetime.timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
        saturday_date = datetime.datetime.strptime(str(datetime.datetime.strptime(str(saturday_date),"%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')),"%Y-%m-%d %H:%M:%S")
        if  oneday_events.strftime('%Y-%m-%d') == saturday_date.strftime('%Y-%m-%d') or oneday_events.strftime('%Y-%m-%d') == sunday_date.strftime('%Y-%m-%d'):
            end_date = (oneday_events + relativedelta.relativedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')
        else:
            end_date = (datetime.datetime.now() + relativedelta.relativedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        event_ids = event.search(cr, uid, [('state','in', ('draft','scheduled')),('event_type','=', event_type),('event_start','>=',(datetime.datetime.now()).strftime('%Y-%m-%d %H:%M:%S')),  \
                                        ('event_start','<=',end_date)], context=context)
#         for each in event_ids:
#             print self.browse(cr,uid,each).name
#             print self.browse(cr,uid,each).event_start
        result['context'] = context
        result['domain'] = "[('id','in',["+','.join(map(str, event_ids))+"])]"
        return result

    def open_current_day_all_lang_events(self, cr, uid, ids, context=None):
        ''' Function used in server action to show Language events only for current day '''
        event = self.pool.get('event')
        if context is None:
            context = {}
        event_type , result ,event_ids = '', False , []
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        event_type=context.get('event_type',False)
	result = False
        if event_type == 'language':
            result = mod_obj.get_object_reference(cr, uid, 'bista_iugroup', 'action_lang_event_form_all')
        elif event_type == 'transport':
            result = mod_obj.get_object_reference(cr, uid, 'bista_lang_transport', 'action_event_form_transport')
        elif event_type == 'translation':
            result = mod_obj.get_object_reference(cr, uid, 'bista_iugroup', 'action_translation_form')
        elif event_type == 'lang_trans':
            result = mod_obj.get_object_reference(cr, uid, 'bista_lang_transport', 'action_event_form_referral')
        else :
            result = mod_obj.get_object_reference(cr, uid, 'bista_iugroup', 'action_event_all_type')
        
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid)
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.utc
        date = pytz.utc.localize(datetime.datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),DATETIME_FORMAT), is_dst=None)
        local_date = datetime.datetime.strptime(date.astimezone(tz).strftime(DATETIME_FORMAT), DATETIME_FORMAT)
        event_ids = event.search(cr, uid, [('event_type','=', event_type) ,\
                                            ('event_start_date','=',(local_date).strftime('%Y-%m-%d'))], context=context)
        
        result['context'] = context
        result['domain'] = "[('id','in',["+','.join(map(str, event_ids))+"])]"
        return result

    def open_next_3days_allocated_lang_events(self, cr, uid, ids, context=None):
        ''' Function used in server action to show Scheduled Language events only for next 3 days.'''
        event = self.pool.get('event')
        if context is None:
            context = {}
        event_type = context.get('event_type',False)
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
	result = False
        if event_type == 'language':
            result = mod_obj.get_object_reference(cr, uid, 'bista_iugroup', 'action_lang_event_form_all')
        elif event_type == 'transport':
            result = mod_obj.get_object_reference(cr, uid, 'bista_lang_transport', 'action_event_form_transport')
        elif event_type == 'translation':
            result = mod_obj.get_object_reference(cr, uid, 'bista_iugroup', 'action_translation_form')
        elif event_type == 'lang_trans':
            result = mod_obj.get_object_reference(cr, uid, 'bista_lang_transport', 'action_event_form_referral')
        else :
            result = mod_obj.get_object_reference(cr, uid, 'bista_iugroup', 'action_event_all_type')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        event_ids = []
        oneday_events = (datetime.datetime.now() + relativedelta.relativedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        oneday_events = datetime.datetime.strptime(str(datetime.datetime.strptime(str(oneday_events),"%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')),"%Y-%m-%d %H:%M:%S")
        sunday_date = (datetime.datetime.now() + relativedelta.relativedelta(days=6 - datetime.datetime.date(datetime.datetime.today()).weekday())).strftime('%Y-%m-%d %H:%M:%S')
        sunday_date = datetime.datetime.strptime(str(datetime.datetime.strptime(str(sunday_date),"%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')),"%Y-%m-%d %H:%M:%S")

        saturday_date = (sunday_date - datetime.timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
        saturday_date = datetime.datetime.strptime(str(datetime.datetime.strptime(str(saturday_date),"%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')),"%Y-%m-%d %H:%M:%S")

        if  oneday_events.strftime('%Y-%m-%d') == saturday_date.strftime('%Y-%m-%d') or oneday_events.strftime('%Y-%m-%d') == sunday_date.strftime('%Y-%m-%d'):
            end_date = (oneday_events + relativedelta.relativedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')
        else:
            end_date = (datetime.datetime.now() + datetime.timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
        event_ids = event.search(cr, uid, [('state','=', 'allocated'),('event_type','=', event_type),('event_start','>=',(datetime.datetime.now()).strftime('%Y-%m-%d %H:%M:%S')),  \
                                            ('event_start','<=',end_date)], context=context)
        result['context'] = context
        result['domain'] = "[('id','in',["+','.join(map(str, event_ids))+"])]"
        return result


##### ++++++++unauthorize Events ++++++++++++++++######
    
    def open_next_unauthorize_lang_events(self, cr, uid, ids, context=None):
        ''' Function used in server action to show Unauthorize events only for next 1 days.'''
        event = self.pool.get('event')
        if context is None:
            context = {}
        event_type = context.get('event_type',False)
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
	result = False
        if event_type == 'language':
            result = mod_obj.get_object_reference(cr, uid, 'bista_iugroup', 'action_lang_event_form_all')
        elif event_type == 'transport':
            result = mod_obj.get_object_reference(cr, uid, 'bista_lang_transport', 'action_event_form_transport')
        elif event_type == 'translation':
            result = mod_obj.get_object_reference(cr, uid, 'bista_iugroup', 'action_translation_form')
        elif event_type == 'lang_trans':
            result = mod_obj.get_object_reference(cr, uid, 'bista_lang_transport', 'action_event_form_referral')
        else :
            result = mod_obj.get_object_reference(cr, uid, 'bista_iugroup', 'action_event_all_type')

        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        event_ids = []
        
        event_ids = event.search(cr, uid, [('state','=', 'unauthorize'),('event_type','=', event_type),('event_start','>=',(datetime.datetime.now()).strftime('%Y-%m-%d %H:%M:%S'))], context=context)
        result['context'] = context
        result['domain'] = "[('id','in',["+','.join(map(str, event_ids))+"])]"
        return result

    def open_next_confirmed_events(self, cr, uid, ids, context=None):
        ''' Function used in server action to show Confirm events only for next 1 days , considering saturday and sunday .'''
        event = self.pool.get('event')
        if context is None:
            context = {}
        event_type = context.get('event_type',False)
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
	result = False
        if event_type == 'language':
            result = mod_obj.get_object_reference(cr, uid, 'bista_iugroup', 'action_lang_event_form_all')
        elif event_type == 'transport':
            result = mod_obj.get_object_reference(cr, uid, 'bista_lang_transport', 'action_event_form_transport')
        elif event_type == 'translation':
            result = mod_obj.get_object_reference(cr, uid, 'bista_iugroup', 'action_translation_form')
        elif event_type == 'lang_trans':
            result = mod_obj.get_object_reference(cr, uid, 'bista_lang_transport', 'action_event_form_referral')
        else :
            result = mod_obj.get_object_reference(cr, uid, 'bista_iugroup', 'action_event_all_type')

        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        event_ids, end_date = [] , False
        oneday_events = (datetime.datetime.now() + relativedelta.relativedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        oneday_events = datetime.datetime.strptime(str(datetime.datetime.strptime(str(oneday_events),"%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')),"%Y-%m-%d %H:%M:%S")
        sunday_date = (datetime.datetime.now() + relativedelta.relativedelta(days=6 - datetime.datetime.date(datetime.datetime.today()).weekday())).strftime('%Y-%m-%d %H:%M:%S')
        sunday_date = datetime.datetime.strptime(str(datetime.datetime.strptime(str(sunday_date),"%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')),"%Y-%m-%d %H:%M:%S")
        saturday_date = (sunday_date - datetime.timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
        saturday_date = datetime.datetime.strptime(str(datetime.datetime.strptime(str(saturday_date),"%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')),"%Y-%m-%d %H:%M:%S")
        if  oneday_events.strftime('%Y-%m-%d') == saturday_date.strftime('%Y-%m-%d') or oneday_events.strftime('%Y-%m-%d') == sunday_date.strftime('%Y-%m-%d'):
            end_date = (oneday_events + relativedelta.relativedelta(days=2)).strftime('%Y-%m-%d')
        else:
            end_date = (datetime.datetime.now() + datetime.timedelta(hours=24)).strftime('%Y-%m-%d')
        event_ids = event.search(cr, uid, [('state','=', 'confirmed'),('event_type','=', event_type),('event_start','>=',(datetime.datetime.now()).strftime('%Y-%m-%d %H:%M:%S')),  \
                                               ('event_date','<=',end_date)], context=context)
        result['context'] = context
        result['domain'] = "[('id','in',["+','.join(map(str, event_ids))+"])]"
        return result

    def _check_permissions(self, cr, uid, id, context=None):
        ''' Function to check for sms sending function access rights'''
        cr.execute('select * from res_smsserver_group_rel where sid=%s and uid=%s' % (id, uid))
        data = cr.fetchall()
        if len(data) <= 0:
            return False
        return True

    def _prepare_smsclient_queue(self, cr, uid, data, name,gateway ,msg , context=None):
        return {
            'name': name,
            'gateway_id': gateway.id,
            'state': 'draft',
            'mobile': str(data.phone).replace("+", ""),
            'msg': msg,
            'validity': gateway.validity,
            'classes': gateway.classes,
            'deffered': gateway.deferred,
            'priorirty': gateway.priority,
            'coding': gateway.coding,
            'tag': gateway.tag,
            'nostop': gateway.nostop,
        }

    def _send_message(self, cr, uid, data, gway , msg , context=None):
        ''' function used in sending sms on event confirmation '''
        if context is None:
            context = {}
        if gway:
            gateway = self.pool.get('sms.smsclient').browse(cr ,uid ,gway , context=context)
            if not self._check_permissions(cr, uid, gateway.id, context=context):
                raise osv.except_osv(_('Permission Error!'), _('You have no permission to access %s ') % (gateway.name,))
            url = gateway.url
            name = url
            if gateway.method == 'http':
                prms = {}
                for p in gateway.property_ids:
                     if not data.phone:
                         continue
                     if p.type == 'user':
                         prms[p.name] = p.value
                     elif p.type == 'password':
                         prms[p.name] = p.value
                     elif p.type == 'to':
                         prms[p.name] = str(data.phone).replace("+", "")
                     elif p.type == 'sms':
                         prms[p.name] = msg
                     elif p.type == 'extra':
                         prms[p.name] = p.value
                params = urllib.urlencode(prms)
                name = url + "?" + params
            queue_obj = self.pool.get('sms.smsclient.queue')
            vals = self._prepare_smsclient_queue(cr, uid, data, name, gateway,msg , context=context)
            queue_obj.create(cr, uid, vals, context=context)
        return True
    
    def sms_send(self, cr, uid, ids, context=None):
        ''' function used in sending sms on event confirmation '''
        for event in self.browse(cr, uid, ids, context) :
            gateway = self._default_get_gateway( cr, uid, ids, context=context)
            if not gateway:
                raise osv.except_osv(_('Error'), _('No Gateway Found'))
            else:
                interp_name= ''
                if event.interpreter_id.name:
                    interp_name += event.interpreter_id.name
                if event.interpreter_id.middle_name:
                    interp_name += ' ' + event.interpreter_id.middle_name
                if event.interpreter_id.last_name:
                    interp_name += ' ' + event.interpreter_id.last_name
                cust_msg = "Interpreter " + interp_name + " is assigned for event " + event.name
                self._send_message(cr, uid, event.partner_id, gateway ,cust_msg , context=context)
        return True
    
    def get_duration(self, cr, uid, ids,origin ,destination , context=None):
        '''----- Depricated -----  function to get distance and duartion between origin and destination and used in searching
         Interpreters and Transporters '''
        result ={}
        departure_time = context.get('departure_time',False)
        if not departure_time:
            n = datetime.datetime.now()
            departure_time = int(time.mktime(n.timetuple()))
        maps = GoogleMaps()
        result['duration'] = ''
        result['distance'] = maps.distance(origin, destination, mode='driving')
        return result

#    def haversine(self , cr ,uid ,ids , lat1, lon1,  lat2, lon2):
#        """
#        Calculate the great circle distance between two points
#        on the earth (specified in decimal degrees)
#        """
#        # convert decimal degrees to radians
#        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
#        # haversine formula
#        dlon = lon2 - lon1
#        dlat = lat2 - lat1
#        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
#        c = 2 * asin(sqrt(a))
#
#        # 6367 km is the radius of the Earth
#        km = 0
#        if c > 0:
#            #km = (6367 * c ) / 1.60934
#            km = ( c * 3960 )
#        else:
#            km = 0
#        return km
#
#    def distance_on_unit_sphere(self , cr ,uid ,ids , lat1, long1,  lat2, long2):
#
#        # Convert latitude and longitude to
#        # spherical coordinates in radians.
#        degrees_to_radians = math.pi/180.0
#        # phi = 90 - latitude
#        phi1 = (90.0 - lat1)*degrees_to_radians
#        phi2 = (90.0 - lat2)*degrees_to_radians
#        # theta = longitude
#        theta1 = long1*degrees_to_radians
#        theta2 = long2*degrees_to_radians
#        # Compute spherical distance from spherical coordinates.
#        # For two locations in spherical coordinates
#        # (1, theta, phi) and (1, theta, phi)
#        # cosine( arc length ) =
#        #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
#        # distance = rho * arc length
#        cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) +
#               math.cos(phi1)*math.cos(phi2))
#        arc = math.acos( cos )
#        # Remember to multiply arc by the radius of the earth
#        # in your favorite set of units to get length.
#        miles = (arc * 3960 )
#        return miles

    def get_distance(self, cr, uid, ids,origins ,destinations , context=None ,key = None):
        ''' function to get distance and duartion between origin and destination and used in searching 
         Interpreters and Transporters '''
        result ={}
        departure_time = context.get('departure_time',False)
        if not departure_time:
            n = datetime.datetime.now()
            departure_time = int(time.mktime(n.timetuple()))
        maps = google_maps_distance()
        result = maps.distance(origins, destinations, mode='driving', departure_time=departure_time ,key = key)
        #print "get_distance.complete..........",result
        return result

    def search_geo_interpreter(self, cr, uid, ids, interp_ids=[],context=None):
        ''' function to get interpreters based on location geo points '''
        interpreter_ids = []
        for event in self.browse(cr, uid, ids, context=context):
            latitude = context.get('location_id',False).latitude if context.get('location_id',False) else event.location_id.latitude
            longitude = context.get('location_id',False).longitude if context.get('location_id',False) else event.location_id.longitude
            if latitude and longitude and interp_ids:
                # 1. first way: in the same country, small area
#                interpreter_ids = interpreter.search(cr, uid, [
#                    ('latitude', '>', latitude - 2), ('latitude', '<', latitude + 2),
#                    ('longitude', '>', longitude - 1.5), ('longitude', '<', longitude + 1.5),
#                    ('country_id', '=', event.location_id.country_id.id),('id','in',interp_ids),
#                    ('company_id','=',event.company_id.id)
#                ], context=context)
#                print "interpreter_ids.1........",len(interpreter_ids)
                cr.execute("""SELECT id FROM  (select id, (point(longitude, latitude) <-> point(%s,%s)) AS distance FROM res_partner
                          WHERE longitude is not null AND latitude is not null AND latitude >= (latitude - 1)
                          AND latitude <= (latitude + 1) AND longitude >= (longitude - 1) AND longitude <= (longitude + 1)
                          AND cust_type in ('interpreter','interp_and_transl') AND company_id = %s AND id in %s
                          ) AS d ORDER BY  distance asc LIMIT 60""", (longitude, latitude , event.company_id.id, tuple(interp_ids)))
                interpreter_ids = map(lambda x: x[0], cr.fetchall())
#                print "interpreter_ids 0.5 ........",interpreter_ids
                if len(interpreter_ids) < 10:
                    cr.execute("""SELECT id FROM  (select id, (point(longitude, latitude) <-> point(%s,%s)) AS distance FROM res_partner
                              WHERE longitude is not null AND latitude is not null AND latitude >= (latitude - 2)
                              AND latitude <= (latitude + 2) AND longitude >= (longitude - 1.5) AND longitude <= (longitude + 1.5)
                              AND cust_type in ('interpreter','interp_and_transl') AND company_id = %s AND id in %s
                              ) AS d ORDER BY  distance asc LIMIT 60""", (longitude, latitude , event.company_id.id, tuple(interp_ids)))
                    interpreter_ids = map(lambda x: x[0], cr.fetchall())
#                print "interpreter_ids.1........",len(interpreter_ids)
                # 2. second way: in the same country, big area
                if not interpreter_ids:
                    cr.execute("""SELECT id FROM  (select id, (point(longitude, latitude) <-> point(%s,%s)) AS distance FROM res_partner
                              WHERE longitude is not null AND latitude is not null AND latitude >= (latitude - 3)
                              AND latitude <= (latitude + 3) AND longitude >= (longitude - 2.5) AND longitude <= (longitude + 2.5)
                              AND cust_type in ('interpreter','interp_and_transl') AND company_id = %s AND id in %s
                              ) AS d ORDER BY  distance asc LIMIT 60""", (longitude, latitude , event.company_id.id, tuple(interp_ids)))
                    interpreter_ids = map(lambda x: x[0], cr.fetchall())
#                print "interpreter_ids.1.5........",len(interpreter_ids)
                if not interpreter_ids :
                    cr.execute("""SELECT id FROM  (select id, (point(longitude, latitude) <-> point(%s,%s)) AS distance FROM res_partner
                          WHERE longitude is not null AND latitude is not null AND latitude >= (latitude - 4)
                          AND latitude <= (latitude + 4) AND longitude >= (longitude - 4) AND longitude <= (longitude + 4)
                          AND cust_type in ('interpreter','interp_and_transl') AND company_id = %s AND id in %s
                          ) AS d ORDER BY  distance asc LIMIT 60""", (longitude, latitude , event.company_id.id, tuple(interp_ids)))
                    interpreter_ids = map(lambda x: x[0], cr.fetchall())
#                print "interpreter_ids2.........",len(interpreter_ids)
                if not interpreter_ids :
                    cr.execute("""SELECT id FROM  (select id, (point(longitude, latitude) <-> point(%s,%s)) AS distance FROM res_partner
                          WHERE longitude is not null AND latitude is not null AND latitude >= (latitude - 6)
                          AND latitude <= (latitude + 6) AND longitude >= (longitude - 6) AND longitude <= (longitude + 6)
                          AND cust_type in ('interpreter','interp_and_transl') AND company_id = %s AND id in %s
                          ) AS d ORDER BY  distance asc LIMIT 60""", (longitude, latitude , event.company_id.id, tuple(interp_ids)))
                    interpreter_ids = map(lambda x: x[0], cr.fetchall())
#                print "interpreter_ids3.........",len(interpreter_ids)
                if not interpreter_ids :
                    cr.execute("""SELECT id FROM  (select id, (point(longitude, latitude) <-> point(%s,%s)) AS distance FROM res_partner
                          WHERE longitude is not null AND latitude is not null AND latitude >= (latitude - 8)
                          AND latitude <= (latitude + 8) AND longitude >= (longitude - 8) AND longitude <= (longitude + 8)
                          AND cust_type in ('interpreter','interp_and_transl') AND company_id = %s AND id in %s
                          ) AS d ORDER BY distance asc LIMIT 60""", (longitude, latitude , event.company_id.id, tuple(interp_ids)))
                    interpreter_ids = map(lambda x: x[0], cr.fetchall())
#                print "interpreter_ids31.........",len(interpreter_ids)
                if not interpreter_ids :
                    cr.execute("""SELECT id FROM  (select id, (point(longitude, latitude) <-> point(%s,%s)) AS distance FROM res_partner
                          WHERE longitude is not null AND latitude is not null AND latitude >= (latitude - 10)
                          AND latitude <= (latitude + 10) AND longitude >= (longitude - 10) AND longitude <= (longitude + 10)
                          AND cust_type in ('interpreter','interp_and_transl') AND company_id = %s AND id in %s
                          ) AS d ORDER BY distance asc LIMIT 60""", (longitude, latitude , event.company_id.id, tuple(interp_ids)))
                    interpreter_ids = map(lambda x: x[0], cr.fetchall())
#                print "interpreter_ids32.........",len(interpreter_ids)
                if not interpreter_ids:
                    cr.execute("""SELECT id FROM  (select id, (point(longitude, latitude) <-> point(%s,%s)) AS distance FROM res_partner
                          WHERE longitude is not null AND latitude is not null AND latitude >= (latitude - 15)
                          AND latitude <= (latitude + 15) AND longitude >= (longitude - 15) AND longitude <= (longitude + 15)
                          AND cust_type in ('interpreter','interp_and_transl') AND company_id = %s AND id in %s
                          ) AS d
                          ORDER BY distance asc LIMIT 60""", (longitude, latitude , event.company_id.id, tuple(interp_ids)))
                    interpreter_ids = map(lambda x: x[0], cr.fetchall())
#                print "interpreter_ids33.........",len(interpreter_ids)
#                # 6. sixth way: closest partner whatsoever, just to have at least one result
                if len(interpreter_ids) < 3:
                    # warning: point() type takes (longitude, latitude) as parameters in this order!
                    cr.execute("""SELECT id, distance FROM  (select id, (point(longitude, latitude) <-> point(%s,%s)) AS distance FROM res_partner
                                WHERE longitude is not null
                                AND latitude is not null and cust_type in ('interpreter','interp_and_transl') and company_id = %s and id in %s
                                ) AS d ORDER BY distance asc LIMIT 60""", (longitude, latitude , event.company_id.id, tuple(interp_ids)))
                    interpreter_ids = map(lambda x: x[0], cr.fetchall())
#                print "interpreter_ids5.........",len(interpreter_ids)
        return interpreter_ids

    def reset_api_keys(self, cr, uid, ids, context):
        api = self.pool.get('api.keys')
#        if not len([key for key in api_keys_dict if api_keys_dict[key]['count'] == 0]) == len(api_keys_dict):
        key_ids = api.search(cr,uid,[])
        for each_key in api.browse(cr,uid,key_ids):
            _logger.debug("each key write+++++++++++", each_key)
            each_key.write( {'used': 0, 'active_run':0})
        return True
    
    def get_key(self,cr,uid, count):
#        global api_count
        global api_keys_dict
        api_key = False
        key_obj = self.pool.get('api.keys')
#        The Date Change Scenario will be handled by scheduler

#        Check if the keys exists in the database if not create
        key_ids = key_obj.search(cr,uid,[])
        if not key_ids:
            for each_key in api_keys_dict:
                key_obj.create(cr, uid, {'used':api_keys_dict[each_key]['count'], 'active_run': api_keys_dict[each_key]['active'],
                                    'name':each_key})
#        Search for active key in db
        act_key_id = key_obj.search(cr,uid,[('active_run','=',True)])
        act_key_id = act_key_id[0] if act_key_id else False
        # To get the api_key for the first time
        if not act_key_id:
            key_ids = key_obj.search(cr,uid,[])
            if key_ids:
                act_key = key_obj.browse(cr,uid,key_ids[0])
                act_key.write({'active_run':True})
                act_key_id = act_key.id

        act_key = key_obj.browse(cr,uid,act_key_id)
        api_count = act_key.used
        if api_count+ count >= 1000:
            act_key.write({'active_run':False, 'used':api_count})
            key_ids2 = key_obj.search(cr,uid,[('used','<',1000-count)])
            if key_ids2:
                key_obj.write(cr,uid,key_ids2[0],{'active_run':True})
                act_key = key_obj.browse(cr,uid,key_ids2[0])
                api_count = act_key.used
            else: #In case all keys are exhausted
                key_ids = key_obj.search(cr,uid,[])
                act_key = key_obj.browse(cr,uid,key_ids[0])
                api_key = act_key.name
                return api_key
        api_key = act_key.name
        key = api_key

        if not key:
            key_ids = key_obj.search(cr,uid,[])
            act_key = key_obj.browse(cr,uid,key_ids[0])
            key = act_key.name
        key_obj1 = self.pool.get('api.keys')
        fin_key_ids = key_obj1.search(cr,uid,[('active_run','=',True)])
#        lock = threading.Condition()
#        if write_lock == False and used_prod == False:
#            custom_thread.write_key(lock,cr,uid,key_ids[0],api_count).start()
#        else :
#            cr1 = pooler.get_db('iug_live').cursor()
#            custom_thread.write_key_consumer(lock,cr1,uid,key_ids[0],api_count).start()
        if fin_key_ids:
            count_old = key_obj.browse(cr,uid,fin_key_ids[0]).used
            key_obj.write(cr,uid,fin_key_ids[0],{'used':count + count_old})
#        print "thresdfdasf enu++++",threading.enumerate()
        return key
    
    def import_interpreter_new(self, cr, uid, ids, context=None):
        ''' This function search for interpreters and brings distance between interpreter and doctor Location as well
            in the event form '''
        ints, rates, int_locations, visit_list, preferred_lst, unlink_ints = [], [], [], [], [], []
        res, dist_dict, block_inter_ids = [], {}, []
        dist_dict['duration'], dist_dict['distance'] = '', 0
        interpreter = self.pool.get('res.partner')
        select_obj = self.pool.get('select.interpreter.line')
        history_obj = self.pool.get('interpreter.alloc.history')
        interpreter_ids , visit_ids, categ_rate= [], [], False
        for event in self.browse(cr ,uid ,ids ):
            if not event.language_id:
                raise osv.except_osv(_('Warning!'),_('Please select Language first.'))
            category = event.language_id and event.language_id.lang_group or False
            event_purpose = event.event_purpose
            for select_line in event.interpreter_ids:
                if (select_line.company_id and event.company_id and select_line.company_id.id != event.company_id.id) :
                    select_obj.unlink(cr ,uid ,[select_line.id])
                else:
                    unlink_ints.append(select_line.interpreter_id.id)
            if not category:
                raise osv.except_osv(_('Warning!'),_('Please select Language Group in language form.'))
#            partner = event.partner_id
            location = context.get('location_id',False) if context.get('location_id',False) else event.location_id
#            print "location..........",location
            if location.latitude == 0 or location.longitude == 0:
                self.pool.get('location').geo_localize(cr ,uid , [location.id], context=context)
            if event.certification_level_id:
                query = "select lang.interpreter_id from interpreter_language as lang INNER JOIN res_partner as partner ON (lang.interpreter_id = partner.id)\
                        where partner.active is true and is_interpretation_active is true and lang.name = %s and certification_level_id = %s and lang.company_id = %s"%( event.language_id.id ,
                        event.certification_level_id and event.certification_level_id.id , event.company_id.id)
                cr.execute(query)
                interpreter_ids = map(lambda x: x[0], cr.fetchall())
#                print "interpreter_ids11......",len(interpreter_ids)
            else:
                query = "select lang.interpreter_id from interpreter_language as lang INNER JOIN res_partner as partner ON (lang.interpreter_id = partner.id)\
                        where partner.active is true and is_interpretation_active is true and lang.name = %s and lang.company_id = %s"%( event.language_id.id , event.company_id.id)
                cr.execute(query)
                interpreter_ids = map(lambda x: x[0], cr.fetchall())
#                print "interpreter_ids12......",len(interpreter_ids)
            if not interpreter_ids:
                raise osv.except_osv(_('Warning!'),_('No Interpreter found for this language.'))

            if interpreter_ids:
                interp_ids = self.search_geo_interpreter( cr ,uid , ids ,interpreter_ids ,  context= context)
#                print "interp_ids..........",interp_ids,type(interp_ids)
#                interp_ids = list(set(flatten(interp_ids)))
                for id in unlink_ints:
                    if id in interp_ids:
                        interp_ids.remove(id)
                if len(interp_ids) > 15:
                    interp_ids = interp_ids[0:15]
#                print "interp_ids........",interp_ids
                location_address = geo_query_address(location.street or False , location.zip or False ,location.city or False, \
                                    location.state_id and location.state_id.name or False, location.country_id and \
                                    location.country_id.name or False)
                patient = event.patient_id
                if event.partner_id and event.partner_id.block_inter_ids:
                    for customer in event.partner_id.block_inter_ids:
                        block_inter_ids.append(customer.id)
                
                if patient:
                    if patient.interpreter_id:
                        visit_ids.append(patient.interpreter_id.id)
                        if patient.interpreter_id.id in interp_ids:
                            interp_ids.remove(patient.interpreter_id.id)
                    for history in patient.interpreter_history:
                        if (history.name.id in interpreter_ids) and history.state in ('allocated','confirm'):
                            visit_ids.append(history.name.id)
                            if history.name.id in interp_ids:
                                interp_ids.remove(history.name.id)
                if event.partner_id and event.partner_id.interpreter_id:
                    visit_ids.append(event.partner_id.interpreter_id.id)
                    if event.partner_id.interpreter_id.id in interp_ids:
                        interp_ids.remove(event.partner_id.interpreter_id.id)
# +++++++++++Bring Visitors +++++++++
                for visit_id in visit_ids:
                    if visit_id in block_inter_ids:
                        continue
                    overlap = False
                    interpreter_browse = interpreter.browse(cr ,uid , visit_id)
#                    company_ids = self.pool.get('res.company').search(cr , SUPERUSER_ID, [('name','ilike','ACD')])
#                    if not (company_ids and event.company_id and event.company_id.id in company_ids or interpreter_browse.is_agency == True):
                    if not interpreter_browse.is_agency:
                        history_ids2 = history_obj.search(cr , SUPERUSER_ID , [('name','=',visit_id),('state','in',('confirm','allocated')),('company_id','=',event.company_id.id),('cancel_date','=',False),
                                                        ('event_start_date','=',event.event_start_date)])
                        for history_browse in history_obj.browse( cr, SUPERUSER_ID, history_ids2):
                            if (event.event_start > history_browse.event_start and event.event_end < history_browse.event_end) :
                                overlap = True
                            elif (event.event_start > history_browse.event_start and event.event_start < history_browse.event_end) :
                                overlap = True
                            elif (event.event_end > history_browse.event_start and event.event_end < history_browse.event_end) :
                                overlap = True
                            elif (event.event_start == history_browse.event_start or event.event_end == history_browse.event_end) :
                                overlap = True
                            elif (history_browse.event_start > event.event_start and history_browse.event_start < event.event_end) :
                                overlap = True
                            elif (history_browse.event_end < event.event_end and history_browse.event_end > event.event_start) :
                                overlap = True
#                            elif (event.event_start == history_browse.event_end ):
#                                overlap = True
                    if overlap:
                        continue
                    else:
                        ints.append(visit_id)
                    categ_rate , rate= 0.0 ,False
                    if event_purpose:
                        for rate_id in interpreter_browse.rate_ids:
                            if rate_id.rate_type == event_purpose:
                                rate = rate_id
                        if category and rate:
                            if category == 'spanish_regular':
                                categ_rate = rate.spanish_regular
                            elif category == 'spanish_licenced':
                                categ_rate = rate.spanish_licenced
                            elif category == 'spanish_certified':
                                categ_rate = rate.spanish_certified
                            elif category == 'exotic_regular':
                                categ_rate = rate.exotic_regular
                            elif category == 'exotic_certified':
                                categ_rate = rate.exotic_certified
                            elif category == 'exotic_middle':
                                categ_rate = rate.exotic_middle
                            elif category == 'exotic_high':
                                categ_rate = rate.exotic_high
                        if rate and categ_rate == 0.0:
                            categ_rate = rate.default_rate
                        rates.append(categ_rate)
                    interpreter_browse = interpreter.browse(cr ,uid , visit_id)
                    interp_address = geo_query_address(interpreter_browse.street or False , interpreter_browse.zip or False ,interpreter_browse.city or False, \
                                    interpreter_browse.state_id and interpreter_browse.state_id.name or False, interpreter_browse.country_id and \
                                    interpreter_browse.country_id.name or False)
#                   #print "interp_address....location_address....",interp_address,location_address
#                    pass_locs = interp_address + '|'
                    int_locations.append(interp_address)
                    if (patient and patient.interpreter_id and patient.interpreter_id.id == visit_id) or (event.partner_id and event.partner_id.interpreter_id and event.partner_id.interpreter_id.id == visit_id):
                        preferred_lst.append(True)
                        visit_list.append(False)
                    else:
                        preferred_lst.append(False)
                        visit_list.append(True)
#                    visit_list.append(False if patient and patient.interpreter_id and patient.interpreter_id.id == visit_id else True)
#                    preferred_lst.append(True if (patient and patient.interpreter_id and patient.interpreter_id.id == visit_id) or (event.partner_id and event.partner_id.interpreter_id and event.partner_id.interpreter_id == visit_id) else False)
#                    preferred_dict[patient.interpreter_id.id] = True
#                    try:
#                        dist_dict = self.get_distance(cr, uid, ids, interp_address ,location_address , context=context , key = key)
#                    except Exception, e :
#                        dist_dict['duration'] = ''
#                        dist_dict['distance'] = 0
#                        print "Exception......",e.args
#                        pass
#                    self.write(cr ,uid ,ids , {'interpreter_ids':[(0, 0, {'rate':categ_rate,'event_id':ids[0],'visited': False if patient and patient.interpreter_id and patient.interpreter_id.id == visit_id else True,
#                                   'duration': dist_dict['duration'] or '','preferred': True if patient and patient.interpreter_id and patient.interpreter_id.id == visit_id else False,
#                                   'distance':float(float(dist_dict['distance']) * 0.000621371) or 0, 'state':'draft','voicemail_msg':'','interpreter_id':visit_id})]})
# -------------------------------------------------------------------------------------------------------------------
#                key = self.get_key(cr,uid,len(interp_ids))
                for interp_id in interp_ids:
                    if interp_id in block_inter_ids:
                        continue
                    overlap = False
                    interpreter_browse = interpreter.browse(cr ,uid , interp_id)
#                    company_ids = self.pool.get('res.company').search(cr , SUPERUSER_ID, [('name','ilike','ACD')])
#                    if not (company_ids and event.company_id and event.company_id.id in company_ids):
                    if not interpreter_browse.is_agency:
                        history_ids2 = history_obj.search(cr , SUPERUSER_ID, [('name','=',interp_id),('state','in',('confirm','allocated')),('company_id','=',event.company_id.id),
                                    ('event_start_date','=',event.event_start_date)])
                        for history_browse in history_obj.browse( cr, SUPERUSER_ID, history_ids2):
                            if (event.event_start > history_browse.event_start and event.event_end < history_browse.event_end) :
                                overlap = True
                            elif (event.event_start > history_browse.event_start and event.event_start < history_browse.event_end) :
                                overlap = True
                            elif (event.event_end > history_browse.event_start and event.event_end < history_browse.event_end) :
                                overlap = True
                            elif event.event_start == history_browse.event_start or event.event_end == history_browse.event_end :
                                overlap = True
                            elif (history_browse.event_start > event.event_start and history_browse.event_start < event.event_end) :
                                overlap = True
                            elif (history_browse.event_end < event.event_end and history_browse.event_end > event.event_start) :
                                overlap = True
    #                        elif (event.event_start == history_browse.event_end )or (event.event_end == history_browse.event_start) :
    #                            overlap = True
                    if overlap:
                        continue
                    else:
                        if interp_id:
                            ints.append(interp_id)
                    interp_address = geo_query_address(interpreter_browse.street or False , interpreter_browse.zip or False ,interpreter_browse.city or False, \
                                    interpreter_browse.state_id and interpreter_browse.state_id.name or False, interpreter_browse.country_id and \
                                    interpreter_browse.country_id.name or False)
#                    pass_locs = interp_address + '|'
                    int_locations.append(interp_address)
                    visit_list.append(False)
                    preferred_lst.append(False)
#                        print "location_address.....interp_address......",location_address,interp_address
#                    dist_dict['duration'] = ''
#                    dist_dict['distance'] = 0
#                    key = self.get_key(cr,uid)
#                    dist_dict = self.get_distance(cr, uid, ids, interp_address ,location_address , context=context, key=key)
                    categ_rate, rate = 0.0, False
                    if event_purpose:
                        for rate_id in interpreter_browse.rate_ids:
                            if rate_id.rate_type == event_purpose:
                                rate = rate_id
                        if category and rate:
                            if category == 'spanish_regular':
                                categ_rate = rate.spanish_regular
                            elif category == 'spanish_licenced':
                                categ_rate = rate.spanish_licenced
                            elif category == 'spanish_certified':
                                categ_rate = rate.spanish_certified
                            elif category == 'exotic_regular':
                                categ_rate = rate.exotic_regular
                            elif category == 'exotic_certified':
                                categ_rate = rate.exotic_certified
                            elif category == 'exotic_middle':
                                categ_rate = rate.exotic_middle
                            elif category == 'exotic_high':
                                categ_rate = rate.exotic_high
                        if rate and categ_rate == 0.0:
                            categ_rate = rate.default_rate
                        rates.append(categ_rate)

#            print 'lenghts+++++++++++='
#            print '+++++++++v++',len(visit_list)
#            print '+++++++++v++',len(preferred_lst)
#            print '+++++++++v++',len(int_locations)
#            print '+++++++++v++',len(ints)
#            print '+++++++++v++',len(rates)
            key = self.get_key(cr, uid, len(ints))
#            key = 'AIzaSyATAqHzxn53tdnzHtneCIi03nSo3Wlq5O'
#            print "key+++++++++++++++",key
##########################################################
#            for intrptr in unlink_ints:
#                select_obj.unlink(cr ,uid ,[intrptr.id])
#######################################################
            div = len(ints)/10
            rem = len(ints)% 10
#            [(10*i,10*j) for i,j in zip( range(0,div), range(1,div+1) )]
#            event_locations = [location_address for i in range(0,len(int_locations))]
            if div:
                for i, j in [(10*k, 10*l) for k, l in zip( range(0, div), range(1, div+1) )]:#[(0,10),(10,20),(20,30),(30,40),(40,50),(50,60)]:
                    locs = '|'.join(int_locations[i:j])
#                    print "locs++++++++++++++",len(int_locations[i:j])
                    event_locations = [location_address + '|' for n in range(0,10)]
#                    print "event_locations++++++++++++",event_locations
        #            dist_dict = self.get_distance(cr, uid, ids, locs ,event_locations[0][:-1] , context=context, key=key)
                    try:
                        dist_dict = self.get_distance(cr, uid, ids, locs ,event_locations[0] , context=context, key=key)
                    except Exception, e :
#                        dist_dict['duration'] = ''
#                        dist_dict['distance'] = 0
#                        print "Exception......",e.args
                        pass
                    dur, dist = [], []
                    dur = dist_dict.get('duration',False) if dist_dict.get('duration',False) else [0 for m in range(0,10)]
                    dist = dist_dict.get('distance',False) if dist_dict.get('distance',False) else [0 for m in range(0,10)]
#                    print "dur+++++++++++++++++++",dur
#                    print "dist++++++++++++++++++",dist
#                    print "ints+++++++++++",ints[i:j]
#                    print "rates+++++++++++",rates[i:j]
#                    print "visitt+++++++++++",visit_list[i:j]
#                    print "preffefer+++++++++++",preferred_lst[i:j]
#                    print "int_locations++++++",int_locations
#                    print "ints+++++++++++",ints
#                    print "i,j++++++++++++++",i,j
#                    print "ints[i:j]++++++++++++++++",ints[i:j]
#                    print "dist++++++++++++++++++",dist
#                    print "zip(ints[i:j],rates[i:j],visit_list[i:j],preferred_lst[i:j],dur,dist)++",zip(ints[i:j],rates[i:j],visit_list[i:j],preferred_lst[i:j],dur,dist)
                    
                    for interp_id, rate, visited, preferred, duration, distance in zip(ints[i:j], rates[i:j], visit_list[i:j], preferred_lst[i:j], dur, dist):
                        self.write(cr ,uid , ids, { 'interpreter_ids':[(0, 0, {'interpreter_id':interp_id ,'event_id':ids[0] ,'state':'draft',
                                                    'duration': duration or '','rate':rate,'visited':visited,'preferred':preferred,
                                                    'distance':float(float(distance) * 0.000621371) or 0})]})
            if rem:
                for i, j in [( div*10, div*10+rem)]:#[(0,10),(10,20),(20,30),(30,40),(40,50),(50,60)]:
#                    print "in remm++++++++++",i   ,      j
                    locs = '|'.join(int_locations[i:j])
#                    print "locs++++++++++++++",len(int_locations[i:j])
#                    print "locs++++++++++++++",type(locs)

                    event_locations = [location_address + '|' for r in range(i,j)]

#                    print "event_locations++++++++++++",event_locations
                    key = self.get_key(cr, uid, len(int_locations))
        #            dist_dict = self.get_distance(cr, uid, ids, locs ,event_locations[0][:-1] , context=context, key=key)
                    try:
                        dist_dict = self.get_distance(cr, uid, ids, locs, event_locations[0] , context=context, key=key)
                    except Exception, e :
#                        dist_dict['duration'] = ''
#                        dist_dict['distance'] = 0
                        print "Exception......",e.args
                        pass
                    dur, dist = [],[]
                    dur = dist_dict.get('duration',False) if dist_dict.get('duration',False) else [0 for o in range(0,10)]
                    dist = dist_dict.get('distance',False) if dist_dict.get('distance',False) else [0 for p in range(0,10)]
#                    print "dur+++++++++++++++++++",dur
#                    print "dist++++++++++++++++++",dist
#                    print "zip(ints[i:j],rates[i:j],visit_list[i:j],preferred_lst[i:j],dur,dist)++",zip(ints[i:j],rates[i:j],visit_list[i:j],preferred_lst[i:j],dur,dist)
                    for interp_id, rate, visited, preferred, duration, distance in zip(ints[i:j], rates[i:j], visit_list[i:j], preferred_lst[i:j], dur,dist):
                        self.write(cr , uid, ids , {'interpreter_ids':[(0, 0, {'interpreter_id':interp_id ,'event_id':ids[0] ,'state':'draft',
                                                        'duration': duration or '','rate':rate,'visited':visited,'preferred':preferred,
                                                        'distance':float(float(distance) * 0.000621371) or 0})]})

        return res
    
    
    def clear_interpreter_list(self, cr, uid, ids, context=None):
        del_list = []
        if ids and isinstance(ids,list):
            for event in self.browse(cr, uid, ids) and self.browse(cr,uid,ids):
                for interpreter in event.interpreter_ids:
                    del_list.append((3,interpreter.id))
                    self.write(cr, uid, [event.id],{'interpreter_ids':[(3,interpreter.id)]}, context=context)
            val = {
            'interpreter_ids': del_list,
        }
        self.write(cr, uid, [event.id],val, context=context)
        return True
    
    def search_geo_transporter(self, cr, uid, ids, transp_ids=[] ,context=None):
        ''' function to search transporters based on location geo points '''
        transporter_ids = []
        for event in self.browse(cr, uid, ids, context=context):
            latitude = context.get('location_id',False).latitude if context.get('location_id',False) else event.location_id.latitude
            longitude = context.get('location_id',False).longitude if context.get('location_id',False) else event.location_id.longitude
            if latitude and longitude and transp_ids:
                # 1. first way: in the same country, small area
#                transporter_ids = transporter.search(cr, uid, [
#                    ('latitude', '>', latitude - 2), ('latitude', '<', latitude + 2),
#                    ('longitude', '>', longitude - 1.5), ('longitude', '<', longitude + 1.5),
#                    ('cust_type','=','transporter'),#('country_id', '=', event.location_id.country_id.id)
#                    ('company_id','=',event.company_id.id)
#                ], context=context)
#                print "transporter_ids.1........",len(transporter_ids)
                cr.execute("""SELECT id
                          FROM  (select id, (point(longitude, latitude) <-> point(%s,%s)) AS distance FROM res_partner
                          WHERE longitude is not null AND latitude is not null AND latitude >= (latitude - 1)
                          AND latitude <= (latitude + 1) AND longitude >= (longitude - 0.5) AND longitude <= (longitude + 0.5)
                          AND cust_type in ('transporter') AND company_id = %s AND id in %s
                          ) AS d
                          ORDER BY distance asc LIMIT 60""", (longitude, latitude , event.company_id.id, tuple(transp_ids,)))
                transporter_ids = map(lambda x: x[0], cr.fetchall())
#                print "transporter_ids 2.........",len(transporter_ids)
                if len(transporter_ids) < 10:
                    cr.execute("""SELECT id
                              FROM  (select id, (point(longitude, latitude) <-> point(%s,%s)) AS distance FROM res_partner
                              WHERE longitude is not null AND latitude is not null AND latitude >= (latitude - 2)
                              AND latitude <= (latitude + 2) AND longitude >= (longitude - 1.5) AND longitude <= (longitude + 1.5)
                              AND cust_type in ('transporter') AND company_id = %s AND id in %s
                              ) AS d
                              ORDER BY distance asc LIMIT 60""", (longitude, latitude , event.company_id.id, tuple(transp_ids,)))
                    transporter_ids = map(lambda x: x[0], cr.fetchall())
#                print "transporter_ids 2.........",len(transporter_ids)
                # 3. third way: in the same country, extra large area
                if not transporter_ids :
                    cr.execute("""SELECT id
                          FROM  (select id, (point(longitude, latitude) <-> point(%s,%s)) AS distance FROM res_partner
                          WHERE longitude is not null AND latitude is not null AND latitude >= (latitude - 6)
                          AND latitude <= (latitude + 6) AND longitude >= (longitude - 6) AND longitude <= (longitude + 6)
                          AND cust_type in ('transporter') AND company_id = %s AND id in %s
                          ) AS d
                          ORDER BY distance asc LIMIT 60""", (longitude, latitude , event.company_id.id, tuple(transp_ids,)))
                    transporter_ids = map(lambda x: x[0], cr.fetchall())
#                print "transporter_ids 3.........",len(transporter_ids)
                if not (transporter_ids) :
                    cr.execute("""SELECT id
                          FROM  (select id, (point(longitude, latitude) <-> point(%s,%s)) AS distance FROM res_partner
                          WHERE longitude is not null AND latitude is not null AND latitude >= (latitude - 8)
                          AND latitude <= (latitude + 8) AND longitude >= (longitude - 8) AND longitude <= (longitude + 8)
                          AND cust_type in ('transporter') AND company_id = %s AND id in %s
                          ) AS d
                          ORDER BY distance asc LIMIT 60""", (longitude, latitude , event.company_id.id, tuple(transp_ids,)))
                    transporter_ids = map(lambda x: x[0], cr.fetchall())
#                print "transporter_ids 31.........",len(transporter_ids)
                if not (transporter_ids) :
                    cr.execute("""SELECT id
                          FROM  (select id, (point(longitude, latitude) <-> point(%s,%s)) AS distance FROM res_partner
                          WHERE longitude is not null AND latitude is not null AND latitude >= (latitude - 10)
                          AND latitude <= (latitude + 10) AND longitude >= (longitude - 10) AND longitude <= (longitude + 10)
                          AND cust_type in ('transporter') AND company_id = %s AND id in %s
                          ) AS d
                          ORDER BY distance asc LIMIT 60""", (longitude, latitude , event.company_id.id, tuple(transp_ids,)))
                    transporter_ids = map(lambda x: x[0], cr.fetchall())
#                print "transporter_ids 32.........",len(transporter_ids)
                if len(transporter_ids) < 2:
                    # warning: point() type takes (longitude, latitude) as parameters in this order!
                    cr.execute("""SELECT id, distance
                                  FROM  (select id, (point(longitude, latitude) <-> point(%s,%s)) AS distance FROM res_partner
                                  WHERE longitude is not null
                                        AND latitude is not null and cust_type = 'transporter' and company_id = %s  AND id in %s
                                        ) AS d
                                  ORDER BY distance asc LIMIT 60""", (longitude, latitude , event.company_id.id, tuple(transp_ids,)))
                    res = cr.dictfetchone()
                    if res:
                        transporter_ids.append(res['id'])
#                print "transporter_ids5.........",len(transporter_ids)
        return transporter_ids

    def import_transporter_new(self, cr, uid, ids, context):
        ''' This function search for transporters and brings distance between transporter and Location 
        in the event form '''
        trans, rates, int_locations, visit_list, preferred_lst = [], [], [], [], []
        res, dist_dict = [], {}
        dist_dict['duration'], dist_dict['distance'] = '', 0.0
        transporter = self.pool.get('res.partner')
        select_obj = self.pool.get('select.transporter.line')
        history_obj = self.pool.get('transporter.alloc.history')
        transporter_ids, select_ids = [],[]
        for event in self.browse(cr ,uid ,ids ):
            for transporter_id in event.transporter_ids:
                select_obj.unlink(cr ,uid , [transporter_id.id])
            for transporter_id2 in event.transporter_ids2:
                select_obj.unlink(cr ,uid , [transporter_id2.id])
            location = context.get('location_id',False) if context.get('location_id',False) else event.location_id
            if location.latitude == 0 or location.longitude == 0:
                self.pool.get('location').geo_localize(cr ,uid , [location.id], context=context)
            t_ids = transporter.search(cr , uid , [('is_transportation_active','=',True),('company_id','=',event.company_id.id),('active','=',True)])
            transp_ids = self.search_geo_transporter( cr ,uid , ids, t_ids,  context= context)
            transp_ids = flatten(transp_ids)
            transp_ids = list(set(transp_ids))
            if len(transp_ids) > 100 :
                transp_ids = transp_ids[:60]
            visit_ids = []
            patient = event.patient_id
            if visit_ids:
                visit_ids = flatten(visit_ids)
                visit_ids = list(set(visit_ids))
            
            location_address = geo_query_address(location.street or False , location.zip or False ,location.city or False, \
                                    location.state_id and location.state_id.name or False, location.country_id and \
                                    location.country_id.name or False)
            context['departure_time'] = False
            select_ids = []
            overlap = False
            for visit_id in visit_ids:
                overlap = False
                history_ids2 = history_obj.search(cr , uid , [('name','=',visit_id),('state','in',('confirm','allocated')),('company_id','=',event.company_id.id),
                                ('event_date','=',(datetime.datetime.strptime(str(datetime.datetime.strptime(str(event.event_start),"%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')),"%Y-%m-%d %H:%M:%S")).strftime('%Y-%m-%d'))])
                for history_id in history_ids2:
                    history_browse = history_obj.browse( cr ,uid , history_id)
                    if (event.event_start > history_browse.event_start and event.event_end < history_browse.event_end) :
                        overlap = True
                    elif (event.event_start > history_browse.event_start and event.event_start < history_browse.event_end) :
                        overlap = True
                    elif (event.event_end > history_browse.event_start and event.event_end < history_browse.event_end) :
                        overlap = True
                    elif (event.event_start == history_browse.event_start or event.event_end == history_browse.event_end) :
                        overlap = True
                    elif (history_browse.event_start > event.event_start and history_browse.event_start < event.event_end) :
                        overlap = True
                    elif (history_browse.event_end < event.event_end and history_browse.event_end > event.event_start) :
                        overlap = True
#                    elif (event.event_start == history_browse.event_end ) :
#                        overlap = True
                if overlap:
                    continue
                else:
                    trans.append(visit_id)
                last_visit_date = False
                if patient:
                    cr.execute("select max(event_date) from transporter_alloc_history where patient_id = %s and name = %s and state in ('allocated','confirm') and company_id = %s "%( patient.id , visit_id, event.company_id.id) )
                    last_visit_date = map(lambda x: x[0], cr.fetchall())
                transporter_browse = transporter.browse(cr ,uid , visit_id)
                transp_address = geo_query_address(transporter_browse.street or False , transporter_browse.zip or False ,transporter_browse.city or False, \
                                    transporter_browse.state_id and transporter_browse.state_id.name or False, transporter_browse.country_id and \
                                    transporter_browse.country_id.name or False)
                int_locations.append(transp_address)
                visit_list.append(False if patient and patient.interpreter_id and patient.interpreter_id.id == visit_id else True)
                preferred_lst.append(True if patient and patient.interpreter_id and patient.interpreter_id.id == visit_id else False)
                
                if last_visit_date and last_visit_date[0]:
                    select_ids.append(select_obj.create(cr ,uid ,{'transporter_id':visit_id,'event_id':ids[0],'visited':True,'visited_date':last_visit_date,
                                    'state': 'draft' ,'voicemail_msg':'','duration':dist_dict['duration'] or '',
                                    'distance':float(float(dist_dict['distance']) * 0.000621371) or 0}))
                else:
                    select_ids.append(select_obj.create(cr ,uid ,{'transporter_id':visit_id,'event_id':ids[0],'visited':True, 'state':'draft','voicemail_msg':'',
                                        'duration':dist_dict['duration'] or '','distance':float(float(dist_dict['distance']) * 0.000621371) or 0}))
            overlap = False
            for new_id in transp_ids:
                overlap = False
                history_ids2 = history_obj.search(cr , uid , [('name','=',new_id),('state','in',('confirm','allocated')),('company_id','=',event.company_id.id),
                               ('event_date','=',(datetime.datetime.strptime(str(datetime.datetime.strptime(str(event.event_start),"%Y-%m-%d %H:%M:%S").strftime('%Y-%m-%d %H:%M:%S')),"%Y-%m-%d %H:%M:%S")).strftime('%Y-%m-%d'))])
                for history_id in history_ids2:
                    history_browse = history_obj.browse( cr ,uid , history_id)
                    if (event.event_start > history_browse.event_start and event.event_end < history_browse.event_end) :
                        overlap = True
                    elif (event.event_start > history_browse.event_start and event.event_start < history_browse.event_end) :
                        overlap = True
                    elif (event.event_end > history_browse.event_start and event.event_end < history_browse.event_end) :
                        overlap = True
                    elif (event.event_start == history_browse.event_start or event.event_end == history_browse.event_end) :
                        overlap = True
                    elif (history_browse.event_start > event.event_start and history_browse.event_start < event.event_end) :
                        overlap = True
                    elif (history_browse.event_end < event.event_end and history_browse.event_end > event.event_start) :
                        overlap = True
#                    elif (event.event_start == history_browse.event_end ) :
#                        overlap = True
                if overlap:
                    continue
                else:
                    trans.append(new_id)
                transporter_browse = transporter.browse(cr ,uid , new_id)
                transp_address = geo_query_address(transporter_browse.street or False , transporter_browse.zip or False ,transporter_browse.city or False, \
                                    transporter_browse.state_id and transporter_browse.state_id.name or False, transporter_browse.country_id and \
                                    transporter_browse.country_id.name or False)

                int_locations.append(transp_address)
                visit_list.append(False)
                preferred_lst.append(False)
            key = self.get_key(cr,uid,len(trans))
            div = len(trans)/10
            rem = len(trans)% 10
            if div:
                for i,j in [(10*k,10*l) for k,l in zip( range(0,div), range(1,div+1) )]:#[(0,10),(10,20),(20,30),(30,40),(40,50),(50,60)]:
                    locs = '|'.join(int_locations[i:j])
                    event_locations = [location_address + '|' for m in range(0,10)]
                    try:
                        dist_dict = self.get_distance(cr, uid, ids, locs ,event_locations[0] , context=context, key=key)
                    except Exception, e :
                        dist_dict['duration'] = ''
                        dist_dict['distance'] = 0
                        print "Exception......",e.args
                        pass
                    dur, dist = [],[]
                    dur = dist_dict.get('duration',False) if dist_dict.get('duration',False) else [0 for n in range(0,10)]
                    dist = dist_dict.get('distance',False) if dist_dict.get('distance',False) else [0 for o in range(0,10)]
#                    print "dur+++++++++++++++++++",dur
#                    print "dist++++++++++++++++++",dist
#                    print "ints+++++++++++",ints[i:j]
#                    print "rates+++++++++++",rates[i:j]
#                    print "visitt+++++++++++",visit_list[i:j]
#                    print "preffefer+++++++++++",preferred_lst[i:j]
                    for trans_id,visited,preferred,duration,distance in zip(trans[i:j],visit_list[i:j],preferred_lst[i:j],dur,dist):
                        select_ids.append(select_obj.create(cr ,uid ,{'transporter_id':trans_id,'event_id':ids[0] ,'state':'draft','voicemail_msg':'',
                                            'duration':duration or '','distance':float(float(distance) * 0.000621371) or 0}))

            if rem:
                for i,j in [( div*10,div*10+rem)]:#[(0,10),(10,20),(20,30),(30,40),(40,50),(50,60)]:
#                    print "in remm++++++++++",i   ,      j
                    locs = '|'.join(int_locations[i:j])
                    event_locations = [location_address + '|' for r in range(i,j)]
                    key = self.get_key(cr,uid,len(int_locations))
                    try:
                        dist_dict = self.get_distance(cr, uid, ids, locs ,event_locations[0] , context=context, key=key)
                    except Exception, e :
                        print "Exception......",e.args
                        pass
                    dur , dist = [],[]
                    dur = dist_dict.get('duration',False) if dist_dict.get('duration',False) else [0 for p in range(0,10)]
                    dist = dist_dict.get('distance',False) if dist_dict.get('distance',False) else [0 for q in range(0,10)]
#                    print "dur+++++++++++++++++++",dur
#                    print "dist++++++++++++++++++",dist
                    for trans_id,visited,preferred,duration,distance in zip(trans[i:j],visit_list[i:j],preferred_lst[i:j],dur,dist):
                        select_ids.append(select_obj.create(cr ,uid ,{'transporter_id':trans_id,'event_id':ids[0] ,'state':'draft','voicemail_msg':'',
                                            'duration':duration or '','distance':float(float(distance) * 0.000621371) or 0}))
        self.write(cr ,uid ,ids , {'transporter_ids':[(6, 0, select_ids)]})
        return res

    def event_confirm_mail(self, cr, uid, ids, context=None):
        """ Send email to user when the event is confirmed """
        template_id = False
        ir_model_data = self.pool.get('ir.model.data')
        for event in self.browse(cr, uid, ids, context=context):
            try:
                if 'customer' not in context:
                    context['customer'] = False
                if 'interpreter' not in context:
                    context['interpreter'] = False
                if 'translator' not in context:
                    context['translator'] = False
                if 'transporter' not in context:
                    context['transporter'] = False
                if context['customer']:
                    template_id = ir_model_data.get_object_reference(cr, SUPERUSER_ID, 'bista_iugroup', 'confirmation_event_customer_new')[1]
                elif context['interpreter']:
                    template_id = ir_model_data.get_object_reference(cr, SUPERUSER_ID, 'bista_iugroup', 'confirmation_event_interpreter')[1]
                elif context['translator']:
                    template_id = ir_model_data.get_object_reference(cr, SUPERUSER_ID, 'bista_iugroup', 'confirmation_event_translator')[1]
                elif context['transporter']:
                    template_id = ir_model_data.get_object_reference(cr, SUPERUSER_ID, 'bista_iugroup', 'confirmation_event_transporter')[1]
                else:
                    template_id = ir_model_data.get_object_reference(cr, SUPERUSER_ID, 'bista_iugroup', 'confirmation_event_customer_new')[1]
            except ValueError:
                template_id = False
            if template_id:
                self.pool.get('email.template').send_mail(cr, uid, template_id, event.id)
        return True
    
    
    def send_sms_to_cust_inter_confirmed_job(self,cr,uid,ids,context={}):
        select_template_body_interp = None
        select_template_body_cust = None
        sms_template_obj = self.pool.get('sms.template.twilio')

        if context.get('assigned_interp',False):
            event_data = self.browse(cr, uid, ids[0])
            event_time_start = event_data.event_start_hr + ':' + event_data.event_start_min + event_data.am_pm
            event_time_end = event_data.event_end_hr + ':' + event_data.event_end_min + event_data.am_pm2

            if self.browse(cr, uid, ids[0]).assigned_interpreters[0].opt_for_sms:
                get_template_interp = sms_template_obj.search(cr, uid, [('action_for', '=', 'assigned_interp')])
                for template_ids in sms_template_obj.browse(cr, uid, get_template_interp):
                    select_template_body_interp = template_ids.sms_text
                get_contact_interp = self.browse(cr, uid, ids[0]).assigned_interpreters[0].phone
                if get_contact_interp:
                    sms_vals_interp = {
                        'sms_body': select_template_body_interp % (event_data.name, event_data.event_start_date,
                                                                   event_time_start, event_time_end,
                                                                   event_data.location_id.state_id.name,
                                                                   event_data.location_id.city,
                                                                   event_data.location_id.zip),
                        'sms_to': get_contact_interp
                    }
                    self.pool.get('twilio.sms.send').create(cr, uid, sms_vals_interp)
                else:
                    pass

            if self.browse(cr, uid, ids[0]).ordering_contact_id.opt_for_sms:
                get_template_cust = sms_template_obj.search(cr, uid, [('action_for', '=', 'assigned_customer')])
                for template_ids in sms_template_obj.browse(cr, uid, get_template_cust):
                    select_template_body_cust = template_ids.sms_text
                get_contact_cust = self.browse(cr, uid, ids[0]).ordering_contact_id.phone
                if get_contact_cust:
                    sms_vals_cust = {
                        'sms_body': select_template_body_cust % (event_data.name, event_data.event_start_date,
                                                                 event_time_start, event_time_end,
                                                                 event_data.location_id.state_id.name,
                                                                 event_data.location_id.city,
                                                                 event_data.location_id.zip),
                        'sms_to': get_contact_cust
                    }
                    self.pool.get('twilio.sms.send').create(cr, uid, sms_vals_cust)
                else:
                    pass

    def confirm_event(self, cr, uid, ids, context=None):
        ''' It confirms the event , creates history for interpreter(if not exists else updates) and
            creates task and a project as its parent with the no of hours '''
        if isinstance(ids, (int,long)): ids = [ids]
        if context is None: context = {}
        event_obj = self.pool.get('event')
        partner = self.pool.get('res.partner')
        ir_model_data = self.pool.get('ir.model.data')
        transporter = self.browse(cr ,uid ,ids[0]).transporter_id
        contact = self.browse(cr ,uid ,ids[0]).partner_id
        cur_obj = self.browse(cr ,uid ,ids[0])
        res, dist_dict, confirm, project_id, template_id,task_id  = {}, {}, True, False, False, False
        if cur_obj.partner_id.fee_note == True and cur_obj.fee_note_test == False:
            if cur_obj.state=='unauthorize':
                raise osv.except_osv(_("Warning"),_("Please attach Event Fee Note"))
            else:
                event_obj.write(cr, uid, ids[0], {'state':'unauthorize'})
                confirm = False
        if cur_obj.partner_id.order_note == True and cur_obj.order_note_test == False:
            if cur_obj.state == 'unauthorize':
                raise osv.except_osv(_("Warning"),_("Please attach SAF"))
            else:
                event_obj.write(cr, uid, ids[0], {'state':'unauthorize'})
                confirm = False
        if confirm == True:
            if cur_obj.multi_type:
                if len(cur_obj.assigned_interpreters) > 1 and cur_obj.multi_type == '1':
                    raise osv.except_osv(_('Error !'), _('You have assigned more than one Interpreter and Interpreter Type is Single Interpreter, Please cancel one Interpreter.'))
                if len(cur_obj.assigned_interpreters) < 2 and cur_obj.multi_type == '2':
                    raise osv.except_osv(_('Error !'), _('Please assign atleast two Interpreters as Interpreter Type is Double Interpreter.'))
                if len(cur_obj.assigned_interpreters) > 2 and cur_obj.multi_type == '2':
                    raise osv.except_osv(_('Error !'), _('You have assigned more than two Interpreters and Interpreter Type is Double Interpreter, Please cancel one Interpreter.'))
            event_start = datetime.datetime.strptime(cur_obj.event_start, tools.DEFAULT_SERVER_DATETIME_FORMAT)
            if cur_obj.event_end:
                event_end = datetime.datetime.strptime(cur_obj.event_end, tools.DEFAULT_SERVER_DATETIME_FORMAT)
            else:
                raise osv.except_osv(_('Warning!'),_('Please enter Event End Time in the event.'))
            DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            from_dt = datetime.datetime.strptime(str(event_start), DATETIME_FORMAT)
            from_dt = from_dt - datetime.timedelta(hours=8 , minutes=00)
            to_dt = datetime.datetime.strptime(str(event_end), DATETIME_FORMAT) - datetime.timedelta(hours=8 , minutes=00)
            timedelta = to_dt - from_dt
            min = float(timedelta.seconds /60.0)
            hour = int(min / 60)
            left_min = float(min - hour * 60)
            if left_min > 54.0:
                hour += 1.0
            elif left_min >34.0 and left_min <= 54.0:
                hour += 0.5
            date_planned = from_dt.strftime('%Y-%m-%d')
            if cur_obj.event_type == 'language':
                history_ids = cur_obj.history_id
                if not history_ids:

                    for interpreter in cur_obj.assigned_interpreters:
                        history_id = self.pool.get('interpreter.alloc.history').create(cr , SUPERUSER_ID ,{'partner_id':contact and contact.id or False,'name':interpreter and interpreter.id or False,
                                'event_id':ids[0],'event_date': date_planned,'event_start':cur_obj.event_start,'event_end':cur_obj.event_end,'state':'confirm','company_id': cur_obj.company_id and cur_obj.company_id.id or False,
                                'confirm_date':time.strftime('%Y-%m-%d %H:%M:%S')})
                        self.write(cr ,SUPERUSER_ID ,ids , {'history_id':[(6,0,[history_id])]})
                else:
                    for history_id in history_ids:
                        self.pool.get('interpreter.alloc.history').write(cr ,SUPERUSER_ID ,[history_id.id] ,{'partner_id':contact and contact.id or False,
                                'event_date': date_planned ,'event_id':ids[0],'event_start':cur_obj.event_start,'event_end':cur_obj.event_end,'state':'confirm','company_id': cur_obj.company_id and cur_obj.company_id.id or False,
                                 'confirm_date':time.strftime('%Y-%m-%d %H:%M:%S')})#'name':interpreter and interpreter.id or False,
            elif cur_obj.event_type == 'transport':
                history_id2 = cur_obj.history_id2
                if not history_id2:
                    history_id2 = self.pool.get('transporter.alloc.history').create(cr ,SUPERUSER_ID ,{'partner_id':contact and contact.id or False,'name':transporter and transporter.id or False,
                            'event_id':ids[0],'event_date': date_planned,'event_start':cur_obj.event_start,'event_end':cur_obj.event_end,'state':'confirm','company_id': cur_obj.company_id and cur_obj.company_id.id or False,
                            'confirm_date':time.strftime('%Y-%m-%d %H:%M:%S')})
                    self.write(cr ,uid ,ids , {'history_id2': history_id2})
                else:
                    self.pool.get('transporter.alloc.history').write(cr ,SUPERUSER_ID ,[history_id2.id] ,{'partner_id':contact and contact.id or False,'name':transporter and transporter.id or False,
                            'event_date': date_planned ,'event_id':ids[0],'event_start':cur_obj.event_start,'event_end':cur_obj.event_end,'state':'confirm','company_id': cur_obj.company_id and cur_obj.company_id.id or False,
                            'confirm_date':time.strftime('%Y-%m-%d %H:%M:%S')})
            if cur_obj.event_type == 'transport':
                location_address = ''
                location_address = geo_query_address(cur_obj.location_id.street or False , cur_obj.location_id.zip or False ,cur_obj.location_id.city or False, \
                                        cur_obj.location_id.state_id and cur_obj.location_id.state_id.name or False, cur_obj.location_id.country_id and cur_obj.location_id.country_id.name or False)
                transp_address = ''
                transp_address = geo_query_address(cur_obj.transporter_id.street or False , cur_obj.transporter_id.zip or False ,cur_obj.transporter_id.city or False, \
                                        cur_obj.transporter_id.state_id and cur_obj.transporter_id.state_id.name or False, cur_obj.transporter_id.country_id and cur_obj.transporter_id.country_id.name or False)
                dist_dict['duration'] = ''
                dist_dict['distance'] = 0
                try:
                    dist_dict = self.get_duration(cr, SUPERUSER_ID, ids, transp_address ,location_address , context=context)
                    #print "dist_dict.2.........",dist_dict
                except Exception ,e:
                    print "Exception..2....",e.args
                    pass
                self.write(cr ,uid ,ids ,{'km':float(float(dist_dict['distance']) * 0.000621371) or 0}) # miles conversion
            self.write(cr ,uid ,ids ,{'state':'confirmed', 'task_id':task_id})
            try:
                self.send_sms_to_cust_inter_confirmed_job(cr,uid,ids,context={'assigned_interp': True})
            except Exception: 
                pass

#          +++++ UPDATING LAST UPDATE DATE ++++++++
            if cur_obj.partner_id:
                partner.write(cr ,uid , [cur_obj.partner_id.id] , {'last_update_date': datetime.datetime.now()})
            if cur_obj.contact_id:
                partner.write(cr ,uid , [cur_obj.contact_id.id] , {'last_update_date': datetime.datetime.now()})
            if cur_obj.ordering_partner_id:
                partner.write(cr ,uid , [cur_obj.ordering_partner_id.id] , {'last_update_date': datetime.datetime.now()})
            if cur_obj.ordering_contact_id:
                partner.write(cr ,uid , [cur_obj.ordering_contact_id.id] , {'last_update_date': datetime.datetime.now()})
            for interpreter_id in cur_obj.assigned_interpreters:
                if interpreter_id:
                    partner.write(cr ,uid , [interpreter_id.id] , {'last_update_date': datetime.datetime.now()})
            if cur_obj.translator_id:
                partner.write(cr ,uid , [cur_obj.translator_id.id] , {'last_update_date': datetime.datetime.now()})
            if cur_obj.transporter_id:
                partner.write(cr ,uid , [cur_obj.transporter_id.id] , {'last_update_date': datetime.datetime.now()})
            if cur_obj.doctor_id:
                self.pool.get('doctor').write(cr ,uid , [cur_obj.doctor_id.id] , {'last_update_date': datetime.datetime.now()})
            if cur_obj.location_id:
                self.pool.get('location').write(cr ,uid , [cur_obj.location_id.id] , {'last_update_date': datetime.datetime.now()})
            if cur_obj.patient_id:
                self.pool.get('patient').write(cr ,uid , [cur_obj.patient_id.id] , {'last_update_date': datetime.datetime.now()}, context=context)
            if context.get('scheduler', False):
                self.enter_timesheet(cr, uid, [cur_obj.id], context)
            else:
                # SEND MAILS to the stakeholders
#                if not (cur_obj.suppress_email or (cur_obj.ordering_partner_id and cur_obj.ordering_partner_id.suppress_email) or \
#                    (cur_obj.ordering_contact_id and cur_obj.ordering_contact_id.suppress_email)):
#                    context['customer'] = True
#                    self.event_confirm_mail( cr, uid, ids, context=context)
                if cur_obj.event_type == 'transport' or cur_obj.event_type == 'translation':
                    if cur_obj.event_type == 'transport':
                        context['transporter'] = True
                        template_id = ir_model_data.get_object_reference(cr, uid, 'bista_iugroup', 'confirmation_event_transporter')[1]
                    elif cur_obj.event_type == 'translation':
                        context['translator'] = True
                        template_id = ir_model_data.get_object_reference(cr, uid, 'bista_iugroup', 'confirmation_event_translator')[1]
                    res = self.action_mail_send(cr, uid, ids, cur_obj,'event', template_id,  context=context)

                elif cur_obj.event_type == 'language':
                    context['interpreter'] = True
                    template_id = ir_model_data.get_object_reference(cr, uid, 'bista_iugroup', 'confirmation_event_interpreter')[1]
                    template_id_cust = ir_model_data.get_object_reference(cr, uid, 'bista_iugroup', 'confirmation_event_customer_new')[1]
                    try:
                        self.pool.get('email.template').send_mail(cr, uid, template_id, ids[0], True, context)
                    except Exception:
                        pass
                    res = self.action_mail_send(cr, uid, ids, cur_obj, 'event', template_id_cust,  context=context)

            #####################################################################
            tz, tz2 = False, False
            user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid)
            event_data = self.browse(cr,uid,ids,context)
            for event in event_data:
                if event.mobile_event and event.location_id:
                    if event.customer_timezone:
                        tz = pytz.timezone(event.customer_timezone) or pytz.utc
                    elif user.tz:
                        tz = pytz.timezone(user.tz) or pytz.utc
                    else:
                        tz = pytz.timezone('US/Pacific') or pytz.utc
                    tz2 = tz
                    if event.customer_timezone2:
                        tz2 = pytz.timezone(event.customer_timezone2) or pytz.utc
                    elif event.customer_timezone:
                            tz2 = pytz.timezone(event.customer_timezone) or pytz.utc
                    elif user.tz:
                        tz2 = pytz.timezone(user.tz) or pytz.utc
                    else:
                        tz2 = pytz.timezone('US/Pacific') or pytz.utc
                    if event.event_start_date:
                        if event.am_pm and event.am_pm == 'pm':
                            if event.event_start_hr < 12:
                                event.event_start_hr += 12
                        if event.am_pm and event.am_pm == 'am':
                            if event.event_start_hr == 12:
                                event.event_start_hr = 0
                        #print "event_start_hr...event_start_min......",event_start_hr,event_start_min
                        if event.event_start_hr == 24: # for the 24 hour format
                            event.event_start_hr = 23
                            event.event_start_min = 59
                    #print "event_start_hr...event_start_min......",event_start_hr,event_start_min
                            event_start = str(event.event_start_date) + ' ' + str(event.event_start_hr) + ':' + str(event.event_start_min) + ':00'
                    local_dt = tz.localize(datetime.datetime.strptime(str(event_start),DATETIME_FORMAT), is_dst=None)
                    local_dt1 = tz2.localize(datetime.datetime.strptime(str(event_end),DATETIME_FORMAT), is_dst=None)
                    duration=False
                    utc_dt = local_dt.astimezone (pytz.utc).strftime(DATETIME_FORMAT)
                    duration=((local_dt1-local_dt).seconds)/60
                    url = "https://iuconnectapp.com/job_schedules/create_event"
                    headers = {'Content-type': 'application/json','Accept': 'application/json'}
                    data = {"job_schedule" : 
                                {
                                "title"          :"Need an Interpreter",
                                "description"    :event.event_purpose or '',
                                "event_id"       :str(event.id),
                                "address_name"   : "Home",
                                "address_street1":event.location_id.street or '',
                                "address_street2":event.location_id.street2 or '',
                                "address_state"  :event.location_id.state_id and event.location_id.state_id.name or '' ,
                                "address_zipcode":event.location_id.zip,
                                "scheduled_at"   :utc_dt+" UTC" or ' ',
                                "language"         :event.language_id and event.language_id.name or '',
                                "duration"         :duration or 0 ,
                                "client_email"   :event.ordering_contact_id and event.ordering_contact_id.email or '' ,   #email or ''
                                "longitude":event.location_id.longitude ,
                                "latitude":event.location_id.latitude, 
                                "interpreter_email":event.assigned_interpreters and event.assigned_interpreters[0].email or event.assigned_interpreters[0].email2,
                                }
                            }
                    try:
                        r = requests.post(url, data=json.dumps(data),headers=headers,auth=('client','secret'))
                        result=r.json()
                        if result['status']=='true':
                            self.write(cr,uid,event.id,{'job_schedule_id':result['job_schedule']['job_schedule_id'],'mobile_sync':True})
                    except:
                        pass
            
        return res
    
    def enter_timesheet(self, cr, uid, ids, context=None):
        ''' function to create timesheet line for every one and redirect over the related task '''
        if isinstance(ids, (int,long)): ids = [ids]
        if context is None: context = {}
        event_obj = self.pool.get('event')
        proj_task_work_obj = self.pool.get('project.task.work')
        task_obj = self.pool.get('project.task')
        cur_obj = self.browse(cr ,SUPERUSER_ID , ids[0])
        task = self.browse(cr ,SUPERUSER_ID ,ids[0] ).task_id
        event = self.browse(cr ,SUPERUSER_ID , ids[0])
        current_time = datetime.datetime.now()
        user = self.pool.get('res.users').browse(cr , SUPERUSER_ID, uid)
        mod_obj = self.pool.get('ir.model.data')
        if user.user_type and user.user_type == 'vendor':
            res = mod_obj.get_object_reference(cr, SUPERUSER_ID, 'bista_iugroup', 'view_task_form_portal')
        else:
            res = mod_obj.get_object_reference(cr, SUPERUSER_ID, 'project', 'view_task_form2')
        res_id = res and res[1] or False
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        task_id = False
        if current_time <= datetime.datetime.strptime(event.event_start,DATETIME_FORMAT):
            raise osv.except_osv(_("Warning"),_("You Can not fill Timesheet before end of the event."))
        if task :
            task_id = task.id
        else:
            event_start = datetime.datetime.strptime(cur_obj.event_start, tools.DEFAULT_SERVER_DATETIME_FORMAT)
            if cur_obj.event_end:
                event_end = datetime.datetime.strptime(cur_obj.event_end, tools.DEFAULT_SERVER_DATETIME_FORMAT)
            else:
                raise osv.except_osv(_('Warning!'),_('Please enter Event End Time in the event.'))
            transporter = self.browse(cr ,uid ,ids[0]).transporter_id
            from_dt = datetime.datetime.strptime(str(event_start), DATETIME_FORMAT)
            from_dt = from_dt - datetime.timedelta(hours=8 , minutes=00)
            to_dt = datetime.datetime.strptime(str(event_end), DATETIME_FORMAT) - datetime.timedelta(hours=8 , minutes=00)
            timedelta = to_dt - from_dt
            min = float(timedelta.seconds /60.0)
            hour = int(min / 60)
            left_min = float(min - hour * 60)
            if left_min > 54.0:
                hour += 1.0
            elif left_min >34.0 and left_min <= 54.0:
                hour += 0.5
            date_planned = from_dt.strftime('%Y-%m-%d')

            task_name= ''
            if cur_obj.name:
                task_name += cur_obj.name + ': Task '
            if cur_obj.patient_id:
                task_name += 'for ' + cur_obj.patient_id.name
            if cur_obj.patient_id and cur_obj.patient_id.last_name:
                task_name += ' ' + cur_obj.patient_id.last_name
            int_ids, int_user_ids = [], []
            for interpreter in cur_obj.assigned_interpreters:
                int_ids.append(interpreter.id)
                int_user_ids.append(interpreter.user_id.id)
            if cur_obj.event_type == 'language':
                task_id = task_obj.create(cr, uid, {
                    'name': task_name ,
                    'date_deadline': str(date_planned) ,
                    'planned_hours': hour,
                    'remaining_hours': hour,
                    'user_id': int_user_ids and int_user_ids[0] or False,
                    'user_id_int': int_user_ids[1] if len(int_user_ids)==2 else int_user_ids[0],
                    'notes': cur_obj.comment,
                    'assigned_interpreters': [(6,0,int_ids)],
                    'description': cur_obj.name,
                    'date_start': cur_obj.event_start,
                    'date_end': cur_obj.event_end,
                    'event_id': ids[0],
                    'company_id':cur_obj.company_id and cur_obj.company_id.id or False,
                    },context=context)
            elif cur_obj.event_type == 'transport':
                task_id = task_obj.create(cr, SUPERUSER_ID, {
                    'name': task_name ,
                    'date_deadline': str(date_planned) ,
                    'planned_hours': hour,
                    'remaining_hours': hour,
                    'user_id': transporter.user_id and transporter.user_id.id or uid,
                    'notes': cur_obj.comment,
                    'transporter_id': transporter and transporter.id or False,
                    'description': cur_obj.name,
                    'date_start': cur_obj.event_start,
                    'date_end': cur_obj.event_end,
                    'event_id':ids[0],
                    'company_id':cur_obj.company_id and cur_obj.company_id.id or False,
                    },context=context)
            self.write(cr ,SUPERUSER_ID ,ids ,{'task_id': task_id})
            task = task_obj.browse(cr ,SUPERUSER_ID , task_id)
        cr.commit()
        new_task = task_obj.browse(cr ,SUPERUSER_ID , task_id)
        if new_task.work_ids:
            return {
                'name': _('Timesheet'),
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': [res_id],
                'res_model': 'project.task',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'res_id': new_task and new_task.id or False,
            }
        # Check for the module 'bista_lang_transport' if that is installed or not
#        module_obj = self.pool.get('ir.module.module')
#        if not module_obj.search(cr, 1, [['name', '=', 'bista_lang_transport'], ['state', 'in', ['installed', 'to upgrade']]], context=context):
#            raise osv.except_osv(_('Warning!'),_('Please install "bista_lang_transport" module first.'))
        if task:
            if cur_obj.event_type == 'lang_trans':
                task_for = 'interpreter'
                for interpreter in cur_obj.assigned_interpreters:
                    task_work_vals={
                        'name': '',#cur_obj.name + 'Task'
                        'task_id':task.id,
                        'date': cur_obj.event_start_date or time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        'hours': 0.0,
                        'am_pm': cur_obj.am_pm or 'am',
                        'am_pm2': cur_obj.am_pm2 or 'am',
                        'event_start_time':cur_obj.event_start,
                        'event_end_time':cur_obj.event_end,
                        'event_start_date': cur_obj.event_start_date or time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        'event_start_hr': cur_obj.event_start_hr or '',
                        'event_start_min': cur_obj.event_start_min or '',
                        'event_end_hr': cur_obj.event_end_hr or '',
                        'event_end_min': cur_obj.event_end_min or '',
                        'user_id': uid,#cur_obj.interpreter_id.user_id and cur_obj.interpreter_id.user_id.id
                        'task_for': task_for,
                        'interpreter_id': interpreter.id
                    }
                    proj_task_work_obj.create(cr,SUPERUSER_ID,task_work_vals,context)
                task_work_vals1={
                    'name': '',
                    'task_id':task.id,
                    'date': cur_obj.event_start_date or time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'hours': 0.0,
                    'am_pm': cur_obj.am_pm or 'am',
                    'am_pm2': cur_obj.am_pm2 or 'am',
                    'event_start_time':cur_obj.event_start,
                    'event_end_time':cur_obj.event_end,
                    'event_start_date': cur_obj.event_start_date or time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'event_start_hr': cur_obj.event_start_hr or '',
                    'event_start_min': cur_obj.event_start_min or '',
                    'event_end_hr': cur_obj.event_end_hr or '',
                    'event_end_min': cur_obj.event_end_min or '',
                    'user_id': uid,
                    'task_for': 'transporter',
                    'total_mileage_covered': 0.0,
                }
                proj_task_work_obj.create(cr, SUPERUSER_ID, task_work_vals1,context)
            elif cur_obj.event_type == 'language':
#                print "in event time++++++", cur_obj.event_start, cur_obj.event_end
                for interpreter in cur_obj.assigned_interpreters:
                    task_work_vals={
                        'name': '',#cur_obj.name + 'Task',
                        'task_id':task.id,
                        'date': cur_obj.event_start_date or time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        'hours': 0.0,
                        'am_pm': '',
                        'am_pm2': '',
                        'event_start_time':cur_obj.event_start,
                        'event_end_time':cur_obj.event_end,
                        'event_start_date': cur_obj.event_start_date or time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        'event_start_hr': '',
                        'event_start_min': '',
                        'event_end_hr': '',
                        'event_end_min': '',
                        'user_id': uid,
                        'task_for': 'interpreter',
                        'interpreter_id':interpreter.id
                    }
                    proj_task_work_obj.create(cr, SUPERUSER_ID, task_work_vals,context)
            elif cur_obj.event_type == 'transport':
                task_work_vals={
                    'name': '',
                    'task_id': task.id,
                    'date': cur_obj.event_start_date or time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'hours': 0.0,
                    'am_pm': cur_obj.am_pm or 'am',
                    'am_pm2': cur_obj.am_pm2 or 'am',
                    'event_start_time':cur_obj.event_start,
                    'event_end_time':cur_obj.event_end,
                    'event_start_date': cur_obj.event_start_date or time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'event_start_hr': cur_obj.event_start_hr or '',
                    'event_start_min': cur_obj.event_start_min or '',
                    'event_end_hr': cur_obj.event_end_hr or '',
                    'event_end_min': cur_obj.event_end_min or '',
                    'user_id': uid,
                    'task_for': 'transporter',
                    'total_mileage_covered': 0.0,
                }
                proj_task_work_obj.create(cr, SUPERUSER_ID, task_work_vals, context)
            event_obj.write(cr, SUPERUSER_ID, ids[0],{'state':'unbilled'})
            cr.commit()
            return {
                'name': _('Tasks Generated'),
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': [res_id],
                'res_model': 'project.task',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'res_id': task and task.id or False,
            }
        else:
            return True
    
    def event_confirm_schedular(self, cr, uid, ids, context=None):
        start_range = (datetime.datetime.now() - relativedelta.relativedelta(days=1)).strftime('%Y-%m-%d')
        end_range = datetime.datetime.now().strftime('%Y-%m-%d')
        event_ids = self.search(cr, uid, [('event_start_date','>=',start_range),('event_start_date','<',end_range),('state','=','allocated')])
#        print "event_ids.........",len(event_ids)
        for event in event_ids:
            context['scheduler'] = True
            self.confirm_event(cr, uid, [event], context)
        return True
    
    def view_timesheet(self ,cr ,uid ,ids ,context=None):
        ''' Function to view timesheet when timesheet is entered '''
        if isinstance(ids, (int,long)): ids = [ids]
        if context is None: context = {}
        task = self.browse(cr ,SUPERUSER_ID ,ids[0] ).task_id
        user = self.pool.get('res.users').browse(cr , SUPERUSER_ID, uid)
        if task:
            mod_obj = self.pool.get('ir.model.data')
            if user.user_type and user.user_type == 'vendor':
                res = mod_obj.get_object_reference(cr, SUPERUSER_ID, 'bista_iugroup', 'view_task_form_portal')
            else:
                res = mod_obj.get_object_reference(cr, SUPERUSER_ID, 'project', 'view_task_form2')
            res_id = res and res[1] or False
            return {
                'name': _('Tasks Generated'),
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': [res_id],
                'res_model': 'project.task',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'res_id': task and task.id or False,
            }
        else:
            return True
    
    def onchange_validate_email(self, cr, uid, ids, approving_mgr_email= False, verifying_mgr_email=False, context={}):
        '''Function to validate email on onchange event'''
        res, res['value'], res['warning']={}, {}, {}
        if approving_mgr_email:
            if not re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", approving_mgr_email):
                warning = {
                    'title': _('Invalid Email'),
                    'message' : _('Please enter a valid Approoving Manager Email address')
                    }
                res['warning'] = warning
                res['value']['approving_mgr_email'] =''
        if verifying_mgr_email:
            if not re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", verifying_mgr_email):
                warning = {
                    'title': _('Invalid Email'),
                    'message' : _('Please enter a valid Verifying Manager Email address')
                    }
                res['warning'] = warning
                res['value']['verifying_mgr_email'] =''
        return res
    
    def onchange_zone_id(self, cr, uid, ids, zone_id=False, context={}):
        '''Function to auto fill scheduler on the basis of zone '''
        vals = {}
        if zone_id:
            user_ids = self.pool.get('res.users').search(cr, uid, [('zone_id','=',zone_id)])
            if user_ids:
                vals={
                    'scheduler_id': user_ids and user_ids[0]
                }
        return {'value': vals}

    def onchange_claimant(self ,cr ,uid ,ids , claimant_id, event_start_date, context=None):
        ''' Onchange Function to bring Payer and adjuster from Claimant(patient) '''
        vals, warning = {}, {}
        event_obj = self.pool.get('event')
        if claimant_id:
            claimant = self.pool.get('patient').browse(cr,uid,claimant_id)
            vals = {
                'employer': claimant.employer,
                'employer_contact': claimant.employer_contact,
                'ssnid': claimant.ssnid,
                'dob': claimant.birthdate,
                'gender': claimant.gender,
                'claim_no': claimant.claim_no or claimant.claim_no2 or '',
                'medical_no': claimant.ssnid or '',#claimant.claim_no or claimant.claim_no2,
                'comment': claimant.comment or '',
            }
            if claimant.billing_partner_id:
                vals['partner_id'] = claimant.billing_partner_id and claimant.billing_partner_id.id or False
            if claimant.billing_contact_id:
                vals['contact_id'] = claimant.billing_contact_id and claimant.billing_contact_id.id or False
            if event_start_date:
                event_ids = event_obj.search(cr, uid, [('patient_id','=',claimant_id),('event_start_date','=',event_start_date)])
                if ids:
                    if isinstance(ids, (int,long)): ids = [ids]
                    if ids[0] in event_ids:
                        event_ids.remove(ids[0])
                if event_ids:
                    warning = {
                            'title': _('Warning!'),
                            'message' : 'Event already created for this date and for this Patient are - '
                        }
                    for event in event_obj.browse(cr, uid, event_ids):
                        warning['message'] += event.name + ', '
        return {'value': vals, 'warning': warning}

    def onchange_is_authorized(cr , uid , ids, is_authorized, context=None):
        return {'value': {'authorize_contact_id' : False, 'authorize_date': False}}

    def get_default_country(self, cr, uid , context={}):
        """Return the Default Country """
        proxy = self.pool.get('ir.config_parameter')
        default_country = proxy.get_param(cr, uid, 'default_country')
        if not default_country:
            raise osv.except_osv(_('Config Error !'), _('Please Default Country as US in config parameters.'))
        return default_country.strip()
    
    def onchange_phone(self, cr, uid, ids, phone, phone2,phone3, phone4, context=None):
        ''' function to change in the format of selected default country '''
        result, new_phone = {}, ''
        result['value'] = {}
        def_country = self.get_default_country(cr , uid, context=context)
        if phone:
            try:
                pn = phonumbers_converter._parse(phone, def_country)
                if  pn:
                    new_phone = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.E164)
                else:
                    new_phone = None
            except phonenumbers.NumberParseException:
                phone = None
                pass
            result['value']['phone'] = new_phone
        new_phone = ''
        if phone2:
            try:
                pn = phonumbers_converter._parse(phone2, def_country)
                if  pn:
                    new_phone = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.E164)  
                else:
                    new_phone = None
            except phonenumbers.NumberParseException:
                phone2 = None
                pass
            result['value']['phone2'] = new_phone
        if phone3:
            try:
                pn = phonumbers_converter._parse(phone3, def_country)
                if  pn:          
                    new_phone = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.E164)  
                else:
                    new_phone = None
            except phonenumbers.NumberParseException:
                phone3 = None
                pass  
            result['value']['phone3'] = new_phone
        if phone4:
            try:
                pn = phonumbers_converter._parse(phone4, def_country)
                if  pn:          
                    new_phone = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.E164)  
                else:
                    new_phone = None
            except phonenumbers.NumberParseException:
                phone4 = None
                pass  
            result['value']['phone4'] = new_phone
        return result
    
    def mark_as_done(self, cr, uid, ids, context=None):
        ''' function to set event as done '''
        if isinstance(ids, (int,long)): ids = [ids]
        if context is None: context = {}
        self.write(cr ,uid ,ids , {'state':'done'})
        return True
    
    def cancel_event(self, cr, uid, ids, context=None):
        ''' function to cancel event and cancel Allocation History '''
        if context is None: context = {}
        context = dict(context, active_ids=ids, active_model=self._name)
        cancel_id = self.pool.get('cancel.event.wizard').create(cr, uid, {}, context=context)
        return {
            'name':_("Cancel Event"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'cancel.event.wizard',
            'res_id': cancel_id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': context,
        }

    def upload_attachment(self, cr, uid, ids, context=None):
        ''' function to Upload Attachment with Document type '''
        if context is None: context = {}
        context = dict(context, active_ids=ids, active_model=self._name)
        wizard_id = self.pool.get('upload.attachment.wizard').create(cr, uid, {}, context=context)
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr,SUPERUSER_ID,'bista_iugroup', 'upload_attachments_wizard')
        view_id = view_ref[1] if view_ref else False
        return {
            'name':_("Upload Attachment"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'upload.attachment.wizard',
            'res_id': wizard_id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': context,
        }
    
    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        ''' Empty some fields on change of company in the event Form '''
        if context.get('default_is_follow_up',False):
            return {}
        domain = {}
        val = {
            'partner_id': False ,
            'contact_id': False ,
            'ordering_partner_id': False ,
            'ordering_contact_id': False ,
            'language_id': False ,
            'language_id2': False ,
            'doctor_id': False ,
            'location_id': False,
            'zone_id': False,
            'patient_id':False,
            'fee_note_status_id': False,
            'event_out_come_id': False,
            'scheduler_id': False,
            'sales_representative_id': False,
        }
        domain['ordering_contact_id'] = [('customer', '=', 1),('cust_type', '=', 'contact'),('is_company', '=',0),('company_id','=',company_id)]
        domain['contact_id'] = [('customer', '=', 1),('cust_type', '=', 'contact'),('is_company', '=',0),('company_id','=',company_id)]
        return {'value': val, 'domain': domain}

    def onchange_partner_id(self, cr, uid, ids, part, company_id, context=None):
        ''' bring contact info from customer '''
        domain, customer_group = {}, False
        partner_obj = self.pool.get('res.partner')
        if not part:
#            contact_ids = partner_obj.search(cr, SUPERUSER_ID, [('company_id','=',company_id),('cust_type','=','contact'),('is_company','=',0),('customer','=',1)])
#            if contact_ids:
#                domain.update({'contact_id':[('id', 'in', contact_ids)],
#                })
            domain['contact_id'] = [('customer', '=', 1),('cust_type', '=', 'contact'),('is_company', '=',0),('company_id','=',company_id)]
            return {'value': {'ref': False, 'customer_group':False, 'customer_basis': False},  'domain': domain}
        part = partner_obj.browse(cr, SUPERUSER_ID, part, context=context)
        customer_group = part.customer_group_id and part.customer_group_id.name and part.customer_group_id.name.lower() or ''
        val = {
            'customer_group': customer_group,
            'special_discount': part.discount or 0.00,
            'customer_basis': part.customer_basis,
            'sales_representative_id': part.sales_representative_id and part.sales_representative_id.id or False,
        }
        contact_ids = partner_obj.search(cr, SUPERUSER_ID, [('parent_id','=',part.id)], context=context)
        if contact_ids:
            domain.update({'contact_id':[('id', 'in', contact_ids)],
            })
        if part.scheduler_id:
            val['scheduler_id'] = part.scheduler_id.id
        return {'value': val, 'domain': domain}
    
    def onchange_order_partner_id(self, cr, uid, ids, part, company_id, context=None):
        ''' bring contact info from customer '''
        val, domain = {}, {}
        partner_obj = self.pool.get('res.partner')
#        user = self.pool.get('res.users').browse(cr , SUPERUSER_ID, uid)
        if not part:
#            contact_ids = partner_obj.search(cr, SUPERUSER_ID, [('company_id','=',company_id),('cust_type','=','contact'),('is_company','=',0),('customer','=',1)])
#            print "contact_ids.......",len(contact_ids)
#            if contact_ids:
#                domain.update({'ordering_contact_id':[('id', 'in', contact_ids)],
#                })
            domain['ordering_contact_id'] = [('customer', '=', 1),('cust_type', '=', 'contact'),('is_company', '=',0),('company_id','=',company_id)]
#            if user.user_type and user.user_type in ('customer','contact'):
#                patient_ids = self.pool.get('patient').search(cr, uid, [('ordering_partner_id','=',part.id),('company_id','=',company_id)], context=context)
#                if patient_ids:
#                    domain.update({'patient_id':[('id', 'in', patient_ids)]})
#                location_ids = self.pool.get('location').search(cr, uid, [('ordering_partner_id','=',part.id),('company_id','=',company_id)], context=context)
#                if location_ids:
#                    domain.update({'patient_id':[('id', 'in', location_ids)]})
            return {'value': {'customer_basis': False }, 'domain': domain}
        part = partner_obj.browse(cr, SUPERUSER_ID, part, context=context)
        val = {
            'customer_basis': part.customer_basis,
#            'suppress_email': part.suppress_email,
        }
#        if user.user_type and user.user_type in ('customer','contact'):
#            patient_ids = self.pool.get('patient').search(cr, uid, [('ordering_partner_id','=',part.id),('company_id','=',company_id)], context=context)
#            if patient_ids:
#                domain.update({'patient_id':[('id', 'in', patient_ids)]})
#            location_ids = self.pool.get('location').search(cr, uid, [('ordering_partner_id','=',part.id),('company_id','=',company_id)], context=context)
#            if location_ids:
#                domain.update({'patient_id':[('id', 'in', location_ids)]})
        contact_ids = partner_obj.search(cr, SUPERUSER_ID, [('parent_id','=',part.id)], context=context)
        if contact_ids:
            domain.update({'ordering_contact_id':[('id', 'in', contact_ids)]})
        return {'value': val, 'domain': domain}
    
    def onchange_contact_id(self, cr, uid, ids, part, context=None):
        ''' bring contact info from customer '''
        if not part:
            return {'value': {}}
        part = self.pool.get('res.partner').browse(cr, SUPERUSER_ID, part, context=context)
        if part.parent_id:
            val = {
                'partner_id': part.parent_id.id ,
            }
        else:
            val={}
        return {'value': val}

    def onchange_ordering_contact_id(self, cr, uid, ids, part, context=None):
        ''' bring contact info from customer '''
        if not part:
            return {'value': {}}
        val = {}
        part = self.pool.get('res.partner').browse(cr, SUPERUSER_ID, part, context=context)
        if part.parent_id:
            if part.parent_id.order_note:
                val['order_note'] = True
            if part.parent_id.customer_group_id and part.parent_id.customer_group_id.name:
                val['customer_group'] = part.parent_id.customer_group_id.name.lower() or ''
            val['ordering_partner_id'] = part.parent_id.id
        return {'value': val}
        
    def onchange_doctor_id(self, cr, uid, ids, doct, company_id, context=None):
        ''' Set Domain on the basis of doctor  '''
        domain, value = {}, {}
        if context.get('default_is_follow_up',False):
            return {}
        if not doct:
            loc_ids = self.pool.get('location').search(cr, SUPERUSER_ID, [('company_id','=',company_id)])
            if loc_ids:
                domain.update({'location_id':[('id', 'in', loc_ids)],
                })
            return {'value': {'location_id': False}, 'domain': domain}
        doctor_obj = self.pool.get('doctor')
        loc_ids = []
        for location in doctor_obj.browse(cr, SUPERUSER_ID, doct, context=context).location_ids:
            loc_ids.append(location.id)
        if loc_ids:
            value.update({'location_id':loc_ids[0]})
        domain.update({'location_id':[('id', 'in', loc_ids)]})
        return {'value': value, 'domain': domain }

    def get_zone_from_zip(self , cr , uid ,ids , context=None):
        val,zip_ids,time_zone,zone = {},False,False,False
        zip_code = self.pool.get('zip.code')
        location = self.pool.get('location')
        for loc in [location.browse(cr, SUPERUSER_ID, id, context=context) for id in location.search(cr, SUPERUSER_ID, [], context=context)]:
            zone, zip_ids = False, []
            if loc.zip:
                zip_ids = zip_code.search(cr, SUPERUSER_ID, [('name','=',loc.zip)])
            if zip_ids:
                for zip_id in zip_ids:
                    time_zone = zip_code.browse(cr, SUPERUSER_ID, zip_id).time_zone
                zone = _timezone_event.get(int(time_zone),False)
            self.pool.get('location').write(cr, SUPERUSER_ID, [loc.id], {'timezone':zone})
        return True
    
    def onchange_location_id(self , cr , uid ,ids , loc, customer_basis, part=False, context=None):
        ''' bring contact info from doctor/location  and get timezone and bring metazone and scheduler'''
        val, zip_ids, time_zone, zone, zone_id = {}, False, False, False, False
        user_obj = self.pool.get('res.users')
#        zip_code = self.pool.get('zip.code')
        if not loc:
            return {'value': {'zone_id': False, 'customer_timezone': False}}
        loc = self.pool.get('location').browse(cr, SUPERUSER_ID, loc, context=context)
#        if loc.zip:
#            zip_ids = zip_code.search(cr, SUPERUSER_ID, [('name','=',loc.zip)])
#        if zip_ids:
#            for zip_id in zip_ids:
#                time_zone = zip_code.browse(cr, SUPERUSER_ID, zip_id).time_zone
#            zone = _timezone_event.get(int(time_zone), False)
        if loc.timezone:
            val['customer_timezone'] = loc.timezone
        else:
            time_zone = self.pool.get('location').get_timezone(cr, SUPERUSER_ID, [loc.id], context=context)
            val['customer_timezone'] = time_zone
        if part:
            part = self.pool.get('res.partner').browse(cr, SUPERUSER_ID, part, context=context)
        if loc.zone_id and loc.zone_id.meta_zone_id:
            zone_id = loc.zone_id.meta_zone_id.id
            val['zone_id'] = zone_id
        if customer_basis and part and part.scheduler_id:
            val['scheduler_id'] = part.scheduler_id and part.scheduler_id.id
        else:
            user_ids = user_obj.search(cr, SUPERUSER_ID, [('zone_id','=',zone_id)])
            if user_ids and user_ids[0] == SUPERUSER_ID:
                val['scheduler_id'] = uid
            else:
                val['scheduler_id'] = user_ids and user_ids[0] or False
        if loc.company_id:
            if loc.company_id.name == 'ASIT' and loc.company_id.scheduler_id:
                val['scheduler_id'] = loc.company_id.scheduler_id.id or False
#        print "val...........",val
        if 'zone_id' not in val or not val['zone_id']:
            out_of_state_ids = []
            if loc.company_id:
                out_of_state_ids = self.pool.get('meta.zone').search(cr, SUPERUSER_ID, [('name','=','Out of State'),('company_id','=',loc.company_id.id)])
            else:
                out_of_state_ids = self.pool.get('meta.zone').search(cr, SUPERUSER_ID, [('name','=','Out of State')])
            if out_of_state_ids:
                val['zone_id'] = out_of_state_ids and out_of_state_ids[0]
                if val['zone_id']:
                    user_ids = user_obj.search(cr, SUPERUSER_ID, [('zone_id','=',val['zone_id'])])
                    if user_ids and user_ids[0] == SUPERUSER_ID:
                        val['scheduler_id'] = uid
                    else:
                        val['scheduler_id'] = user_ids and user_ids[0]
#            if loc.zone_id and loc.zone_id.meta_zone_id:
#                zone_id = loc.zone_id.meta_zone_id.id
#                val['zone_id'] = zone_id
        
#        print "user_id.........",user_id
#        if user_id:
#            scheduler_user = user_obj.browse(cr, SUPERUSER_ID, user_id)
#            if scheduler_user.company_id and loc.company_id and scheduler_user.company_id.id == loc.company_id.id:
#                val['scheduler_id'] = scheduler_user.id
#            val['scheduler_id'] = scheduler_user.id
#        print "val.........",val
        return {'value': val}

################### Default Functions copied from res.partner ####################
    def unlink(self, cr, uid, ids, context=None):
        raise osv.except_osv(_('Warning!'),_('You are not allowed to delete this record.Alternatively you can cancel it.'))
        return super(event, self).unlink(cr, uid, ids, context=context)
    
    def copy(self, cr, uid, id, default=None, context=None):
        ''' Function ovver ridden to blank data for different type of duplication '''
        if default is None:
            default = {}
        default.update({
            'is_follow_up': False,
            'source_event_id': False,
            'state': context.get('state', 'draft'),
            'order_note_test': False,
            'fee_note_test': False,
            'employer_contact': '',
            'event_note': '',
            'function': '',
            'claim_no': '',
            'claim_date': False,
            'is_authorized': False,
            'authorize_date': False,
            'special_discount': 0.0,
            'authorize_date': False,
            'fee_note_status_id': False,
            'invoice_ids': [],
            'history_id': [],
            'history_id2': False,
            'history_id3': False,
            'task_id': False,
            'cust_invoice_id': False,
            'supp_invoice_ids': [],
            'supp_invoice_id2': False,
            'event_follower_ids': [],
            'assigned_interpreters': [],
            'interpreter_id2': [],
            'transporter_id': [],
            'transporter_id2': [],
            'translator_ids': [],
            'interpreter_ids': [],
            'interpreter_ids2': [],
            'transporter_ids2': [],
            'translator_ids2': [],
            'translation_assignment_history_id': False,
            'event_id': False,
            'translate_attach_ids': False,
            'total_cost': 0.0,
            'ssnid': '',
            'quickbooks_id': '',
            'gender': False,
            'cust_gpuid': '',
            'cust_csid': '',
            'nuid_code': '',
            'department': '',
            'schedule_event_time': False,
            'sales_representative_id': False,
            'scheduler_id': False,
            'event_out_come_id': False,
        })
        if context.get('follow_up',False) == True:
            default.update({
                'source_event_id': id,
                'is_follow_up': True,
                'assigned_interpreters': [],
                'transporter_id': False,
                'interpreter_ids': [],
                'interpreter_ids2': [],
                'transporter_ids': [],
                'transporter_ids2': [],
                'translator_ids': [],
                'translator_ids2': [],
                'cancel_reason_id': False,
        })
        elif context.get('recurring', False):
            default.update({
                'event_start': context.get('recurring',False),
                'event_end': False,
                'assigned_interpreters': [],
                'transporter_id': False,
                'interpreter_ids': [],
                'interpreter_ids2': [],
                'transporter_ids': [],
                'transporter_ids2': [],
                'translator_ids': [],
                'translator_ids2': [],
                'invoice_ids': [],
                'history_id': False,
                'history_id2': False,
                'task_id': False,
                'event_follower_ids': False,
                'cancel_reason_id': False,
            })
        if context.get('copy_wizard_vals'):
            default.update({
                'ref': context.get('ref', ''),
                'cost_center': context.get('cost_center', ''),
                'cust_gpuid': context.get('cust_gpuid', ''),
                'cust_csid': context.get('cust_csid', ''),
                'event_note': context.get('event_note', ''),
                'department': context.get('department', ''),
                'scheduler_id':context.get('scheduler_id','')
            })
        return super(event, self).copy(cr, uid, id, default, context)
    
    def reschedule_event(self, cr, uid, ids, context=None):
        ''' function to set event as Unscheduled '''
        if isinstance(ids, (int,long)): ids = [ids]
        if context is None: context = {}
        select_obj = self.pool.get('select.interpreter.line')
        for event in self.browse( cr ,uid ,ids):
            if event.event_type == 'language':
                if event.history_id:
                    for history in event.history_id:
                        self.pool.get('interpreter.alloc.history').write(cr ,uid ,[history.id] , {'state':'draft'} )
                if event.history_id2:
                    self.pool.get('transporter.alloc.history').write(cr ,uid ,[event.history_id2.id] , {'state':'draft'} )
                if event.history_id3:
                    self.pool.get('translator.alloc.history').write(cr ,uid ,[event.history_id3.id] , {'state':'draft'} )
            for invoice_id in event.supp_invoice_ids:
                self.pool.get('account.invoice').unlink(cr ,uid , [invoice_id.id])
            for line in event.interpreter_ids:
                select_obj.unlink(cr ,uid , [line.id])
            for line in event.interpreter_ids2:
                select_obj.unlink(cr ,uid , [line.id])
            for line in event.transporter_ids:
                select_obj.unlink(cr ,uid , [line.id])
            for line in event.transporter_ids2:
                select_obj.unlink(cr ,uid , [line.id])
            for line in event.translator_ids:
                select_obj.unlink(cr ,uid , [line.id])
            for line in event.translator_ids2:
                select_obj.unlink(cr ,uid , [line.id])
            interpreter_list = []
            if event.assigned_interpreters:
                for interpreter in event.assigned_interpreters:
                    interpreter_list.append(interpreter.id)
                cr.execute("""delete from event_partner_rel where event_id = %s and interpreter_id in  %s """,(event.id, tuple(interpreter_list)) )
            interpreter_lines = []
            if event.interpreter_line_ids:
                for line in event.interpreter_line_ids:
                    interpreter_lines.append(line.id)
                cr.execute("""delete from event_interpreter_rel where event_id = %s and interpreter_id in  %s """,(event.id, tuple(interpreter_lines)) )
            follower_list = []
            if event.event_follower_ids:
                for line in event.event_follower_ids:
                    follower_list.append(line.id)
                cr.execute("""delete from event_followers_rel1 where event_id = %s and user_id in  %s """,(event.id, tuple(follower_list)) )
        self.write(cr ,uid ,ids , {
                'interpreter_id': False,
                'transporter_id': False,
                'interpreter_ids': False,
                'interpreter_ids2': False,
                'assigned_interpreters': False,
                'transporter_ids': False,
                'transporter_ids2': False,
                'state': 'draft',
                'invoice_ids': False,
                'history_id': False,
                'history_id2': False,
                'task_id': False,
                'event_follower_ids': False,
                'cancel_reason_id': False,
                'event_out_come_id': False,
            })
        self.message_post(cr, uid, ids, body="This Event was rescheduled .", subject="Event Rescheduled", context=context)
        return True
    
    def follow_up(self, cr, uid, ids, context=None):
        ''' function to create Follow Up of the Event with some default data but date Empty'''
        if context is None: context = {}
        context = dict(context, active_ids=ids, active_model=self._name)
        event = self.browse(cr, uid, ids[0])
        context.update({
            'default_partner_id': event.partner_id and event.partner_id.id or False,
            'default_contact_id': event.contact_id and event.contact_id.id or False,
            'default_ordering_partner_id': event.ordering_partner_id and event.ordering_partner_id.id or False,
            'default_ordering_contact_id': event.ordering_contact_id and event.ordering_contact_id.id or False,
            'default_location_id': event.location_id and event.location_id.id or False,
            'default_doctor_id': event.doctor_id and event.doctor_id.id or False,
            'default_language_id': event.language_id and event.language_id.id or False,
            'default_patient_id': event.patient_id and event.patient_id.id or False,
            'default_company_id': event.company_id and event.company_id.id or False,
            'default_is_follow_up': True,
            'default_source_event_id': event.id,
            'default_comment': event.comment or '',
            'default_event_note': event.event_note or '',
            'default_mental_prog': event.mental_prog or False,
            'default_zone_id': event.zone_id and event.zone_id.id or False,
            'default_appointment_type_id': event.appointment_type_id and event.appointment_type_id.id or False,
            'default_certification_level_id': event.certification_level_id and event.certification_level_id.id or False,
            'default_event_purpose': event.event_purpose or False,
            'default_multi_type': event.multi_type or False,
            'default_scheduler_id': event.scheduler_id and event.scheduler_id.id or False,
            'default_sales_representative_id': event.sales_representative_id and event.sales_representative_id.id or False,
        })
        vid = False
        mod_obj = self.pool.get('ir.model.data')
        if event.event_type == 'language':#action_event_form_language
            vid = mod_obj.get_object_reference(cr, SUPERUSER_ID, 'bista_iugroup', 'view_event_form')
        elif event.event_type == 'transport':
            vid = mod_obj.get_object_reference(cr, SUPERUSER_ID, 'bista_lang_transport', 'view_referral_form')
        elif event.event_type == 'translation':
            vid = mod_obj.get_object_reference(cr, SUPERUSER_ID, 'bista_iugroup', 'view_translation_event_form')
        elif event.event_type == 'lang_trans':
            vid = mod_obj.get_object_reference(cr, SUPERUSER_ID, 'bista_lang_transport', 'view_referral_form')
        else :
            vid = mod_obj.get_object_reference(cr, SUPERUSER_ID, 'bista_iugroup', 'view_event_form')
        vid = vid and vid[1] or False,
        return {
            'name':_("Follow Up Event"),
            'view_mode': 'form',
            'view_id': vid,
            'view_type': 'form',
            'res_model': 'event',
            'res_id': False,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current_edit',
            'domain': '[]',
            'context': context,
        }
        
    def name_get(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').browse(cr, SUPERUSER_ID, uid)
        if context is None: context = {}
        if isinstance(ids, (int, long)): ids = [ids]
        res = []
        for record in self.browse(cr, SUPERUSER_ID, ids, context=context):
            name = record.name
            if  user.user_type and user.user_type in ('staff', 'admin'):
                if record.partner_id:
                    name =  "%s [%s]" % (name, record.partner_id.name)
            res.append((record.id, name))
        return res
    
    def confirm_translation_event( self , cr ,uid ,ids ,context=None):
        ''' It confirms the event , creates history for translator(if not exists else updates) '''
        if isinstance(ids, (int,long)): ids = [ids]
        if context is None: context = {}
        for cur_obj in self.browse(cr ,uid ,ids):
            if not cur_obj.event_end:
                raise osv.except_osv(_('Warning!'),_('Please enter Event End Time in the event.'))
            history_id = cur_obj.history_id3
            if not history_id:
                history_id = self.pool.get('translator.alloc.history').create(cr ,uid ,{'name':cur_obj.translator_id and cur_obj.translator_id.id or False,
                        'event_id':ids[0],'event_date': cur_obj.event_start_date or False,'event_start':cur_obj.event_start,'event_end':cur_obj.event_end,'state':'confirm'})
                self.write(cr ,uid ,ids , {'history_id3':history_id})
            else:
                self.pool.get('translator.alloc.history').write(cr ,uid ,[history_id.id] ,{'name': cur_obj.translator_id and cur_obj.translator_id.id or False,
                        'event_date': cur_obj.event_start_date or False ,'event_id':ids[0],'event_start':cur_obj.event_start,'event_end': cur_obj.event_end,'state':'confirm'})
            self.write(cr ,uid ,ids ,{'state':'confirmed'})
#            if not cur_obj.suppress_email:
#                context['customer'] = True
#                self.event_confirm_mail( cr, uid, ids, context=context)
#            if cur_obj.event_type == 'translation':
#                context['translator'] = True
#            context['customer'] = False
#            self.event_confirm_mail( cr, uid, ids, context=context)
        return True
    
    def create_supp_inv(self, cr, uid, ids, context=None):
        """ Generates invoice for given ids of Task """
        journal_obj = self.pool.get('account.journal')
        inv_obj = self.pool.get('account.invoice')
        inv_line_obj = self.pool.get('account.invoice.line')
        for cur_obj in self.browse(cr, uid, ids):
            if cur_obj.view_interpreter_inv:
                return cur_obj.view_interpreter_inv.id
            if not cur_obj.translator_id:
                raise osv.except_osv(_('Warning!'),_('No Translator is assigned to this event!'))
            journal_ids = journal_obj.search(cr, uid, [('type', '=','purchase'),('company_id', '=', cur_obj.company_id.id)], limit=1)
            if not journal_ids:
                raise osv.except_osv(_('Error!'),
                    _('Define purchase journal for this company: "%s" (id:%d).') % (cur_obj.company_id.name, cur_obj.company_id.id))
            rec_acc_id = cur_obj.translator_id.property_account_payable
            if rec_acc_id.company_id and cur_obj.translator_id.company_id and rec_acc_id.company_id.id != cur_obj.translator_id.company_id.id:
                raise osv.except_osv(_('Warning!'),_('Please Login with proper user for company %s')%(cur_obj.translator_id.company_id and cur_obj.translator_id.company_id.name ))
            product_ids = self.pool.get('product.product').search(cr ,uid ,[('type','=','service'),('sale_ok','=',True),('active','=',True),('company_id', '=',cur_obj.company_id.id),('service_type','=','translator')])
            if not product_ids:
                raise osv.except_osv(_('Warning!'),_('Please define a Translator service type product first.'))
            product = self.pool.get('product.product').browse(cr ,uid ,product_ids[0])

            acc_id = product.property_account_expense.id
            if not acc_id:
                acc_id = product.categ_id.property_account_expense_categ.id
            if not acc_id:
                raise osv.except_osv(_('Error!'), _('There is no expense account defined for this product: "%s" (id:%d).') % (product.name, product.id,))
            total_page = 0.0
            for each in cur_obj.translate_attach_ids:
                page=each.no_of_pages
                total_page += page
            if not cur_obj.translator_id:
                raise osv.except_osv(_('Warning!'),_('Please assign one Translator'))
            total_cost = total_page*cur_obj.translator_id.rate
            #print"rate",total_cost
            inv_line={
                'name': cur_obj.name,
                'account_id': acc_id,
                'price_unit': cur_obj.translator_id.rate or 0.0,
                'quantity': total_page or 0.0,
                'discount': cur_obj.special_discount or cur_obj.translator_id.discount or 0.0 ,
                'product_id': product and product.id or False,
                'uos_id': product and product.uom_id and product.uom_id.id or False,
                'invoice_line_tax_id': False,
                'company_id': cur_obj.company_id and cur_obj.company_id.id or False,
            }
            inv_line_id = inv_line_obj.create(cr, uid, inv_line, context=context)
            inv_data = {
                'name':  cur_obj.translator_id.ref,
                'reference':  cur_obj.name,
                'event_id': ids[0],
                'account_id': rec_acc_id and rec_acc_id.id or False,
                'type': 'in_invoice',
                'date_invoice': cur_obj.event_start_date,
                'partner_id': cur_obj.translator_id.id,
                'currency_id': cur_obj.company_id.currency_id and cur_obj.company_id.currency_id.id or False,
                'journal_id': len(journal_ids) and journal_ids[0] or False,
                'invoice_line': [(6, 0, [inv_line_id])],
                'origin': cur_obj.name,
                'event_start': cur_obj.event_start,
                'event_end': cur_obj.event_end,
                'translator_id': cur_obj.translator_id and cur_obj.translator_id.id or False,
                'doctor_id': cur_obj.doctor_id and cur_obj.doctor_id.id or False,
                'language_id': cur_obj.language_id and cur_obj.language_id.id or False,
                'location_id': cur_obj.location_id and cur_obj.location_id.id or False,
                'contact_id': cur_obj.contact_id and cur_obj.contact_id.id or False,
                'ordering_contact_id': cur_obj.ordering_contact_id and cur_obj.ordering_contact_id.id or False,
                'ordering_partner_id': cur_obj.ordering_partner_id and cur_obj.ordering_partner_id.id or False,
                'payment_term_id': cur_obj.partner_id.property_supplier_payment_term_id and cur_obj.partner_id.property_supplier_payment_term_id.id or False,
                'company_id': cur_obj.company_id and cur_obj.company_id.id or False,
                'project_name_id':cur_obj.project_name_id and cur_obj.project_name_id.id or False,
                'amount_charged': 0.0,
                'invoice_for': 'other',
            }
            inv_id = inv_obj.create(cr, uid, inv_data, context=context)
            self.write(cr, uid, ids, {'supp_invoice_ids': [(6,0,[inv_id])]})
        return inv_id
    
    def create_cust_inv(self, cr, uid, ids, context=None):
        """ Generates customer invoice for Translation Events """
        journal_obj = self.pool.get('account.journal')
        inv_obj = self.pool.get('account.invoice')
        inv_line_obj = self.pool.get('account.invoice.line')
        for cur_obj in self.browse(cr, uid, ids):
            if cur_obj.cust_invoice_id:
                return cur_obj.cust_invoice_id.id
            if not cur_obj.partner_id:
                raise osv.except_osv(_('Warning!'),_('No Billing Customer is selected in this event!'))
            journal_ids = journal_obj.search(cr, uid, [('type', '=','sale'),('company_id', '=', cur_obj.company_id.id)], limit=1)
            if not journal_ids:
                raise osv.except_osv(_('Error!'),
                    _('Define Sale journal for this company: "%s" (id:%d).') % (cur_obj.company_id.name, cur_obj.company_id.id))
            rec_acc_id = cur_obj.partner_id.property_account_receivable
            if rec_acc_id.company_id and cur_obj.partner_id.company_id and rec_acc_id.company_id.id != cur_obj.partner_id.company_id.id:
                raise osv.except_osv(_('Warning!'),_('Please Login with proper user for company %s')%(cur_obj.partner_id.company_id and cur_obj.partner_id.company_id.name ))
            
            product_ids = self.pool.get('product.product').search(cr ,uid ,[('type','=','service'),('sale_ok','=',True),('active','=',True),('company_id', '=',cur_obj.company_id.id),('service_type','=','translator')])
            if not product_ids:
                raise osv.except_osv(_('Warning!'),_('Please define a service type product first.'))
            product = self.pool.get('product.product').browse(cr ,uid ,product_ids[0])

            acc_id = product.property_account_income.id
            if not acc_id:
                acc_id = product.categ_id.property_account_income_categ.id
            if not acc_id:
                raise osv.except_osv(_('Error!'), _('There is no income account defined for this product: "%s" (id:%d).') % (product.name, product.id,))
            total_page = 0.0
            for each in cur_obj.translate_attach_ids:
                page = each.no_of_pages
                total_page += page
            total_cost = total_page * cur_obj.partner_id.rate
            inv_line={
                'name': cur_obj.name,
                'account_id': acc_id,
                'price_unit': cur_obj.partner_id.rate or 0.0,
                'quantity': total_page or 0.0,
                'discount': cur_obj.special_discount or cur_obj.partner_id.discount or 0.0 ,
                'product_id': product and product.id or False,
                'uos_id': product and product.uom_id and product.uom_id.id or False,
                'invoice_line_tax_id': False,
                'company_id': cur_obj.company_id and cur_obj.company_id.id or False,
                'inc_min': '' ,
            }
            inv_line_id = inv_line_obj.create(cr, uid, inv_line, context=context)
            inv_data = {
                'name':  cur_obj.partner_id.ref or '',
                'reference':  cur_obj.name or '',
                'event_id': ids[0] ,
                'account_id': rec_acc_id and rec_acc_id.id or False,
                'type': 'out_invoice',
                'date_invoice': cur_obj.event_start_date,
                'partner_id': cur_obj.partner_id.id,
                'currency_id': cur_obj.company_id.currency_id and cur_obj.company_id.currency_id.id or False,
                'journal_id': len(journal_ids) and journal_ids[0] or False,
                'invoice_line': [(6, 0, [inv_line_id])],
                'origin': cur_obj.name or '',
                'event_start': cur_obj.event_start,
                'event_end': cur_obj.event_end,
                'translator_id': cur_obj.translator_id and cur_obj.translator_id.id or False,
                'doctor_id': cur_obj.doctor_id and cur_obj.doctor_id.id or False,
                'language_id': cur_obj.language_id and cur_obj.language_id.id or False,
                'location_id': cur_obj.location_id and cur_obj.location_id.id or False,
                'contact_id': cur_obj.contact_id and cur_obj.contact_id.id or False,
                'ordering_contact_id': cur_obj.ordering_contact_id and cur_obj.ordering_contact_id.id or False,
                'ordering_partner_id': cur_obj.ordering_partner_id and cur_obj.ordering_partner_id.id or False,
                'payment_term': cur_obj.partner_id.property_payment_term and cur_obj.partner_id.property_payment_term.id or False,
                'company_id': cur_obj.company_id and cur_obj.company_id.id or False,
                'project_name_id':cur_obj.project_name_id and cur_obj.project_name_id.id or False,
                'amount_charged': 0.0,
                'invoice_for': 'other',
            }
            inv_id = inv_obj.create(cr, uid, inv_data, context=context)
            self.write(cr , uid, ids, {'cust_invoice_id': inv_id})
        return inv_id

    def send_for_billing_translation(self, cr, uid, ids, context=None):
        ''' Function to create customer and supplier invoices for translation events '''
        if context == None: context = {}
        inv_obj = self.pool.get('account.invoice')
        for cur_obj in self.browse(cr, uid, ids):
            if not cur_obj.event_end:
                raise osv.except_osv(_('Warning!'),_('You must fill Event End Time in the Event Form.'))
            if cur_obj.event_start > cur_obj.event_end:
                raise osv.except_osv(_('Warning!'),_('Event Start Time should be not greater than Event End Time.'))
            supp_inv_id = self.create_supp_inv(cr, uid, ids, context)
            inv_obj.button_compute(cr, uid, [supp_inv_id], context=context, set_total=True)
            cust_inv_id = self.create_cust_inv(cr, uid, ids, context)
            inv_obj.button_compute(cr, uid, [cust_inv_id], context=context, set_total=True)
            # Link this invoices to each other and to related events
            inv_obj.write(cr, uid, [cust_inv_id], {'invoice_ref': supp_inv_id})
            inv_obj.write(cr, uid, [supp_inv_id], {'invoice_ref': cust_inv_id})
            self.write(cr , uid, ids, {'state': 'invoiced'})
            mod_obj = self.pool.get('ir.model.data')
            res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_supplier_form')
            res_id = res and res[1] or False,
            return {
                'name': _('Invoice For Event %s')%(cur_obj.name),
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': [res_id[0]],
                'res_model': 'account.invoice',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'res_id': supp_inv_id or False,
            }
    
    def correct_translation_invoices(self, cr, uid, ids, context=None):
        ''' Script For creating missing Invoices for all translation Events'''
        if context is None: context = {}
#        wf_service = netsvc.LocalService("workflow")
        inv_obj = self.pool.get('account.invoice')
        event_obj = self.pool.get('event')
        cur_obj = self.browse(cr, uid, ids[0])
        event_ids = event_obj.search(cr, uid, [('event_type','=','translation'),('company_id','=',cur_obj.company_id.id),('state','=','invoiced')])
        print "event_ids......",len(event_ids)
        for event in event_obj.browse(cr, uid, event_ids):
            _logger.info('Event++++++++++++%s',event)
            if not event.cust_invoice_id:
                try:
                    cust_inv_id = self.create_cust_inv(cr, uid, [event.id], context)
                    inv_obj.button_compute(cr, uid, [cust_inv_id], context=context, set_total=True)
#                    self.write(cr , uid, [event.id], {'cust_invoice_id': cust_inv_id})
                except Exception, e:
                    _logger.info('Exception++++++++++++%s',e.args)
                    pass
            if not event.supp_invoice_ids:
                try:
                    supp_inv_id = self.create_supp_inv(cr, uid, [event.id], context)
                    inv_obj.button_compute(cr, uid, [supp_inv_id], context=context, set_total=True)
#                    self.write(cr , uid, [event.id], {'supp_invoice_ids': [(6, 0, [supp_inv_id])]})
                except Exception, e:
                    _logger.info('Exception++++++++++++%s',e.args)
                    pass
        return True
    
    def assign_translation_invoices(self, cr, uid, ids, context=None):
        ''' Script For linking Invoices to each other for all translation Events'''
        if context is None: context = {}
#        wf_service = netsvc.LocalService("workflow")
        inv_obj = self.pool.get('account.invoice')
        event_obj = self.pool.get('event')
        event_ids = event_obj.search(cr, uid, [('event_type','=','translation'),('state','=','invoiced')])
        print "event_ids......",len(event_ids)
        for event in event_obj.browse(cr, uid, event_ids):
            print "event..event.cust_invoice_id..event.view_interpreter_inv...",event,event.cust_invoice_id,event.view_interpreter_inv
            if event.cust_invoice_id and event.view_interpreter_inv:
                event.cust_invoice_id.write({'invoice_ref': event.view_interpreter_inv.id}, context=context)
                event.view_interpreter_inv.write({'invoice_ref': event.cust_invoice_id.id}, context=context)
        return True
    
    def action_send_estimate(self, cr, uid, ids, context=None):
        '''
        This Function Send Estimate for translation type events ,
        This function opens a window to compose an email, with the edi event template message loaded by default
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        for event in self.browse(cr ,uid , ids ):
            if event.event_type=='translation':
                total_page=0.0
                for each in event.translate_attach_ids:
                    page=each.no_of_pages
                    total_page += page
                    if not event.translator_id:
                        raise osv.except_osv(_('Warning!'),_('Please assign one Translator'))
                    total_cost=total_page*event.translator_id.rate
                    self.write(cr ,uid ,ids ,{'total_cost':total_cost})
#            print
            ir_model_data = self.pool.get('ir.model.data')
            try:
#                template_id = ir_model_data.get_object_reference(cr, uid, 'bista_iugroup', 'send_translation_estimate_event')[1]
                template_id = ir_model_data.get_object_reference(cr, uid, 'bista_iugroup', 'send_translation_estimate_event')[1]
            except ValueError:
                template_id = False
            try:
                compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
            except ValueError:
                compose_form_id = False
            ctx = dict(context)
            ctx.update({
                'default_model': 'event',
                'default_res_id': event.id,
                'event_id' : event.id,
                'default_use_template': bool(template_id),
                'default_template_id': template_id,
                'default_composition_mode': 'comment',
                'search_default_event_type':'translation',
                'search_event_type':'translation',
                'default_event_type':'translation',
                #'mark_so_as_sent': True
            })
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(compose_form_id, 'form')],
                'view_id': compose_form_id,
                'target': 'new',
                'context': ctx,
            }

    def import_translator(self , cr ,uid ,ids , context = None):
        ''' This function updates or assigns translator in the event form '''
        res= []
        select_obj = self.pool.get('select.translator.line')
        translator = self.pool.get('res.partner')
        translator_ids , new_ids , select_ids = [],[],[]
        for event in self.browse(cr ,uid ,ids ):
            #print "event..event_start.event_end..",event.event_start,event.event_end
            for translator_id in event.translator_ids:
                select_obj.unlink(cr ,uid , [translator_id.id])
#            if event.certification_level_id:
#                query = "select lang.translator_id from translator_language as lang INNER JOIN res_partner as partner ON (lang.translator_id = partner.id)\
#                        where partner.active is true and is_translation_active is true and lang.name = %s and lang.to_lang_id = %s and certification_level_id = %s and lang.company_id = %s"%( event.language_id.id ,
#                        event.language_id2.id, event.certification_level_id and event.certification_level_id.id , event.company_id.id)
#                cr.execute(query )
#                translator_ids = map(lambda x: x[0], cr.fetchall())
#                print "translator_ids11......",len(translator_ids)
#            else:
            if not event.language_id2.id:
                raise osv.except_osv(_('Warning!'),_('Please select the language to translate from under Translator Tab(From Language)'))
            if not event.language_id.id:
                raise osv.except_osv(_('Warning!'),_('Please select the language to translate to under Appointment Details(language).'))
            query = "select lang.translator_id from translator_language as lang INNER JOIN res_partner as partner ON (lang.translator_id = partner.id)\
                    where partner.active is true and is_translation_active is true and lang.name = %s and lang.to_lang_id = %s and lang.company_id = %s"%( event.language_id.id ,
                    event.language_id2.id, event.company_id.id)
            cr.execute(query )
            translator_ids = map(lambda x: x[0], cr.fetchall())
#            print "translator_ids22......",len(translator_ids)
#            int_lang_ids = self.pool.get('translator.language').search(cr ,uid ,[('name','=',event.language_id.id)])
#            #print"int_lang_ids",len(int_lang_ids)
#            if int_lang_ids:
#                for int_lang_id in int_lang_ids:
#                    lang_browse = self.pool.get('translator.language').browse(cr ,uid ,int_lang_id)
#                    #print"lang_browse",lang_browse
#                    translator_ids.append(lang_browse.translator_id.id)
            #print"translator_ids",len(translator_ids)
            i_ids = translator.search(cr ,uid ,[('id','in',tuple(translator_ids)),('cust_type','=','translator'),('company_id','=',event.company_id.id)] , order ="rate")
            #print"i_ds.....",len(i_ids)
            for each_trans in i_ids:
                select_id=select_obj.create(cr ,uid ,{'translator_id':each_trans,'event_id':ids[0] ,'state':'draft'},context)
                select_ids.append(select_id)
            self.write(cr ,uid ,ids , {'translator_ids':[(6, 0, select_ids)]})
        
        return res

    def confirm_lang_trans_event( self , cr ,uid ,ids ,context=None):
        ''' It confirms the Language and Transport event , creates history for translator and Interprter (if not exists else updates) and
            creates task and a project as its parent with the no of hours '''
        if isinstance(ids, (int,long)):
            ids = [ids]
        if context is None:
            context = {}
        
        project_task = self.pool.get('project.task')
        transporter = self.browse(cr ,uid ,ids[0]).transporter_id
        translator = self.browse(cr ,uid ,ids[0]).translator_id
        contact = self.browse(cr ,uid ,ids[0]).partner_id
        cur_obj = self.browse(cr ,uid ,ids[0])
        partner = self.pool.get('res.partner')
        if not transporter:
            raise osv.except_osv(_('Warning!'),_('Please Assign Transporter First.'))
        event_start = datetime.datetime.strptime(cur_obj.event_start, tools.DEFAULT_SERVER_DATETIME_FORMAT)
        if cur_obj.event_end:
            event_end = datetime.datetime.strptime(cur_obj.event_end, tools.DEFAULT_SERVER_DATETIME_FORMAT)
        else:
            raise osv.except_osv(_('Warning!'),_('Please enter Event End Time in the event.'))
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        from_dt = datetime.datetime.strptime(str(event_start), DATETIME_FORMAT)
        from_dt = from_dt + datetime.timedelta(hours=-8 , minutes=0)
        to_dt = datetime.datetime.strptime(str(event_end), DATETIME_FORMAT) + datetime.timedelta(hours=5 , minutes=30)
        timedelta = to_dt - from_dt
        min = float(timedelta.seconds /60.0)
        #print "MIN...",min
        hour = int(min / 60)
        left_min = float(min - hour * 60)
        #print "left_min.......",left_min
        if left_min > 54.0:
            hour += 1.0
        elif left_min >34.0 and left_min <= 54.0:
            hour += 0.5

        date_planned = from_dt.strftime('%Y-%m-%d')
        task_name= ''
        if cur_obj.name:
            task_name += cur_obj.name + ': Task '
        if cur_obj.patient_id:
                task_name += 'for ' + cur_obj.patient_id.name
        if cur_obj.patient_id and cur_obj.patient_id.last_name:
            task_name += cur_obj.patient_id.last_name
        int_ids = []
        int_user_ids=[]
        for interpreter in cur_obj.assigned_interpreters:
            int_ids.append(interpreter.id)
            int_user_ids.append(interpreter.user_id.id)
        task_id = project_task.create(cr, uid, {
            'name': task_name ,
            'date_deadline': str(date_planned),
            'planned_hours': hour,
            'remaining_hours': hour,
            'user_id': int_user_ids and int_user_ids[0] or False,
            'notes': cur_obj.comment,
            'assigned_interpreters': [(6,0,int_ids)],
            'transporter_id': transporter and transporter.id or False,
            'description': cur_obj.name,
            'date_start': cur_obj.event_start,
            'date_end': cur_obj.event_end,
            'event_id':ids[0],
            'company_id':cur_obj.company_id and cur_obj.company_id.id or False,
            },context=context)
        history_id2 = cur_obj.history_id2
        if cur_obj.patient_id:
                task_name += 'for ' + cur_obj.patient_id.name
        if cur_obj.patient_id and cur_obj.patient_id.last_name:
            task_name += ' ' + cur_obj.patient_id.last_name
        if not history_id2:
            history_id2 = self.pool.get('transporter.alloc.history').create(cr ,uid ,{'partner_id':contact and contact.id or False,'name':transporter and transporter.id or False,
                    'event_id':ids[0],'event_date': date_planned,'event_start':cur_obj.event_start,'event_end':cur_obj.event_end,'state':'confirm','company_id': cur_obj.company_id and cur_obj.company_id.id or False})
            self.write(cr ,uid ,ids , {'history_id2':history_id2})
        else:
            self.pool.get('transporter.alloc.history').write(cr ,uid ,[history_id2.id] ,{'partner_id':contact and contact.id or False,'name':transporter and transporter.id or False,
                    'event_date': date_planned ,'event_id':ids[0],'event_start':cur_obj.event_start,'event_end':cur_obj.event_end,'state':'confirm','company_id': cur_obj.company_id and cur_obj.company_id.id or False})
        if not cur_obj.event_type == 'transport':
            if cur_obj.lang_service_type == 'interpretation' :
                history_id = cur_obj.history_id
                if not history_id:
                    hist_ids=[]
                    for interpreter in cur_obj.assigned_interpreters:
                        hist_ids.append(self.pool.get('interpreter.alloc.history').create(cr ,uid ,{'partner_id':contact and contact.id or False,'name':interpreter and interpreter.id or False,
                                'event_id':ids[0],'event_date': date_planned,'event_start':cur_obj.event_start,'event_end':cur_obj.event_end,'state':'confirm','company_id': cur_obj.company_id and cur_obj.company_id.id or False,
                                'confirm_date': time.strftime('%Y-%m-%d %H:%M:%S')}))
                    if hist_ids:
                        self.write(cr ,uid ,ids , {'history_id': [6, 0, hist_ids]})
                else:
                    for history_id in cur_obj.history_id:
                        self.pool.get('interpreter.alloc.history').write(cr ,uid ,[history_id.id] ,{'partner_id':contact and contact.id or False,
                                'event_date': date_planned ,'event_id':ids[0],'event_start':cur_obj.event_start,'event_end':cur_obj.event_end,'state':'confirm','company_id': cur_obj.company_id and cur_obj.company_id.id or False,
                                'confirm_date': time.strftime('%Y-%m-%d %H:%M:%S')})#,'name':interpreter and interpreter.id or False
            elif cur_obj.lang_service_type == 'translation':
                history_id3 = cur_obj.history_id
                if not history_id3:
                    history_id3 = self.pool.get('translator.alloc.history').create(cr ,uid ,{'partner_id':contact and contact.id or False,'name':translator and translator.id or False,
                            'event_id':ids[0],'event_date': date_planned,'event_start':cur_obj.event_start,'event_end':cur_obj.event_end,'state':'confirm','company_id': cur_obj.company_id and cur_obj.company_id.id or False,
                            }) 
                    self.write(cr ,uid ,ids , {'history_id3': history_id3})
                else:
                    self.pool.get('translator.alloc.history').write(cr ,uid ,[history_id3.id] ,{'partner_id':contact and contact.id or False,'name':translator and translator.id or False,
                            'event_date': date_planned ,'event_id':ids[0],'event_start':cur_obj.event_start,'event_end':cur_obj.event_end,'state':'confirm','company_id': cur_obj.company_id and cur_obj.company_id.id or False,
                            })
        
        self.write(cr ,uid ,ids ,{'state':'confirmed','task_id':task_id})
        if cur_obj.partner_id:
            partner.write(cr ,uid , cur_obj.partner_id.id , {'last_update_date': date_planned})
        if cur_obj.contact_id:
            partner.write(cr ,uid , cur_obj.contact_id.id , {'last_update_date': date_planned})
        if cur_obj.ordering_partner_id:
            partner.write(cr ,uid , cur_obj.ordering_partner_id.id , {'last_update_date': date_planned})
        if cur_obj.ordering_contact_id:
            partner.write(cr ,uid , cur_obj.ordering_contact_id.id , {'last_update_date': date_planned})
        for interpreter_id in cur_obj.assigned_interpreters:
            if interpreter_id:
                partner.write(cr ,uid , interpreter_id.id , {'last_update_date': date_planned})
        if cur_obj.translator_id:
            partner.write(cr ,uid , cur_obj.translator_id.id , {'last_update_date': date_planned})
        if cur_obj.transporter_id:
            partner.write(cr ,uid , cur_obj.transporter_id.id , {'last_update_date': date_planned})
        if cur_obj.doctor_id:
            self.pool.get('doctor').write(cr ,uid , cur_obj.doctor_id.id , {'last_update_date': date_planned})
        if cur_obj.location_id:
            self.pool.get('location').write(cr ,uid , cur_obj.location_id.id , {'last_update_date': date_planned})
        if not cur_obj.suppress_email:
            context['customer'] = True
        self.event_confirm_mail( cr, uid, ids, context=context)
        context['customer'] = False
        context['interpreter'] = True
        self.event_confirm_mail( cr, uid, ids, context=context)
        context['transporter'] = True
        context['customer'] = False
        context['interpreter'] = False
        self.event_confirm_mail( cr, uid, ids, context=context)
        return True
    
    class itinerary_lines(osv.osv):
        _name='itinerary.lines'
