# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    ThinkOpen Solutions Brasil
#    Copyright (C) Thinkopen Solutions <http://www.tkobr.com>.
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

import logging
from datetime import datetime

import odoo
import pytz
import werkzeug.contrib.sessions
from dateutil.relativedelta import *
from odoo import SUPERUSER_ID
from odoo import fields, _
from odoo.addons.web.controllers.main import Home
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT,DEFAULT_SERVER_DATE_FORMAT
import werkzeug.utils
# from odoo import pooler
import time
_logger = logging.getLogger(__name__)
from odoo import http

class Home_tkobr(Home):

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)
        print request.env.user
        if not request.uid:
            request.uid = odoo.SUPERUSER_ID
        print request.env.user
        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            old_uid = request.uid
            uid = False
            if 'login' in request.params and 'password' in request.params:
                uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
            if uid is not False:
                request.params['login_success'] = True
                # try:
                model_serch_log=request.env['ir.model'].sudo().search([('model', '=', 'network.audit.log')])
                model_serch_line=request.env['ir.model'].sudo().search([('model', '=', 'network.audit.log.line')])
                if model_serch_log and model_serch_line:
                        session_value = request.env['ir.http'].session_info()
                        log_obj = request.env['network.audit.log']
                        line_obj = request.env['network.audit.log.line']
                        today_str = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
                        today_datetime = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                        today = datetime.strptime(today_str,'%Y-%m-%d')
                        tm_tuple = today.timetuple()
                        month = tm_tuple.tm_mon
                        year = tm_tuple.tm_year
                        old_ids = log_obj.sudo().search([('name','=',today_str)]).id
                        if old_ids:
                            old_ids=[old_ids]
                        new_ids = False
                        if not old_ids:
                            new_ids = log_obj.sudo().create({'name':today,'month':month,'year':year}).id
                            old_ids = [new_ids]
                        ip = request.httprequest.headers.environ['REMOTE_ADDR']
                        forwarded_for = ''
                        if 'HTTP_X_FORWARDED_FOR' in request.httprequest.headers.environ and \
                                request.httprequest.headers.environ[
                                    'HTTP_X_FORWARDED_FOR']:
                            forwarded_for = request.httprequest.headers.environ['HTTP_X_FORWARDED_FOR'].split(
                                ', ')
                            if forwarded_for and forwarded_for[0]:
                                ip = forwarded_for[0]
                        line_obj.sudo().create({'name':today_datetime,'month':month,'year':year,'user_id':request.session.uid,'user_ip':ip,'log_id':old_ids[0],'session_id':session_value['session_id']})
                # except:
                #         pass
                if not redirect:
                    redirect = '/web'
                return http.redirect_with_hash(redirect)
            request.uid = old_uid
            values['error'] = _("Wrong login/password")
        return request.render('web.login', values)

    @http.route('/web/session/logout', type='http', auth="none")
    def logout(self, redirect='/web'):
        model_serch_log = request.env['ir.model'].sudo().search([('model', '=', 'network.audit.log')])
        model_serch_line=request.env['ir.model'].sudo().search([('model', '=', 'network.audit.log.line')])
        if model_serch_log and model_serch_line:
            log_obj = request.env['network.audit.log']
            line_obj = request.env['network.audit.log.line']
            today_datetime = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            if not request.uid:
                request.uid=request.session.uid
                if not request.uid:
                    request.uid = odoo.SUPERUSER_ID
            print request.env.user
            old_session = request.env['ir.http'].session_info()
            if old_session.get('session_id',False):
                ip = request.httprequest.headers.environ['REMOTE_ADDR']
                forwarded_for = ''
                if 'HTTP_X_FORWARDED_FOR' in request.httprequest.headers.environ and \
                        request.httprequest.headers.environ[
                            'HTTP_X_FORWARDED_FOR']:
                    forwarded_for = request.httprequest.headers.environ['HTTP_X_FORWARDED_FOR'].split(
                        ', ')
                    if forwarded_for and forwarded_for[0]:
                        ip = forwarded_for[0]
                old_session_val = old_session.get('session_id')
                log_session = line_obj.sudo().search([('session_id','=',old_session_val),('user_id','=',request.session.uid),('user_ip','=',ip)])
                if log_session:
                    log_session.sudo().write({'logout':today_datetime})
        request.session.logout(keep_db=True)
        return werkzeug.utils.redirect(redirect, 303)
