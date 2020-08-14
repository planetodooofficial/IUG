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

import re
import openerp
from openerp import  tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import time
from openerp import SUPERUSER_ID, tools
w_types = [('warning','Warning'),('info','Information'),('error','Error')]

class warning(osv.osv_memory):
    _name = 'warning'
    _req_name = 'title'
    _columns = {
        'history_id': fields.many2one("select.interpreter.line", "History Id" ,),
        'event_id': fields.many2one("event", "Event Id" ,),
        'title': fields.char("Title", size=32),
        'message': fields.html("Message", size=32, ),
        'type': fields.selection([('warning','Warning'),('info','Information'),('error','Error')],
                                string='Status', type='selection',),
    }
    
    def _get_view_id(self, cr, uid):
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'bista_iugroup', 'warning_form')
        if res:
            return res[1]
        else:
            return False

    def message(self, cr, uid, id, context):
        message = self.browse(cr, uid, id)
        message_type = [t[1]for t in w_types if message.type == t[0]][0]
        res = {
            'name': '%s: %s' % (_(message_type), _(message.title)),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self._get_view_id(cr, uid),
            'res_model': 'warning',
            'domain': [],
            'context': context,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': message.id
        }
        return res

    def warning(self, cr, uid, title, message, context=None):
        id = self.create(cr , uid, {'title': title, 'message': message, 'type': 'warning'})
        res = self.message(cr, uid, id, context)
        
        return res

    def info(self, cr, uid, title, message, context=None):
        res = []
        return res

    def error(self, cr, uid, title, message, context=None):
        res = []
        return res
    
    def update_interpreter(self, cr, uid, ids, context):
        ''' This function updates or assigns interpreter in the event form '''
        if context is None: context = {}
        res, context['interpreter'] = [], True
        event_obj = self.pool.get('event')
        mod_obj = self.pool.get('ir.model.data')
        user = self.pool.get('res.users').browse(cr ,SUPERUSER_ID , uid)
        event_id = context.get('event_id',False)
        sel_line_id = context.get('history_id',False)
        if event_id:
            event = event_obj.browse(cr ,SUPERUSER_ID ,event_id)
            int_line_obj = self.pool.get('select.interpreter.line')
            if sel_line_id:
                sel_line = int_line_obj.browse(cr ,SUPERUSER_ID ,sel_line_id)
                int_line_obj.write(cr ,SUPERUSER_ID , [sel_line_id], {'state': 'cancel'})
                event_obj.write(cr ,SUPERUSER_ID , [event.id], {'event_follower_ids':[(3, sel_line.interpreter_id.user_id.id)],'assigned_interpreters':[(3,sel_line.interpreter_id.id)], 
                                                        'interpreter_ids2':[(3,sel_line.id)]}) 
                new_event = self.pool.get('event').browse(cr, SUPERUSER_ID, event.id)
                if new_event.multi_type and len(new_event.assigned_interpreters) >= int(new_event.multi_type):
                    event_obj.write(cr , uid, [new_event.id], {'state':'allocated'})
                else:
                    event_obj.write(cr , uid, [new_event.id], {'state':'draft'})
                for interpreter_line in event.interpreter_ids2:
                    if interpreter_line.state != 'cancel':
                        int_line_obj.cancel_appointment(cr, uid, interpreter_line.id, context=context)
#                    if interpreter_line.interpreter_id.user_id.id in event.event_follower_ids:
#                        self.pool.get('event').write(cr ,SUPERUSER_ID , [event.id],{'event_follower_ids':[(4,interpreter_line.interpreter_id.user_id.id)]})
                history_id = event.history_id
                if history_id:
                    for each_history in history_id:
                        if each_history.name.id == sel_line.interpreter_id.id:
                            self.pool.get('interpreter.alloc.history').write(cr, SUPERUSER_ID, [each_history.id],{'state':'cancel','cancel_date':time.strftime('%Y-%m-%d %H:%M:%S')})
            else:
                if 'interpreter_id' in context and context['interpreter_id']:
                    event_obj.write(cr, SUPERUSER_ID, [event.id], {'assigned_interpreters':[(3, context['interpreter_id'])]})
                new_event = event_obj.browse(cr, SUPERUSER_ID, event.id)
                if new_event.multi_type and len(new_event.assigned_interpreters) >= int(new_event.multi_type):
                    event_obj.write(cr , uid, [new_event.id], {'state':'allocated'})
                else:
                    event_obj.write(cr , uid, [new_event.id], {'state':'draft'})
                context['system_rejected'] = True
                for interpreter_line in event.interpreter_ids2:
                    if interpreter_line.state != 'cancel':
                        int_line_obj.cancel_appointment(cr, uid, [interpreter_line.id], context=context)
                history_id = event.history_id
                if history_id:
                    for each_history in history_id:
                        if 'interpreter_id' in context and context['interpreter_id']:
                            if each_history.name.id == context['interpreter_id']:
                                self.pool.get('interpreter.alloc.history').write(cr, SUPERUSER_ID, [each_history.id],{'state':'cancel','cancel_date':time.strftime('%Y-%m-%d %H:%M:%S')})
                
        res = mod_obj.get_object_reference(cr, uid, 'bista_iugroup', 'view_event_form')
        res_id = res and res[1] or False,
        res_int = mod_obj.get_object_reference(cr, uid, 'bista_iugroup', 'view_event_user_form')
        res_int_id = res_int and res_int[1] or False,
        return {
            'name': _('Event'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res_id[0]] if user.user_type in ['staff','admin'] else [res_int_id[0]] ,
            'res_model': 'event',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': event_id or False,
        }
    
    def default_get(self, cr, uid, fields, context):
        res = {}
        if context is None: context = {}
        res = super(warning , self).default_get(cr, SUPERUSER_ID, fields, context=context)
        wiz_ids = context.get('active_ids', [])
        if not wiz_ids or len(wiz_ids) != 1:
            return res
        wiz_id, = wiz_ids
        event_id = context.get('event_id',False)
        history_id = context.get('history_id',False)
        if 'event_id' in fields:
            res.update({'event_id':event_id})
        if 'history_id' in fields:
            res.update({'history_id':history_id})
        return res