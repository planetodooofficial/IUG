import pytz
from odoo import fields, models,_,api
import datetime
from odoo import SUPERUSER_ID
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import time
from dateutil.relativedelta import relativedelta
import calendar
from odoo.exceptions import UserError, RedirectWarning, ValidationError,AccessDenied


class search_events_wizard(models.Model):
    """ A wizard to search events """
    _name = 'search.events.wizard'

    @api.multi
    def search_events(self):
        #import ipdb;ipdb.set_trace()
        ''' This function search events based on the user input'''
        cur_obj = self
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']
        if cur_obj.end_date < cur_obj.start_date:
            raise UserError(_('Start Date Can not be greater than End Date!'))
        result = False
#        print "context.......",context
#         event_type = self._context.get('event_type',False)
#         if event_type == 'language':#action_event_form_language
#             result = mod_obj.sudo().get_object_reference('bista_iugroup', 'action_lang_event_form_all')
#         elif event_type == 'transport':
#             result = mod_obj.sudo().get_object_reference('bista_lang_transport', 'action_event_form_transport')
#         elif event_type == 'translation':
#             result = mod_obj.sudo().get_object_reference('bista_iugroup', 'action_translation_form')
#         elif event_type == 'lang_trans':
#             result = mod_obj.sudo().get_object_reference('bista_lang_transport', 'action_event_form_referral')
#         else :
#             result = mod_obj.sudo().get_object_reference('bista_iugroup', 'action_event_all_type')
#         id = result and result[1] or False
#         result = act_obj.browse().read()[0]
        event_ids, domain = [], []
        if cur_obj.scheduler_id:
            domain.append(('scheduler_id','=',cur_obj.scheduler_id.id))
        if cur_obj.partner_id:
            domain.append(('partner_id','=',cur_obj.partner_id.id))
        if cur_obj.partner_id_2:
            domain.append(('contact_id','=',cur_obj.partner_id_2.id))
        if cur_obj.ordering_partner_id:
            domain.append(('ordering_partner_id','=',cur_obj.ordering_partner_id.id))
        if cur_obj.ordering_contact_id:
            domain.append(('ordering_contact_id','=',cur_obj.ordering_contact_id.id))
        if cur_obj.patient_id:
            domain.append(('patient_id','=',cur_obj.patient_id.id))
        if cur_obj.ordering_contact_id:
            domain.append(('ordering_contact_id','=',cur_obj.ordering_contact_id.id))
        if cur_obj.interpreter_id and cur_obj.state == 'scheduled':
            domain.append(('interpreter_ids2.interpreter_id','in',[cur_obj.interpreter_id.id]))
        elif cur_obj.interpreter_id:
            domain.append(('assigned_interpreters','in',[cur_obj.interpreter_id.id]))
        if cur_obj.language_id:
            domain.append(('language_id','=',cur_obj.language_id.id))
        if cur_obj.doctor_id:
            domain.append(('doctor_id','=',cur_obj.doctor_id.id))
        if cur_obj.location_id:
            domain.append(('location_id','ilike',cur_obj.location_id.id))
        if cur_obj.state_id:
            domain.append(('location_id.state_id', '=', cur_obj.state_id.id))
        if cur_obj.cancel_reason_id:
            if cur_obj.state == 'cancel':
                domain.append(('cancel_reason_id','=',cur_obj.cancel_reason_id.id))
        if cur_obj.event_id:
            domain.append(('event_id','ilike',cur_obj.event_id))
        if cur_obj.new_event_id:
            domain.append(('name','ilike',cur_obj.new_event_id))
        if cur_obj.event_type:
            if cur_obj.event_type != 'all':
                domain.append(('event_type','=',cur_obj.event_type))
        if cur_obj.state:
            if cur_obj.state != 'all':
                domain.append(('state','=',cur_obj.state))
        if cur_obj.start_date:
            domain.append(('event_start_date','>=',cur_obj.start_date))
        if cur_obj.end_date:
            domain.append(('event_start_date','<=',cur_obj.end_date))
        if cur_obj.zone_id:
            domain.append(('zone_id','=',cur_obj.zone_id.id))
        if cur_obj.cust_invoice_id:
            domain.append(('cust_invoice_id','=',cur_obj.cust_invoice_id.id))
        if cur_obj.supp_invoice_id:
            domain.append(('supp_invoice_ids','in',[cur_obj.supp_invoice_id.id]))
        domain.append(('company_id','=',cur_obj.company_id.id))
#        print "domain..........",domain
        event_ids = self.env['event'].sudo().search(domain)
#        print "event_ids..........",len(event_ids)
        self._cr.execute(''' truncate search_events_wizard_rel ''')
        if event_ids:
#            if cur_obj.interpreter_id.id:
#                cr.execute(''' select event_id from event_partner_rel where interpreter_id=%s and event_id in %s''',(cur_obj.interpreter_id.id,tuple(event_ids)))
#                event_ids= map(lambda x: x[0], cr.fetchall())
#                if event_ids:
#                    self.write(cr,uid,ids[0],{'flag':False,'label_flag':True,'result_set':[(6, 0, event_ids)]})
#                else:
#                    self.write(cr,uid,ids[0],{'flag':True,'label_flag':False})
#                    return True
                    
            self.write({'flag':False,'label_flag':True,'result_set':[(6, 0, event_ids.ids)]})
            return True
        else:
            self.write({'flag':True,'label_flag':False})
            return True
    

    name=fields.Char('Name',default='Event Search')
    start_date=fields.Date("Start date",default=lambda *a: time.strftime('%Y-01-01'))
    end_date=fields.Date("End date",default=lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
    scheduler_id=fields.Many2one('res.users','Scheduler', domain="[('user_type','=','staff')]")
    event_type=fields.Selection([('all','All'),('language','Language'),('transport','Transport'),('translation','Translation'),('lang_trans','Lang And Trans')],"Event Type",default='language')
    event_id=fields.Char("Event ID")
    partner_id=fields.Many2one('res.partner','Billing Customer')
    partner_id_2=fields.Many2one('res.partner','Billing Contact')
    patient_id=fields.Many2one('patient','Patient/Client')
    ordering_contact_id=fields.Many2one('res.partner','Ordering Contact')
    ordering_partner_id=fields.Many2one('res.partner','Ordering Customer')
    interpreter_id=fields.Many2one('res.partner','Interpreter')
    language_id=fields.Many2one('language','Language')
    doctor_id=fields.Many2one('doctor','Doctor')
    company_id=fields.Many2one('res.company', 'Company', required=True,default=lambda self: self.env['res.company']._company_default_get('search.events.wizard'))
    state=fields.Selection([
        ('all','All'),
        ('unapproved', 'Unappoved'),
        ('rejected', 'Rejected'),
        ('draft', 'Unscheduled'),
        ('scheduled', 'Job Offered'),
        ('allocated', 'Scheduled'),
        ('unauthorize','Unauthorize'),
        ('confirmed', 'Confirmed'),
        ('unbilled', 'Unbilled'),
        ('invoiced','Invoiced'),
        ('cancel','Cancelled'),
        ('done', 'Done')],'Status',default='all',)
    location_id=fields.Many2one("location",'Location Id' )
    new_event_id=fields.Char("Event ID")
    flag=fields.Boolean('Flag',default=True)
    label_flag=fields.Boolean('Flag',default=True)

#        'result_set':fields.many2many('event','search_events_wizard_rel','search_event_wizard_id','event_id','Event Search Result'),
    result_set= fields.Many2many('event' , 'search_events_wizard_rel','search_event_wizard_id','event_id', 'Event Search Result' , order='event_start asc')
    date_type=fields.Selection([
        ('date_range','Date Range'),
        ('past','Past Event'),
        ('current', 'Today Event'),
        ('future', 'Future Event'),
        ],'Event Date',default='date_range')

    zone_id=fields.Many2one('meta.zone','Zone')
    cancel_reason_id=fields.Many2one('cancel.reason', 'Cancel Reason', track_visibility='onchange')
    cust_invoice_id=fields.Many2one('account.invoice','Customer Invoice')
    supp_invoice_id=fields.Many2one('account.invoice','Supplier Invoice')
    state_id=fields.Many2one("res.country.state", 'State')
    

    @api.onchange('company_id')
    def onchange_company_id(self):
        ''' Empty some fields on change of company in the event Form '''
        val = {
            'partner_id': False ,
            'ordering_contact_id': False,
            'language_id': False ,
            'patient_id': False,
            'interpreter_id': False,
            'scheduler_id': False
            }
        return {'value': val}

    @api.onchange('date_type')
    def onchange_datetype(self):
        '''Date range selected based on date type '''
        vals={}
        if self.date_type:
            start_date = datetime.datetime.now()
            if self.date_type == 'past':
                default_past_date = datetime.datetime(2015, 1, 1)
                present_date=start_date
                days_diff=start_date-default_past_date
                
                days_diff=days_diff.days
                starting_date=start_date - datetime.timedelta(days=days_diff) 
                
                vals={'start_date':str(starting_date.strftime('%Y-%m-%d')),'end_date':str((start_date - datetime.timedelta(days=1)).strftime('%Y-%m-%d'))}
                #self.write(cr,SUPERUSER_ID,ids[0],{'start_date':starting_date.strftime('%y-%m-%d'),'end_date':start_date.strftime('%y-%m-%d')})
                
            elif self.date_type== 'current':
                vals={'start_date':str(start_date.strftime('%Y-%m-%d')),'end_date':str(start_date.strftime('%Y-%m-%d'))}
                     #self.write(cr,SUPERUSER_ID,ids[0],{'start_date':start_date.strftime('%y-%m-%d'),'end_date':start_date.strftime('%y-%m-%d')})
            elif self.date_type== 'future':
                future_date = start_date + datetime.timedelta(days=2190)
                vals={'start_date':str((start_date + datetime.timedelta(days=1)).strftime('%Y-%m-%d')),'end_date':str(future_date.strftime('%Y-%m-%d'))}
                #self.write(cr,SUPERUSER_ID,ids[0],{'start_date':start_date.strftime('%y-%m-%d'),'end_date':future_date.strftime('%y-%m-%d')})
                
            else:
                pass
            #import ipdb;ipdb.set_trace()    
            return {'value': vals}

class search_contact_wizard(models.TransientModel):
    """ A wizard to search contact """
    _name = 'search.contact.wizard'

    @api.onchange('contact_type')
    def onchange_contact(self):
       # import ipdb;ipdb.set_trace()
        if self.contact_type=='doctor':
            vals=self.env['doctor'].sudo().search([]).ids
            value={'doctor':vals}
            
        elif self.contact_type=='patient':
            vals=self.env['patient'].sudo().search([]).ids
            value={'patient':vals}

        elif self.contact_type=='interpreter':
            vals=self.env['res.partner'].sudo().search([('cust_type','in',['interpreter','interp_and_transl'])]).ids
            value={'interpreter_partner_id':vals}
        else:
            value={'partner_id':[]}
        return {'value': value}

    @api.multi
    def search_contact(self):
        #Truncate all many2many tables
#        import ipdb;ipdb.set_trace()
        user = self.env.user
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.utc
        local_date = tz.localize(datetime.datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),DATETIME_FORMAT), is_dst=None)
        local_date = datetime.datetime.strptime(local_date.astimezone (tz).strftime(DATETIME_FORMAT), DATETIME_FORMAT).strftime('%Y-%m-%d')
        self._cr.execute('''truncate search_contact_wizard_rel,search_partner_contact_wizard_rel,search_interpreter_wizard_rel,search_translator_wizard_rel,search_transporter_wizard_rel,search_contact_wizard_rel_doc,search_contact_wizard_rel_patient,search_events_result_rel''')
        self.write({'past_event_flag': True, 'future_event_flag': True})
        ##'interpreter','interp_and_transl'

        remove_rec=''' truncate search_contact_wizard cascade'''
        
                #if vals.get('contact_type') in ['customer','contact','translator','transporter'] and vals.get('partner_id'):
        if self.contact_type == 'customer' and self.partner_id:
            history_ids = self.env['event'].search(['|',('partner_id','=',self.partner_id.id),('ordering_partner_id','=',self.partner_id.id),\
                        ('event_start_date','=',local_date)]).ids
            
            #import ipdb;ipdb.set_trace()
            if history_ids :
                self.write({'cust_flag':False,'contact_flag':True,'inter_flag':True,'translator_flag':True,'transporter_flag':True,'doct_flag':True,'pat_flag':True,'label_flag':True,'cust_event_flag':True,'no_current_event_label_flag':True,'current_event_flag':False,'result_set':[(6, 0, [self.partner_id.id])],'current_event_result_set':[(6,0,history_ids)]})
            else:
                self.write({'cust_flag':False,'contact_flag':True,'inter_flag':True,'translator_flag':True,'transporter_flag':True,'doct_flag':True,'pat_flag':True,'label_flag':True,'cust_event_flag':True,'no_current_event_label_flag':False,'current_event_flag':True,'result_set':[(6, 0, [self.partner_id.id])]})
            #cr.execute(remove_rec)
            
        elif self.contact_type == 'contact' and self.partner_id:
            history_ids = self.env['event'].search([('contact_id','=',self.partner_id.id),\
                        ('event_start_date','=',local_date)]).ids
            if history_ids :
                self.write({'cust_flag':True,'contact_flag':False,'inter_flag':True,'translator_flag':True,'transporter_flag':True,'doct_flag':True,'pat_flag':True,'label_flag':True,'cust_event_flag':True,'no_current_event_label_flag':True,'current_event_flag':False,'current_event_result_set':[(6,0,history_ids)],'result_set_contact':[(6, 0, [self.partner_id.id])]})
            else:            
            
                self.write({'cust_flag':True,'contact_flag':False,'inter_flag':True,'translator_flag':True,'transporter_flag':True,'doct_flag':True,'pat_flag':True,'label_flag':True,'cust_event_flag':True,'no_current_event_label_flag':False,'current_event_flag':True,'result_set_contact':[(6, 0, [self.partner_id.id])]})
        
        elif self.contact_type == 'translator' and self.partner_id:
            history_ids = self.env['event'].search([('translator_id','=',self.partner_id.id),\
                        ('event_start_date','=',local_date)]).ids
            if history_ids:
                
                self.write({'cust_flag':True,'contact_flag':True,'inter_flag':True,'translator_flag':False,'transporter_flag':True,'doct_flag':True,'pat_flag':True,'label_flag':True,'cust_event_flag':True,'no_current_event_label_flag':True,'current_event_flag':False,'current_event_result_set':[(6,0,history_ids)],'result_set_translator':[(6, 0, [self.partner_id.id])]})
            else:
                self.write({'cust_flag':True,'contact_flag':True,'inter_flag':True,'translator_flag':False,'transporter_flag':True,'doct_flag':True,'pat_flag':True,'label_flag':True,'cust_event_flag':True,'no_current_event_label_flag':False,'current_event_flag':True,'result_set_translator':[(6, 0, [self.partner_id.id])]})
        
        elif self.contact_type=='interpreter' and self.interpreter_partner_id:
            
            self._cr.execute(''' select event_id from event_partner_rel where interpreter_id =%s'''%self.interpreter_partner_id.id)
            
            master_event_id= map(lambda x: x[0], self._cr.fetchall())
            if master_event_id:
                self._cr.execute(''' select id from event where id in %s and event_start_date=%s''',(tuple(master_event_id),local_date),)
                history_ids=map(lambda x: x[0], self._cr.fetchall())
            #history_ids = self.pool.get('event').search(cr ,uid ,[('interpreter_id','=',vals.get('interpreter_partner_id')[0]),('event_start_date','=',fields.date.context_today(self,cr,uid,context=context))])
            else:
                history_ids=[]
                
            if history_ids:
#            self.write(cr,uid,ids[0],{'cust_flag':False,'doct_flag':True,'pat_flag':True,'label_flag':True,'result_set':[(6, 0, [vals.get('interpreter_partner_id')[0]])]})

                self.write({'cust_flag':True,'contact_flag':True,'inter_flag':False,'translator_flag':True,'transporter_flag':True,'doct_flag':True,'pat_flag':True,'label_flag':True,'cust_event_flag':True,'no_current_event_label_flag':True,'current_event_flag':False,'current_event_result_set':[(6,0,history_ids)],'result_set_interpreter':[(6, 0, [self.interpreter_partner_id.id])]})
            else:
                self.write({'cust_flag':True,'contact_flag':True,'inter_flag':False,'translator_flag':True,'transporter_flag':True,'doct_flag':True,'pat_flag':True,'label_flag':True,'cust_event_flag':True,'no_current_event_label_flag':False,'current_event_flag':True,'result_set_interpreter':[(6, 0, [self.interpreter_partner_id.id])]})
            

        elif self.contact_type == 'transporter' and self.partner_id:
            history_ids = self.env['event'].search([('transporter_id','=',self.partner_id.id),\
                        ('event_start_date','=',local_date)]).ids
            if history_ids:
                
                self.write({'cust_flag':True,'contact_flag':True,'inter_flag':True,'translator_flag':True,'transporter_flag':False,'doct_flag':True,'pat_flag':True,'label_flag':True,'cust_event_flag':True,'no_current_event_label_flag':True,'current_event_flag':False,'current_event_result_set':[(6,0,history_ids)],'result_set_transporter':[(6, 0, [self.partner_id.id])]})
            else:
                self.write({'cust_flag':True,'contact_flag':True,'inter_flag':True,'translator_flag':True,'transporter_flag':False,'doct_flag':True,'pat_flag':True,'label_flag':True,'cust_event_flag':True,'no_current_event_label_flag':False,'current_event_flag':True,'result_set_transporter':[(6, 0, [self.partner_id.id])]})
                            
            
        
        
        elif self.contact_type=='doctor' and self.doctor_id:
            history_ids = self.env['event'].search([('doctor_id','=',self.doctor_id.id),\
                        ('event_start_date','=',local_date)]).ids
            if history_ids:
            #self.write(cr,uid,ids[0],{'doct_flag':False,'cust_flag':True,'pat_flag':True,'label_flag':True,'result_set_doctor':[(6, 0, [vals.get('doctor_id')[0]])]})
                self.write({'cust_flag':True,'contact_flag':True,'inter_flag':True,'translator_flag':True,'transporter_flag':True,'doct_flag':False,'pat_flag':True,'label_flag':True,'cust_event_flag':True,'no_current_event_label_flag':True,'current_event_flag':False,'current_event_result_set':[(6,0,history_ids)],'result_set_doctor':[(6, 0, [self.doctor_id.id])]})
            else:
                self.write({'cust_flag':True,'contact_flag':True,'inter_flag':True,'translator_flag':True,'transporter_flag':True,'doct_flag':False,'pat_flag':True,'label_flag':True,'cust_event_flag':True,'no_current_event_label_flag':False,'current_event_flag':True,'result_set_doctor':[(6, 0, [self.doctor_id.id])]})
                        
        
        elif self.contact_type=='patient'  and self.patient_id:
            #self.write(cr,uid,ids[0],{'pat_flag':False,'cust_flag':True,'doct_flag':True,'label_flag':True,'result_set_patient':[(6, 0, [vals.get('patient_id')[0]])]})
            history_ids = self.env['event'].search([('patient_id','=',self.patient_id.id),\
                        ('event_start_date','=',local_date)]).ids
            if history_ids:
                self.write({'cust_flag':True,'contact_flag':True,'inter_flag':True,'translator_flag':True,'transporter_flag':True,'doct_flag':True,'pat_flag':False,'label_flag':True,'cust_event_flag':True,'no_current_event_label_flag':True,'current_event_flag':False,'current_event_result_set':[(6,0,history_ids)],'result_set_transporter':[(6, 0, [self.patient_id.id])]})
            else:
                self.write({'cust_flag':True,'contact_flag':True,'inter_flag':True,'translator_flag':True,'transporter_flag':True,'doct_flag':True,'pat_flag':False,'label_flag':True,'cust_event_flag':True,'no_current_event_label_flag':False,'current_event_flag':True,'result_set_transporter':[(6, 0, [self.patient_id.id])]})
        else:
            #self.write(cr,uid,ids[0],{'cust_flag':True,'doct_flag':True,'pat_flag':True,'label_flag':False})
            self.write({'cust_flag':True,'contact_flag':True,'inter_flag':True,'translator_flag':True,'transporter_flag':True,'doct_flag':True,'pat_flag':True,'label_flag':False,'cust_event_flag':True,'no_current_event_label_flag':True,'current_event_flag':True})
            

    name=fields.Char('Name',default='Contact Search')
    contact_type=fields.Selection([('customer','Customer'),('contact','Contact'),('interpreter','Interpreter'),
                ('translator','Translator'),('transporter','Transporter'),
                ('doctor','Doctor'),('patient','Patient')],
                "Contact Type" ,required=False , help="This categorizes ,what kind of partner it is " )
    partner_id=fields.Many2one('res.partner','Contact Person')
    interpreter_partner_id=fields.Many2one('res.partner','Interpreter Person')
    doctor_id=fields.Many2one('doctor','Doctor Contact')
    patient_id=fields.Many2one('patient','Patient Contact')
    cust_flag=fields.Boolean('Cust Flag',default=True)
    contact_flag=fields.Boolean('Contact Flag',default=True)
    inter_flag=fields.Boolean('interpreter Flag',default=True)
    translator_flag=fields.Boolean('Translator Flag',default=True)
    transporter_flag=fields.Boolean('Transporter Flag',default=True)
    doct_flag=fields.Boolean('Doct Flag',default=True)
    pat_flag=fields.Boolean('Pat Flag',default=True)
    label_flag=fields.Boolean('Label Flag',default=True)
    cust_event_flag=fields.Boolean('Cust Event Flag',default=True)
    current_event_flag=fields.Boolean('Current Event Flag',default=True)
    no_current_event_label_flag=fields.Boolean('No Current Event Flag',default=True)
    past_event_flag=fields.Boolean('Past Event Flag',default=True)
    future_event_flag=fields.Boolean('Future Event Flag',default=True)
    result_set=fields.Many2many('res.partner','search_contact_wizard_rel','search_contact_wizard_id','event_id','Event Search Result')
    result_set_contact=fields.Many2many('res.partner','search_partner_contact_wizard_rel','search_contact_wizard_id','event_id','Partner contact Search Result')
    result_set_interpreter=fields.Many2many('res.partner','search_interpreter_wizard_rel','search_contact_wizard_id','event_id','Interpreter contact Search Result')
    result_set_translator=fields.Many2many('res.partner','search_translator_wizard_rel','search_contact_wizard_id','event_id','Translator contact Search Result')
    result_set_transporter=fields.Many2many('res.partner','search_transporter_wizard_rel','search_contact_wizard_id','event_id','Transporter contact Search Result')
    result_set_doctor=fields.Many2many('doctor','search_contact_wizard_rel_doc','search_contact_wizard_id','doctor_id','Doctor Contact Search Result')
    result_set_patient=fields.Many2many('patient','search_contact_wizard_rel_patient','search_contact_wizard_id','patient','Patient Contact Search Result')
    event_result_set=fields.Many2many('event','search_events_result_rel','search_event_result_id','event_id','Event Search Result')
    current_event_result_set=fields.Many2many('event','search_current_events_result_rel','search_event_result_id','event_id','Current Event Search Result')

    
class res_partner(models.Model):
    _inherit='res.partner'
    
    @api.model
    def refresh_my_page(self):
            check_in_type = self._context.get('check_in_type','')
            mod_obj = self.env['ir.model.data']
            
            form_id = mod_obj.get_object_reference('bista_iugroup', 'search_contact_wizard_form')
            #import ipdb;ipdb.set_trace()
            form_res = form_id and form_id[1] or False
            #context['called_from'] ='view_profile'
          #  import ipdb;ipdb.set_trace()
            return {
                'name':_("Patient Profile"),
                'view_mode': 'form',
                'res_id': self._context.get('active_id'),
                'view_type': 'form',
                'res_model': 'search.contact.wizard',
                'type': 'ir.actions.act_window',
                'nodestroy':False,
                'view_id': (form_res,'View'),
                'views': [(form_res, 'form')],
                'context': self._context,
                'target':'current'
                    }
    @api.multi
    def search_customer_past_event(self):
        ''' Search partner past events '''
        user = self.env.user
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.utc
        local_date = tz.localize(datetime.datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),DATETIME_FORMAT), is_dst=None)
        local_date = datetime.datetime.strptime(local_date.astimezone (tz).strftime(DATETIME_FORMAT), DATETIME_FORMAT).strftime('%Y-%m-%d')
        
        search_contact_obj=self.env['search.contact.wizard']
        #Truncate all many2many tables
        self._cr.execute('''truncate search_events_result_rel''')
        part = self
        search_contact_rec=search_contact_obj.browse(self._context.get('active_id'))
        contact_type=search_contact_rec.contact_type
        #import ipdb;ipdb.set_trace()
        if contact_type == 'customer':
#            import ipdb;ipdb.set_trace()
            history_ids = self.env['event'].search([('partner_id','=',part.id),\
                        ('event_start_date','<',local_date)])
            if history_ids:
                search_contact_rec.write({'cust_flag':False,'contact_flag':True,'inter_flag':True,'translator_flag':True,'transporter_flag':True,'doct_flag':True,'pat_flag':True,'label_flag':True,'cust_event_flag':False,'past_event_flag':False,'future_event_flag':True,'event_result_set':[(6, 0, history_ids)]})
            else:
                search_contact_rec.write({'cust_flag':False,'contact_flag':True,'inter_flag':True,'translator_flag':True,'transporter_flag':True,'doct_flag':True,'pat_flag':True,'label_flag':False,'cust_event_flag':True,'past_event_flag':True,'future_event_flag':True})
        elif contact_type == 'contact' :
            history_ids = self.env['event'].search([('contact_id','=',part.id),\
                        ('event_start_date','<',local_date)])
            if history_ids:
                search_contact_rec.write({'cust_flag':True,'contact_flag':False,'inter_flag':True,'translator_flag':True,'transporter_flag':True,'doct_flag':True,'pat_flag':True,'label_flag':True,'cust_event_flag':False,'past_event_flag':False,'future_event_flag':True,'event_result_set':[(6, 0, history_ids)]})
            else:
                search_contact_rec.write({'cust_flag':True,'contact_flag':False,'inter_flag':True,'translator_flag':True,'transporter_flag':True,'doct_flag':True,'pat_flag':True,'label_flag':False,'cust_event_flag':True,'past_event_flag':True,'future_event_flag':True})
            
        elif contact_type == 'translator':
            history_ids = self.env['event'].search([('translator_id','=',part.id),\
                        ('event_start_date','<',local_date)])
            if history_ids:
                search_contact_rec.write({'cust_flag':True,'contact_flag':True,'inter_flag':True,'translator_flag':False,'transporter_flag':True,'doct_flag':True,'pat_flag':True,'label_flag':True,'cust_event_flag':False,'past_event_flag':False,'future_event_flag':True,'event_result_set':[(6, 0, history_ids)]})
            else:
                search_contact_rec.write({'cust_flag':True,'contact_flag':True,'inter_flag':True,'translator_flag':False,'transporter_flag':True,'doct_flag':True,'pat_flag':True,'label_flag':False,'cust_event_flag':True,'past_event_flag':True,'future_event_flag':True})
                
        elif contact_type == 'interpreter':
            self._cr.execute(''' select event_id from event_partner_rel where interpreter_id =%s''',(part.id,))
            master_event_id= map(lambda x: x[0], self._cr.fetchall())
            if master_event_id:
                self._cr.execute(''' select id from event where id in %s and event_start_date < %s''',(tuple(master_event_id),local_date), )
                history_ids=map(lambda x: x[0], self._cr.fetchall())
            #history_ids = self.pool.get('event').search(cr ,uid ,[('interpreter_id','=',vals.get('interpreter_partner_id')[0]),('event_start_date','=',fields.date.context_today(self,cr,uid,context=context))])
            else:
                history_ids=[]            
            if history_ids:
                search_contact_rec.write({'cust_flag':True,'contact_flag':True,'inter_flag':False,'translator_flag':True,'transporter_flag':True,'doct_flag':True,'pat_flag':True,'label_flag':True,'cust_event_flag':False,'past_event_flag':False,'future_event_flag':True,'event_result_set':[(6, 0, history_ids)]})
            else:
                search_contact_rec.write({'cust_flag':True,'contact_flag':True,'inter_flag':False,'translator_flag':True,'transporter_flag':True,'doct_flag':True,'pat_flag':True,'label_flag':False,'cust_event_flag':True,'past_event_flag':True,'future_event_flag':True})
        elif contact_type== 'transporter':
            history_ids = self.env['event'].search([('transporter_id','=',part.id),\
                        ('event_start_date','<',local_date)])
            if history_ids:
                search_contact_rec.write({'cust_flag':True,'contact_flag':True,'inter_flag':True,'translator_flag':True,'transporter_flag':False,'doct_flag':True,'pat_flag':True,'label_flag':True,'cust_event_flag':False,'past_event_flag':False,'future_event_flag':True,'event_result_set':[(6, 0, history_ids)]})
            else:
                search_contact_rec.write({'cust_flag':True,'contact_flag':True,'inter_flag':True,'translator_flag':True,'transporter_flag':False,'doct_flag':True,'pat_flag':True,'label_flag':False,'cust_event_flag':True,'past_event_flag':True,'future_event_flag':True})
        else:
            raise UserError(_(' Please Select Contact Type .'))
        
        return self.refresh_my_page()

    @api.multi
    def search_customer_future_event(self):
        ''' Search Partner's future events'''
        user = self.env.user
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.utc
        local_date = tz.localize(datetime.datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),DATETIME_FORMAT), is_dst=None)
        local_date = datetime.datetime.strptime(local_date.astimezone (tz).strftime(DATETIME_FORMAT), DATETIME_FORMAT).strftime('%Y-%m-%d')
        
        search_contact_obj=self.env['search.contact.wizard']
        #Truncate all many2many tables
        self._cr.execute('''truncate search_events_result_rel''')
        
        part=self
        search_contact_rec = search_contact_obj.browse(self._context.get('active_id'))
        contact_type = search_contact_rec.contact_type
        #import ipdb;ipdb.set_trace()
        if contact_type == 'customer' :
            history_ids = self.env['event'].search(['|',('partner_id','=',part.id),('ordering_partner_id','=',part.id),\
                        ('event_start_date','>=',local_date)])
            if history_ids:
                search_contact_rec.write({'cust_flag':False,'contact_flag':True,'inter_flag':True,'translator_flag':True,'transporter_flag':True,'doct_flag':True,'pat_flag':True,'label_flag':True,'cust_event_flag':False,'past_event_flag':True,'future_event_flag':False,'event_result_set':[(6, 0, history_ids)]})
            else:
                search_contact_rec.write({'cust_flag':False,'contact_flag':True,'inter_flag':True,'translator_flag':True,'transporter_flag':True,'doct_flag':True,'pat_flag':True,'label_flag':False,'cust_event_flag':True,'past_event_flag':True,'future_event_flag':True})

        elif contact_type == 'contact' :
            history_ids = self.env['event'].search([('contact_id','=',part.id),\
                        ('event_start_date','>=',local_date)])
            if history_ids:
                search_contact_rec.write({'cust_flag':True,'contact_flag':False,'inter_flag':True,'translator_flag':True,'transporter_flag':True,'doct_flag':True,'pat_flag':True,'label_flag':True,'cust_event_flag':False,'past_event_flag':True,'future_event_flag':False,'event_result_set':[(6, 0, history_ids)]})
            else:
                search_contact_rec.write({'cust_flag':True,'contact_flag':False,'inter_flag':True,'translator_flag':True,'transporter_flag':True,'doct_flag':True,'pat_flag':True,'label_flag':False,'cust_event_flag':True,'past_event_flag':True,'future_event_flag':True})
           
        elif contact_type == 'translator':
            history_ids = self.env['event'].search([('translator_id','=',part.id),\
                        ('event_start_date','>=',local_date)])
            if history_ids:
                search_contact_rec.write({'cust_flag':True,'contact_flag':True,'inter_flag':True,'translator_flag':False,'transporter_flag':True,'doct_flag':True,'pat_flag':True,'label_flag':True,'cust_event_flag':False,'past_event_flag':True,'future_event_flag':False,'event_result_set':[(6, 0, history_ids)]})
            else:
                search_contact_rec.write({'cust_flag':True,'contact_flag':True,'inter_flag':True,'translator_flag':False,'transporter_flag':True,'doct_flag':True,'pat_flag':True,'label_flag':False,'cust_event_flag':True,'past_event_flag':True,'future_event_flag':True})
            
             
            
        elif contact_type == 'interpreter':
            
            self._cr.execute(''' select event_id from event_partner_rel where interpreter_id = %s''',(part.id,))
            
            master_event_id= map(lambda x: x[0], self._cr.fetchall())
            
            if master_event_id:
                self._cr.execute(''' select id from event where id in %s and event_start_date >= %s''',(tuple(master_event_id),local_date), )
                history_ids=map(lambda x: x[0], self._cr.fetchall())
            #history_ids = self.pool.get('event').search(cr ,uid ,[('interpreter_id','=',vals.get('interpreter_partner_id')[0]),('event_start_date','=',fields.date.context_today(self,cr,uid,context=context))])
            else:
                history_ids=[]            
            if history_ids:
                search_contact_rec.write({'cust_flag':True,'contact_flag':True,'inter_flag':False,'translator_flag':True,'transporter_flag':True,'doct_flag':True,'pat_flag':True,'label_flag':True,'cust_event_flag':False,'past_event_flag':True,'future_event_flag':False,'event_result_set':[(6, 0, history_ids)]})
            else:
                search_contact_rec.write({'cust_flag':True,'contact_flag':True,'inter_flag':False,'translator_flag':True,'transporter_flag':True,'doct_flag':True,'pat_flag':True,'label_flag':False,'cust_event_flag':True,'past_event_flag':True,'future_event_flag':True})
                
                            
        elif contact_type== 'transporter':
            history_ids = self.env['event'].search([('transporter_id','=',part.id),\
                        ('event_start_date','>=',local_date)])
            if history_ids:
                search_contact_rec.write({'cust_flag':True,'contact_flag':True,'inter_flag':True,'translator_flag':True,'transporter_flag':False,'doct_flag':True,'pat_flag':True,'label_flag':True,'cust_event_flag':False,'past_event_flag':True,'future_event_flag':False,'event_result_set':[(6, 0, history_ids)]})
            else:
                search_contact_rec.write({'cust_flag':True,'contact_flag':True,'inter_flag':True,'translator_flag':True,'transporter_flag':False,'doct_flag':True,'pat_flag':True,'label_flag':False,'cust_event_flag':True,'past_event_flag':True,'future_event_flag':True})
            
        else:
           
            raise UserError(_(' Please Select Contact Type .'))
    
#         if history_ids:
#             
#              search_contact_obj.write(cr,uid,context.get('active_id'),{'cust_flag':False,'contact_flag':True,'inter_flag':True,'translator_flag':True,'transporter_flag':True,'doct_flag':True,'pat_flag':True,'label_flag':True,'cust_event_flag':False,'event_result_set':[(6, 0, history_ids)]})
#             
#         else:
#              search_contact_obj.write(cr,uid,context.get('active_id'),{'cust_flag':False,'contact_flag':True,'inter_flag':True,'translator_flag':True,'transporter_flag':True,'doct_flag':True,'pat_flag':True,'label_flag':False,'cust_event_flag':True})
        
        return self.refresh_my_page()

class patient(models.Model):
    _inherit='patient'

    @api.model
    def refresh_my_page(self):
            mod_obj = self.pool.get('ir.model.data')
            form_id = mod_obj.get_object_reference('bista_iugroup', 'search_contact_wizard_form')
            form_res = form_id and form_id[1] or False
            return {
                'name':_("Patient Profile"),
                'view_mode': 'form',
                'res_id': self._context.get('active_id'),
                'view_type': 'form',
                'res_model': 'search.contact.wizard',
                'type': 'ir.actions.act_window',
                'nodestroy':False,
                'view_id': (form_res,'View'),
                'views': [(form_res, 'form')],
                'context': self._context,
                'target':'current'
                    }    

    @api.multi
    def search_patient_past_event(self):
        '''search patient past events'''
        user = self.env.user
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.utc
        local_date = tz.localize(datetime.datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),DATETIME_FORMAT), is_dst=None)
        local_date = datetime.datetime.strptime(local_date.astimezone (tz).strftime(DATETIME_FORMAT), DATETIME_FORMAT).strftime('%Y-%m-%d')
        search_contact_obj=self.env['search.contact.wizard']
        self._cr.execute('''truncate search_events_result_rel''')
        
        part=self
        history_ids = self.env['event'].search([('patient_id','=',part.id),\
                    ('event_start_date','<',local_date)])
        search_contact_rec = search_contact_obj.browse(self._context.get('active_id'))
        if history_ids :
            
            search_contact_rec.write({'cust_flag':True,'contact_flag':True,'inter_flag':True,'translator_flag':True,'transporter_flag':True,'doct_flag':False,'pat_flag':True,'label_flag':True,'cust_event_flag':False,'past_event_flag':False,'future_event_flag':True,'event_result_set':[(6, 0, history_ids)]})
            
        else :
            
            search_contact_rec.write({'cust_flag':True,'contact_flag':True,'inter_flag':True,'translator_flag':True,'transporter_flag':True,'doct_flag':False,'pat_flag':True,'label_flag':False,'cust_event_flag':True})
        
        return self.refresh_my_page()

    @api.multi
    def search_patient_future_event(self):
        '''search patient future events'''
        user = self.env.user
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.utc
        local_date = tz.localize(datetime.datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),DATETIME_FORMAT), is_dst=None)
        local_date = datetime.datetime.strptime(local_date.astimezone (tz).strftime(DATETIME_FORMAT), DATETIME_FORMAT).strftime('%Y-%m-%d')
        
        search_contact_obj=self.env['search.contact.wizard']
        #Truncate all many2many tables
        self._cr.execute('''truncate search_events_result_rel''')
        
        part=self
        history_ids = self.env['event'].search([('patient_id','=',part.id),\
                        ('event_start_date','>=',local_date)])
        search_contact_rec = search_contact_obj.browse(self._context.get('active_id'))
        if history_ids :
            search_contact_rec.write({'cust_flag':True,'contact_flag':True,'inter_flag':True,'translator_flag':True,
                                    'transporter_flag':True,'doct_flag':True,'pat_flag':False,'label_flag':True,'cust_event_flag':False,'past_event_flag':True,'future_event_flag':False,'event_result_set':[(6, 0, history_ids)]})
        else:
            search_contact_rec.write({'cust_flag':True,'contact_flag':True,'inter_flag':True,'translator_flag':True,
                                    'transporter_flag':True,'doct_flag':True,'pat_flag':False,'label_flag':False,'cust_event_flag':True,'past_event_flag':True,'future_event_flag':True})
        return self.refresh_my_page()
        


class doctor(models.Model):
    _inherit='doctor'

    def refresh_my_page(self):
            mod_obj = self.env['ir.model.data']
            form_id = mod_obj.get_object_reference('bista_iugroup', 'search_contact_wizard_form')
            form_res = form_id and form_id[1] or False
            return {
                'name':_("Doctor Profile"),
                'view_mode': 'form',
                'res_id': self._context.get('active_id'),
                'view_type': 'form',
                'res_model': 'search.contact.wizard',
                'type': 'ir.actions.act_window',
                'nodestroy':False,
                'view_id': (form_res,'View'),
                'views': [(form_res, 'form')],
                'context': self._context,
                'target':'current'
                    }    

    @api.multi
    def search_doctor_past_event(self):
        '''search patient past events'''
        user = self.env.user
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.utc
        local_date = tz.localize(datetime.datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),DATETIME_FORMAT), is_dst=None)
        local_date = datetime.datetime.strptime(local_date.astimezone (tz).strftime(DATETIME_FORMAT), DATETIME_FORMAT).strftime('%Y-%m-%d')
        
        search_contact_obj=self.env['search.contact.wizard']
        #Truncate all many2many tables
        self._cr.execute('''truncate search_events_result_rel''')
        
        part=self
        history_ids = self.env['event'].search([('doctor_id','=',part.id),\
                    ('event_start_date','<',local_date)])
        search_contact_rec = search_contact_obj.browse(self._context.get('active_id'))
       # import ipdb;ipdb.set_trace()
        if history_ids :
            
            search_contact_rec.write({'cust_flag':True,'contact_flag':True,'inter_flag':True,'translator_flag':True,
                                    'transporter_flag':True,'doct_flag':False,'pat_flag':True,'label_flag':True,'cust_event_flag':False,'past_event_flag':False,'future_event_flag':True,'event_result_set':[(6, 0, history_ids)]})
        else:
            search_contact_rec.write({'cust_flag':True,'contact_flag':True,'inter_flag':True,'translator_flag':True,'transporter_flag':True,'doct_flag':False,'pat_flag':True,'label_flag':False,'cust_event_flag':True,'past_event_flag':True,'future_event_flag':True})
        
        return self.refresh_my_page()

    @api.multi
    def search_doctor_future_event(self):
        '''search patient future events'''
        user = self.env.user
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
        else:
            tz = pytz.utc
        local_date = tz.localize(datetime.datetime.strptime(str(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),DATETIME_FORMAT), is_dst=None)
        local_date = datetime.datetime.strptime(local_date.astimezone (tz).strftime(DATETIME_FORMAT), DATETIME_FORMAT).strftime('%Y-%m-%d')
        
        search_contact_obj=self.env['search.contact.wizard']
        self._cr.execute('''truncate search_events_result_rel''')
        #cr.execute('''truncate search_contact_wizard_rel,search_partner_contact_wizard_rel,search_interpreter_wizard_rel,search_translator_wizard_rel,search_transporter_wizard_rel,search_contact_wizard_rel_doc,search_contact_wizard_rel_patient,search_events_result_rel''')
        
        part=self
        history_ids = self.env['event'].search([('doctor_id','=',part.id),\
                      ('event_start_date','>=',local_date)])
        search_contact_rec = search_contact_obj.browse(self._context.get('active_id'))
        if history_ids :
            
            search_contact_rec.write({'cust_flag':True,'contact_flag':True,'inter_flag':True,'translator_flag':True,'transporter_flag':True,'doct_flag':False,'pat_flag':True,'label_flag':True,'cust_event_flag':False,'past_event_flag':True,'future_event_flag':False,'event_result_set':[(6, 0, history_ids)]})
        else:
            search_contact_rec.write({'cust_flag':True,'contact_flag':True,'inter_flag':True,'translator_flag':True,'transporter_flag':True,'doct_flag':False,'pat_flag':True,'label_flag':False,'cust_event_flag':True,'past_event_flag':True,'future_event_flag':True})
        return self.refresh_my_page()


