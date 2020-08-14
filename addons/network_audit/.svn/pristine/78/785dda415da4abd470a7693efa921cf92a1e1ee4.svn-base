# -*- encoding: utf-8 -*-
##############################################################################
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details, but reseller should inform 
#    or take permission from Bista Solutions Pvt Ltd before resell..
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#    
##############################################################################
import time
from odoo.service import security, model as service_model
import odoo
from datetime import datetime,timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import json
from odoo.http import OpenERPSession
import werkzeug.contrib.sessions
import logging
import sys
_logger = logging.getLogger(__name__)
rpc_request = logging.getLogger(__name__ + '.rpc.request')
rpc_response = logging.getLogger(__name__ + '.rpc.response')
from odoo.service.server import memory_info
import threading
import os
try:
    import psutil
except ImportError:
    psutil = None
#----------------------------------------------------------
# Odoo Session RPC Odoo backend access
#----------------------------------------------------------
#
import werkzeug.local
_request_stack = werkzeug.local.LocalStack()

request = _request_stack()
NO_POSTMORTEM = (odoo.osv.orm.except_orm,
                 odoo.exceptions.AccessError,
                 odoo.exceptions.ValidationError,
                 odoo.exceptions.MissingError,
                 odoo.exceptions.AccessDenied,
                 odoo.exceptions.Warning,
                 odoo.exceptions.RedirectWarning)
def replace_request_password(args):
    # password is always 3rd argument in a request, we replace it in RPC logs
    # so it's easier to forward logs for diagnostics/debugging purposes...
    if len(args) > 2:
        args = list(args)
        args[2] = '*'
    return tuple(args)

def dispatch_rpc(service_name, method, params):
    """ Handle a RPC call.

    This is pure Python code, the actual marshalling (from/to XML-RPC) is done
    in a upper layer.
    """
    try:
        rpc_request_flag = rpc_request.isEnabledFor(logging.DEBUG)
        rpc_response_flag = rpc_response.isEnabledFor(logging.DEBUG)
        if rpc_request_flag or rpc_response_flag:
            start_time = time.time()
            start_rss, start_vms = 0, 0
            if psutil:
                start_rss, start_vms = memory_info(psutil.Process(os.getpid()))
            if rpc_request and rpc_response_flag:
                odoo.netsvc.log(rpc_request, logging.DEBUG, '%s.%s' % (service_name, method), replace_request_password(params))

        threading.current_thread().uid = None
        threading.current_thread().dbname = None
        if service_name == 'common':
            dispatch = odoo.service.common.dispatch
        elif service_name == 'db':
            dispatch = odoo.service.db.dispatch
        elif service_name == 'object':
            dispatch = odoo.service.model.dispatch
        elif service_name == 'report':
            dispatch = odoo.service.report.dispatch
        result = dispatch(method, params)

        if rpc_request_flag or rpc_response_flag:
            end_time = time.time()
            end_rss, end_vms = 0, 0
            if psutil:
                end_rss, end_vms = memory_info(psutil.Process(os.getpid()))
            logline = '%s.%s time:%.3fs mem: %sk -> %sk (diff: %sk)' % (service_name, method, end_time - start_time, start_vms / 1024, end_vms / 1024, (end_vms - start_vms)/1024)
            if rpc_response_flag:
                odoo.netsvc.log(rpc_response, logging.DEBUG, logline, result)
            else:
                odoo.netsvc.log(rpc_request, logging.DEBUG, logline, replace_request_password(params), depth=1)

        return result
    except NO_POSTMORTEM:
        raise
    except odoo.exceptions.DeferredException, e:
        _logger.exception(odoo.tools.exception_to_unicode(e))
        odoo.tools.debugger.post_mortem(odoo.tools.config, e.traceback)
        raise
    except Exception, e:
        _logger.exception(odoo.tools.exception_to_unicode(e))
        odoo.tools.debugger.post_mortem(odoo.tools.config, sys.exc_info())
        raise

# super_base=odoo.http.OpenERPSession.authenticate
#
# class OpenERPSessionnew(odoo.http.OpenERPSession):
#
#     def authenticate(self,db, login=None, password=None, uid=None):
#         res=super_base(db=db, login=login, password=password, uid=uid)
#         session_value = request.env['ir.http'].session_info(request)
#         try:
#             model_serch_log=request.session.model('ir.model').search([('model', '=', 'network.audit.log')])
#             model_serch_line=request.session.model('ir.model').search([('model', '=', 'network.audit.log.line')])
#             if model_serch_log and model_serch_line:
#                 log_obj = request.session.model('network.audit.log')
#                 line_obj = request.session.model('network.audit.log.line')
#                 today = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
#                 today_datetime = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
#                 today = datetime.strptime(today,'%Y-%m-%d')
#                 tm_tuple = today.timetuple()
#                 month = tm_tuple.tm_mon
#                 year = tm_tuple.tm_year
#                 old_ids = log_obj.search([('name','=',today)])
#                 new_ids = False
#                 if not old_ids:
#                     new_ids = log_obj.create({'name':today,'month':month,'year':year})
#                     old_ids = [new_ids]
#
#                 line_obj.create({'name':today_datetime,'month':month,'year':year,'user_id':request.session._uid,'user_ip':env['REMOTE_ADDR'],'log_id':old_ids[0],'session_id':session_value['session_id']})
#         except:
#             pass
#         return
#
# OpenERPSession.authenticate=OpenERPSessionnew.authenticate

    # def destroy(self, req):
    #     wsgienv = req.httprequest.environ
    #     new_env = dict(
    #         HTTP_HOST=wsgienv['HTTP_HOST'],
    #         REMOTE_ADDR=wsgienv['REMOTE_ADDR'],
    #     )
    #     model_serch_log=req.session.model('ir.model').search([('model', '=', 'network.audit.log')])
    #     model_serch_line=req.session.model('ir.model').search([('model', '=', 'network.audit.log.line')])
    #     if model_serch_log and model_serch_line:
    #         log_obj = req.session.model('network.audit.log')
    #         line_obj = req.session.model('network.audit.log.line')
    #         today_datetime = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
    #         old_session = self.session_info(req)
    #         if old_session.get('session_id',False):
    #             old_session_val = old_session.get('session_id')
    #             log_session = line_obj.search([('session_id','=',old_session_val),('user_id','=',req.session._uid),('user_ip','=',new_env['REMOTE_ADDR'])])
    #             if log_session:
    #                 login_date = line_obj.read(log_session[0],['name'])
    #                 line_obj.write([log_session[0]],{'logout':today_datetime})
    #         req.session._suicide = True
    #
    #
