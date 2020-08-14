import pytz
from odoo import fields,models,api
from odoo.tools.translate import _
# from openerp.tools import flatten
import datetime
from odoo import SUPERUSER_ID
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import time
from dateutil.relativedelta import relativedelta
import calendar
from odoo.exceptions import UserError


class iug_dashboard(models.Model):
    _name='iug.dashboard'

    name=fields.Char('Name')
    start_date= fields.Date("Start date", )
    end_date=fields.Date("End date", )
    lastmonth=fields.Many2many('iug.dashboard.lastmonth','lastmonth_rel','dashboard_wizard_id','lastmonth_id','Last Month Event Results')
    currentmonth=fields.Many2many('iug.dashboard.currentmonth','currentmonth_rel','dashboard_wizard_id','currentmonth_id','Current Month Event Results')
    futuremonth=fields.Many2many('iug.dashboard.futuremonth','futuremonth_rel','dashboard_wizard_id','futuremonth_id','Future Month Event Results')
    rangemonth=fields.Many2many('iug.dashboard.rangemonth','rangemonth_rel','dashboard_wizard_id','rangemonth_id','Range Month Event Results')
    rangemonth_flag=fields.Boolean('Range Month Flag',default=True)

    @api.model
    def default_get(self, fields):
        '''set default dashboard values'''
        #Clean up the many2many entries intially to reduce database load factor
        self._cr.execute('''truncate lastmonth_rel, currentmonth_rel , futuremonth_rel ''')
        
        result = super(iug_dashboard, self).default_get(fields)
        cols=['acd','albors_alnet','asit','iug_sd','options']
        ##############################Past events details############################
        lastmonth_ids, currentmonth_ids, futuremonth_ids =[], [], []
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        user = self.env.user
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.utc
        current_date = tz.localize(datetime.datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),DATETIME_FORMAT), is_dst=None)
        current_date1 = datetime.datetime.strptime(current_date.astimezone (tz).strftime(DATETIME_FORMAT), DATETIME_FORMAT)
        current_date = current_date1.strftime('%Y-%m-%d')
        print "current_date.........",current_date
#        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        previous_day = current_date1 - datetime.timedelta(days=30)
        previous_month = previous_day.strftime('%Y-%m')+ '-01'
        
        #Last month events#
        #cr.execute('''select count(id) from event where event_start_0date BETWEEN %s AND %s ''',(previous_month,current_date))
        
        vals={}
        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='ACD' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",(previous_month,current_date))\
        ;prev_total_event = self._cr.fetchall();[vals.update({'acd':str(i[1])}) for i in prev_total_event] if prev_total_event else vals.update({'acd':'0'})
        
        
        
        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='Albors And Alnet' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",(previous_month,current_date))\
        ;prev_total_event = self._cr.fetchall();[vals.update({'albors_alnet':str(i[1])}) for i in prev_total_event] if prev_total_event else vals.update({'albors_alnet':'0'})
        
        
        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='ASIT' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",(previous_month,current_date))\
        ;prev_total_event = self._cr.fetchall();[vals.update({'asit':str(i[1])}) for i in prev_total_event] if prev_total_event else vals.update({'asit':'0'})
        
        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='IUG-SD' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",(previous_month,current_date))\
        ;prev_total_event = self._cr.fetchall();[vals.update({'iug_sd':str(i[1])}) for i in prev_total_event] if prev_total_event else vals.update({'iug_sd':'0'})
        
        vals.update({'options':'total_event'});last_id=self.env['iug.dashboard.lastmonth'].create(vals).id;lastmonth_ids.append(last_id)
       
        
#Unbilled Events#   
        vals={}    
        
#         cr.execute("select count(id) from event where state='unbilled' and event_start_date BETWEEN %s AND %s ",(previous_month,current_date))
#         prev_unbilled_event = cr.fetchone()

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='ACD' and event.state='unbilled' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",(previous_month,current_date))\
        ;prev_unbilled_event = self._cr.fetchall();[vals.update({'acd':str(i[1])}) for i in prev_unbilled_event] if prev_unbilled_event else vals.update({'acd':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='Albors And Alnet' and event.state='unbilled' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",(previous_month,current_date))\
        ;prev_unbilled_event = self._cr.fetchall();[vals.update({'albors_alnet':str(i[1])}) for i in prev_unbilled_event] if prev_unbilled_event else vals.update({'albors_alnet':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='ASIT' and event.state='unbilled' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",(previous_month,current_date))\
        ;prev_unbilled_event = self._cr.fetchall();[vals.update({'asit':str(i[1])}) for i in prev_unbilled_event] if prev_unbilled_event else vals.update({'asit':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='IUG-SD' and event.state='unbilled' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",(previous_month,current_date))\
        ;prev_unbilled_event = self._cr.fetchall();[vals.update({'iug_sd':str(i[1])}) for i in prev_unbilled_event] if prev_unbilled_event else vals.update({'iug_sd':'0'})

        vals.update({'options':'ubilled'});last_id=self.env['iug.dashboard.lastmonth'].create(vals).id;lastmonth_ids.append(last_id)


#Invoiced Events
        vals={}
        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='ACD' and event.state='invoiced' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",(previous_month,current_date))\
        ;prev_invoiced_event = self._cr.fetchall();[vals.update({'acd':str(i[1])}) for i in prev_invoiced_event] if prev_invoiced_event else vals.update({'acd':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='Albors And Alnet' and event.state='invoiced' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",(previous_month,current_date))\
        ;prev_invoiced_event = self._cr.fetchall();[vals.update({'albors_alnet':str(i[1])}) for i in prev_invoiced_event] if prev_invoiced_event else vals.update({'albors_alnet':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='ASIT' and event.state='invoiced' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",(previous_month,current_date))\
        ;prev_invoiced_event = self._cr.fetchall();[vals.update({'asit':str(i[1])}) for i in prev_invoiced_event] if prev_invoiced_event else vals.update({'asit':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='IUG-SD' and event.state='invoiced' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",(previous_month,current_date))\
        ;prev_invoiced_event = self._cr.fetchall();[vals.update({'iug_sd':str(i[1])}) for i in prev_invoiced_event] if prev_invoiced_event else vals.update({'iug_sd':'0'})

        vals.update({'options':'invoiced'});last_id=self.env['iug.dashboard.lastmonth'].create(vals).id;lastmonth_ids.append(last_id)


        
#         if prev_unbilled_event: 
#             for i in prev_unbilled_event:
#                 i=str(i)
#                 
#                 vals={'acd':i,'albors_alnet':i,'asit':i,'iug_sd':i,'options':'ubilled'}
#                 last_id=self.pool.get('iug.dashboard.lastmonth').create(cr,uid,vals)
#                 lastmonth_ids.append(last_id)
#         #Invoiced Events
#         cr.execute("select count(id) from event where state='invoiced' and event_start_date BETWEEN %s AND %s ",(previous_month,current_date))
#         prev_invoiced_event = cr.fetchone()   
#         if prev_invoiced_event:
#             for i in prev_invoiced_event:
#                 i=str(i)
#                 vals={'acd':i,'albors_alnet':i,'asit':i,'iug_sd':i,'options':'invoiced'}
#                 last_id=self.pool.get('iug.dashboard.lastmonth').create(cr,uid,vals)
#                 lastmonth_ids.append(last_id)                
#                 

        ##############################Past events details Ends############################
        
        
        ##############################Current events details############################
        
#unschedule event

        vals={}
        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='ACD' and event.state='draft' and event.event_start_date =%s group by res_company.id ",(current_date,))\
        ;current_unscheduled_event = self._cr.fetchall();[vals.update({'acd':str(i[1])}) for i in current_unscheduled_event] if current_unscheduled_event else vals.update({'acd':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='Albors And Alnet' and event.state='draft' and event.event_start_date =%s group by res_company.id ",(current_date,))\
        ;current_unscheduled_event = self._cr.fetchall();[vals.update({'albors_alnet':str(i[1])}) for i in current_unscheduled_event] if current_unscheduled_event else vals.update({'albors_alnet':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='ASIT' and event.state='draft' and event.event_start_date =%s group by res_company.id ",(current_date,))\
        ;current_unscheduled_event = self._cr.fetchall();[vals.update({'asit':str(i[1])}) for i in current_unscheduled_event] if current_unscheduled_event else vals.update({'asit':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='IUG-SD' and event.state='draft' and event.event_start_date =%s group by res_company.id ",(current_date,))\
        ;current_unscheduled_event = self._cr.fetchall();[vals.update({'iug_sd':str(i[1])}) for i in current_unscheduled_event] if current_unscheduled_event else vals.update({'iug_sd':'0'})

        vals.update({'options':'draft'});last_id=self.env['iug.dashboard.currentmonth'].create(vals).id;currentmonth_ids.append(last_id)

#scedule event

        vals={}
        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='ACD' and event.state='scheduled' and event.event_start_date =%s group by res_company.id ",(current_date,))\
        ;current_scheduled_event = self._cr.fetchall();[vals.update({'acd':str(i[1])}) for i in current_scheduled_event] if current_scheduled_event else vals.update({'acd':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='Albors And Alnet' and event.state='scheduled' and event.event_start_date =%s group by res_company.id ",(current_date,))\
        ;current_scheduled_event = self._cr.fetchall();[vals.update({'albors_alnet':str(i[1])}) for i in current_scheduled_event] if current_scheduled_event else vals.update({'albors_alnet':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='ASIT' and event.state='scheduled' and event.event_start_date =%s group by res_company.id ",(current_date,))\
        ;current_scheduled_event = self._cr.fetchall();[vals.update({'asit':str(i[1])}) for i in current_scheduled_event] if current_scheduled_event else vals.update({'asit':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='IUG-SD' and event.state='scheduled' and event.event_start_date =%s group by res_company.id ",(current_date,))\
        ;current_scheduled_event = self._cr.fetchall();[vals.update({'iug_sd':str(i[1])}) for i in current_scheduled_event] if current_scheduled_event else vals.update({'iug_sd':'0'})

        vals.update({'options':'scheduled'});last_id=self.env['iug.dashboard.currentmonth'].create(vals).id;currentmonth_ids.append(last_id)

#confirmed Events
        vals={}
        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='ACD' and event.state='confirmed' and event.event_start_date =%s group by res_company.id ",(current_date,))\
        ;current_confirmed_event = self._cr.fetchall();[vals.update({'acd':str(i[1])}) for i in current_confirmed_event] if current_confirmed_event else vals.update({'acd':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='Albors And Alnet' and event.state='confirmed' and event.event_start_date =%s group by res_company.id ",(current_date,))\
        ;current_confirmed_event = self._cr.fetchall();[vals.update({'albors_alnet':str(i[1])}) for i in current_confirmed_event] if current_confirmed_event else vals.update({'albors_alnet':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='ASIT' and event.state='confirmed' and event.event_start_date =%s group by res_company.id ",(current_date,))\
        ;current_confirmed_event = self._cr.fetchall();[vals.update({'asit':str(i[1])}) for i in current_confirmed_event] if current_confirmed_event else vals.update({'asit':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='IUG-SD' and event.state='confirmed' and event.event_start_date =%s group by res_company.id ",(current_date,))\
        ;current_confirmed_event = self._cr.fetchall();[vals.update({'iug_sd':str(i[1])}) for i in current_confirmed_event] if current_confirmed_event else vals.update({'iug_sd':'0'})

        vals.update({'options':'confirmed'});last_id=self.env['iug.dashboard.currentmonth'].create(vals).id;currentmonth_ids.append(last_id)

#total event
         
        vals={}

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='ACD' and event.event_start_date = %s group by res_company.id ",(current_date,))\
        ;prev_total_event = self._cr.fetchall();[vals.update({'acd':str(i[1])}) for i in prev_total_event] if prev_total_event else vals.update({'acd':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='Albors And Alnet' and event.event_start_date =%s group by res_company.id ",(current_date,))\
        ;prev_total_event = self._cr.fetchall();[vals.update({'albors_alnet':str(i[1])}) for i in prev_total_event] if prev_total_event else vals.update({'albors_alnet':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='ASIT' and event.event_start_date =%s group by res_company.id ",(current_date,))\
        ;prev_total_event = self._cr.fetchall();[vals.update({'asit':str(i[1])}) for i in prev_total_event] if prev_total_event else vals.update({'asit':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='IUG-SD' and event.event_start_date =%s group by res_company.id ",(current_date,))\
        ;prev_total_event = self._cr.fetchall();[vals.update({'iug_sd':str(i[1])}) for i in prev_total_event] if prev_total_event else vals.update({'iug_sd':'0'})
        
        vals.update({'options':'total_event'});last_id=self.env['iug.dashboard.currentmonth'].create(vals).id;currentmonth_ids.append(last_id)
        
        
        
        
#Unbilled Events#   
        vals={}    
        
#         cr.execute("select count(id) from event where state='unbilled' and event_start_date BETWEEN %s AND %s ",(previous_month,current_date))
#         prev_unbilled_event = cr.fetchone()

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='ACD' and event.state='unbilled' and event.event_start_date =%s group by res_company.id ",(current_date,))\
        ;prev_unbilled_event = self._cr.fetchall();[vals.update({'acd':str(i[1])}) for i in prev_unbilled_event] if prev_unbilled_event else vals.update({'acd':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='Albors And Alnet' and event.state='unbilled' and event.event_start_date =%s group by res_company.id ",(current_date,))\
        ;prev_unbilled_event = self._cr.fetchall();[vals.update({'albors_alnet':str(i[1])}) for i in prev_unbilled_event] if prev_unbilled_event else vals.update({'albors_alnet':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='ASIT' and event.state='unbilled' and event.event_start_date =%s group by res_company.id ",(current_date,))\
        ;prev_unbilled_event = self._cr.fetchall();[vals.update({'asit':str(i[1])}) for i in prev_unbilled_event] if prev_unbilled_event else vals.update({'asit':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='IUG-SD' and event.state='unbilled' and event.event_start_date =%s group by res_company.id ",(current_date,))\
        ;prev_unbilled_event = self._cr.fetchall();[vals.update({'iug_sd':str(i[1])}) for i in prev_unbilled_event] if prev_unbilled_event else vals.update({'iug_sd':'0'})

        vals.update({'options':'ubilled'});last_id=self.env['iug.dashboard.currentmonth'].create(vals).id;currentmonth_ids.append(last_id)


#Invoiced Events
        vals={}
        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='ACD' and event.state='invoiced' and event.event_start_date =%s group by res_company.id ",(current_date,))\
        ;prev_invoiced_event = self._cr.fetchall();[vals.update({'acd':str(i[1])}) for i in prev_invoiced_event] if prev_invoiced_event else vals.update({'acd':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='Albors And Alnet' and event.state='invoiced' and event.event_start_date =%s group by res_company.id ",(current_date,))\
        ;prev_invoiced_event = self._cr.fetchall();[vals.update({'albors_alnet':str(i[1])}) for i in prev_invoiced_event] if prev_invoiced_event else vals.update({'albors_alnet':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='ASIT' and event.state='invoiced' and event.event_start_date =%s group by res_company.id ",(current_date,))\
        ;prev_invoiced_event = self._cr.fetchall();[vals.update({'asit':str(i[1])}) for i in prev_invoiced_event] if prev_invoiced_event else vals.update({'asit':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='IUG-SD' and event.state='invoiced' and event.event_start_date =%s group by res_company.id ",(current_date,))\
        ;prev_invoiced_event = self._cr.fetchall();[vals.update({'iug_sd':str(i[1])}) for i in prev_invoiced_event] if prev_invoiced_event else vals.update({'iug_sd':'0'})

        vals.update({'options':'invoiced'});last_id=self.env['iug.dashboard.currentmonth'].create(vals).id;currentmonth_ids.append(last_id)


        
        #current month events#
#         cr.execute("select count(id) from event where event_start_date=%s ",(current_date,))
#         current_total_event = cr.fetchone()
#         for i in current_total_event:
#             i=str(i)
#             vals={'acd':i,'albors_alnet':i,'asit':i,'iug_sd':i,'options':'total_event'}
#             current_id=self.pool.get('iug.dashboard.currentmonth').create(cr,uid,vals)
#             currentmonth_ids.append(current_id)
#             
#             
#             
#         
#         #Unbilled Events#
#         cr.execute("select count(id) from event where state='unbilled' and event_start_date=%s ",(current_date,))
#         current_unbilled_event = cr.fetchone()
#         for i in current_unbilled_event:
#             i=str(i)
#             vals={'acd':i,'albors_alnet':i,'asit':i,'iug_sd':i,'options':'ubilled'}
#             current_id=self.pool.get('iug.dashboard.currentmonth').create(cr,uid,vals)
#             currentmonth_ids.append(current_id)            
#             
#         
#         #Invoiced Events
#         cr.execute("select count(id) from event where state='invoiced' and event_start_date=%s ",(current_date,))
#         current_invoiced_event = cr.fetchone()  
#         for i in current_invoiced_event:
#             i=str(i)
#             vals={'acd':i,'albors_alnet':i,'asit':i,'iug_sd':i,'options':'invoiced'}
#             current_id=self.pool.get('iug.dashboard.currentmonth').create(cr,uid,vals)
#             currentmonth_ids.append(current_id)                      
#                      
#         
        ##############################Current events details Ends############################


        ##############################Future events details############################     
        
       
        #unapproved
        vals={}
        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='ACD' and event.state='unapproved' and event.event_start_date >=%s group by res_company.id ",(current_date,))\
        ;future_unapproved_event = self._cr.fetchall();[vals.update({'acd':str(i[1])}) for i in future_unapproved_event] if future_unapproved_event else vals.update({'acd':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='Albors And Alnet' and event.state='unapproved' and event.event_start_date >=%s group by res_company.id ",(current_date,))\
        ;future_unapproved_event = self._cr.fetchall();[vals.update({'albors_alnet':str(i[1])}) for i in future_unapproved_event] if future_unapproved_event else vals.update({'albors_alnet':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='ASIT' and event.state='unapproved' and event.event_start_date >=%s group by res_company.id ",(current_date,))\
        ;future_unapproved_event = self._cr.fetchall();[vals.update({'asit':str(i[1])}) for i in future_unapproved_event] if future_unapproved_event else vals.update({'asit':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='IUG-SD' and event.state='unapproved' and event.event_start_date >=%s group by res_company.id ",(current_date,))\
        ;future_unapproved_event = self._cr.fetchall();[vals.update({'iug_sd':str(i[1])}) for i in future_unapproved_event] if future_unapproved_event else vals.update({'iug_sd':'0'})

        vals.update({'options':'unapproved'});last_id=self.env['iug.dashboard.futuremonth'].create(vals).id;futuremonth_ids.append(last_id)





        
#         cr.execute("select count(id) from event where event_start_date>=%s and state='unapproved' ",(current_date,))
#         future_unapproved_event = cr.fetchone()
#         for i in future_unapproved_event:
#             i=str(i)
#             vals={'acd':i,'albors_alnet':i,'asit':i,'iug_sd':i,'options':'unapproved'}
#             future_id=self.pool.get('iug.dashboard.futuremonth').create(cr,uid,vals)
#             futuremonth_ids.append(future_id)            
#             
#         
#rejected Events#

        vals={}
        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='ACD' and event.state='rejected' and event.event_start_date >=%s group by res_company.id ",(current_date,))\
        ;future_unbilled_event = self._cr.fetchall();[vals.update({'acd':str(i[1])}) for i in future_unbilled_event] if future_unbilled_event else vals.update({'acd':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='Albors And Alnet' and event.state='rejected' and event.event_start_date >=%s group by res_company.id ",(current_date,))\
        ;future_unbilled_event = self._cr.fetchall();[vals.update({'albors_alnet':str(i[1])}) for i in future_unbilled_event] if future_unbilled_event else vals.update({'albors_alnet':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='ASIT' and event.state='rejected' and event.event_start_date >=%s group by res_company.id ",(current_date,))\
        ;future_unbilled_event = self._cr.fetchall();[vals.update({'asit':str(i[1])}) for i in future_unbilled_event] if future_unbilled_event else vals.update({'asit':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='IUG-SD' and event.state='rejected' and event.event_start_date >=%s group by res_company.id ",(current_date,))\
        ;future_unbilled_event = self._cr.fetchall();[vals.update({'iug_sd':str(i[1])}) for i in future_unbilled_event] if future_unbilled_event else vals.update({'iug_sd':'0'})

        vals.update({'options':'rejected'});last_id=self.env['iug.dashboard.futuremonth'].create(vals).id;futuremonth_ids.append(last_id)

#         cr.execute("select count(id) from event where state='rejected' and event_start_date>=%s ",(current_date,))
#         future_unbilled_event = cr.fetchone()
#         for i in future_unbilled_event:
#             i=str(i)
#             vals={'acd':i,'albors_alnet':i,'asit':i,'iug_sd':i,'options':'rejected'}
#             future_id=self.pool.get('iug.dashboard.futuremonth').create(cr,uid,vals)
#             futuremonth_ids.append(future_id)            
#             
#         
##Unscheduled Events

        vals={}
        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='ACD' and event.state='draft' and event.event_start_date >=%s group by res_company.id ",(current_date,))\
        ;future_unscheduled_event = self._cr.fetchall();[vals.update({'acd':str(i[1])}) for i in future_unscheduled_event] if future_unscheduled_event else vals.update({'acd':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='Albors And Alnet' and event.state='draft' and event.event_start_date >=%s group by res_company.id ",(current_date,))\
        ;future_unscheduled_event = self._cr.fetchall();[vals.update({'albors_alnet':str(i[1])}) for i in future_unscheduled_event] if future_unscheduled_event else vals.update({'albors_alnet':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='ASIT' and event.state='draft' and event.event_start_date >=%s group by res_company.id ",(current_date,))\
        ;future_unscheduled_event = self._cr.fetchall();[vals.update({'asit':str(i[1])}) for i in future_unscheduled_event] if future_unscheduled_event else vals.update({'asit':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='IUG-SD' and event.state='draft' and event.event_start_date >=%s group by res_company.id ",(current_date,))\
        ;future_unscheduled_event = self._cr.fetchall();[vals.update({'iug_sd':str(i[1])}) for i in future_unscheduled_event] if future_unscheduled_event else vals.update({'iug_sd':'0'})

        vals.update({'options':'draft'});last_id=self.env['iug.dashboard.futuremonth'].create(vals).id;futuremonth_ids.append(last_id)



#         cr.execute("select count(id) fromdef default_ge event where state='draft' and event_start_date>%s ",(current_date,))
#         future_unscheduled_event = cr.fetchone()  
#         for i in future_unscheduled_event:
#             i=str(i)
#             vals={'acd':i,'albors_alnet':i,'asit':i,'iug_sd':i,'options':'draft'}
#             future_id=self.pool.get('iug.dashboard.futuremonth').create(cr,uid,vals)
#             futuremonth_ids.append(future_id)            
#             
#         
#scheduled
        vals={}
        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='ACD' and event.state='scheduled' and event.event_start_date >=%s group by res_company.id ",(current_date,))\
        ;future_scheduled_event = self._cr.fetchall();[vals.update({'acd':str(i[1])}) for i in future_scheduled_event] if future_scheduled_event else vals.update({'acd':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='Albors And Alnet' and event.state='scheduled' and event.event_start_date >=%s group by res_company.id ",(current_date,))\
        ;future_scheduled_event = self._cr.fetchall();[vals.update({'albors_alnet':str(i[1])}) for i in future_scheduled_event] if future_scheduled_event else vals.update({'albors_alnet':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='ASIT' and event.state='scheduled' and event.event_start_date >=%s group by res_company.id ",(current_date,))\
        ;future_scheduled_event = self._cr.fetchall();[vals.update({'asit':str(i[1])}) for i in future_scheduled_event] if future_scheduled_event else vals.update({'asit':'0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
        res_company.name='IUG-SD' and event.state='scheduled' and event.event_start_date >=%s group by res_company.id ",(current_date,))\
        ;future_scheduled_event = self._cr.fetchall();[vals.update({'iug_sd':str(i[1])}) for i in future_scheduled_event] if future_scheduled_event else vals.update({'iug_sd':'0'})

        vals.update({'options':'scheduled'});last_id=self.env['iug.dashboard.futuremonth'].create(vals).id;futuremonth_ids.append(last_id)


#         cr.execute("select count(id) from event where event_start_date>=%s and state='scheduled' ",(current_date,))
#         future_scheduled_event = cr.fetchone()
#         for i in future_scheduled_event:
#             i=str(i)
#             vals={'acd':i,'albors_alnet':i,'asit':i,'iug_sd':i,'options':'scheduled'}
#             future_id=self.pool.get('iug.dashboard.futuremonth').create(cr,uid,vals)
#             futuremonth_ids.append(future_id)              
#             
#         
#allocated Events#
        vals={}
        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                res_company.name='ACD' and event.state='allocated' and event.event_start_date >=%s group by res_company.id ",
                        (current_date,)) \
            ;
        future_allocated_event = self._cr.fetchall();
        [vals.update({'acd': str(i[1])}) for i in future_allocated_event] if future_allocated_event else vals.update(
            {'acd': '0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                res_company.name='Albors And Alnet' and event.state='allocated' and event.event_start_date >=%s group by res_company.id ",
                        (current_date,)) \
            ;
        future_allocated_event = self._cr.fetchall();
        [vals.update({'albors_alnet': str(i[1])}) for i in
         future_allocated_event] if future_allocated_event else vals.update({'albors_alnet': '0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                res_company.name='ASIT' and event.state='allocated' and event.event_start_date >=%s group by res_company.id ",
                        (current_date,)) \
            ;
        future_allocated_event = self._cr.fetchall();
        [vals.update({'asit': str(i[1])}) for i in future_allocated_event] if future_allocated_event else vals.update(
            {'asit': '0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                res_company.name='IUG-SD' and event.state='allocated' and event.event_start_date >=%s group by res_company.id ",
                        (current_date,)) \
            ;
        future_allocated_event = self._cr.fetchall();
        [vals.update({'iug_sd': str(i[1])}) for i in future_allocated_event] if future_allocated_event else vals.update(
            {'iug_sd': '0'})

        vals.update({'options': 'allocated'});
        last_id = self.env['iug.dashboard.futuremonth'].create(vals).id;
        futuremonth_ids.append(last_id)

        vals = {}
        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                res_company.name='ACD' and event.state='unauthorize' and event.event_start_date >=%s group by res_company.id ",
                        (current_date,)) \
            ;
        future_unauthorize_event = self._cr.fetchall();
        [vals.update({'acd': str(i[1])}) for i in
         future_unauthorize_event] if future_unauthorize_event else vals.update({'acd': '0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                res_company.name='Albors And Alnet' and event.state='unauthorize' and event.event_start_date >=%s group by res_company.id ",
                        (current_date,)) \
            ;
        future_unauthorize_event = self._cr.fetchall();
        [vals.update({'albors_alnet': str(i[1])}) for i in
         future_unauthorize_event] if future_unauthorize_event else vals.update({'albors_alnet': '0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                res_company.name='ASIT' and event.state='unauthorize' and event.event_start_date >=%s group by res_company.id ",
                        (current_date,)) \
            ;
        future_unauthorize_event = self._cr.fetchall();
        [vals.update({'asit': str(i[1])}) for i in
         future_unauthorize_event] if future_unauthorize_event else vals.update({'asit': '0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                res_company.name='IUG-SD' and event.state='unauthorize' and event.event_start_date >=%s group by res_company.id ",
                        (current_date,)) \
            ;
        future_unauthorize_event = self._cr.fetchall();
        [vals.update({'iug_sd': str(i[1])}) for i in
         future_unauthorize_event] if future_unauthorize_event else vals.update({'iug_sd': '0'})
        vals.update({'options': 'unauthorize'});
        last_id = self.env['iug.dashboard.futuremonth'].create(vals).id;
        futuremonth_ids.append(last_id)

        vals = {}
        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                res_company.name='ACD' and event.state='confirmed' and event.event_start_date >=%s group by res_company.id ",
                        (current_date,)) \
            ;
        future_confirmed_event = self._cr.fetchall();
        [vals.update({'acd': str(i[1])}) for i in future_confirmed_event] if future_confirmed_event else vals.update(
            {'acd': '0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                res_company.name='Albors And Alnet' and event.state='confirmed' and event.event_start_date >=%s group by res_company.id ",
                        (current_date,)) \
            ;
        future_confirmed_event = self._cr.fetchall();
        [vals.update({'albors_alnet': str(i[1])}) for i in
         future_confirmed_event] if future_confirmed_event else vals.update({'albors_alnet': '0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                res_company.name='ASIT' and event.state='confirmed' and event.event_start_date >=%s group by res_company.id ",
                        (current_date,)) \
            ;
        future_confirmed_event = self._cr.fetchall();
        [vals.update({'asit': str(i[1])}) for i in future_confirmed_event] if future_confirmed_event else vals.update(
            {'asit': '0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                res_company.name='IUG-SD' and event.state='confirmed' and event.event_start_date >=%s group by res_company.id ",
                        (current_date,)) \
            ;
        future_confirmed_event = self._cr.fetchall();
        [vals.update({'iug_sd': str(i[1])}) for i in future_confirmed_event] if future_confirmed_event else vals.update(
            {'iug_sd': '0'})

        vals.update({'options': 'confirmed'});
        last_id = self.env['iug.dashboard.futuremonth'].create(vals).id;
        futuremonth_ids.append(last_id)

        vals = {}
        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                res_company.name='ACD' and event.state='cancel' and event.event_start_date >=%s group by res_company.id ",
                        (current_date,)) \
            ;
        future_cancel_event = self._cr.fetchall();
        [vals.update({'acd': str(i[1])}) for i in future_cancel_event] if future_cancel_event else vals.update(
            {'acd': '0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                res_company.name='Albors And Alnet' and event.state='cancel' and event.event_start_date >=%s group by res_company.id ",
                        (current_date,)) \
            ;
        future_cancel_event = self._cr.fetchall();
        [vals.update({'albors_alnet': str(i[1])}) for i in future_cancel_event] if future_cancel_event else vals.update(
            {'albors_alnet': '0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                res_company.name='ASIT' and event.state='cancel' and event.event_start_date >=%s group by res_company.id ",
                        (current_date,)) \
            ;
        future_cancel_event = self._cr.fetchall();
        [vals.update({'asit': str(i[1])}) for i in future_cancel_event] if future_cancel_event else vals.update(
            {'asit': '0'})

        self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                res_company.name='IUG-SD' and event.state='cancel' and event.event_start_date >=%s group by res_company.id ",
                        (current_date,)) \
            ;
        future_cancel_event = self._cr.fetchall();
        [vals.update({'iug_sd': str(i[1])}) for i in future_cancel_event] if future_cancel_event else vals.update(
            {'iug_sd': '0'})

        vals.update({'options': 'cancel'});
        last_id = self.env['iug.dashboard.futuremonth'].create(vals).id;
        futuremonth_ids.append(last_id)

        res = {'name': 'Events Dashboard', 'lastmonth': lastmonth_ids, 'currentmonth': currentmonth_ids,
               'futuremonth': futuremonth_ids, 'start_date': str(previous_month), 'end_date': str(current_date)}

        result.update(res)
        return result

    @api.multi
    def default_get_refresh(self):
        fields, res = {}, {}
        result = self.default_get(fields)
        print (result)
        [res.update({i: [(6, 0, result[i])]}) if i not in ['name', 'start_date', 'end_date'] else res.update(
            {i: result[i]}) for i in result.keys()]
        # import ipdb;ipdb.set_trace()
        self.write(res)
        return True

    @api.multi
    def past_events(self):
        ''' show events depending on specified range'''
        rangemonth_ids = []
        if not self.start_date:
            raise UserError(_('Please select end date.'))
        elif not self.end_date:
            raise UserError(_('Please select start date.'))
        elif not (self.start_date and self.end_date):
            raise UserError(_('Please select start date & end date.'))
        val = {'start_date':self.start_date, 'end_date':self.end_date}
        if val.get('start_date') and val.get('end_date'):
            if val.get('start_date') > val.get('end_date'):
                raise UserError(_('Start Date cannot be greater than End Date !!.'))

            ########unapproved##############3
            vals = {}

            self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                    res_company.name='ACD' and event.state='draft' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",
                            (val.get('start_date'), val.get('end_date'))) \
                ;
            future_unscheduled_event = self._cr.fetchall();
            [vals.update({'acd': str(i[1])}) for i in
             future_unscheduled_event] if future_unscheduled_event else vals.update({'acd': '0'})

            self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                    res_company.name='Albors And Alnet' and event.state='unapproved' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",
                            (val.get('start_date'), val.get('end_date'))) \
                ;
            range_unapproved_event = self._cr.fetchall();
            [vals.update({'albors_alnet': str(i[1])}) for i in
             range_unapproved_event] if range_unapproved_event else vals.update({'albors_alnet': '0'})

            self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                    res_company.name='ASIT' and event.state='unapproved' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",
                            (val.get('start_date'), val.get('end_date'))) \
                ;
            range_unapproved_event = self._cr.fetchall();
            [vals.update({'asit': str(i[1])}) for i in
             range_unapproved_event] if range_unapproved_event else vals.update({'asit': '0'})

            self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                    res_company.name='IUG-SD' and event.state='unapproved' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",
                            (val.get('start_date'), val.get('end_date'))) \
                ;
            range_unapproved_event = self._cr.fetchall();
            [vals.update({'iug_sd': str(i[1])}) for i in
             range_unapproved_event] if range_unapproved_event else vals.update({'iug_sd': '0'})

            vals.update({'options': 'unapproved'});
            last_id = self.env['iug.dashboard.rangemonth'].create(vals).id;
            rangemonth_ids.append(last_id)

            #####rejected########
            self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                    res_company.name='ACD' and event.state='rejected' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",
                            (val.get('start_date'), val.get('end_date'))) \
                ;
            range_unbilled_event = self._cr.fetchall();
            [vals.update({'acd': str(i[1])}) for i in range_unbilled_event] if range_unbilled_event else vals.update(
                {'acd': '0'})

            self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                    res_company.name='Albors And Alnet' and event.state='rejected' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",
                            (val.get('start_date'), val.get('end_date'))) \
                ;
            range_unbilled_event = self._cr.fetchall();
            [vals.update({'albors_alnet': str(i[1])}) for i in
             range_unbilled_event] if range_unbilled_event else vals.update({'albors_alnet': '0'})

            self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                    res_company.name='ASIT' and event.state='rejected' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",
                            (val.get('start_date'), val.get('end_date'))) \
                ;
            range_unbilled_event = self._cr.fetchall();
            [vals.update({'asit': str(i[1])}) for i in range_unbilled_event] if range_unbilled_event else vals.update(
                {'asit': '0'})

            self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                    res_company.name='IUG-SD' and event.state='rejected' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",
                            (val.get('start_date'), val.get('end_date'))) \
                ;
            range_unbilled_event = self._cr.fetchall();
            [vals.update({'iug_sd': str(i[1])}) for i in range_unbilled_event] if range_unbilled_event else vals.update(
                {'iug_sd': '0'})

            vals.update({'options': 'rejected'});
            last_id = self.env['iug.dashboard.rangemonth'].create(vals).id;
            rangemonth_ids.append(last_id)

            ##Unscheduled Events##################

            vals = {}
            self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                    res_company.name='ACD' and event.state='draft' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",
                            (val.get('start_date'), val.get('end_date'))) \
                ;
            future_unscheduled_event = self._cr.fetchall();
            [vals.update({'acd': str(i[1])}) for i in
             future_unscheduled_event] if future_unscheduled_event else vals.update({'acd': '0'})

            self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                    res_company.name='Albors And Alnet' and event.state='draft' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",
                            (val.get('start_date'), val.get('end_date'))) \
                ;
            future_unscheduled_event = self._cr.fetchall();
            [vals.update({'albors_alnet': str(i[1])}) for i in
             future_unscheduled_event] if future_unscheduled_event else vals.update({'albors_alnet': '0'})

            self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                    res_company.name='ASIT' and event.state='draft' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",
                            (val.get('start_date'), val.get('end_date'))) \
                ;
            future_unscheduled_event = self._cr.fetchall();
            [vals.update({'asit': str(i[1])}) for i in
             future_unscheduled_event] if future_unscheduled_event else vals.update({'asit': '0'})

            self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                    res_company.name='IUG-SD' and event.state='draft' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",
                            (val.get('start_date'), val.get('end_date'))) \
                ;
            future_unscheduled_event = self._cr.fetchall();
            [vals.update({'iug_sd': str(i[1])}) for i in
             future_unscheduled_event] if future_unscheduled_event else vals.update({'iug_sd': '0'})

            vals.update({'options': 'draft'});
            last_id = self.env['iug.dashboard.rangemonth'].create(vals).id;
            rangemonth_ids.append(last_id)

            ################scheduled####################
            vals = {}
            self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                    res_company.name='ACD' and event.state='scheduled' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",
                            (val.get('start_date'), val.get('end_date'))) \
                ;
            future_scheduled_event = self._cr.fetchall();
            [vals.update({'acd': str(i[1])}) for i in
             future_scheduled_event] if future_scheduled_event else vals.update({'acd': '0'})

            self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                    res_company.name='Albors And Alnet' and event.state='scheduled' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",
                            (val.get('start_date'), val.get('end_date'))) \
                ;
            future_scheduled_event = self._cr.fetchall();
            [vals.update({'albors_alnet': str(i[1])}) for i in
             future_scheduled_event] if future_scheduled_event else vals.update({'albors_alnet': '0'})

            self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                    res_company.name='ASIT' and event.state='scheduled' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",
                            (val.get('start_date'), val.get('end_date'))) \
                ;
            future_scheduled_event = self._cr.fetchall();
            [vals.update({'asit': str(i[1])}) for i in
             future_scheduled_event] if future_scheduled_event else vals.update({'asit': '0'})

            self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                    res_company.name='IUG-SD' and event.state='scheduled' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",
                            (val.get('start_date'), val.get('end_date'))) \
                ;
            future_scheduled_event = self._cr.fetchall();
            [vals.update({'iug_sd': str(i[1])}) for i in
             future_scheduled_event] if future_scheduled_event else vals.update({'iug_sd': '0'})

            vals.update({'options': 'scheduled'});
            last_id = self.env['iug.dashboard.rangemonth'].create(vals).id;
            rangemonth_ids.append(last_id)

            ############allocated Events################
            vals = {}
            self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                    res_company.name='ACD' and event.state='allocated' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",
                            (val.get('start_date'), val.get('end_date'))) \
                ;
            future_allocated_event = self._cr.fetchall();
            [vals.update({'acd': str(i[1])}) for i in
             future_allocated_event] if future_allocated_event else vals.update({'acd': '0'})

            self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                    res_company.name='Albors And Alnet' and event.state='allocated' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",
                            (val.get('start_date'), val.get('end_date'))) \
                ;
            future_allocated_event = self._cr.fetchall();
            [vals.update({'albors_alnet': str(i[1])}) for i in
             future_allocated_event] if future_allocated_event else vals.update({'albors_alnet': '0'})

            self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                    res_company.name='ASIT' and event.state='allocated' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",
                            (val.get('start_date'), val.get('end_date'))) \
                ;
            future_allocated_event = self._cr.fetchall();
            [vals.update({'asit': str(i[1])}) for i in
             future_allocated_event] if future_allocated_event else vals.update({'asit': '0'})

            self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                    res_company.name='IUG-SD' and event.state='allocated' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",
                            (val.get('start_date'), val.get('end_date'))) \
                ;
            future_allocated_event = self._cr.fetchall();
            [vals.update({'iug_sd': str(i[1])}) for i in
             future_allocated_event] if future_allocated_event else vals.update({'iug_sd': '0'})

            vals.update({'options': 'allocated'});
            last_id = self.env['iug.dashboard.rangemonth'].create(vals).id;
            rangemonth_ids.append(last_id)

            ##############unauthorize Events##############
            vals = {}
            self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                    res_company.name='ACD' and event.state='unauthorize' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",
                            (val.get('start_date'), val.get('end_date'))) \
                ;
            future_unauthorize_event = self._cr.fetchall();
            [vals.update({'acd': str(i[1])}) for i in
             future_unauthorize_event] if future_unauthorize_event else vals.update({'acd': '0'})

            self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                    res_company.name='Albors And Alnet' and event.state='unauthorize' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",
                            (val.get('start_date'), val.get('end_date'))) \
                ;
            future_unauthorize_event = self._cr.fetchall();
            [vals.update({'albors_alnet': str(i[1])}) for i in
             future_unauthorize_event] if future_unauthorize_event else vals.update({'albors_alnet': '0'})

            self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                    res_company.name='ASIT' and event.state='unauthorize' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",
                            (val.get('start_date'), val.get('end_date'))) \
                ;
            future_unauthorize_event = self._cr.fetchall();
            [vals.update({'asit': str(i[1])}) for i in
             future_unauthorize_event] if future_unauthorize_event else vals.update({'asit': '0'})

            self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                    res_company.name='IUG-SD' and event.state='unauthorize' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",
                            (val.get('start_date'), val.get('end_date'))) \
                ;
            future_unauthorize_event = self._cr.fetchall();
            [vals.update({'iug_sd': str(i[1])}) for i in
             future_unauthorize_event] if future_unauthorize_event else vals.update({'iug_sd': '0'})

            vals.update({'options': 'unauthorize'});
            last_id = self.env['iug.dashboard.rangemonth'].create(vals).id;
            rangemonth_ids.append(last_id)

            ####################confirmed Events##################
            vals = {}
            self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                    res_company.name='ACD' and event.state='confirmed' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",
                            (val.get('start_date'), val.get('end_date'))) \
                ;
            future_confirmed_event = self._cr.fetchall();
            [vals.update({'acd': str(i[1])}) for i in
             future_confirmed_event] if future_confirmed_event else vals.update({'acd': '0'})

            self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                    res_company.name='Albors And Alnet' and event.state='confirmed' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",
                            (val.get('start_date'), val.get('end_date'))) \
                ;
            future_confirmed_event = self._cr.fetchall();
            [vals.update({'albors_alnet': str(i[1])}) for i in
             future_confirmed_event] if future_confirmed_event else vals.update({'albors_alnet': '0'})

            self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                    res_company.name='ASIT' and event.state='confirmed' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",
                            (val.get('start_date'), val.get('end_date'))) \
                ;
            future_confirmed_event = self._cr.fetchall();
            [vals.update({'asit': str(i[1])}) for i in
             future_confirmed_event] if future_confirmed_event else vals.update({'asit': '0'})

            self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                    res_company.name='IUG-SD' and event.state='confirmed' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",
                            (val.get('start_date'), val.get('end_date'))) \
                ;
            future_confirmed_event = self._cr.fetchall();
            [vals.update({'iug_sd': str(i[1])}) for i in
             future_confirmed_event] if future_confirmed_event else vals.update({'iug_sd': '0'})

            vals.update({'options': 'confirmed'});
            last_id = self.env['iug.dashboard.rangemonth'].create(vals).id;
            rangemonth_ids.append(last_id)

            ########### #cancel Events##############
            vals = {}
            self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                    res_company.name='ACD' and event.state='cancel' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",
                            (val.get('start_date'), val.get('end_date'))) \
                ;
            future_cancel_event = self._cr.fetchall();
            [vals.update({'acd': str(i[1])}) for i in future_cancel_event] if future_cancel_event else vals.update(
                {'acd': '0'})

            self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                    res_company.name='Albors And Alnet' and event.state='cancel' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",
                            (val.get('start_date'), val.get('end_date'))) \
                ;
            future_cancel_event = self._cr.fetchall();
            [vals.update({'albors_alnet': str(i[1])}) for i in
             future_cancel_event] if future_cancel_event else vals.update({'albors_alnet': '0'})

            self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                    res_company.name='ASIT' and event.state='cancel' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",
                            (val.get('start_date'), val.get('end_date'))) \
                ;
            future_cancel_event = self._cr.fetchall();
            [vals.update({'asit': str(i[1])}) for i in future_cancel_event] if future_cancel_event else vals.update(
                {'asit': '0'})

            self._cr.execute("select res_company.name,count(event.id) from res_company left join event on (res_company.id = event.company_id) where \
                    res_company.name='IUG-SD' and event.state='cancel' and event.event_start_date BETWEEN %s AND %s group by res_company.id ",
                            (val.get('start_date'), val.get('end_date'))) \
                ;
            future_cancel_event = self._cr.fetchall();
            [vals.update({'iug_sd': str(i[1])}) for i in future_cancel_event] if future_cancel_event else vals.update(
                {'iug_sd': '0'})

            vals.update({'options': 'cancel'});
            last_id = self.env['iug.dashboard.rangemonth'].create(vals).id;
            rangemonth_ids.append(last_id)

            self.write({'rangemonth_flag': False, 'rangemonth': [(6, 0, rangemonth_ids)]})

    @api.multi
    def refresh_my_page(self):
        return self.default_get_refresh()

class iug_dashboard_lastmonth(models.Model):
    _name = 'iug.dashboard.lastmonth'

    acd = fields.Char('ACD')
    albors_alnet = fields.Char('Albors And Alnet')
    asit = fields.Char('ASIT')
    iug_sd = fields.Char('IUG-SD')
    options = fields.Selection([('total_event', 'Total Event'), ('ubilled', 'Unbilled'), ('invoiced', 'Invoiced')],
                               'Options')

class iug_dashboard_currentmonth(models.Model):
    _name = 'iug.dashboard.currentmonth'

    acd = fields.Char('ACD')
    albors_alnet = fields.Char('Albors And Alnet')
    asit = fields.Char('ASIT')
    iug_sd = fields.Char('IUG-SD')
    options = fields.Selection([
        ('total_event', 'Total Event'),
        ('ubilled', 'Unbilled'),
        ('invoiced', 'Invoiced'),
        ('draft', 'Unscheduled'),
        ('scheduled', 'Job Offered'),
        ('confirmed', 'Confirmed')], 'Options')

class iug_dashboard_futuremonth(models.Model):
    _name = 'iug.dashboard.futuremonth'

    acd = fields.Char('ACD')
    albors_alnet = fields.Char('Albors And Alnet')
    asit = fields.Char('ASIT')
    iug_sd = fields.Char('IUG-SD')
    options = fields.Selection([
        ('unapproved', 'Unappoved'),
        ('rejected', 'Rejected'),
        ('draft', 'Unscheduled'),
        ('scheduled', 'Job Offered'),
        ('allocated', 'Scheduled'),
        ('unauthorize', 'Unauthorize'),
        ('confirmed', 'Confirmed'),
        ('cancel', 'Cancelled')], 'Options')

class iug_dashboard_rangemonth(models.Model):
    _name = 'iug.dashboard.rangemonth'

    acd = fields.Char('ACD')
    albors_alnet = fields.Char('Albors And Alnet')
    asit = fields.Char('ASIT')
    iug_sd = fields.Char('IUG-SD')
    options = fields.Selection([
        ('unapproved', 'Unappoved'),
        ('rejected', 'Rejected'),
        ('draft', 'Unscheduled'),
        ('scheduled', 'Job Offered'),
        ('allocated', 'Scheduled'),
        ('unauthorize', 'Unauthorize'),
        ('confirmed', 'Confirmed'),
        ('cancel', 'Cancelled')], 'Options')

class iug_statistics_dashboard(models.Model):

    _name = 'iug.statistics.dashboard'

    name = fields.Char('Name', readonly=True, default='Event Statistics')
    company_id = fields.Many2one('res.company', 'Company')
    today = fields.Char("Event count for today", readonly=True)
    tomorrow = fields.Char("Event count for tomorrow", readonly=True)
    unfilled_tomorrow = fields.Char('Event unfilled for tomorrow', readonly=True)
    unauthorized_tomorrow = fields.Char('Event unauthorized for tomorrow', readonly=True)
    unconfirmed_tomorrow = fields.Char('Event unconfirmed for tomorrow', readonly=True)
    empty_list = fields.Char('Events on empty list', readonly=True)
    jobs_added_today = fields.Char('New jobs added for today', readonly=True)
    event_added_today = fields.Char('New events added for today', readonly=True)
    conf_call_today = fields.Char('Conference call today', readonly=True)
    book_month = fields.Char('Events booked for this month', readonly=True)
    book_next_month = fields.Char('Events booked for next month', readonly=True)
    completed_month = fields.Char('Events completed this month', readonly=True)
    invoice_mtd = fields.Float('Invoiced MTD', readonly=True)
    average = fields.Float('Average %/event', readonly=True)
    projected = fields.Float('Projected', readonly=True)
    interpretingYTD = fields.Float('Interpreting YTD', readonly=True)

    def last_day(self, year, month):
        return str(calendar.monthrange(year, month)[1])

    @api.model
    def default_get(self, fields):
        ''' Set default values for statisrics dashboard'''
        res = {}
        lastmonth_ids, currentmonth_ids, futuremonth_ids = [], [], []
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        user = self.env.user
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.utc
        current_date = tz.localize(
            datetime.datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), DATETIME_FORMAT),
            is_dst=None)
        current_date1 = datetime.datetime.strptime(current_date.astimezone(tz).strftime(DATETIME_FORMAT),
                                                   DATETIME_FORMAT)
        current_date = current_date1.strftime('%Y-%m-%d')
        next_day_format = current_date1 + datetime.timedelta(days=1)
        next_day = next_day_format.strftime('%Y-%m-%d')
        first_day_month = current_date1.strftime('%Y-%m') + '-01'
        format = current_date1
        year = format.year
        month = format.month
        last_day_month = current_date1.strftime('%Y-%m') + '-' + self.last_day(year, month)
        format = current_date1 + relativedelta(months=1)
        year = format.year
        month = format.month
        first_day_next_month = format.strftime('%Y-%m') + '-01'
        last_day_next_month = format.strftime('%Y-%m') + '-' + self.last_day(year, month)
        if self._context.get('comp_id'):
            company_id = tuple(self._context.get('comp_id'))
        else:
            self._cr.execute('select company_id from res_users where id=%s', (self._uid,))
            company_id = self._cr.fetchone()
        if company_id:
            if len(company_id) > 1:
                raise UserError(_('  Duplicate company name exist !!.'))
            self._cr.execute('select name from res_company where id=%s', (company_id,))
            company_name = self._cr.fetchone()[0]

            #             Event count for today
            query = '''select count(id) from event where event_start_date=%s and company_id=%s'''
            self._cr.execute(query, (current_date, company_id))
            today_event = str(self._cr.fetchone()[0])
            #             Event count for tomorrow
            self._cr.execute(query, (next_day, company_id))
            tomorrow_event = str(self._cr.fetchone()[0])
            #             Event unfilled for tomorrow
            self._cr.execute(query + ''' and state='draft' ''', (next_day, company_id))
            tomorrow_unfilled_event = str(self._cr.fetchone()[0])
            #             Event unauthorized for tomorrow
            self._cr.execute(query + ''' and state='unauthorize' ''', (next_day, company_id))
            tomorrow_unauthorized_event = str(self._cr.fetchone()[0])
            #             Event unconfirmed for tomorrow
            self._cr.execute(query + ''' and state='unapproved' ''', (next_day, company_id))
            tomorrow_unconfirmed_event = str(self._cr.fetchone()[0])
            #             Events on empty list
            query_2 = 'select count(id) from event where event_start_date>%s and company_id=%s'
            self._cr.execute(query_2 + ''' and state='unapproved' ''', (next_day, company_id))
            empty_list_event = str(self._cr.fetchone()[0])
            #             New jobs added for today
            #             New events added for today
            self._cr.execute(query + ''' and state='draft' ''', (current_date, company_id))
            today_new_event = str(self._cr.fetchone()[0])
            #             Conference call today
            #             Events booked for this month
            query_3 = ''' select count(id) from event where event_start_date BETWEEN %s and %s and company_id=%s'''
            self._cr.execute(query_3, (first_day_month, last_day_month, company_id))
            event_book_month = str(self._cr.fetchone()[0])
            #             Events booked for next month
            self._cr.execute(query_3, (first_day_next_month, last_day_next_month, company_id))
            event_book_next_month = str(self._cr.fetchone()[0])
            #             Events completed this month
            self._cr.execute(query_3 + ''' and state='done' ''', (first_day_month, last_day_month, company_id))
            event_completed_month = str(self._cr.fetchone()[0])
        #         Invoiced MTD
        #         Average %/event
        #         Projected
        #         Interpreting YTD
        else:
            raise UserError(_('  No Company Exist !!.'))
        res = {'company_id': company_id[0], 'today': today_event, 'tomorrow': tomorrow_event,
               'unfilled_tomorrow': tomorrow_unfilled_event, 'unauthorized_tomorrow': \
                   tomorrow_unauthorized_event, 'unconfirmed_tomorrow': tomorrow_unconfirmed_event,
               'empty_list': empty_list_event, \
               'event_added_today': today_new_event, 'book_month': event_book_month,
               'book_next_month': event_book_next_month, \
               'completed_month': event_completed_month}
        return res

    @api.multi
    def refresh_page(self):
        ''' refresh current dashboard'''
        if self.company_id:
            comp_id = self.company_id.id
            self=self.with_context(comp_id=[comp_id])
        result = self.default_get([])
        return self.write(result)

