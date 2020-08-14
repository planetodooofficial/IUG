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
import pytz
import time
from datetime import datetime, date
from odoo import tools, SUPERUSER_ID
from odoo import fields,models,api,_
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

from dateutil.relativedelta import relativedelta
from jinja2.lexer import _describe_token_type
import xlwt
import cStringIO
import base64
from . import format_common
from distutils.log import info
from dateutil.relativedelta import relativedelta 
from calendar import month
from odoo.exceptions import UserError
from datetime import timedelta
import logging
import requests, json
_logger = logging.getLogger(__name__)

def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + timedelta(days=4)
    return next_month - timedelta(days=next_month.day)

# from addons_iu.account.test.test_parent_structure import ids
class invoice_analysis_iug(models.Model):
    _name = 'invoice.analysis.iug'
    _description = "IUG Invoices Statistics"
    _order = 'month'

    month=fields.Integer('Month')
    month_name=fields.Selection([('1','January'), ('2','February'), ('3','March'), ('4','April'), ('5','May'), ('6','June'),
                ('7','July'), ('8','August'), ('9','September'), ('10','October'), ('11','November'), ('12','December')], string='Month', readonly=True, index=True )
    draft=fields.Float('Draft')
    open=fields.Float('Open')
    paid=fields.Float('Paid')
    total=fields.Float('Total')
    gp=fields.Float('GP%')
    dashboard_id=fields.Many2one('iug.invoice.dashboard', 'Dashboard Id')
    dashboard_id2=fields.Many2one('iug.invoice.dashboard', 'Dashboard Id')

    
class iug_invoice_dashboard(models.Model):
    _name = "iug.invoice.dashboard"
    _description = "IUG Invoices Statistics"

    @api.model
    def _get_year(self):
        ''' this Function gets Current Year on the basis of users timezone '''
        user = self.env.user
        tz = False
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.timezone("US/Pacific") or pytz.utc
        localized_datetime = pytz.utc.localize(datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),"%Y-%m-%d %H:%M:%S")).astimezone(tz)
        localized_datetime = localized_datetime.replace(tzinfo=None)
        return str(datetime.strptime(str(localized_datetime), "%Y-%m-%d %H:%M:%S").timetuple().tm_year)

    date=fields.Date('Current Date',default=fields.Date.context_today)
    year=fields.Char('Current Year',default=_get_year)
    company_id=fields.Many2one("res.company","Company Id", required=True,default=lambda self: self.env['res.company']._company_default_get('iug.invoice.dashboard'))
    analysis_lines=fields.One2many('invoice.analysis.iug','dashboard_id', 'Analysis Lines')
    supp_analysis_lines=fields.One2many('invoice.analysis.iug','dashboard_id2', 'Analysis Lines')

    @api.multi
    def search_invoices(self):
        ''' Function to Load Invoice '''
        cur_obj = self
        analysis_lines = cur_obj.analysis_lines + cur_obj.supp_analysis_lines
        analysis_lines.unlink()
        #inv_ids = invoice_obj.search(cr, uid, [('company_id','=',cur_obj.company_id.id),('year','=',cur_obj.year)])
        year = "'" + cur_obj.year + "'"
        self._cr.execute(""" SELECT month,sum (CASE WHEN state= 'draft' then amount_total else 0 END) as Draft,
                    sum (CASE WHEN state= 'open' then amount_total else 0 END) as Open,
                    sum (CASE WHEN state= 'paid' then amount_total else 0 END) as Paid,
                    sum(CASE WHEN state = 'paid' or state ='open' or state ='draft' then amount_total else 0 END) as Total
                    from account_invoice where type = 'out_invoice' and company_id =%s and year= %s  group by month order by month;"""%(cur_obj.company_id.id,year))
        
        cust_inv_data = self._cr.fetchall()
        
        self._cr.execute(""" SELECT month,sum (CASE WHEN state= 'draft' then amount_total else 0 END) as Draft,
                    sum (CASE WHEN state= 'open' then amount_total else 0 END) as Open,
                    sum (CASE WHEN state= 'paid' then amount_total else 0 END) as Paid,
                    sum(CASE WHEN state = 'paid' or state ='open' or state ='draft' then amount_total else 0 END) as Total
                    from account_invoice where type = 'in_invoice' and company_id =%s and year= %s group by month order by month;"""%(cur_obj.company_id.id,year))
        supp_inv_data = self._cr.fetchall()
        
       
        dict = {}
        for inv_sup in supp_inv_data:
            dict.update({inv_sup[0]:inv_sup[4]})
            self.write({'supp_analysis_lines': [(0, False, {'month': inv_sup[0], 'month_name': inv_sup[0], 'draft': inv_sup[1],
                                    'open': inv_sup[2],'paid': inv_sup[3],
                                    'total': inv_sup[4]})]})
        
        for inv_cust in cust_inv_data:
            gp = 0
            if inv_cust[0] in dict:
                profit = inv_cust[4] - dict.get(inv_cust[0])
                gp = (profit *100 / inv_cust[4])  if inv_cust[4] > 0.0 else 0.0 
            self.write({'analysis_lines': [(0, False, {'month': inv_cust[0], 'month_name': inv_cust[0], 'draft': inv_cust[1],
                                    'open': inv_cust[2],'paid': inv_cust[3],
                                    'total': inv_cust[4],'gp':gp})]})
            
        return True


class event_analysis_iug(models.Model):
    _name = 'event.analysis.iug'
    _description = "IUG Event Statistics"
    _order = 'month'

    month=fields.Integer('Month')
    month_name=fields.Selection([('1','January'), ('2','February'), ('3','March'), ('4','April'), ('5','May'), ('6','June'),
                ('7','July'), ('8','August'), ('9','September'), ('10','October'), ('11','November'), ('12','December')], string='Month', readonly=True, index=True )
    draft=fields.Integer('Draft')
    scheduled=fields.Integer('Job Offered')
    allocated=fields.Integer('Scheduled')
    unauthorize=fields.Integer('Unauthorized')
    confirmed=fields.Integer('Confirmed')
    unbilled=fields.Integer('Unbilled')
    invoiced=fields.Integer('Invoiced')
    cancel=fields.Integer('Cancelled')
    done=fields.Integer('Done')
    total=fields.Integer('Total')
    dashboard_id=fields.Many2one('iug.event.dashboard', 'Dashboard Id')
    
class iug_event_dashboard(models.Model):
    _name = "iug.event.dashboard"
    _description = "IUG Event Statistics"

    @api.model
    def _get_year(self):
        ''' this Function gets Current Year on the basis of users timezone '''
        user = self.env.user
        tz = False
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.timezone("US/Pacific") or pytz.utc
        localized_datetime = pytz.utc.localize(datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),"%Y-%m-%d %H:%M:%S")).astimezone(tz)
        localized_datetime = localized_datetime.replace(tzinfo=None)
        return str(datetime.strptime(str(localized_datetime), "%Y-%m-%d %H:%M:%S").timetuple().tm_year)
    

    date=fields.Date('Current Date',default=fields.Date.context_today)
    year=fields.Char('Current Year',default=_get_year)
    company_id=fields.Many2one("res.company","Company Id", required=True,default=lambda self: self.env['res.company']._company_default_get('iug.event.dashboard'))
    analysis_lines=fields.One2many('event.analysis.iug','dashboard_id', 'Analysis Lines')

    @api.multi
    def search_events(self):
        ''' Function to Load Event Analysis '''
        cur_obj = self
        analysis_lines = cur_obj.analysis_lines
        analysis_lines.unlink()
        year = "'" + cur_obj.year + "'"
        self._cr.execute("""SELECT month,sum (CASE WHEN state= 'draft' then 1 else 0 END) as unscheduled,
                    sum(CASE WHEN state= 'allocated' then 1 else 0 END) as allocated,
                    sum (CASE WHEN state= 'scheduled' then 1 else 0 END) as scheduled,
                    sum(CASE WHEN state= 'unauthorize' then 1 else 0 END) as unauthorize,
                    sum(CASE WHEN state= 'confirmed' then 1 else 0 END) as confirmed,
                    sum(CASE WHEN state= 'unbilled' then 1 else 0 END) as unbilled,
                    sum (CASE WHEN state= 'invoiced' then 1 else 0 END) as invoice,
                    sum (CASE WHEN state= 'done' then 1 else 0 END) as done,
                    sum (CASE WHEN state= 'cancel' then 1 else 0 END) as cancel,
                    count(*) as Total from event where company_id =%s and year= %s group by month order by month;"""%(cur_obj.company_id.id,year))
        data = self._cr.fetchall()
        if data and len(data) != 0:
            for d in data:
                if d[0] != None:
                    self.write({'analysis_lines': [(0, False, {'month': d[0], 'month_name': d[0], 'draft': d[1],
                                               'allocated':d[2], 'scheduled':d[3],'unauthorize':d[4],'confirmed':d[5],'unbilled':d[6],
                                              'invoiced':d[7],'done':d[8],'cancel':d[9],'total':d[10]})]})
            
        return True

class cancel_event_analysis_iug(models.Model):
    _name = 'cancel.event.analysis.iug'
    _description = "IUG Event Cancel Statistics"
    _order = 'month'

    month=fields.Integer('Month')
    month_name=fields.Selection([('1','January'), ('2','February'), ('3','March'), ('4','April'), ('5','May'), ('6','June'),
                ('7','July'), ('8','August'), ('9','September'), ('10','October'), ('11','November'), ('12','December')], string='Month', readonly=True, index=True )
    count=fields.Integer('Cancelled Count')
    fill_rate=fields.Float('Fill Rate%')
    total=fields.Integer('Total Events')
    dashboard_id=fields.Many2one('iug.cancel.event.dashboard', 'Dashboard Id')

    
class iug_cancel_event_dashboard(models.Model):
    _name = "iug.cancel.event.dashboard"
    _description = "IUG Cancel Event Statistics"

    @api.model
    def _get_year(self):
        ''' this Function gets Current Year on the basis of users timezone '''
        user = self.env.user
        tz = False
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.timezone("US/Pacific") or pytz.utc
        localized_datetime = pytz.utc.localize(datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),"%Y-%m-%d %H:%M:%S")).astimezone(tz)
        localized_datetime = localized_datetime.replace(tzinfo=None)
        return str(datetime.strptime(str(localized_datetime), "%Y-%m-%d %H:%M:%S").timetuple().tm_year)
    
    
#     def _get_default_reason(self, cr, uid, context=None):
#         company_id = self.browse(cr, uid, uid).company_id.id,
#         res = self.pool.get('cancel.reason').search(cr, uid, [('name','=','No interpreter available') and ('company_id','=',company_id) ], context=context)
#         for data in res:
#             return res[1] or False

    date=fields.Date('Current Date',default=fields.Date.context_today)
    year=fields.Char('Current Year',default=_get_year)
    cancel_reason_id=fields.Many2one('cancel.reason', 'Cancel Reason', track_visibility='onchange')
    company_id=fields.Many2one("res.company","Company Id", required=True,default=lambda self: self.env['res.company']._company_default_get('iug.cancel.event.dashboard'))
    partner_id=fields.Many2one("res.partner",'Customer Name')
    analysis_lines=fields.One2many('cancel.event.analysis.iug','dashboard_id', 'Analysis Lines')

    @api.multi
    def search_events(self):
        ''' Function to Load Event Analysis '''
        cur_obj = self
        analysis_lines = cur_obj.analysis_lines
        analysis_lines.unlink()
        year = "'" + cur_obj.year + "'"
        self._cr.execute("""SELECT month, sum (CASE WHEN state= 'cancel' then 1 else 0 END) as cancel, count(*) as Total
                    from event where company_id=6 and year = '2015' group by month order by month """)
        
        where = ""
#         if cur_obj.cancel_reason_id:
#             where+="and cancel_reason_id="+str(cur_obj.cancel_reason_id.id)
        if cur_obj.partner_id:
            where+= " and partner_id="+str(cur_obj.partner_id.id)
            
        dict = {}
        get_total = self._cr.fetchall()
        for total in get_total:
            dict.update({total[0]:total[2]})

        
        if cur_obj.cancel_reason_id and cur_obj.cancel_reason_id.id != False:
            query = """SELECT month,sum (CASE WHEN state= 'cancel' and cancel_reason_id=%s then 1 else 0 END) as cancel, count(*) as Total 
                        from event where company_id=%s and year =%s"""%(cur_obj.cancel_reason_id.id,cur_obj.company_id.id,year)
        else:
            query = """SELECT month,sum (CASE WHEN state= 'cancel' then 1 else 0 END) as cancel, count(*) as Total 
                        from event where company_id=%s and year =%s"""%(cur_obj.company_id.id,year)
        
        self._cr.execute(query+where+" group by month order by month;")
        
        cancel_data = self._cr.fetchall()
        
        fill_rate = 0
        for cancel_env in cancel_data:
            if cancel_env[0] in dict:
                fill_rate = (dict.get(cancel_env[0],0) - cancel_env[1]) * 100/ dict.get(cancel_env[0],0) if dict.get(cancel_env[0]) > 0 else 0.0
            self.write({'analysis_lines': [(0, False, {'month': cancel_env[0], 'month_name': cancel_env[0],
                                    'count': cancel_env[1],'total':cancel_env[2], 'fill_rate':fill_rate})]})
        return True
    
    @api.onchange('company_id')
    def onchange_company_id(self):
        ''' Empty some fields on change of company in the event Form '''
        res = self.env['cancel.reason'].search([('name','=','No interpreter available'),('company_id','=',self.company_id.id)]).ids
        val = {
            'partner_id': False ,
            'cancel_reason_id':res,
        }
        return {'value': val}


class scheduler_event_analysis_iug(models.Model):
    _name = 'scheduler.event.analysis.iug'
    _description = "IUG Event Scheduler Statistics"
    _order = 'scheduler_id'

    scheduler_id=fields.Many2one('res.users','Scheduler')
    count=fields.Integer('Count')
    draft=fields.Integer('Draft')
    allocated=fields.Integer('Scheduled')
    unauthorize=fields.Integer('Unauthorized')
    confirmed=fields.Integer('Confirmed')
    unbilled=fields.Integer('Unbilled')
    invoiced=fields.Integer('Invoiced')
    cancel=fields.Integer('Cancelled')
    done=fields.Integer('Done')
    total=fields.Integer('Total')
    dashboard_id=fields.Many2one('iug.scheduler.event.dashboard', 'Dashboard Id')

    
class iug_scheduler_event_dashboard(models.Model):
    _name = "iug.scheduler.event.dashboard"
    _description = "IUG Scheduler Event Statistics"

    @api.model
    def _get_year(self):
        ''' this Function gets Current Year on the basis of users timezone '''
        user = self.env.user
        tz = False
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.timezone("US/Pacific") or pytz.utc
        localized_datetime = pytz.utc.localize(datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),"%Y-%m-%d %H:%M:%S")).astimezone(tz)
        localized_datetime = localized_datetime.replace(tzinfo=None)
        return str(datetime.strptime(str(localized_datetime), "%Y-%m-%d %H:%M:%S").timetuple().tm_year)

    @api.model
    def _get_month(self):
        ''' this Function gets Current Month on the basis of users timezone '''
        user = self.env.user
        tz = False
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.timezone("US/Pacific") or pytz.utc
        localized_datetime = pytz.utc.localize(datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),"%Y-%m-%d %H:%M:%S")).astimezone(tz)
        localized_datetime = localized_datetime.replace(tzinfo=None)
        return str(datetime.strptime(str(localized_datetime), "%Y-%m-%d %H:%M:%S").timetuple().tm_mon)
    

    date=fields.Date('Current Date',default=fields.Date.context_today)
    year=fields.Char('Current Year',default=_get_year)
    month=fields.Selection([('1','January'), ('2','February'), ('3','March'), ('4','April'), ('5','May'), ('6','June'),
                ('7','July'), ('8','August'), ('9','September'), ('10','October'), ('11','November'), ('12','December')], 'Month',default=_get_month)
    company_id=fields.Many2one("res.company","Company Id", required=True,default=lambda self: self.env['res.company']._company_default_get('iug.scheduler.event.dashboard'))
    analysis_lines=fields.One2many('scheduler.event.analysis.iug','dashboard_id', 'Analysis Lines')

    @api.multi
    def search_events(self):
        ''' Function to Load Event Analysis '''
        cur_obj = self
        analysis_lines = cur_obj.analysis_lines
        analysis_lines.unlink()
        year = "'" + cur_obj.year + "'"
        month ="'" + cur_obj.month + "'"
        self._cr.execute(""" SELECT scheduler_id, sum(CASE WHEN state='draft' then 1 else 0 END) as Unscheduled,
                    sum(CASE WHEN state='scheduled' then 1 else 0 END) as Scheduled,
                    sum(CASE WHEN state='unauthorize' then 1 else 0 END) as Unauthorize,
                    sum(CASE WHEN state='confirmed' then 1 else 0 END) as Confirmed,
                    sum(CASE WHEN state='unbilled' then 1 else 0 END) as Unbilled,
                    sum(CASE WHEN state='invoiced' then 1 else 0 END) as Invoiced,
                    sum(CASE WHEN state='done' then 1 else 0 END) as done,
                    sum(CASE WHEN state='cancel' then 1 else 0 END) as Cancel,count(*) as Total
                    from event where company_id=%s and month=%s and year =%s group by scheduler_id
                    order by scheduler_id"""%(cur_obj.company_id.id,month,year))
        sch_events = self._cr.fetchall()
        for sch in sch_events:
             if sch[0] != None:
                self.write({'analysis_lines': [(0, False, {'scheduler_id':sch[0],'draft':sch[1],'scheduled':sch[2],
                                        'unauthorize':sch[3],'confirmed':sch[4],'unbilled':sch[5],'invoiced':sch[6],
                                        'done':sch[7],'cancel':sch[8],'total':sch[9]})]})
        return True

class AccountCommonReport(models.TransientModel):
    _inherit = "account.common.report"
    _description = "Account Common Report"



# class account_aged_trial_dashboard(models.TransientModel):
#     _name = 'account.aged.trial.balance'
#     _inherit = 'account.aged.trial.balance'
#
#     account_aged_lines=fields.One2many('columns.accounts.aged.receivable','account_aged_id', 'Aged Receivable Lines')
#     account_aged_pay_lines=fields.One2many('columns.accounts.aged.payable','account_aged_id', 'Aged Payable Lines')
#     chart_account_id=fields.Many2one('account.account', 'Chart of Account', help='Select Charts of Accounts',
#                                         domain=[('parent_id', '=', False)])
#     fiscalyear_id=fields.Many2one('account.fiscalyear', 'Fiscal Year', help='Keep empty for all open fiscal year')
#     filter=fields.Selection([('filter_no', 'No Filters'), ('filter_date', 'Date'), ('filter_period', 'Periods')],
#                                "Filter by", required=True,default='filter_no')
#     period_from=fields.Many2one('account.period', 'Start Period')
#     period_to=fields.Many2one('account.period', 'End Period')
#
#     @api.onchange('chart_account_id')
#     def onchange_chart_id(self):
#         res = {}
#         if self.chart_account_id:
#             company_id = self.chart_account_id.company_id.id
#             now = time.strftime('%Y-%m-%d')
#             domain = [('company_id', '=', company_id), ('date_start', '<', now), ('date_stop', '>', now)]
#             fiscalyears = self.env['account.fiscalyear'].search(domain).ids
#             res['value'] = {'company_id': company_id, 'fiscalyear_id': fiscalyears and fiscalyears[0] or False}
#         return res
#
#     @api.multi
#     def _check_company_id(self):
#         for wiz in self:
#             company_id = wiz.company_id.id
#             if wiz.fiscalyear_id and company_id != wiz.fiscalyear_id.company_id.id:
#                 return False
#             if wiz.period_from and company_id != wiz.period_from.company_id.id:
#                 return False
#             if wiz.period_to and company_id != wiz.period_to.company_id.id:
#                 return False
#         return True
#
#     _constraints = [
#         (_check_company_id, 'The fiscalyear, periods or chart of account chosen have to belong to the same company.', []),
#     ]
#
#     @api.onchange('filter')
#     def onchange_filter(self):
#         res = {'value': {}}
#         if self.filter == 'filter_no':
#             res['value'] = {'period_from': False, 'period_to': False, 'date_from': False ,'date_to': False}
#         if self.filter == 'filter_date':
#             res['value'] = {'period_from': False, 'period_to': False, 'date_from': time.strftime('%Y-01-01'), 'date_to': time.strftime('%Y-%m-%d')}
#         if self.filter == 'filter_period' and self.fiscalyear_id:
#             start_period = end_period = False
#             self._cr.execute('''
#                 SELECT * FROM (SELECT p.id
#                                FROM account_period p
#                                LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
#                                WHERE f.id = %s
#                                AND p.special = false
#                                ORDER BY p.date_start ASC, p.special ASC
#                                LIMIT 1) AS period_start
#                 UNION ALL
#                 SELECT * FROM (SELECT p.id
#                                FROM account_period p
#                                LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
#                                WHERE f.id = %s
#                                AND p.date_start < NOW()
#                                AND p.special = false
#                                ORDER BY p.date_stop DESC
#                                LIMIT 1) AS period_stop''', (self.fiscalyear_id.id, self.fiscalyear_id.id))
#             periods =  [i[0] for i in self._cr.fetchall()]
#             if periods and len(periods) > 1:
#                 start_period = periods[0]
#                 end_period = periods[1]
#             res['value'] = {'period_from': start_period, 'period_to': end_period, 'date_from': False, 'date_to': False}
#         return res
#
#     @api.model
#     def _get_account(self):
#         user = self.env.user
#         accounts = self.env['account.account'].search([('parent_id', '=', False), ('company_id', '=', user.company_id.id)], limit=1).ids
#         return accounts and accounts[0] or False
#
#     @api.model
#     def _get_fiscalyear(self):
#         now = time.strftime('%Y-%m-%d')
#         company_id = False
#         ids = self._context.get('active_ids', [])
#         if ids and self._context.get('active_model') == 'account.account':
#             company_id = self.env['account.account'].browse(ids[0]).company_id.id
#         else:  # use current company id
#             company_id = self.env.user.company_id.id
#         domain = [('company_id', '=', company_id), ('date_start', '<', now), ('date_stop', '>', now)]
#         fiscalyears = self.env['account.fiscalyear'].search(domain, limit=1).ids
#         return fiscalyears and fiscalyears[0] or False
#     #
#     # def _build_contexts(self,data):
#     #     result = {}
#     #     result['fiscalyear'] = 'fiscalyear_id' in data['form'] and data['form']['fiscalyear_id'] or False
#     #     result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
#     #     result['chart_account_id'] = 'chart_account_id' in data['form'] and data['form']['chart_account_id'] or False
#     #     result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
#     #     if data['form']['filter'] == 'filter_date':
#     #         result['date_from'] = data['form']['date_from']
#     #         result['date_to'] = data['form']['date_to']
#     #     elif data['form']['filter'] == 'filter_period':
#     #         if not data['form']['period_from'] or not data['form']['period_to']:
#     #             raise UserError(_('Select a starting and an ending period.'))
#     #         result['period_from'] = data['form']['period_from']
#     #         result['period_to'] = data['form']['period_to']
#     #     return result
#
#     @api.multi
#     def get_accounts_total(self):
#         res = {}
#         data = {}
#         tbal_obj = account_aged_partner_balance.aged_trial_report(self._cr, self._uid, 'account.aged_trial_balance', context=self._context)
#         data['ids'] = self._context.get('active_ids', [])
#         data['model'] = self._context.get('active_model', 'ir.ui.menu')
#         print self.read([])
#         data['form'] = self.read(['date_from',  'date_to',  'fiscalyear_id', 'journal_ids', 'period_from', 'period_to',  'filter',  'chart_account_id', 'target_move'])[0]
#         for field in ['fiscalyear_id', 'chart_account_id', 'period_from', 'period_to']:
#             if isinstance(data['form'][field], tuple):
#                 data['form'][field] = data['form'][field][0]
#         used_context = self._build_contexts(data)
#         data['form']['periods'] = used_context.get('periods', False) and used_context['periods'] or []
#         data['form']['used_context'] = dict(used_context, lang=self._context.get('lang', 'en_US'))
#         data = self.pre_print_report(data)
#         data['form'].update(self.read(['period_length', 'direction_selection'])[0])
#         select_cus = {'result_selection':'customer'}
#         data['form'].update(select_cus)
#         if data['form']['result_selection'] == 'customer':
#             objects = self.env['account.aged.trial.balance'].browse(data['ids'])
#             tbal_obj.set_context(objects, data, data['ids'], report_type=None)
#
#             period_length = data['form']['period_length']
#             if period_length<=0:
#                 raise UserError(_('You must set a period length greater than 0.'))
#             if not data['form']['date_from']:
#                 raise UserError(_('You must set a start date.'))
#
#             start = datetime.strptime(data['form']['date_from'], "%Y-%m-%d")
#             if data['form']['direction_selection'] == 'past':
#                 for i in range(5)[::-1]:
#                     stop = start - relativedelta(days=period_length)
#                     res[str(i)] = {
#                         'name': (i!=0 and (str((5-(i+1)) * period_length) + '-' + str((5-i) * period_length)) or ('+'+str(4 * period_length))),
#                         'stop': start.strftime('%Y-%m-%d'),
#                         'start': (i!=0 and stop.strftime('%Y-%m-%d') or False),
#                     }
#                     start = stop - relativedelta(days=1)
#             else:
#                 for i in range(5):
#                     stop = start + relativedelta(days=period_length)
#                     res[str(5-(i+1))] = {
#                         'name': (i!=4 and str((i) * period_length)+'-' + str((i+1) * period_length) or ('+'+str(4 * period_length))),
#                         'start': start.strftime('%Y-%m-%d'),
#                         'stop': (i!=4 and stop.strftime('%Y-%m-%d') or False),
#                     }
#                     start = stop + relativedelta(days=1)
#             data['form'].update(res)
#             if data.get('form',False):
#                 data['ids']=[data['form'].get('chart_account_id',False)]
#             data['form'].update(self.read(['target_move','period_length', 'direction_selection'])[0])
#
#             if self.direction_selection == 'future':
#                 head='Due'
#             period_length = data['form']['period_length']
#             if period_length<=0:
#                 raise UserError(_('You must set a period length greater than 0.'))
#             if not data['form']['date_from']:
#                 raise UserError(_('You must set a start date.'))
#
#             start = datetime.strptime(data['form']['date_from'], "%Y-%m-%d")
#
#             if data['form']['direction_selection'] == 'past':
#                 for i in range(5)[::-1]:
#                     stop = start - relativedelta(days=period_length)
#                     res[str(i)] = {
#                         'name': (i!=0 and (str((5-(i+1)) * period_length) + '-' + str((5-i) * period_length)) or ('+'+str(4 * period_length))),
#                         'stop': start.strftime('%Y-%m-%d'),
#                         'start': (i!=0 and stop.strftime('%Y-%m-%d') or False),
#                     }
#                     start = stop - relativedelta(days=1)
#             else:
#                 for i in range(5):
#                     stop = start + relativedelta(days=period_length)
#                     res[str(5-(i+1))] = {
#                         'name': (i!=4 and str((i) * period_length)+'-' + str((i+1) * period_length) or ('+'+str(4 * period_length))),
#                         'start': start.strftime('%Y-%m-%d'),
#                         'stop': (i!=4 and stop.strftime('%Y-%m-%d') or False),
#                     }
#                     start = stop + relativedelta(days=1)
#             data['form'].update(res)
#             if data.get('form',False):
#                 data['ids']=[data['form'].get('chart_account_id',False)]
#             tbal_obj._get_lines(data['form'])
#             get_data_receive =self.env['columns.accounts.aged.receivable'].search([])
#             get_data_receive.unlink()
#             self.write({'account_aged_lines': [(0, False, {'not_due': tbal_obj._get_direction('6'), 'period_30': tbal_obj._get_for_period('4'),'period_60': tbal_obj._get_for_period('3'),
#                                     'period_90': tbal_obj._get_for_period('2'),'period_120': tbal_obj._get_for_period('1'), 'period_above_120': tbal_obj._get_for_period('0'),'total': tbal_obj._get_for_period('5')})]})
#         tbal_obj.total_account = []
#         select_sup = {'result_selection':'supplier'}
#         data['form'].update(select_sup)
#         if data['form']['result_selection'] == 'supplier':
#             objects = self.env['account.aged.trial.balance'].browse(data['ids'])
#             tbal_obj.set_context(objects, data, data['ids'], report_type=None)
#
#             period_length = data['form']['period_length']
#             if period_length<=0:
#                 raise UserError(_('You must set a period length greater than 0.'))
#             if not data['form']['date_from']:
#                 raise UserError(_('You must set a start date.'))
#
#             start = datetime.strptime(data['form']['date_from'], "%Y-%m-%d")
#             if data['form']['direction_selection'] == 'past':
#                 for i in range(5)[::-1]:
#                     stop = start - relativedelta(days=period_length)
#                     res[str(i)] = {
#                         'name': (i!=0 and (str((5-(i+1)) * period_length) + '-' + str((5-i) * period_length)) or ('+'+str(4 * period_length))),
#                         'stop': start.strftime('%Y-%m-%d'),
#                         'start': (i!=0 and stop.strftime('%Y-%m-%d') or False),
#                     }
#                     start = stop - relativedelta(days=1)
#             else:
#                 for i in range(5):
#                     stop = start + relativedelta(days=period_length)
#                     res[str(5-(i+1))] = {
#                         'name': (i!=4 and str((i) * period_length)+'-' + str((i+1) * period_length) or ('+'+str(4 * period_length))),
#                         'start': start.strftime('%Y-%m-%d'),
#                         'stop': (i!=4 and stop.strftime('%Y-%m-%d') or False),
#                     }
#                     start = stop + relativedelta(days=1)
#             data['form'].update(res)
#             if data.get('form',False):
#                 data['ids']=[data['form'].get('chart_account_id',False)]
#             data['form'].update(self.read(['target_move','period_length', 'direction_selection'])[0])
#             if self.direction_selection == 'future':
#                 head='Due'
#             period_length = data['form']['period_length']
#             if period_length<=0:
#                 raise UserError(_('You must set a period length greater than 0.'))
#             if not data['form']['date_from']:
#                 raise UserError(_('You must set a start date.'))
#
#             start = datetime.strptime(data['form']['date_from'], "%Y-%m-%d")
#
#             if data['form']['direction_selection'] == 'past':
#                 for i in range(5)[::-1]:
#                     stop = start - relativedelta(days=period_length)
#                     res[str(i)] = {
#                         'name': (i!=0 and (str((5-(i+1)) * period_length) + '-' + str((5-i) * period_length)) or ('+'+str(4 * period_length))),
#                         'stop': start.strftime('%Y-%m-%d'),
#                         'start': (i!=0 and stop.strftime('%Y-%m-%d') or False),
#                     }
#                     start = stop - relativedelta(days=1)
#             else:
#                 for i in range(5):
#                     stop = start + relativedelta(days=period_length)
#                     res[str(5-(i+1))] = {
#                         'name': (i!=4 and str((i) * period_length)+'-' + str((i+1) * period_length) or ('+'+str(4 * period_length))),
#                         'start': start.strftime('%Y-%m-%d'),
#                         'stop': (i!=4 and stop.strftime('%Y-%m-%d') or False),
#                     }
#                     start = stop + relativedelta(days=1)
#             data['form'].update(res)
#             if data.get('form',False):
#                 data['ids']=[data['form'].get('chart_account_id',False)]
#             tbal_obj._get_lines(data['form'])
#             get_data_pay =self.env['columns.accounts.aged.payable'].search([])
#             get_data_pay.unlink()
#             self.write({'account_aged_pay_lines': [(0, False, {'not_due': tbal_obj._get_direction('6'), 'period_30': tbal_obj._get_for_period('4'),'period_60': tbal_obj._get_for_period('3'),
#                                     'period_90': tbal_obj._get_for_period('2'),'period_120': tbal_obj._get_for_period('1'), 'period_above_120': tbal_obj._get_for_period('0'),'total': tbal_obj._get_for_period('5')})]})
#
# account_aged_trial_dashboard()
#
# class columns_accounts_aged_receivable(models.TransientModel):
#     _name = 'columns.accounts.aged.receivable'
#
#     not_due=fields.Float('Not Due')
#     period_30=fields.Float('Period of 30')
#     period_60=fields.Float('Period of 60')
#     period_90=fields.Float('Period of 90')
#     period_120=fields.Float('Period of 120')
#     period_above_120=fields.Float('Period above 120')
#     total=fields.Float('Total')
#     account_aged_id=fields.Many2one('account.aged.trial.balance','Account aged ids')
#
# class columns_accounts_aged_payable(models.TransientModel):
#     _name = 'columns.accounts.aged.payable'
#
#     not_due=fields.Float('Not Due')
#     period_30=fields.Float('Period of 30')
#     period_60=fields.Float('Period of 60')
#     period_90=fields.Float('Period of 90')
#     period_120=fields.Float('Period of 120')
#     period_above_120=fields.Float('Period above 120')
#     total=fields.Float('Total')
#     account_aged_id=fields.Many2one('account.aged.trial.balance','Account aged ids')


# """ Current Day's Event Analysis based on states for all companies """

class iug_current_day_event_analysis(models.Model):
    _name = 'iug.current.day.event.analysis'
    _description = "Current Day Event"

    previous_date_from=fields.Date("Previous From")
    previous_date_to=fields.Date("Previous To")
    current_date_from=fields.Date("Current From")
    current_date_to=fields.Date("Current To")
    event_data_line_ids=fields.One2many('get.event.data','event_data_id','Event Lines')

    @api.model
    def default_get(self,fields):
        self._cr.execute("""SELECT company_id, sum (CASE WHEN state= 'draft' then 1 else 0 END) as unscheduled,
                    sum (CASE WHEN state= 'scheduled' then 1 else 0 END) as scheduled,
                    sum (CASE WHEN state= 'allocated' then 1 else 0 END) as allocated,
                    sum (CASE WHEN state='unauthorize' then 1 else 0 END) as unauthorize,
                    sum (CASE WHEN state='confirmed' then 1 else 0 END) as confirmed,
                    sum(CASE WHEN state='unbilled' then 1 else 0 END) as unbilled,
                    sum (CASE WHEN state= 'invoiced' then 1 else 0 END) as invoice,
                    sum (CASE WHEN state= 'cancel' then 1 else 0 END) as cancel,
                    sum (CASE WHEN state= 'done' then 1 else 0 END) as done, count(*) as Total
                    from event where event_start_date=date(CURRENT_TIMESTAMP AT TIME ZONE 'PDT') group by company_id order by company_id; """)
        res = {}
        event_data = self._cr.fetchall()
        lst_tpls = []
        for event in event_data:
            lst_tpls.append((0, False, {'company_name':str(event[0]),'draft': event[1], 'scheduled': event[2],
                                    'allocated': event[3],'unauthorize':event[4],'confirmed':event[5],
                                    'unbilled':event[6],'invoiced':event[7],'cancel':event[8],'done':event[9],
                                    'total':event[10]}))
        res={'event_data_line_ids':lst_tpls}
        res.update(res)
        return res

    @api.multi
    def get_compare_report(self):
        self._cr.execute(""" DELETE FROM iug_current_day_event_analysis where id != %s """, (self.ids))
        vals = {}
        self._cr.execute("""SELECT company_id, sum (CASE WHEN state= 'draft' then 1 else 0 END) as unscheduled,
                                   sum (CASE WHEN state= 'scheduled' then 1 else 0 END) as scheduled,
                                   sum (CASE WHEN state= 'allocated' then 1 else 0 END) as allocated,
                                   sum (CASE WHEN state='unauthorize' then 1 else 0 END) as unauthorize,
                                   sum (CASE WHEN state='confirmed' then 1 else 0 END) as confirmed,
                                   sum(CASE WHEN state='unbilled' then 1 else 0 END) as unbilled,
                                   sum (CASE WHEN state= 'invoiced' then 1 else 0 END) as invoice,
                                   sum (CASE WHEN state= 'cancel' then 1 else 0 END) as cancel,
                                   sum (CASE WHEN state= 'done' then 1 else 0 END) as done, count(*) as Total
                                   from event where event_start_date between %s and %s group by company_id order by company_id; """,
                         (self.previous_date_from, self.previous_date_to))
        res = {}
        previous_event_data = self._cr.fetchall()
        lst_tpls = []
        self._cr.execute(""" DELETE FROM get_event_data;""")
        for event in previous_event_data:
            lst_tpls.append((0, 0, {'date_from':self.previous_date_from, 'date_to':self.previous_date_to, 'company_name': str(event[0]), 'draft': event[1], 'scheduled': event[2],
                                    'allocated': event[3], 'unauthorize': event[4], 'confirmed': event[5],
                                    'unbilled': event[6], 'invoiced': event[7], 'cancel': event[8],
                                    'done': event[9],
                                    'total': event[10]}))
        self._cr.execute("""SELECT company_id, sum (CASE WHEN state= 'draft' then 1 else 0 END) as unscheduled,
                                           sum (CASE WHEN state= 'scheduled' then 1 else 0 END) as scheduled,
                                           sum (CASE WHEN state= 'allocated' then 1 else 0 END) as allocated,
                                           sum (CASE WHEN state='unauthorize' then 1 else 0 END) as unauthorize,
                                           sum (CASE WHEN state='confirmed' then 1 else 0 END) as confirmed,
                                           sum(CASE WHEN state='unbilled' then 1 else 0 END) as unbilled,
                                           sum (CASE WHEN state= 'invoiced' then 1 else 0 END) as invoice,
                                           sum (CASE WHEN state= 'cancel' then 1 else 0 END) as cancel,
                                           sum (CASE WHEN state= 'done' then 1 else 0 END) as done, count(*) as Total
                                           from event where event_start_date between %s and %s group by company_id order by company_id; """,
                         (self.current_date_from, self.current_date_to))
        current_event_data = self._cr.fetchall()
        for event in current_event_data:
            lst_tpls.append((0, 0, {'date_from':self.current_date_from, 'date_to':self.current_date_to, 'company_name': str(event[0]), 'draft': event[1], 'scheduled': event[2],
                                    'allocated': event[3], 'unauthorize': event[4], 'confirmed': event[5],
                                    'unbilled': event[6], 'invoiced': event[7], 'cancel': event[8],
                                    'done': event[9],
                                    'total': event[10]}))
        vals = {'event_data_line_ids': lst_tpls}
        current_id = self.write(vals)
        return current_id

    
    @api.model
    def get_vals_ids(self):
        self._cr.execute(""" DELETE FROM iug_current_day_event_analysis;""")
        vals = {}
        self._cr.execute("""SELECT company_id, sum (CASE WHEN state= 'draft' then 1 else 0 END) as unscheduled,
                    sum (CASE WHEN state= 'scheduled' then 1 else 0 END) as scheduled,
                    sum (CASE WHEN state= 'allocated' then 1 else 0 END) as allocated,
                    sum (CASE WHEN state='unauthorize' then 1 else 0 END) as unauthorize,
                    sum (CASE WHEN state='confirmed' then 1 else 0 END) as confirmed,
                    sum(CASE WHEN state='unbilled' then 1 else 0 END) as unbilled,
                    sum (CASE WHEN state= 'invoiced' then 1 else 0 END) as invoice,
                    sum (CASE WHEN state= 'cancel' then 1 else 0 END) as cancel,
                    sum (CASE WHEN state= 'done' then 1 else 0 END) as done, count(*) as Total
                    from event where event_start_date=date(CURRENT_TIMESTAMP AT TIME ZONE 'PDT') group by company_id order by company_id; """)
        res = {}
        event_data = self._cr.fetchall()
        lst_tpls = []
        for event in event_data:
            lst_tpls.append((0, False, {'company_name':str(event[0]),'draft': event[1], 'scheduled': event[2],
                                    'allocated': event[3],'unauthorize':event[4],'confirmed':event[5],
                                    'unbilled':event[6],'invoiced':event[7],'cancel':event[8],'done':event[9],
                                    'total':event[10]}))
        vals={'event_data_line_ids':lst_tpls}
        current_id = self.create(vals).id
        return current_id

    @api.model
    def send_mail_events_daily(self):
        la = pytz.timezone("America/Los_Angeles")
        now = datetime.now(la).strftime("%H : %M %p")
        template_id = None
        email_template_obj = self.env['mail.template']
        ir_model_data = self.env['ir.model.data']
        if 'AM' in now:
            template_id = ir_model_data.get_object_reference('bista_iugroup', 'current_day_event_analysis_template')[1]
        else:
            template_id = ir_model_data.get_object_reference('bista_iugroup', 'current_day_evening_event_analysis_template')[1]
        
        data = self.env['report.users'].search([('template_id', '=', template_id)])
        if data:
            for id in data:
                info = id
                for dd in info.get_info:
                    rec_id = self.get_vals_ids()
                    if template_id:
                        values=self.env['mail.template'].browse(template_id).generate_email(rec_id)
                        values['email_to'] = dd.mail_id
                        mail_mail_obj = self.env['mail.mail']
                        msg_id = mail_mail_obj.create(values)
                        if msg_id:
                            msg_id.send()
        else:
            rec_id = self.get_vals_ids()
            if template_id:
                values = self.env['mail.template'].browse(template_id).generate_email(rec_id)
                mail_mail_obj = self.env['mail.mail']
                msg_id = mail_mail_obj.create(values)
                if msg_id:
                    msg_id.send()
                
iug_current_day_event_analysis()


class get_event_data(models.Model):
    _name = 'get.event.data'

    draft=fields.Integer('Draft')
    scheduled=fields.Integer('Job Offered')
    allocated=fields.Integer('Scheduled')
    unauthorize=fields.Integer('Unauthorized')
    confirmed=fields.Integer('Confirmed')
    unbilled=fields.Integer('Unbilled')
    invoiced=fields.Integer('Invoiced')
    cancel=fields.Integer('Cancelled')
    done=fields.Integer('Done')
    total=fields.Integer('Total')
    event_data_id=fields.Many2one('iug.current.day.event.analysis','Events')
    company_name=fields.Selection([('6','ASIT'),('3','ACD'),('4','IUG-SD')], string='Company Name', readonly=True, index=True)
    date_from=fields.Date("From")
    date_to=fields.Date("To")

class print_xls_cols(models.Model):
    _name="print.xls.cols"

    name=fields.Char('Name',size=256)
    xls_output=fields.Binary('Excel output',readonly=True)

class profit_based_on_cust(models.Model):
    _name = 'profit.based.on.cust'

    @api.depends('total_amt_cust','total_amt_vend')
    def _compute_gp_price(self):
        for line in self:
            if line.total_amt_cust and line.total_amt_vend:
                line.gp_total=((line.total_amt_cust-line.total_amt_vend)/line.total_amt_cust)*100

    @api.depends('cols_profit.cust_inv','cols_profit.supp_inv')
    def _compute_cust_price(self):
        for line in self:
            cust_amount=0.0
            vend_amount=0.0
            for amt in line.cols_profit:
                cust_amount+=amt.cust_inv
                vend_amount+=amt.supp_inv
            line.total_amt_cust=cust_amount
            line.total_amt_vend=vend_amount




    company_id=fields.Many2one("res.company","Company Id", required=True,default=lambda self: self.env['res.company']._company_default_get('profit.based.on.cust'))
    cols_profit=fields.One2many("cols.profit.data",'cust_profit')
    date_from=fields.Date('Date From',required=True,default=lambda *a: datetime.now().strftime('%Y-%m-01'))
    date_to=fields.Date('Date To',required=True,default=lambda *a:datetime.now().strftime('%Y-%m-%d'))
    partner_id=fields.Many2one('res.partner','Select Customer')
    xls_output=fields.Boolean('Excel Output', help='Tick if you want to export report in excel file.')
    gp_total=fields.Float("Total GP%",compute='_compute_gp_price')
    total_amt_cust=fields.Float("Total customer amount%",compute='_compute_cust_price')
    total_amt_vend=fields.Float(compute='_compute_cust_price')
    @api.multi
    def get_data(self):
        cur_obj = self
        analysis_lines = cur_obj.cols_profit
        analysis_lines.unlink()
        
        self._cr.execute("""DELETE FROM profit_based_on_cust
                     WHERE date(create_date) < date(CURRENT_TIMESTAMP AT TIME ZONE 'PDT' - INTERVAL '2 days'); """)
        
        date_from = "'"+cur_obj.date_from+"'"
        date_to = "'"+cur_obj.date_to+"'"
        if cur_obj.partner_id.id:
            self._cr.execute("""
            select coalesce(cust_invoice.company_id,supp_invoice.company_id) as company_id,
            coalesce(cust_invoice.partner_id,supp_invoice.partner_id) as partner_id,
            coalesce(cust_invoice.name,supp_invoice.name) as partner_name,    
            CUST,
            CUST_PAID,
            SUPP,
            SUPP_RECVD,
            cust_invoice. no_of_events                
        
        from
        (
            select res_partner.company_id,res_partner.id as partner_id,res_partner.name,         
            sum (amount_total) as CUST,
            sum (amount_total-residual) as CUST_PAID,
            count(distinct event.id) as no_of_events,
            count(account_invoice.id)
                     
                        from res_partner 
                        inner join event on event.partner_id = res_partner.id
            inner join account_invoice on account_invoice.id=event.cust_invoice_id
            where event.event_start_date between %s and %s
                        group by res_partner.company_id, res_partner.id order by 2
            ) as cust_invoice inner join 
        (

        select res_partner.company_id,res_partner.id as partner_id, res_partner.name,         
        sum (amount_total) as SUPP,
        sum (amount_total-residual) as SUPP_RECVD,
        count(distinct event.id) as  no_of_events,
        count(account_invoice.id)                     
                        from res_partner 
                        inner join event on event.partner_id = res_partner.id
            inner join task_inv_rel on (event.id=task_inv_rel.event_id)
            inner join account_invoice on (account_invoice.id=task_inv_rel.invoice_id)                            
            where event.event_start_date between %s and %s and res_partner.id = %s and res_partner.company_id = %s
                        group by res_partner.company_id, res_partner.id order by 2
        ) as supp_invoice on (cust_invoice.partner_id=supp_invoice.partner_id)
            """
                        %(date_from,date_to,date_from,date_to,cur_obj.partner_id.id,cur_obj.company_id.id))
        
        else:
            self._cr.execute("""
            select coalesce(cust_invoice.company_id,supp_invoice.company_id) as company_id,
            coalesce(cust_invoice.partner_id,supp_invoice.partner_id) as partner_id,
            coalesce(cust_invoice.name,supp_invoice.name) as partner_name,    
            CUST,
            CUST_PAID,
            SUPP,
            SUPP_RECVD,
            cust_invoice. no_of_events                
        
        from
        (
            select res_partner.company_id,res_partner.id as partner_id,res_partner.name,         
            sum (amount_total) as CUST,
            sum (amount_total-residual) as CUST_PAID,
            count(distinct event.id) as no_of_events,
            count(account_invoice.id)
                     
                        from res_partner 
                        inner join event on event.partner_id = res_partner.id
            inner join account_invoice on account_invoice.id=event.cust_invoice_id
            where event.event_start_date between %s and %s
                        group by res_partner.company_id, res_partner.id order by 2
            ) as cust_invoice inner join 
        (

        select res_partner.company_id,res_partner.id as partner_id, res_partner.name,         
        sum (amount_total) as SUPP,
        sum (amount_total-residual) as SUPP_RECVD,
        count(distinct event.id) as  no_of_events,
        count(account_invoice.id)                     
                        from res_partner 
                        inner join event on event.partner_id = res_partner.id
            inner join task_inv_rel on (event.id=task_inv_rel.event_id)
            inner join account_invoice on (account_invoice.id=task_inv_rel.invoice_id)                            
            where event.event_start_date between %s and %s and res_partner.company_id = %s
                        group by res_partner.company_id, res_partner.id order by res_partner.id
        ) as supp_invoice on (cust_invoice.partner_id=supp_invoice.partner_id)
            """
                        %(date_from,date_to,date_from,date_to,cur_obj.company_id.id))
        data = self._cr.fetchall()
        if not data:
            raise UserError(_('No data available for selected filters'))
        else:
            for d in data:
                gp = 0
                if cur_obj.company_id != None: 
                    profit = d[3]-d[5]
                    gp = (profit *100 / d[3])  if  d[3] > 0.0 else 0.0 
                    self.write({'cols_profit': [(0, False, {'partner_id': d[1],
                                                   'cust_inv':d[3], 'cust_rec':d[4],'supp_inv':d[5],'supp_rec':d[6],
                                                   'event_count':d[7],'total_income':profit,'gp':gp})]})
        return True
    
    @api.multi
    def print_xls(self):
        self.get_data()
        cur_obj = self
#       Stying of worksheet
        M_header_tstyle = format_common.font_style(position='center', bold=1, border=1, fontos='black', font_height=400)
        header_tstyle_c = format_common.font_style(position='center', bold=1, border=1, fontos='black', font_height=150, color='grey')
        other_tstyle_c = format_common.font_style(position='center', fontos='black', font_height=200)  
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('Profitability Report')
        sheet.row(0).height = 256 * 3
        
        row = 0
        sheet.write(row, 0, 'Customer Name', header_tstyle_c)
        sheet.write(row, 1, 'Event Count',header_tstyle_c )
        sheet.write(row, 2, 'Amount Invoiced(Customer)',header_tstyle_c )
        sheet.write(row, 3, 'Amount Received(Customer)', header_tstyle_c)
        sheet.write(row, 4, 'Amount Invoiced(Vendor)', header_tstyle_c)
        sheet.write(row, 5, 'Amount Paid(Vendor)', header_tstyle_c)
        sheet.write(row, 6, 'Profit', header_tstyle_c)
        sheet.write(row, 7, 'GP', header_tstyle_c)
        
        
        row = 1
        for data in  cur_obj.cols_profit:
            sheet.write(row,0,data.partner_id.name,other_tstyle_c)
            sheet.write(row,1,data.event_count,other_tstyle_c)
            sheet.write(row,2,data.cust_inv,other_tstyle_c)
            sheet.write(row,3,data.cust_rec,other_tstyle_c)
            sheet.write(row,4,data.supp_inv,other_tstyle_c)
            sheet.write(row,5,data.supp_rec,other_tstyle_c)
            sheet.write(row,6,data.total_income,other_tstyle_c)
            sheet.write(row,7,data.gp,other_tstyle_c)
            row +=1

        
        
        stream = cStringIO.StringIO()
        workbook.save(stream)
        attach_id = self.env['print.xls.cols'].create({'name':'Profitability Report.xls', 'xls_output':base64.encodestring(stream.getvalue())})
        return {
            'name': ('Notification'),
            'context': self._context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'print.xls.cols',
            'res_id': attach_id.id,
            'type': 'ir.actions.act_window',
            'target':'new'
        }
 
##########################################################       
    @api.model
    def send_monthy_profit_report(self):
        today = date.today() 
        d = today - relativedelta(months=1) 
        date_from = (date(today.year, today.month, 1) - relativedelta(days=1)).strftime('%Y-%m-01')
        date_to = date(today.year, today.month, 1) - relativedelta(days=1)
        frm = "'"+str(date_from)+"'"
        to = "'"+str(date_to)+"'"
        self._cr.execute("""
            select coalesce(cust_invoice.company_id,supp_invoice.company_id) as company_id,
            coalesce(cust_invoice.partner_id,supp_invoice.partner_id) as partner_id,
            coalesce(cust_invoice.name,supp_invoice.name) as partner_name,    
            CUST,
            CUST_PAID,
            SUPP,
            SUPP_RECVD,
            cust_invoice. no_of_events                
        
        from
        (
            select res_partner.company_id,res_partner.id as partner_id,res_partner.name,         
            sum (amount_total) as CUST,
            sum (amount_total-residual) as CUST_PAID,
            count(distinct event.id) as no_of_events,
            count(account_invoice.id)
                     
                        from res_partner 
                        inner join event on event.partner_id = res_partner.id
            inner join account_invoice on account_invoice.id=event.cust_invoice_id
            where event.event_start_date between %s and %s
                        group by res_partner.company_id, res_partner.id order by 2
            ) as cust_invoice inner join 
        (

        select res_partner.company_id,res_partner.id as partner_id, res_partner.name,         
        sum (amount_total) as SUPP,
        sum (amount_total-residual) as SUPP_RECVD,
        count(distinct event.id) as  no_of_events,
        count(account_invoice.id)                     
                        from res_partner 
                        inner join event on event.partner_id = res_partner.id
            inner join task_inv_rel on (event.id=task_inv_rel.event_id)
            inner join account_invoice on (account_invoice.id=task_inv_rel.invoice_id)                            
            where event.event_start_date between %s and %s 
                        group by res_partner.company_id, res_partner.id order by res_partner.id
        ) as supp_invoice on (cust_invoice.partner_id=supp_invoice.partner_id)
            """
                        %(frm,to,frm,to))
        data = self._cr.fetchall()
   
        M_header_tstyle = format_common.font_style(position='center', bold=1, border=1, fontos='black', font_height=400)
        header_tstyle_c = format_common.font_style(position='center', bold=1, border=1, fontos='black', font_height=150, color='grey')
        other_tstyle_c = format_common.font_style(position='center', fontos='black', font_height=200)  
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('Profitability Report')
        sheet.row(0).height = 256 * 3
        
        row = 0
        sheet.write(row, 0, 'Company Name', header_tstyle_c)
        sheet.write(row, 1, 'Customer Name', header_tstyle_c)
        sheet.write(row, 2, 'Event Count',header_tstyle_c )
        sheet.write(row, 3, 'Amount Invoiced Customer(A)',header_tstyle_c )
        sheet.write(row, 4, 'Amount Received(Customer)', header_tstyle_c)
        sheet.write(row, 5, 'Amount Invoiced Vendor(B)', header_tstyle_c)
        sheet.write(row, 6, 'Amount Paid(Vendor)', header_tstyle_c)
        sheet.write(row, 7, 'Profit(A-B)', header_tstyle_c)
        sheet.write(row, 8, 'GP%', header_tstyle_c)
        
        
        get_company_name = {4:'ASIT',5:'ACD',6:'IUG-SD'}
        company = None
        row = 1
        for  info in data:
            if info[0] in get_company_name:
                company = get_company_name.get(info[0])
            profit = info[3]-info[5]
            gp = (profit *100 / info[3])  if  info[3] > 0.0 or info[2] < 0.0 else 0.0
            sheet.write(row,0,str(company),other_tstyle_c)
            sheet.write(row,1,str(info[2]),other_tstyle_c)
            sheet.write(row,2,str(info[7]),other_tstyle_c)
            sheet.write(row,3,str(info[3]),other_tstyle_c)
            sheet.write(row,4,str(info[4]),other_tstyle_c)
            sheet.write(row,5,str(info[5]),other_tstyle_c)
            sheet.write(row,6,str(info[6]),other_tstyle_c)
            sheet.write(row,7,str(profit),other_tstyle_c)
            sheet.write(row,8,str(gp),other_tstyle_c)
            row +=1

        
        stream = cStringIO.StringIO()
        workbook.save(stream)
        result  = base64.encodestring(stream.getvalue())
        file_name = 'profitability report of '+(datetime.now()- relativedelta(days=1)).strftime('%B-%Y')+'.xls'
        ir_attachment = self.env['ir.attachment'].create({'name': file_name,
                                                                       'datas': result,
                                                                       'datas_fname': file_name,
                                                                       })

        email_template_obj = self.env['mail.template']
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('bista_iugroup', 'monthly_event_analysis_template')[1]
        
        data = self.env['report.users'].search([('template_id', '=', template_id)])
        
        if data:
            for id in data:
                info = id
                for dd in info.get_info:
                    message = """<p><font color="blue">Hello """+dd.users.name+""",</font></p>
                               <p><font color="blue">Following is the PFA of monthly profitability report.</font></p>"""
                    if template_id:  
                        values=self.env['mail.template'].browse(template_id).generate_email([])
                        values['attachment_ids'] = [(6, 0, [ir_attachment])]
                        values['subject']="Monthly Profitability Report for "+(datetime.now()- relativedelta(months=1)).strftime('%B-%Y')
                        values['email_to'] = dd.mail_id
                        values['body_html'] = message
                        mail_mail_obj = self.env['mail.mail']
                        msg_id = mail_mail_obj.create(values)
                        if msg_id:
                            msg_id.send()
                            
        else:
            if template_id:  
                values = self.env['mail.template'].browse(template_id).generate_email([])
                values['attachment_ids'] = [(6, 0, [ir_attachment])]
                values['subject']="Monthly Profitability Report for "+(datetime.now()- relativedelta(months=1)).strftime('%B-%Y')
                mail_mail_obj = self.env['mail.mail']
                msg_id = mail_mail_obj.create(values)
                if msg_id:
                    msg_id.send()
                            
                            
                            
                            
class cols_profit_data(models.Model):
    _name = 'cols.profit.data'

    partner_id=fields.Many2one('res.partner','Customer Name')
    cust_inv=fields.Float('Amount Invoiced-Customer (A)')
    cust_rec=fields.Float('Amount Received-Customer')
    supp_inv=fields.Float('Amount Invoiced-Vendor (B)')
    supp_rec=fields.Float('Amount Paid-Vendor')
    event_count=fields.Integer('Event Count')
    invoice_cnt=fields.Integer('Invoice Count')
    total_income=fields.Float('Profit (A - B)')
    gp=fields.Float('GP%')
    cust_profit=fields.Many2one('profit.based.on.cust','Cust Profit')


# Detailed Cancellation report

class detailed_cancel_report(models.Model):
    _name = 'detailed.cancel.report'

    @api.model
    def _get_year(self):
        ''' this Function gets Current Year on the basis of users timezone '''
        user = self.env.user
        tz = False
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.timezone("US/Pacific") or pytz.utc
        localized_datetime = pytz.utc.localize(datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),"%Y-%m-%d %H:%M:%S")).astimezone(tz)
        localized_datetime = localized_datetime.replace(tzinfo=None)
        return str(datetime.strptime(str(localized_datetime), "%Y-%m-%d %H:%M:%S").timetuple().tm_year)

    @api.model
    def _get_mnt(self):
            ''' this Function gets Current month on the basis of users timezone '''
            return str(datetime.now().strftime('%-m'))
        
#     def _get_default_reason(self, cr, uid, context=None):
#         res = self.pool.get('cancel.reason').search(cr, uid, [('name','=','No interpreter available')], context=context)
#         for data in res:
#             return res[1] or False
    

    year=fields.Char('Current Year',required=True,default=_get_year)
    month_name=fields.Selection([('1','January'), ('2','February'), ('3','March'), ('4','April'), ('5','May'), ('6','June'),
                ('7','July'), ('8','August'), ('9','September'), ('10','October'), ('11','November'), ('12','December')],
                                   string='Month', index=True, required=True,default=_get_mnt)
    partner_id=fields.Many2one("res.partner",'Customer Name')
    cancel_reason_id=fields.Many2one('cancel.reason', 'Cancel Reason',)
    company_id=fields.Many2one('res.company','Company Name',required=True,default=lambda self: self.env['res.company']._company_default_get('detailed.cancel.report'))
    cols_lines=fields.One2many('cols.detailed.cancel.report','detail_report_id', 'Cols Lines')


    @api.onchange('company_id')
    def onchange_company_id(self):
        ''' Empty some fields on change of company in the event Form '''
        res = self.env['cancel.reason'].search([('name','=','No interpreter available'),('company_id','=',self.company_id.id) ])
        val = {
            'partner_id': False ,
            'cancel_reason_id':res,
        }
        return {'value': val}
    
    @api.multi
    def search_details(self):
        cur_obj = self
        cols_lines = cur_obj.cols_lines
        cols_lines.unlink()
        year = "'" + cur_obj.year + "'"
        month = "'"+cur_obj.month_name+"'"
        company_id = cur_obj.company_id.id
        
        query="""
                SELECT event.name, event.company_id,event.event_start_date, cancel_reason.name,
                event.partner_id,event.contact_id,event.ordering_partner_id,event.ordering_contact_id
                FROM event INNER JOIN cancel_reason ON (event.cancel_reason_id = cancel_reason.id)
                where month=%s and year = %s and event.company_id = %s and state='cancel'"""%(month,year,str(company_id))
        
        where = ""
 
        if cur_obj.cancel_reason_id and cur_obj.cancel_reason_id.id != False and not cur_obj.partner_id:
            where+= " and event.cancel_reason_id = "+str(cur_obj.cancel_reason_id.id)

        elif cur_obj.partner_id and cur_obj.cancel_reason_id.id == False:
            where+= " and event.partner_id ="+str(cur_obj.partner_id.id)
        elif cur_obj.cancel_reason_id and cur_obj.partner_id:
            where+= "and event.partner_id ="+str(cur_obj.partner_id.id) + " and event.cancel_reason_id = "+str(cur_obj.cancel_reason_id.id)
            
        self._cr.execute(query+where+";")
        data = self._cr.fetchall()
        if not data:
            raise UserError(_('No data available for selected filters'))
        else:
            for res in data:
                self.write({'cols_lines': [(0, False, {'event_id':res[0],'partner_id':res[4],
                                            'contact_id':res[5],'order_partner_id':res[6],'order_contact_id':res[7],
                                            'event_start_date':res[2],'cancel_reason':res[3],})]})
             
        return True

    @api.multi
    def print_xls_report(self):
        self.search_details()
        cur_obj = self
        M_header_tstyle = format_common.font_style(position='center', bold=1, border=1, fontos='black', font_height=400)
        header_tstyle_c = format_common.font_style(position='center', bold=1, border=1, fontos='black', font_height=150, color='grey')
        other_tstyle_c = format_common.font_style(position='center', fontos='black', font_height=200)  
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('Detailed Cancellation Report')
        sheet.row(0).height = 256 * 3
        sheet.normal_magn=120
        
        
        sheet.write_merge(0,0,0,4, 'Report for : '+cur_obj.company_id.name, header_tstyle_c)
        
#         sheet.write(2,0, 'Company Name: '+cur_obj.company_id.name, header_tstyle_c)
#         sheet.write(2,1, 'Year : '+cur_obj.year, header_tstyle_c)
#         sheet.write(2,2, 'Month : '+cur_obj.month_name, header_tstyle_c)
#         if cur_obj.cancel_reason_id and cur_obj.cancel_reason_id.id != False:
#             sheet.write(2,3, 'Cancel Reason : '+cur_obj.cancel_reason_id.name, header_tstyle_c)
#         if cur_obj.partner_id and cur_obj.partner_id.id != False:
#             sheet.write(2,4, 'Partner Name : '+cur_obj.partner_id.name, header_tstyle_c)
#         
        row = 5
        sheet.write(row, 0, 'Event Id', header_tstyle_c)
        sheet.write(row, 1, 'Event Date',header_tstyle_c )
        sheet.write(row, 2, 'Billing Customer',header_tstyle_c )
        sheet.write(row, 3, 'Billing Contact', header_tstyle_c)
        sheet.write(row, 4, 'Ordering Customer', header_tstyle_c)
        sheet.write(row, 5, 'Ordering Contact', header_tstyle_c)
        sheet.write(row, 6, 'Cancel Reason', header_tstyle_c)
        
        
        row = 6
        for data in  cur_obj.cols_lines:
            sheet.write(row,0,data.event_id,other_tstyle_c)
            sheet.write(row,1,data.event_start_date,other_tstyle_c)
            sheet.write(row,2,data.partner_id.name,other_tstyle_c)
            sheet.write(row,3,data.contact_id.name,other_tstyle_c)
            sheet.write(row,4,data.order_partner_id.name,other_tstyle_c)
            sheet.write(row,5,data.order_contact_id.name,other_tstyle_c)
            sheet.write(row,6,data.cancel_reason,other_tstyle_c)
            row +=1

        
        stream = cStringIO.StringIO()
        workbook.save(stream)
        attach_id = self.env['print.xls.cols'].create({'name':'Event Cancellation Report.xls', 'xls_output':base64.encodestring(stream.getvalue())})
        return {
            'name': ('Notification'),
            'context': self._context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'print.xls.cols',
            'res_id': attach_id.id,
            'type': 'ir.actions.act_window',
            'target':'new'
        }
 
        
        

class cols_detailed_cancel_report(models.Model):
    _name = 'cols.detailed.cancel.report'

    event_id=fields.Char('Event Id')
    partner_id=fields.Many2one('res.partner','Billing Customer')
    contact_id=fields.Many2one('res.partner','Billing Contact')
    order_partner_id=fields.Many2one('res.partner','Ordering Customer')
    order_contact_id=fields.Many2one('res.partner','Ordering Contact')
    event_start_date=fields.Char('Event Date')
    cancel_reason=fields.Char('Cancel Reason')
    location=fields.Char('Location')
    detail_report_id=fields.Many2one('detailed.cancel.report', 'Cancel Report Id')

class cols_interpreter_details(models.TransientModel):
    _name = 'cols.interpreter.details'

    first_name=fields.Char('First Name')
    last_name=fields.Char('Last Name')
    address_one=fields.Char('Address1')
    address_two=fields.Char('Address2')
    city=fields.Char('City')
    state=fields.Char('State')
    zip=fields.Char('Zip Code')
    ssnid=fields.Char('SSN-No')
    sinid=fields.Char('Social Insurance',)
    vat=fields.Char('VAT')
    email=fields.Char('Email')
    language_id=fields.Many2one("language",'Language Spoken')
    interpreter_profile_id=fields.Integer("Interpreter Profile")
    interpreter_data=fields.Many2one("interpreters.details",'Interpereter Data')

    @api.multi
    def get_interpreter_id(self):
        view_ref = self.env['ir.model.data'].sudo().get_object_reference('bista_iugroup','view_interpreter_form')
        view_id = view_ref and view_ref[1] or False,
        return {
               'type': 'ir.actions.act_window',
               'name': 'Form heading',
               'view_mode': 'form',
               'view_type': 'form',
               'view_id': view_id,
               'res_model': 'res.partner',
               'nodestroy': False,
               'res_id': int(self.interpreter_profile_id),
               'target':'current',
               'context': self._context,
        }
   

    
class interpreters_details(models.Model):
    _name = 'interpreters.details'
    _rec_name = 'cname'

    cname=fields.Char(related="company_id.name",index=True)
    company_id=fields.Many2one("res.company","Company Name",default=lambda self: self.env['res.company']._company_default_get('interpreters.details'))
    interperter_id=fields.Many2one("res.partner",'Interpreter Name')
    state_id=fields.Many2one("res.country.state",'State')
    language_id=fields.Many2one("language",'Language')
    certificate_level=fields.Many2one("certification.level","Certification Level")
    city=fields.Char("City",size=40)
    cols_interpreter_data=fields.One2many("cols.interpreter.details",'interpreter_data')

    @api.onchange('company_id')
    def onchange_company_id(self):
        ''' Empty some fields on change of company in the event Form '''
        res_int = self.env['res.partner'].search([('company_id','=',self.company_id.id),('cust_type','=','interpreter')]).ids
        res_lang = self.env['language'].search([('company_id','=',self.company_id.id)]).ids
        res_certify = self.env['certification.level'].search([('company_id','=',self.company_id.id)]).ids
        res = {'domain':
                {'interperter_id':[('id', 'in', res_int)],
                'language_id':[('id', 'in', res_lang)],
                'certificate_level':[('id', 'in', res_certify)]},
               'value':{
                        'interperter_id':False,'language_id':False,'certificate_level':False
                    }
            }
        return res

    @api.multi
    def get_interperter_info(self):
        cur_obj = self
        analysis_lines = cur_obj.cols_interpreter_data
        analysis_lines.unlink()
        
        query= """SELECT  r.name, r.last_name, r.street, r.street2, r.city,s.name, r.zip, r.ssnid, r.sinid, r.vat, r.email, l.id, r.id
            FROM interpreter_language i, res_partner r, language l, res_country_state s
            WHERE i.interpreter_id = r.id and l.id= i.name 
            and s.id = r.state_id
            and r.cust_type='interpreter' """
        where = ""
        where += " and r.company_id="+str(cur_obj.company_id.id)  
        if cur_obj.interperter_id:
            where += " and r.id="+str(cur_obj.interperter_id.id)
        if cur_obj.state_id:
            where += " and r.state_id="+str(cur_obj.state_id.id)
        if cur_obj.city:
            where += " and upper(r.city) = "+str("'"+cur_obj.city.upper()+"'")
        if cur_obj.language_id:
            where += " and l.id="+str(cur_obj.language_id.id)
        if cur_obj.certificate_level:
            where += " and i.certification_level_id="+str(cur_obj.certificate_level.id)
            
        self._cr.execute(query+where)
        data = self._cr.fetchall()
        if not data:
            raise UserError(_('No data available for selected filters'))
        else:
            for res in data:
                self.write({'cols_interpreter_data': [(0, False, {'first_name':res[0],'last_name':res[1],
                                            'address_one':res[2],'address_two':res[3],'city':res[4],
                                            'state':res[5],'zip':res[6],'ssnid':res[7],'sinid':res[8],'vat':res[9],
                                            'email':res[10],'language_id':res[11],'interpreter_profile_id':res[12]})]})

        return True

    @api.multi
    def print_interpreter_data(self):
        cur_obj = self
        if not cur_obj.cols_interpreter_data:
            raise UserError(_('No data available for xls print'))
        
        M_header_tstyle = format_common.font_style(position='center', bold=1, border=1, fontos='black', font_height=400)
        header_tstyle_c = format_common.font_style(position='center', bold=1, border=1, fontos='black', font_height=150, color='grey')
        other_tstyle_c = format_common.font_style(position='center', fontos='black', font_height=200)  
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('Interpreters Details')
        sheet.row(0).height = 256 * 3
        
        cloumn_headers = ['First Name','Last Name','Address1','Address2','City','State','Zip Code','SSN-No','Social Insurance No',
                          'Vat','Email','Launguage Spoken']
        row = 0
        count = 0
        while (len(cloumn_headers) > count):
            for headers in cloumn_headers:
                sheet.write(row,count,headers,header_tstyle_c),
                count = count + 1
        
        row = 1
        for data in cur_obj.cols_interpreter_data:
            sheet.write(row,0,data.first_name or None,other_tstyle_c)
            sheet.write(row,1,data.last_name or None,other_tstyle_c)
            sheet.write(row,2,data.address_one or None,other_tstyle_c)
            sheet.write(row,3,data.address_two or None,other_tstyle_c)
            sheet.write(row,4,data.city or None,other_tstyle_c)
            sheet.write(row,5,data.state or None,other_tstyle_c)
            sheet.write(row,6,data.zip or None,other_tstyle_c)
            sheet.write(row,7,data.ssnid or None,other_tstyle_c)
            sheet.write(row,8,data.sinid or None,other_tstyle_c)
            sheet.write(row,9,data.vat or None,other_tstyle_c)
            sheet.write(row,10,data.email or None,other_tstyle_c)
            sheet.write(row,11,data.language_id.name or None,other_tstyle_c)
            row +=1
                
        stream = cStringIO.StringIO()
        workbook.save(stream)
        attach_id = self.env['print.xls.cols'].create({'name':cur_obj.company_id.name+' Interpreters Details.xls', 'xls_output':base64.encodestring(stream.getvalue())})
        return {
            'name': ('Notification'),
            'context': self._context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'print.xls.cols',
            'res_id': attach_id.id,
            'type': 'ir.actions.act_window',
            'target':'new'
        }
    
#     cr.execute(""" """)


class cols_profit_year_data(models.Model):
    _name = 'cols.profit.year.data'

    partner_id=fields.Many2one('res.partner', 'Customer Name')
    cust_inv=fields.Float('Year 1: Amount Invoiced-Customer (A)')
    supp_inv=fields.Float('Year 1: Amount Invoiced-Vendor (B)')
    event_count=fields.Integer('Year 1: Event Count')
    total_income=fields.Float('Year 1: Profit (A - B)')
    cust_inv_2=fields.Float('Year 2: Amount Invoiced-Customer (A)')
    supp_inv_2=fields.Float('Year 2: Amount Invoiced-Vendor (B)')
    event_count_2=fields.Integer('Year 2: Event Count')
    total_income_2=fields.Float('Year 2: Profit (A - B)')
    cust_profit_year=fields.Many2one('yearly.profit.analysis.report', 'Cust Profit')



class yearly_profit_analysis(models.Model):
    _name = 'yearly.profit.analysis.report'


    partner_id=fields.Many2one('res.partner', 'Select Customer')
    cols_profit_year=fields.One2many("cols.profit.year.data", 'cust_profit_year')
    company_id=fields.Many2one("res.company", "Company Id", required=True,default=lambda self: self.env['res.company']._company_default_get('yearly.profit.analysis.report'))
    year_1=fields.Many2one("account.fiscalyear", 'Year 1')
    year_2=fields.Many2one("account.fiscalyear", 'Year 2')
    month=fields.Selection(
            [('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'), ('05', 'May'), ('06', 'June'),
             ('07', 'July'), ('08', 'August'), ('09', 'September'), ('10', 'October'), ('11', 'November'),
             ('12', 'December')], string='Month')
    date_1 = fields.Selection(
            [('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'), ('05', '05'), ('06', '06'),
             ('07', '07'), ('08', '08'), ('09', '09'), ('10', '10'), ('11', '11'),
             ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'), ('16', '16'), ('17', '17'), ('18', '18'),
             ('19', '19'), ('20', '20'), ('21', '21'), ('22', '22'), ('23', '23'), ('24', '24'),
             ('25', '25'), ('26', '26'), ('27', '27'), ('28', '28'), ('29', '29'), ('30', '30'), ('31', '31')], string='Date 1')
    date_2 = fields.Selection(
            [('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'), ('05', '05'), ('06', '06'),
             ('07', '07'), ('08', '08'), ('09', '09'), ('10', '10'), ('11', '11'),
             ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'), ('16', '16'), ('17', '17'), ('18', '18'),
             ('19', '19'), ('20', '20'), ('21', '21'), ('22', '22'), ('23', '23'), ('24', '24'),
             ('25', '25'), ('26', '26'), ('27', '27'), ('28', '28'), ('29', '29'), ('30', '30'), ('31', '31')], string='Date 2')
    month_1 = fields.Selection(
        [('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'), ('05', 'May'), ('06', 'June'),
         ('07', 'July'), ('08', 'August'), ('09', 'September'), ('10', 'October'), ('11', 'November'),
         ('12', 'December')], string='Month 1')
    month_2 = fields.Selection(
        [('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'), ('05', 'May'), ('06', 'June'),
         ('07', 'July'), ('08', 'August'), ('09', 'September'), ('10', 'October'), ('11', 'November'),
         ('12', 'December')], string='Month 2')
    date_or_month = fields.Selection([('01', 'Date Range'), ('02', 'Month')], string='Select Date Range OR Month')

    @api.onchange('date_or_month')
    def change_date_or_month(self):
        self.date_1=False
        self.date_2=False
        self.month_1=False
        self.month_2=False
        self.month=False


    @api.multi
    def get_yearwise_data(self):
        cur_obj = self
        analysis_lines = cur_obj.cols_profit_year
        analysis_lines.unlink()

        self._cr.execute("""DELETE FROM yearly_profit_analysis_report
                         WHERE date(create_date) < date(CURRENT_TIMESTAMP AT TIME ZONE 'PDT' - INTERVAL '2 days'); """)

        y1_date_from = "'01-01-" + cur_obj.year_1.name + "'"
        y1_date_to = "'12-31-" + cur_obj.year_1.name + "'"
        y2_date_from = "'01-01-" + cur_obj.year_2.name + "'"
        y2_date_to = "'12-31-" + cur_obj.year_2.name + "'"
        if cur_obj.month:
            y1_date_from = "'"+ cur_obj.month +"-01-" + cur_obj.year_1.name + "'"
            y2_date_from = "'" + cur_obj.month + "-01-" + cur_obj.year_2.name + "'"
            y1_date_to="'"+(last_day_of_month(datetime.strptime(""+ cur_obj.month +"-01-" + cur_obj.year_1.name + "",'%m-%d-%Y')).strftime("%m-%d-%Y"))+"'"
            y2_date_to = "'"+(last_day_of_month(datetime.strptime("" + cur_obj.month + "-01-" + cur_obj.year_2.name + "", '%m-%d-%Y')).strftime('%m-%d-%Y'))+"'"
        if cur_obj.date_1 and cur_obj.date_2 and cur_obj.month_1 and cur_obj.month_2:
            y1_date_from = "'" + cur_obj.month_1 + "-" + cur_obj.date_1  + "-" + cur_obj.year_1.name + "'"
            y2_date_from = "'" + cur_obj.month_1 +  "-" + cur_obj.date_1  + "-" + cur_obj.year_2.name + "'"
            y1_date_to = "'" + cur_obj.month_2 + "-" + cur_obj.date_2  + "-" + cur_obj.year_1.name + "'"
            y2_date_to = "'" + cur_obj.month_2 + "-" + cur_obj.date_2  + "-" + cur_obj.year_2.name + "'"
        if cur_obj.partner_id.id:
            self._cr.execute("""
                select coalesce(year_1.y1_company_id,0),coalesce(year_1.y1_partner_id,year_2.y2_partner_id) as partner_id,
                coalesce(year_1.y1_cust,0) as CUST,coalesce(year_1.y1_supp,0) as SUPP,
                coalesce(year_1.y1_event_count,0) as EVENT_COUNT_1,coalesce(year_2.y2_cust,0) as CUST_2,
                coalesce(year_2.y2_supp,0) as SUPP_2,coalesce(year_2.y2_event_count,0) as EVENT_COUNT_2

            from (
                    (select coalesce(cust_invoice.company_id,supp_invoice.company_id) as y1_company_id,
                        coalesce(cust_invoice.partner_id,supp_invoice.partner_id) as y1_partner_id,
                        coalesce(cust_invoice.name,supp_invoice.name) as y1_partner_name,
                        CUST as y1_cust,SUPP as y1_supp,cust_invoice.no_of_events as y1_event_count
                    from(
                        select res_partner.company_id,res_partner.id as partner_id,res_partner.name,
                            sum (amount_total) as CUST,count(distinct event.id) as no_of_events,
                            count(account_invoice.id)
                        from res_partner inner join event on event.partner_id = res_partner.id
                            inner join account_invoice on account_invoice.id=event.cust_invoice_id
                            where event.event_start_date between %s and %s
                            group by res_partner.company_id, res_partner.id order by 2) as cust_invoice

                    inner join(
                        select res_partner.company_id,res_partner.id as partner_id, res_partner.name,
                            sum (amount_total) as SUPP,count(distinct event.id) as  no_of_events,
                            count(account_invoice.id)
                        from res_partner inner join event on event.partner_id = res_partner.id
                            inner join task_inv_rel on (event.id=task_inv_rel.event_id)
                            inner join account_invoice on (account_invoice.id=task_inv_rel.invoice_id)
                            where event.event_start_date between %s and %s and res_partner.id = %s
                            and res_partner.company_id = %s
                            group by res_partner.company_id, res_partner.id order by res_partner.id
                            ) as supp_invoice on (cust_invoice.partner_id=supp_invoice.partner_id)
                    ) as year_1

                full outer join

                    (select coalesce(cust_invoice.company_id,supp_invoice.company_id) as y2_company_id,
                        coalesce(cust_invoice.partner_id,supp_invoice.partner_id) as y2_partner_id,
                        coalesce(cust_invoice.name,supp_invoice.name) as y2_partner_name,
                        CUST as y2_cust,SUPP as y2_supp,cust_invoice.no_of_events as y2_event_count
                    from(
                        select res_partner.company_id,res_partner.id as partner_id,res_partner.name,
                            sum (amount_total) as CUST,count(distinct event.id) as no_of_events,
                            count(account_invoice.id)
                        from res_partner inner join event on event.partner_id = res_partner.id
                            inner join account_invoice on account_invoice.id=event.cust_invoice_id
                            where event.event_start_date between %s and %s
                            group by res_partner.company_id, res_partner.id order by 2) as cust_invoice
                    inner join(
                        select res_partner.company_id,res_partner.id as partner_id, res_partner.name,
                            sum (amount_total) as SUPP,count(distinct event.id) as  no_of_events,
                            count(account_invoice.id)
                        from res_partner inner join event on event.partner_id = res_partner.id
                            inner join task_inv_rel on (event.id=task_inv_rel.event_id)
                            inner join account_invoice on (account_invoice.id=task_inv_rel.invoice_id)
                            where event.event_start_date between %s and %s and res_partner.id = %s
                            and res_partner.company_id = %s
                            group by res_partner.company_id, res_partner.id order by res_partner.id
                            ) as supp_invoice on (cust_invoice.partner_id=supp_invoice.partner_id)
                    ) as year_2 on (y1_partner_id = y2_partner_id))
                """
                       % (y1_date_from, y1_date_to, y1_date_from, y1_date_to, cur_obj.partner_id.id,
                          cur_obj.company_id.id, y2_date_from, y2_date_to, y2_date_from, y2_date_to,
                          cur_obj.partner_id.id, cur_obj.company_id.id))

        else:
            self._cr.execute("""
                select coalesce(year_1.y1_company_id,0),coalesce(year_1.y1_partner_id,year_2.y2_partner_id) as partner_id,
                coalesce(year_1.y1_cust,0) as CUST,coalesce(year_1.y1_supp,0) as SUPP,
                coalesce(year_1.y1_event_count,0) as EVENT_COUNT_1,coalesce(year_2.y2_cust,0) as CUST_2,
                coalesce(year_2.y2_supp,0) as SUPP_2,coalesce(year_2.y2_event_count,0) as EVENT_COUNT_2

            from (
                    (select coalesce(cust_invoice.company_id,supp_invoice.company_id) as y1_company_id,
                        coalesce(cust_invoice.partner_id,supp_invoice.partner_id) as y1_partner_id,
                        coalesce(cust_invoice.name,supp_invoice.name) as y1_partner_name,
                        CUST as y1_cust,SUPP as y1_supp,cust_invoice.no_of_events as y1_event_count
                    from(
                        select res_partner.company_id,res_partner.id as partner_id,res_partner.name,
                            sum (amount_total) as CUST,count(distinct event.id) as no_of_events,
                            count(account_invoice.id)
                        from res_partner inner join event on event.partner_id = res_partner.id
                            inner join account_invoice on account_invoice.id=event.cust_invoice_id
                            where event.event_start_date between %s and %s
                            group by res_partner.company_id, res_partner.id order by 2) as cust_invoice

                    inner join(
                        select res_partner.company_id,res_partner.id as partner_id, res_partner.name,
                            sum (amount_total) as SUPP,count(distinct event.id) as  no_of_events,
                            count(account_invoice.id)
                        from res_partner inner join event on event.partner_id = res_partner.id
                            inner join task_inv_rel on (event.id=task_inv_rel.event_id)
                            inner join account_invoice on (account_invoice.id=task_inv_rel.invoice_id)
                            where event.event_start_date between %s and %s
                            and res_partner.company_id = %s
                            group by res_partner.company_id, res_partner.id order by res_partner.id
                            ) as supp_invoice on (cust_invoice.partner_id=supp_invoice.partner_id)
                    ) as year_1

                full outer join

                    (select coalesce(cust_invoice.company_id,supp_invoice.company_id) as y2_company_id,
                        coalesce(cust_invoice.partner_id,supp_invoice.partner_id) as y2_partner_id,
                        coalesce(cust_invoice.name,supp_invoice.name) as y2_partner_name,
                        CUST as y2_cust,SUPP as y2_supp,cust_invoice.no_of_events as y2_event_count
                    from(
                        select res_partner.company_id,res_partner.id as partner_id,res_partner.name,
                            sum (amount_total) as CUST,count(distinct event.id) as no_of_events,
                            count(account_invoice.id)
                        from res_partner inner join event on event.partner_id = res_partner.id
                            inner join account_invoice on account_invoice.id=event.cust_invoice_id
                            where event.event_start_date between %s and %s
                            group by res_partner.company_id, res_partner.id order by 2) as cust_invoice
                    inner join(
                        select res_partner.company_id,res_partner.id as partner_id, res_partner.name,
                            sum (amount_total) as SUPP,count(distinct event.id) as  no_of_events,
                            count(account_invoice.id)
                        from res_partner inner join event on event.partner_id = res_partner.id
                            inner join task_inv_rel on (event.id=task_inv_rel.event_id)
                            inner join account_invoice on (account_invoice.id=task_inv_rel.invoice_id)
                            where event.event_start_date between %s and %s
                            and res_partner.company_id = %s
                            group by res_partner.company_id, res_partner.id order by res_partner.id
                            ) as supp_invoice on (cust_invoice.partner_id=supp_invoice.partner_id)
                    ) as year_2 on (y1_partner_id = y2_partner_id))
                """
                       % (y1_date_from, y1_date_to, y1_date_from, y1_date_to, cur_obj.company_id.id,
                          y2_date_from, y2_date_to, y2_date_from, y2_date_to, cur_obj.company_id.id))

        data = self._cr.fetchall()
        if not data:
            raise UserError(_('No data available for selected filters'))
        else:
            for d in data:
                if cur_obj.company_id != None:
                    year1_profit = d[2] - d[3]
                    year2_profit = d[5] - d[6]
                    self.write({'cols_profit_year': [(0, False, {'partner_id': d[1], 'cust_inv': d[2],
                                                                               'supp_inv': d[3], 'event_count': d[4],
                                                                               'total_income': year1_profit,
                                                                               'cust_inv_2': d[5], 'supp_inv_2': d[6],
                                                                               'event_count_2': d[7],
                                                                               'total_income_2': year2_profit})]})
        return True

    @api.multi
    def print_profit_xls(self):
        self.get_yearwise_data()
        cur_obj = self

        # Styling of worksheet
        header_tstyle_c = format_common.font_style(position='center', bold=1, border=1, fontos='black',
                                                   font_height=150, color='grey')
        other_tstyle_c = format_common.font_style(position='center', fontos='black', font_height=200)
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('Profitability Report')
        sheet.row(0).height = 256 * 3

        row = 0
        sheet.write(row, 0, 'Customer Name', header_tstyle_c)
        sheet.write(row, 1, cur_obj.year_1.name + ': Event Count', header_tstyle_c)
        sheet.write(row, 2, cur_obj.year_1.name + ': Amount Invoiced(Customer)', header_tstyle_c)
        sheet.write(row, 3, cur_obj.year_1.name + ': Amount Invoiced(Vendor)', header_tstyle_c)
        sheet.write(row, 4, cur_obj.year_1.name + ': Profit', header_tstyle_c)
        sheet.write(row, 5, cur_obj.year_2.name + ': Event Count', header_tstyle_c)
        sheet.write(row, 6, cur_obj.year_2.name + ': Amount Invoiced(Customer)', header_tstyle_c)
        sheet.write(row, 7, cur_obj.year_2.name + ': Amount Invoiced(Vendor)', header_tstyle_c)
        sheet.write(row, 8, cur_obj.year_2.name + ': Profit', header_tstyle_c)

        row = 1
        for data in cur_obj.cols_profit_year:
            sheet.write(row, 0, data.partner_id.name, other_tstyle_c)
            sheet.write(row, 1, data.event_count, other_tstyle_c)
            sheet.write(row, 2, data.cust_inv, other_tstyle_c)
            sheet.write(row, 3, data.supp_inv, other_tstyle_c)
            sheet.write(row, 4, data.total_income, other_tstyle_c)
            sheet.write(row, 5, data.event_count_2, other_tstyle_c)
            sheet.write(row, 6, data.cust_inv_2, other_tstyle_c)
            sheet.write(row, 7, data.supp_inv_2, other_tstyle_c)
            sheet.write(row, 8, data.total_income_2, other_tstyle_c)
            row += 1

        stream = cStringIO.StringIO()
        workbook.save(stream)
        attach_id = self.env['print.xls.cols'].create({'name': 'Yearwise Profitability Analysis Report.xls',
                                                                     'xls_output': base64.encodestring(
                                                                         stream.getvalue())})
        return {
            'name': ('Notification'),
            'context': self._context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'print.xls.cols',
            'res_id': attach_id.id,
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

class cols_new_report_data(models.Model):
    _name = 'cols.new.report.data'

    partner_id = fields.Many2one('res.partner', 'Customer Name')
    prior_year = fields.Float('Prior YR MTD')
    current_year = fields.Float('Current YR YTD')
    change_rev = fields.Float('Change Rev')
    change_gp = fields.Float('Change GP')
    change_events = fields.Integer('Change Events')
    prior_year_total = fields.Float('% of Total Rev ( Prior YR )')
    current_year_total = fields.Float('% of Total Rev ( Current ')
    new_report_data = fields.Many2one('iug.new.report', 'New Report Data')

class iug_new_report(models.Model):
    _name = 'iug.new.report'

    partner_id = fields.Many2many('res.partner', string='Customer')
    all_customer = fields.Boolean(string='All Customer')
    cols_report_data = fields.One2many('cols.new.report.data', 'new_report_data')
    period_from=fields.Date("Period 1 From")
    period_to=fields.Date("Period 1 To")
    period2_from=fields.Date("Period 2 From")
    period2_to=fields.Date("Period 2 To")


    def get_report_data(self):
        partners = []

        last_year_date = datetime.strftime(datetime.now() - timedelta(365), '%Y-%m-%d')
        last_year = datetime.strptime(last_year_date, '%Y-%m-%d').date()
        last_start_date = date(int(last_year.strftime("%Y")), 1, 1)

        today_date = datetime.date(datetime.now())
        temp = today_date.strftime('%m/%d/%Y')
        iug_date_format = datetime.strptime(temp, '%m/%d/%Y').date()
        start_date_year = date(int(today_date.strftime("%Y")), 1, 1)
        start = start_date_year.strftime('%m/%d/%Y')
        temp = datetime.strptime(start, '%m/%d/%Y').date()
        # self.cols_report_data=False
        _logger.info('---------self.all_customer-----------%s', self.all_customer)
        if  self.all_customer:
            part_obj = self.env['res.partner'].sudo().search([('cust_type', '=', 'customer'), ('active' , '=', True)])
            for partner in part_obj:
                partners.append(partner)
            _logger.info('----------all partners-----------%s', partners)

            for partner in partners:
		_logger.info('----------1111111111111111 partners-----------%s', partner)
                self._cr.execute("""
                   	select res.name as CustomerName,(select count(ev.name) from event ev 
where ev.event_start_date BETWEEN '%s' AND '%s' AND ev.partner_id=%s) as LastYearEventCount,                                                                                               
(select count(ev.name) from event ev 
where ev.event_start_date BETWEEN '%s' AND '%s' AND ev.partner_id=%s) as CurrentYearEventCount,      
(select sum(acc.amount_total)  from event ev  inner join account_invoice acc  on acc.id=ev.cust_invoice_id AND ev.event_start_date BETWEEN '%s' AND '%s' AND acc.partner_id=%s AND ev.partner_id=%s) as PriorYRMTD,
(select sum(acc.amount_total)  from event ev  inner join account_invoice acc  on acc.id=ev.cust_invoice_id AND ev.event_start_date BETWEEN '%s' AND '%s' AND acc.partner_id=%s AND ev.partner_id=%s) as CurrentYRMTD,
(select ROUND(sum(acc.amount_total), 2)  from event ev  inner join account_invoice acc  on acc.id=ev.cust_invoice_id 
where ev.event_start_date BETWEEN '%s' AND '%s' AND acc.company_id=ev.company_id) as PreviousCompanytotal,  
(select ROUND(sum(acc.amount_total), 2)  from event ev  inner join account_invoice acc  on acc.id=ev.cust_invoice_id 
where ev.event_start_date BETWEEN '%s' AND '%s' AND acc.company_id=ev.company_id) as currentCompanytotal 
 from res_partner as res where res.id=%s;
                    """
                                % (last_start_date, last_year,partner.id,
                                    start_date_year, iug_date_format,partner.id,
                                    last_start_date, last_year,partner.id,partner.id,
                                    start_date_year, iug_date_format,partner.id,partner.id,
                                    last_start_date, last_year, partner,
                                    start_date_year, iug_date_format,
                                    partner.id
                                    ))
                data = self._cr.fetchall()
                if not data:
                    _logger.info('----------allnoiooooooooooooooooodatat>>>>>-----------%s',data)
                    pass
                else:
                    for d in data:
                            _logger.info('----------alldatat>>>>>-----------%s',d)
                            if d[2] and d[1]:
                                event_count = d[2] - d[1]
                            if d[4] and d[3]:
                                change_rev = d[4] - d[3]
                            # if d[5] != 0:
                            #     chng_gp = ((d[5] - d[6]) / d[5]) * 100
                            if d[3] != 0 or None and d[5] !=0:
                                previous_year_total = (d[3] / d[5]) * 100
                            if d[4] != 0 and d[6] !=0:
                                current_year_total = (d[4] / d[6]) * 100
                            self.write({'cols_report_data': [(0, False, {'partner_id': d[1] or 0.0,
                                                                         'prior_year': d[3] or 0.0,
                                                                         'current_year': d[4] or 0.0,
                                                                         'change_rev': change_rev or 0.0,
                                                                         'change_gp': 0.0,
                                                                         'change_events': event_count or 0.0,
                                                                         'prior_year_total': previous_year_total or 0.0,
                                                                         'current_year_total': current_year_total or 0.0})]})

        elif self.partner_id:
            for partner in self.partner_id:
                partners.append(partner)
            _logger.info('----------partners-----------%s',partners)
            last_year_date = datetime.strftime(datetime.now() - timedelta(365), '%Y-%m-%d')
            # last_year = datetime.strptime(last_year_date, '%Y-%m-%d').date()
            last_year = self.period2_to
            # last_start_date = datetime(int(last_year.strftime("%Y")), 1, 1)
            last_start_date = self.period2_from

            today_date = datetime.date(datetime.now())
            temp = today_date.strftime('%m/%d/%Y')
            # iug_date_format = datetime.strptime(temp, '%m/%d/%Y').date()
            iug_date_format = self.period_to
            # start_date_year = datetime(int(today_date.strftime("%Y")), 1, 1)
            start_date_year = self.period_from


            # curr_event_obj = self.env['event'].sudo().search(['&', ('partner_id','=',partner.id), ('event_start_date', '>=', start_date_year), ('event_start_date', '<=', iug_date_format)])
            # previous_event_obj = self.env['event'].sudo().search(['&', ('partner_id','=',partner.id), ('event_start_date', '>=', last_start_date), ('event_start_date', '<=', last_year)])

            for partner in partners:
                curr_event_obj = self.env['event'].sudo().search(['&', ('partner_id', '=', partner.id), ('event_start_date', '>=', start_date_year),('event_start_date', '<=', iug_date_format)])
                previous_event_obj = self.env['event'].sudo().search(['&', ('partner_id', '=', partner.id), ('event_start_date', '>=', last_start_date),('event_start_date', '<=', last_year)])
                curr_event_total = 0
                curr_event_count = 0
                previous_event_total = 0
                previous_event_count = 0
                change_rev = 0
                change_gp = 0
                change_gp_current = 0
                change_gp_prev = 0
                change_event = 0
                curr_inv_total = 0
                prev_inv_total = 0
                previous_year_total = 0
                current_year_total = 0
                curr_bill_comp_tot = 0
                prv_bill_comp_tot = 0
                for curr in curr_event_obj:
                    curr_event_total += curr.cust_invoice_id.amount_total
                    curr_event_count += 1
                _logger.info('----------current event total-----------%s', curr_event_total)
                _logger.info('----------current event count-----------%s', curr_event_count)
                for previous in previous_event_obj:
                    previous_event_total += previous.cust_invoice_id.amount_total
                    previous_event_count += 1
                _logger.info('----------previous event total-----------%s', previous_event_total)
                _logger.info('----------previous event count-----------%s', previous_event_count)
                for curr_inv in curr_event_obj:
                    curr_inv_total += curr_inv.view_interpreter_inv.amount_total
                _logger.info('----------current inv total-----------%s', curr_inv_total)
                for prev_inv in previous_event_obj:
                    prev_inv_total += prev_inv.view_interpreter_inv.amount_total
                change_rev = curr_event_total - previous_event_total
                change_event = curr_event_count - previous_event_count
                if curr_event_total != 0:
                    change_gp_current = ((curr_event_total - curr_inv_total)/curr_event_total)*100
                    _logger.info('----------change_gp_current-----------%s', change_gp_current)
                if previous_event_total != 0:
                    change_gp_prev = ((previous_event_total - prev_inv_total)/previous_event_total)*100
                    _logger.info('----------change_gp_prev-----------%s', change_gp_prev)
                if change_gp_current or change_gp_prev:
                    change_gp=change_gp_current-change_gp_prev
                _logger.info('----------change gp-----------%s', change_gp)
                curr_bill_comp = self.env['account.invoice'].sudo().search(['&', ('company_id','=',partner.company_id.id), ('date_invoice', '>=', start_date_year),('date_invoice', '<=', iug_date_format)])
                prv_bill_comp = self.env['account.invoice'].sudo().search(['&', ('company_id','=',partner.company_id.id), ('date_invoice', '>=', last_start_date),('date_invoice', '<=', last_year)])
                for x in curr_bill_comp:
                    curr_bill_comp_tot += x.amount_total
                _logger.info('----------curr bill comp total-----------%s', curr_bill_comp_tot)
                for x in prv_bill_comp:
                    prv_bill_comp_tot += x.amount_total
                if  curr_bill_comp_tot != 0:
                    current_year_total = (curr_event_total / curr_bill_comp_tot)*100
                if  prv_bill_comp_tot != 0:
                    previous_year_total = (previous_event_total / prv_bill_comp_tot)*100

                vals={'cols_report_data': [(0, 0, {'partner_id': partner.id,
                                                         'prior_year': previous_event_total,
                                                         'current_year': curr_event_total,
                                                         'change_rev': change_rev,
                                                         'change_gp': change_gp,
                                                         'change_events': change_event,
                                                         'prior_year_total': previous_year_total,
                                                         'current_year_total': current_year_total,
                                                  })]}
                _logger.info('----------vals-----------%s', vals)
                self.write(vals)
                self._cr.commit()
        return  True

    @api.multi
    def print_profit_xls(self):
        self.get_report_data()
        cur_obj = self
        current_date = datetime.now()
        current_year = current_date.year
        previous_year = current_year-1

        # Styling of worksheet
        header_tstyle_c = format_common.font_style(position='center', bold=1, border=1, fontos='black',
                                                   font_height=150, color='grey')
        other_tstyle_c = format_common.font_style(position='center', fontos='black', font_height=200)
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('Revenue Report')
        sheet.row(0).height = 256 * 3

        row = 0
        sheet.write(row, 0, 'Customer Name', header_tstyle_c)
        sheet.write(row, 1, str(previous_year) + ': Prior YR MTD', header_tstyle_c)
        sheet.write(row, 2, str(current_year) + ':  Current YR YTD', header_tstyle_c)
        sheet.write(row, 3, str(previous_year)+'-'+ str(current_year) + ': Change Rev', header_tstyle_c)
        sheet.write(row, 4, str(previous_year)+'-'+ str(current_year) + ':  Change GP.', header_tstyle_c)
        sheet.write(row, 5, str(previous_year)+'-'+ str(current_year) + ':  Change Events', header_tstyle_c)
        sheet.write(row, 6, str(previous_year)+ ':  % of Total Rev ( Prior YR )', header_tstyle_c)
        sheet.write(row, 7, str(current_year) + ':  % of Total Rev ( Current )', header_tstyle_c)

        row = 1
        for data in cur_obj.cols_report_data:
            sheet.write(row, 0, data.partner_id.name, other_tstyle_c)
            sheet.write(row, 1, data.prior_year, other_tstyle_c)
            sheet.write(row, 2, data.current_year, other_tstyle_c)
            sheet.write(row, 3, data.change_rev, other_tstyle_c)
            sheet.write(row, 4, round(data.change_gp, 2), other_tstyle_c)
            sheet.write(row, 5, data.change_events, other_tstyle_c)
            sheet.write(row, 6, round(data.prior_year_total, 2), other_tstyle_c)
            sheet.write(row, 7, round(data.current_year_total, 2), other_tstyle_c)
            row += 1

        stream = cStringIO.StringIO()
        workbook.save(stream)
        attach_id = self.env['print.xls.cols'].create({'name': 'Yearwise New Analysis Report.xls',
                                                       'xls_output': base64.encodestring(
                                                           stream.getvalue())})
        return {
            'name': ('Notification'),
            'context': self._context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'print.xls.cols',
            'res_id': attach_id.id,
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
