# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2012 OpenERP S.A. (<http://openerp.com>).
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
import re
import unicodedata

from odoo import models,fields,api
from odoo.tools import ustr
# from openerp.modules.registry import RegistryManager
# from openerp import SUPERUSER_ID

_logger = logging.getLogger(__name__)

# Inspired by http://stackoverflow.com/questions/517923
# def remove_accents(input_str):
#     """Suboptimal-but-better-than-nothing way to replace accented
#     latin letters by an ASCII equivalent. Will obviously change the
#     meaning of input_str and work only for some cases"""
#     input_str = ustr(input_str)
#     nkfd_form = unicodedata.normalize('NFKD', input_str)
#     return u''.join([c for c in nkfd_form if not unicodedata.combining(c)])

class mail_alias(models.Model):
    """ Overidden to use existing Domain "donotreply" """
    _inherit = 'mail.alias'

    
    # def create_unique_alias(self, cr, uid, vals, model_name=None, context=None):
    #     """ Overidden to use donotreply alias   """
    #     # when an alias name appears to already be an email, we keep the local part only
    #     alias_name = remove_accents(vals['alias_name']).lower().split('@')[0]
    #     alias_name = re.sub(r'[^\w+.]+', '-', alias_name)
    #     alias_name = self._find_unique(cr, uid, alias_name, context=context)
    #     alias_ids = self.search(cr, uid, [('alias_name','=','donotreply')])
    #     if alias_ids:
    #         return alias_ids[0]
    #     vals['alias_name'] = alias_name
    #     if model_name:
    #         model_id = self.pool.get('ir.model').search(cr, uid, [('model', '=', model_name)], context=context)[0]
    #         vals['alias_model_id'] = model_id
    #     return self.create(cr, uid, vals, context=context)

    @api.model
    def create(self,vals):
        # User alias is sync'ed with 'donotreply'
        vals['alias_name'] = 'donotreply'
        res = super(mail_alias, self).create(vals)
        return res

    @api.multi
    def write(self,vals):
        # User alias is sync'ed with login
        vals['alias_name'] = 'donotreply'
        res = super(mail_alias, self).write(vals)
        return res
    
#    def migrate_to_alias(self, cr, child_model_name, child_table_name, child_model_auto_init_fct,
#        alias_id_column, alias_key, alias_prefix='', alias_force_key='', alias_defaults={}, context=None):
#        """ Installation hook to create aliases for all users and avoid constraint errors.
#
#            :param child_model_name: model name of the child class (i.e. res.users)
#            :param child_table_name: table name of the child class (i.e. res_users)
#            :param child_model_auto_init_fct: pointer to the _auto_init function
#                (i.e. super(res_users,self)._auto_init(cr, context=context))
#            :param alias_id_column: alias_id column (i.e. self._columns['alias_id'])
#            :param alias_key: name of the column used for the unique name (i.e. 'login')
#            :param alias_prefix: prefix for the unique name (i.e. 'jobs' + ...)
#            :param alias_force_key': name of the column for force_thread_id;
#                if empty string, not taken into account
#            :param alias_defaults: dict, keys = mail.alias columns, values = child
#                model column name used for default values (i.e. {'job_id': 'id'})
#        """
#        if context is None:
#            context = {}
#
#        # disable the unique alias_id not null constraint, to avoid spurious warning during
#        # super.auto_init. We'll reinstall it afterwards.
#        alias_id_column.required = False
#
#        # call _auto_init
#        result = child_model_auto_init_fct(cr, context=context)
#
#        registry = RegistryManager.get(cr.dbname)
#        mail_alias = registry.get('mail.alias')
#        child_class_model = registry.get(child_model_name)
#        no_alias_ids = child_class_model.search(cr, SUPERUSER_ID, [('alias_id', '=', False)], context={'active_test': False})
#        # Use read() not browse(), to avoid prefetching uninitialized inherited fields
#        for obj_data in child_class_model.read(cr, SUPERUSER_ID, no_alias_ids, [alias_key]):
#            alias_vals = {'alias_name': '%s%s' % (alias_prefix, 'donotreply')}
#            print "alias_vals.........",alias_vals
#            if alias_force_key:
#                alias_vals['alias_force_thread_id'] = obj_data[alias_force_key]
#            alias_vals['alias_defaults'] = dict((k, obj_data[v]) for k, v in alias_defaults.iteritems())
#            alias_id = mail_alias.create_unique_alias(cr, SUPERUSER_ID, alias_vals, model_name=context.get('alias_model_name', child_model_name))
#            child_class_model.write(cr, SUPERUSER_ID, obj_data['id'], {'alias_id': alias_id})
#            _logger.info('Mail alias created for %s %s (uid %s)', child_model_name, obj_data[alias_key], obj_data['id'])
#
#        # Finally attempt to reinstate the missing constraint
#        try:
#            cr.execute('ALTER TABLE %s ALTER COLUMN alias_id SET NOT NULL' % (child_table_name))
#        except Exception:
#            _logger.warning("Table '%s': unable to set a NOT NULL constraint on column '%s' !\n"\
#                            "If you want to have it, you should update the records and execute manually:\n"\
#                            "ALTER TABLE %s ALTER COLUMN %s SET NOT NULL",
#                            child_table_name, 'alias_id', child_table_name, 'alias_id')
#
#        # set back the unique alias_id constraint
#        alias_id_column.required = True
#        return result

    
