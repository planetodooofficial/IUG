# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2013 OpenERP s.a. (<http://openerp.com>).
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
from odoo import fields,models,api,SUPERUSER_ID
from odoo.tools.translate import _
from datetime import datetime, timedelta
import random
from urllib import urlencode
from odoo import tools
import odoo.exceptions
# from openerp import SUPERUSER_ID
# from urlparse import urljoin
# from ast import literal_eval
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, RedirectWarning, ValidationError,AccessDenied

class SignupError(Exception):
    pass

def random_token():
    # the token has an entropy of about 120 bits (6 bits/char * 20 chars)
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.choice(chars) for i in xrange(20))

def now(**kwargs):
    dt = datetime.now() + timedelta(**kwargs)
    return dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

_logger = logging.getLogger(__name__)

class users_type(models.Model):
    _name = "users.type"


    name=fields.Char('Name', size=70)
    users_type_id=fields.Integer("IU User Type Id")
    company_id=fields.Many2one('res.company',"Company")


class res_users(models.Model):
    _inherit = "res.users"

    mail_group=fields.Selection([('supervisor','Supervisor')],
        string='Mail Group', help='Mail Group for mail receipt')
    user_id=fields.Integer("IU User Id")
    entity_id=fields.Integer("IU Entity Id")
    user_type_id=fields.Many2one('users.type',"User Type Id")
    login_id=fields.Integer("IU Login Id")
    require_to_reset=fields.Boolean('Require To Reset')
    user_type=fields.Selection([('staff','Staff'),('customer','Customer'),('contact','Contact'),('vendor','Vendor'),('admin','Admin')],\
                                'User Type', index=True)
    zone_id=fields.Many2one('meta.zone',"Zone", index=True)

    @api.multi
    def action_reset_password(self):
        """ create signup token for each user, and send their signup url by email """
        # prepare reset password signup
        create_mode = bool(self.env.context.get('create_user'))
        mail_obj = self.env['mail.mail']
        # no time limit for initial invitation, only for reset password
        expiration = False if create_mode else now(days=+1)

        self.mapped('partner_id').signup_prepare(signup_type="reset", expiration=expiration)

        # send email to users with their signup url
        template = False
        if create_mode:
            try:
                template = self.env.ref('bista_iugroup.set_password_email', raise_if_not_found=False)
            except ValueError:
                pass
        if not template:
            template = self.env.ref('bista_iugroup.reset_password_email')
        assert template._name == 'mail.template'

        for user in self:
            if not user.email:
                raise UserError(_("Cannot send email: user %s has no email address.") % user.name)
            mail_id=template.with_context(lang=user.lang).send_mail(user.id, force_send=True, raise_exception=True)
            #mail_state=mail_obj.browse(mail_id).state
            #if mail_state and mail_state == 'exception':
            #    raise UserError(_(
            #        "Cannot send email: no outgoing email server configured.\nYou can configure it under Settings/General Settings."))
            #else:
            _logger.info("Password reset email sent for user <%s> to <%s>", user.login, user.email)

    @classmethod
    def _login(cls, db, login, password):
        '''Function Overridden for authenticate incasesentitive login '''
        if not password:
            return False
        user_id = False
        try:
            with cls.pool.cursor() as cr:
                self = api.Environment(cr, SUPERUSER_ID, {})[cls._name]
                cr.execute("SELECT id FROM res_users WHERE lower(login)=%s", (login.lower(),))
                res = map(lambda x: x[0], cr.fetchall())
                if res:
                    user_id = res[0]
                    user = self.search([('id', '=',user_id)],limit=1)
                    user.sudo(user_id).check_credentials(password)
                    user.sudo(user_id)._update_last_login()
        except AccessDenied:
            _logger.info("Login failed for db:%s login:%s", db, login)
            user_id = False
        return user_id

    @api.model
    def create(self, vals):
        login = vals.get('login', False)
        if login:
            vals['login'] = login.lower()
        user = super(res_users, self).create(vals)
        return user

    @api.multi
    def write(self, vals):
        '''Function to write in lower case '''
        if 'login' in vals and vals['login']:
            vals['login'] = vals.get('login').lower()
        res = super(res_users, self).write(vals)
        return res
    
#    def name_get(self, cr, uid, ids, context=None):
#        if context is None: context = {}
#        if isinstance(ids, (int, long)): ids = [ids]
#        res = []
#        for record in self.browse(cr, uid, ids, context=context):
#            name = record.name
#            if record.last_name:
#                name = name + ' ' + (record.last_name or '')
#            if context.get('show_login') and record.login:
#                name = "%s" % (record.login)
#            print "name.........",name
#            res.append((record.id, name))
#        return res

class report_users_info(models.Model):
    _name = "report.users.info"

    name=fields.Char('First Name', size=70)
    mail_id=fields.Char('Email-id',size=70,required=True)
    report_user=fields.Many2one('report.users','Report Users')
    users=fields.Many2one('res.users',"User Name", index=True)

    @api.onchange('users')
    def onchange_users(self):
        vals={}
        if self.users:
            if self.users.email:
                vals.update({'mail_id':self.users.email})
            else:
                raise UserError('Please add the e-mail id for the user.')
        return {'value':vals}

   
        
class report_users(models.Model):
    _name = 'report.users'
    _rec_name = 'group_name'

    group_name=fields.Char('Group Name',size=30,required=True)
    template_id=fields.Many2one('mail.template','Select Template')
    get_info=fields.One2many('report.users.info','report_user','Add Users')

    @api.onchange('template_id')
    def onchange_template(self):
        vals={}
        get_temp = self.search([('template_id', '=', self.template_id.id)])
        if get_temp:
            grp_name = get_temp.group_name
            vals.update({'template_id':False})
            return {'value':vals,'warning':{'title':'Group Exists','message':"The group for the selected template is already created.Please add users in the group namely "+grp_name}}
        else:
            return {'value':vals}
