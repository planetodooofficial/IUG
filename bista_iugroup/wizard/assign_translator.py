from odoo import fields,models,api
from odoo.tools.translate import _
import datetime
import time
from odoo import SUPERUSER_ID, tools
from odoo.exceptions import UserError

class assign_transl_wizard(models.TransientModel):
    """ A wizard to assign translator to event """
    _name = 'assign.transl.wizard'

    @api.multi
    def update_translator(self):
        ''' This function updates or assigns translator in the event form '''
        res= True
        self=self.with_context(translator=[])
        mod_obj = self.env['ir.model.data']
        cur_obj = self
        event = cur_obj.event_id
        user = self.env.user
        if event:
            if event.translator_id:
                if user.user_type and user.user_type  == 'vendor':
                    raise UserError(_('The Translator has already been assigned to this event'))

                print"translator_id",event.translator_id
                title = "Translator Already Assigned"
                message = " The Translator '%s %s' has been already assigned to the event. Do you want to change it?"%(event.translator_id.name, event.translator_id.last_name or '')
                self = self.with_context(event_id=event.id,history_id=cur_obj.history_id.id)
                return self.env['warning.translator'].warning(title, message)
            else:
                print"cur_obj.translator_id",cur_obj.translator_id,event
                assign_history_id=self.env['assign.translator.history'].sudo().create({'partner_id': event.partner_id and event.partner_id.id or False,'name': cur_obj.history_id and cur_obj.history_id.translator_id  \
                                            and cur_obj.history_id.translator_id.id or False, 'company_id': event.company_id and event.company_id.id or False,
                                            'event_id': event.id,'event_date': event.event_date ,'event_start': event.event_start,'event_end': event.event_end,'state':'assign',
                                            'schedule_translator_event_time': time.strftime('%Y-%m-%d %H:%M:%S'),'language_id': event.language_id.id}).id
                res = event.sudo().write({'translator_id': cur_obj.translator_id and cur_obj.translator_id.id or False,
                                            'state':'allocated','schedule_event_time': time.strftime('%Y-%m-%d %H:%M:%S'),'translation_assignment_history_id': assign_history_id})
                res = cur_obj.history_id.sudo().write({'state': 'assigned'})
#                if user.user_type and user.user_type == 'vendor':
#                    self.pool.get('event').event_confirm_mail(cr ,SUPERUSER_ID , [event.id] , context=context)
#                    self.pool.get('event').confirm_event(cr ,SUPERUSER_ID , [event.id] , context=context)
#                    res = mod_obj.get_object_reference(cr, SUPERUSER_ID, 'bista_iugroup', 'view_event_user_form')
#                    res_id = res and res[1] or False,
#                    return {
#                        'name': _('Event'),
#                        'view_type': 'form',
#                        'view_mode': 'form',
#                        'view_id': [res_id[0]],
#                        'res_model': 'event',
#                        'type': 'ir.actions.act_window',
#                        'nodestroy': True,
#                        'target': 'current',
#                        'res_id': event.id or False,
#                    }
#                    return  res
#                else:

#                if not event.suppress_email:
#                    template_id = mod_obj.get_object_reference(cr, SUPERUSER_ID, 'bista_iugroup', 'event_allocation_customer')[1]
#                    if template_id:
#                        self.pool.get('email.template').send_mail(cr , uid,template_id ,event.id)
                template_id1 = mod_obj.sudo().get_object_reference('bista_iugroup', 'event_allocation_translator')[1]
                if template_id1:
                    if user.user_type and user.user_type == 'vendor':
                        self.env['mail.template'].sudo().browse(template_id1).send_mail(event.id)
                    else:
                        res = event.sudo().action_mail_send(event,'event', template_id1)
        return res

    @api.model
    def default_get(self, fields):
        res = super(assign_transl_wizard , self).default_get(fields)
        history_ids = self._context.get('active_ids', [])
        if not history_ids or len(history_ids) != 1:
            return res
        history_id, = history_ids
        event_id = False
        history = self.env['select.translator.line'].browse(history_ids[0])
        if 'history_id' in fields:
            res.update(history_id = history_id)
        if 'translator_id' in fields:
            res.update(translator_id = history.translator_id.id)
            print"history.translator_id.id",history.translator_id.id
        if 'event_id' in fields:
            res.update(event_id = history.event_id.id)
        history_obj = self.env['translator.alloc.history']
        h_ids = []
        if history_ids:
            if history.event_id:
                event_id = history.event_id
                event_start_date = event_id.event_start_date
                if event_start_date:
                    h_ids = history_obj.search([('name','=',history.translator_id.id),('event_start_date','=',event_start_date),('state','in',('confirm','allocated'))])
        res['translator_ids']= h_ids #[(6, 0, select_ids)]
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(assign_transl_wizard, self).fields_view_get(view_id, view_type, toolbar, submenu)
        if 'active_ids' not in self._context:
            self=self.with_context(active_ids = [])
        return result


    history_id=fields.Many2one("select.translator.line", "History Id" )
    event_id=fields.Many2one("event", "Event Id" )
    translator_id=fields.Many2one("res.partner", "Translator" )
    translator_ids=fields.Many2many("translator.alloc.history",'transplator_alloc_rel','wiz_id','history_id',"Translator History")

