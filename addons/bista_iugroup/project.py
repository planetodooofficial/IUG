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
import pytz
import datetime
from odoo import tools ,SUPERUSER_ID
from odoo import models, fields,_,api
import math
import time
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from os.path import splitext
import base64
from odoo.exceptions import UserError, RedirectWarning, ValidationError
import logging
_logger = logging.getLogger(__name__)

class project_project(models.Model):
    _inherit = "project.project"

    event_id=fields.Many2one("event","Source Event",)
    interpreter_id=fields.Many2one("res.partner","Responsible",)
    transporter_id=fields.Many2one("res.partner","Responsible",)
    event_type=fields.Selection([('language','Language'),('transport','Transport'),('translation','Translation'),('lang_trans','Language and Transport')],"Event Type")
    Project_id=fields.Integer("Project ID")
    company_id=fields.Many2one('res.company', 'Company', index=1,default=lambda self: self.env['res.company']._company_default_get('project.project'))


class project_task(models.Model):
    ''' Fields added for  Responsible interpreter '''
    _inherit = "project.task"

    @api.multi
    def _message_auto_subscribe_notify(self, partner_ids):
        return

    @api.depends('work_ids')
    def _get_interpreter_task(self):
        ''' Function to get interpreter wise task for interpreter portal '''
        work_ids = []
        for task in self:
            for each_work in task.work_ids:
                if each_work.interpreter_id and each_work.interpreter_id.user_id:
                    if each_work.task_for == 'interpreter' and each_work.interpreter_id.user_id.id == self.env.uid:
                        work_ids.append(each_work.id)
            task.interpreter_work_ids= work_ids


    def _set_interpreter_task(self):
        # work_ids = []
        # logger = logging.getLogger('test2')
        # logger.info("This is set------->%s " % str(self))
        # for task in self:
        #     for each_work in task.interpreter_work_ids:
        #         if each_work.interpreter_id and each_work.interpreter_id.user_id:
        #             if each_work.task_for == 'interpreter' and each_work.interpreter_id.user_id.id == self.env.uid:
        #                 work_ids.append(each_work.id)
        #     task.interpreter_work_ids = work_ids
        pass

    @api.depends('work_ids')
    def _get_transporter_task(self):
        ''' Function to get transporter wise task for transporter portal '''
        work_ids = []
        for task in self:
            for each_work in task.work_ids:
                if each_work.transporter_id and each_work.transporter_id.user_id:
                    if each_work.task_for == 'transporter' and each_work.transporter_id.user_id.id == self.env.uid:
                        work_ids.append(each_work.id)
            task.transporter_work_ids = work_ids



    # @api.depends('')
    # def _set_interpreter_task(self, cr, uid, id, name, value, args, context=None):
    #     ''' Function to make interpreter wise task editable for interpreter portal '''
    #     if value is False: return
    #     task_work = self.pool.get('project.task.work')
    #     for line in value:
    #         if line[0] == 1: # one2many Update
    #             line_id = line[1]
    #             task_work.write(cr, uid, [line_id], line[2])
    #     return True
    #
    def _set_transporter_task(self):
        pass

    # def _set_transporter_task(self, cr, uid, id, name, value, args, context=None):
    #     ''' Function to set Transporter task '''
    #     if value is False:
    #         return
    #     task_work = self.pool.get('project.task.work')
    #     for line in value:
    #         if line[0] == 1: # one2many Update
    #             line_id = line[1]
    #             task_work.write(cr, uid, [line_id], line[2])
    #     return True

    @api.depends('work_ids.edited')
    def _all_task_lines_edited(self):
        ''' Function to check that all timesheet lines are edited , so that marking All are Entered and Done the Task if All Edited '''
        edited = True
        logger = logging.getLogger('test2')
        logger.info("This is tasks edited------->%s " % str(self))
        for task in self:
            if task.work_ids:
                logger = logging.getLogger('test2')
                logger.info("This is tasks edited------->%s " % 'test')
                for line in task.work_ids:
                    if not line.edited:
                        edited = False
                        break
            else:
                edited = False
            logger = logging.getLogger('test2')
            logger.info("This is tasks edited------->%s " % str(self))
            task.all_edited = edited
            if edited:
                ir_model_data = self.env['ir.model.data']
                event = task.event_id
                task.remaining_hours = 0.0
                stage_id = self.env['project.task.type'].search([('name', '=', 'done')], limit=1).id
                task.stage_id = stage_id
                #vals={'remaining_hours':0.0,'stage_id':stage_id,'all_edited':True}
                if not task.date_end:
                    task.date_end = fields.datetime.now()
                    #vals.update({'date_end':fields.datetime.now()})
                #task.write(vals)
                #self._cr.commit()
                template_id = False
                if event:
                    template_id = ir_model_data.get_object_reference('bista_iugroup', 'event_time_verification')[1]
                    if event.order_note and event.verify_state != 'verified':
                        try:
                            if template_id:
                                self.env['mail.template'].sudo().browse(template_id).send_mail(event.id)
                        except Exception:
                            pass

    @api.depends('event_id','event_id.partner_id')
    def _get_partner_id(self):
        ''' Function to get partner_id from related event '''
        for task in self:
            if task.event_id:
                task.related_partner_id= task.event_id.partner_id and task.event_id.partner_id.id or False
            else:
                task.related_partner_id= False


    @api.depends('assigned_interpreters')
    def _interpreters_phone(self):
        res = {}
        phone = False
        for val in self:
            for line in val.assigned_interpreters:
                if not phone:
                    phone = line.cell_phone
            val.interpreters_phone= phone
            phone = False

    @api.depends('assigned_interpreters')
    def _interpreters_email(self):
        ''' Function to get one interpreter's email for searching purpose '''
        email = False
        for val in self:
            for line in val.assigned_interpreters:
                if not email:
                    email = line.email
            val.interpreters_email= email
            email = False

    @api.depends('assigned_interpreters')
    def _single_interpreter(self):
        ''' Function to get one interpreter for sorting purpose '''
        interpreter = False
        for event in self:
            interpreter = False
            for line in event.assigned_interpreters:
                if line.cell_phone:
                    if not interpreter:
                        interpreter = line.id
            event.view_interpreter = interpreter

#    def _get_interpreter_id(self, cr, uid, ids, field_id, args, context=None):
#        ''' Function to get interpreter_id from related event '''
#        result = {}
#        for task in self.browse(cr, SUPERUSER_ID, ids, context=context):
#            if task.event_id and task.event_id.assigned_interpreters:
#                result[task.id] = task.event_id.assigned_interpreters[0].id or False
#            else:
#                result[task.id] = False
#        returnreturn result
#    
#    def _get_task_interpreter_id(self, cr, uid, ids, context=None):
#        '''  Function to change interpreter_id stored in related task on change of interpreter_id in this event'''
#        result = {}
#        for event in self.pool.get('event').browse(cr, uid, ids, context=context):
#            result[event.task_id.id] = True
#        return result.keys()

    event_start_date=fields.Date(related='event_id.event_start_date', string='Event Date', store=True)
    event_start_time=fields.Char(related='event_id.event_start_time', string='Event start time', store=True)
    event_end_time=fields.Char(related='event_id.event_end_time', string='Event End time', store=True)
    transporter_id=fields.Many2one("res.partner","Responsible",)
    assigned_interpreters=fields.Many2many('res.partner','project_task_partner_rel','task_id','interpreter_id','Interpreters')
#        'search_interpreter_id': fields.related('assigned_interpreters', 'interpreter_id','id', type='many2one', relation='res.partner', string='Interpreter', store=True ),
#        'search_interpreter_id': fields.related('work_ids','interpreter_id', type='many2one', relation="res.partner", string="Interpreters", store=True),
    interpreters_phone=fields.Char(compute=_interpreters_phone, string="Phone", size=20,store=True)
    interpreters_email=fields.Char(compute=_interpreters_email, string="Email",size=64,store=True)
    event_id=fields.Many2one("event","Source Event",)
    billing_state=fields.Selection([('not_billed','Not Billed'),('billed','Billed')], 'Billing State',default='not_billed')
    event_type=fields.Selection([('language','Language'),('transport','Transport'),('lang_trans','Language and Transport')],"Event Type")

    cust_invoice_id=fields.Many2one('account.invoice','Customer Invoice')
    supp_invoice_ids=fields.Many2many('account.invoice','project_task_inv_rel','task_id','invoice_id','Interpreter Invoices')
    supp_invoice_id2=fields.Many2one('account.invoice','Supplier Invoice2')
    interpreter_work_ids=fields.One2many('project.task.work','task_id',string="Interpreter's Task",domain=lambda self:[('interpreter_id.user_id','=',self.env.user.id)])
    # interpreter_work_ids = fields.One2many(related='work_ids', string='Task Lines')
    transporter_work_ids=fields.One2many('project.task.work','task_id',string="Transporter's Task",domain=lambda self:[('transporter_id.user_id','=',self.env.user.id)])
    user_id_int=fields.Many2one('res.users','Interpreter 2')
    all_edited=fields.Boolean(string="All Edited?",store=True)
    related_interpreter_id=fields.Many2one(related='work_ids.interpreter_id', string='Interpreter')
    related_transporter_id=fields.Many2one(related='work_ids.transporter_id', string='Transporter' )
#        'related_partner_id': fields.related('event_id', 'partner_id', type='many2one', relation='res.partner', string='Billing Customer', store=True ),
    related_partner_id=fields.Many2one('res.partner',compute=_get_partner_id, string="Billing Customer",)
#        'search_interpreter_id': fields.function(_get_interpreter_id, type='many2one', relation='res.partner', string="Interpreter",
#                      store={
#                          'event': (_get_task_interpreter_id, ['assigned_interpreters'], 20),
#                          }),
    view_interpreter=fields.Many2one('res.partner',compute=_single_interpreter, string="Interpreter",store=True)
    edited=fields.Boolean(related='work_ids.edited', string='Edited')
    current_time=fields.Datetime('Current Time',default=lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
    timesheet_attachment=fields.Binary('Attach Timesheet')
    attachment_filename=fields.Char('Filename')
    stage_id = fields.Many2one('project.task.type', string='Stage', track_visibility='onchange')
    state=fields.Char(related='stage_id.name', store=True,string="Status", readonly=True,)

    # def script_correct_task(self, cr, uid, ids, context=None):
    #     '''Script to delete all tasks for completed and cancelled events and adding lines for deleted task lines '''
    #     if isinstance(ids, (int,long)): ids = [ids]
    #     task_ids = self.search(cr, uid, [('state','=','draft')])
    #     event_obj = self.pool.get('event')
    #     count, count1 = 0, 0
    #     for task in self.browse(cr, uid, task_ids):
    #         if task.event_id:
    #             if task.event_id.state == 'confirmed':
    #                 count += 1
    #                 print "task,........timesheet deleted", task
    #                 self.unlink(cr, uid, [task.id], context=context)
    #             elif task.event_id.state == 'unbilled' and not task.work_ids:
    #                 count1 += 1
    #                 print "task,........timesheet line created",task
    #                 event_obj.enter_timesheet(cr, uid, [task.event_id.id])
    #     print "count....count1.....",count,count1
    #     return True

    @api.multi
    def action_close(self):
        '''Overriden for marking Task lines edited and sending mails for verification'''
        ir_model_data = self.env['ir.model.data']
        event = self.event_id
        # if not ('function' in self._context and self._context['function']):
        #     for line in self.work_ids:
        #         line.write({'edited': True})

        self.remaining_hours= 0.0
        if not self.date_end:
            self.date_end= fields.datetime.now()
        stage_id=self.env['project.task.type'].search([('name','=','done')],limit=1).id
        self.stage_id=stage_id
        self._cr.commit()
        template_id = False
        if event:
            template_id = ir_model_data.get_object_reference('bista_iugroup', 'event_time_verification')[1]
            if event.order_note and event.verify_state != 'verified':
                try:
                    if template_id:
                        self.env['mail.template'].sudo().browse(template_id).send_mail(event.id)
                except Exception:
                    pass
        return True

    @api.multi
    def write(self,vals):
        res = super(project_task, self).write(vals)
        attachment_obj = self.env['ir.attachment']
        if 'timesheet_attachment' in vals and vals['timesheet_attachment']:
            for record in self:
                result = base64.decodestring(vals['timesheet_attachment'])
                rec_name = str(record.name)
                file_name = rec_name[:rec_name.find(':')]
                if not vals.get('attachment_filename').lower().endswith(('.jpg', '.tiff', '.gif', '.bmp', '.png',
                                                                         '.pdf')):
                    raise UserError(_('Unsupported File Format.'))
                uploaded_filename, extension = splitext(str(vals.get('attachment_filename')))
                file_name = file_name + '_timesheet' + extension
                attachment_id = attachment_obj.create(
                                                      { 'name': file_name,'datas': base64.encodestring(result),
                                                        'datas_fname': file_name,'res_model': self._context.get('active_model'),
                                                        'res_id': record.event_id.id,'type': 'binary',
                                                      })
        return res
#        print "vals..........",vals
#        if isinstance(ids, (int,long)): ids = [ids]
#        cur_obj = self.browse(cr, uid, ids[0])
#        if 'stage_id' in vals and vals['stage_id']:
#            if vals['stage_id'] == 7:
#                event = self.browse(cr, uid, ids[0]).event_id
#        for line in self.browse(cr, uid, ids[0]).work_ids:
#            self.pool.get('project.task.work').write(cr, uid, [line.id], {'edited': True})
#        template_id = False
#        if event:
#            template_id = ir_model_data.get_object_reference(cr, uid, 'bista_iugroup', 'event_time_verification')[1]
#            if event.order_note and event.verify_state != 'verified':
#                try:
#                    if template_id:
#                        self.pool.get('email.template').send_mail(cr, uid, template_id, event.id)
#                except Exception:
#                    pass
#        res = super(project_task, self).write(cr, uid, ids, vals, context=context)
#        return res

    @api.multi
    def project_task_reevaluate(self):
        '''Overriden for marking Task lines un edited '''
        if self.env.user.has_group('project.group_time_work_estimation_tasks'):
            return {
                'view_type': 'form',
                "view_mode": 'form',
                'res_model': 'project.task.reevaluate',
                'type': 'ir.actions.act_window',
                'target': 'new',
            }
        for line in self.work_ids:
            line.write({'edited': False})
        return self.do_reopen()

    @api.multi
    def copy(self, default=None):
        ''' Function ovver ridden to blank data for different type of duplication '''
        if default is None: default = {}
        default.update({
            'interpreter_id': False,
            'translator_id': False,
            'transporter_id': False,
            'supp_invoice_ids': [],
            'supp_invoice_ids2': [],
            'user_id_int': False,
            'all_edited': False,
            'state': 'draft',
            'cust_invoice_id': False,
            'event_type': False,
            'event_id': False,
        })
        return super(project_task, self).copy(default)

    @api.multi
    def unlink(self):
        if self.env.uid != SUPERUSER_ID:
            raise UserError(_('You cannot delete Timesheet.'))
        return super(project_task, self).unlink()

    @api.multi
    def do_reopen(self):
        for task in self:
            task.write({'state':'draft'})
            task.event_id.task_state='draft'
        return True

    def stage_find(self, section_id, domain=[], order='sequence'):
        """ Override of the base.stage method
            Parameter of the stage search taken from the lead:
            - section_id: if set, stages must belong to this section or
              be a default stage; if not set, stages must be default stages """

        cases = self
        # collect all section_ids
        section_ids = []
        if section_id:
            section_ids.append(section_id)
        for task in cases:
            if task.project_id:
                section_ids.append(task.project_id.id)
        search_domain = []
        if section_ids:
            search_domain = [('|')] * (len(section_ids)-1)
            for section_id in section_ids:
                search_domain.append(('project_ids', '=', section_id))
        search_domain += list(domain)
        # perform search, return the first found
        stage_ids = self.env['project.task.type'].search(search_domain, order=order)
        if stage_ids:
            return stage_ids[0]
        else:
            stage_ids = self.env['project.task.type'].search([('state','=','draft')], order=order)
            if stage_ids:
                return stage_ids[0]
        return False
    #
    # def float_time_convert(self,float_val):
    #     factor = float_val < 0 and -1 or 1
    #     val = abs(float_val)
    #     str_time = str(val % 1).split('.')[1]
    #     #print "str_time.......",str_time
    #     return (factor * int(math.floor(val)), int(str_time))

    @api.model
    def _prepare_inv_line_interpreter(self,account_id, task_line, event, product):
        """Collects require data from task line that is used to create invoice line for that task line """
#        print 'PREPARE line for Supplier Invoice (Interpreter)...............'
        price_unit, milage_to_pay = 0.0, 0.0
        hr, hrs, min, new_hours, new_min, tr_new_hours, tr_new_min  = 0.0 ,0.0 ,0.0 ,0.0 ,0.0,0.0 ,0.0
        new_time, rate, inc_min, base_hour, tr_rate, tr_rate_unit,tr_new_time,tr_inc_min,tr_base_hour = 0.0 ,False , False, False, False, 0.0, 0.0, 0.0, 0.0
        category, total_editable = '', 0.0
        night_price_unit, night_base_hour, night_inc_min= 0.0, False, False
        if event.event_type=='language' or event.event_type=='lang_trans':
            customer = event.partner_id
            interpreter = task_line.interpreter_id or False
            category = event.language_id and event.language_id.lang_group or False
            day, night, weekend = False, False, False
            day_hr, night_hr = False, False
            night_rate = False
            n_min_price, min_price = 0.0, 0.0
            up_categ_rate, night_categ_rate = False, False
            DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            event_start = event.event_start
            event_end = event.event_end
            from_dt = datetime.datetime.strptime(str(event_start), DATETIME_FORMAT)
            to_dt = datetime.datetime.strptime(str(event_end), DATETIME_FORMAT)
            diff = to_dt - from_dt
            hr = str(diff).split(':')[0]
            min = str(diff).split(':')[1]
            cu_min = 00
            if int(min) > 00 and int(min) <= 15:
                cu_min = 0.25
            elif int(min) > 15 and int(min) <= 30:
                cu_min = 0.50
            elif int(min) > 30 and int(min) <= 45:
                cu_min = 0.75
            spend_min = int(int(hr) * 60 + int(min))
            if not interpreter.w_start_time == '00' and not interpreter.w_end_time == '00' and not interpreter.even_start_time == '00' and not interpreter.even_end_time == '00':
                if interpreter.w_am_pm1 == 'am':
                    week_time_s = datetime.time(int(interpreter.w_start_time), 0, 0)
                if interpreter.w_am_pm1 == 'pm':
                    add_time = 12 + int(interpreter.w_start_time)
                    if interpreter.w_start_time == '12':
                        add_time = int(interpreter.w_start_time)
                    week_time_s = datetime.time(int(add_time), 0, 0)
                if interpreter.w_am_pm2 == 'am':
                    week_time_e = datetime.time(int(interpreter.w_end_time), 0, 0)
                if interpreter.w_am_pm2 == 'pm':
                    add_time_e = 12 + int(interpreter.w_end_time)
                    if interpreter.w_end_time == '12':
                        add_time_e = int(interpreter.w_end_time)
                    week_time_e = datetime.time(int(add_time_e), 0, 0)
                if event.am_pm == 'am':
                    event_time_s = datetime.time(int(event.event_start_hr), int(event.event_start_min), 0)
                if event.am_pm == 'pm':
                    event_add_time_s = 12 + int(event.event_start_hr)
                    if event.event_start_hr == '12':
                        event_add_time_s = int(event.event_start_hr)
                    event_time_s = datetime.time(int(event_add_time_s), int(event.event_start_min), 0)
                if event.am_pm2 == 'am':
                    event_time_e = datetime.time(int(event.event_end_hr), int(event.event_end_min), 0)
                if event.am_pm2 == 'pm':
                    event_add_time_e = 12 + int(event.event_end_hr)
                    if event.event_end_hr == '12':
                        event_add_time_e = int(event.event_end_hr)
                    event_time_e = datetime.time(int(event_add_time_e), int(event.event_end_min), 0)
                if interpreter.even_am_pm1 == 'am':
                    nigh_time_s = datetime.time(int(interpreter.even_start_time), 0, 0)
                if interpreter.even_am_pm1 == 'pm':
                    e_add_time = 12 + int(interpreter.even_start_time)
                    if interpreter.even_start_time == '12':
                        e_add_time = int(interpreter.even_start_time)
                    nigh_time_s = datetime.time(int(e_add_time), 0, 0)
                if interpreter.even_am_pm2 == 'am':
                    nigh_time_e = datetime.time(int(interpreter.even_end_time), 0, 0)
                if interpreter.even_am_pm2 == 'pm':
                    e_add_time_e = 12 + int(interpreter.even_end_time)
                    if interpreter.even_end_time == '12':
                        e_add_time_e = int(interpreter.even_end_time)
                    nigh_time_e = datetime.time(int(e_add_time_e), 0, 0)
                if event.weekday == 'Saturday':
                    weekend = 'weekend'
                elif (week_time_s <= event_time_s and week_time_e > event_time_s) and (
                        week_time_s < event_time_e and week_time_e >= event_time_e):
                    day = 'weekday'
                elif (week_time_s <= event_time_s and week_time_e > event_time_s) and (
                        week_time_s < event_time_e and week_time_e < event_time_e):
                    day = 'weekday'
                    night = 'even_night'
                    a = datetime.timedelta(hours=week_time_e.hour, minutes=week_time_e.minute,
                                           seconds=week_time_e.second)
                    b = datetime.timedelta(hours=event_time_e.hour, minutes=event_time_e.minute,
                                           seconds=event_time_e.second)
                    c = b - a
                    night_hr = int(c.total_seconds() / 60)
                    day_hr = int(spend_min - night_hr)

                elif (nigh_time_s <= event_time_s and nigh_time_e < event_time_s) and (
                        nigh_time_s < event_time_e and nigh_time_e <= event_time_e):
                    night = 'even_night'
                else:
                    day = 'weekday'
            else:
                if event.weekday == 'Saturday':
                    weekend = 'weekend'
                else:
                    day = 'weekday'
            if event.event_purpose:
                if event.am_pm == 'am':
                    event_cust_time = datetime.datetime.combine(
                        datetime.datetime.strptime(event.event_start_date, '%Y-%m-%d'),
                        datetime.time(int(event.event_start_hr), int(event.event_start_min), 0))
                if event.am_pm == 'pm':
                    event_s = 12 + int(event.event_start_hr)
                    if event.event_start_hr == '12':
                        event_s = int(event.event_start_hr)
                    event_cust_time = datetime.datetime.combine(
                        datetime.datetime.strptime(event.event_start_date, '%Y-%m-%d'),
                        datetime.time(int(event_s),
                                      int(event.event_start_min), 0))
                offer_date = datetime.datetime.strptime(str(event.job_offer_date), '%Y-%m-%d %H:%M:%S')
                diff = event_cust_time - offer_date
                hr_diff = str(diff).split(':')[0]
                rush_rate=False
                if diff <= datetime.timedelta(hours=24):
                    for rate_id in interpreter.rate_ids:
                        if rate_id.rate_type == event.event_purpose and rate_id.day_type == 'weekday':
                            rate = rate_id
                            rush_rate=rate_id.rush_rate
                else:
                    for rate_id in interpreter.rate_ids:
                        if day:
                            if rate_id.rate_type == event.event_purpose and rate_id.day_type == day:
                                rate = rate_id
                        if night:
                            if rate_id.rate_type == event.event_purpose and rate_id.day_type == night:
                                night_rate = rate_id
                            elif rate_id.rate_type == event.event_purpose and rate_id.day_type == 'weekday':
                                rate = rate_id
                            if night_rate and not rate:
                                rate=night_rate
                                night_rate=False
                        if weekend:
                            if rate_id.rate_type == event.event_purpose and rate_id.day_type == weekend:
                                rate = rate_id
                            elif rate_id.rate_type == event.event_purpose and rate_id.day_type == 'weekday':
                                rate = rate_id
                        if rate_id.rate_type == 'travel':
                            tr_rate = rate_id
                    if night_rate and not rate:
                        rate = night_rate
                        night_rate = False
                    if not night_rate and not rate:
                        for rate_id in customer.rate_ids:
                            if rate_id.rate_type == event.event_purpose and rate_id.day_type == 'weekday':
                                 rate = rate_id
                if category and rate and not rush_rate:
                    if category == 'spanish_regular':
                        price_unit = rate.spanish_regular
                        base_hour = rate.base_hour
                        inc_min  = rate.inc_min
                    elif category == 'spanish_licenced':
                        price_unit = rate.spanish_licenced
                        base_hour = rate.base_hour
                        inc_min  = rate.inc_min
                    elif category == 'spanish_certified':
                        price_unit = rate.spanish_certified
                        base_hour = rate.base_hour
                        inc_min  = rate.inc_min
                    elif category == 'exotic_regular':
                        price_unit = rate.exotic_regular
                        base_hour = rate.base_hour
                        inc_min  = rate.inc_min
                    elif category == 'exotic_certified':
                        price_unit = rate.exotic_certified
                        base_hour = rate.base_hour
                        inc_min  = rate.inc_min
                    elif category == 'exotic_middle':
                        price_unit = rate.exotic_middle
                        base_hour = rate.base_hour
                        inc_min  = rate.inc_min
                    elif category == 'exotic_high':
                        price_unit = rate.exotic_high
                        base_hour = rate.base_hour
                        inc_min  = rate.inc_min
                if rate and not rush_rate and price_unit == 0.0:
                    price_unit = rate.default_rate
                    base_hour = rate.base_hour
                    inc_min  = rate.inc_min
                if category and night_rate and not rush_rate:
                    if category == 'spanish_regular':
                        night_price_unit = night_rate.spanish_regular
                        night_base_hour = night_rate.base_hour
                        night_inc_min  = night_rate.inc_min
                    elif category == 'spanish_licenced':
                        night_price_unit = night_rate.spanish_licenced
                        night_base_hour = night_rate.base_hour
                        night_inc_min = night_rate.inc_min
                    elif category == 'spanish_certified':
                        night_price_unit = night_rate.spanish_certified
                        night_base_hour = night_rate.base_hour
                        night_inc_min = night_rate.inc_min
                    elif category == 'exotic_regular':
                        night_price_unit = night_rate.exotic_regular
                        night_base_hour = night_rate.base_hour
                        night_inc_min = night_rate.inc_min
                    elif category == 'exotic_certified':
                        night_price_unit = night_rate.exotic_certified
                        night_base_hour = night_rate.base_hour
                        night_inc_min = night_rate.inc_min
                    elif category == 'exotic_middle':
                        night_price_unit = night_rate.exotic_middle
                        night_base_hour = night_rate.base_hour
                        night_inc_min = night_rate.inc_min
                    elif category == 'exotic_high':
                        night_price_unit = night_rate.exotic_high
                        night_base_hour = night_rate.base_hour
                        night_inc_min = night_rate.inc_min
                if night_rate and not rush_rate and night_price_unit == 0.0:
                    night_price_unit = night_rate.default_rate
                    night_base_hour = night_rate.base_hour
                    night_inc_min = night_rate.inc_min
                if category and rate and rush_rate:
                    price_unit = rate.rush_rate
                    base_hour = rate.base_hour
                    inc_min = rate.inc_min

                # if rate and night_rate:
                #     if base_hour == '2hour':
                #         per_min_price=price_unit/120
                #         ra_price_unit=night_hr
                #     if base_hour == '3hour':
                #         per_min_price = price_unit / 180
                #     if night_base_hour == '2hour':
                #         n_per_min_price = price_unit / 120
                #     if night_base_hour == '3hour':
                #         n_per_min_price = price_unit / 180
                if price_unit and not night_price_unit:
                    if base_hour == '2hour':
                        price_unit /= 2
                    elif base_hour == '3hour':
                        price_unit /= 3
                if night_price_unit and not price_unit:
                    if night_base_hour == '2hour':
                        night_price_unit /= 2
                    elif night_base_hour == '3hour':
                        night_price_unit /= 3
                    price_unit=night_price_unit
                    base_hour=night_base_hour
                    inc_min=night_inc_min
                    night_price_unit=False
                if price_unit and night_price_unit:
                    # if base_hour == '2hour':
                    #     price_unit /= 2
                    # if base_hour == '3hour':
                    #     price_unit /= 3
                    # if night_base_hour == '2hour':
                    #     night_price_unit /= 2
                    # if night_base_hour == '3hour':
                    #     night_price_unit /= 3
                    # price_unit = (price_unit + night_price_unit)/2
                    if base_hour and day_hr:
                        if base_hour == '1min':
                            min = 1
                            min_price = price_unit
                        if base_hour == '1hour':
                            min = 60
                            min_price = (price_unit / min) * day_hr
                        elif base_hour == '2hour':
                            min = 2 * 60

                            min_price = (price_unit / min) * day_hr
                        elif base_hour == '3hour':
                            min = 2 * 60
                            min_price = (price_unit / min) * day_hr
                    if night_base_hour and night_hr:
                        if night_base_hour == '1min':
                            n_min_price = night_price_unit
                        elif night_base_hour == '1hour':
                            n_min = 60
                            n_min_price = (night_price_unit / n_min) * night_hr
                        elif night_base_hour == '2hour':
                            n_min = 2 * 60

                            n_min_price = (night_price_unit / n_min) * night_hr
                        elif night_base_hour == '3hour':
                            n_min = 2 * 60
                            n_min_price = (night_price_unit / n_min) * night_hr
                    price_unit = (min_price + n_min_price) / (int(hr)+cu_min)

                #            if event.event_purpose and event.event_purpose == 'conf_call':
    #                inc_min = False
                new_hours = int(task_line.hours)
                minus_hrs = (task_line.hours - int(task_line.hours))
                r_minus_hrs = round(minus_hrs, 2)
                p_minus_hrs = r_minus_hrs * 100
                new_min = round(p_minus_hrs, 2)
                #new_min = int(round(task_line.hours - int(task_line.hours),2)*100)
                print "new_min.....new_hours...",new_min,type(new_min),new_hours
            if category and tr_rate:
                if category == 'spanish_regular':
                    tr_rate_unit = tr_rate.spanish_regular
                elif category == 'spanish_licenced':
                    tr_rate_unit = tr_rate.spanish_licenced

                elif category == 'spanish_certified':
                    tr_rate_unit = tr_rate.spanish_certified

                elif category == 'exotic_regular':
                    tr_rate_unit = tr_rate.exotic_regular

                elif category == 'exotic_certified':
                    tr_rate_unit = tr_rate.exotic_certified

                elif category == 'exotic_middle':
                    tr_rate_unit = tr_rate.exotic_middle

                elif category == 'exotic_high':
                    tr_rate_unit = tr_rate.exotic_high

            if tr_rate and tr_rate_unit == 0.0:
                tr_rate_unit = tr_rate.default_rate
            if tr_rate:
                tr_base_hour = tr_rate.base_hour
                tr_inc_min  = tr_rate.inc_min
            if tr_base_hour == '2hour':
                tr_rate_unit /= 2
            elif tr_base_hour == '3hour':
                tr_rate_unit /= 3
            tr_new_hours = int(task_line.travel_time)
            tr_new_min = int(round(task_line.travel_time - int(task_line.travel_time),2)*60)
            print "nw hrs mins++++++++++++111111",new_hours,new_min
#                    if not line.invoice_id.partner_id.special_customer and  rate.rate_type == 'conf_call' and base_hour == '1min':
#                        new_time = new_hours + (new_min/60.0)
#                        print "in conf call ++custonmer++++++++++", new_time
            if not customer.special_customer:
#                        if base_hour == '1min':
#                            raise osv.except_osv(_('Warning!'),_('Please Select Proper Travelling Base Hour for Partner.'))
                if tr_base_hour == '1hour':
                    if tr_new_hours < 1:
                        tr_new_hours = 1
                        tr_new_min = 0
                elif tr_base_hour == '2hour':
                    if tr_new_hours < 2:
                        tr_new_hours = 2
                        tr_new_min = 0
                elif tr_base_hour == '3hour':
                    if tr_new_hours < 3:
                        tr_new_hours = 3
                        tr_new_min = 0
#                        if inc_min == '1min':
#                            raise osv.except_osv(_('Warning!'),_('Please Select Proper Travelling Increment Minutes for Partner.'))
                if tr_inc_min == '15min':
                    if tr_new_min > 00 and tr_new_min <= 15:
                        tr_new_min = 25
                    elif tr_new_min > 15 and tr_new_min <= 30:
                        tr_new_min = 50
                    elif tr_new_min > 30 and tr_new_min <= 45:
                        tr_new_min = 75
                    elif tr_new_min > 45 and tr_new_min <= 60:
                        tr_new_min = 0
                        tr_new_hours += 1
                    else:
                        tr_new_min = 0
                else:
                    if tr_new_min > 00 and tr_new_min <= 30:
                        tr_new_min = 50
                    elif tr_new_min > 30 :
                        tr_new_min = 0
                        tr_new_hours += 1
                tr_new_time = str(tr_new_hours).strip() + '.' + str(tr_new_min).strip()
            else:
#                        if inc_min == '1min':
#                            raise osv.except_osv(_('Warning!'),_('Please Select Proper Increment Minutes.'))
                tr_inc_min = '30min'
                if tr_new_min > 00:
                    tr_new_hours += 1
                tr_new_time = str(tr_new_hours).strip()
    # ------ CALCULATION  FOR BASE HOUR AND MINUTES OF INTERPRETER ----------
            if not customer.special_customer and not night_rate and rate and rate.rate_type in ('conf_call','medical','other') and base_hour == '1min':
                new_time = new_hours * 60 + new_min
                print "in conf call interrpeter+++++++++++++++",new_time
            elif not customer.special_customer:
#                if base_hour == '1min':
#                    raise osv.except_osv(_('Warning!'),_('Please Select Proper Base Hour for Customer.'))
                if base_hour == '1hour':
                    if new_hours < 1:
                        new_hours = 1
                        new_min = 0
                elif base_hour == '2hour':
                    if new_hours < 2:
                        new_hours = 2
                        new_min = 0
                elif base_hour == '3hour':
                    if new_hours < 3:
                        new_hours = 3
                        new_min = 0
                if inc_min == '15min':
                    if new_min > 00 and new_min <= 15:
                        new_min = 25
                    elif new_min > 15 and new_min <= 30:
                        new_min = 50
                    elif new_min > 30 and new_min <= 45:
                        new_min = 75
                    elif new_min > 45 and new_min <= 60:
                        print "new_min..in.....",new_min
                        new_min = 0
                        new_hours += 1
                    else:
                        new_min = 0
                else:
                    if new_min > 00 and new_min <= 30:
                        new_min = 50
                    elif new_min > 30:
                        new_min = 0
                        new_hours += 1
#                else:
#                    new_min = new_min / 60 # converting minute into 100 decimal
                new_time = str(new_hours).strip() + '.' + str(new_min).strip()
            else:
                inc_min = '30min'
                if new_min > 00:
                    new_hours += 1
                new_time = str(new_hours).strip()
# ++++++++Condition for Event oUtcome based billing +++++++++
            if task_line.event_out_come_id:
                if 'no show' in task_line.event_out_come_id.name.lower() or \
                    'late xl' in task_line.event_out_come_id.name.lower():
                    if rate and rate.base_hour == '1hour':
                        new_time = 1
                    elif rate and rate.base_hour == '2hour':
                        new_time = 2
                    elif rate and rate.base_hour == '3hour':
                        new_time = 3
#                    price_unit = rate.default_rate
#                    total_editable = original_price_unit
                elif 'no pay, no bill' in task_line.event_out_come_id.name.lower():
                    new_time, price_unit = 0.0, 0.0
            if task_line.total_mileage_covered > 0:
                if task_line.total_mileage_covered >= interpreter.bill_miles_after:
                    milage_to_pay=task_line.total_mileage_covered - interpreter.bill_miles_after
        return {
            'name': task_line.name or 'Task',
            'account_id': account_id,
            'price_unit': price_unit or 0.0,
            'quantity': new_time or 0.0,
#            'discount': event.special_discount or 0.0 ,
            'product_id': product and product.id or False,
            'uom_id': product and product.uom_id and product.uom_id.id or False,
            'invoice_line_tax_ids': False,
            'company_id': event.company_id and event.company_id.id or False,
            'miles_driven': milage_to_pay or 0.0,
            'mileage' : milage_to_pay or 0.0,
            'mileage_rate': task_line.interpreter_id.rate or 0.0,
            'inc_min': inc_min,
            'event_out_come_id': task_line.event_out_come_id and task_line.event_out_come_id.id or False,
            'task_line_id': task_line.id,
            'total_editable': total_editable or 0.0,
            'travelling_rate': tr_rate_unit or 0.0,
            'travel_time': tr_new_time or 0.0,
        }

    @api.model
    def _prepare_inv_line_interpreter_for_customer(self,account_id, task_line, event , product):
        print 'PREPARE line for customer Invoice in case of Interpreter(Language Events)...............'
        """Collects require data from task line that is used to create invoice line for that task line """
        price_unit, milage_to_pay, rate = 0.0, 0.0, False
        new_hours, new_min, mileage, tr_new_hours, tr_new_min = 0.0 ,0.0, 0.0, 0.0, 0.0
        new_time, name, original_price_unit, tr_rate, tr_rate_unit, tr_new_time = 0.00, 'Task', 0.0, False, 0.0, 0.0
        category, inc_min, base_hour, total_editable, tr_inc_min, tr_base_hour = '', '30min', False, 0.0, 0.0, 0.0
        night_price_unit, night_base_hour, night_inc_min = 0.0, False, False
        if event.event_type =='language' or event.event_type=='lang_trans':
            interpreter = self._context.get('interpreter',False)
            customer = event.partner_id
            category = event.language_id and event.language_id.lang_group or False
            day, night, weekend = False, False, False
            day_hr, night_hr = False, False
            night_rate = False
            n_min_price, min_price = 0.0, 0.0
            up_categ_rate, night_categ_rate = False, False
            DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            event_start = event.event_start
            event_end = event.event_end
            from_dt = datetime.datetime.strptime(str(event_start), DATETIME_FORMAT)
            to_dt = datetime.datetime.strptime(str(event_end), DATETIME_FORMAT)
            diff = to_dt - from_dt
            hr = str(diff).split(':')[0]
            min = str(diff).split(':')[1]
            cu_min=00
            if int(min) > 00 and int(min) <= 15:
                cu_min = 0.25
            elif int(min) > 15 and int(min) <= 30:
                cu_min = 0.50
            elif int(min) > 30 and int(min) <= 45:
                cu_min = 0.75
            spend_min = int(int(hr) * 60 + int(min))
            if not customer.w_start_time == '00' and not customer.w_end_time == '00' and not customer.even_start_time == '00' and not customer.even_end_time == '00':
                if customer.w_am_pm1 == 'am':
                    week_time_s = datetime.time(int(customer.w_start_time), 0, 0)
                if customer.w_am_pm1 == 'pm':
                    add_time = 12 + int(customer.w_start_time)
                    if customer.w_start_time == '12':
                        add_time = int(customer.w_start_time)
                    week_time_s = datetime.time(int(add_time), 0, 0)
                if customer.w_am_pm2 == 'am':
                    week_time_e = datetime.time(int(customer.w_end_time), 0, 0)
                if customer.w_am_pm2 == 'pm':
                    add_time_e = 12 + int(customer.w_end_time)
                    if customer.w_end_time == '12':
                        add_time_e = int(customer.w_end_time)
                    week_time_e = datetime.time(int(add_time_e), 0, 0)
                if event.am_pm == 'am':
                    event_time_s = datetime.time(int(event.event_start_hr), int(event.event_start_min), 0)
                if event.am_pm == 'pm':
                    event_add_time_s = 12 + int(event.event_start_hr)
                    if event.event_start_hr == '12':
                        event_add_time_s = int(event.event_start_hr)
                    event_time_s = datetime.time(int(event_add_time_s), int(event.event_start_min), 0)
                if event.am_pm2 == 'am':
                    event_time_e = datetime.time(int(event.event_end_hr), int(event.event_end_min), 0)
                if event.am_pm2 == 'pm':
                    event_add_time_e = 12 + int(event.event_end_hr)
                    if event.event_end_hr == '12':
                        event_add_time_e = int(event.event_end_hr)
                    event_time_e = datetime.time(int(event_add_time_e), int(event.event_end_min), 0)
                if customer.even_am_pm1 == 'am':
                    nigh_time_s = datetime.time(int(customer.even_start_time), 0, 0)
                if customer.even_am_pm1 == 'pm':
                    e_add_time = 12 + int(customer.even_start_time)
                    if customer.even_start_time == '12':
                        e_add_time = int(customer.even_start_time)
                    nigh_time_s = datetime.time(int(e_add_time), 0, 0)
                if customer.even_am_pm2 == 'am':
                    nigh_time_e = datetime.time(int(customer.even_end_time), 0, 0)
                if customer.even_am_pm2 == 'pm':
                    e_add_time_e = 12 + int(customer.even_end_time)
                    if customer.even_end_time == '12':
                        e_add_time_e = int(customer.even_end_time)
                    nigh_time_e = datetime.time(int(e_add_time_e), 0, 0)
                if event.weekday == 'Saturday':
                    weekend = 'weekend'
                elif (week_time_s <= event_time_s and week_time_e > event_time_s) and (
                        week_time_s < event_time_e and week_time_e >= event_time_e):
                    day = 'weekday'
                elif (week_time_s <= event_time_s and week_time_e > event_time_s) and (
                        week_time_s < event_time_e and week_time_e < event_time_e):
                    day = 'weekday'
                    night = 'even_night'
                    a = datetime.timedelta(hours=week_time_e.hour, minutes=week_time_e.minute,
                                           seconds=week_time_e.second)
                    b = datetime.timedelta(hours=event_time_e.hour, minutes=event_time_e.minute,
                                           seconds=event_time_e.second)
                    c = b - a
                    night_hr = int(c.total_seconds() / 60)
                    day_hr = int(spend_min - night_hr)

                elif (nigh_time_s <= event_time_s and nigh_time_e < event_time_s) and (
                        nigh_time_s < event_time_e and nigh_time_e <= event_time_e):
                    night = 'even_night'
                else:
                    day = 'weekday'
            else:
                if event.weekday == 'Saturday':
                    weekend = 'weekend'
                else:
                    day = 'weekday'
            if event.event_purpose:
                if event.am_pm == 'am':
                    event_cust_time = datetime.datetime.combine(
                        datetime.datetime.strptime(event.event_start_date, '%Y-%m-%d'),
                        datetime.time(int(event.event_start_hr), int(event.event_start_min), 0))

                if event.am_pm == 'pm':
                    event_s = 12 + int(event.event_start_hr)
                    if event.event_start_hr == '12':
                        event_s = int(event.event_start_hr)
                    event_cust_time = datetime.datetime.combine(
                        datetime.datetime.strptime(event.event_start_date, '%Y-%m-%d'),
                        datetime.time(int(event_s),
                                      int(event.event_start_min), 0))
                offer_date = datetime.datetime.strptime(str(event.job_offer_date), '%Y-%m-%d %H:%M:%S')
                diff = event_cust_time - offer_date
                hr_diff = str(diff).split(':')[0]
                rush_rate=False
                if diff <= datetime.timedelta(hours=24):
                    for rate_id in interpreter.rate_ids:
                        if rate_id.rate_type == event.event_purpose and rate_id.day_type == 'weekday':
                            rate = rate_id
                            rush_rate=rate_id.rush_rate
                else:
                    for rate_id in customer.rate_ids:
                        if day:
                            if rate_id.rate_type == event.event_purpose and rate_id.day_type == day:
                                rate = rate_id
                        if night:
                            if rate_id.rate_type == event.event_purpose and rate_id.day_type == night:
                                night_rate = rate_id
                            # elif rate_id.rate_type == event.event_purpose and rate_id.day_type == 'weekday':
                            #     rate = rate_id
                            # if night_rate and not rate:
                            #     rate = night_rate
                            #     night_rate = False
                        if weekend:
                            if rate_id.rate_type == event.event_purpose and rate_id.day_type == weekend:
                                rate = rate_id
                            elif rate_id.rate_type == event.event_purpose and rate_id.day_type == 'weekday':
                                rate = rate_id
                        if rate_id.rate_type == 'travel':
                            tr_rate = rate_id
                    if night_rate and not rate:
                        rate = night_rate
                        night_rate = False
                    if not night_rate and not rate:
                        for rate_id in customer.rate_ids:
                            if rate_id.rate_type == event.event_purpose and rate_id.day_type == 'weekday':
                                 rate = rate_id

                    # if rate_id.rate_type == event.event_purpose and rate_id.day_type==day:
                    #     rate = rate_id
                    # if rate_id.rate_type == 'travel':
                    #     tr_rate = rate_id
                # if not rate:
                #     raise UserError(_(' There is no Rate type mention for %s.') % (day))

                if category and rate and not rush_rate:
                    if category == 'spanish_regular':
                        price_unit = rate.spanish_regular
                        base_hour = rate.base_hour
                        inc_min  = rate.inc_min
                    elif category == 'spanish_licenced':
                        price_unit = rate.spanish_licenced
                        base_hour = rate.base_hour
                        inc_min  = rate.inc_min
                    elif category == 'spanish_certified':
                        price_unit = rate.spanish_certified
                        base_hour = rate.base_hour
                        inc_min  = rate.inc_min
                    elif category == 'exotic_regular':
                        price_unit = rate.exotic_regular
                        base_hour = rate.base_hour
                        inc_min  = rate.inc_min
                    elif category == 'exotic_certified':
                        price_unit = rate.exotic_certified
                        base_hour = rate.base_hour
                        inc_min  = rate.inc_min
                    elif category == 'exotic_middle':
                        price_unit = rate.exotic_middle
                        base_hour = rate.base_hour
                        inc_min  = rate.inc_min
                    elif category == 'exotic_high':
                        price_unit = rate.exotic_high
                        base_hour = rate.base_hour
                        inc_min  = rate.inc_min
                if rate and not rush_rate and price_unit == 0.0:
                    price_unit = rate.default_rate
                    base_hour = rate.base_hour
                    inc_min  = rate.inc_min
                if category and night_rate and not rush_rate:
                    if category == 'spanish_regular':
                        night_price_unit = night_rate.spanish_regular
                        night_base_hour = night_rate.base_hour
                        night_inc_min  = night_rate.inc_min
                    elif category == 'spanish_licenced':
                        night_price_unit = night_rate.spanish_licenced
                        night_base_hour = night_rate.base_hour
                        night_inc_min = night_rate.inc_min
                    elif category == 'spanish_certified':
                        night_price_unit = night_rate.spanish_certified
                        night_base_hour = night_rate.base_hour
                        night_inc_min = night_rate.inc_min
                    elif category == 'exotic_regular':
                        night_price_unit = night_rate.exotic_regular
                        night_base_hour = night_rate.base_hour
                        night_inc_min = night_rate.inc_min
                    elif category == 'exotic_certified':
                        night_price_unit = night_rate.exotic_certified
                        night_base_hour = night_rate.base_hour
                        night_inc_min = night_rate.inc_min
                    elif category == 'exotic_middle':
                        night_price_unit = night_rate.exotic_middle
                        night_base_hour = night_rate.base_hour
                        night_inc_min = night_rate.inc_min
                    elif category == 'exotic_high':
                        night_price_unit = night_rate.exotic_high
                        night_base_hour = night_rate.base_hour
                        night_inc_min = night_rate.inc_min
                if night_rate and not rush_rate and night_price_unit == 0.0:
                    night_price_unit = night_rate.default_rate
                    night_base_hour = night_rate.base_hour
                    night_inc_min = night_rate.inc_min
                if category and rate and rush_rate:
                    price_unit = rate.rush_rate
                    base_hour = rate.base_hour
                    inc_min = rate.inc_min
                _logger.info(">>>>>>>>>>>>>>>>>>price >>>>>>%s>>>>%s>>>>", price_unit, night_price_unit)
                if price_unit and not night_price_unit:
                    _logger.info("????????condition1??????^%s>>>>>%s>>>", price_unit, night_price_unit)
                    if base_hour == '2hour':
                        price_unit /= 2
                    elif base_hour == '3hour':
                        price_unit /= 3
                if night_price_unit and not price_unit:
                    _logger.info("????????conditio31??????^%s>>>>>%s>>>", price_unit, night_price_unit)
                    if night_base_hour == '2hour':
                        night_price_unit /= 2
                    elif night_base_hour == '3hour':
                        night_price_unit /= 3
                    price_unit=night_price_unit
                    base_hour=night_base_hour
                    inc_min=night_inc_min
                    night_price_unit=False
                if price_unit and night_price_unit:
                    _logger.info("????????condition3??????^%s>>>>>%s>>>", price_unit, night_price_unit)
                    # if base_hour == '2hour':
                    #     price_unit /= 2
                    # if base_hour == '3hour':
                    #     price_unit /= 3
                    # if night_base_hour == '2hour':
                    #     night_price_unit /= 2
                    # if night_base_hour == '3hour':
                    #     night_price_unit /= 3
                    if base_hour and day_hr:
                        if base_hour == '1min':
                            min = 1
                            min_price = price_unit
                        if base_hour == '1hour':
                            min = 60
                            min_price = (price_unit / min) * day_hr
                        elif base_hour == '2hour':
                            min = 2 * 60

                            min_price = (price_unit / min) * day_hr
                        elif base_hour == '3hour':
                            min = 2 * 60
                            min_price = (price_unit / min) * day_hr
                    if night_base_hour and night_hr:
                        if night_base_hour == '1min':
                            n_min_price = night_price_unit
                        elif night_base_hour == '1hour':
                            n_min = 60
                            n_min_price = (night_price_unit / n_min) * night_hr
                        elif night_base_hour == '2hour':
                            n_min = 2 * 60

                            n_min_price = (night_price_unit / n_min) * night_hr
                        elif night_base_hour == '3hour':
                            n_min = 2 * 60
                            n_min_price = (night_price_unit / n_min) * night_hr
                    price_unit = (min_price + n_min_price) / (int(hr)+cu_min)
                    _logger.info(">>>>>>>>>>>>>>>>>>>>>>hours price unit>>>>%s>>>>%s>>>>", min_price, n_min_price)
                    # price_unit = (price_unit + night_price_unit)/2
                _logger.info(">>>>>>>>>>>>>>>>>>>>>final >hours price unit>>>>%s>>>>%s>>>>", price_unit)
#            print "price_unit..base_hour.inc_min.....",price_unit,base_hour,inc_min
#             if base_hour == '2hour':
#                 price_unit /= 2
#             elif base_hour == '3hour':
#                 price_unit /= 3
#             _logger.info("-------This is base hour------->%s " % str(base_hour))
                new_hours = int(task_line.hours)
                minus_hrs= (task_line.hours - int(task_line.hours))
                r_minus_hrs = round(minus_hrs,2)
                p_minus_hrs=r_minus_hrs*100
                new_min=int(round(p_minus_hrs,2))

               # new_min = int(round(task_line.hours - int(task_line.hours),2)*100)
                print "customer new_hours...new_min......",new_hours,new_min
            if category and tr_rate:
                if category == 'spanish_regular':
                    tr_rate_unit = tr_rate.spanish_regular
                elif category == 'spanish_licenced':
                    tr_rate_unit = tr_rate.spanish_licenced

                elif category == 'spanish_certified':
                    tr_rate_unit = tr_rate.spanish_certified

                elif category == 'exotic_regular':
                    tr_rate_unit = tr_rate.exotic_regular

                elif category == 'exotic_certified':
                    tr_rate_unit = tr_rate.exotic_certified

                elif category == 'exotic_middle':
                    tr_rate_unit = tr_rate.exotic_middle

                elif category == 'exotic_high':
                    tr_rate_unit = tr_rate.exotic_high

            if tr_rate and tr_rate_unit == 0.0:
                tr_rate_unit = tr_rate.default_rate
            if tr_rate:
                tr_base_hour = tr_rate.base_hour
                tr_inc_min  = tr_rate.inc_min
            if tr_base_hour == '2hour':
                tr_rate_unit /= 2
            elif tr_base_hour == '3hour':
                tr_rate_unit /= 3
            tr_new_hours = int(task_line.travel_time)
            tr_new_min = int(round(task_line.travel_time - int(task_line.travel_time),2)*60)
            print "nw hrs mins++++++++++++111111",new_hours,new_min
#                    if not line.invoice_id.partner_id.special_customer and  rate.rate_type == 'conf_call' and base_hour == '1min':
#                        new_time = new_hours + (new_min/60.0)
#                        print "in conf call ++custonmer++++++++++", new_time
            if not customer.special_customer:
#                        if base_hour == '1min':
#                            raise osv.except_osv(_('Warning!'),_('Please Select Proper Travelling Base Hour for Partner.'))
                if tr_base_hour == '1hour':
                    if tr_new_hours < 1:
                        tr_new_hours = 1
                        tr_new_min = 0
                elif tr_base_hour == '2hour':
                    if tr_new_hours < 2:
                        tr_new_hours = 2
                        tr_new_min = 0
                elif tr_base_hour == '3hour':
                    if tr_new_hours < 3:
                        tr_new_hours = 3
                        tr_new_min = 0
#                        if inc_min == '1min':
#                            raise osv.except_osv(_('Warning!'),_('Please Select Proper Travelling Increment Minutes for Partner.'))
                if tr_inc_min == '15min':
                    if tr_new_min > 00 and tr_new_min <= 15:
                        tr_new_min = 25
                    elif tr_new_min > 15 and tr_new_min <= 30:
                        tr_new_min = 50
                    elif tr_new_min > 30 and tr_new_min <= 45:
                        tr_new_min = 75
                    elif tr_new_min > 45 and tr_new_min <= 60:
                        tr_new_min = 0
                        tr_new_hours += 1
                    else:
                        tr_new_min = 0
                else:
                    if tr_new_min > 00 and tr_new_min <= 30:
                        tr_new_min = 50
                    elif tr_new_min > 30 :
                        tr_new_min = 0
                        tr_new_hours += 1
                tr_new_time = str(tr_new_hours).strip() + '.' + str(tr_new_min).strip()
            else:
#                        if inc_min == '1min':
#                            raise osv.except_osv(_('Warning!'),_('Please Select Proper Increment Minutes.'))
                tr_inc_min = '30min'
                if tr_new_min > 00:
                    tr_new_hours += 1
                tr_new_time = str(tr_new_hours).strip()

# ------ CALCULATION  FOR BASE HOUR AND MINUTES OF INTERPRETER ----------
            if not customer.special_customer and not night_rate and rate and rate.rate_type in ('conf_call','medical','other') and base_hour == '1min':
                new_time = new_hours * 60 + new_min
                print "in conf call ++custonmer++++++++++", new_time
            elif not customer.special_customer:
#                if base_hour == '1min':
#                    raise osv.except_osv(_('Warning!'),_('Please Select Proper Base Hour for Customer.'))
                if base_hour == '1hour':
                    if new_hours < 1:
                        new_hours = 1
                        new_min = 0
                elif base_hour == '2hour':
                    if new_hours < 2:
                        new_hours = 2
                        new_min = 0
                elif base_hour == '3hour':
                    if new_hours < 3:
                        new_hours = 3
                        new_min = 0
                _logger.info("----------This is new hours------->%s " % str(new_hours))
                if inc_min == '15min':
                    if new_min > 00 and new_min <= 15:
                        new_min = 25
                    elif new_min > 15 and new_min <= 30:
                        new_min = 50
                    elif new_min > 30 and new_min <= 45:
                        new_min = 75
                    elif new_min > 45 and new_min <= 60:
                        new_min = 0
                        new_hours += 1
                    else:
                        new_min = 0
                else:
                    if new_min > 00 and new_min <= 30:
                        new_min = 50
                    elif new_min > 30 :
                        new_min = 0
                        new_hours += 1
                new_time = str(new_hours).strip() + '.' + str(new_min).strip()
            else:
                inc_min = '30min'
                if new_min > 00:
                    new_hours += 1
                new_time = str(new_hours).strip()
#            print "new_time final...customer........",new_time
# ++++++++Condition for Event oUtcome based billing +++++++++
            if task_line.event_out_come_id:
                if 'no show' in task_line.event_out_come_id.name.lower() or \
                'late xl' in task_line.event_out_come_id.name.lower():
                    if rate and rate.base_hour == '1hour':
                        new_time = 1
                    elif rate and rate.base_hour == '2hour':
                        new_time = 2
                    elif rate and rate.base_hour == '3hour':
                        new_time = 3
#                    price_unit = rate.default_rate

#                    new_time, price_unit = rate.base_hour, rate.default_rate
#                    total_editable = original_price_unit
                elif 'no pay, no bill' in task_line.event_out_come_id.name.lower():
                    new_time, price_unit = 0.0, 0.0
                elif 'pay but no bill' in task_line.event_out_come_id.name.lower():
                    new_time, price_unit = 0.0, 0.0
            if task_line.total_mileage_covered > 0:
                if task_line.total_mileage_covered >= customer.bill_miles_after:
                    milage_to_pay = task_line.total_mileage_covered
            if  task_line.interpreter_id:
                if task_line.name:
                    name = task_line.name + task_line.interpreter_id.name or 'Task'
                else:
                    name = task_line.interpreter_id.name or 'Task'
            else:
                name= task_line.name or 'Task'
        return {
            'name': name,
            'account_id': account_id,
            'price_unit': price_unit,
            'quantity': new_time or 0.0,
            'discount': event.special_discount or event.partner_id.discount or 0.0 ,
            'product_id': product and product.id or False,
            'uom_id': product and product.uom_id and product.uom_id.id or False,
            'invoice_line_tax_ids': False,
            'company_id': event.company_id and event.company_id.id or False,
            'miles_driven': milage_to_pay or 0.0,
            'mileage' : milage_to_pay or 0.0,
            'mileage_rate': event.partner_id.rate or 0.0,
            'inc_min': inc_min or '',
            'event_out_come_id': task_line.event_out_come_id and task_line.event_out_come_id.id or False,
            'task_line_id': task_line.id,
            'total_editable': total_editable or 0.0,
            'travelling_rate': tr_rate_unit or 0.0,
            'travel_time': tr_new_time or 0.0,
        }

    @api.model
    def _prepare_inv_line_transporter(self, account_id, task_line, event , product):
        print 'PREPARE line for Supplier Invoice (Transporter)...............'
        """Collects require data from task line that is used to create invoice line for that task line """
        cancel_rate, rate, miles, gratuity_fee = 0.0, 0.0, 0.0, 0.0
        hour, minute, am_pm, hour2, minute2, am_pm2 = 0, 0, 'am', 0, 0, 'am'
        if event.transporter_id:
            rate_obj = self.env['transporter.rate']
            type = event.transportation_type
            rate_ids = rate_obj.search([('transporter_id','=',event.transporter_id.id),('type','=',type)])
            if rate_ids:
                rate_browse = rate_ids[0]
                if task_line.wait_time:
                    wait_time_fee = rate_browse.wait_time * task_line.wait_time
                else:
                    wait_time_fee = 0.0

                iti_lines_len = len(event.itinerary_lines) if event.itinerary_lines else False
                if not event.itinerary_lines:
                    pickup_fee = rate_browse.pickup_fee
                else:
                    pickup_fee = rate_browse.pickup_fee * (iti_lines_len - 1)
                if task_line.total_mileage_covered <= rate_browse.equiv_min_miles:
                    rate = rate_browse.min_round_trip
                    miles = 1.0
                else:
                    rate = rate_browse.rate
                    miles = task_line.total_mileage_covered
                hour = int(task_line.event_start_hr)
                am_pm = task_line.am_pm
                hour2 = int(task_line.event_end_hr)
                am_pm2 = task_line.am_pm2
#                print"data=========",hour2, minute2, am_pm2, am_pm
                if hour < 7 and am_pm=='am':
                    after_hours = rate_browse.after_hours
                if hour2 >= 6 and am_pm2 == 'pm':
                    after_hours = rate_browse.after_hours
#                    print"after_hours===============",after_hours
                else:
                    after_hours=0.0
                cancel_rate=rate_browse.cancel_fee
                if rate_browse.gratuity > 0.0:
                    gratuity_fee = (( miles * rate + after_hours + wait_time_fee + pickup_fee) * rate_browse.gratuity)/ 100
#                    print"gratuity_fee========",gratuity_fee
                else:
                    gratuity_fee = 0.0
            else:
                wait_time_fee = 0.0
                pickup_fee = 0.0
                gratuity_fee = 0.0
                after_hours = 0.0
                rate = 0.0
#        print"main_data==================",wait_time_fee, pickup_fee, gratuity_fee, after_hours
        if event.state=='cancel':
            return {
                'name': task_line.name or 'Task',
                'account_id': account_id or False,
                'price_unit': cancel_rate or 0.0,
                'quantity': 1.0,
    #            'discount': event.special_discount or 0.0 ,
                'product_id': product and product.id or False,
                'uom_id': product and product.uom_id and product.uom_id.id or False,
                'invoice_line_tax_ids': False,
                'company_id': event.company_id and event.company_id.id or False,
                'miles_driven': 0.0,
                'mileage' :  0.0,
                'mileage_rate': 0.0,
                'inc_min': '' ,
                'wait_time': 0.0,
                'pickup_fee': 0.0,
                'gratuity': 0.0,
                'after_hours': 0.0,
                'event_out_come_id': task_line.event_out_come_id and task_line.event_out_come_id.id or False,
                'task_line_id': task_line.id,
                'travel_time': task_line.travel_time,
            }
        else:
            return {
                'name': task_line.name or 'Task',
                'account_id': account_id or False,
                'price_unit': rate or 0.0,
                'quantity': miles or 0.0,
    #            'discount': event.special_discount or 0.0 ,
                'product_id': product and product.id or False,
                'uom_id': product and product.uom_id and product.uom_id.id or False,
                'invoice_line_tax_ids': False,
                'company_id': event.company_id and event.company_id.id or False,
                'miles_driven': task_line.total_mileage_covered or 0.0,
                'mileage' :  0.0,
                'mileage_rate': 0.0,
                'inc_min': '' ,
                'wait_time': wait_time_fee or 0.0,
                'pickup_fee': pickup_fee or 0.0,
                'gratuity': gratuity_fee or 0.0,
                'after_hours': after_hours or 0.0,
                'event_out_come_id': task_line.event_out_come_id and task_line.event_out_come_id.id or False,
                'task_line_id': task_line.id,
                'travel_time': task_line.travel_time,
            }

    @api.model
    def _prepare_inv_line_transporter_for_customer(self,account_id, task_line, event , product):
        print ' Prepare line for Customer Invoice (Transport  Events)...............'
        """Collects require data from task line that is used to create invoice line for that task line """
        cancel_rate, rate, miles, gratuity_fee = 0.0, 0.0, 0.0, 0.0
        hour, minute, am_pm, hour2, minute2, am_pm2 = 0, 0, 'am', 0, 0, 'am'
        if event.transporter_id:
            rate_obj = self.env['transporter.rate']
            type = event.transportation_type
            rate_ids = rate_obj.search([('transporter_id','=',event.transporter_id.id),('type','=',type)])
            if rate_ids:
                rate_browse = rate_ids[0]
                if task_line.wait_time_bill > 0:
                    wait_time_fee = rate_browse.wait_time * task_line.wait_time_bill
#                    print"wait_time========",wait_time_fee,task_line.wait_time_bill
                else:
                    wait_time_fee = 0.0
                iti_lines_len = len(event.itinerary_lines) if event.itinerary_lines else False
                if not event.itinerary_lines:
                    pickup_fee = rate_browse.pickup_fee
                else:
                    pickup_fee = rate_browse.pickup_fee*(iti_lines_len - 1)
                if task_line.total_mileage_covered <= rate_browse.equiv_min_miles:
                    rate = rate_browse.min_round_trip
                    miles = 1.0
                else:
                    rate = rate_browse.rate
                    miles = task_line.total_mileage_covered
                hour = int(task_line.event_start_hr)
                minute = int(task_line.event_start_min)
                am_pm = task_line.am_pm
                hour2 = int(task_line.event_end_hr)
                minute2 = int(task_line.event_end_min)
                am_pm2 = task_line.am_pm2
#                print"data=========",hour2, minute2, am_pm2, am_pm
                if hour < 7 and am_pm=='am':
                    after_hours = rate_browse.after_hours
                if hour2 >= 6 and am_pm2 == 'pm':
                    after_hours = rate_browse.after_hours
#                    print"after_hours===============",after_hours
                else:
                    after_hours=0.0
                cancel_rate=rate_browse.cancel_fee
                if rate_browse.gratuity > 0.0:
                    gratuity_fee = (( miles * rate + after_hours + wait_time_fee + pickup_fee) * rate_browse.gratuity)/ 100
#                    print"gratuity_fee========",gratuity_fee
                else:
                    gratuity_fee = 0.0
            else:
                wait_time_fee = 0.0
                pickup_fee = 0.0
                gratuity_fee = 0.0
                after_hours = 0.0
                rate = 0.0
#        print"main_data==================",wait_time_fee, pickup_fee, gratuity_fee, after_hours
        if event.state=='cancel':
            return {
                'name': task_line.name or 'Task',
                'account_id': account_id or False,
                'price_unit': cancel_rate or 0.0,
                'quantity': 1.0,
                'discount': event.special_discount or event.partner_id.discount or 0.0 ,
                'product_id': product and product.id or False,
                'uom_id': product and product.uom_id and product.uom_id.id or False,
                'invoice_line_tax_ids': False,
                'company_id': event.company_id and event.company_id.id or False,
                'miles_driven': 0.0,
                'mileage' :  0.0,
                'mileage_rate': 0.0,
                'inc_min': '' ,
                'wait_time': 0.0,
                'pickup_fee': 0.0,
                'gratuity': 0.0,
                'after_hours': 0.0,
                'event_out_come_id': task_line.event_out_come_id and task_line.event_out_come_id.id or False,
                'task_line_id': task_line.id,
                'travel_time': task_line.travel_time,
            }
        else:
            return {
                'name': task_line.name or 'Task',
                'account_id': account_id or False,
                'price_unit': rate or 0.0,
                'quantity': miles or 0.0,
                'discount': event.special_discount or event.partner_id.discount or 0.0 ,
                'product_id': product and product.id or False,
                'uom_id': product and product.uom_id and product.uom_id.id or False,
                'invoice_line_tax_ids': False,
                'company_id': event.company_id and event.company_id.id or False,
                'miles_driven': task_line.total_mileage_covered or 0.0,
                'mileage' :  0.0,
                'mileage_rate': 0.0,
                'inc_min': '' ,
                'wait_time': wait_time_fee or 0.0,
                'pickup_fee': pickup_fee or 0.0,
                'gratuity': gratuity_fee or 0.0,
                'after_hours': after_hours or 0.0,
                'event_out_come_id': task_line.event_out_come_id and task_line.event_out_come_id.id or False,
                'task_line_id': task_line.id,
                'travel_time': task_line.travel_time,
            }
#        return {
#            'name': task_line.name or 'Task',
#            'account_id': account_id,
#            'price_unit': event.partner_id and event.partner_id.rate or 0.0,
#            'quantity': task_line.total_mileage_covered or 0.0,
#            'discount': event.special_discount or 0.0 ,
#            'product_id': product and product.id or False,
#            'uos_id': product and product.uom_id and product.uom_id.id or False,
#            'invoice_line_tax_id': False,
#            'company_id': event.company_id and event.company_id.id or False,
#            'miles_driven': task_line.total_mileage_covered or 0.0,
#            'mileage' :  0.0,
#            'mileage_rate': 0.0,
#            'inc_min': '',
#        }

    @api.model
    def action_invoice_create_customer(self):
        """ Generates Customer Invoice for given ids of Task """
        res = True
        invoice_for='other'
        journal_obj = self.env['account.journal']
        inv_obj = self.env['account.invoice']
        inv_line_obj = self.env['account.invoice.line']
        for task in self:
            partner_brw = task.event_id.partner_id
            if not task.event_id:
                raise UserError(_('No Event is attached to this task.'))
            if not task.work_ids:
                raise UserError(_('Please enter timesheet first.'))
            journal_ids = journal_obj.search([('type', '=','sale'),('company_id', '=', task.event_id.company_id.id)], limit=1)
            if not journal_ids:
                raise UserError(_('Define purchase journal for this company: "%s" (id:%d).') % (task.event_id.company_id.name, task.event_id.company_id.id))
            inv_lines = []
            rec_acc_id = partner_brw.property_account_receivable_id
            #print "rec_acc_id............",rec_acc_id
            if rec_acc_id.company_id and partner_brw.company_id and rec_acc_id.company_id.id != partner_brw.company_id.id:
                raise UserError(_('Please Login with proper user for company %s')%(task.company_id and task.company_id.name))
            for task_line in task.work_ids:
                inv_line_data = {}
                inv_line_data2 = {}
                product_ids = self.env['product.product'].search([('type','=','service'),('sale_ok','=',True),('active','=',True),('company_id','=',task.event_id.company_id.id),('service_type','=','interpreter')])
                if not product_ids:
                    raise UserError(_('Please define a Interpreter service type product for this company.'))
                product = product_ids[0]
                acc_id = product.property_account_income_id.id
                if not acc_id:
                    acc_id = product.categ_id.property_account_income_categ_id.id
                if not acc_id:
                    raise UserError(_('Define income account for this product: "%s" (id:%d).') % (product.name, product.id,))
#                acc_id1=self.pool.get('account.account').search(cr ,uid ,[('name','ilike','%Product Sales%')])
#                print "acc_id1,........",acc_id1
                analytic_account_id = task.project_id and task.project_id.analytic_account_id or False
                if task.event_id.event_type == 'language':
                    if task_line.task_for and task_line.task_for == 'interpreter':
                        for interpreter in task.event_id.assigned_interpreters:
                            self=self.with_context(interpreter=interpreter)
                            inv_line_data = self._prepare_inv_line_interpreter_for_customer(acc_id, task_line,task.event_id ,product)
                elif task.event_id.event_type == 'transport':
                    if task_line.task_for and task_line.task_for == 'transporter':
                        invoice_for='transporter'
                        inv_line_data = self._prepare_inv_line_transporter_for_customer(acc_id, task_line,task.event_id ,product)
                elif task.event_id.event_type == 'lang_trans':
                    if task_line.task_for and task_line.task_for == 'interpreter':
                        for interpreter in task.event_id.assigned_interpreters:
                            self = self.with_context(interpreter=interpreter)
                            inv_line_data = self._prepare_inv_line_interpreter_for_customer(acc_id, task_line,task.event_id ,product)
                    if task_line.task_for and task_line.task_for == 'transporter':
                        invoice_for='transporter'
                        inv_line_data2 = self._prepare_inv_line_transporter_for_customer(acc_id, task_line,task.event_id ,product)
                if inv_line_data:
                    inv_line_id = inv_line_obj.create(inv_line_data).id
                    inv_lines.append(inv_line_id)
                if inv_line_data2:
                    inv_line_id = inv_line_obj.create(inv_line_data2).id
                    inv_lines.append(inv_line_id)
            inv_data = {
                'name':  task.event_id.partner_id and task.event_id.partner_id.ref or '',
                'reference':  task.event_id.name,
                'date_invoice': self._context.get('invoice_date',False),
                'event_id': task.event_id.id ,
                'account_id': rec_acc_id and rec_acc_id.id or False,
                'type': 'out_invoice',
                'partner_id': task.event_id.partner_id and task.event_id.partner_id.id or False,
                'currency_id': task.event_id.company_id.currency_id and task.event_id.company_id.currency_id.id or False,
                'journal_id': len(journal_ids) and journal_ids[0].id or False,
                'invoice_line_ids': [(6, 0, inv_lines)],
                'origin': task.event_id.name,
                'doctor_id': task.event_id.doctor_id and task.event_id.doctor_id.id or False,
                'language_id': task.event_id.language_id and task.event_id.language_id.id or False,
                'location_id': task.event_id.location_id and task.event_id.location_id.id or False,
                'contact_id': task.event_id.contact_id and task.event_id.contact_id.id or False,
                'ordering_partner_id': task.event_id.ordering_partner_id and task.event_id.ordering_partner_id.id or False,
                'ordering_contact_id': task.event_id.ordering_contact_id and task.event_id.ordering_contact_id.id or False,
                'project_name_id': task.event_id.project_name_id and task.event_id.project_name_id.id or False,
                #'fiscal_position': order.fiscal_position.id or False,
                'payment_term_id': partner_brw.property_payment_term_id and partner_brw.property_payment_term_id.id or False,
                'company_id': task.event_id.company_id and task.event_id.company_id.id or False,
                'amount_charged': 0.0,
                'cust_gpuid': task.event_id.cust_gpuid,
                'cust_csid': task.event_id.cust_csid,
                'sales_representative_id':task.event_id.sales_representative_id and task.event_id.sales_representative_id.id or False,
                'invoice_for': invoice_for,
                'is_monthly': task.event_id.partner_id and task.event_id.partner_id.is_monthly or False,
            }
            #print "inv_data.................",inv_data
            inv_id = inv_obj.create(inv_data)
            #print "inv_id.................",inv_id
            # compute the invoice
            inv_id.compute_taxes()
            res = inv_id.id
        return res

    @api.model
    def action_invoice_create_supplier(self):
        """ Generates Supplier invoice for given ids of Task """
        res, invoice_for = [], 'other'
        journal_obj = self.env['account.journal']
        inv_obj = self.env['account.invoice']
        inv_line_obj = self.env['account.invoice.line']
        for task in self:
            partner_brw = task.event_id.partner_id
            if not task.event_id:
                raise UserError(_('No Event is attached to this task.'))
            if not task.work_ids:
                raise UserError(_('Please enter timesheet first.'))
            journal_ids = journal_obj.search([('type', '=','purchase'),('company_id', '=', task.event_id.company_id.id)], limit=1)
            if not journal_ids:
                raise UserError(_('Define purchase journal for this company: "%s" (id:%d).') % (task.event_id.company_id.name, task.event_id.company_id.id))
            inv_lines = []
#            rec_acc_id = partner.browse(cr ,uid ,task.event_id.partner_id.id).property_account_receivable
            rec_acc_id = partner_brw.property_account_payable_id
            if rec_acc_id.company_id and partner_brw.company_id and rec_acc_id.company_id.id != partner_brw.company_id.id:
                raise UserError(_('Please Login with proper user for company %s')%(task.company_id and task.company_id.name ))
            for task_line in task.work_ids:
                inv_line_data, inv_line_data2 = {}, {}
                product_ids = self.env['product.product'].search([('type','=','service'),('sale_ok','=',True),('active','=',True),('company_id','=',task.event_id.company_id.id),('service_type','=','interpreter')])
                if not product_ids:
                    raise UserError(_('Please define a Interpreter service type product for this company.'))
                product = product_ids[0]
                acc_id = product.property_account_expense_id.id
                if not acc_id:
                    acc_id = product.categ_id.property_account_expense_categ_id.id
                if not acc_id:
                    raise UserError(_('There is no expense account defined for this product: "%s" (id:%d).') % (product.name, product.id,))
                analytic_account_id = task.project_id and task.project_id.analytic_account_id or False
                if task.event_id.event_type == 'language':
                    inv_line_data = self._prepare_inv_line_interpreter(acc_id, task_line,task.event_id ,product)

                elif task.event_id.event_type == 'transport':
                    if task_line.task_for and task_line.task_for == 'transporter':
                        invoice_for='transporter'
                        inv_line_data = self._prepare_inv_line_transporter(acc_id, task_line,task.event_id ,product)
                elif task.event_id.event_type == 'lang_trans':
                    if self._context.get('transporter',False):
                        if task_line.task_for and task_line.task_for == 'transporter' :
                            invoice_for='transporter'
                            inv_line_data2 = self._prepare_inv_line_transporter(acc_id, task_line,task.event_id ,product)
                    else:
                        inv_line_data = self._prepare_inv_line_interpreter(acc_id, task_line,task.event_id ,product)
                #print"inv_line_data",inv_line_data
                inv_line_id1,inv_line_id2 = False,False
                if inv_line_data:
                    inv_line_id1 = inv_line_obj.create(inv_line_data).id
#                    inv_lines.append(inv_line_id)
                if inv_line_data2:
                    inv_line_id2 = inv_line_obj.create(inv_line_data2).id
#                    inv_lines.append(inv_line_id)
                #order_line_browse.write({'invoiced':True, 'invoice_lines': [(4, inv_line_id)]}, context=context)
            # get invoice data and create invoice
            #################################################################################3
                partner_id = False
                if task.event_id.event_type == 'transport':#in ('transport','lang_trans'):
                    partner_id = task.event_id.transporter_id and task.event_id.transporter_id.id or False
                elif task.event_id.event_type == 'language':
                    partner_id = task_line.interpreter_id.id or False
                elif task.event_id.event_type == 'lang_trans':
                    if self._context.get('transporter',False) and task_line.task_for == 'transporter':
                        partner_id = task.event_id.transporter_id and task.event_id.transporter_id.id or False
                    else:
                        partner_id = task_line.interpreter_id.id or False
#                print "ppartner_id++++++++++",partner_id
                supplier = self.env['res.partner'].browse(partner_id)
                if inv_line_id1 or inv_line_id2:
                    inv_data = {
                        'name':  task.event_id.partner_id and task.event_id.partner_id.ref or False,
                        'reference':  task.event_id.name,
                        'date_invoice': self._context.get('invoice_date',False),
                        'event_id': task.event_id.id ,
                        'account_id': rec_acc_id and rec_acc_id.id or False,
                        'type': 'in_invoice',
                        'partner_id': partner_id or False,
                        'currency_id': task.event_id.company_id.currency_id and task.event_id.company_id.currency_id.id or False,
                        'journal_id': len(journal_ids) and journal_ids[0].id or False,
                        'invoice_line_ids': [(6, 0, [inv_line_id1 or inv_line_id2])],
                        'origin': task.event_id.name,
                        'transporter_id': task.event_id.transporter_id and task.event_id.transporter_id.id or False,
                        'doctor_id': task.event_id.doctor_id and task.event_id.doctor_id.id or False,
                        'language_id': task.event_id.language_id and task.event_id.language_id.id or False,
                        'location_id': task.event_id.location_id and task.event_id.location_id.id or False,
                        'contact_id': task.event_id.contact_id and task.event_id.contact_id.id or False,
                        'ordering_partner_id': task.event_id.ordering_partner_id and task.event_id.ordering_partner_id.id or False,
                        'ordering_contact_id': task.event_id.ordering_contact_id and task.event_id.ordering_contact_id.id or False,
                        'project_name_id': task.event_id.project_name_id and task.event_id.project_name_id.id or False,
                        #'fiscal_position': order.fiscal_position.id or False,
                        'payment_term_id': supplier.property_supplier_payment_term_id and supplier.property_supplier_payment_term_id.id or False,
                        'company_id': task.event_id.company_id and task.event_id.company_id.id or False,
                        'amount_charged':0.0,
                        'cust_gpuid': task.event_id.cust_gpuid,
                        'cust_csid': task.event_id.cust_csid,
                        'department':task.event_id.department,
                        'sales_representative_id':task.event_id.sales_representative_id and task.event_id.sales_representative_id.id or False,
                        'invoice_for':invoice_for,
                    }
                    inv_id = inv_obj.create(inv_data)
                    # compute the invoice
                    inv_id.compute_taxes()
                    res.append(inv_id.id)
        return res

    @api.multi
    def send_for_billing(self):
        ''' function to create invoices for the event related to this task.  '''
        cust_inv_id, supp_inv_id, supp_inv_transp_id = False, False, False
        cur_obj = self
        event = cur_obj.event_id
        mod_obj = self.env['ir.model.data']
        # self.action_close()
#        if cur_obj.state != 'done':
#            raise osv.except_osv(_('Warning!'),_('Please mark the timesheet as done first.'))
#        if not cur_obj.work_ids:
#            raise osv.except_osv(_('Warning!'),_('No Timesheet Lines available for the related Task.'))    
        if event.order_note: # To test , if the event is verified 
            if event.verify_state != 'verified':
                raise UserError(_('Event is not verified yet and it requires Verification.'))
        if event:
            if not event.event_end:
                raise UserError(_('You must fill Event End Time in the Event Form.'))
            if event.event_start > event.event_end:
                raise UserError(_('Event Start Time should be not greater than Event End Time.'))
            supp_inv_transp_id = False
            cust_inv_id = self.action_invoice_create_customer()
            supp_inv_id = self.action_invoice_create_supplier()
            if event.event_type == 'lang_trans':
                self=self.with_context(transporter=True)
                supp_inv_transp_id = self.action_invoice_create_supplier()
            trans_inv_id = False
            if event.event_type =='lang_trans':
                event.write({'cust_invoice_id': cust_inv_id,'supp_invoice_ids': [(6,0,supp_inv_id)],'supp_invoice_id2': supp_inv_transp_id[0]})
                self.write({'cust_invoice_id': cust_inv_id, 'supp_invoice_ids': [(6,0,supp_inv_id)], 'supp_invoice_id2': supp_inv_transp_id[0],'billing_state':'billed'})
                trans_inv_id = supp_inv_transp_id[0]
            if event.event_type =='language':
                event.write({'cust_invoice_id': cust_inv_id,'supp_invoice_ids': [(6,0,supp_inv_id)]})
                self.write({'cust_invoice_id': cust_inv_id, 'supp_invoice_ids': [(6,0,supp_inv_id)],'billing_state':'billed'})
            if event.event_type =='transport':
                event.write({'cust_invoice_id': cust_inv_id,'supp_invoice_id2': supp_inv_id[0]})
                self.write({'cust_invoice_id': cust_inv_id, 'supp_invoice_id2': supp_inv_id[0],'billing_state':'billed'})
                trans_inv_id = supp_inv_id[0]
                
            if self._context.get('customer_service',False):
                return True
            elif self._context.get('billing_form',False):# going  back to billing form
                if self._context.get('billing_form_id',False):
                    billing_form_rec=self.env['billing.form'].browse(self._context.get('billing_form_id'))
                    billing_form_rec.write({
                        'cust_invoice_id': cust_inv_id or False,
                        'supp_invoice_ids': [(6,0,supp_inv_id)] if event.event_type in ('language','lang_trans') else [(6,0,[])],
                        'supp_invoice_id2': trans_inv_id,
                    })
                res = mod_obj.get_object_reference('bista_iugroup', 'view_billing_form')
                res_id = res and res[1] or False,
                return {
                    'name': _('Billing Form'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': [res_id[0]],
                    'res_model': 'billing.form',
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'current',
                    'res_id': self._context.get('billing_form_id',False),
                }
            else:
                if event.event_type in ('lang_trans','transport'):
                    res = mod_obj.get_object_reference('bista_iugroup', 'invoice_supplier_transporter_form')
                else:
                    res = mod_obj.get_object_reference('account', 'invoice_supplier_form')
                res_id = res and res[1] or False,
                return {
                    'name': _('Invoice For Event %s')%(event.name),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': [res_id[0]],
                    'res_model': 'account.invoice',
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'current',
                    'res_id': supp_inv_id[0] or False,
                }
        else:
            return True

    @api.multi
    def send_for_billing_cust(self):
        ''' function to restrict Customer Service to see the Invoice Details and Create Invoice '''
        self=self.with_context(customer_service=True)
        res = self.send_for_billing()
        return res or True



class project_work(models.Model):
    _inherit = "project.task.work"

    @api.depends('event_start_time','event_end_time')
    def _calculate_hours(self):
        ''' Calculates Hours from start and End time Entered By user '''
        for task_line in self:
            DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            event_start = task_line.event_start_time
            event_end = task_line.event_end_time
            if not event_start or not event_end:
                task_line.hours = 0.0
                continue
            event_id = task_line.task_id.event_id
            from_dt = datetime.datetime.strptime(str(event_start), DATETIME_FORMAT)
            to_dt = datetime.datetime.strptime(str(event_end), DATETIME_FORMAT)
#            if event_id:
 #               if (event_id.event_start_date != task_line.event_start_date) or  (event_id.event_start_date != task_line.event_start_date):
  #                  raise UserError(_('Task Line date cannot be different from Event Date'))
   #         if event_end < event_start :
    #            raise UserError(_('Event start time cannot be greater than event end time'))
            
            diff =to_dt - from_dt
            #print"diff..hours.......",diff
            if 'days' in str(diff) or 'day' in str(diff):
                raise UserError(_('Difference cannot be greater than 1 day'))
            hr = str(diff).split(':')[0]
            min = str(diff).split(':')[1]
            #print"hr....,min....hours.",hr,min
            spend_time = str(hr) +"."+ str(min)
            #print"spend_time.....",spend_time
            task_line.hours= float(spend_time) or 0.0


    @api.depends('event_start_time','event_end_time')
    def _calculate_time_spent(self):
        ''' Calculates Hours from start and End time Entered By user '''
        for task_line in self:
            DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            event_start = task_line.event_start_time
            event_end = task_line.event_end_time
            if not event_start or not event_end:
                task_line.time_spent = 0.0
                continue
            event_id = task_line.task_id.event_id
            from_dt = datetime.datetime.strptime(str(event_start), DATETIME_FORMAT)
            to_dt = datetime.datetime.strptime(str(event_end), DATETIME_FORMAT)
#            if event_id:
#                if (event_id.event_start_date != task_line.event_start_date) or  (event_id.event_start_date != task_line.event_start_date):
#                    raise osv.except_osv(_('Warning!'),_('Task Line date cannot be different from Event Date'))
#            if event_end < event_start :
#                raise osv.except_osv(_('Warning!'),_('Event start time cannot be greater than event end time'))
            diff =  to_dt - from_dt
#            print "diff+++++++spent++++",diff
#            if 'days' in str(diff) or 'day' in str(diff):
#                raise osv.except_osv(_('Warning!'),_('Difference cannot be greater than 1 day'))
            hr = str(diff).split(':')[0]
            min = str(diff).split(':')[1]
#            print "hr++++min+++++spent++",hr,min
#            hrs_min = float(5.0/3.0) * int(min)
            hrs_min = int(min)/60.0
#            print "hrs_min+++++spent++",hrs_min
            hrs_dec = int(hr)+hrs_min
#            hrs_dec = str(hr) +"."+ str(int(hrs_min))
#            print "hrs_dec+++++spent++",hrs_dec
            task_line.time_spent= hrs_dec
        
    @api.model
    def create(self,vals):
        ''' Inherited for the calculation of start and end time of task lines '''
        event_tz = False
                # get user's timezone
        user = self.env.user
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if 'task_id' in vals:
            task = self.env['project.task'].browse(vals['task_id'])
            if task.event_id:
                event_tz = task.event_id.customer_timezone
        if event_tz:
            tz = pytz.timezone(event_tz) or pytz.utc
        elif user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.timezone('US/Pacific') or pytz.utc

        if not ('event_start_time' in vals) and ('event_start_date' in vals or 'event_start_hr' in vals or 'event_start_min' in vals or 'am_pm' in vals):
#            print "in not event statyr tyime++++++++++++++++++++++++++++=="
            event_start_date = vals.get('event_start_date',False)
            event_start_hr = int(vals.get('event_start_hr',0.0))
            event_start_min = int(vals.get('event_start_min',0.0))
            event_end_hr = int(vals.get('event_end_hr',0.0))
            event_end_min = int(vals.get('event_end_min',0.0))
            am_pm = vals.get('am_pm',False)
            
            #print "event_date ,event_start_hr,event_start_min ,event_end_hr,event_start_min,event_end_min, am_pm,am_pm2........",event_start_date,event_start_hr,event_end_hr,event_end_min,am_pm,am_pm2
            if event_start_hr and event_start_hr > 12:
                raise UserError(_("Task start time hours can't be greater than 12 "))
            if event_start_min and event_start_min > 59:
                raise UserError(_("Task start time minutes can't be greater than 59 "))
#            if (event_start_hr and event_start_min) and (event_start_hr == 12 and event_start_min > 0):
#                raise osv.except_osv(_('Check Start time!'), _("Task start time can't be greater than 12 O'clock "))
            if event_end_hr and event_end_hr > 12:
                raise UserError(_(" Task end time hours can't be greater than 12 "))
            if event_end_min and event_end_min > 59:
                raise UserError(_("Task end time minutes can't be greater than 59 "))
#            if (event_end_hr and event_end_min) and (event_end_hr == 12 and event_end_min > 0):
#                raise osv.except_osv(_('Check End time!'), _("Task End time can't be greater than 12 O'clock "))
            if event_start_hr < 1 and event_start_min < 1:
                raise UserError(_("Task start time can not be 0 or less than 0"))
#            if event_end_hr < 1 and event_end_min < 1:
#                raise osv.except_osv(_('Check End time!'), _("Task end time can not be 0 or less than 0"))
            if event_start_date:
                if am_pm and am_pm == 'pm':
                    if event_start_hr < 12:
                        event_start_hr += 12
                if am_pm and am_pm == 'am':
                    if event_start_hr == 12:
                        event_start_hr = 0
                if event_start_hr == 24: # for the 24 hour format
                    event_start_hr = 23
                    event_start_min = 59
                event_start = str(event_start_date) + ' ' + str(event_start_hr) + ':' + str(event_start_min) + ':00'
                #print 'event_start.......',event_start
                # get localized dates
                local_dt = tz.localize(datetime.datetime.strptime(event_start,DATETIME_FORMAT), is_dst=None)
#                print "local_dt........",local_dt
                vals['event_start_time'] = local_dt.astimezone (pytz.utc).strftime (DATETIME_FORMAT)
#                print "local_dt222........",local_dt.astimezone (pytz.utc).strftime (DATETIME_FORMAT)
################As we already pass the GMT/UTC time no need to convert########################
#        if 'event_start_time' in vals and vals['event_start_time']:
#            print "in event start time+++++++++++++++++++++++"
#            local_dt = tz.localize(datetime.datetime.strptime(vals['event_start_time'],DATETIME_FORMAT), is_dst=None)
#            print "local_dt........",local_dt
#            vals['event_start_time'] = local_dt.astimezone (pytz.utc).strftime (DATETIME_FORMAT)
#            print "local_dt222........",local_dt.astimezone (pytz.utc).strftime (DATETIME_FORMAT)


        if not ('event_end_time' in vals) and ('event_end_hr' in vals or 'event_end_min' in vals or 'am_pm2' in vals) :
#            print "in not efvewnt end tome in d+++++++++++++++++++++="
            event_end_hr = int(vals.get('event_end_hr',0.0))
            event_end_min = int(vals.get('event_end_min',0.0))
            am_pm2 = vals.get('am_pm2',False)
            if am_pm2 and am_pm2 == 'pm':
                if event_end_hr < 12:
                    event_end_hr += 12
            if am_pm2 and am_pm2 == 'am':
                if event_end_hr == 12:
                    event_end_hr = 0
            if event_end_hr == 24: # for the 24 hour format
                event_end_hr = 23
                event_end_min = 59
            event_end = str(event_start_date) + ' ' + str(event_end_hr) + ':' + str(event_end_min) + ':00'
            #print 'event_end.......',event_end
            local_dt1 = tz.localize(datetime.datetime.strptime(event_end,DATETIME_FORMAT), is_dst=None)
#            print "local_dt1........",local_dt1
            vals['event_end_time'] = local_dt1.astimezone (pytz.utc).strftime (DATETIME_FORMAT)
#            print "local_dt1222222........",local_dt1.astimezone (pytz.utc).strftime (DATETIME_FORMAT)
#                if datetime.datetime.strptime(event_end,DATETIME_FORMAT) < datetime.datetime.strptime(event_start,DATETIME_FORMAT):
#                    raise osv.except_osv(_('Warning!'),_('Task start time cannot be greater than Task End Time.'))
#                elif datetime.datetime.strptime(event_end,DATETIME_FORMAT) == datetime.datetime.strptime(event_start,DATETIME_FORMAT):
#                    raise osv.except_osv(_('Warning!'),_('Task start time cannot be equal to Task End Time.'))
        #print "vals..final........",vals
        ######################################################################
################As we already pass the GMT/UTC time no need to convert########################

#        if 'event_end_time' in vals and vals['event_end_time']:
#            print "in event end time+++++++++++++++++++"
#            local_dt = tz.localize(datetime.datetime.strptime(vals['event_end_time'],DATETIME_FORMAT), is_dst=None)
#            print "local_dt........",local_dt
#            vals['event_end_time'] = local_dt.astimezone (pytz.utc).strftime (DATETIME_FORMAT)
#            print "local_dt222........",local_dt.astimezone (pytz.utc).strftime (DATETIME_FORMAT)
        task_line_id = super(project_work, self).create(vals)
       # task_line_id.edited=True
        return task_line_id

    @api.multi
    def write(self, vals):
        ''' Inherited for the calculation of start and end time of task lines '''
        event_tz = False
        if 'edited' in vals and vals['edited'] == False:
            vals['edited'] = False
        else:
            vals['edited'] = True
        vals['user_id'] = self.env.uid
                # Here formatting for Task Start date and Task End Date is done according to timezone of user or server
        if 'event_out_come_id' in vals or 'event_start_date' in vals or 'event_start_hr' in vals or 'event_start_min' in vals or 'event_end_hr' in vals or \
            'event_end_min' in vals or 'am_pm' in vals or 'am_pm2' in vals :
            DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            # get user's timezone
            user = self.env.user
            tz = False
            for task_work in self:
                if task_work.task_id and task_work.task_id.event_id:
                    event_tz = task_work.task_id.event_id.customer_timezone or False
            if event_tz:
                tz = pytz.timezone(event_tz) or pytz.utc
            elif user.tz:
                tz = pytz.timezone(user.tz) or pytz.utc
            else:
                tz = pytz.timezone('US/Pacific') or pytz.utc

            #print "tz...........",tz
            event_start_date ,event_start_hr ,event_start_min = False , 0 ,0
            event_end_hr , event_end_min , am_pm , am_pm2 = 0 , 0 , 'am' , 'pm'
            cur_obj = self
            if 'event_start_date' in vals and vals['event_start_date']:
                event_start_date = vals.get('event_start_date',False)
            else:
                event_start_date = cur_obj.event_start_date
            if 'event_start_hr' in vals :
                event_start_hr = int(vals.get('event_start_hr',0.0))
            else:
                event_start_hr = int(cur_obj.event_start_hr) if cur_obj.event_start_hr else 0
            if 'event_start_min' in vals :
                event_start_min = int(vals.get('event_start_min',0.0))
            else:
                event_start_min = int(cur_obj.event_start_min) if cur_obj.event_start_min else 0
            if 'event_end_hr' in vals :
                event_end_hr = int(vals.get('event_end_hr',0.0))
            else:
                event_end_hr = int(cur_obj.event_end_hr) if cur_obj.event_end_hr else 0
            if 'event_end_min' in vals :
                event_end_min = int(vals.get('event_end_min',0.0))
            else:
                event_end_min = int(cur_obj.event_end_min) if cur_obj.event_end_min else 0
            if 'am_pm' in vals and vals['am_pm']:
                am_pm = vals.get('am_pm',False)
            else:
                am_pm = cur_obj.am_pm
            if 'am_pm2' in vals and vals['am_pm2']:
                am_pm2 = vals.get('am_pm2',False)
            else:
                am_pm2 = cur_obj.am_pm2
            #print "event_date ,event_start_hr,event_start_min ,event_end_hr,event_start_min,event_end_min, am_pm,am_pm2........",event_start_date,event_start_hr,event_end_hr,event_end_min,am_pm,am_pm2
            if event_start_hr and event_start_hr > 12:
                raise UserError(_("Timesheet start time hours can't be greater than 12 "))
            if event_start_min and event_start_min > 59:
                raise UserError(_("Timesheet start time minutes can't be greater than 59 "))
#            if (event_start_hr and event_start_min) and (event_start_hr == 12 and event_start_min > 0):
#                raise osv.except_osv(_('Check Start time!'), _("Task start time can't be greater than 12 O'clock "))
            if event_end_hr and event_end_hr > 12:
                raise UserError(_(" Timesheet end time hours can't be greater than 12 "))
            if event_end_min and event_end_min > 59:
                raise UserError(_("Timesheet end time minutes can't be greater than 59 "))
#            if (event_end_hr and event_end_min) and (event_end_hr == 12 and event_end_min > 0):
#                raise osv.except_osv(_('Check End time!'), _("Task End time can't be greater than 12 O'clock "))
            if event_start_hr < 1 and event_start_min < 1:
                raise UserError(_("Timesheet start time can not be 00 or less than 00"))
            if event_end_hr < 1 and event_end_min < 1:
                raise UserError(_("Timesheet end time can not be 00 or less than 00"))
#            if event_start_date:
            if am_pm and am_pm == 'pm':
                if event_start_hr < 12:
                    event_start_hr += 12
            if am_pm and am_pm == 'am':
                if event_start_hr == 12:
                    event_start_hr = 0
            if event_start_hr == 24: # for the 24 hour format
                event_start_hr = 23
                event_start_min = 59
            event_start = str(event_start_date) + ' ' + str(event_start_hr) + ':' + str(event_start_min) + ':00'
            #print 'event_start.......',event_start
            # get localized dates
            local_dt = tz.localize(datetime.datetime.strptime(event_start,DATETIME_FORMAT), is_dst=None)
            vals['event_start_time'] = local_dt.astimezone (pytz.utc).strftime (DATETIME_FORMAT)

            if am_pm2 and am_pm2 == 'pm':
                if event_end_hr < 12:
                    event_end_hr += 12
            if am_pm2 and am_pm2 == 'am':
                if event_end_hr == 12:
                    event_end_hr = 0
            if event_end_hr == 24: # for the 24 hour format
                event_end_hr = 23
                event_end_min = 59
            event_end = str(event_start_date) + ' ' + str(event_end_hr) + ':' + str(event_end_min) + ':00'
            #print 'event_end.......',event_end
            local_dt1 = tz.localize(datetime.datetime.strptime(event_end,DATETIME_FORMAT), is_dst=None)
            #print "local_dt1........",local_dt1
            vals['event_end_time'] = local_dt1.astimezone (pytz.utc).strftime (DATETIME_FORMAT)
            if datetime.datetime.strptime(event_end,DATETIME_FORMAT) < datetime.datetime.strptime(event_start,DATETIME_FORMAT):
                raise UserError(_('The task start time cannot be greater then end time.'))
            elif datetime.datetime.strptime(event_end,DATETIME_FORMAT) == datetime.datetime.strptime(event_start,DATETIME_FORMAT):
                raise UserError(_('The task start time cannot be equal to end time.'))
#        print "vals....write final....",vals
        attachment_obj = self.env['ir.attachment']
        if 'timesheet_attachment' in vals and vals['timesheet_attachment']:
            for record in self:
                result = base64.decodestring(vals['timesheet_attachment'])
                rec_name = str(record.task_id.name)
                file_name = rec_name[:rec_name.find(':')]
                if not vals.get('attachment_filename').lower().endswith(('.jpg', '.tiff', '.gif', '.bmp', '.png',
                                                                         '.pdf')):
                    raise UserError(_('Unsupported File Format.'))
                uploaded_filename, extension = splitext(str(vals.get('attachment_filename')))
                file_name = file_name + '_timesheet' + extension
                attachment_id = attachment_obj.create(
                                                      { 'name': file_name,'datas': base64.encodestring(result),
                                                        'datas_fname': file_name,'res_model': 'event',
                                                        'res_id': record.task_id.event_id.id,'type': 'binary',
                                                      })
        res = super(project_work, self).write(vals)
        for rec in  self:
            if not rec.event_start_hr:
              raise UserError(_('Please enter event start hour'))
            if not rec.event_start_min:
               raise UserError(_('Please enter event start min'))
            if not rec.am_pm:
              raise UserError(_('Please enter AM/PM'))
            if not rec.am_pm2:
               raise UserError(_('Please enter AM/PM'))
            if not rec.event_end_hr:
               raise UserError(_('Please enter event end hour'))
            if not rec.event_end_min:
               raise UserError(_('Please enter event end min'))
            if not rec.event_out_come_id:
               raise UserError(_('Please enter Event Outcome'))
            edited = True
            task=rec.task_id
            if task.work_ids:
                # logger = logging.getLogger('test2')
                # logger.info("This is tasks edited------->%s " % 'test')
                for line in task.work_ids:
                    if not line.edited:
                        edited = False
                        break
            else:
                edited = False
            stage_id = self.env['project.task.type'].search([('name', '=', 'done')], limit=1).id
            if task.stage_id == stage_id:
                for line in task.work_ids:
                    if not line.edited:
                        line.edited= True
                event = task.event_id
                event.task_state = 'done'
            logger = logging.getLogger('test2')
            logger.info("This is tasks edited------->%s " % str(self))
            task.all_edited = edited
            if edited:
                ir_model_data = self.env['ir.model.data']
                event = task.event_id

                task.remaining_hours = 0.0
                stage_id = self.env['project.task.type'].search([('name', '=', 'done')], limit=1).id
                event.task_state='done'
                task.stage_id = stage_id
                if not task.date_end:
                    task.date_end = fields.datetime.now()

                template_id = False
                if event:
                    template_id = ir_model_data.get_object_reference('bista_iugroup', 'event_time_verification')[1]
                    if event.order_note and event.verify_state != 'verified':
                        try:
                            if template_id:
                                self.env['mail.template'].sudo().browse(template_id).send_mail(event.id)
                        except Exception:
                            pass
        return res


    def _get_hour(self):
        ''' this Function gets default hours on the basis of users timezone '''
        # get user's timezone
        user = self.env.user
        tz = False
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.timezone("US/Pacific") or pytz.utc
        #print "time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)......",time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        localized_datetime = pytz.utc.localize(datetime.datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),"%Y-%m-%d %H:%M:%S")).astimezone(tz)
        #print "localized_datetime.............",localized_datetime
        localized_datetime = localized_datetime.replace(tzinfo=None)
        #localized_datetime = str(localized_datetime)[:19]
        dt = datetime.datetime.strptime(str(localized_datetime), "%Y-%m-%d %H:%M:%S")
        tm_tuple = dt.timetuple()
        hour = tm_tuple.tm_hour
        min = tm_tuple.tm_min
        #print "hour...min..........",hour,min
        if hour == 12 and min == 0 :
            hour -= 12
        elif hour >= 12 and min > 0 :
            hour -= 12
        #print "tm_tuple.tm_hour.......",tm_tuple.tm_hour
        return str(hour) or str(0)

    def _get_minute(self):
        ''' this Function gets default minutes on the basis of users timezone '''
        user = self.env.user
        tz = False
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.timezone("US/Pacific") or pytz.utc
        #print "time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)......",time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        localized_datetime = pytz.utc.localize(datetime.datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),"%Y-%m-%d %H:%M:%S")).astimezone(tz)
        #print "localized_datetime.............",localized_datetime
        localized_datetime = localized_datetime.replace(tzinfo=None)
        dt = datetime.datetime.strptime(str(localized_datetime), "%Y-%m-%d %H:%M:%S")
        tm_tuple = dt.timetuple()
        return str(tm_tuple.tm_min) or str(0)

    def _get_am_pm(self):
        ''' this Function gets default Am-Pm on the basis of users timezone '''
        user = self.env.user
        tz = False
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.timezone("US/Pacific") or pytz.utc
        #print "time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)......",time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        localized_datetime = pytz.utc.localize(datetime.datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),"%Y-%m-%d %H:%M:%S")).astimezone(tz)
        #print "localized_datetime.............",localized_datetime
        localized_datetime = localized_datetime.replace(tzinfo=None)
        dt = datetime.datetime.strptime(str(localized_datetime), "%Y-%m-%d %H:%M:%S")
        tm_tuple = dt.timetuple()
        hour = tm_tuple.tm_hour
        min = tm_tuple.tm_min
        #print "hour...min..........",hour,min
        am_pm = 'am'
        if hour == 12 and min == 0:
            am_pm = 'pm'
        elif hour >= 12 and min >= 0 :
            am_pm = 'pm'
        return am_pm or 'am'

    hours=fields.Float(compute=_calculate_hours, string='Time Spent', store=True,default=0.0)
    hours_spend=fields.Char('Time Spent',size=64)
    event_start_time=fields.Datetime('Task Start Time',default=lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
    event_end_time=fields.Datetime('Task End Time',default=lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
    total_mileage_covered=fields.Integer('Total Mileage Covered')
    task_for=fields.Selection([('interpreter','Interpreter'),('transporter','Transporter'),('translator','Translator')], 'Task For', required=True,default='interpreter')
    # Fields Added for Custom Start and End Date Time
    event_start_date=fields.Date("Task Date", required=True,default=lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT))
    event_start_hr=fields.Char("Task Start Hours", size=2,default=_get_hour)
    event_start_min=fields.Char("Task Start Minutes", size=2,default=_get_minute)
    event_end_hr=fields.Char("Task End Hours", size=2,default=_get_hour)
    event_end_min=fields.Char("Task End Minutes", size=2,default=_get_minute)
    am_pm=fields.Selection([('am','AM'),('pm','PM')],"AM/ PM",default=_get_am_pm)
    am_pm2=fields.Selection([('am','AM'),('pm','PM')],"AM/ PM",default=_get_am_pm)
    wait_time=fields.Float('Wait Time')
    wait_time_bill=fields.Float('Wait Time Bill')
    travel_time=fields.Float('Travel Time')
    interpreter_id=fields.Many2one('res.partner','Interpreter')
    #interpreter_user_id=fields.Many2one('res.users',related='interpreter_id.user_id',store=True)
    transporter_id=fields.Many2one('res.partner','Transporter')
    event_out_come_id=fields.Many2one('event.out.come', 'Event Outcome')
    edited=fields.Boolean('Edited?')
    time_spent=fields.Float(compute=_calculate_time_spent,string='Time Spent',store=True)
    timesheet_attachment=fields.Binary('Attach Timesheet')
    attachment_filename=fields.Char('Filename')

    @api.multi
    def mark_as_done(self):
        ''' function to mark as time sheet line is Entered '''
        cur_obj = self
        user = self.env.user
        if not cur_obj.edited:
            self.write({'edited': True})
            mod_obj = self.env['ir.model.data']#SUPERUSER_ID
            if user.user_type and user.user_type == 'vendor':
                if user.partner_id.cust_type == 'transporter':
                    res = mod_obj.sudo().get_object_reference('bista_iugroup', 'view_task_form_portal_transporter')
                else:
                    res = mod_obj.sudo().get_object_reference('bista_iugroup', 'view_task_form_portal')
            else:
                res = mod_obj.sudo().get_object_reference('project', 'view_task_form2')
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
                'res_id': cur_obj.task_id and cur_obj.task_id.id or False,
            }
        else:
            return True

    @api.onchange('event_start_hr')
    def onchange_event_start_hr(self):
        res = {'value': {}, 'warning': {}}
        if not self.event_start_hr:
            return res
        time = self.event_start_hr.strip()
        try:
            int(time)
        except:
            warning = {
                'title': _('Invalid Time'),
                'message': _('Please enter valid time value.(Do not use Characters)')
            }
            res['warning'] = warning
            res['value']['event_start_hr'] = ''
            return res
        if len(time) == 1:
            res['value']['event_start_hr'] = '0' + time
        return res

    @api.onchange('event_start_min')
    def onchange_event_start_min(self):
        res = {'value': {}, 'warning': {}}
        if not self.event_start_min:
            return res
        time = self.event_start_min.strip()
        try:
            int(time)
        except:
            warning = {
                'title': _('Invalid Time'),
                'message': _('Please enter valid time value.(Do not use Characters)')
            }
            res['warning'] = warning
            res['value']['event_start_min'] = ''
            return res
        if len(time) == 1:
            res['value']['event_start_min'] = '0' + time
        return res

    @api.onchange('event_end_hr')
    def onchange_event_end_hr(self):
        res = {'value': {}, 'warning': {}}
        if not self.event_end_hr:
            return res
        time = self.event_end_hr.strip()
        try:
            int(time)
        except:
            warning = {
                'title': _('Invalid Time'),
                'message': _('Please enter valid time value.(Do not use Characters)')
            }
            res['warning'] = warning
            res['value']['event_end_hr'] = ''
            return res
        if len(time) == 1:
            res['value']['event_end_hr'] = '0' + time
        return res

    @api.onchange('event_end_min')
    def onchange_event_end_min(self):
        res = {'value': {}, 'warning': {}}
        if not self.event_end_min:
            return res
        time = self.event_end_min.strip()
        try:
            int(time)
        except:
            warning = {
                'title': _('Invalid Time'),
                'message': _('Please enter valid time value.(Do not use Characters)')
            }
            res['warning'] = warning
            res['value']['event_end_min'] = ''
            return res
        if len(time) == 1:
            res['value']['event_end_min'] = '0' + time
        return res

    @api.multi
    def _check_start_end_date(self):
        ''' validates Start and End Date in Task Lines . Task End Date should be greater than Task start Date'''
        for task_line in self:
            DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            if task_line.event_start_time and task_line.event_end_time:
                start=datetime.datetime.strptime(str(task_line.event_start_time), DATETIME_FORMAT)
#                print "in _check_start_end_date  start+++",start
                end=datetime.datetime.strptime(str(task_line.event_end_time), DATETIME_FORMAT)
#                print "in _check_start_end_date  end+++",end
                if start > end:
                    raise UserError(_(' Task start date can not be greater than task end Date.'))
        return True
    _constraints = [(_check_start_end_date, '', [])]

    @api.onchange('wait_time')
    def onchange_wait_time(self):
        if self.wait_time > 0:
            return {'value':{'wait_time_bill': self.wait_time}}
        else:
            return {'value':{}}
