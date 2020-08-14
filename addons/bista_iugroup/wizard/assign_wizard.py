from odoo import fields,models,api
from odoo.tools.translate import _
import time
from odoo.tools import flatten
import urllib
import re
import datetime
from odoo import tools
from odoo.exceptions import UserError

class select_interpreter(models.Model):
    _name = 'select.interpreter'

    name=fields.Char(related='interpreter_id.name', string='Name',store=True)
    middle_name=fields.Char(related='interpreter_id.middle_name',  string='Middle Name',store=True)
    last_name=fields.Char(related='interpreter_id.last_name', string='Last Name',store=True)
    zip=fields.Char(related='interpreter_id.zip', string='Zip',store=True)
    rate=fields.Float(related='interpreter_id.rate', string='Rate',store=True)
    interpreter_id=fields.Many2one("hr.employee",'Interpreter')
    #'assign_id': fields.many2one("assign.interpreter",'Assign Interpreter', ondelete="CASCADE" ),
    select=fields.Boolean("Select")
    event_id=fields.Many2one('event',"Event Id", )
    visited=fields.Boolean("Visited")
    visited_date=fields.Date("Visited Date")
    voicemail_msg=fields.Char("Voicemail Message", size=128,default='')
    state=fields.Selection([
        ('draft', 'Unscheduled'),
        ('voicemailsent', 'Voicemail Sent'),
        ('scheduled', 'Scheduled'),
        ('allocated', 'Allocated'),
        ('confirmed', 'Confirmed'),
        ('unbilled', 'Unbilled'),
        ('cancel','Cancelled'),
        ('done', 'Done')],
        'Status', readonly=True, required=True,default='draft')

    @api.multi
    def leave_voicemail(self):
        ''' This function updates or assigns interpreter in the event form '''
        res= []
        cur_obj = self
        event = cur_obj.event_id
        self.write({'state': 'voicemailsent'})
        event_browse = event
        #print "event update........",event
        print "cur_obj.voicemail_msg......",cur_obj.voicemail_msg
        if not cur_obj.voicemail_msg:
            raise UserError(_('You must enter Voicemail Message first.'))
        res =event.write({'state':'scheduled'})
        event_start = datetime.datetime.strptime(event_browse.event_start, tools.DEFAULT_SERVER_DATETIME_FORMAT)
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        from_dt = datetime.datetime.strptime(str(event_start), DATETIME_FORMAT)
        self.env['interpreter.history'].create({'partner_id':event_browse.partner_id and event_browse.partner_id.id or False,
                    'name':cur_obj.interpreter_id and cur_obj.interpreter_id.id or False,'event_id':event.id,'event_date': from_dt.strftime('%Y-%m-%d'),
                    'state':'voicemailsent' , 'voicemail_msg':cur_obj.voicemail_msg})
        return res

#    def update_interpreter(self, cr, uid, ids, context):
#        ''' This function updates or assigns interpreter in the event form '''
#        res= []
#        cur_obj = self.browse(cr ,uid ,ids[0])
#        self.write(cr ,uid ,ids ,{'state': 'voicemailsent'} )
#        #event = cur_obj.event_id
#        #print "event update........",event
##        print "cur_obj.voicemail_msg......",cur_obj.voicemail_msg
##        res = self.pool.get('event').write(cr ,uid , [event.id],{'interpreter_id':cur_obj.interpreter_id and cur_obj.interpreter_id.id or False,
##        'state':'allocated'})
##        if cur_obj.interpreter_id and cur_obj.interpreter_id.id:
##            self.pool.get('hr.employee').write(cr ,uid , [cur_obj.interpreter_id.id],{'voicemail_msg':cur_obj.voicemail_msg})
#        return res

    @api.multi
    def update_interpreter(self):
        ''' This function updates or assigns interpreter in the event form '''
        res= []
        cur_obj = self
        event = cur_obj.event_id
        #print "event update........",event
        print "cur_obj.voicemail_msg......",cur_obj.voicemail_msg
        res = event.write({'interpreter_id':cur_obj.interpreter_id and cur_obj.interpreter_id.id or False,
        'state':'allocated'})
#        if cur_obj.interpreter_id and cur_obj.interpreter_id.id:
#            self.pool.get('hr.employee').write(cr ,uid , [cur_obj.interpreter_id.id],{'voicemail_msg':cur_obj.voicemail_msg})
        return res

#    def default_get(self, cr, uid, fields, context=None):
#        print "default_get..line......"
#        #cr.execute('insert into relation_name (self_id,module_name_id) values(%s,%s)',(first_value,second_value)
#        if context is None: context = {}
#        res = super(select_interpreter, self).default_get(cr, uid, fields, context=context)
#        event_ids = context.get('event_ids', [])
#        print "event_ids........",event_ids
#        voicemail_msg = context.get('voicemail_msg', False)
#
#        if voicemail_msg:
#            if 'voicemail_msg' in fields:
#                res.update(voicemail_msg = voicemail_msg)
#
#        print "res.......",res
#        return res


    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            zip = record.zip
            if zip:
                name = record.name
                name = name + ' ' + (record.middle_name or '')
                name = name + ' ' + (record.last_name or '')
                name =  "%s, [%s] " % (name , zip)
            else:
                name = record.name
                name = name + ' ' + (record.middle_name or '')
                name = name + ' ' + (record.last_name or '')
            rate = record.rate
            if rate > 0:
                name =  "%s, [%s]" % (name , rate)
            res.append((record.id, name))
        return res
    
    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        #print "operator.....name....args..",operator,name,args
        #interpreter_obj = self.pool.get('hr.employee')
        if not args:
            args = []
        if name:
            ids = self.search(cr, user, [('name','=',name)]+ args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, user, [('middle_name','=',name)]+ args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, user, [('last_name','=',name)]+ args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, user, [('zip','=',name)]+ args, limit=limit, context=context)
            if not ids:
                ids = set()
                ids.update(self.search(cr, user, args + [('name',operator,name)], limit=limit, context=context))
                ids.update(self.search(cr, user, args + [('middle_name',operator,name)], limit=limit, context=context))
                ids.update(self.search(cr, user, args + [('last_name',operator,name)], limit=limit, context=context))
                #print "ids.......",ids
#                query = "select id from hr_employee where zip::text like %s "%( str(name) + '%')
#                #convert(char(32), zip),CAST(zip AS TEXT)
#                cr.execute(query )
#                ids.update(map(lambda x: x[0], cr.fetchall()))
                ids.update(self.search(cr, user, args + [('zip',operator,name)], limit=limit, context=context))
                if not limit or len(ids) < limit:
                    # we may underrun the limit because of dupes in the results, that's fine
                    ids.update(self.search(cr, user, args + [('name',operator,name)], limit=(limit and (limit-len(ids)) or False) , context=context))
                ids = list(ids)
            if not ids:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    ids = self.search(cr, user, [('name','=', res.group(2))] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, [], limit=limit, context=context)
        #print "ids..last........",ids
        result = self.name_get(cr, user, ids, context=context)
        return result

class assign_interpreter(osv.osv_memory):
    """ A wizard to assign interpreter to event """
    _name = 'assign.interpreter'
    
#    def message_open(self , cr ,uid , ids , context=None):
#        res = self.pool.get('warning').warning(cr ,uid ,title='Title', message='Text' )
#        return res
    def update_interpreter(self, cr, uid, ids, context):
        ''' This function updates or assigns interpreter in the event form '''
        res= []
        cur_obj = self.browse(cr ,uid ,ids[0])

#        if not interpreter2:
#            raise osv.except_osv(_('Warning!'),_('You must select an Interpreter to assign to this event.'))
        #print "interpreter.......",interpreter
        event_ids = context.get('active_ids', [])
        #print "event_ids......",event_ids
        if not event_ids:
            return res
        count = 0
        for interp in cur_obj.interpreter_ids:
            if interp.select:
                count += 1
        if count == 0 :
            raise osv.except_osv(_('Warning!'),_('You must select an Interpreter to assign to this event.'))
        if count >1 :
            raise osv.except_osv(_('Warning!'),_('You can select only one Interpreter to assign to this event.'))
        for interp in cur_obj.interpreter_ids:
            #print "interp...........",interp
            if interp.select:
                res = self.pool.get('event').write(cr ,uid ,event_ids , {'interpreter_id':interp.interpreter_id and interp.interpreter_id.id or False,
                'voicemail_msg':interp.voicemail_msg ,'state':'scheduled'})
                return res

        #res = self.pool.get('event').write(cr ,uid ,event_ids , {'interpreter_id':interpreter2.interpreter_id and interpreter2.interpreter_id.id or False,'state':'scheduled'})
        return res

#    def onchange_partner_id(self, cr, uid, ids,  partner_id, context = None):
#
#        for p in self.pool.get('product.product').browse(cr, uid, product_ids):
#            invoice_lines.append((0,0,{'product_id':p.id,'name':p.name,
#                              'account_id':p.categ_id.property_account_income_categ.id,
#                              }))#this dict contain keys which are fields of one2many field
#        res['value']['interpreter_ids']=[(6, 0, tax_ids)]
#        return res

    def default_get(self, cr, uid, fields, context=None):
        print "default_get........"
        #cr.execute('insert into relation_name (self_id,module_name_id) values(%s,%s)',(first_value,second_value)
        res = {}
        if context is None: context = {}
        res = super(assign_interpreter, self).default_get(cr, uid, fields, context=context)
        event_ids = context.get('active_ids', [])
        print "event_ids........",event_ids
        #active_model = context.get('active_model')
        if not event_ids or len(event_ids) != 1:
            # Partial Picking Processing may only be done for one picking at a time
            return res
        event_id, = event_ids
        if 'event_id' in fields:
            res.update(event_id = event_id)
        event = self.pool.get('event').browse(cr, uid, event_id, context=context)
        state = event.state
        if 'language_id' in fields:
            res.update({'language_id':event.language_id and event.language_id.id or False})
        #print "default_get..........",res

        event_ids = context.get('active_ids', [])
        #print "event_ids.......",event_ids
        obj = self.pool.get('hr.employee')
        select_obj = self.pool.get('select.interpreter')
        interpreter_ids = new_ids = select_ids = []
        if event_ids:
            lang = self.pool.get('event').browse(cr ,uid ,event_ids[0]).language_id
            partner = self.pool.get('event').browse(cr ,uid ,event_ids[0]).partner_id
#            print "lang....",lang
#            lang = self.browse(cr, uid, ids, context=context)
#            sql = "select  interpreter_id from interpreter_language where name = %d"%(lang.id)
            int_lang_ids = self.pool.get('interpreter.language').search(cr ,uid ,[('name','=',lang.id)])
#            print "int_lang_ids........",int_lang_ids

            if int_lang_ids:
                for int_lang_id in int_lang_ids:
                    lang_browse = self.pool.get('interpreter.language').browse(cr ,uid ,int_lang_id)
                    interpreter_ids.append(lang_browse.interpreter_id.id)
            new_ids = interpreter_ids
            if interpreter_ids:
                print "interpreter_ids........",interpreter_ids
                zip = partner.zip
                #print "zip...........",zip
                if zip:
#                    gibberish = urllib.urlopen('http://www.uszip.com/zip/' + '203150')
#                    less_gib = gibberish.read().decode('utf-8')
#                    query = "select id from hr_employee where zip = %s and id in %s"%( str(zip) + '' , tuple(interpreter_ids))
#                    cr.execute(query )
#                    i_ids = map(lambda x: x[0], cr.fetchall())
                    min_zip = int(zip) - 10
                    max_zip = int(zip) + 10
                    print "min_zip...max_zip......",min_zip,max_zip
                    visit_ids = []
                    for history in partner.interpreter_history:
                        if history.name.id in interpreter_ids:
                            visit_ids.append(history.name.id)
                    if visit_ids:
                        visit_ids = flatten(visit_ids)
                        visit_ids = list(set(visit_ids))
                    
                    print "visit_ids........",visit_ids
                    for visit_id in visit_ids:
                        if visit_id in interpreter_ids:
                            interpreter_ids.remove(visit_id)
#                    print "visit_ids........",visit_ids
#                    print "interpreter_ids......",interpreter_ids
                    i_ids = obj.search(cr ,uid ,[('zip','=',zip),('id','in',tuple(interpreter_ids))] , order ="rate")
#                    print "i_ids.......",i_ids
#                    i_ids1 = obj.search(cr ,uid ,[('zip','!=',zip),('zip','!=',zip),('zip','!=',zip),('id','in',tuple(interpreter_ids))])
#                    query = "select id from hr_employee where zip::integer != %s and zip::integer <= %s and zip::integer >= %s and id in %s  order by rate "%( str(zip), str(max_zip) ,str(min_zip)  , tuple(interpreter_ids))
#                    cr.execute(query )
#                    i_ids1 = map(lambda x: x[0], cr.fetchall())
                    i_ids1 = obj.search(cr ,uid ,[('zip','!=',zip),('zip','<=',max_zip),('zip','>=',min_zip),('id','in',tuple(interpreter_ids))] , order ="rate")
                    print "i_ids1.......",i_ids1
                    new_ids =  i_ids + i_ids1
#                    print "new_ids...........",new_ids
#                    select_ids = select_obj.search(cr ,uid ,[])
#                    print "select_ids........",select_ids
#                    for select_id in select_ids:
#                        select_obj.unlink(cr ,uid , select_id)
#                    query1 = "delete from select_assign_rel "
#                    cr.execute(query1 )
                    select_ids = []
                    for visit_id in visit_ids:
                        query = "select max(event_date) from interpreter_alloc_history where partner_id = %s and name = %s "%( partner.id , visit_id )
                        cr.execute(query )
                        last_visit_date = map(lambda x: x[0], cr.fetchall())
#                        print "last_visit_date........",last_visit_date
                        history_ids = self.pool.get('interpreter.history').search(cr ,uid ,[('name','=',visit_id,),('event_id','=',event_ids[0]),('state','=','voicemailsent')], order="event_date desc")
                        #voicemail_msg = self.pool.get('hr.employee').browse(cr ,uid , visit_id).voicemail_msg
                        voicemail_msg = ''
                        if history_ids:
                            voicemail_msg = self.pool.get('interpreter.history').browse(cr ,uid , history_ids[0]).voicemail_msg
                        if last_visit_date and last_visit_date[0]:
                            select_ids.append(select_obj.create(cr ,uid ,{'interpreter_id':visit_id,'event_id':event_ids[0],'visited':True,'visited_date':last_visit_date,
                                                                        'state':state ,'voicemail_msg':voicemail_msg}))
                        else:
                            select_ids.append(select_obj.create(cr ,uid ,{'interpreter_id':visit_id,'event_id':event_ids[0],'visited':True, 'state':state,'voicemail_msg':voicemail_msg}))
                    for new_id in new_ids:
                        history_ids = self.pool.get('interpreter.history').search(cr ,uid ,[('name','=',new_id,),('event_id','=',event_ids[0]),('state','=','voicemailsent')], order="event_date desc")
                        voicemail_msg = ''
                        if history_ids:
                            voicemail_msg = self.pool.get('interpreter.history').browse(cr ,uid , history_ids[0]).voicemail_msg
                        select_ids.append(select_obj.create(cr ,uid ,{'interpreter_id':new_id,'event_id':event_ids[0] ,'state':state,'voicemail_msg':voicemail_msg}))
#                    new_ids = tuple(new_ids)
#                    print "new_ids.....",new_ids
#                    print "list(new_ids).....",list(new_ids)
#                    print "select_ids........",select_ids

        res['interpreter_ids']= select_ids #[(6, 0, select_ids)]
        return res

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        print "fields_view_get......."
        if context is None:
            context = {}
        result = super(assign_interpreter, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar, submenu)
        if 'active_ids' not in context:
            context['active_ids'] = []
#        event_ids = context.get('active_ids', [])
#        print "event_ids.......",event_ids
#        obj = self.pool.get('hr.employee')
#        select_obj = self.pool.get('select.interpreter')
#        interpreter_ids = new_ids = []
        query = "delete from select_interpreter "
        cr.execute(query )
        query = "delete from select_assign_rel "
        cr.execute(query )
#        if event_ids:
#            lang = self.pool.get('event').browse(cr ,uid ,event_ids[0]).language_id
#            partner = self.pool.get('event').browse(cr ,uid ,event_ids[0]).partner_id
#            print "lang....",lang
#            lang = self.browse(cr, uid, ids, context=context)
#            sql = "select  interpreter_id from interpreter_language where name = %d"%(lang.id)
#            int_lang_ids = self.pool.get('interpreter.language').search(cr ,uid ,[('name','=',lang.id)])
#            print "int_lang_ids........",int_lang_ids
#
#            if int_lang_ids:
#                for int_lang_id in int_lang_ids:
#                    lang_browse = self.pool.get('interpreter.language').browse(cr ,uid ,int_lang_id)
#                    interpreter_ids.append(lang_browse.interpreter_id.id)
#            new_ids = interpreter_ids
#            if interpreter_ids:
#                print "interpreter_ids........",interpreter_ids
#                zip = partner.zip
#                print "zip...........",zip
#                if zip:
#                    gibberish = urllib.urlopen('http://www.uszip.com/zip/' + '203150')
#                    less_gib = gibberish.read().decode('utf-8')
#                    query = "select id from hr_employee where zip = %s and id in %s"%( str(zip) + '' , tuple(interpreter_ids))
#                    cr.execute(query )
#                    i_ids = map(lambda x: x[0], cr.fetchall())
#                    min_zip = int(zip) - 10
#                    max_zip = int(zip) + 10
#                    print "min_zip...max_zip......",min_zip,max_zip
#                    visit_ids = []
#                    for history in partner.interpreter_history:
#                        visit_ids.append(history.name.id)
#                    if visit_ids:
#                        visit_ids = flatten(visit_ids)
#                        visit_ids = list(set(visit_ids))
#                    print "visit_ids........",visit_ids
#                    for visit_id in visit_ids:
#                        if visit_id in interpreter_ids:
#                            interpreter_ids.remove(visit_id)
#                    print "visit_ids........",visit_ids
#                    print "interpreter_ids......",interpreter_ids
#                    i_ids = obj.search(cr ,uid ,[('zip','=',zip),('id','in',tuple(interpreter_ids))] , order ="rate")
#                    print "i_ids.......",i_ids
#                    #i_ids1 = obj.search(cr ,uid ,[('zip','!=',zip),('zip','!=',zip),('zip','!=',zip),('id','in',tuple(interpreter_ids))])
#                    query = "select id from hr_employee where zip::integer != %s and zip::integer <= %s and zip::integer >= %s and id in %s  order by rate "%( str(zip), str(max_zip) ,str(min_zip)  , tuple(interpreter_ids))
#                    cr.execute(query )
#                    i_ids1 = map(lambda x: x[0], cr.fetchall())
#                    print "i_ids1.......",i_ids1
#                    new_ids = visit_ids + i_ids + i_ids1
#                    print "new_ids...........",new_ids
#                    select_ids = select_obj.search(cr ,uid ,[])
#                    print "select_ids........",select_ids
#                    for select_id in select_ids:
#                        select_obj.unlink(cr ,uid , select_id)
#                    for new_id in new_ids:
#                        select_ids = select_obj.create(cr ,uid ,{'interp_id':new_id,'interpreter_id':new_id,})
#                    new_ids = tuple(new_ids)
#                    print "new_ids.....",new_ids
#                    print "list(new_ids).....",list(new_ids)
#                    print "select_ids.......",select_ids
#                    new_ids = flatten(new_ids)
#                    print "new_ids.........",new_ids
#                    new_ids = list(set(new_ids))
#                    print "new_ids.........",new_ids
#            #print "interpreter_ids.......",interpreter_ids
#        if view_type=='form':
#            _moves_arch_lst = """<form string="Assign Interpreter" version="7.0">
#                   """
#            #<field name="interpreter_id" domain="[('id','in',%s)]" required="1"/> %(list(new_ids))
#            _moves_arch_lst += """
#                    <group>
#
#                        <field name="interpreter_id2"  />
#                        <separator/>
#                        <separator/>
#                        <field name="interpreter_ids" nolabel="1" >
#                            <tree editable="top">
#                                <field name="select" />
#                                <field name="name" />
#                                <field name="middle_name" />
#                                <field name="last_name" />
#                                <field name="zip" />
#                                <field name="rate" />
#                            </tree>
#                        <field />
#                    </group>
#                    <footer>
#                        <button string="Assign Interpreter" name="update_interpreter" type="object" class="oe_highlight"/>
#                        or
#                        <button string="Cancel" class="oe_link" special="cancel" />
#                    </footer> """
#            _moves_arch_lst += """ </form>"""
#            result['arch'] = _moves_arch_lst
        return result

    _columns = {
        #'language_id': fields.many2one("language" ,"Language",ondelete="CASCADE"),
        'event_id': fields.many2one("event", "Event Id" ,),
        #'voicemail_msg': fields.char("Voicemail Message" , size=32),
        #'interpreter_id': fields.many2one("hr.employee",'Interpreter', ondelete="CASCADE" ),
        #'interpreter_id2': fields.many2one("select.interpreter",'Interpreter2', ondelete="CASCADE" ),
        #'interpreter_lines': fields.one2many('select.interpreter','assign_id','Interpreters'),
        'interpreter_ids': fields.many2many("select.interpreter",'select_assign_rel','wiz_id','interp_id',"Interpreters"),
    }
    