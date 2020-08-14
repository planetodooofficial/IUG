from odoo import models, fields,api
import time
import datetime
from dateutil import relativedelta


class schedulars_function(models.Model):
    _name='schedulars.function'
    
    @api.model
    def duplicate_event(self):
        curr_date=datetime.date.today()
        event_obj=self.env['event']
#        event_ids=event_obj.search(cr,uid,[('recurring_next_date','=',datetime.date.today()),('duplicate_end_month','!=',datetime.date.today())])
        self._cr.execute("select id from event where recurring_next_date='%s' and duplicate_active=True"%(curr_date))
        event_ids=filter(None, map(lambda x:x[0], self._cr.fetchall()))
        print"event_ids",event_ids
        print"curr_date",curr_date
        for each in event_ids:
            event_brw=event_obj.browse(each)
            recurring_type=event_brw.recurring_type
            self = self.with_context(recurring=datetime.date.today())
            event_id=event_brw.copy()

            print"event_id",event_id
#            curr_date=event_brw.event_start
#            curr_date=curr_date.split(' ')[0]
            
            if recurring_type=='day':
                next_date=curr_date + relativedelta.relativedelta(days=1)
                print"next_date",next_date
                event_brw.write({'recurring_next_date':next_date,'duplicate_active':False})
                event_id.write({'recurring_next_date':next_date,'duplicate_active':True,'recurring_type':'day','duplicate_end_month':event_brw.duplicate_end_month})
                if event_brw.duplicate_end_month <= str(curr_date):
##                stop_duplicate=True
                    event_id.write({'recurring_next_date':next_date,'duplicate_active':False})
#                else:
#                    event_obj.write(cr,uid,each,{'recurring_next_date':next_date})
            if recurring_type=='week':
                next_date=curr_date + relativedelta.relativedelta(days=7)
                event_brw.write({'recurring_next_date':next_date,'duplicate_active':False})
                event_id.write({'recurring_next_date':next_date,'duplicate_active':True,'recurring_type':'week','duplicate_end_month':event_brw.duplicate_end_month})
                if event_brw.duplicate_end_month <= str(curr_date):
##                stop_duplicate=True
                    event_id.write({'recurring_next_date':next_date,'duplicate_active':False})
            if recurring_type=='bi_week':
                next_date=curr_date + relativedelta.relativedelta(days=14)
                event_brw.write({'recurring_next_date':next_date,'duplicate_active':False})
                event_id.write({'recurring_next_date':next_date,'duplicate_active':True,'recurring_type':'bi_week','duplicate_end_month':event_brw.duplicate_end_month})
                if event_brw.duplicate_end_month <= str(curr_date):
##                stop_duplicate=True
                    event_id.write({'recurring_next_date':next_date,'duplicate_active':False})
            if recurring_type=='monthly':
                next_date=curr_date + relativedelta.relativedelta(months=1)
                event_brw.write({'recurring_next_date':next_date,'duplicate_active':False})
                event_id.write({'recurring_next_date':next_date,'duplicate_active':True,'recurring_type':'monthly','duplicate_end_month':event_brw.duplicate_end_month})
                if event_brw.duplicate_end_month <= str(curr_date):
##                stop_duplicate=True
                    event_id.write({'recurring_next_date':next_date,'duplicate_active':False})
            if recurring_type=='date1':
                curr_date=event_brw.recurring_next_date
                next_date=curr_date + relativedelta.relativedelta(months=1)
                event_brw.write({'recurring_next_date':next_date,'duplicate_active':False})
                event_id.write({'recurring_next_date':next_date,'duplicate_active':True,'recurring_type':'date1','duplicate_end_month':event_brw.duplicate_end_month})
                if event_brw.duplicate_end_month <= str(curr_date):
##                stop_duplicate=True
                    event_id.write({'recurring_next_date':next_date,'duplicate_active':False})

        return True

