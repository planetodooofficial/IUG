# -*- coding: utf-8 -*-
import time
from odoo.report import report_sxw #import report_sxw

class event_completion(report_sxw.rml_parse):
#    _inherit='account.invoice'
#    _name = 'account.invoice'
    def __init__(self, cr, uid, name, context):
        super(event_completion, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'time_start':self.time_start,
            'time_end':self.time_end,
            'verify_time':self.verify_time,
            

        })
        
    def verify_time(self,event_id):
        
        if event_id.verify_time:
            if event_id.verify_time=='False':
                pass
            else:
                return event_id.verify_time
            
        else:
            pass
                
        
        
    def time_start(self,event_id):
        
        if event_id.actual_event_start:
            if event_id.actual_event_start=='False':
                pass
                #return True
            else:
                
                return event_id.actual_event_start
        else:
            pass
        
    
    
    def time_end(self,event_id):
        
        if event_id.actual_event_end:
            if event_id.actual_event_start=='False':
                pass
                #return True
            else:
                
                return event_id.actual_event_end
        else:
            pass
        



report_sxw.report_sxw(
    'report.event.completion.report',
    'event',
    'custom_addons/bista_iugroup/report/event_completion_report.rml',
    parser=event_completion
)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

