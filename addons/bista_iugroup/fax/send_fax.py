# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-Today OpenERP S.A. (<http://www.openerp.com>).
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
import time
import base64
from odoo import models, fields,_,api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import datetime
import os
from odoo.exceptions import UserError, RedirectWarning, ValidationError

class incoming_fax(models.Model):
    '''Keeps Incoming Fax'''
    _name = 'incoming.fax'
    _order = 'date desc, fax_date desc'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Incoming Fax'
    
    @api.onchange('company_id')
    def onchange_company_id(self):
        val={
            'partner_id': False,
            'event_id': False,
            }
        return {'value': val}

    @api.onchange('attach_to')
    def onchange_attach_to(self):
        ''' Onchange Function to bring Fax from partner '''

        if self.attach_to and self.attach_to == 'event':
            val={
                'partner_id': False,
                'event_id': False,
            }
        else:
            val={
                'partner_id': False,
                'event_id': False,
                }
        return {'value': val}

    @api.onchange('document_type_id')
    def onchange_document_type_id(self):
        val={}
        if self.document_type_id:

            doc_name=self.document_type_id.name
            if 'bad' in doc_name.lower():
                val={'doc_type':'other',
#                     'state_visible':True,
                     'state':'done',
                     }
            else:
              val={  'doc_type':'',
#                     'state_visible':False,
                     'state':'done',
                     }
        return {'value':val}

    @api.multi
    def attach_documents_old(self):
        ''' Function to attach incoming Documents to any event or Partner '''
        ir_attachment = self.env['ir.attachment']
        for cur in self:
            if cur.attach_to == 'event' and cur.event_id:
                for attach in cur.fax_attachment_ids:
                    if attach.attach:
                        attachment_data = {
                        'name': attach.name,
                        'datas_fname': attach.datas_fname,
                        'datas': attach.datas,
                        'res_model':'event',
                        'res_id':cur.event_id.id,
                        'res_name':cur.event_id.name,
                        'document_type_id': attach.document_type_id and attach.document_type_id.id or False,
                        }
                        ir_attachment.create(attachment_data)
                        if cur.doc_type and cur.doc_type == 'fee_note':
                            cur.event_id.write({'fee_note_test':True})
                        elif cur.doc_type and cur.doc_type == 'saf':
                            cur.event_id.write({'order_note_test':True})
                        cur.write({'attached':True})
            elif cur.attach_to == 'partner' and cur.partner_id:
                for attach in cur.fax_attachment_ids:
                    if attach.attach:
                        attachment_data = {
                        'name': attach.name,
                        'datas_fname': attach.datas_fname,
                        'datas': attach.datas,
                        'res_model':'res.partner',
                        'res_id':cur.partner_id.id,
                        'res_name':cur.partner_id.name,
                        'document_type_id': attach.document_type_id and attach.document_type_id.id or False,
                        }
                        ir_attachment.create(attachment_data)
                    cur.write({'attached':True})
        return True

    @api.multi
    def attach_documents(self):
        ''' Function to attach incoming Documents to any event or Partner '''
        ir_attachment = self.env['ir.attachment']
        for cur in self:
            if cur.fax_attachment_id:
                attachment_data = {
                        'name': cur.fax_attachment_id.name,
                        'datas_fname': cur.fax_attachment_id.datas_fname,
                        'datas': cur.fax_attachment_id.datas,
                        'document_type_id': cur.document_type_id and cur.document_type_id.id or False,
                        'company_id': cur.company_id2.id,
                        }
                if cur.attach_to == 'event' and cur.event_ids:
                    for event in cur.event_ids:
                        attachment_data.update({
                        'res_model':'event',
                        'res_id':event.id,
                        'res_name':event.name,
                        })
                        ir_attachment.create(attachment_data)
                        if cur.doc_type and cur.doc_type == 'fee_note':
                            event.write({'fee_note_test':True})
                        elif cur.doc_type and cur.doc_type == 'saf':
                            event.write({'order_note_test':True})
                        cur.write({'attached':True})
                elif cur.attach_to == 'partner' and cur.partner_ids:
                    for partner in cur.partner_ids:
                        attachment_data.update({
                        'res_model':'res.partner',
                        'res_id':partner.id,
                        'res_name':partner.name,
                        })
                        ir_attachment.create(attachment_data)
                    cur.write({'attached':True})
        return True

    @api.depends('date')
    def _get_date(self):
        """ get fax date from incoming fax """
        for fax_in in self:
            DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            date_planned = False
            if fax_in.date:
                from_dt = datetime.datetime.strptime(str(fax_in.date[:19]), DATETIME_FORMAT)
    #            from_dt = from_dt + datetime.timedelta(hours=5 , minutes=30)
                date_planned = from_dt.strftime('%Y-%m-%d')
            fax_in.fax_date = date_planned

    @api.multi
    def fax_script(self):
        ids_list = self.search([])
        event, partner, attachment = False, False, False
        count = 0
        for each_fax in self:
            count += 1
            event = each_fax.event_id.id if each_fax.event_id else False
            partner = each_fax.partner_id.id if each_fax.partner_id else False
            attachment = each_fax.fax_attachment_ids[0].id if each_fax.fax_attachment_ids else False
            each_fax.write({'event_ids': [(4,event)] if event else False, 'partner_ids': [(4,partner)] if partner else False, 'fax_attachment_id': attachment})
        if count%100:
            print "coount+++++++",count

        return True


    name=fields.Char('Subject', size=300)
    fax=fields.Char('Fax', size=64, index=1)
    date=fields.Datetime('Date')
    fax_date=fields.Char(compute='_get_date', string='Fax Date' ,store=True)
    attach_to=fields.Selection([('event','Event'),('partner','Partner')],'Attach To',default='event')
    doc_type=fields.Selection([('fee_note','Fee Note'),('saf','SAF'),('other','Other')],'Document Type')
    partner_id=fields.Many2one('res.partner','Partner')
    event_id=fields.Many2one('event','Event')
    partner_ids=fields.Many2many('res.partner','fax_partner_rel','fax_id','partner_id','Partners')
    event_ids=fields.Many2many('event','fax_event_rel','fax_id','event_id','Events')
    company_id=fields.Many2one('res.company', 'Company', index=1,default=lambda self: self.env['res.company']._company_default_get('incoming.fax'))
    company_id2=fields.Many2one('res.company', 'Select Company',default=lambda self: self.env['res.company']._company_default_get('incoming.fax'))
    fax_attachment_ids=fields.One2many('ir.attachment','in_fax_id','Incoming Fax')
    fax_attachment_id=fields.Many2one('ir.attachment','Incoming Fax')
    document_type_id=fields.Many2one('document.type','Document Type')
    attached=fields.Boolean('Attached')
    datas_rel=fields.Binary(related='fax_attachment_id.datas',string = 'Download')
    datas_fname_rel=fields.Char(related='fax_attachment_id.datas_fname',size = 64 ,string = 'Filename')
    msg_id=fields.Integer('Message id')
    ph_no=fields.Char('Phone Number')
    csid=fields.Char('Remote CSID')
    msg_stat=fields.Char('Msg Stat')
    pages=fields.Integer('Pages')
    msg_size=fields.Integer('Size')
    msg_type=fields.Char('Type')
    rcv_time=fields.Char('Receive Time')
    caller_id=fields.Char('Caller Id', size=64, index=1)
    rec_duration=fields.Char('MessageRecordingDuration')
    received_status=fields.Char('Status')
    state=fields.Selection([('done','Done'),('close','Close')],'State')


    @api.multi
    def get_fax(self):
        in_fax = self.env['incoming.fax']
        succecced_list, files=[],[]
        attach_id, fax_id = False, False
        interfax = self.env['inbound.interfax']
        rec_dict = interfax.get_fax()
        if rec_dict:
            in_list,failed,succecced = rec_dict.get('received',False),rec_dict.get('failed',False),rec_dict.get('succecced',False)
            #in_list contains description of each and every msgs received at interfax 
            # Hence querying it with succecced msgs which are successfully received by us.
            for tup in succecced:
                # Getting Description of succedded messages.
                succecced_list.extend([each_tup for each_tup in in_list if each_tup[0]==tup[0]])
            for each_tup in succecced_list:
                print "--------------------------",type(each_tup[0]),each_tup[0]
                
                files.append(r"/opt/openerp-7.0/temp_fax_in/%d.pdf" % each_tup[0])
                fp = open(r"/opt/openerp-7.0/temp_fax_in/%d.pdf" % each_tup[0],'rb')
                cont = fp.read()
                
#                print
                fp.close()
#                if isinstance(cont, unicode):
#                    cont = cont.encode('utf-8')
                content = base64.b64encode(cont)
#                content = base64.b64encode(str(cont))
#                print "b4 cretater++++++++++++++++++++++"
                
                fax_id = in_fax.create({'msg_id':each_tup[0],'ph_no':each_tup[1],'csid': each_tup[2],
                    'msg_stat':each_tup[3],'pages':each_tup[4],'msg_size':each_tup[5],'msg_type':each_tup[6],
                    'rcv_time':each_tup[7],'caller_id':each_tup[8] ,'rec_duration':each_tup[9],'date':datetime.datetime.now(),
                    })

                attach_id =self.env['ir.attachment'].create({'name': str(each_tup[0])+'.pdf','datas_fname': str(each_tup[0])+'.pdf',
                    'datas': content ,'description': str(each_tup[0])+'.pdf',
                    'res_model': 'incoming.fax','res_id': fax_id.id})
#                attach_id =[(0, 0, {'name': str(each_tup[0])+'.pdf','datas_fname': str(each_tup[0])+'.pdf',
#                    'datas': content ,'description': str(each_tup[0])+'.pdf',
#                    'res_model': 'incoming.fax','res_id': fax_id})]
                if attach_id:
#                    fax_id = in_fax.write(cr,uid,[fax_id],{'fax_attachment_ids': [(6,0,[attach_id])]})
                    fax_id = fax_id.write({'fax_attachment_id':attach_id.id})
#                print "after cretater++++++++++++++++++++++"
    #                'res_id': res_id
        if files:
            is_removed = [os.remove(path_name) for path_name in files if os.path.isfile(path_name)]
        return True

class outgoing_fax(models.Model):
    '''Fax Sent History '''
    _name = 'outgoing.fax'
    _description = 'Outgoing Fax'

    @api.depends('date')
    def _get_date(self):
        """ get fax date from incoming fax """
        for fax_out in self:
            DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            date_planned = False
            if fax_out.date:
                from_dt = datetime.datetime.strptime(str(fax_out.date[:19]), DATETIME_FORMAT)
    #            from_dt = from_dt + datetime.timedelta(hours=5 , minutes=30)
                date_planned = from_dt.strftime('%Y-%m-%d')
            fax_out.fax_date = date_planned

    

    name=fields.Char('Attachment name')
    partner_id=fields.Many2one('res.partner',"Partner", )
    fax=fields.Char('Fax', size=64)
    date=fields.Datetime('Date')
    fax_date=fields.Date(compute='_get_date', string='Fax Date' ,store=True)
    fax_cover=fields.Text('Fax Cover')
    company_id=fields.Many2one('res.company', 'Company', index=1,default=lambda self: self.env['res.company']._company_default_get('outgoing.fax'))
#                'fax_attachment_ids': fields.many2many('ir.attachment', 'fax_attachment_rel',
#                    'fax_id', 'attachment_id', 'Attachments'),
    sent_fax_status=fields.Char('Fax Status')
    stat_des=fields.Char('Description')
    trans_id=fields.Integer('Transaction Id')

    @api.multi
    def get_status_out(self):
        out_ids=[]
        trans_ids = []
        interfax = self.env['outbound.interfax']
        stat_dict = interfax.get_status(number=20)
#        print stat_dict
        for trans_id in stat_dict:
#            print "trans-id from stat dicty__+++++",type(trans_id)
            out_ids.extend(self.search([('trans_id','=',trans_id)]))
#            print out_ids
        for id in out_ids:
            trans_id = id.trans_id
#            print "trans id from berewse errec+++",type(int(trans_id))
            id.write({'sent_fax_status':stat_dict[int(trans_id)]['status'],'stat_des':stat_dict[int(trans_id)]['description']})
        return True

class fax_attachments(models.TransientModel):
    '''Used in fax Attachments '''
    _name = 'fax.attachments'
    _description = 'Fax Attachments'

    name=fields.Char('Attachment name')
    datas=fields.Binary('Attachment')
    send_fax_id=fields.Many2one('send.fax','Send Fax')
    document_type_id=fields.Many2one('document.type','Document Action')


class send_fax(models.TransientModel):
    '''Form For Fax sending '''
    _name = 'send.fax'
    _description = 'Send Faxes'

    @api.depends('partner_id')
    def _get_name(self):
        ''' Returns name for Fax '''
        for obj in self:
            if obj.partner_id :
                obj.name =  obj.partner_id.name
            else:
                obj.name = ""


    @api.depends('show_fax')
    def _get_fax(self):
        ''' Returns Fax  '''
        result = {}
        for obj in self:
            if obj.show_fax:
                obj.fax=  re.sub(r'[^0-9]',r'',str(obj.show_fax).strip())
            else:
                obj.fax = ""


    @api.depends('send_attachment_ids')
    def _count_attachments(self):
        ''' Returns No of Attachments  '''
        result = {}
        count = 0
        for obj in self:
            if obj.send_attachment_ids :
                for attachment in obj.send_attachment_ids:
                    count += 1
            obj.count= count
    

    name=fields.Char(compute='_get_name', string='Is Empty', store=True)
    partner_id=fields.Many2one('res.partner',"Partner",)
    send_attachment_ids=fields.One2many('fax.attachments','send_fax_id',"Attachments")
    state=fields.Selection([('draft','New'),('done','Sent')],'State',default='draft')
    fax=fields.Char(compute='_get_fax', string='Fax', store=True)
    show_fax=fields.Char('Fax', size=32)
    manual_fax=fields.Boolean('Send To Partner?',default=True)
    fax_cover=fields.Text('Fax Cover')
    count=fields.Integer(compute='_count_attachments', string='No of Attachments')
    existing=fields.Selection([('event','Event'),('partner','Partner')],'Existing')
    partner_attachment=fields.Many2one('res.partner',"Partner Attachment")
    event_attachment=fields.Many2one('event',"Event Attachment")

    @api.onchange('partner_id')
    def onchange_partner_attachment(self):
        vals = {}
        vals['send_attachment_ids'] = []

        if self.partner_id:
            attach_ids = []
            attachment_obj = self.env['ir.attachment']
            attach_ids = attachment_obj.search([('res_model','=','res.partner'),('res_id','=',self.partner_id.id)])
    #        print "attach_idsattach_ids++++++++++++++++++"   , attach_ids
            for attachment in attach_ids:
                val = {
                    'name': attachment.name,
                    'data': attachment.db_datas,
                    'document_type_id': attachment.document_type_id and attachment.document_type_id.id or False,
                }
                vals['send_attachment_ids'].append((0, 0, val))
        return {'value':vals}

    @api.onchange('event_attachment')
    def onchange_event_attachment(self):
        vals = {}
        vals['send_attachment_ids'] =[]
        if self.event_attachment:
            attach_ids = []
            attachment_obj = self.env['ir.attachment']
            attach_ids = attachment_obj.search([('res_model', '=', 'event'), ('res_id', '=', self.event_attachment.id)])
            for attachment in attach_ids:
                val = {
                    'name': attachment.name,
                    'data': attachment.db_datas,
                    'document_type_id': attachment.document_type_id and attachment.document_type_id.id or False,
                }
                vals['send_attachment_ids'].append((0, 0, val))
        return {'value':vals}

    @api.multi
    def send_fax(self):
        '''Function to send Fax '''
        fax_numbers , filenames = [],[]
        interfax = self.env['outbound.interfax']
        ir_model_data = self.env['ir.model.data']
        ir_attachment = self.env['ir.attachment']
        outgoing_obj = self.env['outgoing.fax']
        for each in self:
            if each.count < 1:
                raise UserError(_("No Attachment is selected to send via Fax"))
            if each.manual_fax:
                if not each.partner_id:
                    raise UserError(_("No Partner is selected to send Fax"))
            if each.manual_fax:
                if each.partner_id:
                    fax = each.partner_id.fax
                    if not fax:
                        raise UserError(_("No Fax is available for this Partner. Open form to enter Fax"))
            if not each.fax:
                raise UserError(_("No Fax Number"))
#            template_id = False
#            try:
#                template_id = ir_model_data.get_object_reference(cr, uid, 'bista_iugroup', 'event_fax_sending_template')[1]
#                #print"template_id",template_id
#            except ValueError:
#                template_id = False
#            if template_id:
#                msg_id = self.pool.get('email.template').send_mail_custom( cr, uid, template_id, each.id, True, each , context)
#                print "msg_id .......",msg_id
            attachment_ids = []
            fax_numbers = [str(each.fax)]
#            fax_numbers = ['+14084305814']
            for attachment in each.send_attachment_ids:
#                print "attachment name+++++++",attachment.name
                file_name = str(self._uid)+'_'+str(attachment.name)
                file_path = r'/opt/openerp-7.0/temp_fax/%s'%file_name
                fp = open(file_path,'w')
                fp.write(attachment.datas.decode('base64'))
                fp.close()
                filenames.append(file_path)
            if fax_numbers and filenames:
                stat_dict = interfax.send_fax(fax_numbers=fax_numbers,filenames = filenames)
#            print "stauttsaas++++++++++++",stat_dict
                history_data = {
                    'partner_id': each.partner_id and each.partner_id.id or False,
                    'name': each.name or '',
                    'fax': each.fax or '',
                    'date': str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                    'sent_fax_status': stat_dict['status'],
                    'trans_id': stat_dict['transmission_id'],
                    'stat_des': stat_dict['description'],

                    }
                history_id = outgoing_obj.create(history_data).id
            
                for attachment in each.send_attachment_ids:
    #                print "attachment name+++++++",attachment.name

                    attachment_data = {
                        'name': attachment.name,
                        'datas_fname': attachment.name,
                        'datas': attachment.datas,
                        'res_model': 'outgoing.fax',
                        'res_id': history_id or False,
    #                    'document_type_id':attachment.document_type_id
                    }

                    attachment_ids.append(ir_attachment.create(attachment_data).id)
#                outgoing_obj.write(cr, uid, [history_id], {'attachment_ids': [(6, 0, attachment_ids)]}, context=context)
        if filenames:
            is_removed= [os.remove(path_name) for path_name in filenames if os.path.isfile(path_name)]
#            print "-----is removed+++++++++++++=",is_removed
        return True

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        ''' Onchange Function to bring Fax from partner '''
        if self.partner_id:
            val={
                'show_fax': self.partner_id.fax,
                }
        else:
            val={
                'show_fax': False,
                }
        return {'value': val}
    
