from odoo import fields,models,api
from odoo.tools.translate import _
import time
from odoo import SUPERUSER_ID, tools
from odoo.exceptions import UserError

class assign_transp_wizard(models.TransientModel):
    """ A wizard to assign transporter to event """
    _name = 'assign.transp.wizard'

    @api.multi
    def update_transporter(self):
        ''' This function updates or assigns transporter in the event form '''
        res= True
        self=self.with_context(transporter=[])
        mod_obj = self.env['ir.model.data']
        cur_obj = self
        event = cur_obj.event_id
        user = self.env.user
        if event:
            if event.transporter_id:
                if user.user_type and user.user_type  == 'vendor':
                    raise UserError(_('The Transporter has already been assigned to this event'))
                title = "Transporter Already Assigned"
                message = " The Transporter '%s %s' has been already assigned to the event. Do you want to change it?"%(event.transporter_id.name, event.transporter_id.last_name or '')
                self = self.with_context(event_id=event.id,history_id=cur_obj.history_id.id)
                return self.env['warning.transporter'].warning(title, message)
            else:
                if not event.history_id2:
                    history_id2=self.env['transporter.alloc.history'].sudo().create({'partner_id':event.partner_id and event.partner_id.id or False,'name':cur_obj.history_id and cur_obj.history_id.transporter_id  and cur_obj.history_id.transporter_id.id or False,
                        'event_id':event.id,'event_date':event.event_date ,'event_start':event.event_start,'event_end':event.event_end,'state':'allocated','company_id': event.company_id and event.company_id.id or False,
                        'allocate_date':time.strftime('%Y-%m-%d %H:%M:%S'),'language_id':event.language_id.id})
                else:
                    history_id2=event.history_id2.sudo().write({'partner_id':event.partner_id and event.partner_id.id or False,'name':cur_obj.history_id and cur_obj.history_id.transporter_id  and cur_obj.history_id.transporter_id.id or False,
                        'event_id':event.id,'event_date':event.event_date ,'event_start':event.event_start,'event_end':event.event_end,'state':'allocated','company_id': event.company_id and event.company_id.id or False,
                        'allocate_date':time.strftime('%Y-%m-%d %H:%M:%S'),'language_id':event.language_id.id})

                res = event.sudo().write({'transporter_id':cur_obj.transporter_id and cur_obj.transporter_id.id or False,
                'state':'allocated','schedule_event_time':time.strftime('%Y-%m-%d %H:%M:%S'),'history_id2':history_id2.id})
                res = cur_obj.history_id.sudo().write({'state': 'assigned'})
#                if user.user_type and user.user_type == 'vendor':
#                    self.pool.get('event').event_confirm_mail(cr ,SUPERUSER_ID , [event.id] , context=context)
#                    self.pool.get('event').confirm_event(cr ,SUPERUSER_ID , [event.id] , context=context)
#                    res = mod_obj.get_object_reference(cr, SUPERUSER_ID, 'bista_iugroup', 'view_event_user_form')
#                    res_id = res and res[1] or False,
##                    print "res_id.......",res_id
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
                template_id1 = mod_obj.sudo().get_object_reference('bista_iugroup', 'event_allocation_transporter')[1]
                if template_id1:
                    if user.user_type and user.user_type == 'vendor':
                        self.env['mail.template'].sudo().browse(template_id1).send_mail(event.id)
                    else:
                        res = event.sudo().action_mail_send(event, 'event', template_id1)
        return res

    @api.model
    def default_get(self, fields):
        res = {}
        res = super(assign_transp_wizard , self).default_get(fields)
        history_ids = self._context.get('active_ids', [])
        if not history_ids or len(history_ids) != 1:
            return res
        history_id, = history_ids
        event_id = False
        history = self.env['select.transporter.line'].browse(history_ids[0])
        if 'history_id' in fields:
            res.update(history_id = history_id)
        if 'transporter_id' in fields:
            res.update(transporter_id = history.transporter_id.id)
        if 'event_id' in fields:
            res.update(event_id = history.event_id.id)
        history_obj = self.pool.get('transporter.alloc.history')
        h_ids = []
        if history_ids:
            if history.event_id:
                event_id = history.event_id.id
                event_date = event_id.event_start_date
                if event_date:
                    h_ids = history_obj.search([('name','=',history.transporter_id.id),('event_start_date','=',event_date),('state','in',('confirm','allocated'))])
        res['transporter_ids']= h_ids #[(6, 0, select_ids)]
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(assign_transp_wizard, self).fields_view_get(view_id, view_type, toolbar, submenu)
        if 'active_ids' not in self._context:
            self = self.with_context(active_ids=[])
        return result


    history_id= fields.Many2one("select.transporter.line", "History Id" )
    event_id=fields.Many2one("event", "Event Id" )
    transporter_id=fields.Many2one("res.partner", "Transporter" )
    transporter_ids=fields.Many2many("transporter.alloc.history",'transporter_alloc_rel','wiz_id','history_id',"Transporter History")
