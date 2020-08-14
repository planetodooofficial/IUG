# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
import os
from odoo import fields, models,api
from odoo.tools.translate import _
from odoo.exceptions import UserError, RedirectWarning, ValidationError
''' 
These are config and Migration scripts for documents from old db.
'''
class attach_attachments(models.TransientModel):
    _name = "attach.attachments"

    @api.model
    def get_doc_dir_path(self):
        """Return the Document Directory path"""
        proxy = self.env['ir.config_parameter']
        file_path = proxy.sudo().get_param('doc_dir_path')
        if not file_path:
            raise UserError('Please configure doc_dir_path as "file:///filestore" in config parameters.')
        if not file_path.endswith('/'):
            file_path += '/'
        return file_path

    @api.multi
    def create_attachments_for_all(self):
        '''Function to create ir.attachment for customer and load old attachments from Document Sender Table'''
#        doc_obj= self.pool.get('document')
        sender_obj = self.env['document.sender']
        doc_ids = sender_obj.search([])
        ir_attachment = self.env['ir.attachment']
        count = 0
        for doc in doc_ids:
            if not doc.document_id:
                continue
            count += 1
            if doc.document_id and doc.document_id.name:
                path = self.get_doc_dir_path()
                if os.path.exists(path+doc.document_id.name):
                    print "exist... file",path+doc.document_id.name
                    attachment_data = {
                        'name': doc.document_id.name,
                        'datas_fname': doc.document_id.name,
                        'datas': False,
                        'document_type_id': doc.document_id and doc.document_id.doc_type_id and doc.document_id.doc_type_id.id or False,
                        'res_model': 'res.partner',
                        'user_id': self._uid,
                        'store_fname': doc.document_id.name or False,#doc.document_id.name.split('.', 1)[0] or False,
                        'company_id': doc.company_id and doc.company_id.id or False,
                    }
                    if doc.interpreter_id:
                        attachment_data['res_id'] = doc.interpreter_id and doc.interpreter_id.id or False
                    elif doc.vendor_id:
                        vendor_ids = self.env['res.partner'].search([('vendor_id','=',doc.vendor_id),('company_id','=',doc.company_id and doc.company_id.id or False)])
                        if vendor_ids:
                            attachment_data['res_id'] = vendor_ids[0]
                    if doc.customer_id:
                        attachment_data['res_id'] = doc.customer_id and doc.customer_id.id or False
                    elif doc.contact_id:
                        attachment_data['res_id'] = doc.contact_id and doc.contact_id.id or False
                    ir_attachment.create(attachment_data)
                else:
                    print "does not exist ..",path+doc.document_id.name
            if count % 1000 == 0:
                print "count.....",count
                self._cr.commit()
        return True

    @api.multi
    def create_attachments_for_all_recipient(self):
        '''Function to create ir.attachment for customer and load old attachments from Document Recipient Table'''
#        doc_obj= self.pool.get('document')
        sender_obj = self.env['document.recipient']
        doc_ids = sender_obj.search([])
        ir_attachment = self.env['ir.attachment']
        count = 0
        for doc in doc_ids:
#            print "doc....",doc
            if not doc.document_id:
                continue
#            if not doc.vendor_id and (not doc.customer_id or not doc.contact_id):
#                continue
            count += 1
            if doc.document_id and doc.document_id.name:
                path = self.get_doc_dir_path()
                if os.path.exists(path+doc.document_id.name):
                    print "exist... file",path+doc.document_id.name
                    attachment_data = {
                        'name': doc.document_id.name,
                        'datas_fname': doc.document_id.name,
                        'datas': False,
                        'document_type_id': doc.document_id and doc.document_id.doc_type_id and doc.document_id.doc_type_id.id or False,
                        'res_model': 'res.partner',
                        'user_id': self._uid,
                        'store_fname': doc.document_id.name or False,#doc.document_id.name.split('.', 1)[0] or False,
                        'company_id': doc.company_id and doc.company_id.id or False,
                    }
                    if doc.interpreter_id:
                        attachment_data['res_id'] = doc.interpreter_id and doc.interpreter_id.id or False
                    elif doc.vendor_id:
                        vendor_ids = self.env['res.partner'].search([('vendor_id','=',doc.vendor_id),('company_id','=',doc.company_id and doc.company_id.id or False)])
                        if vendor_ids:
                            attachment_data['res_id'] = vendor_ids[0]
                    if doc.customer_id:
                        attachment_data['res_id'] = doc.customer_id and doc.customer_id.id or False
                    elif doc.contact_id:
                        attachment_data['res_id'] = doc.contact_id and doc.contact_id.id or False
                    ir_attachment.create(attachment_data)
                else:
                    print "does not exist ..",path+doc.document_id.name
            if count % 1000 == 0:
                print "count.....",count
                self._cr.commit()
        return True

    @api.multi
    def create_attachments_for_events(self):
        '''Function to create ir.attachment for Events and load old attachments'''
#        doc_obj= self.pool.get('document')
        event_doc_obj = self.env['document.to.event']
        doc_ids = event_doc_obj.search([])
        print "event doc_ids......",len(doc_ids)
        ir_attachment = self.env['ir.attachment']
        count = 0
        for doc in doc_ids:
#            print "doc....",doc
            if not doc.document_id: continue
            if not doc.event_id: continue
#            if not doc.vendor_id and (not doc.customer_id or not doc.contact_id):
#                continue
            count += 1
            if doc.document_id and doc.document_id.name:
                path = self.get_doc_dir_path()
                if os.path.exists(path+doc.document_id.name):
                    print "Exist... file",path+doc.document_id.name
                    if doc.event_id:
                        attachment_data = {
                            'name': doc.document_id.name,
                            'datas_fname': doc.document_id.name,
                            'datas': False,
                            'document_type_id': doc.document_id and doc.document_id.doc_type_id and doc.document_id.doc_type_id.id or False,
                            'res_model': 'event',
                            'user_id': self._uid,
                            'res_id': doc.event_id and doc.event_id.id or False,
                            'store_fname': doc.document_id.name or False,#doc.document_id.name.split('.', 1)[0] or False,
                            'company_id': doc.company_id and doc.company_id.id or False,
                        }
                        ir_attachment.create(attachment_data)
                else:
                    print "Does not exist ..",path+doc.document_id.name
            if count % 1000 == 0:
                print "count.....",count
                self._cr.commit()
        return True

#    def rename_files(self , cr , uid , ids , context=None):
#        ''' Function to rename all files of a folder , so that documents can be transferred '''
#        #path =  os.getcwd()
#        #path = """/home/openerp/test_folder"""
#        path = self.get_doc_dir_path( cr , uid , context=context)
#        filenames = os.listdir(path)
##        print "filenames......",filenames
#        for filename in filenames:
##            print "filename...........",filename
#            new_filename = filename.split('.', 1)[0];
##            print "new_filename.........",new_filename
#            os.rename(os.path.join(path,filename), os.path.join(path, new_filename))
#        return True
#
#    def create_attachments_for_interpreter(self, cr, uid, ids, context=None):
#        '''Function to create ir.attachment for interpret and load old attachments'''
#        doc_obj= self.pool.get('document')
#        sender_obj = self.pool.get('document.sender')
#        #doc_ids = sender_obj.search(cr , uid , [('vendor_id','is not', False),('document_id','is not',False)])
#        #doc_ids = sender_obj.search(cr , uid , [])
#        ir_attachment = self.pool.get('ir.attachment')
#        count = 0
#        for doc in sender_obj.browse(cr , uid ,range(1,10)):
#            print "doc....",doc
#            count += 1
#            if doc.document_id and doc.document_id.name:
#                path = self.get_doc_dir_path( cr , uid , context=context)
#                if os.path.exists(path+doc.document_id.name):
#                    print "exist... file",path+doc.document_id.name
#                    attachment_data = {
#                        'name': doc.document_id.name,
#                        'datas_fname': doc.document_id.name,
#                        'datas': False,
#                        'document_type_id': doc.document_id and doc.document_id.doc_type_id and doc.document_id.doc_type_id.id or False,
#                        'res_model': 'res.partner',
#                        'res_id': doc.interpreter_id and doc.interpreter_id.id or False,
#                        'user_id': 1,
#                        'store_fname': doc.document_id.name or False,#doc.document_id.name.split('.', 1)[0] or False,
#                        'company_id': doc.company_id and doc.company_id.id or False,
#                    }
#                    ir_attachment.create(cr, uid, attachment_data, context=context)
#                else:
#                    print "does not exist ..",path+doc.document_id.name
#            if count % 1000 == 0:
#                print "count.....",count
#                cr.commit()
#        return True
#
#    def create_attachments_for_vendors(self, cr, uid, ids, context=None):
#        '''Function to create ir.attachment for vendors and load old attachments'''
#        doc_obj= self.pool.get('document')
#        sender_obj = self.pool.get('document.sender')
#        #doc_ids = sender_obj.search(cr , uid , [('vendor_id','is not', False),('document_id','is not',False)])
#        #doc_ids = sender_obj.search(cr , uid , [])
#        ir_attachment = self.pool.get('ir.attachment')
#        count = 0
#        for doc in sender_obj.browse(cr , uid ,range(1,10)):
#            print "doc....",doc
#            count += 1
#            if doc.document_id and doc.document_id.name:
#                path = self.get_doc_dir_path( cr , uid , context=context)
#                if os.path.exists(path+doc.document_id.name):
#                    print "exist... file",path+doc.document_id.name
#                    attachment_data = {
#                        'name': doc.document_id.name,
#                        'datas_fname': doc.document_id.name,
#                        'datas': False,
#                        'document_type_id': doc.document_id and doc.document_id.doc_type_id and doc.document_id.doc_type_id.id or False,
#                        'res_model': 'res.partner',
#                        'res_id': doc.interpreter_id and doc.interpreter_id.id or False,
#                        'user_id': 1,
#                        'store_fname': doc.document_id.name or False,#doc.document_id.name.split('.', 1)[0] or False,
#                        'company_id': doc.company_id and doc.company_id.id or False,
#                    }
#                    ir_attachment.create(cr, uid, attachment_data, context=context)
#                else:
#                    print "does not exist ..",path+doc.document_id.name
#            if count % 1000 == 0:
#                print "count.....",count
#                cr.commit()
#        return True