from odoo import fields,models,api
from odoo.tools.translate import _
import datetime
from dateutil import relativedelta
import calendar
from odoo.exceptions import UserError

class recurring_event(models.TransientModel):
    _name='recurring.event'

    @api.model
    def default_get(self, fields):
        res = {}
        res = super(recurring_event, self).default_get(fields)
        active_ids = self._context.get('active_ids',False)
        if active_ids:
            brow_event = self.env['event'].browse(active_ids[0])
            if 'event_start_hr' in fields:
                res.update(event_start_hr = brow_event.event_start_hr)
            if 'event_start_min' in fields:
                res.update(event_start_min = brow_event.event_start_min)
            if 'event_end_hr' in fields:
                res.update(event_end_hr = brow_event.event_end_hr)
            if 'event_end_min' in fields:
                res.update(event_end_min = brow_event.event_end_min) 
            if 'am_pm' in fields:
                res.update(am_pm = brow_event.am_pm)
            if 'am_pm2' in fields:
                res.update(am_pm2 = brow_event.am_pm2)
        return res

    recurring_type=fields.Selection([('daily','Daily'),('weekly','Weekly'),('monthly','Monthly')],"Recurring Type",required=True,default='daily')
    monday=fields.Boolean('Monday')
    tuesday=fields.Boolean('Tuesday')
    wednesday=fields.Boolean('Wednesday')
    thursday=fields.Boolean('Thursday')
    friday=fields.Boolean('Friday')
    saturday=fields.Boolean('Saturday')
    sunday=fields.Boolean('Sunday')
    start_date=fields.Date('Start Date', required=True)
    end_date=fields.Date('End Date', required=True)
    event_start_hr=fields.Char("Event Start Hours", size=2, required=True,default='00')
    event_start_min=fields.Char("Event Start Minutes", size=2, required=True,default='00')
    event_end_hr=fields.Char("Event End Hours", size=2, required=True,default='00')
    event_end_min=fields.Char("Event End Minutes", size=2, required=True,default='00')
    am_pm=fields.Selection([('am','AM'),('pm','PM')],"AM/PM", required=True,default='am')
    am_pm2=fields.Selection([('am','AM'),('pm','PM')],"AM/PM", required=True,default='am')
    appt_date=fields.Integer('Appointment Date', required=True,size=2)
    recurring_attachment=fields.Binary('Attach File')
    file_name=fields.Char('Attachment Name', size=64)

    @api.multi
    def recur_event(self):
        ''' Function to recur event for the selected days or months '''
        event_obj = self.env['event']
        obj = self
        active_id = self._context.get('active_id')
        event_rec = event_obj.browse(active_id)
        if not active_id:
            return True
        if not obj.start_date:
            raise UserError(_('Please enter Start Date!'))
        if not obj.end_date:
            raise UserError(_('Please enter End Date!'))
        if obj.start_date >= obj.end_date:
             raise UserError(_('End date should be greater than start date.'))
        sta_date = datetime.datetime.strptime(obj.start_date, '%Y-%m-%d')
        day = calendar.day_name[sta_date.weekday()]
        print "day............",day
        en_date = datetime.datetime.strptime(obj.end_date, '%Y-%m-%d')
        diff_days = int((en_date - sta_date).days)
        month_diff = int(en_date.month - sta_date.month)
        print"-------------month_diff",month_diff
        
        sta_date = sta_date.strftime('%Y-%m-%d')
        print "sta_date------------",sta_date,type(sta_date)
        print "diff_days.........",diff_days
        new_event_ids = []
        default = {'ref':event_rec.ref or '',
            'cost_center':event_rec.cost_center or '',
            'cust_gpuid':event_rec.cust_gpuid or '',
            'cust_csid':event_rec.cust_csid or '',
            'event_note':event_rec.event_note or '',
            'department':event_rec.department or '',
            'scheduler_id':event_rec.scheduler_id.id or ''}
        self=self.with_context(
            copy_wizard_vals=True,
            ref=event_rec.ref or '',
            cost_center=event_rec.cost_center or '',
            cust_gpuid=event_rec.cust_gpuid or '',
            cust_csid=event_rec.cust_csid or '',
            event_note=event_rec.event_note or '',
            department=event_rec.department or '',
            scheduler_id=event_rec.scheduler_id.id or '')
        if obj.recurring_type in ('daily','weekly'):
            for day1 in range(0,diff_days):
                fix_date = False
                fix_date = datetime.datetime.strptime(sta_date, '%Y-%m-%d') + relativedelta.relativedelta(days=day1)
                day = calendar.day_name[fix_date.weekday()]
                print"fix_date............",fix_date
                print"----------------DAY",day,type(type)
                if obj.monday and day=="Monday" or obj.tuesday and day=="Tuesday" or obj.wednesday and day=="Wednesday" or obj.thursday and day=="Thursday" or obj.friday and day=="Friday" or obj.saturday and day=="Saturday" or obj.sunday and day=="Sunday" :
                    default.update({
                        'event_start_hr': obj.event_start_hr or '00',
                        'event_start_min': obj.event_start_min or '00',
                        'am_pm': obj.am_pm or False,
                        'event_end_hr': obj.event_end_hr or '00',
                        'event_end_min': obj.event_end_min or '00',
                        'am_pm2': obj.am_pm2 or False,
                        'event_start_date': fix_date.date() or False,
                    })
                    res_id = event_rec.with_context(
            copy_wizard_vals=True,
            ref=event_rec.ref or '',
            cost_center=event_rec.cost_center or '',
            cust_gpuid=event_rec.cust_gpuid or '',
            cust_csid=event_rec.cust_csid or '',
            event_note=event_rec.event_note or '',
            department=event_rec.department or '',
            scheduler_id=event_rec.scheduler_id.id or '',
                    user_id=event_rec.user_id.id or '').copy(default)
                    new_event_ids.append(res_id.id)
                    file_name = 'Attachment'
                    if obj.recurring_attachment:
                        self.env['ir.attachment'].with_context(type='binary').create({
                            'name': obj.file_name or file_name,
                            'datas': obj.recurring_attachment,
                            'datas_fname': obj.file_name or file_name,
                            'res_model': self._context.get('active_model'),
                            'res_id': res_id.id})
        else:
            for month_new in range(0, month_diff+1):
                month_date = False
                month_date = datetime.datetime.strptime(sta_date, '%Y-%m-%d') + relativedelta.relativedelta(months=month_new)
                print"month_date............",month_date
                if not obj.appt_date or obj.appt_date > 31:
                    raise UserError(_('Please enter valid appointment date!'))
                apt_date = str(obj.appt_date)
                if len(apt_date) == 1:
                    apt_date = '0' + apt_date
                new_date = str(month_date.year) + '-' + str(month_date.month) + '-' + apt_date
                default.update({
                    'event_start_hr': obj.event_start_hr or '00',
                    'event_start_min': obj.event_start_min or '00',
                    'am_pm': obj.am_pm or False,
                    'event_end_hr': obj.event_end_hr or '00',
                    'event_end_min': obj.event_end_min or '00',
                    'am_pm2': obj.am_pm2 or False,
                    'event_start_date': new_date or False,
                })
                res_id = event_rec.with_context(
            copy_wizard_vals=True,
            ref=event_rec.ref or '',
            cost_center=event_rec.cost_center or '',
            cust_gpuid=event_rec.cust_gpuid or '',
            cust_csid=event_rec.cust_csid or '',
            event_note=event_rec.event_note or '',
            department=event_rec.department or '',
            scheduler_id=event_rec.scheduler_id.id or '',
                    user_id=event_rec.user_id.id or '').copy(default)
                new_event_ids.append(res_id.id)
                file_name = 'Attachment'
                if obj.recurring_attachment:
                    self.env['ir.attachment'].with_context(type='binary').create({
                        'name': obj.file_name or file_name,
                        'datas': obj.recurring_attachment,
                        'datas_fname': obj.file_name or file_name,
                        'res_model': self._context.get('active_model'),
                        'res_id': res_id.id})
        print "new_event_ids.......",new_event_ids
        res = {
            'domain': str([('id','in',new_event_ids)]),
            'name': 'Events',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'event',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
        return res

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
    
#     def onchange_time(self,cr,uid,ids,event_start_time,event_end_time,context=None):
#         ''' ----Depricated-----'''
#         res,warning = {},{}
#         DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
#         res = {}
#         if event_start_time and not event_end_time:
#             return True
#         else:
#             if event_start_time and event_end_time:
#                 start=datetime.datetime.strptime(str(event_start_time), DATETIME_FORMAT)
#                 if event_end_time:
#                     end=datetime.datetime.strptime(str(event_end_time), DATETIME_FORMAT)
#                     if start > end:
#                         res.update({'event_end': False})
#                         warning = {
#                             'title': _('Warning!'),
#                             'message' : _('Event start time cannot be greater than event end time')
#                             }
#         return {'value': res,'warning':warning}
#
#
#
# recurring_event()

