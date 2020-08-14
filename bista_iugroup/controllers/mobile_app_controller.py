
import ast
import base64
import csv
import glob
import itertools
import logging
import operator
import datetime
import hashlib
import os
import re
import simplejson
import time
import urllib
import urllib2
import urlparse
import xmlrpclib
import zlib
from xml.etree import ElementTree
from cStringIO import StringIO

import babel.messages.pofile
import werkzeug.utils
import werkzeug.wrappers
from odoo import http
#from http import request
# import openerp.pooler as pooler
# import openerp
# import openerp.modules.registry
import odoo
from odoo import api,SUPERUSER_ID


class MyController(http.Controller):
    _cp_path = '/job'

    @http.route('/job/job_assign', type='json', auth='none')
    def job_assign(self,req):
        print'===========', req.jsonrequest
        result={}
        data=req.jsonrequest
        if data['job_update']['user']!='admin' or data['job_update']['password']!='iug@bista':
            raise ValueError('Invalid login credential')

        print'data===============',data['job_update']['event_id'],data['job_update']['interpreter_email']
        email=data['job_update']['interpreter_email']
        registry = odoo.registry('iug')


        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            user = env['res.users']
            event_obj = env['event']
            interpreter_obj = env['res.partner']
            event=event_obj.browse(int(data['job_update']['event_id']))
            if not event:
               raise ValueError('Invalid Event ID')
            

            interpreter_id=interpreter_obj.search([('email','=',email),('cust_type','=','interpreter')])
            print'interpreter_id==================',interpreter_id
            if not interpreter_id:
                raise ValueError('Invalid interpreter email')
            int_ids=[interpreter_id[0].ids]
            interpreter=interpreter_id[0]
            history_id = env['interpreter.alloc.history'].create({'name':interpreter_id[0] or False,
                                'event_id':event.id,'event_date':event.event_start_date ,'state':'allocated',
                                'allocate_date':time.strftime('%Y-%m-%d %H:%M:%S')})
            write_obj=event.write({'assigned_interpreters': [(6,0,int_ids)],
                                    'history_id':[(6,0,[history_id])],'schedule_event_time':time.strftime('%Y-%m-%d %H:%M:%S')})
        
            result['status']='assigned'
            result['message']='Job succesfully assigned to interpreter'
            if data['job_update']['job_status']=='done':
                event.write({'state':'confirmed'})
                result['status']='done'
                result['message']='Job succesfully Done'        
        return result


    
