from odoo import api,fields,models
import xmlrpclib

class Sync_Records(models.Model):
    _inherit="sync.records"

    @api.model
    def sync_event_and_related_records(self):
        model_ids = self.env['ir.model'].search(
            [('model', 'in',
              ['event', 'interpreter.alloc.history', 'interpreter.history', 'event.interpreter.calendar', 'select.interpreter.line', 'select.translator.line',
               'assign.translator.history'])]).ids
        recs_to_sync = self.env['auditlog.log'].search(
            [('sync', '=', False), ('error', '=', False), ('model_id', 'in', model_ids)], order='create_date asc')
        if recs_to_sync:
            config_obj = self.env['server.config']
            config_ids = config_obj.search([])
            if not config_ids:
                raise UserError(_('No Active server config found!'))
            config = config_ids[0]
            ip = config.host  # Host
            port = config.port  # Port
            username = config.username  # the userl
            pwd = config.password  # the password of the user
            dbname = config.dbname  # the db name
            sock_common = xmlrpclib.ServerProxy('http://' + ip + ':' + port + '/xmlrpc/common')
            d_uid = sock_common.login(dbname, username, pwd)
            sock = xmlrpclib.ServerProxy('http://' + ip + ':' + port + '/xmlrpc/object')
            for rec in recs_to_sync:
                if rec.method == 'create':
                    if rec.model_id.model == 'event':
                        try:
                            event_rec = self.env['event'].browse(rec.res_id)
                            if event_rec.authorize_partner_id:
                                authorize_partner_id = event_rec.authorize_partner_id.customer_record_old_id
                            else:
                                authorize_partner_id = False
                            if event_rec.contact_id:
                                contact_id = event_rec.contact_id.customer_record_old_id
                            else:
                                contact_id = False
                            if event_rec.transporter_id:
                                transporter_id = event_rec.transporter_id.customer_record_old_id
                            else:
                                transporter_id = False
                            if event_rec.user_id:
                                user_id = event_rec.user_id.user_old_id
                            else:
                                user_id = False
                            if event_rec.company_id:
                                company_id = event_rec.company_id.res_company_old_id
                            else:
                                company_id = False
                            if event_rec.ordering_contact_id:
                                ordering_contact_id = event_rec.ordering_contact_id.customer_record_old_id
                            else:
                                ordering_contact_id = False
                            if event_rec.interpreter_id:
                                interpreter_id = event_rec.interpreter_id.customer_record_old_id
                            else:
                                interpreter_id = False
                            if event_rec.ordering_partner_id:
                                ordering_partner_id = event_rec.ordering_partner_id.customer_record_old_id
                            else:
                                ordering_partner_id = False
                            if event_rec.location_id:
                                location_id = event_rec.location_id.location_old_id
                            else:
                                location_id = False
                            if event_rec.certification_level_id:
                                certification_level_id = event_rec.certification_level_id.certification_level_old_id
                            else:
                                certification_level_id = False
                            if event_rec.partner_id:
                                partner_id = event_rec.partner_id.customer_record_old_id
                            else:
                                partner_id = False
                            if event_rec.language_id:
                                language_id = event_rec.language_id.language_old_id
                            else:
                                language_id = False
                            if event_rec.authorize_contact_id:
                                authorize_contact_id = event_rec.authorize_contact_id.customer_record_old_id
                            else:
                                authorize_contact_id = False
                            if event_rec.history_id3:
                                history_id3 = event_rec.history_id3.transporter_alloc_history_old_id
                            else:
                                history_id3 = False
                            if event_rec.translator_id:
                                translator_id = event_rec.translator_id.customer_record_old_id
                            else:
                                translator_id = False
                            if event_rec.history_id2:
                                history_id2 = event_rec.history_id2.transporter_alloc_history_old_id
                            else:
                                history_id2 = False
                            if event_rec.doctor_id:
                                doctor_id = event_rec.doctor_id.doctor_old_id
                            else:
                                doctor_id = False
                            if event_rec.zone_id:
                                zone_id = event_rec.zone_id.meta_zone_old_id
                            else:
                                zone_id = False
                            if event_rec.cancel_reason_id:
                                cancel_reason_id = event_rec.cancel_reason_id.cancel_reason_old_id
                            else:
                                cancel_reason_id = False
                            if event_rec.patient_id:
                                patient_id = event_rec.patient_id.patient_old_id
                            else:
                                patient_id = False
                            if event_rec.translation_assignment_history_id:
                                translation_assignment_history_id = event_rec.translation_assignment_history_id.assign_translator_history_old_id
                            else:
                                translation_assignment_history_id = False
                            if event_rec.interpreter_id2:
                                interpreter_id2 = event_rec.interpreter_id2.customer_record_old_id
                            else:
                                interpreter_id2 = False
                            if event_rec.transporter_id2:
                                transporter_id2 = event_rec.transporter_id2.customer_record_old_id
                            else:
                                transporter_id2 = False
                            if event_rec.translator_id2:
                                translator_id2 = event_rec.translator_id2.customer_record_old_id
                            else:
                                translator_id2 = False
                            if event_rec.language_id2:
                                language_id2 = event_rec.language_id2.language_old_id
                            else:
                                language_id2 = False
                            if event_rec.event_out_come_id:
                                event_out_come_id = event_rec.event_out_come_id.event_outcome_old_id
                            else:
                                event_out_come_id = False
                            if event_rec.fee_note_status_id:
                                fee_note_status_id=event_rec.fee_note_status_id.fee_note_status_old_id
                            else:
                                fee_note_status_id=False
                            if event_rec.appointment_type_id:
                                appointment_type_id = event_rec.appointment_type_id.app_type_old_id
                            else:
                                appointment_type_id=False
                            if event_rec.scheduler_id:
                                scheduler_id = event_rec.scheduler_id.user_old_id
                            else:
                                scheduler_id=False
                            if event_rec.sales_representative_id:
                                sales_representative_id=event_rec.sales_representative_id.user_old_id
                            else:
                                sales_representative_id=False
                            if event_rec.single_interpreter:
                                single_interpreter = event_rec.single_interpreter.customer_record_old_id
                            else:
                                single_interpreter=False
                            if event_rec.project_name_id:
                                project_name_id = event_rec.project_name_id.iug_project_old_id
                            else:
                                project_name_id=False
                            if event_rec.task_id:
                                task_id = event_rec.task_id.project_task_old_id
                            else:
                                task_id=False
                            if event_rec.supp_invoice_id2:
                                supp_invoice_id2 = event_rec.supp_invoice_id2.invoice_old_id
                            else:
                                supp_invoice_id2 = False
                            if event_rec.supp_invoice_id:
                                supp_invoice_id = event_rec.supp_invoice_id.invoice_old_id
                            else:
                                supp_invoice_id = False
                            if event_rec.cust_invoice_id:
                                cust_invoice_id = event_rec.cust_invoice_id.invoice_old_id
                            else:
                                cust_invoice_id = False
                            if event_rec.source_event_id:
                                source_event_id =event_rec.source_event_id.event_old_id
                            else:
                                source_event_id=False
                            supp_invoice_ids = []
                            for supp_invoice in event_rec.supp_invoice_ids:
                                supp_invoice_id = supp_invoice.invoice_old_id
                                if supp_invoice_id:
                                    supp_invoice_ids.append(supp_invoice_id)
                            interpreter_ids=[]
                            for select_interpreter_line_id in event_rec.interpreter_ids:
                                interpreter_ids.append(select_interpreter_line_id.interpreter_line_old_id)
                            interpreter_ids2 = []
                            for select_interpreter_line_id2 in event_rec.interpreter_ids2:
                                interpreter_ids2.append(select_interpreter_line_id2.interpreter_line_old_id)
                            translator_ids = []
                            for select_translator_line_id in event_rec.translator_ids:
                                translator_ids.append(select_translator_line_id.translator_line_old_id)
                            translator_ids2 = []
                            for select_translator_line_id2 in event_rec.translator_ids2:
                                translator_ids2.append(select_translator_line_id2.translator_line_old_id)
                            event_follower_ids=[]
                            for event_follower_id in event_rec.event_follower_ids:
                                event_follower_ids.append(event_follower_id.user_old_id)
                            interpreter_line_ids=[]
                            for interpreter_line_id in event_rec.interpreter_line_ids:
                                interpreter_line_ids.append(interpreter_line_id.customer_record_old_id)
                            assigned_interpreters=[]
                            for assigned_interpreter in event_rec.assigned_interpreters:
                                assigned_interpreters.append(assigned_interpreter.customer_record_old_id)
                            event_vals = {
                                # 'event_old_id': int(event_old_id),
                                'supp_invoice_ids': [(6, 0, supp_invoice_ids)],
                                'interpreter_ids': [(6, 0, interpreter_ids)],
                                'interpreter_ids2': [(6, 0, interpreter_ids2)],
                                'translator_ids': [(6, 0, translator_ids)],
                                'translator_ids2': [(6, 0, translator_ids2)],
                                'event_follower_ids': [(6, 0, event_follower_ids)],
                                'interpreter_line_ids': [(6, 0, interpreter_line_ids)],
                                'assigned_interpreters': [(6, 0, assigned_interpreters)],
                                'translation_assignment_history_id': translation_assignment_history_id,
                                'comment': event_rec.comment,
                                'is_follow_up': event_rec.is_follow_up,
                                'special_discount': event_rec.special_discount,
                                'authorize_partner_id': authorize_partner_id,
                                'contact_id': contact_id,
                                'date': event_rec.date,
                                'authorize_date': event_rec.authorize_date,
                                'transporter_id': transporter_id,
                                'user_id':user_id,
                                'company_id': company_id,
                                'event_start': event_rec.event_start,
                                'ordering_contact_id': ordering_contact_id,
                                'project_id': project_id,
                                'suppress_email': event_rec.suppress_email,
                                'function': event_rec.function,
                                'history_id': history_id,
                                'interpreter_id': interpreter_id,
                                'name': event_rec.name,
                                'cust_gpuid': event_rec.cust_gpuid,
                                'gender': event_rec.gender,
                                'ssnid': event_rec.ssnid,
                                'appointment_type_id':appointment_type_id,
                                'fee_note_status_id':fee_note_status_id,
                                'event_type': event_rec.event_type,
                                'event_end': event_rec.event_end,
                                'ordering_partner_id': ordering_partner_id,
                                'km': event_rec.km,
                                'location_id': location_id,
                                'certification_level_id': certification_level_id,
                                'claim_no': event_rec.claim_no,
                                'partner_id': partner_id,
                                'event_id': event_rec.event_id,
                                'language_id': language_id,
                                'state': event_rec.state,
                                'ref': event_rec.ref,
                                'authorize_contact_id': authorize_contact_id,
                                'history_id3': history_id3,
                                'fee_note_test':event_rec.fee_note_test,
                                'order_note_test': event_rec.order_note_test,
                                'task_id':task_id,
                                'translator_id': translator_id,
                                'dob': event_rec.dob,
                                'cust_csid': event_rec.cust_csid,
                                'claim_date': event_rec.claim_date,
                                'quickbooks_id': event_rec.quickbooks_id,
                                'total_cost': event_rec.total_cost,
                                'history_id2': history_id2,
                                'doctor_id': doctor_id,
                                'event_note': event_rec.event_note,
                                'cust_invoice_id':cust_invoice_id,
                                'am_pm2': event_rec.am_pm2,
                                'transportation_type': event_rec.transportation_type,
                                'event_purpose': event_rec.event_purpose,
                                'am_pm': event_rec.am_pm,

                                'injury_date': event_rec.injury_date,
                                'zone_id': zone_id,
                                'event_start_date': event_rec.event_start_date,
                                'supp_invoice_id':supp_invoice_id,
                                'supp_invoice_id2':supp_invoice_id2,
                                'cancel_reason_id': cancel_reason_id,
                                'customer_timezone': event_rec.customer_timezone,
                                'schedule_event_time': event_rec.schedule_event_time,
                                'patient_id': patient_id,
                                'interpreter_id2': interpreter_id2,
                                'department': event_rec.department,
                                'transporter_id2': transporter_id2,
                                'translator_id2': translator_id2,
                                'scheduler_id':scheduler_id,
                                'language_id2': language_id2,
                                'sales_representative_id':sales_representative_id,
                                'project_name_id':project_name_id,
                                'approving_mgr': event_rec.approving_mgr,
                                'is_authorized': event_rec.is_authorized,
                                'approving_mgr_email': event_rec.approving_mgr_email,
                                'verifying_mgr_email': event_rec.verifying_mgr_email,
                                'verified_event_start': event_rec.verified_event_start,
                                'verified_event_end': event_rec.verified_event_end,
                                'event_out_come_id': event_out_come_id,
                                'customer_timezone2': event_rec.customer_timezone2,
                                'verifying_mgr': event_rec.verifying_mgr,
                                'verify_state': event_rec.verify_state,
                                'fax': event_rec.fax,
                                'mental_prog': event_rec.mental_prog,
                                'verify_time': event_rec.verify_time,
                                'approve_time': event_rec.approve_time,
                                'history_id4': history_id4,
                                'phone_cust': event_rec.phone_cust,
                                'interpreter_note': event_rec.interpreter_note,
                                'cust_note': event_rec.cust_note,
                                'multi_type': event_rec.multi_type,
                                'source_event_id':source_event_id,
                                'event_end_min': event_rec.event_end_min,
                                'event_end_hr': event_rec.event_end_hr,
                                'event_start_hr': event_rec.event_start_hr,
                                'event_start_min': event_rec.event_start_min,
                                'customer_basis': event_rec.customer_basis,
                                'po_no': event_rec.po_no,
                                'medical_no': event_rec.medical_no,
                                'order_note': event_rec.order_note ,
                                'event_date': event_rec.event_date,
                                'dr_name': event_rec.dr_name,
                                'job_offered_interpreters_name': event_rec.job_offered_interpreters_name,
                                'task_state': event_rec.task_state,
                                'cost_center': event_rec.cost_center,
                                'emergency_rate': event_rec.emergency_rate,
                                'all_interpreter_email':event_rec.all_interpreter_email,
                                'interpreters_phone':event_rec.interpreters_phone,
                                'customer_group': event_rec.customer_group,
                                'single_interpreter':single_interpreter,
                                'actual_event_end': event_rec.actual_event_end,
                                'actual_event_start': event_rec.actual_event_start,
                                'job_schedule_id': event_rec.job_schedule_id,
                                'employer': event_rec.employer,
                                'mobile_sync': event_rec.mobile_sync,
                                'mobile_event': event_rec.mobile_event,
                                'cust_edit': event_rec.cust_edit,
                                'verified_dt': event_rec.verified_dt,
                                'verified_by': event_rec.verified_by,
                                'stat': event_rec.stat,
                                'no_editable': event_rec.no_editable,
                                'org_number': event_rec.org_number
                            }
                            event_old_id = sock.execute(dbname, d_uid, pwd, 'event',
                                                                    'create',
                                                                    event_vals)
                            event_rec.write({'event_old_id': event_old_id})
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model == 'interpreter.alloc.history':
                        try:
                            interpreter_alloc_history_rec = self.env['interpreter.alloc.history'].browse(rec.res_id)
                            if interpreter_alloc_history_rec.name:
                                partner_id= interpreter_alloc_history_rec.name.customer_record_old_id
                            else:
                                partner_id=False
                            if interpreter_alloc_history_rec.event_id:
                                event_id = interpreter_alloc_history_rec.event_id.event_old_id
                            else:
                                event_id = False
                            interpreter_alloc_his_vals = {
                                'name': partner_id,
                                'event_id': event_id,
                                'voicemail_msg': interpreter_alloc_history_rec.voicemail_msg,
                                'state': interpreter_alloc_history_rec.state,
                                'event_date': interpreter_alloc_history_rec.event_date,
                                'allocate_date': interpreter_alloc_history_rec.allocate_date,
                                'cancel_date': interpreter_alloc_history_rec.cancel_date,
                                'confirm_date': interpreter_alloc_history_rec.confirm_date,
                                'event_end': interpreter_alloc_history_rec.event_end,
                                'event_start': interpreter_alloc_history_rec.event_start,
                                'event_start_date': interpreter_alloc_history_rec.event_start_date,
                            }
                            interpreter_alloc_his_old_id=sock.execute(dbname, d_uid, pwd, 'interpreter.alloc.history','create',interpreter_alloc_his_vals)
                            interpreter_alloc_history_rec.write({'interpreter_alloc_his_old_id': interpreter_alloc_his_old_id})
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model =='interpreter.history':
                        try:
                            interpreter_history_rec = self.env['interpreter.history'].browse(rec.res_id)
                            if interpreter_history_rec.name:
                                name=interpreter_history_rec.name.customer_record_old_id
                            else:
                                name=False
                            if interpreter_history_rec.task_id:
                                task_id=interpreter_history_rec.task_id.project_task_old_id
                            else:
                                task_id=False
                            if interpreter_history_rec.event_id:
                                event_id=interpreter_history_rec.event_id.event_old_id
                            else:
                                event_id=False
                            if interpreter_history_rec.language_id:
                                language_id= interpreter_history_rec.language_id.language_old_id
                            else:
                                language_id=False
                            if interpreter_history_rec.company_id:
                                company_id=interpreter_history_rec.company_id.res_company_old_id
                            else:
                                company_id=False
                            inter_his_vals={
                                'name':name,
                                'task_id':task_id,
                                'event_id':event_id,
                                'language_id':language_id,
                                'company_id':company_id,
                                'voicemail_msg':interpreter_history_rec.voicemail_msg,
                                'state':interpreter_history_rec.state,
                                'event_date':interpreter_history_rec.event_date,
                                'event_start_time':interpreter_history_rec.event_start_time,
                                'event_end_time':interpreter_history_rec.event_end_time,
                            }
                            inter_his_old_id=sock.execute(dbname, d_uid, pwd, 'interpreter.history','create',inter_his_vals)
                            interpreter_history_rec.write({'inter_his_old_id': inter_his_old_id})
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model =='event.interpreter.calendar':
                        try:
                            event_interpreter_calendar_rec = self.env['event.interpreter.calendar'].browse(rec.res_id)
                            if event_interpreter_calendar_rec.event_id:
                                event_id = event_interpreter_calendar_rec.event_id.event_old_id
                            else:
                                event_id=False
                            if event_interpreter_calendar_rec.partner_id:
                                partner_id = event_interpreter_calendar_rec.partner_id.customer_record_old_id
                            else:
                                partner_id=False
                            if event_interpreter_calendar_rec.company_id:
                                company_id = event_interpreter_calendar_rec.company_id.res_company_old_id
                            else:
                                company_id=False

                            evnt_inrt_calendar_vals = {
                                # 'event_intr_calendar_old_id': value[0].strip(),
                                'allday': event_interpreter_calendar_rec.allday,
                                'start_time': event_interpreter_calendar_rec.start_time,
                                'duration': event_interpreter_calendar_rec.duration,
                                'event_id': event_id,
                                'name': event_interpreter_calendar_rec.name,
                                'note': event_interpreter_calendar_rec.note,
                                'partner_id': partner_id,
                                'end_time': event_interpreter_calendar_rec.end_time,
                                'cancelled': event_interpreter_calendar_rec.cancelled,
                                'is_event': event_interpreter_calendar_rec.is_event,
                                'company_id': company_id,
                            }
                            event_intr_calendar_old_id=sock.execute(dbname, d_uid, pwd, 'event.interpreter.calendar','create',evnt_inrt_calendar_vals)
                            event_interpreter_calendar_rec.write({'event_intr_calendar_old_id': event_intr_calendar_old_id})
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model == 'select.interpreter.line':
                        try:
                            select_interpreter_line_rec = self.env['select.interpreter.line'].browse(rec.res_id)
                            if select_interpreter_line_rec.interpreter_id:
                                interpreter_id = select_interpreter_line_rec.interpreter_id.customer_record_old_id
                            else:
                                interpreter_id = False
                            if select_interpreter_line_rec.event_id:
                                event_id = select_interpreter_line_rec.event_id.event_old_id
                            else:
                                event_id = False
                            interpreter_line_vals = {
                                                    'rate':select_interpreter_line_rec.rate,
                                                    'interpreter_id':interpreter_id,
                                                    'preferred':select_interpreter_line_rec.preferred,
                                                    'event_id':event_id,
                                                    'visited':select_interpreter_line_rec.visited,
                                                    'visited_date':select_interpreter_line_rec.visited_date,
                                                    'voicemail_msg':select_interpreter_line_rec.voicemail_msg,
                                                    'duration':select_interpreter_line_rec.duration,
                                                    'distance':select_interpreter_line_rec.distance,
                                                    'state':select_interpreter_line_rec.state,
                                                    'select_interpreter':select_interpreter_line_rec.select_interpreter,
                                                     # 'parent_state':parent_state,
                                                     # 'company_id':company_id
                                                    }
                            interpreter_line_old_id=sock.execute(dbname, d_uid, pwd, 'select.interpreter.line','create',interpreter_line_vals)
                            select_interpreter_line_rec.write({'interpreter_line_old_id': interpreter_line_old_id})
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model == 'select.translator.line':
                        try:
                            select_translator_line_rec = self.env['select.translator.line'].browse(rec.res_id)
                            if select_translator_line_rec.event_id:
                                event_id = select_translator_line_rec.event_id.event_old_id
                            else:
                                event_id = False
                            if select_translator_line_rec.translator_id:
                                translator_id = select_translator_line_rec.translator_id.customer_record_old_id
                            else:
                                translator_id = False
                            translator_line_vals = {
                                                     'select': select_translator_line_rec.select,
                                                     'event_id': event_id,
                                                     'visited': select_translator_line_rec.visited,
                                                     'visited_date': select_translator_line_rec.visited_date,
                                                     'voicemail_msg': select_translator_line_rec.voicemail_msg,
                                                     'duration': select_translator_line_rec.duration,
                                                     'distance': select_translator_line_rec.distance,
                                                     'state': select_translator_line_rec.state,
                                                     'translator_id': translator_id,
                                                     }
                            translator_line_old_id=sock.execute(dbname, d_uid, pwd, 'select.translator.line','create',translator_line_vals)
                            select_translator_line_rec.write({'translator_line_old_id': translator_line_old_id})
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model == 'assign.translator.history':
                        try:
                            assign_translator_history_rec = self.env['assign.translator.history'].browse(rec.res_id)
                            if assign_translator_history_rec.name:
                                name = assign_translator_history_rec.name.customer_record_old_id
                            else:
                                name=False
                            if assign_translator_history_rec.partner_id:
                                partner_id = assign_translator_history_rec.partner_id.customer_record_old_id
                            else:
                                partner_id=False
                            if assign_translator_history_rec.event_id:
                                event_id = assign_translator_history_rec.event_id.event_old_id
                            else:
                                event_id=False
                            as_trans_his_vals = {
                                # 'assign_trans_his_old_id': row[0].strip() or '',
                                'name': name,
                                'partner_id': partner_id,
                                'event_date': assign_translator_history_rec.event_date,
                                'event_id': event_id,
                                'state': assign_translator_history_rec.state,
                                'schedule_translator_event_time': assign_translator_history_rec.schedule_translator_event_time,
                            }
                            assign_trans_his_old_id=sock.execute(dbname, d_uid, pwd, 'assign.translator.history','create',as_trans_his_vals)
                            assign_translator_history_rec.write({'assign_trans_his_old_id': assign_trans_his_old_id})
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                elif rec.method == 'write':
                    if rec.model_id.model == 'event':
                        try:
                            event_rec = self.env['event'].browse(rec.res_id)
                            if event_rec.authorize_partner_id:
                                authorize_partner_id = event_rec.authorize_partner_id.customer_record_old_id
                            else:
                                authorize_partner_id = False
                            if event_rec.contact_id:
                                contact_id = event_rec.contact_id.customer_record_old_id
                            else:
                                contact_id = False
                            if event_rec.transporter_id:
                                transporter_id = event_rec.transporter_id.customer_record_old_id
                            else:
                                transporter_id = False
                            if event_rec.user_id:
                                user_id = event_rec.user_id.user_old_id
                            else:
                                user_id = False
                            if event_rec.company_id:
                                company_id = event_rec.company_id.res_company_old_id
                            else:
                                company_id = False
                            if event_rec.ordering_contact_id:
                                ordering_contact_id = event_rec.ordering_contact_id.customer_record_old_id
                            else:
                                ordering_contact_id = False
                            if event_rec.interpreter_id:
                                interpreter_id = event_rec.interpreter_id.customer_record_old_id
                            else:
                                interpreter_id = False
                            if event_rec.ordering_partner_id:
                                ordering_partner_id = event_rec.ordering_partner_id.customer_record_old_id
                            else:
                                ordering_partner_id = False
                            if event_rec.location_id:
                                location_id = event_rec.location_id.location_old_id
                            else:
                                location_id = False
                            if event_rec.certification_level_id:
                                certification_level_id = event_rec.certification_level_id.certification_level_old_id
                            else:
                                certification_level_id = False
                            if event_rec.partner_id:
                                partner_id = event_rec.partner_id.customer_record_old_id
                            else:
                                partner_id = False
                            if event_rec.language_id:
                                language_id = event_rec.language_id.language_old_id
                            else:
                                language_id = False
                            if event_rec.authorize_contact_id:
                                authorize_contact_id = event_rec.authorize_contact_id.customer_record_old_id
                            else:
                                authorize_contact_id = False
                            if event_rec.history_id3:
                                history_id3 = event_rec.history_id3.transporter_alloc_history_old_id
                            else:
                                history_id3 = False
                            if event_rec.translator_id:
                                translator_id = event_rec.translator_id.customer_record_old_id
                            else:
                                translator_id = False
                            if event_rec.history_id2:
                                history_id2 = event_rec.history_id2.transporter_alloc_history_old_id
                            else:
                                history_id2 = False
                            if event_rec.doctor_id:
                                doctor_id = event_rec.doctor_id.doctor_old_id
                            else:
                                doctor_id = False
                            if event_rec.zone_id:
                                zone_id = event_rec.zone_id.meta_zone_old_id
                            else:
                                zone_id = False
                            if event_rec.cancel_reason_id:
                                cancel_reason_id = event_rec.cancel_reason_id.cancel_reason_old_id
                            else:
                                cancel_reason_id = False
                            if event_rec.patient_id:
                                patient_id = event_rec.patient_id.patient_old_id
                            else:
                                patient_id = False
                            if event_rec.translation_assignment_history_id:
                                translation_assignment_history_id = event_rec.translation_assignment_history_id.assign_translator_history_old_id
                            else:
                                translation_assignment_history_id = False
                            if event_rec.interpreter_id2:
                                interpreter_id2 = event_rec.interpreter_id2.customer_record_old_id
                            else:
                                interpreter_id2 = False
                            if event_rec.transporter_id2:
                                transporter_id2 = event_rec.transporter_id2.customer_record_old_id
                            else:
                                transporter_id2 = False
                            if event_rec.translator_id2:
                                translator_id2 = event_rec.translator_id2.customer_record_old_id
                            else:
                                translator_id2 = False
                            if event_rec.language_id2:
                                language_id2 = event_rec.language_id2.language_old_id
                            else:
                                language_id2 = False
                            if event_rec.event_out_come_id:
                                event_out_come_id = event_rec.event_out_come_id.event_outcome_old_id
                            else:
                                event_out_come_id = False
                            if event_rec.fee_note_status_id:
                                fee_note_status_id=event_rec.fee_note_status_id.fee_note_status_old_id
                            else:
                                fee_note_status_id=False
                            if event_rec.appointment_type_id:
                                appointment_type_id = event_rec.appointment_type_id.app_type_old_id
                            else:
                                appointment_type_id=False
                            if event_rec.scheduler_id:
                                scheduler_id = event_rec.scheduler_id.user_old_id
                            else:
                                scheduler_id=False
                            if event_rec.sales_representative_id:
                                sales_representative_id=event_rec.sales_representative_id.user_old_id
                            else:
                                sales_representative_id=False
                            if event_rec.single_interpreter:
                                single_interpreter = event_rec.single_interpreter.customer_record_old_id
                            else:
                                single_interpreter=False
                            if event_rec.project_name_id:
                                project_name_id = event_rec.project_name_id.iug_project_old_id
                            else:
                                project_name_id=False
                            if event_rec.task_id:
                                task_id = event_rec.task_id.project_task_old_id
                            else:
                                task_id=False
                            if event_rec.supp_invoice_id2:
                                supp_invoice_id2 = event_rec.supp_invoice_id2.invoice_old_id
                            else:
                                supp_invoice_id2 = False
                            if event_rec.supp_invoice_id:
                                supp_invoice_id = event_rec.supp_invoice_id.invoice_old_id
                            else:
                                supp_invoice_id = False
                            if event_rec.cust_invoice_id:
                                cust_invoice_id = event_rec.cust_invoice_id.invoice_old_id
                            else:
                                cust_invoice_id = False
                            if event_rec.source_event_id:
                                source_event_id =event_rec.source_event_id.event_old_id
                            else:
                                source_event_id=False
                            supp_invoice_ids = []
                            for supp_invoice in event_rec.supp_invoice_ids:
                                supp_invoice_id = supp_invoice.invoice_old_id
                                if supp_invoice_id:
                                    supp_invoice_ids.append(supp_invoice_id)
                            interpreter_ids = []
                            for select_interpreter_line_id in event_rec.interpreter_ids:
                                interpreter_ids.append(select_interpreter_line_id.interpreter_line_old_id)
                            interpreter_ids2 = []
                            for select_interpreter_line_id2 in event_rec.interpreter_ids2:
                                interpreter_ids2.append(select_interpreter_line_id2.interpreter_line_old_id)
                            translator_ids = []
                            for select_translator_line_id in event_rec.translator_ids:
                                translator_ids.append(select_translator_line_id.translator_line_old_id)
                            translator_ids2 = []
                            for select_translator_line_id2 in event_rec.translator_ids2:
                                translator_ids2.append(select_translator_line_id2.translator_line_old_id)
                            event_follower_ids = []
                            for event_follower_id in event_rec.event_follower_ids:
                                event_follower_ids.append(event_follower_id.user_old_id)
                            interpreter_line_ids = []
                            for interpreter_line_id in event_rec.interpreter_line_ids:
                                interpreter_line_ids.append(interpreter_line_id.customer_record_old_id)
                            assigned_interpreters = []
                            for assigned_interpreter in event_rec.assigned_interpreters:
                                assigned_interpreters.append(assigned_interpreter.customer_record_old_id)
                            event_vals = {
                                # 'event_old_id': int(event_old_id),
                                'supp_invoice_ids': [(6, 0, supp_invoice_ids)],
                                'interpreter_ids': [(6, 0, interpreter_ids)],
                                'interpreter_ids2': [(6, 0, interpreter_ids2)],
                                'translator_ids': [(6, 0, translator_ids)],
                                'translator_ids2': [(6, 0, translator_ids2)],
                                'event_follower_ids': [(6, 0, event_follower_ids)],
                                'interpreter_line_ids': [(6, 0, interpreter_line_ids)],
                                'assigned_interpreters': [(6, 0, assigned_interpreters)],
                                'translation_assignment_history_id': translation_assignment_history_id,
                                'comment': event_rec.comment,
                                'is_follow_up': event_rec.is_follow_up,
                                'special_discount': event_rec.special_discount,
                                'authorize_partner_id': authorize_partner_id,
                                'contact_id': contact_id,
                                'date': event_rec.date,
                                'authorize_date': event_rec.authorize_date,
                                'transporter_id': transporter_id,
                                'user_id':user_id,
                                'company_id': company_id,
                                'event_start': event_rec.event_start,
                                'ordering_contact_id': ordering_contact_id,
                                'project_id': project_id,
                                'suppress_email': event_rec.suppress_email,
                                'function': event_rec.function,
                                'history_id': history_id,
                                'interpreter_id': interpreter_id,
                                'name': event_rec.name,
                                'cust_gpuid': event_rec.cust_gpuid,
                                'gender': event_rec.gender,
                                'ssnid': event_rec.ssnid,
                                'appointment_type_id':appointment_type_id,
                                'fee_note_status_id':fee_note_status_id,
                                'event_type': event_rec.event_type,
                                'event_end': event_rec.event_end,
                                'ordering_partner_id': ordering_partner_id,
                                'km': event_rec.km,
                                'location_id': location_id,
                                'certification_level_id': certification_level_id,
                                'claim_no': event_rec.claim_no,
                                'partner_id': partner_id,
                                'event_id': event_rec.event_id,
                                'language_id': language_id,
                                'state': event_rec.state,
                                'ref': event_rec.ref,
                                'authorize_contact_id': authorize_contact_id,
                                'history_id3': history_id3,
                                'fee_note_test':event_rec.fee_note_test,
                                'order_note_test': event_rec.order_note_test,
                                'task_id':task_id,
                                'translator_id': translator_id,
                                'dob': event_rec.dob,
                                'cust_csid': event_rec.cust_csid,
                                'claim_date': event_rec.claim_date,
                                'quickbooks_id': event_rec.quickbooks_id,
                                'total_cost': event_rec.total_cost,
                                'history_id2': history_id2,
                                'doctor_id': doctor_id,
                                'event_note': event_rec.event_note,
                                'cust_invoice_id':cust_invoice_id,
                                'am_pm2': event_rec.am_pm2,
                                'transportation_type': event_rec.transportation_type,
                                'event_purpose': event_rec.event_purpose,
                                'am_pm': event_rec.am_pm,
                                'injury_date': event_rec.injury_date,
                                'zone_id': zone_id,
                                'event_start_date': event_rec.event_start_date,
                                'supp_invoice_id':supp_invoice_id,
                                'supp_invoice_id2':supp_invoice_id2,
                                'cancel_reason_id': cancel_reason_id,
                                'customer_timezone': event_rec.customer_timezone,
                                'schedule_event_time': event_rec.schedule_event_time,
                                'patient_id': patient_id,
                                'interpreter_id2': interpreter_id2,
                                'department': event_rec.department,
                                'transporter_id2': transporter_id2,
                                'translator_id2': translator_id2,
                                'scheduler_id':scheduler_id,
                                'language_id2': language_id2,
                                'sales_representative_id':sales_representative_id,
                                'project_name_id':project_name_id,
                                'approving_mgr': event_rec.approving_mgr,
                                'is_authorized': event_rec.is_authorized,
                                'approving_mgr_email': event_rec.approving_mgr_email,
                                'verifying_mgr_email': event_rec.verifying_mgr_email,
                                'verified_event_start': event_rec.verified_event_start,
                                'verified_event_end': event_rec.verified_event_end,
                                'event_out_come_id': event_out_come_id,
                                'customer_timezone2': event_rec.customer_timezone2,
                                'verifying_mgr': event_rec.verifying_mgr,
                                'verify_state': event_rec.verify_state,
                                'fax': event_rec.fax,
                                'mental_prog': event_rec.mental_prog,
                                'verify_time': event_rec.verify_time,
                                'approve_time': event_rec.approve_time,
                                'history_id4': history_id4,
                                'phone_cust': event_rec.phone_cust,
                                'interpreter_note': event_rec.interpreter_note,
                                'cust_note': event_rec.cust_note,
                                'multi_type': event_rec.multi_type,
                                'source_event_id':source_event_id,
                                'event_end_min': event_rec.event_end_min,
                                'event_end_hr': event_rec.event_end_hr,
                                'event_start_hr': event_rec.event_start_hr,
                                'event_start_min': event_rec.event_start_min,
                                'customer_basis': event_rec.customer_basis,
                                'po_no': event_rec.po_no,
                                'medical_no': event_rec.medical_no,
                                'order_note': event_rec.order_note ,
                                'event_date': event_rec.event_date,
                                'dr_name': event_rec.dr_name,
                                'job_offered_interpreters_name': event_rec.job_offered_interpreters_name,
                                'task_state': event_rec.task_state,
                                'cost_center': event_rec.cost_center,
                                'emergency_rate': event_rec.emergency_rate,
                                'all_interpreter_email':event_rec.all_interpreter_email,
                                'interpreters_phone':event_rec.interpreters_phone,
                                'customer_group': event_rec.customer_group,
                                'single_interpreter':single_interpreter,
                                'actual_event_end': event_rec.actual_event_end,
                                'actual_event_start': event_rec.actual_event_start,
                                'job_schedule_id': event_rec.job_schedule_id,
                                'employer': event_rec.employer,
                                'mobile_sync': event_rec.mobile_sync,
                                'mobile_event': event_rec.mobile_event,
                                'cust_edit': event_rec.cust_edit,
                                'verified_dt': event_rec.verified_dt,
                                'verified_by': event_rec.verified_by,
                                'stat': event_rec.stat,
                                'no_editable': event_rec.no_editable,
                                'org_number': event_rec.org_number
                            }
                            result = sock.execute(dbname, d_uid, pwd, 'event',
                                                                    'write',[event_rec.event_old_id],
                                                                    event_vals)
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model == 'interpreter.alloc.history':
                        try:
                            interpreter_alloc_history_rec = self.env['interpreter.alloc.history'].browse(rec.res_id)
                            if interpreter_alloc_history_rec.name:
                                partner_id= interpreter_alloc_history_rec.name.customer_record_old_id
                            else:
                                partner_id=False
                            if interpreter_alloc_history_rec.event_id:
                                event_id = interpreter_alloc_history_rec.event_id.event_old_id
                            else:
                                event_id = False
                            interpreter_alloc_his_vals = {
                                'name': partner_id,
                                'event_id': event_id,
                                'voicemail_msg': interpreter_alloc_history_rec.voicemail_msg,
                                'state': interpreter_alloc_history_rec.state,
                                'event_date': interpreter_alloc_history_rec.event_date,
                                'allocate_date': interpreter_alloc_history_rec.allocate_date,
                                'cancel_date': interpreter_alloc_history_rec.cancel_date,
                                'confirm_date': interpreter_alloc_history_rec.confirm_date,
                                'event_end': interpreter_alloc_history_rec.event_end,
                                'event_start': interpreter_alloc_history_rec.event_start,
                                'event_start_date': interpreter_alloc_history_rec.event_start_date,
                            }
                            result=sock.execute(dbname, d_uid, pwd, 'interpreter.alloc.history','write',[interpreter_alloc_history_rec.interpreter_alloc_his_old_id],interpreter_alloc_his_vals)
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model =='interpreter.history':
                        try:
                            interpreter_history_rec = self.env['interpreter.history'].browse(rec.res_id)
                            if interpreter_history_rec.name:
                                name=interpreter_history_rec.name.customer_record_old_id
                            else:
                                name=False
                            if interpreter_history_rec.task_id:
                                task_id=interpreter_history_rec.task_id.project_task_old_id
                            else:
                                task_id=False
                            if interpreter_history_rec.event_id:
                                event_id=interpreter_history_rec.event_id.event_old_id
                            else:
                                event_id=False
                            if interpreter_history_rec.language_id:
                                language_id= interpreter_history_rec.language_id.language_old_id
                            else:
                                language_id=False
                            if interpreter_history_rec.company_id:
                                company_id=interpreter_history_rec.company_id.res_company_old_id
                            else:
                                company_id=False
                            inter_his_vals={
                                'name':name,
                                'task_id':task_id,
                                'event_id':event_id,
                                'language_id':language_id,
                                'company_id':company_id,
                                'voicemail_msg':interpreter_history_rec.voicemail_msg,
                                'state':interpreter_history_rec.state,
                                'event_date':interpreter_history_rec.event_date,
                                'event_start_time':interpreter_history_rec.event_start_time,
                                'event_end_time':interpreter_history_rec.event_end_time,
                            }
                            result=sock.execute(dbname, d_uid, pwd, 'interpreter.history','write',[interpreter_history_rec.inter_his_old_id],inter_his_vals)
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model =='event.interpreter.calendar':
                        try:
                            event_interpreter_calendar_rec = self.env['event.interpreter.calendar'].browse(rec.res_id)
                            if event_interpreter_calendar_rec.event_id:
                                event_id = event_interpreter_calendar_rec.event_id.event_old_id
                            else:
                                event_id=False
                            if event_interpreter_calendar_rec.partner_id:
                                partner_id = event_interpreter_calendar_rec.partner_id.customer_record_old_id
                            else:
                                partner_id=False
                            if event_interpreter_calendar_rec.company_id:
                                company_id = event_interpreter_calendar_rec.company_id.res_company_old_id
                            else:
                                company_id=False

                            evnt_inrt_calendar_vals = {
                                # 'event_intr_calendar_old_id': value[0].strip(),
                                'allday': event_interpreter_calendar_rec.allday,
                                'start_time': event_interpreter_calendar_rec.start_time,
                                'duration': event_interpreter_calendar_rec.duration,
                                'event_id': event_id,
                                'name': event_interpreter_calendar_rec.name,
                                'note': event_interpreter_calendar_rec.note,
                                'partner_id': partner_id,
                                'end_time': event_interpreter_calendar_rec.end_time,
                                'cancelled': event_interpreter_calendar_rec.cancelled,
                                'is_event': event_interpreter_calendar_rec.is_event,
                                'company_id': company_id,
                            }
                            result=sock.execute(dbname, d_uid, pwd, 'event.interpreter.calendar','write',[event_interpreter_calendar_rec.event_intr_calendar_old_id],evnt_inrt_calendar_vals)
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model == 'select.interpreter.line':
                        try:
                            select_interpreter_line_rec = self.env['select.interpreter.line'].browse(rec.res_id)
                            if select_interpreter_line_rec.interpreter_id:
                                interpreter_id = select_interpreter_line_rec.interpreter_id.customer_record_old_id
                            else:
                                interpreter_id = False
                            if select_interpreter_line_rec.event_id:
                                event_id = select_interpreter_line_rec.event_id.event_old_id
                            else:
                                event_id = False
                            interpreter_line_vals = {
                                                    'rate':select_interpreter_line_rec.rate,
                                                    'interpreter_id':interpreter_id,
                                                    'preferred':select_interpreter_line_rec.preferred,
                                                    'event_id':event_id,
                                                    'visited':select_interpreter_line_rec.visited,
                                                    'visited_date':select_interpreter_line_rec.visited_date,
                                                    'voicemail_msg':select_interpreter_line_rec.voicemail_msg,
                                                    'duration':select_interpreter_line_rec.duration,
                                                    'distance':select_interpreter_line_rec.distance,
                                                    'state':select_interpreter_line_rec.state,
                                                    'select_interpreter':select_interpreter_line_rec.select_interpreter,
                                                     # 'parent_state':parent_state,
                                                     # 'company_id':company_id
                                                    }
                            result=sock.execute(dbname, d_uid, pwd, 'select.interpreter.line','write',[select_interpreter_line_rec.interpreter_line_old_id],interpreter_line_vals)
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model == 'select.translator.line':
                        try:
                            select_translator_line_rec = self.env['select.translator.line'].browse(rec.res_id)
                            if select_translator_line_rec.event_id:
                                event_id = select_translator_line_rec.event_id.event_old_id
                            else:
                                event_id = False
                            if select_translator_line_rec.translator_id:
                                translator_id = select_translator_line_rec.translator_id.customer_record_old_id
                            else:
                                translator_id = False
                            translator_line_vals = {
                                                     'select': select_translator_line_rec.select,
                                                     'event_id': event_id,
                                                     'visited': select_translator_line_rec.visited,
                                                     'visited_date': select_translator_line_rec.visited_date,
                                                     'voicemail_msg': select_translator_line_rec.voicemail_msg,
                                                     'duration': select_translator_line_rec.duration,
                                                     'distance': select_translator_line_rec.distance,
                                                     'state': select_translator_line_rec.state,
                                                     'translator_id': translator_id,
                                                     }
                            result=sock.execute(dbname, d_uid, pwd, 'select.translator.line','write',[select_translator_line_rec.translator_line_old_id],translator_line_vals)
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model == 'assign.translator.history':
                        try:
                            assign_translator_history_rec = self.env['assign.translator.history'].browse(rec.res_id)
                            if assign_translator_history_rec.name:
                                name = assign_translator_history_rec.name.customer_record_old_id
                            else:
                                name=False
                            if assign_translator_history_rec.partner_id:
                                partner_id = assign_translator_history_rec.partner_id.customer_record_old_id
                            else:
                                partner_id=False
                            if assign_translator_history_rec.event_id:
                                event_id = assign_translator_history_rec.event_id.event_old_id
                            else:
                                event_id=False
                            as_trans_his_vals = {
                                # 'assign_trans_his_old_id': row[0].strip() or '',
                                'name': name,
                                'partner_id': partner_id,
                                'event_date': assign_translator_history_rec.event_date,
                                'event_id': event_id,
                                'state': assign_translator_history_rec.state,
                                'schedule_translator_event_time': assign_translator_history_rec.schedule_translator_event_time,
                            }
                            result=sock.execute(dbname, d_uid, pwd, 'assign.translator.history','write',[assign_translator_history_rec.assign_trans_his_old_id],as_trans_his_vals)
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                elif rec.method == 'unlink':
                    if rec.model_id.model == 'interpreter.alloc.history':
                        try:
                            interpreter_alloc_history_rec = self.env['interpreter.alloc.history'].browse(rec.res_id)
                            result = sock.execute(dbname, d_uid, pwd, 'interpreter.alloc.history', 'unlink',
                                              [interpreter_alloc_history_rec.interpreter_alloc_his_old_id])
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model =='interpreter.history':
                        try:
                            interpreter_history_rec = self.env['interpreter.history'].browse(rec.res_id)
                            result=sock.execute(dbname, d_uid, pwd, 'interpreter.history','unlink',[interpreter_history_rec.inter_his_old_id])
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model =='event.interpreter.calendar':
                        try:
                            event_interpreter_calendar_rec = self.env['event.interpreter.calendar'].browse(rec.res_id)
                            result=sock.execute(dbname, d_uid, pwd, 'event.interpreter.calendar','unlink',[event_interpreter_calendar_rec.event_intr_calendar_old_id])
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model == 'select.interpreter.line':
                        try:
                            select_interpreter_line_rec = self.env['select.interpreter.line'].browse(rec.res_id)
                            result=sock.execute(dbname, d_uid, pwd, 'select.interpreter.line','unlink',[select_interpreter_line_rec.interpreter_line_old_id])
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model == 'select.translator.line':
                        try:
                            select_translator_line_rec = self.env['select.translator.line'].browse(rec.res_id)
                            result=sock.execute(dbname, d_uid, pwd, 'select.translator.line','unlink',[select_translator_line_rec.translator_line_old_id])
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model == 'assign.translator.history':
                        try:
                            assign_translator_history_rec = self.env['assign.translator.history'].browse(rec.res_id)
                            result=sock.execute(dbname, d_uid, pwd, 'assign.translator.history','unlink',[assign_translator_history_rec.assign_trans_his_old_id])
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()

    @api.model
    def sync_partner_user_and_ir_attachment_records(self):
        model_ids = self.env['ir.model'].search(
            [('model', 'in',
              ['res.users', 'res.partner', 'ir.attachment'])]).ids
        recs_to_sync = self.env['auditlog.log'].search(
            [('sync', '=', False), ('error', '=', False), ('model_id', 'in', model_ids)], order='create_date asc')
        if recs_to_sync:
            config_obj = self.env['server.config']
            config_ids = config_obj.search([])
            if not config_ids:
                raise UserError(_('No Active server config found!'))
            config = config_ids[0]
            ip = config.host  # Host
            port = config.port  # Port
            username = config.username  # the userl
            pwd = config.password  # the password of the user
            dbname = config.dbname  # the db name
            sock_common = xmlrpclib.ServerProxy('http://' + ip + ':' + port + '/xmlrpc/common')
            d_uid = sock_common.login(dbname, username, pwd)
            sock = xmlrpclib.ServerProxy('http://' + ip + ':' + port + '/xmlrpc/object')
            for rec in recs_to_sync:
                if rec.method == 'create':
                    if rec.model_id.model == 'res.partner':
                        try:
                            res_partner_rec =self.env['res.partner'].browse(rec.res_id)
                            if res_partner_rec.company_id:
                                company_id = res_partner_rec.company_id.res_company_old_id
                            else:
                                company_id=False
                            if res_partner_rec.user_id:
                                user_id = res_partner_rec.user_id.user_old_id
                            else:
                                user_id=False
                            if res_partner_rec.parent_id:
                                parent_id = res_partner_rec.parent_id.customer_record_old_id
                            else:
                                parent_id=False
                            if res_partner_rec.state_id:
                                state_id = res_partner_rec.state_id.state7_id
                            else:
                                state_id=False
                            # if res_partner_rec.notification_email_send == 'always':
                            #     notification_email_send = 'email'
                            # else:
                            #     notification_email_send = 'none'
                            if res_partner_rec.billing_contact_id:
                                billing_contact_id = res_partner_rec.billing_contact_id.customer_record_old_id
                            else:
                                billing_contact_id=False
                            if res_partner_rec.meta_zone_id:
                                meta_zone_id = res_partner_rec.meta_zone_id.meta_zone_old_id
                            else:
                                meta_zone_id=False
                            if res_partner_rec.zone_id:
                                zone_id = res_partner_rec.zone_id.zone_old_id
                            else:
                                zone_id=False
                            if res_partner_rec.language_id:
                                language_id = res_partner_rec.language_id.language_old_id
                            else:
                                language_id=False
                            if res_partner_rec.billing_partner_id:
                                billing_partner_id = res_partner_rec.billing_partner_id.customer_record_old_id
                            else:
                                billing_partner_id=False
                            if res_partner_rec.sales_representative_id:
                                sales_representative_id = res_partner_rec.sales_representative_id.user_old_id
                            else:
                                sales_representative_id=False
                            if res_partner_rec.scheduler_id:
                                scheduler_id = res_partner_rec.scheduler_id.user_old_id
                            else:
                                scheduler_id=False
                            if res_partner_rec.head_contact_id:
                                head_contact_id = res_partner_rec.head_contact_id.customer_record_old_id
                            else:
                                head_contact_id=False
                            if res_partner_rec.customer_group_id:
                                customer_group_id = res_partner_rec.customer_group_id.customer_group_old_id
                            else:
                                customer_group_id=False
                            if res_partner_rec.interpreter_id:
                                interpreter_id = res_partner_rec.interpreter_id.customer_record_old_id
                            else:
                                interpreter_id=False
                            block_inter_ids=[]
                            for block_interpreter_id in res_partner_rec.block_inter_ids:
                                block_inter_ids.append(block_interpreter_id.customer_record_old_id)
                            customer_vals = {
                                'block_inter_ids': [(6, 0, block_inter_ids)],
                                # 'customer_record_old_id': int(customer_record_old_id),
                                'name': res_partner_rec.name,
                                'lang': res_partner_rec.lang,
                                'company_id': company_id,
                                'comment': res_partner_rec.comment,
                                'barcode': res_partner_rec.ean13,
                                'color': res_partner_rec.color,
                                # 'use_parent_address': True if use_parent_address=='t' else False,
                                'active': res_partner_rec.active,
                                'street': res_partner_rec.street,
                                'supplier': res_partner_rec.supplier,
                                'city': res_partner_rec.city,
                                'user_id': user_id,
                                'zip': res_partner_rec.zip,
                                'country_id': 235,
                                'parent_id': parent_id,
                                'employee': res_partner_rec.employee,
                                'type': res_partner_rec.type,
                                'email': res_partner_rec.email,
                                'vat': res_partner_rec.vat,
                                'website': res_partner_rec.website,
                                'fax': res_partner_rec.fax,
                                'street2': res_partner_rec.street2,
                                'phone': res_partner_rec.phone,
                                'credit_limit': res_partner_rec.credit_limit,
                                'date': res_partner_rec.date,
                                'tz': res_partner_rec.tz,
                                'customer': res_partner_rec.customer,
                                'image_medium': res_partner_rec.image_medium,
                                'mobile': res_partner_rec.mobile,
                                'ref': res_partner_rec.ref,
                                'image_small': res_partner_rec.image_small,
                                'is_company': res_partner_rec.is_company,
                                'state_id': state_id,
                                # 'notify_email':notification_email_send,
                                'opt_out': res_partner_rec.opt_out,
                                'signup_type': res_partner_rec.signup_type,
                                'signup_expiration': res_partner_rec.signup_expiration,
                                'signup_token': res_partner_rec.signup_token,
                                'last_reconciliation_date':  res_partner_rec.last_time_entries_checked,
                                'debit_limit': res_partner_rec.debit_limit,
                                # 'section_id':section_id,
                                'display_name': res_partner_rec.display_name,
                                # 'customer_profile_id':customer_profile_id,
                                'date_localization': res_partner_rec.date_localization,
                                'is_agency': res_partner_rec.is_agency,
                                'last_name': res_partner_rec.last_name,
                                'cust_type': res_partner_rec.cust_type,
                                'wb_on_file': res_partner_rec.wb_on_file,
                                'short_name': res_partner_rec.short_name,

                                'fee_note': res_partner_rec.fee_note,
                                'billing_contact': res_partner_rec.billing_contact,
                                # 'is_gpuid':is_gpuid,
                                # 'billing_addr':billing_addr,
                                'ssnid': res_partner_rec.ssnid,
                                'billing_contact_id': billing_contact_id,
                                'meta_zone_id': meta_zone_id,
                                'gender': res_partner_rec.gender,
                                'is_payee': res_partner_rec.is_payee,

                                'extension2': res_partner_rec.extension2,
                                'extension1': res_partner_rec.extension1,
                                'customer_profile': res_partner_rec.customer_profile,
                                # 'sddhs':sddhs,
                                'phone2': res_partner_rec.phone2,
                                'phone3': res_partner_rec.phone3,

                                'phone4': res_partner_rec.phone4,
                                'do_editing': res_partner_rec.do_editing,
                                'extension': res_partner_rec.extension,
                                # 'email2':email2,
                                'gpuid': res_partner_rec.gpuid,
                                'is_alert': res_partner_rec.is_alert,
                                'csid': res_partner_rec.csid,
                                'due_days': res_partner_rec.due_days,
                                # 'bill_miles':bill_miles,
                                'minimum_rate': res_partner_rec.minimum_rate,
                                # 'customer_letter':customer_letter,
                                # 'staff_id':True if staff_id=='t' else False,
                                'is_csid': res_partner_rec.is_csid,
                                'fax2': res_partner_rec.fax2,
                                'need_glcode': res_partner_rec.need_glcode,
                                'end_date': res_partner_rec.end_date,
                                # 'country_id2':235,
                                'sinid': res_partner_rec.sinid,
                                'zone_id': zone_id,
                                'auth_cc_number': res_partner_rec.auth_cc_number,
                                'latitude': res_partner_rec.latitude,
                                # 'phone_type_id1':phone_type_id1,
                                # 'phone_type_id3':phone_type_id3,
                                # 'phone_type_id2':phone_type_id2,
                                # 'phone_type_id4':phone_type_id4,
                                'longitude': res_partner_rec.longitude,
                                # 'customer_type':customer_type,
                                # 'suffix':suffix,
                                'order_note': res_partner_rec.order_note,
                                'ordering_contact': res_partner_rec.ordering_contact,
                                # 'distribution':distribution,
                                # 'vendor_id2':vendor_id2,
                                # 'is_contact':is_contact,
                                'min_editing_rate': res_partner_rec.min_editing_rate,
                                'is_schedular': res_partner_rec.is_schedular,
                                # 'city2':city2,
                                'billing_comment': res_partner_rec.billing_comment,
                                # 'contact_letter':contact_letter,
                                'middle_name': res_partner_rec.middle_name,
                                'is_geo': res_partner_rec.is_geo,
                                'company_name': res_partner_rec.company_name,
                                'auth_cc_expiration_date': res_partner_rec.auth_cc_expiration_date,
                                'department': res_partner_rec.department,
                                'login_id': res_partner_rec.login_id,
                                'language_id': language_id,
                                'is_adjuster': res_partner_rec.is_adjuster,
                                'expiry_date': res_partner_rec.expiry_date,
                                'confirmation_email': res_partner_rec.confirmation_email,
                                'telephone_interpretation': res_partner_rec.telephone_interpretation,
                                'quickbooks_id': res_partner_rec.quickbooks_id,
                                'gsa': res_partner_rec.gsa,
                                'ext': res_partner_rec.ext,
                                'billing_partner_id': billing_partner_id,
                                'modem': res_partner_rec.modem,
                                'vendor_id': res_partner_rec.vendor_id,
                                'complete_name': res_partner_rec.complete_name,
                                # 'inc_min':inc_min,
                                'provider_id': res_partner_rec.provider_id,

                                'special_customer': res_partner_rec.special_customer,
                                # 'base_hour_conf':base_hour_conf,
                                # 'base_hour_med':base_hour_med,
                                'last_update_date': res_partner_rec.last_update_date,
                                # 'base_hour_depos':base_hour_depos,
                                # 'inc_min_depos':inc_min_depos,
                                'contract_on_file': res_partner_rec.contract_on_file,
                                'is_translation_active': res_partner_rec.is_translation_active,
                                'sales_representative_id': sales_representative_id,
                                'has_login': res_partner_rec.has_login,
                                'is_interpretation_active': res_partner_rec.is_interpretation_active,
                                'is_transportation_active': res_partner_rec.is_transportation_active,
                                # 'event_approval':True if event_approval=='t' else False,
                                # 'event_verification':True if event_verification=='t' else False,
                                'suppress_email': res_partner_rec.suppress_email,
                                'scheduler_id': scheduler_id,
                                'head_contact_id': head_contact_id,
                                'customer_basis': res_partner_rec.customer_basis,
                                'mental_prog': res_partner_rec.mental_prog,
                                'rubrik': res_partner_rec.rubrik,
                                'rate': res_partner_rec.rate,
                                'discount': res_partner_rec.discount,
                                'bill_miles_after': res_partner_rec.bill_miles_after,
                                'is_monthly': res_partner_rec.is_monthly,
                                'contract_no': res_partner_rec.contract_no,
                                'customer_group_id': customer_group_id,
                                'interpreter_id': interpreter_id,
                                # 'sd_id':sd_id,
                                'albors_id': res_partner_rec.albors_id,
                                'is_sync': res_partner_rec.is_sync,
                                # 'parent_cust_id':parent_cust_id,
                                'opt_for_sms': res_partner_rec.opt_for_sms,
                                'ext_phone3': res_partner_rec.ext_phone3,
                                'ext_phone1': res_partner_rec.ext_phone1,
                                'ext_phone4': res_partner_rec.ext_phone4,
                                'ext_phone2': res_partner_rec.ext_phone2,
                                'dob': res_partner_rec.dob,
                                'age': res_partner_rec.age,
                                # 'opt_out_of_feedback_emails':opt_out_of_feedback_emails,
                                'partner_id_sms':res_partner_rec.partner_id_sms,
                            }
                            customer_record_old_id = sock.execute(dbname, d_uid, pwd, 'res.partner', 'create',
                                                                  customer_vals)
                            res_partner_rec.write({'customer_record_old_id': customer_record_old_id})
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model == 'res.users':
                        try:
                            res_users_rec =self.env['res.users'].browse(rec.res_id)
                            if res_users_rec.company_id:
                                company_id = res_users_rec.company_id.res_company_old_id
                            else:
                                company_id = False
                            if res_users_rec.partner_id:
                                partner_id = res_users_rec.partner_id.customer_record_old_id
                            else:
                                partner_id = False
                            if res_users_rec.zone_id:
                                zone_id=res_users_rec.zone_id.zone_old_id

                            else:
                                zone_id=False
                            group_ids=[]
                            for g_id in res_users_rec.groups_id:
                                group_id= g_id.group_old_id
                                if group_id:
                                    group_ids.append(group_id)

                            user_vals = {
                                # 'user_old_id': user_old_id,
                                # 'name':res_users_rec.login,
                                'active': res_users_rec.active,
                                'login': res_users_rec.login,
                                'password': password,
                                'groups_id': [(6, 0, group_ids)],
                                'company_id': company_id,
                                'partner_id': partner_id,
                                'login_date': res_users_rec.login_date,
                                'signature': res_users_rec.signature,
                                'share': res_users_rec.share,
                                'user_type': res_users_rec.user_type,
                                'entity_id': res_users_rec.entity_id,
                                'mail_group': res_users_rec.mail_group,
                                'login_id': res_users_rec.login_id,
                                'require_to_reset': res_users_rec.require_to_reset,
                                'state': 'active',
                                 'company_ids': [(6, 0, [company_id])],
                                'zone_id': zone_id,
                            }
                            for line in rec.line_ids:
                                if line.field_name=='password':
                                    if line.new_value_text:
                                        user_vals.update({'password':line.new_value_text})
                            user_old_id = sock.execute(dbname, d_uid, pwd, 'res.users', 'create',
                                                                  user_vals)
                            res_users_rec.write({'user_old_id': user_old_id})
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model == 'ir.attachment':
                        try:
                            ir_attachment_rec =self.env['ir.attachment'].browse(rec.res_id)
                            if ir_attachment_rec.event_id:
                                event_old_id = ir_attachment_rec.event_id.event_old_id
                            else:
                                event_old_id=False
                            if ir_attachment_rec.company_id:
                                company_id = ir_attachment_rec.company_id.res_company_old_id
                            else:
                                company_id=False
                            if ir_attachment_rec.user_id:
                                user_id = ir_attachment_rec.user_id.user_old_id
                            else:
                                user_id=False

                            if ir_attachment_rec.res_model == 'event':
                                old_res_id = self.env['event'].search(
                                    [('id', '=', ir_attachment_rec.res_id)],
                                    limit=1).event_old_id
                            elif ir_attachment_rec.res_model == 'select.interpreter.line':
                                old_res_id = self.env['select.interpreter.line'].search(
                                    [('id', '=', ir_attachment_rec.res_id)], limit=1).interpreter_line_old_id
                            elif ir_attachment_rec.res_model == 'account.invoice':
                                old_res_id = self.env['account.invoice'].search(
                                    [('id', '=', ir_attachment_rec.res_id)],
                                    limit=1).invoice_old_id
                            elif ir_attachment_rec.res_model == 'project.task':
                                old_res_id = self.env['project.task'].search(
                                    [('id', '=', ir_attachment_rec.res_id)], limit=1).project_task_old_id
                            elif ir_attachment_rec.res_model == 'res.partner':
                                old_res_id = self.env['res.partner'].search(
                                    [('id', '=', ir_attachment_rec.res_id)], limit=1).customer_record_old_id
                            elif ir_attachment_rec.res_model == 'patient':
                                old_res_id = self.env['patient'].search(
                                    [('id', '=', ir_attachment_rec.res_id)],
                                    limit=1).patient_old_id
                            elif ir_attachment_rec.res_model == 'incoming.fax':
                                old_res_id = self.env['incoming.fax'].search(
                                    [('id', '=', ir_attachment_rec.res_id)],
                                    limit=1).fax_in_old_id
                            else:
                                old_res_id = False
                            ir_attachment_vals = {
                                'name': ir_attachment_rec.name,
                                'datas_fname': ir_attachment_rec.datas_fname,
                                'res_model': ir_attachment_rec.res_model,
                                'res_id': old_res_id,
                                'create_uid': user_id,
                                'user_id': user_id,
                                'company_id': company_id,
                                'type': ir_attachment_rec.type,
                                'store_fname': ir_attachment_rec.store_fname,
                                'index_content': ir_attachment_rec.index_content,
                                'attach': ir_attachment_rec.attach,
                                'no_of_pages': ir_attachment_rec.no_of_pages,
                                'no_of_words': ir_attachment_rec.no_of_words,
                                'event_id': event_old_id,
                                'db_datas':ir_attachment_rec.db_datas
                                # 'in_fax_id' = fields.Many2one('incoming.fax', 'Incoming Fax')
                                # 'document_type_id': document_type_id,
                            }
                            ir_attach_old_id = sock.execute(dbname, d_uid, pwd, 'ir.attachment', 'create',
                                                                  ir_attachment_vals)
                            ir_attachment_rec.write({'ir_attach_old_id': ir_attach_old_id})
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                elif rec.method == 'write':
                    if rec.model_id.model == 'res.partner':
                        try:
                            res_partner_rec =self.env['res.partner'].browse(rec.res_id)
                            if res_partner_rec.company_id:
                                company_id = res_partner_rec.company_id.res_company_old_id
                            else:
                                company_id=False
                            if res_partner_rec.user_id:
                                user_id = res_partner_rec.user_id.user_old_id
                            else:
                                user_id=False
                            if res_partner_rec.parent_id:
                                parent_id = res_partner_rec.parent_id.customer_record_old_id
                            else:
                                parent_id=False
                            if res_partner_rec.state_id:
                                state_id = res_partner_rec.state_id.state7_id
                            else:
                                state_id=False
                            # if res_partner_rec.notification_email_send == 'always':
                            #     notification_email_send = 'email'
                            # else:
                            #     notification_email_send = 'none'
                            if res_partner_rec.billing_contact_id:
                                billing_contact_id = res_partner_rec.billing_contact_id.customer_record_old_id
                            else:
                                billing_contact_id=False
                            if res_partner_rec.meta_zone_id:
                                meta_zone_id = res_partner_rec.meta_zone_id.meta_zone_old_id
                            else:
                                meta_zone_id=False
                            if res_partner_rec.zone_id:
                                zone_id = res_partner_rec.zone_id.zone_old_id
                            else:
                                zone_id=False
                            if res_partner_rec.language_id:
                                language_id = res_partner_rec.language_id.language_old_id
                            else:
                                language_id=False
                            if res_partner_rec.billing_partner_id:
                                billing_partner_id = res_partner_rec.billing_partner_id.customer_record_old_id
                            else:
                                billing_partner_id=False
                            if res_partner_rec.sales_representative_id:
                                sales_representative_id = res_partner_rec.sales_representative_id.user_old_id
                            else:
                                sales_representative_id=False
                            if res_partner_rec.scheduler_id:
                                scheduler_id = res_partner_rec.scheduler_id.user_old_id
                            else:
                                scheduler_id=False
                            if res_partner_rec.head_contact_id:
                                head_contact_id = res_partner_rec.head_contact_id.customer_record_old_id
                            else:
                                head_contact_id=False
                            if res_partner_rec.customer_group_id:
                                customer_group_id = res_partner_rec.customer_group_id.customer_group_old_id
                            else:
                                customer_group_id=False
                            if res_partner_rec.interpreter_id:
                                interpreter_id = res_partner_rec.interpreter_id.customer_record_old_id
                            else:
                                interpreter_id=False

                            block_inter_ids = []
                            for block_interpreter_id in res_partner_rec.block_inter_ids:
                                block_inter_ids.append(block_interpreter_id.customer_record_old_id)
                            customer_vals = {
                                'block_inter_ids': [(6, 0, block_inter_ids)],
                                'name': res_partner_rec.name,
                                'lang': res_partner_rec.lang,
                                'company_id': company_id,
                                'comment': res_partner_rec.comment,
                                'barcode': res_partner_rec.ean13,
                                'color': res_partner_rec.color,
                                # 'use_parent_address': True if use_parent_address=='t' else False,
                                'active': res_partner_rec.active,
                                'street': res_partner_rec.street,
                                'supplier': res_partner_rec.supplier,
                                'city': res_partner_rec.city,
                                'user_id': user_id,
                                'zip': res_partner_rec.zip,
                                'country_id': 235,
                                'parent_id': parent_id,
                                'employee': res_partner_rec.employee,
                                'type': res_partner_rec.type,
                                'email': res_partner_rec.email,
                                'vat': res_partner_rec.vat,
                                'website': res_partner_rec.website,
                                'fax': res_partner_rec.fax,
                                'street2': res_partner_rec.street2,
                                'phone': res_partner_rec.phone,
                                'credit_limit': res_partner_rec.credit_limit,
                                'date': res_partner_rec.date,
                                'tz': res_partner_rec.tz,
                                'customer': res_partner_rec.customer,
                                'image_medium': res_partner_rec.image_medium,
                                'mobile': res_partner_rec.mobile,
                                'ref': res_partner_rec.ref,
                                'image_small': res_partner_rec.image_small,
                                'is_company': res_partner_rec.is_company,
                                'state_id': state_id,
                                # 'notify_email':notification_email_send,
                                'opt_out': res_partner_rec.opt_out,
                                'signup_type': res_partner_rec.signup_type,
                                'signup_expiration': res_partner_rec.signup_expiration,
                                'signup_token': res_partner_rec.signup_token,
                                'last_reconciliation_date':  res_partner_rec.last_time_entries_checked,
                                'debit_limit': res_partner_rec.debit_limit,
                                # 'section_id':section_id,
                                'display_name': res_partner_rec.display_name,
                                # 'customer_profile_id':customer_profile_id,
                                'date_localization': res_partner_rec.date_localization,
                                'is_agency': res_partner_rec.is_agency,
                                'last_name': res_partner_rec.last_name,
                                'cust_type': res_partner_rec.cust_type,
                                'wb_on_file': res_partner_rec.wb_on_file,
                                'short_name': res_partner_rec.short_name,

                                'fee_note': res_partner_rec.fee_note,
                                'billing_contact': res_partner_rec.billing_contact,
                                # 'is_gpuid':is_gpuid,
                                # 'billing_addr':billing_addr,
                                'ssnid': res_partner_rec.ssnid,
                                'billing_contact_id': billing_contact_id,
                                'meta_zone_id': meta_zone_id,
                                'gender': res_partner_rec.gender,
                                'is_payee': res_partner_rec.is_payee,

                                'extension2': res_partner_rec.extension2,
                                'extension1': res_partner_rec.extension1,
                                'customer_profile': res_partner_rec.customer_profile,
                                # 'sddhs':sddhs,
                                'phone2': res_partner_rec.phone2,
                                'phone3': res_partner_rec.phone3,

                                'phone4': res_partner_rec.phone4,
                                'do_editing': res_partner_rec.do_editing,
                                'extension': res_partner_rec.extension,
                                # 'email2':email2,
                                'gpuid': res_partner_rec.gpuid,
                                'is_alert': res_partner_rec.is_alert,
                                'csid': res_partner_rec.csid,
                                'due_days': res_partner_rec.due_days,
                                # 'bill_miles':bill_miles,
                                'minimum_rate': res_partner_rec.minimum_rate,
                                # 'customer_letter':customer_letter,
                                # 'staff_id':True if staff_id=='t' else False,
                                'is_csid': res_partner_rec.is_csid,
                                'fax2': res_partner_rec.fax2,
                                'need_glcode': res_partner_rec.need_glcode,
                                'end_date': res_partner_rec.end_date,
                                # 'country_id2':235,
                                'sinid': res_partner_rec.sinid,
                                'zone_id': zone_id,
                                'auth_cc_number': res_partner_rec.auth_cc_number,
                                'latitude': res_partner_rec.latitude,
                                # 'phone_type_id1':phone_type_id1,
                                # 'phone_type_id3':phone_type_id3,
                                # 'phone_type_id2':phone_type_id2,
                                # 'phone_type_id4':phone_type_id4,
                                'longitude': res_partner_rec.longitude,
                                # 'customer_type':customer_type,
                                # 'suffix':suffix,
                                'order_note': res_partner_rec.order_note,
                                'ordering_contact': res_partner_rec.ordering_contact,
                                # 'distribution':distribution,
                                # 'vendor_id2':vendor_id2,
                                # 'is_contact':is_contact,
                                'min_editing_rate': res_partner_rec.min_editing_rate,
                                'is_schedular': res_partner_rec.is_schedular,
                                # 'city2':city2,
                                'billing_comment': res_partner_rec.billing_comment,
                                # 'contact_letter':contact_letter,
                                'middle_name': res_partner_rec.middle_name,
                                'is_geo': res_partner_rec.is_geo,
                                'company_name': res_partner_rec.company_name,
                                'auth_cc_expiration_date': res_partner_rec.auth_cc_expiration_date,
                                'department': res_partner_rec.department,
                                'login_id': res_partner_rec.login_id,
                                'language_id': language_id,
                                'is_adjuster': res_partner_rec.is_adjuster,
                                'expiry_date': res_partner_rec.expiry_date,
                                'confirmation_email': res_partner_rec.confirmation_email,
                                'telephone_interpretation': res_partner_rec.telephone_interpretation,
                                'quickbooks_id': res_partner_rec.quickbooks_id,
                                'gsa': res_partner_rec.gsa,
                                'ext': res_partner_rec.ext,
                                'billing_partner_id': billing_partner_id,
                                'modem': res_partner_rec.modem,
                                'vendor_id': res_partner_rec.vendor_id,
                                'complete_name': res_partner_rec.complete_name,
                                # 'inc_min':inc_min,
                                'provider_id': res_partner_rec.provider_id,

                                'special_customer': res_partner_rec.special_customer,
                                # 'base_hour_conf':base_hour_conf,
                                # 'base_hour_med':base_hour_med,
                                'last_update_date': res_partner_rec.last_update_date,
                                # 'base_hour_depos':base_hour_depos,
                                # 'inc_min_depos':inc_min_depos,
                                'contract_on_file': res_partner_rec.contract_on_file,
                                'is_translation_active': res_partner_rec.is_translation_active,
                                'sales_representative_id': sales_representative_id,
                                'has_login': res_partner_rec.has_login,
                                'is_interpretation_active': res_partner_rec.is_interpretation_active,
                                'is_transportation_active': res_partner_rec.is_transportation_active,
                                # 'event_approval':True if event_approval=='t' else False,
                                # 'event_verification':True if event_verification=='t' else False,
                                'suppress_email': res_partner_rec.suppress_email,
                                'scheduler_id': scheduler_id,
                                'head_contact_id': head_contact_id,
                                'customer_basis': res_partner_rec.customer_basis,
                                'mental_prog': res_partner_rec.mental_prog,
                                'rubrik': res_partner_rec.rubrik,
                                'rate': res_partner_rec.rate,
                                'discount': res_partner_rec.discount,
                                'bill_miles_after': res_partner_rec.bill_miles_after,
                                'is_monthly': res_partner_rec.is_monthly,
                                'contract_no': res_partner_rec.contract_no,
                                'customer_group_id': customer_group_id,
                                'interpreter_id': interpreter_id,
                                # 'sd_id':sd_id,
                                'albors_id': res_partner_rec.albors_id,
                                'is_sync': res_partner_rec.is_sync,
                                # 'parent_cust_id':parent_cust_id,
                                'opt_for_sms': res_partner_rec.opt_for_sms,
                                'ext_phone3': res_partner_rec.ext_phone3,
                                'ext_phone1': res_partner_rec.ext_phone1,
                                'ext_phone4': res_partner_rec.ext_phone4,
                                'ext_phone2': res_partner_rec.ext_phone2,
                                'dob': res_partner_rec.dob,
                                'age': res_partner_rec.age,
                                # 'opt_out_of_feedback_emails':opt_out_of_feedback_emails,
                                'partner_id_sms':res_partner_rec.partner_id_sms,
                            }
                            result= sock.execute(dbname, d_uid, pwd, 'res.partner', 'write',[res_partner_rec.customer_record_old_id],
                                                                  customer_vals)
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model == 'res.users':
                        try:
                            res_users_rec =self.env['res.users'].browse(rec.res_id)
                            if res_users_rec.company_id:
                                company_id = res_users_rec.company_id.res_company_old_id
                            else:
                                company_id = False
                            if res_users_rec.partner_id:
                                partner_id = res_users_rec.partner_id.customer_record_old_id
                            else:
                                partner_id = False
                            if res_users_rec.zone_id:
                                zone_id=res_users_rec.zone_id.zone_old_id

                            else:
                                zone_id=False
                            group_ids=[]
                            for g_id in res_users_rec.groups_id:
                                group_id= g_id.group_old_id
                                if group_id:
                                    group_ids.append(group_id)
                            user_vals = {
                                # 'user_old_id': user_old_id,
                                'active': res_users_rec.active,
                                'login': res_users_rec.login,
                                # 'password': 'iux@pass',
                                'groups_id': [(6, 0, group_ids)],
                                'company_id': company_id,
                                'partner_id': partner_id,
                                'login_date': res_users_rec.login_date,
                                'signature': res_users_rec.signature,
                                'share': res_users_rec.share,
                                'user_type': res_users_rec.user_type,
                                'entity_id': res_users_rec.entity_id,
                                'mail_group': res_users_rec.mail_group,
                                'login_id': res_users_rec.login_id,
                                'require_to_reset': res_users_rec.require_to_reset,
                                'company_ids': [(6, 0, [company_id])],
                                'zone_id': zone_id,
                            }
                            for line in rec.line_ids:
                                if line.field_name=='password':
                                    if line.new_value_text:
                                        user_vals.update({'password':line.new_value_text})
                            result = sock.execute(dbname, d_uid, pwd, 'res.users', 'write',
                                                  [res_users_rec.user_old_id],
                                                  user_vals)
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model == 'ir.attachment':
                        try:
                            ir_attachment_rec =self.env['ir.attachment'].browse(rec.res_id)
                            if ir_attachment_rec.ir_attach_old_id:
                                if ir_attachment_rec.event_id:
                                    event_old_id = ir_attachment_rec.event_id.event_old_id
                                else:
                                    event_old_id=False
                                if ir_attachment_rec.company_id:
                                    company_id = ir_attachment_rec.company_id.res_company_old_id
                                else:
                                    company_id=False
                                if ir_attachment_rec.user_id:
                                    user_id = ir_attachment_rec.user_id.user_old_id
                                else:
                                    user_id=False

                                if ir_attachment_rec.res_model == 'event':
                                    old_res_id = self.env['event'].search(
                                        [('id', '=', ir_attachment_rec.res_id)],
                                        limit=1).event_old_id
                                elif ir_attachment_rec.res_model == 'select.interpreter.line':
                                    old_res_id = self.env['select.interpreter.line'].search(
                                        [('id', '=', ir_attachment_rec.res_id)], limit=1).interpreter_line_old_id
                                elif ir_attachment_rec.res_model == 'account.invoice':
                                    old_res_id = self.env['account.invoice'].search(
                                        [('id', '=', ir_attachment_rec.res_id)],
                                        limit=1).invoice_old_id
                                elif ir_attachment_rec.res_model == 'project.task':
                                    old_res_id = self.env['project.task'].search(
                                        [('id', '=', ir_attachment_rec.res_id)], limit=1).project_task_old_id
                                elif ir_attachment_rec.res_model == 'res.partner':
                                    old_res_id = self.env['res.partner'].search(
                                        [('id', '=', ir_attachment_rec.res_id)], limit=1).customer_record_old_id
                                elif ir_attachment_rec.res_model == 'patient':
                                    old_res_id = self.env['patient'].search(
                                        [('id', '=', ir_attachment_rec.res_id)],
                                        limit=1).patient_old_id
                                elif ir_attachment_rec.res_model == 'incoming.fax':
                                    old_res_id = self.env['incoming.fax'].search(
                                        [('id', '=', ir_attachment_rec.res_id)],
                                        limit=1).fax_in_old_id
                                else:
                                    old_res_id = False
                                ir_attachment_vals = {
                                    'name': ir_attachment_rec.name,
                                    'datas_fname': ir_attachment_rec.datas_fname,
                                    'res_model': ir_attachment_rec.res_model,
                                    'res_id': old_res_id,
                                    'create_uid': user_id,
                                    'user_id': user_id,
                                    'company_id': company_id,
                                    'type': ir_attachment_rec.type,
                                    'store_fname': ir_attachment_rec.store_fname,
                                    'index_content': ir_attachment_rec.index_content,
                                    'attach': ir_attachment_rec.attach,
                                    'no_of_pages': ir_attachment_rec.no_of_pages,
                                    'no_of_words': ir_attachment_rec.no_of_words,
                                    'event_id': event_old_id,
                                    'db_datas':ir_attachment_rec.db_datas
                                    # 'in_fax_id' = fields.Many2one('incoming.fax', 'Incoming Fax')
                                    # 'document_type_id': document_type_id,
                                }
                                result = sock.execute(dbname, d_uid, pwd, 'ir.attachment', 'write',[ir_attachment_rec.ir_attach_old_id],
                                                                      ir_attachment_vals)
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                elif rec.method == 'unlink':
                    if rec.model_id.model == 'ir.attachment':
                        try:
                            ir_attachment_rec = self.env['ir.attachment'].browse(rec.res_id)
                            if ir_attachment_rec.ir_attach_old_id:
                                result = sock.execute(dbname, d_uid, pwd, 'ir.attachment', 'unlink',
                                                      [ir_attachment_rec.ir_attach_old_id])
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()