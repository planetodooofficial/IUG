from odoo import fields,models,api,_
import csv
import os
import StringIO
import logging
import base64
from tempfile import TemporaryFile
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.exceptions import UserError
import glob
import threading

_logger = logging.getLogger('sale')

class DataMigration3(models.TransientModel):
    _name='data.migration.wizard_last'

    upload_file3 = fields.Binary(string='File URL')
    upload_error3= fields.Binary(string='Click To Download Error Log')
    upload_error_file_name3=fields.Char("File name")

    # path = '/home/abhishek/Desktop/IUG csv server data/cust'

    # for filename in os.listdir(path):
    #     # do your stuff
    #     file= filename
    #
    # # for filename in glob.glob(os.path.join(path, '*.txt')):

    # def import_event(self):
    #     path = '/home/iuadmin/cust_upload/cust_upload/event_data'
    #     t1 = threading.Thread(target=self.import_event_function,args=(path,))
    #     t1.start()




    @api.multi
    def import_event(self):
        error_list = []
        header_list = []
        # file path should be server file path in server
        # path = '/home/abhishek/Desktop/IUG_csv_server_data/event_data' #complete record local
        # path = '/home/abhishek/Desktop/IUG_csv_server_data/event'#sample local path
        path = '/home/iuadmin/cust_upload/event_data' #complete record server
        for filename in os.listdir(path):
            # do your stuff
            file_obj = path + '/' + filename
            target_doc = csv.reader(open(file_obj, 'rU'), delimiter=",")
            row_num = 0
            faulty_rows = []
            header = ''
            data_dict = {}
            for row in target_doc:
                data_dict.update({row_num: row})
                row.append(row_num)
                row_num += 1
            for key, value in data_dict.items():
                try:
                    if key == 0:
                        header_list.append(value)
                        _logger.error('------------FILE NAME-------- %s', filename)
                    else:
                        row = value
                        _logger.error('------------row number---------- %s', key)
                        event_old_id = row[0].strip()
                        event_obj=self.env['event'].search([('event_old_id','=',event_old_id)],limit=1)
                        comment = row[5].strip() or ''
                        is_follow_up = row[6].strip() or '' #boolean
                        special_discount = row[7].strip() or ''
                        authorize_partner_id = row[8].strip() or False
                        if authorize_partner_id:
                            self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                                authorize_partner_id) + " limit 1")
                            authorize_partner_id = self._cr.fetchone()
                            authorize_partner_id = authorize_partner_id and authorize_partner_id[0] or False
                        # doctor_street = row[9].strip() or ''
                        contact_id = row[10].strip() or False
                        if contact_id:
                            self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                                contact_id) + " limit 1")
                            contact_id = self._cr.fetchone()
                            contact_id = contact_id and contact_id[0] or False
                        month = row[11].strip() or ''
                        date = row[12].strip() or '' #date
                        if date:
                            date = datetime.strptime(date, "%Y-%m-%d").strftime(DF)
                        else:
                            date = False
                        authorize_date = row[13].strip() or '' #date
                        if authorize_date:
                            authorize_date = datetime.strptime(authorize_date, "%Y-%m-%d").strftime(DF)
                        else:
                            authorize_date = False
                        transporter_id = row[14].strip() or False
                        if transporter_id:
                            self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                                transporter_id) + " limit 1")
                            transporter_id = self._cr.fetchone()
                            transporter_id = transporter_id and transporter_id[0] or False
                        user_id = row[15].strip() or False
                        if user_id:
                            self._cr.execute("select id from res_users where user_old_id=" + str(
                                user_id) + " limit 1")
                            user_id = self._cr.fetchone()
                            user_id = user_id and user_id[0] or False
                        company = row[16].strip() or ''
                        if company:
                            company_id = self.env['res.company'].search([('res_company_old_id','=',company)],limit=1).id
                        else:
                            company_id=False
                        event_start = row[17].strip() or '' #datetime
                        if event_start:
                            event_start = datetime.strptime(event_start, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
                        else:
                            event_start = False
                        # parent = row[18].strip() or ''
                        # if parent:
                        #     parent_id = self.env['patient'].search([('patient_old_id','=',parent)],limit=1).id
                        # else:
                        #     parent_id=False
                        ordering_contact_id = row[19].strip() or False
                        if ordering_contact_id:
                            self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                                ordering_contact_id) + " limit 1")
                            ordering_contact_id = self._cr.fetchone()
                            ordering_contact_id = ordering_contact_id and ordering_contact_id[0] or False
                        project_id = row[20].strip() or ''
                        suppress_email = row[21].strip() or '' #boolean
                        function = row[22].strip() or ''
                        cancel_reason = row[23].strip() or ''
                        history_id = row[24].strip() or '' #one2many
                        interpreter_id = row[25].strip() or False
                        if interpreter_id:
                            self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                                interpreter_id) + " limit 1")
                            interpreter_id = self._cr.fetchone()
                            interpreter_id = interpreter_id and interpreter_id[0] or False
                        # day = row[26].strip() or ''
                        name = row[27].strip() or ''
                        cust_gpuid = row[28].strip() or '' #Char
                        gender = row[29].strip() or ''
                        ssnid = row[30].strip() or '' #char
                        # appointment_type_id = row[31].strip() or ''
                        # appointment_type_id = row[31].strip() or ''
                        # fee_note_status_id = row[32].strip() or ''
                        event_type = row[33].strip() or ''
                        event_end = row[34].strip() or ''
                        ordering_partner_id = row[35].strip() or False
                        if ordering_partner_id:
                            self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                                ordering_partner_id) + " limit 1")
                            ordering_partner_id = self._cr.fetchone()
                            ordering_partner_id = ordering_partner_id and ordering_partner_id[0] or False
                        # interpreter_type = row[36].strip() or ''
                        km = row[37].strip() or ''
                        year = row[38].strip() or ''
                        location_id = row[39].strip() or False
                        if location_id:
                            self._cr.execute("select id from location where location_old_id=" + str(
                                location_id) + " limit 1")
                            location_id = self._cr.fetchone()
                            location_id = location_id and location_id[0] or False
                        certification_level = row[40].strip() or ''
                        if certification_level:
                            certification_level_id = self.env['certification.level'].search([('certification_level_old_id','=',certification_level)],limit=1).id
                        else:
                            certification_level_id=False
                        claim_no = row[41].strip() or ''
                        partner_id= row[42].strip() or False
                        if partner_id:
                            self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                                partner_id) + " limit 1")
                            partner_id = self._cr.fetchone()
                            partner_id = partner_id and partner_id[0] or False
                        event_id = row[43].strip() or '' #int
                        language = row[44].strip() or ''
                        if language:
                            language_id = self.env['language'].search([('language_old_id','=',language)],limit=1).id
                        else:
                            language_id=False
                        state = row[45].strip() or ''
                        ref = row[46].strip() or ''
                        authorize_contact_id = row[47].strip() or False
                        if authorize_contact_id:
                            self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                                authorize_contact_id) + " limit 1")
                            authorize_contact_id = self._cr.fetchone()
                            authorize_contact_id = authorize_contact_id and authorize_contact_id[0] or False
                        history3 = row[48].strip() or ''
                        if history3:
                            history_id3 = self.env['transporter.alloc.history'].search([('transporter_alloc_history_old_id', '=', history3)], limit=1).id
                        else:
                            history_id3=False
                        # active = row[49].strip() or ''
                        fee_note_test = row[50].strip() or '' #boolean
                        order_note_test = row[51].strip() or ''#boolean
                        # task_id = row[52].strip() or ''
                        translator_id = row[53].strip() or False
                        if translator_id:
                            self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                                translator_id) + " limit 1")
                            translator_id = self._cr.fetchone()
                            translator_id = translator_id and translator_id[0] or False
                        dob = row[54].strip() or ''
                        cust_csid = row[55].strip() or ''#int
                        claim_date = row[56].strip() or ''
                        quickbooks_id = row[57].strip() or '' #text
                        # entered_bystaff_id = row[58].strip() or ''
                        total_cost = row[59].strip() or ''
                        # doctor_phone = row[60].strip() or ''
                        # authorazation_date = row[61].strip() or ''
                        history2 = row[62].strip() or ''
                        if history2:
                            history_id2 =  self.env['transporter.alloc.history'].search([('transporter_alloc_history_old_id','=',history2)],limit=1).id
                        else:
                            history_id2=False
                        doctor_id = row[63].strip() or False
                        if doctor_id:
                            self._cr.execute("select id from doctor where doctor_old_id=" + str(
                                doctor_id) + " limit 1")
                            doctor_id = self._cr.fetchone()
                            doctor_id = doctor_id and doctor_id[0] or False
                        event_note = row[64].strip() or ''
                        # cust_invoice_id = row[65].strip() or '' updated after creation
                        am_pm2 = row[66].strip() or ''
                        transportation_type = row[67].strip() or ''
                        event_purpose = row[68].strip() or ''
                        # provider = row[69].strip() or ''
                        am_pm = row[70].strip() or ''
                        # case_manager = row[71].strip() or ''
                        injury_date = row[72].strip() or ''
                        zone = row[73].strip() or ''
                        if zone:
                            zone_id = self.env['meta.zone'].search([('meta_zone_old_id','=',zone)],limit=1).id
                        else:
                            zone_id=False
                        event_start_date = row[74].strip() or '' #data
                        # supp_invoice_id = row[75].strip() or ''
                        # supp_invoice_id2 = row[76].strip() or ''
                        cancel_reason = row[77].strip() or ''
                        if cancel_reason:
                            cancel_reason_id =self.env['cancel.reason'].search([('cancel_reason_old_id','=',cancel_reason)],limit=1).id
                        else:
                            cancel_reason_id=False
                        customer_timezone = row[78].strip() or ''
                        schedule_event_time = row[79].strip() or ''#datetime
                        if schedule_event_time:
                            schedule_event_time = datetime.strptime(schedule_event_time, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
                        else:
                            schedule_event_time = False
                        approving_manager = row[80].strip() or ''
                        # interpreter_assignment_history_id = row[81].strip() or ''
                        # nuid_code = row[82].strip() or ''
                        sales_representative= row[83].strip() or ''
                        # transporter_assignment_history_id = row[84].strip() or ''
                        patient_id = row[85].strip() or False
                        if patient_id:
                            self._cr.execute("select id from patient where patient_old_id=" + str(
                                patient_id) + " limit 1")
                            patient_id = self._cr.fetchone()
                            patient_id = patient_id and patient_id[0] or False
                        # gl_code = row[86].strip() or ''
                        translation_assignment_history = row[87].strip() or ''
                        if translation_assignment_history:
                            translation_assignment_history_id = self.env['assign.translator.history'].search([('assign_translator_history_old_id','=',translation_assignment_history)],limit=1).id
                        else:
                            translation_assignment_history_id=False
                        interpreter_id2 = row[88].strip() or False
                        if interpreter_id2:
                            self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                                interpreter_id2) + " limit 1")
                            interpreter_id2 = self._cr.fetchone()
                            interpreter_id2 = interpreter_id2 and interpreter_id2[0] or False
                        # approving_manager_id = row[89].strip() or ''
                        department = row[90].strip() or ''
                        transporter_id2 = row[91].strip() or False
                        if transporter_id2:
                            self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                                transporter_id2) + " limit 1")
                            transporter_id2 = self._cr.fetchone()
                            transporter_id2 = transporter_id2 and transporter_id2[0] or False
                        translator_id2 = row[92].strip() or False
                        if translator_id2:
                            self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                                translator_id2) + " limit 1")
                            translator_id2 = self._cr.fetchone()
                            translator_id2 = translator_id2 and translator_id2[0] or False
                        # scheduler_id = row[93].strip() or '' updated after creation
                        language2 = row[94].strip() or ''
                        if language2:
                            language_id2 = self.env['language'].search([('language_old_id','=',language2)],limit=1).id
                        else:
                            language_id2=False
                        # sales_representative_id = row[95].strip() or '' updated after creation
                        # project_name_id = row[96].strip() or ''
                        approving_mgr = row[97].strip() or ''
                        is_authorized = row[98].strip() or '' #booelan
                        approving_mgr_email = row[99].strip() or ''
                        verifying_mgr_email = row[100].strip() or ''
                        verified_event_start = row[101].strip() or ''
                        verified_event_end = row[102].strip() or ''
                        event_out_come = row[103].strip() or ''
                        if event_out_come:
                            event_out_come_id = self.env['event.out.come'].search([('event_outcome_old_id','=',event_out_come)],limit=1).id
                        else:
                            event_out_come_id=False
                        # event_approval = row[104].strip() or ''
                        # event_verification = row[105].strip() or ''
                        customer_timezone2 = row[106].strip() or ''
                        verifying_mgr = row[107].strip() or ''
                        verify_state = row[108].strip() or ''
                        fax = row[109].strip() or ''
                        mental_prog = row[110].strip() or ''
                        verify_time = row[111].strip() or ''
                        approve_time = row[112].strip() or '' #date
                        if approve_time:
                            approve_time = datetime.strptime(approve_time, "%Y-%m-%d").strftime(DF)
                        else:
                            approve_time = False
                        history_id4 = row[113].strip() or ''
                        phone_cust = row[114].strip() or ''
                        interpreter_note = row[115].strip() or ''
                        cust_note = row[116].strip() or ''
                        multi_type = row[117].strip() or ''
                        # source_event_id = row[118].strip() or '' #update after creation
                        event_end_min = row[119].strip() or ''
                        event_end_hr = row[120].strip() or ''
                        event_start_hr = row[121].strip() or ''
                        event_start_min = row[122].strip() or ''
                        customer_basis = row[123].strip() or '' #boolean
                        po_no = row[124].strip() or ''
                        medical_no = row[125].strip() or ''
                        order_note = row[126].strip() or '' #boolean
                        event_end_time = row[127].strip() or ''
                        event_start_time = row[128].strip() or ''
                        created_by = row[129].strip() or ''
                        event_date = row[130].strip() or '' #date
                        dr_name = row[131].strip() or ''
                        job_offered_interpreters_name = row[132].strip() or ''
                        task_state = row[133].strip() or ''
                        cost_center = row[134].strip() or ''
                        emergency_rate = row[135].strip() or '' #boolean
                        all_interpreter_email = row[136].strip() or ''
                        interpreters_phone = row[137].strip() or ''
                        customer_group = row[138].strip() or ''
                        single_interpreter = row[139].strip() or ''
                        actual_event_end = row[140].strip() or ''
                        actual_event_start = row[141].strip() or ''
                        employer = row[142].strip() or ''
                        job_schedule_id = row[143].strip() or ''
                        mobile_sync = row[144].strip() or '' #boolean
                        mobile_event = row[145].strip() or ''#boolean
                        cust_edit = row[146].strip() or ''#boolean
                        verified_dt = row[147].strip() or ''
                        verified_by = row[148].strip() or ''
                        stat = row[149].strip() or ''#boolean
                        no_editable = row[150].strip() or ''#boolean
                        org_number = row[151].strip() or ''
                        event_vals={
                            'event_old_id':int(event_old_id),
                            'comment':comment,
                            'is_follow_up':True if is_follow_up=='t' else False,
                            'special_discount':special_discount,
                            'authorize_partner_id':authorize_partner_id,
                            # 'doctor_street':doctor_street,
                            'contact_id':contact_id,
                            'month':month,
                            'date':date,
                            'authorize_date':authorize_date,
                            'transporter_id':transporter_id,
                            'user_id':user_id,
                            'company_id':company_id,
                            'event_start':event_start,

                            'ordering_contact_id':ordering_contact_id,
                            'project_id':project_id,
                            'suppress_email':True if suppress_email=='t' else False,
                            'function':function,
                            # 'cancel_reason_id':cancel_reason,
                            'history_id':history_id,
                            'interpreter_id':interpreter_id,
                            # 'day':day,
                            'name':name,
                            'cust_gpuid':cust_gpuid,
                            'gender':gender,
                            'ssnid':ssnid,
                            # 'appointment_type_id':appointment_type_id,
                            # 'fee_note_status_id':fee_note_status_id,
                            'event_type':event_type,
                            'event_end':event_end,
                            'ordering_partner_id':ordering_partner_id,
                            # 'interpreter_type':interpreter_type,
                            'km':km,
                            # 'year':year,
                            'location_id':location_id,
                            'certification_level_id':certification_level_id,
                            'claim_no':claim_no,
                            'partner_id':partner_id,
                            'event_id':event_id,
                            'language_id':language_id,
                            'state':state,
                            'ref':ref,
                            'authorize_contact_id':authorize_contact_id,
                            'history_id3':history_id3,
                            # 'active':active,
                            'fee_note_test':True if fee_note_test=='t' else False,
                            'order_note_test':True if fee_note_test=='t' else False,
                            # 'task_id':task_id,
                            'translator_id':translator_id,
                            'dob':dob,
                            'cust_csid':cust_csid,
                            'claim_date':claim_date,
                            'quickbooks_id':quickbooks_id,
                            # 'entered_bystaff_id':entered_bystaff_id,
                            'total_cost':total_cost,
                            # 'doctor_phone':doctor_phone,
                            # 'authorazation_date':authorazation_date,
                            'history_id2':history_id2,
                            'doctor_id':doctor_id,
                            'event_note':event_note,
                            # 'cust_invoice_id':cust_invoice_id,
                            'am_pm2':am_pm2,
                            'transportation_type':transportation_type,
                            'event_purpose':event_purpose,
                            # 'provider':provider,
                            'am_pm':am_pm,
                            # 'case_manager':case_manager,
                            'injury_date':injury_date,
                            'zone_id':zone_id,
                            'event_start_date':event_start_date,
                            # 'supp_invoice_id':supp_invoice_id,
                            # 'supp_invoice_id2':supp_invoice_id2,
                            'cancel_reason_id':cancel_reason_id,
                            'customer_timezone':customer_timezone,
                            'schedule_event_time':schedule_event_time,
                            # 'approving_manager':approving_manager,
                            # 'interpreter_assignment_history_id':interpreter_assignment_history_id,
                            # 'nuid_code':nuid_code,
                            'sales_representative_id':sales_representative,
                            # 'transporter_assignment_history_id':transporter_assignment_history_id,
                            'patient_id':patient_id,
                            # 'gl_code':gl_code,
                            'translation_assignment_history_id':translation_assignment_history_id,
                            'interpreter_id2':interpreter_id2,
                            # 'approving_manager_id':approving_manager_id,
                            'department':department,
                            'transporter_id2':transporter_id2,
                            'translator_id2':translator_id2,
                            # 'scheduler_id':scheduler_id,
                            'language_id2':language_id2,
                            # 'sales_representative_id':sales_representative_id,
                            # 'project_name_id':project_name_id,
                            'approving_mgr':approving_mgr,
                            'is_authorized':True if is_authorized=='t' else False,
                            'approving_mgr_email':approving_mgr_email,
                            'verifying_mgr_email':verifying_mgr_email,
                            'verified_event_start':verified_event_start,
                            'verified_event_end':verified_event_end,
                            'event_out_come_id':event_out_come_id,
                            # 'event_approval':event_approval,
                            # 'event_verification':event_verification,
                            'customer_timezone2':customer_timezone2,
                            'verifying_mgr':verifying_mgr,
                            'verify_state':verify_state,
                            'fax':fax,
                            'mental_prog':mental_prog,
                            'verify_time':verify_time,
                            'approve_time':approve_time,
                            'history_id4':history_id4,
                            'phone_cust':phone_cust,
                            'interpreter_note':interpreter_note,
                            'cust_note':cust_note,
                            'multi_type':multi_type,
                            # 'source_event_id':source_event_id,
                            'event_end_min':event_end_min,
                            'event_end_hr':event_end_hr,
                            'event_start_hr':event_start_hr,
                            'event_start_min':event_start_min,
                            'customer_basis':True if customer_basis=='t' else False,
                            'po_no':po_no,
                            'medical_no':medical_no,
                            'order_note':True if order_note=='t' else False,
                            # 'event_end_time':event_end_time if not event_end_time =='0:00 AM' else False ,
                            # 'event_start_time':event_start_time if not event_start_time =='0:00 AM' else False ,
                            # 'created_by':created_by,
                            'event_date':event_date,
                            'dr_name':dr_name,
                            'job_offered_interpreters_name':job_offered_interpreters_name,
                            'task_state':task_state,
                            'cost_center':cost_center,
                            'emergency_rate':True if emergency_rate=='t' else False,
                            # 'all_interpreter_email':all_interpreter_email,
                            # 'interpreters_phone':interpreters_phone,
                            'customer_group':customer_group,
                            # 'single_interpreter':single_interpreter,
                            'actual_event_end':actual_event_end,
                            'actual_event_start':actual_event_start,
                            'job_schedule_id':job_schedule_id,
                            'employer':employer,
                            'mobile_sync':True if mobile_sync=='t' else False,
                            'mobile_event':True if mobile_event=='t' else False,
                            'cust_edit':True if cust_edit=='t' else False,
                            'verified_dt':verified_dt,
                            'verified_by':verified_by,
                            'stat':True if stat=='t' else False,
                            'no_editable':True if no_editable=='t' else False,
                            'org_number':org_number
                        }
                        if not event_obj:
                            event_new_id=self.env['event'].create(event_vals)
                            # uncomment below line for server
                            self._cr.commit()
                        else:
                            event_obj.write(event_vals)
                            self._cr.commit()
                            _logger.error('-----Event present------')
                except Exception as e:
                    self._cr.rollback()
                    _logger.error('------------error log_id exception---------- %s', e)
                    value.append(str(e))
                    error_list.append(value)
        # with open('/home/abhishek/Desktop/output.csv', 'wb') as f:
        with open('/home/iuadmin/cust_upload_err/event_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

    # function to import mail messages
    @api.multi
    def import_mail_messages(self):
        csv_datas = self.upload_file3
        if not csv_datas:
            raise UserError(_("Choose the file before uploading!!!"))
        fileobj = TemporaryFile('w+')
        fileobj.write(base64.decodestring(csv_datas))
        fileobj.seek(0)
        str_csv_data = fileobj.read()
        lis = csv.reader(StringIO.StringIO(str_csv_data), delimiter=',')
        row_num = 0
        faulty_rows = []
        header = ''
        for row in lis:
            try:
                if row_num == 0:
                    header = row
                else:
                    if not row:
                        continue
                    _logger.error('------------rown---------- %s', row_num)
                    mail_message_old_id = row[1].strip() or ''
                    body = row[1].strip() or ''
                    model = row[2].strip() or 0.0
                    record_name = row[3].strip() or 0.0
                    date = row[4].strip() or ''
                    subject = row[4].strip() or ''
                    message_id = row[4].strip() or ''
                    # parent_id = row[4].strip() or ''
                    res_id = row[4].strip() or ''
                    subtype_id = row[4].strip() or ''
                    author_id = row[4].strip() or ''
                    type = row[4].strip() or ''
                    email_from = row[4].strip() or ''
                    event_id = row[4].strip() or ''
                    company_id = row[4].strip() or ''
                    partner_id = row[4].strip() or ''
                    attach_to = row[4].strip() or ''
                    mail_message_vals = {
                        'mail_message_old_id':mail_message_old_id,
                        'body': body,
                        'model': model,
                        'record_name': record_name,
                        'date': date,
                        'subject':subject,
                        'message_id':message_id,
                        # 'parent_id':parent_id,
                        'author_id':author_id,
                        'res_id':res_id,
                        'subtype_id':subtype_id,
                        'type':type,
                        'email_from':email_from,
                        'event_id':event_id,
                        'company_id':company_id,
                        'partner_id':partner_id,
                        'attach_to':attach_to,
                    }
                    mail_message_new_id = self.env['mail.message'].create(mail_message_vals)

            except Exception as e:
                _logger.error('------------error log_id exception---------- %s', e)
                row.append(row_num)
                faulty_rows.append(row)
            row_num += 1
        csvfile = StringIO.StringIO()
        w = csv.writer(csvfile, delimiter=',')
        w.writerow(header)
        w.writerows(faulty_rows)
        file_data = csvfile.getvalue()
        self.upload_error3 = base64.encodestring(bytes(file_data))
        self.upload_error_file_name3 = 'mail messages Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }
    # function to import event interpreter calendar
    @api.multi
    def import_event_interpreter_calendar(self):
        error_list = []
        header_list = []
        path = '/home/iuadmin/event_interpreter_calendar'
        for filename in os.listdir(path):
            # do your stuff
            file_obj = path + '/' + filename
            lis = csv.reader(open(file_obj, 'rU'), delimiter=",")
            row_num = 0
            data_dict = {}
            for row in lis:
                data_dict.update({row_num: row})
                row.append(row_num)
                row_num += 1
            for key, value in data_dict.items():
                try:
                    if key == 0:
                        header_list.append(value)
                    else:
                        _logger.error('------------rown---------- %s', key)
                        # location_id = value[8].strip() or False
                        # if location_id:
                        #     self._cr.execute("select id from location where location_old_id=" + str(
                        #         location_id) + " limit 1")
                        #     location_id = self._cr.fetchone()
                        #     location_id = location_id and location_id[0] or False
                        event_id = value[10].strip() or False
                        if event_id:
                            self._cr.execute("select id from event where event_old_id=" + str(
                                event_id) + " limit 1")
                            event_id = self._cr.fetchone()
                            event_id = event_id and event_id[0] or False
                        partner_id = value[11].strip() or False
                        if partner_id:
                            self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                                partner_id) + " limit 1")
                            partner_id = self._cr.fetchone()
                            partner_id = partner_id and partner_id[0] or False
                        company = value[16].strip() or False
                        company_id=self.env['res.company'].search([('res_company_old_id','=',company)],limit=1).id

                        evnt_inrt_calendar_vals = {
                            'event_intr_calendar_old_id':value[0].strip() ,
                            'allday': value[5].strip() or False,
                            'start_time': value[6].strip() or False,
                            'duration': value[7].strip() or 0,
                            # 'location_id':location_id, related field
                            'event_id':event_id,
                            'name':value[9].strip() or '',
                            'note':value[12].strip() or '',
                            'partner_id':partner_id,
                            'end_time':value[13].strip() or False,
                            'cancelled':value[14].strip() or False,
                            'is_event':value[15].strip() or False,
                            'company_id':company_id,
                        }
                        evnt_inrt_calendar_new_id = self.env['event.interpreter.calendar'].search([('event_intr_calendar_old_id','=',value[0].strip())],limit=1)
                        if not evnt_inrt_calendar_new_id:
                            evnt_inrt_calendar_new_id = self.env['event.interpreter.calendar'].create(evnt_inrt_calendar_vals)
                        else:
                            evnt_inrt_calendar_new_id.write(evnt_inrt_calendar_vals)
                        self._cr.commit()
                except Exception as e:
                    _logger.error('------------error log_id exception---------- %s', e)
                    value.append(str(e))
                    error_list.append(value)
        with open('/home/iuadmin/uploading_error/event_interpreter_calendar_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()


    #function to import res titles
    @api.multi
    def import_res_title(self):
        csv_datas = self.upload_file3
        if not csv_datas:
            raise UserError(_("Choose the file before uploading!!!"))
        fileobj = TemporaryFile('w+')
        fileobj.write(base64.decodestring(csv_datas))
        fileobj.seek(0)
        str_csv_data = fileobj.read()
        lis = csv.reader(StringIO.StringIO(str_csv_data), delimiter=',')
        row_num = 0
        faulty_rows = []
        header = ''
        data_dict = {}
        for row in lis:
            data_dict.update({row_num: row})
            row.append(row_num)
            row_num += 1
        for key, value in data_dict.items():
            try:
                if key == 0:
                    header = value
                else:
                    row = value
                    _logger.error('------------rown---------- %s', key)
                    res_title_old_id = row[0].strip() or ''
                    name = row[6].strip() or ''
                    res_title_obj=self.env['res.partner.title'].search([('name','=',name)])
                    if not res_title_obj:
                        shortcut = row[7].strip() or ''
                        company = row[8].strip() or ''

                        if company:
                            company_id = self.env['res.company'].search([('res_company_old_id','=',company)],limit=1).id
                        else:
                            company_id=False
                        res_title_vals = {
                            'res_title_old_id':res_title_old_id,
                            'shortcut':shortcut,
                            'name':name,
                            'company_id':company_id,
                        }
                        res_title_id = self.env['res.partner.title'].create(res_title_vals)

            except Exception as e:
                _logger.error('------------Error Exception---------- %s', key)
                faulty_rows.append(value)
        csvfile = StringIO.StringIO()
        w = csv.writer(csvfile, delimiter=',')
        w.writerow(header)
        w.writerows(faulty_rows)
        file_data = csvfile.getvalue()
        self.upload_error3 = base64.encodestring(bytes(file_data))
        self.upload_error_file_name3 = 'Res Title Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }

    # function to import interpret allocation history
    @api.multi
    def import_interpreter_alloc_history(self):
        error_list = []
        header_list = []
        # file path should be server file path in server
        # path = '/opt/home/iuadmin/alloc_history'
        path = '/home/iuadmin/alloc_history'
        for filename in os.listdir(path):
            # do your stuff
            file_obj = path + '/' + filename
            target_doc = csv.reader(open(file_obj, 'rU'), delimiter=",")
            row_num = 0
            faulty_rows = []
            header = ''
            data_dict = {}
            for row in target_doc:
                data_dict.update({row_num: row})
                row.append(row_num)
                row_num += 1
            for key, value in data_dict.items():
                try:
                    if key == 0:
                        header_list.append(value)
                    else:
                        row = value
                        _logger.error('----------Row Number---------- %s', key)
                        interpreter_alloc_his_old_id= row[0].strip() or ''
                        # city= row[1].strip() or '' #related field
                        event_id = value[7].strip() or False
                        if event_id:
                            self._cr.execute("select id from event where event_old_id=" + str(
                                event_id) + " limit 1")
                            event_id = self._cr.fetchone()
                            event_id = event_id and event_id[0] or False
                        partner_id = value[6].strip() or False
                        if partner_id:
                            self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                                partner_id) + " limit 1")
                            partner_id = self._cr.fetchone()
                            partner_id = partner_id and partner_id[0] or False
                        voicemail_msg= row[8].strip() or ''#pass
                        # rate= row[1].strip() or ''#related field
                        state= row[10].strip() or ''#pass
                        event_date= row[11].strip() or '' #pass
                        # event_id1= row[1].strip() or ''#related field
                        # patient_name= row[1].strip() or ''#na
                        allocate_date= row[14].strip() or ''
                        if allocate_date:
                            allocate_date = datetime.strptime(allocate_date, "%Y-%m-%d %H:%M:%S").strftime(DF)
                        else:
                            allocate_date = False
                        cancel_date= row[15].strip() or ''
                        if cancel_date:
                            cancel_date = datetime.strptime(cancel_date, "%Y-%m-%d %H:%M:%S").strftime(DF)
                        else:
                            cancel_date = False
                        confirm_date= row[16].strip() or ''
                        if confirm_date:
                            confirm_date = datetime.strptime(confirm_date, "%Y-%m-%d %H:%M:%S").strftime(DF)
                        else:
                            confirm_date = False
                        event_end= row[17].strip() or ''
                        if event_end:
                            event_end = datetime.strptime(event_end, "%Y-%m-%d %H:%M:%S").strftime(DF)
                        else:
                            event_end = False
                        event_start= row[18].strip() or ''
                        if event_start:
                            event_start = datetime.strptime(event_start, "%Y-%m-%d %H:%M:%S").strftime(DF)
                        else:
                            event_start = False
                        event_start_date= row[19].strip() or ''
                        if event_start_date:
                            event_start_date = datetime.strptime(event_start_date, "%Y-%m-%d").strftime(DF)
                        else:
                            event_start_date = False
                        interpreter_alloc_his_vals={
                            'interpreter_alloc_his_old_id':interpreter_alloc_his_old_id,
                            # 'city':city,
                            'name':partner_id,
                            'event_id':event_id,
                            'voicemail_msg':voicemail_msg,
                            # 'rate':rate,
                            'state':state,
                            'event_date':event_date,
                            # 'event_id1':event_id1,
                            # 'patient_name':patient_name,
                            'allocate_date':allocate_date,
                            'cancel_date':cancel_date,
                            'confirm_date':confirm_date,
                            'event_end':event_end,
                            'event_start':event_start,
                            'event_start_date':event_start_date,
                        }
                        interpreter_alloc_his_id=self.env['interpreter.alloc.history'].search([('interpreter_alloc_his_old_id','=',interpreter_alloc_his_old_id)],limit=1)
                        if not interpreter_alloc_his_id:
                            interpreter_alloc_his_id= self.env['interpreter.alloc.history'].create(interpreter_alloc_his_vals)
                            self._cr.commit()
                        else:
                            interpreter_alloc_his_id.write(interpreter_alloc_his_vals)
                            self._cr.commit()
                except Exception as e:
                    self._cr.rollback()
                    _logger.error('------------error log_id exception---------- %s', e)
                    value.append(str(e))
                    error_list.append(value)
        # with open('/opt/home/iuadmin/alloc_history/output.csv', 'wb') as f:
        with open('/home/iuadmin/alloc_history/alloc_his_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

    # function to import translator language
    @api.multi
    def import_translator_language(self):
        csv_datas = self.upload_file3
        if not csv_datas:
            raise UserError(_("Choose the file before uploading!!!"))
        fileobj = TemporaryFile('w+')
        fileobj.write(base64.decodestring(csv_datas))
        fileobj.seek(0)
        str_csv_data = fileobj.read()
        lis = csv.reader(StringIO.StringIO(str_csv_data), delimiter=',')
        row_num = 0
        faulty_rows = []
        header = ''
        data_dict = {}
        for row in lis:
            data_dict.update({row_num: row})
            row.append(row_num)
            row_num += 1
        for key, value in data_dict.items():
            try:
                if key == 0:
                    header = value
                else:
                    row = value
                    _logger.error('------------rown---------- %s', key)
                    translator_language_old_id = row[0].strip()
                    name = row[15].strip() or ''
                    if name:
                        name_id = self.env['language'].search([('language_old_id','=',name)],limit=1).id
                    else:
                        name_id = False
                    to_lang_id = row[5].strip() or ''
                    if to_lang_id:
                        to_language_id = self.env['language'].search([('language_old_id','=',to_lang_id)],limit=1).id
                    else:
                        to_language_id = False
                    view_order = row[11].strip() or ''
                    certification = row[9].strip() or ''
                    if certification:
                        certification_id = self.env['translator.certification'].search([('translator_certification_old_id','=',certification)],limit=1).id
                    else:
                        certification_id = False
                    do_poofing = row[8].strip() or ''
                    amount_poofing_per_word = row[10].strip() or ''
                    max_amount_per_word = row[13].strip() or ''
                    min_amount_per_word = row[6].strip() or ''
                    translation_language_id = row[14].strip() or ''
                    translator = row[7].strip() or ''
                    if translator:
                        translator_id = self.env['res.partner'].search([('customer_record_old_id','=',translator)],limit=1).id
                    else:
                        translator_id = False
                    # company_id = row[6].strip() or ''

                    translator_language_vals = { 'name':name_id,
                                                 'translator_language_old_id':int(translator_language_old_id),
                                                 'to_lang_id': to_language_id,
                                                 'view_order': int(view_order) if view_order else 0,
                                                 'certification_id': certification_id,
                                                 'do_poofing': True if do_poofing=='t' else False,
                                                 'amount_poofing_per_word':float(amount_poofing_per_word) if amount_poofing_per_word else 0.0,
                                                 'max_amount_per_word': float(max_amount_per_word) if max_amount_per_word else 0.0,
                                                 'min_amount_per_word': float(min_amount_per_word) if min_amount_per_word else 0.0,
                                                 'translation_language_id': int(translation_language_id) if translation_language_id else 0,
                                                 'translator_id': translator_id,
                                                 # 'company_id': company_id,
                                                 }
                    translator_language_new_id = self.env['translator.language'].create(translator_language_vals)
                    self._cr.commit()

            except Exception as e:
                _logger.error('------------Error Exception---------- %s', e)
                print(e)
                faulty_rows.append(value)
        csvfile = StringIO.StringIO()
        w = csv.writer(csvfile, delimiter=',')
        w.writerow(header)
        w.writerows(faulty_rows)
        file_data = csvfile.getvalue()
        self.upload_error3 = base64.encodestring(bytes(file_data))
        self.upload_error_file_name3 = 'Translator Language Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }

    #function to import translator certification
    @api.multi
    def import_translator_certification(self):
        csv_datas = self.upload_file3
        if not csv_datas:
            raise UserError(_("Choose the file before uploading!!!"))
        fileobj = TemporaryFile('w+')
        fileobj.write(base64.decodestring(csv_datas))
        fileobj.seek(0)
        str_csv_data = fileobj.read()
        lis = csv.reader(StringIO.StringIO(str_csv_data), delimiter=',')
        row_num = 0
        faulty_rows = []
        header = ''
        data_dict = {}
        for row in lis:
            data_dict.update({row_num: row})
            row.append(row_num)
            row_num += 1
        for key, value in data_dict.items():
            try:
                if key == 0:
                    header = value
                else:
                    row = value
                    _logger.error('------------rown---------- %s', key)
                    translator_certification_old_id = row[0].strip()
                    name = row[6].strip() or ''
                    translator_certification_id = row[5].strip() or ''
                    company_id = row[7].strip() or ''
                    if company_id:
                        company = self.env['res.company'].search([('res_company_old_id', '=', company_id)], limit=1).id
                    else:
                        company = False

                    translator_certification_vals = {
                        'translator_certification_old_id':int(translator_certification_old_id),
                        'name':name,
                        'translator_certification_id': int(translator_certification_id),
                        'company_id': company,
                    }
                    translator_certification_new_id = self.env['translator.certification'].create(translator_certification_vals)

            except Exception as e:
                _logger.error('------------Error Exception---------- %s', key)
                faulty_rows.append(value)
        csvfile = StringIO.StringIO()
        w = csv.writer(csvfile, delimiter=',')
        w.writerow(header)
        w.writerows(faulty_rows)
        file_data = csvfile.getvalue()
        self.upload_error3 = base64.encodestring(bytes(file_data))
        self.upload_error_file_name3 = 'Translator Certification Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }

    # function to import software
    @api.multi
    def import_software(self):
        csv_datas = self.upload_file3
        if not csv_datas:
            raise UserError(_("Choose the file before uploading!!!"))
        fileobj = TemporaryFile('w+')
        fileobj.write(base64.decodestring(csv_datas))
        fileobj.seek(0)
        str_csv_data = fileobj.read()
        lis = csv.reader(StringIO.StringIO(str_csv_data), delimiter=',')
        row_num = 0
        faulty_rows = []
        header = ''
        data_dict = {}
        for row in lis:
            data_dict.update({row_num: row})
            row.append(row_num)
            row_num += 1
        for key, value in data_dict.items():
            try:
                if key == 0:
                    header = value
                else:
                    row = value
                    _logger.error('------------rown---------- %s', key)
                    software_old_id = row[0].strip()
                    name = row[6].strip() or ''
                    software_id = row[5].strip() or ''
                    company = row[7].strip() or ''
                    if company:
                        company_id = self.env['res.company'].search([('res_company_old_id', '=', company)],limit=1).id
                    else:
                        company_id = False

                    software_vals = {
                        'software_old_id': int(software_old_id),
                        'name': name,
                        'software_id': int(software_id),
                        'company_id': company_id,
                    }
                    software_new_id = self.env['software'].create(software_vals)

            except Exception as e:
                _logger.error('------------Error Exception---------- %s', key)
                faulty_rows.append(value)
        csvfile = StringIO.StringIO()
        w = csv.writer(csvfile, delimiter=',')
        w.writerow(header)
        w.writerows(faulty_rows)
        file_data = csvfile.getvalue()
        self.upload_error3 = base64.encodestring(bytes(file_data))
        self.upload_error_file_name3 = 'Software  Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }
    #function to import interpreter language
    @api.multi
    def import_interpreter_language(self):
        csv_datas = self.upload_file3
        if not csv_datas:
            raise UserError(_("Choose the file before uploading!!!"))
        fileobj = TemporaryFile('w+')
        fileobj.write(base64.decodestring(csv_datas))
        fileobj.seek(0)
        str_csv_data = fileobj.read()
        lis = csv.reader(StringIO.StringIO(str_csv_data), delimiter=',')
        row_num = 0
        faulty_rows = []
        header = ''
        data_dict = {}
        for row in lis:
            data_dict.update({row_num: row})
            row.append(row_num)
            row_num += 1
        for key, value in data_dict.items():
            try:
                if key == 0:
                    header = value
                else:
                    row = value
                    _logger.error('------------rown---------- %s', key)
                    interpret_language_old_id = row[0].strip() or ''
                    interpreter_language_id = self.env['interpreter.language'].search([('interpret_language_old_id', '=', interpret_language_old_id)], limit=1)
                    name = row[14].strip() or ''
                    if name:
                        language_id=self.env['language'].search([('language_old_id', '=', name)], limit=1).id
                    else:
                         language_id=False
                    sort_order = row[11].strip() or ''
                    is_simultaneous = row[12].strip() or ''
                    specialization = row[7].strip() or ''
                    certification_code = row[8].strip() or ''
                    certification_level = row[6].strip() or ''
                    if certification_level:
                        certification_level_id = self.env['certification.level'].search(
                            [('certification_level_old_id', '=', certification_level)], limit=1).id
                    else:
                        certification_level_id = False
                    interpreter_id = row[13].strip() or ''
                    if interpreter_id:
                        self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                            interpreter_id) + " limit 1")
                        interpreter_id = self._cr.fetchone()
                        interpreter_id = interpreter_id and interpreter_id[0] or False
                    interpreter_language_vals = {
                        'interpret_language_old_id': interpret_language_old_id,
                        'name': language_id,
                        'sort_order': sort_order,
                        'is_simultaneous': True if is_simultaneous == 't' else False,
                        'specialization': specialization,
                        'certification_code': certification_code,
                        'certification_level_id': certification_level_id,
                        'interpreter_id': interpreter_id,
                    }
                    if interpreter_language_id:
                        interpreter_language_id.write(interpreter_language_vals)
                    else:
                        interpreter_language_id = self.env['interpreter.language'].create(interpreter_language_vals)

            except Exception as e:
                _logger.error('------------Error Exception---------- %s', key)
                faulty_rows.append(value)
        csvfile = StringIO.StringIO()
        w = csv.writer(csvfile, delimiter=',')
        w.writerow(header)
        w.writerows(faulty_rows)
        file_data = csvfile.getvalue()
        self.upload_error3 = base64.encodestring(bytes(file_data))
        self.upload_error_file_name3 = 'Interpreter Language Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }

# fucntion to import cancel event

    @api.multi
    def import_cancelled_event(self):
        csv_datas = self.upload_file3
        if not csv_datas:
            raise UserError(_("Choose the file before uploading!!!"))
        fileobj = TemporaryFile('w+')
        fileobj.write(base64.decodestring(csv_datas))
        fileobj.seek(0)
        str_csv_data = fileobj.read()
        lis = csv.reader(StringIO.StringIO(str_csv_data), delimiter=',')
        row_num = 0
        faulty_rows = []
        header = ''
        data_dict = {}
        for row in lis:
            data_dict.update({row_num: row})
            row.append(row_num)
            row_num += 1
        for key, value in data_dict.items():
            try:
                if key == 0:
                    header = value
                else:
                    row = value
                    _logger.error('------------rown---------- %s', key)
                    cancel_event_old_id = row[0].strip()
                    name = row[5].strip() or ''
                    cancelled_event_id= row[6].strip() or ''
                    company = row[7].strip() or ''
                    if company:
                        company_id = self.env['res.company'].search([('res_company_old_id', '=', company)],limit=1).id
                    else:
                        company_id = False

                    cancelled_event_vals = {
                        'cancel_event_old_id': int(cancel_event_old_id),
                        'name': name,
                        'cancelled_event_id': int(cancelled_event_id),
                        'company_id': company_id,
                    }
                    cancelled_event_id = self.env['cancelled.event'].create(cancelled_event_vals)

            except Exception as e:
                _logger.error('------------Error Exception---------- %s', key)
                faulty_rows.append(value)
        csvfile = StringIO.StringIO()
        w = csv.writer(csvfile, delimiter=',')
        w.writerow(header)
        w.writerows(faulty_rows)
        file_data = csvfile.getvalue()
        self.upload_error3 = base64.encodestring(bytes(file_data))
        self.upload_error_file_name3 = 'Cancelled Event  Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }

    # function to import Affiliation
    @api.multi
    def import_affiliation(self):
        csv_datas = self.upload_file3

        if not csv_datas:
            raise UserError(_("Choose the file before uploading!!!"))
        fileobj = TemporaryFile('w+')
        fileobj.write(base64.decodestring(csv_datas))
        fileobj.seek(0)
        str_csv_data = fileobj.read()
        lis = csv.reader(StringIO.StringIO(str_csv_data), delimiter=',')
        row_num = 0
        faulty_rows = []
        header = ''
        data_dict = {}
        for row in lis:
            data_dict.update({row_num: row})
            row.append(row_num)
            row_num += 1
        for key, value in data_dict.items():
            try:
                if key == 0:
                    header = value
                else:
                    row = value
                    _logger.error('------------rown---------- %s', key)
                    affiliation_old_id = row[0].strip()
                    name = row[6].strip() or ''
                    affiliation_id = row[5].strip() or ''
                    company = row[7].strip() or ''
                    if company:
                        company_id = self.env['res.company'].search([('res_company_old_id', '=', company)], limit=1).id
                    else:
                        company_id = False

                    affiliation_vals = {
                        'affiliation_old_id':affiliation_old_id,
                        'name': name,
                        'affiliation_id': affiliation_id,
                        'company_id': company_id,
                    }
                    affiliation_new_id = self.env['affiliation'].create(affiliation_vals)
                    self._cr.commit()

            except Exception as e:
                _logger.error('------------Error Exception---------- %s', key)
            faulty_rows.append(value)
            csvfile = StringIO.StringIO()
            w = csv.writer(csvfile, delimiter=',')
            w.writerow(header)
            w.writerows(faulty_rows)
            file_data = csvfile.getvalue()
            self.upload_error3 = base64.encodestring(bytes(file_data))
            self.upload_error_file_name3 = 'Affiliation Uploading Error.csv'
            csvfile.close()
            return {
                "type": "ir.actions.do_nothing",
            }
# function to import phone type
    @api.multi
    def import_phone_type(self):
        csv_datas = self.upload_file3

        if not csv_datas:
            raise UserError(_("Choose the file before uploading!!!"))
        fileobj = TemporaryFile('w+')
        fileobj.write(base64.decodestring(csv_datas))
        fileobj.seek(0)
        str_csv_data = fileobj.read()
        lis = csv.reader(StringIO.StringIO(str_csv_data), delimiter=',')
        row_num = 0
        faulty_rows = []
        header = ''
        data_dict = {}
        for row in lis:
            data_dict.update({row_num: row})
            row.append(row_num)
            row_num += 1
        for key, value in data_dict.items():
            try:
                if key == 0:
                    header = value
                else:
                    row = value
                    _logger.error('------------rown---------- %s', key)
                    phone_type_old_id = row[0].strip()
                    name = row[6].strip() or ''
                    phone_type_id = row[6].strip() or ''
                    company = row[6].strip() or ''
                    if company:
                        company_id = self.env['res.company'].search([('res_company_old_id', '=', company)],limit=1).id
                    else:
                        company_id = False

                    phone_type_vals = {
                        'phone_type_old_id': int(phone_type_old_id),
                        'name': name,
                        'phone_type_id': int(phone_type_id),
                        'company_id':company_id
                    }
                    phone_type_new_id = self.env['phone.type'].create(phone_type_vals)

            except Exception as e:
                _logger.error('------------Error Exception---------- %s', key)
            faulty_rows.append(value)
            csvfile = StringIO.StringIO()
            w = csv.writer(csvfile, delimiter=',')
            w.writerow(header)
            w.writerows(faulty_rows)
            file_data = csvfile.getvalue()
            self.upload_error3 = base64.encodestring(bytes(file_data))
            self.upload_error_file_name3 = 'Phone Type Uploading Error.csv'
            csvfile.close()
            return {
                "type": "ir.actions.do_nothing",
            }
#function to import zip time zone
    @api.multi
    def import_zip_time_zone(self):
        csv_datas = self.upload_file3

        if not csv_datas:
            raise UserError(_("Choose the file before uploading!!!"))
        fileobj = TemporaryFile('w+')
        fileobj.write(base64.decodestring(csv_datas))
        fileobj.seek(0)
        str_csv_data = fileobj.read()
        lis = csv.reader(StringIO.StringIO(str_csv_data), delimiter=',')
        row_num = 0
        faulty_rows = []
        header = ''
        data_dict = {}
        for row in lis:
            data_dict.update({row_num: row})
            row.append(row_num)
            row_num += 1
        for key, value in data_dict.items():
            try:
                if key == 0:
                    header = value
                else:
                    row = value
                    _logger.error('------------rown---------- %s', key)
                    zip_time_zone_old_id = row[0].strip()
                    name = row[6].strip() or ''
                    city = row[5].strip() or ''
                    state_code = row[9].strip() or ''
                    state = row[8].strip() or ''
                    if state:
                        state_id = self.env['res.country.state'].search([('state7_id','=',state)],limit=1).id
                    else:
                        state_id = False
                    time_zone = row[10].strip() or ''
                    time_zone_code = row[12].strip() or ''
                    latitude = row[7].strip() or ''
                    longitude = row[11].strip() or ''

                    zip_time_zone_vals = {
                                            'zip_time_zone_old_id': int(zip_time_zone_old_id),
                                            'name': name,
                                            'city': city,
                                            'state_code': state_code,
                                            'state_id': state_id,
                                            'time_zone': time_zone,
                                            'time_zone_code': time_zone_code,
                                            'latitude': float(latitude) if latitude else 0.0,
                                            'longitude': float(longitude) if longitude else 0.0,
                                        }
                    zip_time_zone_new_id = self.env['zip.time.zone'].create(zip_time_zone_vals)
                    self._cr.commit()

            except Exception as e:
                _logger.error('------------Error Exception---------- %s', key)
                faulty_rows.append(value)
        csvfile = StringIO.StringIO()
        w = csv.writer(csvfile, delimiter=',')
        w.writerow(header)
        w.writerows(faulty_rows)
        file_data = csvfile.getvalue()
        self.upload_error3 = base64.encodestring(bytes(file_data))
        self.upload_error_file_name3 = 'ZipTime Zone Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
                    }

#function to import resource
    @api.multi
    def import_resource(self):
        csv_datas = self.upload_file3
        if not csv_datas:
            raise UserError(_("Choose the file before uploading!!!"))
        fileobj = TemporaryFile('w+')
        fileobj.write(base64.decodestring(csv_datas))
        fileobj.seek(0)
        str_csv_data = fileobj.read()
        lis = csv.reader(StringIO.StringIO(str_csv_data), delimiter=',')
        row_num = 0
        faulty_rows = []
        header = ''
        data_dict = {}
        for row in lis:
            data_dict.update({row_num: row})
            row.append(row_num)
            row_num += 1
        for key, value in data_dict.items():
            try:
                if key == 0:
                    header = value
                else:
                    row = value
                    _logger.error('------------rown---------- %s', key)
                    resource_old_id = row[0].strip()
                    name = row[8].strip() or ''
                    code = row[6].strip() or ''
                    active = row[10].strip() or ''
                    resource_type = row[12].strip() or ''
                    company = row[9].strip() or ''
                    if company:
                        company_id = self.env['res.company'].search([('res_company_old_id','=',company)],limit=1).id
                    else:
                        company_id = False
                    user = row[7].strip() or False
                    if user:
                        user_id = self.env['res.users'].search([('user_old_id','=',user)])
                        if not user_id and user:
                            user_id=1
                        else:
                            user_id=False
                    else:
                        user_id = False
                    time_efficiency = row[5].strip() or ''
                    resource_vals = {
                                            'resource_old_id': int(resource_old_id),
                                            'name': name,
                                            'code': code,
                                            'resource_type': resource_type,
                                            'active': True if active=='t' else False,
                                            'user_id': user_id,
                                            'company_id': company_id,
                                            'time_efficiency': float(time_efficiency) if time_efficiency else 0.0,
                                        }
                    resource_new_id = self.env['resource.resource'].create(resource_vals)
                    self._cr.commit()

            except Exception as e:
                _logger.error('------------Error Exception---------- %s', key)
            faulty_rows.append(value)
            csvfile = StringIO.StringIO()
            w = csv.writer(csvfile, delimiter=',')
            w.writerow(header)
            w.writerows(faulty_rows)
            file_data = csvfile.getvalue()
            self.upload_error3 = base64.encodestring(bytes(file_data))
            self.upload_error_file_name3 = 'Resource Uploading Error.csv'
            csvfile.close()
            return {
                "type": "ir.actions.do_nothing",
                        }

# function to import twilio sms send
    @api.multi
    def import_twilio_sms_send(self):
        error_list = []
        header_list = []
        # file path should be server file path in server
        path = '/home/iuadmin/tw_sms_send'
        for filename in os.listdir(path):
            # do your stuff
            file_obj = path + '/' + filename
            target_doc = csv.reader(open(file_obj, 'rU'), delimiter=",")
            row_num = 0
            data_dict = {}
            for row in target_doc:
                data_dict.update({row_num: row})
                row.append(row_num)
                row_num += 1
            for key, value in data_dict.items():
                try:
                    if key == 0:
                        header_list.append(value)
                    else:
                        row = value
                        _logger.error('----------Row Number---------- %s', key)

                        twilio_sms_send_old_id= row[0].strip(),
                        sms_to= row[10].strip(),
                        sms_from = row[11].strip(),
                        sms_body=row[13].strip(),
                        message_sid= row[9].strip(),
                        direction=row[6].strip(),
                        price= row[8].strip(),
                        price_unit= row[16].strip(),
                        error_msg=row[12].strip(),
                        error_code= row[15].strip(),
                        account_sid= row[14].strip(),
                        status=  row[5].strip(),
                        account = row[7]
                        # account_id = self.env['twilio.accounts'].search([('twilio_acc_old_id','=',account)],limit=1).id

                        vals=(twilio_sms_send_old_id,status, direction, price, message_sid, sms_to, error_msg, sms_body, account_sid, error_code, price_unit)

                        self._cr.execute(""" INSERT INTO twilio_sms_send (twilio_sms_send_old_id,status,direction,price,message_sid,
                                            sms_to,error_msg,sms_body,account_sid,error_code,price_unit)
                                             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",vals)
                        self._cr.commit()

                except Exception as e:
                    _logger.error('------------error log_id exception---------- %s', e)
                    error_list.append(value)
        with open('/home/iuadmin/cust_upload_err/tw_send_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()


#function to import twilio sms receive
    @api.multi
    def import_twilio_sms_received(self):
        error_list = []
        header_list = []
        # file path should be server file path in server
        path = '/home/iuadmin/tw_sms_rec'
        for filename in os.listdir(path):
            # do your stuff
            file_obj = path + '/' + filename
            target_doc = csv.reader(open(file_obj, 'rU'), delimiter=",")
            row_num = 0
            data_dict = {}
            for row in target_doc:
                data_dict.update({row_num: row})
                row.append(row_num)
                row_num += 1
            for key, value in data_dict.items():
                try:
                    if key == 0:
                        header_list.append(value)
                    else:
                        row = value
                        _logger.error('----------Row Number---------- %s', key)

                        twilio_sms_received_old_id = row[0].strip(),
                        sms_from = row[11].strip(),
                        sms_to = row[16].strip(),
                        sms_body = row[15].strip(),
                        account_sid = row[17].strip(),
                        service_sid = row[10].strip(),
                        message_sid = row[9].strip(),
                        status = row[5].strip(),
                        from_zip = row[7].strip(),
                        from_city = row[20].strip(),
                        from_state = row[13].strip(),
                        from_country = row[8].strip(),
                        to_zip = row[12].strip(),
                        to_city = row[18].strip(),
                        to_state = row[14].strip(),
                        to_country = row[19].strip(),
                        api_version = row[21].strip(),
                        account = row[6].strip(),
                        # account_id = self.env['twilio.accounts'].search([('twilio_acc_old_id', '=', account)],limit=1).id

                        vals = (twilio_sms_received_old_id,sms_from,sms_to,sms_body,account_sid,service_sid,message_sid,status,from_zip,from_city,from_state,from_country,
                                to_zip,to_city,to_state,to_country,api_version)

                        self._cr.execute(""" INSERT INTO twilio_sms_received (twilio_sms_received_old_id,sms_from,sms_to,sms_body,account_sid,service_sid,
                                                                                message_sid,status,from_zip,from_city,from_state,from_country,
                                                                                to_zip,to_city,to_state,to_country,api_version)
                                                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", vals)
                        self._cr.commit()

                except Exception as e:
                    _logger.error('------------error log_id exception---------- %s', e)
                    error_list.append(value)
        with open('/home/iuadmin/cust_upload_err/tw_sms_rec.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()


    # function to import mail messages
    @api.multi
    def import_mail_messages(self):
        error_list = []
        header_list = []
        # file path should be server file path in server

        path = '/home/iuadmin/'
        for filename in os.listdir(path):
            # do your stuff
            file_obj = path + '/' + filename
            target_doc = csv.reader(open(file_obj, 'rU'), delimiter=",")
            row_num = 0
            faulty_rows = []
            header = ''
            data_dict = {}
            for row in target_doc:
                data_dict.update({row_num: row})
                row.append(row_num)
                row_num += 1
            for key, value in data_dict.items():
                try:
                    if key == 0:
                        header_list.append(value)
                    else:
                        row = value
                        _logger.error('----------Row Number---------- %s', key)

                        mail_message_old_id = row[0].strip()
                        # mail_server_id = row[11].strip(),
                        subject = row[9].strip()
                        parent_id = row[11].strip()
                        subtype_id = row[13].strip()
                        res_id = row[12].strip()
                        message_id = row[10].strip()
                        body = row[5].strip()
                        record_name = row[7].strip()
                        # no_auto_thread = row[20].strip(),
                        date = row[8].strip()
                        # reply_to = row[8].strip(),
                        author_id = row[14].strip()
                        model = row[6].strip()
                        # message_type = row[14].strip(),
                        email_from = row[16].strip()
                        # website_published = row[21].strip(),
                        partner_id = row[19].strip()
                        event_id = row[17].strip()
                        attach_to = row[20].strip()
                        company= row[18].strip()
                        company_id = self.env['res.company'].search([('res_company_old_id', '=', company)],limit=1).id

                        vals = ( mail_message_old_id,subject,parent_id,subtype_id,res_id,message_id,body,record_name,date,
                                 author_id,model,email_from,partner_id,event_id,company_id,attach_to)

                        self._cr.execute(""" INSERT INTO mail_messages (mail_message_old_id,subject,parent_id,subtype_id,res_id,message_id,body,record_name,date,
                                 author_id,model,email_from,partner_id,event_id,company_id,attach_to ,)
                                                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                                         vals)
                        self._cr.commit()

                except Exception as e:
                    _logger.error('------------error log_id exception---------- %s', e)
                    error_list.append(value)
        with open('/home/girish/Desktop/TWI/output3.csv', 'wb') as f:
            # with open('/home/iuadmin/cust_upload_err/interpret_alloc_his_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

#function to import Select interpreter line
    @api.multi
    def import_select_interpreter_line(self):
        error_list = []
        header_list = []
        # file path should be server file path in server
        # path = '/home/abhishek/Desktop/inter_line'
        path = '/home/iuadmin/select_interpreter_line'
        for filename in os.listdir(path):
            # do your stuff
            file_obj = path + '/' + filename
            target_doc = csv.reader(open(file_obj, 'rU'), delimiter=",")
            row_num = 0
            faulty_rows = []
            header = ''
            data_dict = {}
            for row in target_doc:
                data_dict.update({row_num: row})
                row.append(row_num)
                row_num += 1
            for key, value in data_dict.items():
                try:
                    if key == 0:
                        header_list.append(value)
                    else:
                        row = value
                        _logger.error('----------Row Number---------- %s', key)

                        interpreter_line_old_id = row[0].strip() or 0
                        interpreter_line_obj=self.env['select.interpreter.line'].search([('interpreter_line_old_id', '=', interpreter_line_old_id)],limit=1)
                        rate = row[19].strip() or ''
                        interpreter_id =row[8].strip() or ''
                        if interpreter_id:
                            self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                                interpreter_id) + " limit 1")
                            interpreter_id = self._cr.fetchone()
                            interpreter_id = interpreter_id and interpreter_id[0] or False
                        preferred = row[21].strip() or ''
                        event_id = row[13].strip() or ''
                        if event_id:
                            self._cr.execute("select id from event where event_old_id=" + str(
                                event_id) + " limit 1")
                            event_id = self._cr.fetchone()
                            event_id = event_id and event_id[0] or False
                        visited = row[18].strip() or ''
                        visited_date =row[17].strip() or ''
                        voicemail_msg = row[15].strip() or ''
                        duration = row[7].strip() or ''
                        distance = row[20].strip() or ''
                        state = row[16].strip() or ''
                        select_interpreter = row[23].strip() or ''
                        # parent_state = row[6].strip(),
                        # company = row[14].strip(),
                        # company_id = self.env['res.company'].search([('res_company_old_id', '=', company)],limit=1).id

                        interpreter_line_vals = {'interpreter_line_old_id':int(interpreter_line_old_id),
                                                'rate':float(rate) if rate else 0.0,
                                                'interpreter_id':interpreter_id,
                                                'preferred':True if preferred=='t' else False,
                                                'event_id':event_id,
                                                'visited':True if visited=='t' else False,
                                                'visited_date':visited_date,
                                                'voicemail_msg':voicemail_msg,
                                                'duration':duration,
                                                'distance':float(distance) if distance else 0.0,
                                                'state':state,
                                                'select_interpreter':True if select_interpreter=='t' else False,
                                                 # 'parent_state':parent_state,
                                                 # 'company_id':company_id
                                                }
                        if not interpreter_line_obj:
                            select_interpreter_line_new_id=self.env['select.interpreter.line'].create(interpreter_line_vals)
                            self._cr.commit()
                        else:
                            interpreter_line_obj.write(interpreter_line_vals)
                            self._cr.commit()
                            _logger.error('-------record found !!!!-------')
                except Exception as e:
                    _logger.error('------------error log_id exception---------- %s', e)
                    value.append(str(e))
                    error_list.append(value)
        with open('/home/iuadmin/select_interpreter_line_error.csv', 'wb') as f:
            # with open('/home/iuadmin/cust_upload_err/interpret_alloc_his_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

    # function to import Select translator line
    @api.multi
    def import_select_translator_line(self):
        csv_datas = self.upload_file3
        if not csv_datas:
            raise UserError(_("Choose the file before uploading!!!"))
        fileobj = TemporaryFile('w+')
        fileobj.write(base64.decodestring(csv_datas))
        fileobj.seek(0)
        str_csv_data = fileobj.read()
        target_doc = csv.reader(StringIO.StringIO(str_csv_data), delimiter=',')
        row_num = 0
        error_list = []
        header_list = []
        data_dict = {}
        for row in target_doc:
            data_dict.update({row_num: row})
            row.append(row_num)
            row_num += 1
        for key, value in data_dict.items():
            try:
                if key == 0:
                    header_list.append(value)
                else:
                    row = value
                    _logger.error('----------Row Number---------- %s', key)

                    translator_line_old_id = row[0].strip()
                    select = row[9].strip() or ''
                    event = row[15].strip() or ''
                    if event:
                        event_id = self.env['event'].search([('event_old_id','=',event)],limit=1).id
                    else:
                        event_id = False
                    visited = row[20].strip()  or ''
                    visited_date = row[19].strip() or ''
                    voicemail_msg = row[17].strip()  or ''
                    duration = row[8].strip() or ''
                    distance = row[10].strip() or 0.0
                    state = row[18].strip() or ''
                    translator = row[14].strip() or ''
                    if translator:
                        translator_id = self.env['res.partner'].search([('customer_record_old_id','=',translator)],limit=1).id
                    else:
                        translator_id = False
                    interpreter_line_vals = {'translator_line_old_id': translator_line_old_id,
                                             'select': True if select=='t' else False,
                                             'event_id': event_id,
                                             'visited': True if visited=='t' else False,
                                             'visited_date': visited_date,
                                             'voicemail_msg': voicemail_msg,
                                             'duration': duration,
                                             'distance': float(distance) if distance else 0.0,
                                             'state': state,
                                             'translator_id': translator_id,
                                             # 'parent_state':parent_state,
                                             # 'company_id':company_id
                                             }

                    select_translator_line_new_id = self.env['select.translator.line'].create(interpreter_line_vals)
                    self._cr.commit()

            except Exception as e:
                _logger.error('------------error log_id exception---------- %s', e)
                error_list.append(value)
        csvfile = StringIO.StringIO()
        w = csv.writer(csvfile, delimiter=',')
        w.writerow(header_list)
        w.writerows(error_list)
        file_data = csvfile.getvalue()
        self.upload_error3 = base64.encodestring(bytes(file_data))
        self.upload_error_file_name3 = 'Select Translator Line Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }

# function to import Project Task
    #uncomment stage_id,user_id,event_id,user_id_int,view_interpreter,cust_invoive_id,timesheet_attachment
    @api.multi
    def import_project_task(self):
        error_list = []
        header_list = []
        total_row=0
        # file path should be server file path in server
        path = '/home/iuadmin/task'
        # path = '/home/iuadmin/select_interpreter_line'
        for filename in os.listdir(path):
            # do your stuff
            file_obj = path + '/' + filename
            target_doc = csv.reader(open(file_obj, 'rU'), delimiter=",")
            row_num = 0
            faulty_rows = []
            header = ''
            data_dict = {}
            for row in target_doc:
                data_dict.update({row_num: row})
                row.append(row_num)
                row_num += 1
            for key, value in data_dict.items():
                try:
                    if key == 0:
                        header_list.append(value)
                    else:
                        row = value
                        _logger.error('----------Row Number---------- %s', key)
                        project_task_old_id = row[0].strip()
                        project_task_obj=self.env['project.task'].search([('project_task_old_id','=',project_task_old_id)],limit=1)

                        # sequence= row[5].strip()
                        color= row[6].strip()
                        date_end = row[7].strip()
                        planned_hours = row[9].strip()
                        partner_id = value[10].strip() or False
                        if partner_id:
                            self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                                partner_id) + " limit 1")
                            partner_id = self._cr.fetchone()
                            partner_id = partner_id and partner_id[0] or False
                        user_id = row[11].strip()
                        if user_id:
                            self._cr.execute("select id from res_users where user_old_id=" + str(
                                user_id) + " limit 1")
                            user_id = self._cr.fetchone()
                            user_id = user_id and user_id[0] or False
                        date_start = row[12].strip()
                        company = row[13].strip()
                        company_id = self.env['res.company'].search([('res_company_old_id','=',company)]).id
                        priority = row[14].strip()
                        state = row[15].strip()
                        description = row[18].strip()
                        kanban_state = row[19].strip()
                        active = row[20].strip()
                        stage = row[22].strip()
                        if stage:
                            stage_id = self.env['project.task.type'].search([('project_task_type_old_id','=',stage)],limit=1).id
                        else:
                            stage_id = False
                        name = row[23].strip()
                        date_deadline = row[24].strip()
                        notes = row[25].strip()
                        event_type = row[28].strip()
                        task_id = row[29].strip()
                        event_id = row[30].strip()
                        if event_id:
                            self._cr.execute("select id from event where event_old_id=" + str(
                                event_id) + " limit 1")
                            event_id = self._cr.fetchone()
                            event_id = event_id and event_id[0] or False
                        transporter_id = row[31].strip()
                        billing_state = row[34].strip()
                        cust_invoice = row[35].strip()
                        # if cust_invoice:
                        #     cust_invoice_id = self.env['account.invoice'].search([('invoice_old_id','=',cust_invoice)],limit=1).id
                        # else:
                        #     cust_invoice_id = False
                        # supp_invoice_id2 = row[37].strip()
                        user_id_int_id = row[38].strip()
                        if user_id_int_id:
                            self._cr.execute("select id from res_users where user_old_id=" + str(
                                user_id_int_id) + " limit 1")
                            user_id_int_id = self._cr.fetchone()
                            user_id_int_id = user_id_int_id and user_id_int_id[0] or False
                        view_interpreter = row[46].strip()
                        if view_interpreter:
                            self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                                view_interpreter) + " limit 1")
                            view_interpreter = self._cr.fetchone()
                            view_interpreter = view_interpreter and view_interpreter[0] or False


                        current_time = row[47].strip()
                        # timesheet_attachment = row[48].strip()
                        attachment_filename = row[49].strip()
                        interpreters_phone=row[44].strip()
                        interpreters_email=row[45].strip()
                        all_edited=row[39].strip()
                        project_task_vals = {'project_task_old_id': project_task_old_id,
                                             # 'sequence': sequence,
                                             'color': color,
                                             'date_end': date_end,
                                             'planned_hours': float(planned_hours) if planned_hours else '',
                                             'partner_id': partner_id,
                                             'user_id': user_id,
                                             'date_start': date_start,
                                             'company_id': company_id,
                                             'priority': priority,
                                             'state': state,
                                             'description': description,
                                             'kanban_state': kanban_state,
                                             'active': True if active=='t' else False,
                                             'stage_id': stage_id,
                                             'name': name,
                                             'date_deadline': date_deadline,
                                             'notes': notes,
                                             'event_type': event_type,
                                             # 'task_id': task_id,
                                             'event_id': event_id,
                                             # 'transporter_id': transporter_id,
                                             'billing_state': billing_state,
                                             # 'cust_invoice_id': cust_invoice_id,
                                             # 'supp_invoice_id2': supp_invoice_id2,
                                             'user_id_int': user_id_int_id,
                                             'view_interpreter': view_interpreter,
                                             'current_time': current_time,
                                             # 'timesheet_attachment': timesheet_attachment,
                                             'attachment_filename': attachment_filename,
                                             'interpreters_phone':interpreters_phone,
                                             'interpreters_email':interpreters_email,
                                             'all_edited': True if all_edited=='t' else False,
                                                 }
                        if not project_task_obj:
                            project_task_new_id = self.env['project.task'].create(project_task_vals)
                            self._cr.commit()
                        else:
                            project_task_obj.write(project_task_vals)
                            self._cr.commit()
                            _logger.error('-------already found------------')

                except Exception as e:
                    _logger.error('------------error log_id exception---------- %s', e)
                    value.append(str(e))
                    error_list.append(value)
        with open('/home/iuadmin/task/task_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

    # function to import project task work
    @api.multi
    def import_project_task_work(self):
        error_list = []
        header_list = []
        total_row=0
        path = '/home/iuadmin/task_mov'
        for filename in os.listdir(path):
            # do your stuff
            file_obj = path + '/' + filename
            target_doc = csv.reader(open(file_obj, 'rU'), delimiter=",")
            row_num = 0
            data_dict = {}
            for row in target_doc:
                data_dict.update({row_num: row})
                row.append(row_num)
                row_num += 1
            for key, value in data_dict.items():
                try:
                    if key == 0:
                        header_list.append(value)
                    else:
                        row = value
                        _logger.error('----------Row Number---------- %s---%s', key,filename)
                        project_task_work_old_id = row[0].strip()
                        user_id = row[5].strip() or False
                        if user_id:
                            self._cr.execute("select id from res_users where user_old_id=" + str(
                                user_id) + " limit 1")
                            user_id = self._cr.fetchone()
                            user_id = user_id and user_id[0] or False
                        task_obj = self.env['project.task.work'].search([('project_task_work_old_id','=',project_task_work_old_id)],limit=1)
                        task_id = row[7].strip()
                        if task_id:
                            self._cr.execute("select id from project_task where project_task_old_id=" + str(
                                task_id) + " limit 1")
                            task_id = self._cr.fetchone()
                            task_id = task_id and task_id[0] or False
                        name = row[6].strip()

                        date = row[8].strip()
                        company = row[9].strip()
                        if company:
                            company_id = self.env['res.company'].search([('res_company_old_id','=',company)]).id
                        else:
                            company_id = False
                        total_mileage_covered = row[10].strip()
                        hours_spend = row[15].strip()
                        event_start_time = row[12].strip()
                        event_end_time = row[13].strip()
                        task_for = row[14].strip()
                        am_pm2 = row[19].strip()
                        am_pm = row[20].strip()
                        event_start_date = row[22].strip()
                        wait_time_bill = row[23].strip()
                        wait_time = row[24].strip()
                        interpreter_id = row[25].strip()
                        if interpreter_id:
                            self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                                interpreter_id) + " limit 1")
                            interpreter_id = self._cr.fetchone()
                            interpreter_id = interpreter_id and interpreter_id[0] or False
                        event_out_come = row[26].strip()
                        if event_out_come:
                            event_out_come_id = self.env['event.out.come'].search([('event_outcome_old_id','=',event_out_come)],limit=1).id
                        else:
                            event_out_come_id = False
                        event_start_hr = row[29].strip()
                        event_end_hr = row[30].strip()
                        event_end_min = row[31].strip()
                        event_start_min = row[32].strip()
                        edited = row[33].strip()
                        travel_time = row[34].strip()
                        project_task_work_vals = {'project_task_work_old_id': int(project_task_work_old_id),
                                                  'user_id': user_id,
                                                  'name': name,
                                                  'task_id': task_id,
                                                  'date': date,
                                                  'company_id': company_id,
                                                  'total_mileage_covered': int(total_mileage_covered) if total_mileage_covered else 0,
                                                  'hours_spend': hours_spend,
                                                  'event_start_time': event_start_time,
                                                  'event_end_time': event_end_time,
                                                  'task_for': task_for,
                                                  'am_pm2': am_pm2,
                                                  'am_pm': am_pm,
                                                  'event_start_date': event_start_date,
                                                  'wait_time_bill': float(wait_time_bill) if wait_time_bill else 0.0,
                                                  'wait_time': float(wait_time) if wait_time else 0.0,
                                                  'interpreter_id': interpreter_id,
                                                  'event_out_come_id': event_out_come_id,
                                                  'event_start_hr': event_start_hr or 0.0,
                                                  'event_end_hr': event_end_hr or 0.0,
                                                  'event_end_min': event_end_min or 0.0,
                                                  'event_start_min': event_start_min or 0.0,
                                                  'edited': True if edited=='t' else False,
                                                  'travel_time': float(travel_time) if travel_time else 0.0,
                                                 }
                        if not task_obj and task_id:
                            project_task_work_new_id = self.env['project.task.work'].create(project_task_work_vals)
                            self._cr.commit()
                        else:
                            task_obj.write(project_task_work_vals)
                            self._cr.commit()
                            _logger.error('-------already found------------')

                except Exception as e:
                    _logger.error('------------error log_id exception---------- %s', e)
                    self._cr.rollback()
                    value.append(str(e))
                    error_list.append(value)
        with open('/home/iuadmin/uploading_error/task_work_full_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()





