# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

import hashlib
import itertools
import logging
import os
import re

from odoo import tools
from odoo import fields,models,api
from odoo import SUPERUSER_ID
from odoo.tools import config, human_size, ustr, html_escape

_logger = logging.getLogger(__name__)

class ir_attachment(models.Model):
    _inherit = 'ir.attachment'
    
    def check_file_exist(self,file_path):
        if os.path.isfile(file_path):
            return True
        return False
# This function is overriden to add proper extension
#     def _full_path(self, cr, uid, location, path):
#         # location = 'file:filestore'
# #        assert location.startswith('file:'), "Unhandled filestore location %s" % location
# #        location = location[5:]
# #
# #        # sanitize location name and path
# #        location = re.sub('[.]','',location)
# #        location = location.strip('/\\')
# #
# #        path = path.strip('/\\')
# #        return os.path.join(tools.config['root_path'], location, '', path)#cr.dbname
#         return os.path.join('', location, '', path)#cr.dbname

    @api.model
    def _file_write(self, value, checksum):
        bin_value = value.decode('base64')
        fname, full_path = self._get_path(bin_value, checksum)
        fname2=fname
        i, ext, fname_next = 1, False, ''
        while self.check_file_exist(full_path):
            if i == 1:
                fname = fname.split('.')
                if len(fname) > 1:
                    ext = fname[1]
            else:
                fname = fname.split('.')
                if len(fname) > 1:
                    ext = fname[1]
            if ext:
                fname_next = fname2 + "_" + str(i) + "." + ext
            else:
                fname_next = fname2 + "_" + str(i)
            fname = fname_next
            full_path = self._full_path(fname)
            i += 1
        if not os.path.exists(full_path):
            try:
                with open(full_path, 'wb') as fp:
                    fp.write(bin_value)
                # add fname to checklist, in case the transaction aborts
                self._mark_for_gc(fname)
            except IOError:
                _logger.info("_file_write writing %s", full_path, exc_info=True)
        return fname
# This function is overriden to give proper filename as required
#     def _file_write(self, cr, uid,id, location, value):
#         bin_value = value.decode('base64')
#         attach = self.browse(cr, uid, id)
#         #fname= str(attach.res_model).replace('.','_')+"/"+ attach.name
#         fname= attach.name
# #        fname = fname[:3] + '/' + fname
#         full_path = self._full_path(cr, uid, location, fname)
# #        print "full_path..........",full_path
#         i , ext, fname_next  = 1, False , ''
#         while self.check_file_exist(full_path):
#             if i==1:
#                 fname = fname.split('.')
#                 if len(fname) > 1 :
#                     ext = fname[1]
#             else:
#                 fname = fname.split('.')
#                 if len(fname) > 1 :
#                     ext = fname[1]
#             if ext:
#                 fname_next = attach.name + "_" + str(i)+"."+ext
#             else:
#                 fname_next = attach.name + "_" + str(i)
#             fname = fname_next
#             full_path = self._full_path(cr, uid, location, fname)
#             i+=1
#         try:
#             dirname = os.path.dirname(full_path)
#             if not os.path.isdir(dirname):
#                 os.makedirs(dirname)
#             open(full_path,'wb').write(bin_value)
#         except IOError:
#             _logger.error("_file_write writing %s",full_path)
#         return fname
#
#     def _data_get(self, cr, uid, ids, name, arg, context=None):
#         if context is None: context = {}
#         result = {}
#         location = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ir_attachment.location')
#         bin_size = context.get('bin_size')
#         for attach in self.browse(cr, uid, ids, context=context):
#             if location and attach.store_fname:
#                 result[attach.id] = self._file_read(cr, uid, location, attach.store_fname, bin_size)
# #                print "attach.store_fname......",attach.store_fname
#             else:
#                 result[attach.id] = attach.db_datas
#         return result
#
#
#     def _data_set(self, cr, uid, id, name, value, arg, context):
#         # We dont handle setting data to null
#         if not value: return True
#         if context is None: context = {}
#         location = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ir_attachment.location')
# #        print "location..........",location
#         #file:///filestore
#         file_size = len(value.decode('base64'))
# #        bin_value = value.decode('base64')
#         if location:
#             attach = self.browse(cr, uid, id, context=context)
#             if attach.store_fname:
#                 self._file_delete(cr, uid, location, attach.store_fname)
# #            location=location+"/"+str(attach.res_model).replace('.','_')
#             fname = self._file_write(cr, uid,id, location, value)
#             #For storing data in attachment master
#             # SUPERUSER_ID as probably don't have write access, trigger during create
#             super(ir_attachment, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
#         else:
#             super(ir_attachment, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
#         return True



    @api.depends('document_type_id')
    def _name_get_fnc(self):
        ''' Function to store complete Attachment name to be shown '''
        res={}
        for line in self:
            complete_name = ""
            if line.document_type_id:
                complete_name = "[" + line.document_type_id.name.encode('utf-8', 'ignore') + "] " + line.name.encode('utf-8', 'ignore')
            else:
                complete_name = line.name.encode('utf-8', 'ignore')
            line.complete_name=complete_name

    @api.model
    def _file_read(self, fname, bin_size=False):
        full_path = self.with_context(read=True)._full_path(fname)
        r = ''
        try:
            if bin_size:
                r = human_size(os.path.getsize(full_path))
            else:
                r = open(full_path, 'rb').read().encode('base64')
        except (IOError, OSError):
            _logger.info("_read_file reading %s", full_path, exc_info=True)
        return r

    @api.model
    def _full_path(self, path):
        # sanitize path
        if self._context.get('read',False):
            pass
        else:
            path = re.sub('[.]', '', path)
        path = path.strip('/\\')
        return os.path.join(self._filestore(), path)

    attach=fields.Boolean('Custom name')
    no_of_pages=fields.Integer("No of Pages")
    no_of_words=fields.Integer("No of words")
    event_id=fields.Many2one('event','Event Id')
    in_fax_id=fields.Many2one('incoming.fax','Incoming Fax')
#                'fax_type': fields.many2one('fax.type','Fax Type'),
    document_type_id=fields.Many2one('document.type','Document Type')
    complete_name=fields.Char(compute='_name_get_fnc', string='Complete Name',store=True)

    @api.multi
    def select_attach(self):
        self.write({'attach':True})
        return True
    
#    def create(self, cr, uid, values, context=None):
#        if 'datas_fname' not in values or not values['datas_fname']:
#            if 'name' in values['name'] and values['name']:
#                values['datas_fname'] = values['name']
#        return super(ir_attachment, self).create(cr, uid, values, context)
    
    