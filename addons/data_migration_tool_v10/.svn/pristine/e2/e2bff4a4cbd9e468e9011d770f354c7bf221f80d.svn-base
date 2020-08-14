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

_logger = logging.getLogger('sale')

class DataMigration2(models.TransientModel):
    _name='data.migration.wizard2'

    upload_file2 = fields.Binary(string='File URL')
    upload_error2= fields.Binary(string='Click To Download Error Log')
    upload_error_file_name2=fields.Char("File name")
# function to import event outcome
    @api.multi
    def cancel_journal_entries(self):
       account_move_ids=self.env['account.move'].search([('amount','=',0.0),('state','=','posted'),('name','not ilike','INV%'),('name','not ilike','%SAJ'),('name','not ilike','EXJ%')])
       for move in account_move_ids:
           move.button_cancel()
           self._cr.commit()
           _logger.info('---------------move cancelled---------------%s',move.id)
       return True



    @api.multi
    def import_event_outcome(self):
        csv_datas = self.upload_file2
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
                    event_outcome_old_id = row[0].strip()
                    name = row[6].strip() or ''
                    company = row[7].strip() or ''
                    event_out_come_id = row[5].strip() or ''
                    company_id=self.env['res.company'].search([('res_company_old_id','=',company)])
                    event_outcome_vals={
                        'name':name,
                        'event_out_come_id':event_out_come_id,
                        'company_id':company_id.id,
                        'event_outcome_old_id':event_outcome_old_id,

                    }
                    event_out_come_new_id=self.env['event.out.come'].create(event_outcome_vals)
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
        self.upload_error2 = base64.encodestring(bytes(file_data))
        self.upload_error_file_name2 = 'Event Outcome Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }
# function to import translator allocation history
    @api.multi
    def import_translator_alloc_history(self):
        csv_datas = self.upload_file2
        error_list = []
        header_list = []
        if not csv_datas:
            raise UserError(_("Choose the file before uploading!!!"))
        fileobj = TemporaryFile('w+')
        fileobj.write(base64.decodestring(csv_datas))
        fileobj.seek(0)
        str_csv_data = fileobj.read()
        lis = csv.reader(StringIO.StringIO(str_csv_data), delimiter=',')
        row_num = 0
        data_dict = {}
        for row in lis:
            data_dict.update({row_num: row})
            row.append(row_num)
            row_num += 1
        # print "Reading Data Complete......"
        for key, value in data_dict.items():
            try:
                if key == 0:
                    header_list.append(value)
                else:
                    _logger.error('------------row number---------- %s', key)
                    translator_alloc_his_old_id = value[0].strip()
                    name = value[5].strip() or False
                    if name:
                        name=self.env['res.partner'].search([('customer_record_old_id','=',name)],limit=1).id
                    event_id = value[6].strip() or False
                    if event_id:
                        event_id = self.env['event'].search([('event_old_id', '=', event_id)],limit=1).id
                    translator_alloc_history_vals = {
                        'certification':translator_alloc_his_old_id,
                        'rate': value[8].strip() or 0.0,
                        'city': value[16].strip() or 0,
                        'event_id':event_id,
                        'state':value[9].strip() or False,
                        'event_date':value[10].strip() or False,
                        'name':name,
                        'event_start_date':value[19].strip() or False,
                        'translator_alloc_his_old_id':value[0].strip() or 0,
                    }
                    translator_alloc_history_id = self.env['translator.alloc.history'].create(translator_alloc_history_vals)
                    self._cr.commit()
            except Exception as e:
                _logger.error('------------error log_id exception---------- %s', e)
                error_list.append(value)
        csvfile = StringIO.StringIO()
        w = csv.writer(csvfile, delimiter=',')
        w.writerow(header_list)
        w.writerows(error_list)
        file_data = csvfile.getvalue()
        self.upload_error = base64.encodestring(bytes(file_data))
        self.upload_error_file_name = 'Translator_Alloc_History_Uploading_Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }

# function to import document type
    @api.multi
    def import_document_type(self):
        csv_datas = self.upload_file2
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
                    _logger.error('------------rownum---------- %s', row_num)
                    document_type_old_id = row[0].strip()
                    name = row[15].strip() or ''
                    for_event = row[6].strip() or ''
                    for_vendor = row[13].strip() or ''
                    for_contact = row[9].strip() or ''
                    has_template = row[7].strip() or ''
                    prefix = row[10].strip() or ''
                    template_master_path = row[11].strip() or ''
                    template_body_path = row[12].strip() or ''
                    doc_type_id = row[5].strip() or ''
                    template = row[14].strip() or ''
                    # template_id=self.env.search([('name','=',template)])
                    company = row[8].strip() or ''
                    company_id = self.env['res.company'].search([('res_company_old_id', '=', company)])
                    document_type_vals = {
                        'name': name,
                        'for_event': True if for_event=='t' else False,
                        'for_vendor':  True if for_vendor=='t' else False,
                        'for_contact': True if for_contact=='t' else False,
                        'has_template': True if has_template=='t' else False,
                        'prefix': prefix,
                        'template_master_path': template_master_path,
                        'template_body_path': template_body_path,
                        'doc_type_id': int(doc_type_id) if doc_type_id==True else 0,
                        'template_id': False,
                        'company_id': company_id.id,
                        'document_type_old_id':int(document_type_old_id),
                    }
                    document_type_new_id = self.env['document.type'].create(document_type_vals)
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
        self.upload_error2 = base64.encodestring(bytes(file_data))
        self.upload_error_file_name2 = 'Document Type Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }
# function to import event to document
    @api.multi
    def import_E2D(self):
        error_list = []
        header_list = []
        total_row=0
        path = '/home/iuadmin/doc_to_event'
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
                        _logger.error('------------rownum---------- %s', key)
                        document_to_event_old_id = row[0].strip()
                        name = row[5].strip() or ''
                        event = row[6].strip() or ''
                        event_id = self.env['event'].search([('event_old_id','=',event)],limit=1).id
                        document = row[11].strip() or ''
                        document_id = self.env['document'].search([('document_old_id','=',document)],limit=1).id
                        interpreter = row[7].strip() or ''
                        interpreter_id = self.env['res.partner'].search([('customer_record_old_id', '=', interpreter)], limit=1).id
                        vendor_id = row[8].strip() or 0
                        document_to_event_id = row[9].strip() or 0
                        company = row[10].strip() or ''
                        company_id = self.env['res.company'].search([('res_company_old_id', '=', company)])
                        e2d_vals = {
                            'name': name,
                            'event_id': event_id,
                            'document_id': document_id,
                            'interpreter_id': interpreter_id,
                            'vendor_id': vendor_id,
                            'document_to_event_id': document_to_event_id,
                            'company_id': company_id.id,
                            'document_to_event_old_id':document_to_event_old_id,
                        }
                        e2d_new_id = self.env['document.to.event'].create(e2d_vals)
                        self._cr.commit()
                except Exception as e:
                    _logger.error('------------error log_id exception---------- %s', e)
                    error_list.append(value)
        with open('/home/iuadmin/uploading_error/document_to_event_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

# function to import document sender
    @api.multi
    def import_doc_sender(self):
        error_list = []
        header_list = []
        # path = '/home/abhishek/Desktop/IUG_master_data/move'
        path = '/home/iuadmin/document_sender'
        for filename in os.listdir(path):
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
                        _logger.error('---current progress -- %s', key)
                        document_sender_old_id = row[0].strip()
                        name = row[5].strip() or ''
                        location = row[6].strip() or ''
                        location_id = self.env['location'].search([('location_old_id','=',location)],limit=1).id
                        document = row[13].strip() or ''
                        document_id = self.env['document'].search([('document_old_id','=',document)],limit=1).id
                        contact = row[9].strip() or ''
                        contact_id = self.env['res.partner'].search([('customer_record_old_id','=',contact)],limit=1).id
                        doctor = row[10].strip() or ''
                        doctor_id = self.env['doctor'].search([('doctor_old_id','=',doctor)],limit=1).id
                        customer = row[11].strip() or ''
                        customer_id = self.env['res.partner'].search([('customer_record_old_id','=',customer)],limit=1).id
                        interpreter = row[12].strip() or ''
                        interpreter_id = self.env['res.partner'].search([('customer_record_old_id','=',interpreter)],limit=1).id
                        vendor_id = row[7].strip() or 0     #Integer
                        doc_sender_id = row[14].strip() or 0 #Integer
                        company = row[8].strip() or ''
                        company_id = self.env['res.company'].search([('res_company_old_id', '=', company)],limit=1).id
                        doc_sender_vals = {
                            'document_sender_old_id':document_sender_old_id,
                            'name': name,
                            'location_id': location_id,
                            'document_id': document_id,
                            'contact_id': contact_id,
                            'doctor_id': doctor_id,
                            'customer_id': customer_id,
                            'interpreter_id': interpreter_id,
                            'vendor_id': vendor_id,
                            'doc_sender_id': doc_sender_id,
                            'company_id': company_id,
                        }
                        doc_sender_new_id = self.env['document.sender'].create(doc_sender_vals)
                        self._cr.commit()
                except Exception as e:
                    _logger.error('------------error log_id exception---------- %s', e)
                    error_list.append(value)
        # with open('/home/abhishek/Desktop/output.csv', 'wb') as f:
        with open('/home/iuadmin/uploading_error/document_sender_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

# function to import document receiver
    @api.multi
    def import_doc_receipt(self):
        csv_datas = self.upload_file2
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
                    _logger.error('------------rownum---------- %s', row_num)
                    document_recipient_old_id =  row[0].strip()
                    name = row[5].strip() or ''
                    location = row[7].strip() or ''
                    location_id = self.env['location'].search([('location_old_id', '=', location)],limit=1).id
                    document = row[16].strip() or ''
                    document_id = self.env['document'].search([('document_old_id', '=', document)],limit=1).id
                    contact = row[11].strip() or ''
                    contact_id = self.env['res.partner'].search([('customer_record_old_id', '=', contact)],limit=1).id
                    doctor = row[13].strip() or ''
                    doctor_id = self.env['doctor'].search([('doctor_old_id', '=', doctor)],limit=1).id
                    customer = row[14].strip() or ''
                    customer_id = self.env['res.partner'].search([('customer_record_old_id', '=', customer)],limit=1).id
                    interpreter = row[15].strip() or ''
                    interpreter_id = self.env['res.partner'].search([('customer_record_old_id', '=', interpreter)],limit=1).id
                    vendor_id = row[9].strip() or 0  # Integer
                    doc_recipient_id = row[8].strip() or 0  # Integer
                    company = row[10].strip() or ''
                    company_id = self.env['res.company'].search([('res_company_old_id', '=', company)],limit=1).id
                    sent_to_company = row[12].strip() or ''
                    sent_to_contact = row[6].strip() or ''
                    doc_receipt_vals = {
                        'document_recipient_old_id':document_recipient_old_id,
                        'name': name,
                        'location_id': location_id,
                        'document_id': document_id,
                        'contact_id': contact_id,
                        'doctor_id': doctor_id,
                        'customer_id': customer_id,
                        'interpreter_id': interpreter_id,
                        'vendor_id': vendor_id,
                        'doc_recipient_id': doc_recipient_id,
                        'company_id': company_id,
                        'sent_to_company': sent_to_company,
                        'sent_to_contact': sent_to_contact
                    }
                    doc_sender_new_id = self.env['document.recipient'].create(doc_receipt_vals)
                    self._cr.commit()
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
        self.upload_error2 = base64.encodestring(bytes(file_data))
        self.upload_error_file_name2 = 'Doc Receiver Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }

# function to import iu message
    @api.multi
    def import_iu_message(self):
        csv_datas = self.upload_file2
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
                    _logger.error('------------rownum---------- %s', row_num)
                    iu_message_old_id = row[0].strip() or ''
                    name = row[6].strip() or ''
                    entered_date = row[7].strip() or ''
                    delivered_date = row[13].strip() or ''
                    contact = row[12].strip() or ''
                    contact_id = self.env['res.partner'].search([('customer_record_old_id','=',contact)],limit=1).id
                    interpreter = row[8].strip() or ''
                    interpreter_id = self.env['res.partner'].search([('customer_record_old_id','=',interpreter)],limit=1).id
                    amount = row[14].strip() or ''
                    notes = row[9].strip() or ''
                    vendor_id = row[10].strip() or ''
                    is_alert = row[5].strip() or ''
                    entered_by_staff= row[15].strip() or ''
                    entered_by_staff_id = self.env['hr.employee'].search([('employee_old_id','=',entered_by_staff)],limit=1).id
                    delivered_by_staff = row[16].strip() or ''
                    delivered_by_staff_id = self.env['hr.employee'].search([('employee_old_id','=',delivered_by_staff)],limit=1).id
                    message_id = row[17].strip() or ''
                    company = row[11].strip() or ''
                    company_id = self.env['res.company'].search([('res_company_old_id','=',company)],limit=1).id
                    if delivered_by_staff_id:
                        iu_message_vals={
                            'iu_message_old_id':iu_message_old_id,
                            'name':name,
                            'entered_date':entered_date,
                            'delivered_date':delivered_date,
                            'contact_id':contact_id,
                            'interpreter_id':interpreter_id,
                            'amount':float(amount) if amount else 0.0,
                            'notes':notes,
                            'vendor_id':int(vendor_id) if vendor_id else 0,
                            'is_alert':True if is_alert=='t' else False,
                            'entered_by_staff_id':entered_by_staff_id,
                            'delivered_by_staff_id':delivered_by_staff_id,
                            'message_id':int(message_id) if message_id else 0,
                            'company_id':company_id
                        }
                        iu_message_id = self.env['iu.message'].create(iu_message_vals)
                    else:
                        _logger.error('-------No Staff Id ----')
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
        self.upload_error2 = base64.encodestring(bytes(file_data))
        self.upload_error_file_name2 = 'IU Message Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }
# fucntion to import location: multiple relations are found
    @api.multi
    def import_location(self):
        error_list = []
        header_list = []
        # file path should be server file path in server
        # path = '/home/abhishek/Desktop/IUG_csv_server_data/event'
        path = '/home/iuadmin/cust_upload/location_data'
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
                        _logger.error('------------rownum---------- %s', key)
                        location_old_id = row[0].strip()
                        location_obj=self.env['location'].search([('location_old_id','=',location_old_id)])

                        doctor_id = row[31].strip() or ''
                        patient_id = row[39].strip() or ''
                        name = row[14].strip() or ''
                        actual_name = row[24].strip() or ''
                        date = row[23].strip() or ''
                        ref = row[16].strip() or ''
                        # user_id = row[11].strip() or ''
                        location_type = row[37].strip() or ''
                        comment = row[5].strip() or ''
                        active = row[7].strip() or ''
                        street = row[8].strip() or ''
                        street2 = row[20].strip() or ''
                        zip = row[27].strip() or ''
                        city = row[10].strip() or ''
                        state_id = row[30].strip() or ''
                        # country_id = row[12].strip() or ''
                        email = row[17].strip() or ''
                        phone = row[21].strip() or ''
                        fax = row[18].strip() or ''
                        mobile = row[28].strip() or ''
                        company_id = row[13].strip() or ''
                        phone2 = row[19].strip() or ''
                        is_alert = row[26].strip() or ''
                        is_sdhhs = row[22].strip() or ''
                        location_id = row[9].strip() or ''
                        location_id2 = row[36].strip() or ''
                        zone_id = row[25].strip() or ''
                        latitude = row[15].strip() or ''
                        longitude = row[29].strip() or ''
                        date_localization = row[6].strip() or ''
                        is_geo = row[33].strip() or ''
                        last_update_date = row[35].strip() or ''
                        land_mark = row[34].strip() or ''
                        complete_name = row[43].strip() or ''
                        is_pat_loc = row[38].strip() or ''
                        # address_type_id = row[40].strip() or ''
                        ordering_partner_id = row[41].strip() or False
                        timezone = row[42].strip() or ''

                        if doctor_id:
                            doc_id = self.env['doctor'].search([('doctor_old_id', '=', doctor_id)],limit=1).id
                        else:
                            doc_id = False

                        if patient_id:
                            pat_id = self.env['patient'].search([('patient_old_id', '=', patient_id)],limit=1).id
                        else:
                            pat_id = False

                        if date:
                            date_format = datetime.strptime(date, "%Y-%m-%d").strftime(DF)
                        else:
                            date_format = False

                        # user = self.env['res.users'].search([('res')])

                        if state_id:
                            state = self.env['res.country.state'].search([('state7_id', '=', state_id)],limit=1).id
                        else:
                            state = False

                        if zone_id:
                            zone = self.env['zone'].search([('zone_old_id', '=', zone_id)],limit=1).id
                        else:
                            zone = False

                        if date_localization:
                            date_localization_format = datetime.strptime(date_localization, "%Y-%m-%d").strftime(DF)
                        else:
                            date_localization_format = False

                        if last_update_date:
                            last_update_date_format = datetime.strptime(last_update_date, "%Y-%m-%d").strftime(DF)
                        else:
                            last_update_date_format = False

                        if ordering_partner_id:
                            self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                                ordering_partner_id) + " limit 1")
                            ordering_partner_id = self._cr.fetchone()
                            ordering_partner_id = ordering_partner_id and ordering_partner_id[0] or False

                        if company_id:
                            company = self.env['res.company'].search([('res_company_old_id', '=', company_id)],limit=1).id
                        else:
                            company = False

                        location_vals = {
                            'location_old_id': location_old_id,
                            'doctor_id': doc_id,
                            'patient_id': pat_id,
                            'name': name,
                            'actual_name': actual_name,
                            'date': date_format,
                            'ref': ref,
                            # 'user_id': user,
                            'location_type':location_type,
                            'comment': comment,
                            'active': True if active == 't' else False,
                            'street': street,
                            'is_alert': True if is_alert == 't' else False,
                            'street2': street2,
                            'zip': zip,
                            'city': city,
                            'state_id': state,
                            'country_id': 235,
                            'email': email,
                            'phone': phone,
                            'fax': fax,
                            'mobile': mobile,
                            'phone2': phone2,
                            'is_sdhhs': True if is_sdhhs == 't' else False,
                            'location_id': int(location_id) if location_id else 0,
                            'location_id2': int(location_id2) if location_id2 else 0,
                            'zone_id': zone,
                            'latitude': float(latitude) if latitude else 0.0,
                            'longitude': float(longitude) if longitude else 0.0,
                            'date_localization': date_localization_format,
                            'is_geo': True if is_geo == 't' else False,
                            'last_update_date': last_update_date_format,
                            'land_mark': land_mark,
                            'complete_name': complete_name,
                            'is_pat_loc': True if is_pat_loc == 't' else False,
                            # 'address_type_id': address_type_id,
                            'ordering_partner_id': ordering_partner_id,
                            'timezone': timezone,
                            'company_id': company,
                        }
                        if not location_obj:
                            location_new_id = self.env['location'].create(location_vals)
                            self._cr.commit()
                        else:
                            location_obj.write(location_vals)
                            self._cr.commit()
                            _logger.error('---location exist-----')
                except Exception as e:
                    _logger.error('------------error log_id exception---------- %s', e)
                    value.append(str(e))
                    error_list.append(value)

        # with open('/home/abhishek/Desktop/output.csv', 'wb') as f:
        with open('/home/iuadmin/cust_upload_err/location_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()
# function to import leads
    @api.multi
    def import_interpret_alloc_his(self):
        csv_datas = self.upload_file2
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
                    _logger.error('------------rownum---------- %s', row_num)
                    name = row[1].strip() or ''
                    event_date = row[1].strip() or ''
                    event_id = row[1].strip() or ''
                    voicemail_msg = row[1].strip() or ''
                    state = row[1].strip() or ''
                    event_start_date = row[1].strip() or ''
                    event_start = row[1].strip() or ''
                    event_end = row[1].strip() or ''
                    allocate_date = row[1].strip() or ''
                    confirm_date = row[1].strip() or ''
                    cancel_date = row[1].strip() or ''
                    company = row[1].strip() or ''
                    company_id = self.env['res.partner'].search([('name', '=', company)])
                    interpret_alloc_his_vals = {
                        'name': name,
                        'event_date': event_date,
                        'event_id': event_id,
                        'voicemail_msg': voicemail_msg,
                        'state': state,
                        'event_start_date': event_start_date,
                        'event_start': event_start,
                        'event_end': event_end,
                        'allocate_date': allocate_date,
                        'confirm_date': confirm_date,
                        'cancel_date': cancel_date,
                        'company_id': company_id
                    }
                    interpret_alloc_his_id = self.env['interpreter.alloc.history'].create(interpret_alloc_his_vals)
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
        self.upload_error2 = base64.encodestring(bytes(file_data))
        self.upload_error_file_name2 = 'Interpret Alloc His Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }

    # function to import res users
    @api.multi
    def import_users(self):
        path = '/home/iuadmin/user_data'
        error_list = []
        header_list = []
        group_id_vendor = [960]
        group_id_customer = [962]
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
                        header = value
                    else:
                        row = value
                        _logger.error('------------rownum---------- %s', key)
                        user_old_id = row[0].strip()
                        active = row[1].strip() or ''
                        login = row[2].strip() or ''
                        password = row[3].strip() or ''
                        company = row[4].strip() or ''
                        if company:
                            company_id = self.env['res.company'].search([('res_company_old_id', '=', company)], limit=1).id
                        else:
                            company_id = False
                        partner_id = value[5].strip() or False
                        if partner_id:
                            self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                                partner_id) + " limit 1")
                            partner_id = self._cr.fetchone()
                            partner_id = partner_id and partner_id[0] or False
                        login_date = row[11].strip() or ''
                        if login_date:
                            login_date = datetime.strptime(login_date, "%Y-%m-%d").strftime(DF)
                        else:
                            login_date = False
                        signature = row[12].strip() or ''
                        share = row[15].strip() or ''  # bool
                        user_type = row[20].strip() or ''
                        entity_id = row[17].strip() or ''  # int
                        mail_group = row[18].strip() or ''
                        login_id = row[19].strip() or ''  # int
                        # user_type_id=row[15].strip() or ''
                        require_to_reset = row[22].strip() or ''
                        zone_id = row[24].strip() or ''
                        if zone_id:
                            zone_id = self.env['zone'].search([('zone_old_id', '=', zone_id)], limit=1).id
                        else:
                            zone_id = False

                        user_obj = self.env['res.users'].search([('login', 'ilike', login)])
                        if user_obj:
                            user_update_vals = {
                                'user_old_id': user_old_id,
                                'active': True if active == 't' else False,
                                'password': password,
                                'company_ids': [(4, company_id)],
                                'company_id': company_id,
                                'login_date': login_date,
                                'signature': signature,
                                'share': True if share == 't' else False,
                                'user_type': user_type,
                                'entity_id': entity_id,
                                'mail_group': mail_group,
                                'login_id': login_id,
                                'require_to_reset': True if require_to_reset == 't' else False,
                                'zone_id': zone_id,
                            }
                            user_obj.sudo().write(user_update_vals)
                            self._cr.commit()
                        elif partner_id:
                            user_vals = {
                                'user_old_id': user_old_id,
                                'active': True if active == 't' else False,
                                'login': login,
                                'company_ids': [(4, company_id)],
                                'password': password,
                                'company_id': company_id,
                                'partner_id': partner_id,
                                'login_date': login_date,
                                'signature': signature,
                                'share': True if share == 't' else False,
                                'user_type': user_type,
                                'entity_id': entity_id,
                                'mail_group': mail_group,
                                'login_id': login_id,
                                'require_to_reset': True if require_to_reset == 't' else False,
                                'zone_id': zone_id,
                            }
                            if user_type == 'vendor':
                                user_vals.update({'groups_id': [(6, 0, group_id_vendor)]})
                            elif user_type == 'contact':
                                user_vals.update({'groups_id': [(6, 0, group_id_customer)]})
                            user_new_id = self.env['res.users'].sudo().create(user_vals)
                            self._cr.commit()
                        else:
                            _logger.error('-----No matching partner----')

                except Exception as e:
                    self._cr.rollback()
                    _logger.error('------------Error Exception---------- %s', e)
                    value.append(str(e))
                    error_list.append(value)
        with open('/home/iuadmin/cust_upload_err/user_upload_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()
    # function to import customers
    @api.multi
    def import_customers(self):
        error_list=[]
        header_list=[]
        # path = '/home/abhishek/Desktop/IUG_csv_server_data/custmr'
        path = '/home/iuadmin/cust_upload/cust_upload'
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
                        header = value
                        header_list.append(value)
                    else:
                        row=value
                        customer_record_old_id = row[0].strip() or 0
                        cut_ob=self.env['res.partner'].search([('customer_record_old_id','=',customer_record_old_id)],limit=1)

                        _logger.error('------------rown---------- %s', key)
                        _logger.error('------------current File---------- %s', filename)

                        name=row[1].strip() or ''
                        lang=row[2].strip() or ''

                        company_id=row[3].strip() or False
                        if company_id:
                            company_id=self.env['res.company'].search([('res_company_old_id','=',company_id)],limit=1).id
                        comment=row[8].strip() or ''
                        ean13=row[9].strip() or '' #new name barcode
                        color=row[10].strip() or ''
                       # image=row[11].strip() or ''
                        # use_parent_address=row[12].strip() or '' #boolean
                        active=row[13].strip() or ''
                        street=row[14].strip() or ''
                        supplier=row[15].strip() or '' #boolean
                        city=row[16].strip() or ''
                        user_id=row[17].strip() or False
                        # if user_id:
                        #     user_id=self.env['res.users'].search([('user_old_id','=',user_id)],limit=1).id
                        zip=row[18].strip() or ''
                        # title_id=row[19].strip() or False
                        # if title_id:
                        #     title_id=self.env['res.partner.title'].search([('res_title_old_id', '=', title_id)],limit=1).id #fix it
                        country_id=row[21].strip() or ''#M2O
                        # parent_id=row[22].strip() or False
                        # if parent_id:
                        #     parent_id=self.env['res.partner'].search([('customer_record_old_id','=',parent_id)],limit=1).id
                        employee=row[23].strip() or '' #Boolean
                        type=row[24].strip() or ''
                        email=row[25].strip() or ''
                        vat=row[26].strip() or ''
                        website=row[27].strip() or ''
                        fax=row[28].strip() or ''
                        street2=row[29].strip() or ''
                        try:
                            phone=row[30].strip().replace("+", "").replace("-", "").replace("N/A", "")
                        except Exception as err:
                            phone=1234567890
                        credit_limit=row[31].strip() or ''
                        date=row[32].strip() or ''
                        if date:
                            date = datetime.strptime(date, "%Y-%m-%d").strftime(DF)
                        else:
                            date = False

                        tz=row[33].strip() or ''
                        customer=row[34].strip() or '' #Boolean
                        #image_medium=row[35].strip() or ''
                        mobile=row[36].strip() or ''
                        ref=row[37].strip() or ''
                        #image_small=row[38].strip() or ''
                        is_company=row[40].strip() or '' #boolean
                        state_id=row[41].strip() or False
                        if state_id:
                            state_id=self.env['res.country.state'].search([('state7_id','=',state_id)],limit=1).id
                        notification_email_send=row[42].strip() or ''
                        if notification_email_send =='email':
                            notification_email_send= 'always'
                        else:
                            notification_email_send = 'none'

                        opt_out=row[43].strip() or '' #boolean
                        signup_type=row[44].strip() or ''
                        signup_expiration=row[45].strip() or ''
                        signup_token=row[46].strip() or ''
                        last_reconciliation_date=row[47].strip() or ''
                        if last_reconciliation_date:
                            last_reconciliation_date = datetime.strptime(last_reconciliation_date, "%Y-%m-%d %H:%M:%S").strftime(DF)
                        else:
                            last_reconciliation_date = False

                        debit_limit=row[48].strip() or ''
                        # section_id=row[49].strip() or '' #update after creation
                        display_name=row[50].strip() or ''
                        # customer_profile_id=row[51].strip() or '' #NOT AN ISSUE
                        date_localization=row[52].strip() or ''
                        if date_localization:
                            date_localization = datetime.strptime(date_localization, "%Y-%m-%d").strftime(DF)

                        else:
                            date_localization = False
                        is_agency=row[54].strip() or '' #boolean field
                        last_name=row[55].strip() or ''
                        cust_type=row[56].strip() or ''
                        wb_on_file=row[58].strip() or '' #boolean
                        location=row[59].strip() or '' #create location
                        short_name=row[65].strip() or ''
                        # rating_id=row[66].strip() or ''
                        fee_note=row[68].strip() or '' #boolean
                        billing_contact=row[69].strip() or '' #boolean
                        ssnid=row[72].strip() or ''#updated after creation
                        # billing_contact_id=row[73].strip() or False
                        # if billing_contact_id:
                        #     billing_contact_id=self.env['res.partner'].search([('customer_record_old_id','=',
                        #                                                         billing_contact_id)],limit=1).id
                        # meta_zone_id=row[74].strip() or False
                        # if meta_zone_id:
                        #     meta_zone_id = self.env['meta.zone'].search([('meta_zone_old_id', '=', meta_zone_id)],
                        #                                                 limit=1).id
                        gender=row[75].strip() or ''
                        is_payee=row[76].strip() or '' #boolean
                        degree_subject2=row[77].strip() or '' #updated after creation

                        zip2=row[79].strip() or ''
                        extension2=row[81].strip() or '' #nul
                        extension1=row[82].strip() or '' #nul
                        customer_profile=row[83].strip() or '' #boolean field
                        sddhs=row[85].strip() or ''
                        phone2=row[86].strip() or ''
                        phone3=row[87].strip() or ''
                        street3=row[88].strip() or ''
                        street4=row[89].strip() or ''
                        call_date=row[90].strip() or ''
                        resume_on_file=row[91].strip() or '' #boolean field
                        phone4=row[92].strip() or ''
                        do_editing=row[93].strip() or '' #boolean field
                        extension=row[94].strip() or ''
                        email2=row[95].strip() or ''
                        gpuid=row[96].strip() or ''
                        is_alert=row[97].strip() or '' #booelan
                        csid=row[98].strip() or ''
                        due_days=row[99].strip() or ''
                        # bill_miles=row[100].strip() or ''
                        minimum_rate=row[101].strip() or ''
                        # customer_letter=row[102].strip() or ''
                        # staff_id=row[103].strip() or '' #boolean
                        is_csid=row[104].strip() or ''
                        fax2=row[105].strip() or ''
                        need_glcode=row[106].strip() or '' #boolean
                        end_date=row[107].strip() or ''
                        country_id2=row[108].strip() or ''
                        sinid=row[109].strip() or ''
                        # zone_id=row[110].strip() or False
                        # if zone_id:
                        #     zone_id = self.env['zone'].search([('zone_old_id', '=', zone_id)],
                        #                                       limit=1).id
                        auth_cc_number=row[111].strip() or ''
                        latitude=row[112].strip() or ''
                        longitude=row[117].strip() or ''
                        suffix=row[119].strip() or ''
                        order_note=row[120].strip() or '' #boolean
                        ordering_contact=row[121].strip() or '' #boolean
                        distribution=row[122].strip() or ''
                        # is_contact=row[124].strip() or ''
                        min_editing_rate=row[125].strip() or ''
                        is_schedular=row[126].strip() or '' #boolean
                        city2=row[127].strip() or ''
                        billing_comment=row[128].strip() or ''
                        contact_letter=row[129].strip() or ''
                        middle_name=row[130].strip() or ''
                        is_geo=row[131].strip() or ''#boolean
                        company_name=row[132].strip() or ''
                        auth_cc_expiration_date=row[133].strip() or ''
                        if auth_cc_expiration_date:
                            auth_cc_expiration_date = datetime.strptime(auth_cc_expiration_date, "%Y-%m-%d").strftime(DF)
                        else:
                            auth_cc_expiration_date = False
                        department=row[134].strip() or ''
                        login_id=row[135].strip() or '' #NA
                        language_id=row[136].strip() or False
                        if language_id:
                            language_id = self.env['language'].search([('language_old_id', '=', language_id)],
                                                                      limit=1).id
                        is_adjuster=row[137].strip() or '' #booelan
                        expiry_date=row[138].strip() or ''
                        confirmation_email=row[139].strip() or '' #boolean
                        telephone_interpretation=row[141].strip() or '' #boolean
                        quickbooks_id=row[142].strip() or '' #integer
                        gsa=row[144].strip() or '' #boolean
                        ext=row[145].strip() or ''
                        billing_partner_id=row[146].strip() or False
                        # if billing_partner_id:
                        #     billing_partner_id=self.env['res.partner'].search([('customer_record_old_id', '=',
                        #                                       billing_partner_id)], limit=1).id

                        modem=row[147].strip() or ''
                        vendor_id=row[148].strip() or ''
                        complete_name=row[149].strip() or ''
                        # inc_min=row[150].strip() or ''
                        provider_id=row[151].strip() or ''
                        # duplicate_partner=row[152].strip() or ''
                        # base_hour=row[153].strip() or ''
                        # inc_min_med=row[154].strip() or ''
                        # inc_min_conf=row[155].strip() or ''
                        special_customer=row[156].strip() or ''
                        base_hour_conf=row[157].strip() or ''
                        # base_hour_med=row[158].strip() or ''
                        last_update_date=row[159].strip() or ''
                        if last_update_date:
                            last_update_date = datetime.strptime(last_update_date, "%Y-%m-%d").strftime(DF)
                        else:
                            last_update_date = False
                        base_hour_depos=row[160].strip() or ''
                        inc_min_depos=row[161].strip() or ''
                        contract_on_file=row[162].strip() or ''
                        # sales_representative=row[163].strip() or ''
                        is_translation_active=row[164].strip() or '' #boolean
                        # sales_representative_id=row[165].strip() or False
                        # if sales_representative_id:
                        #     sales_representative_id = self.env['res.users'].search(
                        #         [('user_old_id', '=', sales_representative_id)], limit=1).id
                        has_login=row[166].strip() or ''#boolean
                        is_interpretation_active=row[167].strip() or ''#boolean
                        is_transportation_active=row[168].strip() or ''#boolean
                        event_approval=row[169].strip() or ''#boolean
                        event_verification=row[170].strip() or ''#boolean
                        suppress_email=row[171].strip() or ''#boolean
                        # scheduler_id=row[172].strip() or False
                        # if scheduler_id:
                        #     scheduler_id = self.env['res.users'].search(
                        #         [('user_old_id', '=', scheduler_id)], limit=1).id
                        # head_contact_id=row[173].strip() or False
                        # if head_contact_id:
                        #     head_contact_id = self.env['res.partner'].search(
                        #         [('customer_record_old_id', '=', head_contact_id)], limit=1).id
                        customer_basis=row[174].strip() or '' #boolean
                        mental_prog=row[175].strip() or ''
                        rubrik=row[176].strip() or ''
                        rate=row[177].strip() or ''
                        discount=row[178].strip() or ''
                        bill_miles_after=row[179].strip() or ''
                        is_monthly=row[180].strip() or '' #boolean
                        contract_no=row[181].strip() or ''
                        customer_group_id=row[182].strip() or False
                        if customer_group_id:
                            customer_group_id=self.env['customer.group'].search(
                                [('customer_group_old_id','=',customer_group_id)],limit=1).id

                        # interpreter_id=row[183].strip() or False
                        # if interpreter_id:
                        #     interpreter_id= self.env['res.partner'].search(
                        #         [('customer_record_old_id', '=', interpreter_id)], limit=1).id

                        # sd_id=row[184].strip() or ''
                        albors_id=row[185].strip() or ''
                        is_sync=row[186].strip() or '' #boolean
                        # parent_cust_id=row[187].strip() or '' #updated after creation
                        opt_for_sms=row[188].strip() or '' #boolean
                        ext_phone3=row[189].strip() or 0
                        ext_phone1=row[190].strip() or 0
                        ext_phone4=row[191].strip() or 0
                        ext_phone2=row[192].strip() or 0
                        dob=row[193].strip() or ''
                        age=row[194].strip() or ''
                        opt_out_of_feedback_emails=row[195].strip() or '' #boolean
                        # partner_id_sms=row[196].strip() or ''

                        customer_vals={
                                'customer_record_old_id':int(customer_record_old_id),
                                'name':name,
                                'lang':lang,
                                'company_id':company_id,
                                'comment':comment,
                                'barcode':ean13,
                                'color':color,
                                # 'use_parent_address': True if use_parent_address=='t' else False,
                                'active':active,
                                'street':street,
                                'supplier':True if supplier=='t' else False,
                                'city':city,
                                # 'user_id':user_id,
                                'zip':zip,
                                # 'title':title_id.id,
                                'country_id':235,
                                # 'parent_id':parent_id,
                                'employee':True if employee=='t' else False,
                                'type':type,
                                'email':email,
                                'vat':vat,
                                'website':website,
                                'fax':fax,
                                'street2':street2,
                                'phone':phone,
                                'credit_limit':credit_limit,
                                'date':date,
                                'tz':tz,
                                'customer':True if customer=='t' else False,
                               # 'image_medium':image_medium,
                                'mobile':mobile,
                                'ref':ref,
                               # 'image_small':image_small,
                                'is_company':True if is_company=='t' else False,
                                'state_id':state_id,
                                # 'notify_email':notification_email_send,
                                'opt_out':True if opt_out=='t' else False,
                                'signup_type':signup_type,
                                'signup_expiration':signup_expiration,
                                'signup_token':signup_token,
                                'last_time_entries_checked':last_reconciliation_date,
                                'debit_limit':debit_limit,
                                # 'section_id':section_id,
                                'display_name':display_name,
                                # 'customer_profile_id':customer_profile_id,
                                'date_localization':date_localization,
                                'is_agency':True if is_agency=='t' else False,
                                'last_name':last_name,
                                'cust_type':cust_type,
                                'wb_on_file':True if wb_on_file=='t' else False,
                                'short_name':short_name,

                                'fee_note':True if fee_note=='t' else False,
                                'billing_contact':True if billing_contact=='t' else False,
                                # 'is_gpuid':is_gpuid,
                                # 'billing_addr':billing_addr,
                                'ssnid':ssnid,
                                # 'billing_contact_id':billing_contact_id,
                                # 'meta_zone_id':meta_zone_id,
                                'gender':gender,
                                'is_payee':True if is_payee=='t' else False,

                                'extension2':extension2,
                                'extension1':extension1,
                                'customer_profile':True if customer_profile=='t' else False,
                                # 'sddhs':sddhs,
                                'phone2':phone2,
                                'phone3':phone3,

                                'phone4':phone4,
                                'do_editing':True if do_editing=='t' else False,
                                'extension':extension,
                                # 'email2':email2,
                                'gpuid':gpuid,
                                'is_alert':True if is_alert=='t' else False,
                                'csid':csid,
                                'due_days':due_days,
                                # 'bill_miles':bill_miles,
                                'minimum_rate':minimum_rate,
                                # 'customer_letter':customer_letter,
                                # 'staff_id':True if staff_id=='t' else False,
                                'is_csid':is_csid,
                                'fax2':fax2,
                                'need_glcode':True if need_glcode=='t' else False,
                                'end_date':end_date,
                                # 'country_id2':235,
                                'sinid':sinid,
                                # 'zone_id':zone_id,
                                'auth_cc_number':auth_cc_number,
                                'latitude':latitude,
                                # 'phone_type_id1':phone_type_id1,
                                # 'phone_type_id3':phone_type_id3,
                                # 'phone_type_id2':phone_type_id2,
                                # 'phone_type_id4':phone_type_id4,
                                'longitude':longitude,
                                # 'customer_type':customer_type,
                                # 'suffix':suffix,
                                'order_note':True if order_note=='t' else False,
                                'ordering_contact':True if ordering_contact=='t' else False,
                                # 'distribution':distribution,
                                # 'vendor_id2':vendor_id2,
                                # 'is_contact':is_contact,
                                'min_editing_rate':min_editing_rate,
                                'is_schedular':True if is_schedular=='t' else False,
                                # 'city2':city2,
                                'billing_comment':billing_comment,
                                # 'contact_letter':contact_letter,
                                'middle_name':middle_name,
                                'is_geo':True if is_geo=='t' else False,
                                'company_name':company_name,
                                'auth_cc_expiration_date':auth_cc_expiration_date,
                                'department':department,
                                'login_id':login_id,
                                'language_id':language_id,
                                'is_adjuster':True if is_adjuster=='t' else False,
                                'expiry_date':expiry_date,
                                'confirmation_email':True if confirmation_email=='t' else False,
                                'telephone_interpretation':True if telephone_interpretation=='t' else False,
                                'quickbooks_id':quickbooks_id,
                                'gsa':True if gsa=='t' else False,
                                'ext':ext,
                                # 'billing_partner_id':billing_partner_id,
                                'modem':modem,
                                'vendor_id':vendor_id,
                                'complete_name':complete_name,
                                # 'inc_min':inc_min,
                                'provider_id':provider_id,

                                'special_customer':special_customer,
                                # 'base_hour_conf':base_hour_conf,
                                # 'base_hour_med':base_hour_med,
                                'last_update_date':last_update_date,
                                # 'base_hour_depos':base_hour_depos,
                                # 'inc_min_depos':inc_min_depos,
                                'contract_on_file':True if contract_on_file=='t' else False,
                                'is_translation_active':True if is_translation_active=='t' else False,
                                # 'sales_representative_id':sales_representative_id,
                                'has_login':True if has_login=='t' else False,
                                'is_interpretation_active':True if is_interpretation_active=='t' else False,
                                'is_transportation_active':True if is_transportation_active=='t' else False,
                                # 'event_approval':True if event_approval=='t' else False,
                                # 'event_verification':True if event_verification=='t' else False,
                                'suppress_email':True if suppress_email=='t' else False,
                                # 'scheduler_id':scheduler_id,
                                # 'head_contact_id':head_contact_id,
                                'customer_basis':True if customer_basis=='t' else False,
                                'mental_prog':mental_prog,
                                'rubrik':rubrik,
                                'rate':rate,
                                'discount':discount,
                                'bill_miles_after':bill_miles_after,
                                'is_monthly':True if is_monthly=='t' else False,
                                'contract_no':contract_no,
                                'customer_group_id':customer_group_id,
                                # 'interpreter_id':interpreter_id,
                                #'sd_id':sd_id,
                                'albors_id':albors_id,
                                'is_sync':True if is_sync=='t' else False,
                                # 'parent_cust_id':parent_cust_id,
                                'opt_for_sms':True if opt_for_sms=='t' else False,
                                'ext_phone3':ext_phone3,
                                'ext_phone1':ext_phone1,
                                'ext_phone4':ext_phone4,
                                'ext_phone2':ext_phone2,
                                'dob':dob,
                                'age':age,
                                'opt_out_of_feedback_emails':True if opt_out_of_feedback_emails=='t' else False,
                                # 'partner_id_sms':partner_id_sms,
                            }


                        if not cut_ob:
                            customer_new_id = self.env['res.partner'].create(customer_vals)
                            self._cr.commit()
                        else:
                            cut_ob.write(customer_vals)
                            _logger.error('------------Customer written !!----------%s', key)
                            self._cr.commit()
            # code here
                except Exception as e:
                   self._cr.rollback()
                   value.append(str(e))
                   _logger.error('------------error log_id exception---------- %s', e)
                   error_list.append(value)
        # with open('/home/abhishek/Desktop/output.csv', 'wb') as f:
        with open('/home/iuadmin/cust_upload_err/cust_upload_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()


# funtion to create twilio send sms
    @api.multi
    def import_twilio_send(self):
        csv_datas = self.upload_file2
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
                    _logger.error('------------rownum---------- %s', row_num)
                    twilio_send_old_id=row[2].strip() or ''
                    status=row[2].strip() or ''
                    direction=row[2].strip() or ''
                    account_id=row[2].strip() or ''
                    price=row[2].strip() or ''
                    message_sid=row[2].strip() or ''
                    sms_to=row[2].strip() or ''
                    sms_from=row[2].strip() or ''
                    error_msg=row[2].strip() or ''
                    sms_body=row[2].strip() or ''
                    account_sid=row[2].strip() or ''
                    error_code=row[2].strip() or ''
                    price_unit=row[2].strip() or ''

                    twilio_send_vals = {
                        'name': twilio_send_old_id,
                        'status': status,
                        'direction': direction,
                        'account_id': account_id,
                        'price': price,
                        'message_sid': message_sid,
                        'sms_to': sms_to,
                        'sms_from': sms_from,
                        'error_msg': error_msg,
                        'sms_body': sms_body,
                        'account_sid': account_sid,
                        'error_code': error_code,
                        'price_unit': price_unit,
                    }
                    twilio_send_id = self.env['twilio.sms.send'].create(twilio_send_vals)
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
        self.upload_error2 = base64.encodestring(bytes(file_data))
        self.upload_error_file_name2 = 'twilio send Uploading Error.csv'
        csvfile.close()


    # funtion to create twilio receive sms
    @api.multi
    def import_twilio_receive(self):
        csv_datas = self.upload_file2
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
                    _logger.error('------------rownum---------- %s', row_num)
                    twilio_rec_old_id = row[2].strip() or ''
                    status = row[2].strip() or ''
                    account_id = row[2].strip() or ''
                    from_zip = row[2].strip() or ''
                    from_country = row[2].strip() or ''
                    message_sid = row[2].strip() or ''
                    service_sid = row[2].strip() or ''
                    sms_from = row[2].strip() or ''
                    to_zip = row[2].strip() or ''
                    from_state = row[2].strip() or ''
                    to_state = row[2].strip() or ''
                    sms_body = row[2].strip() or ''
                    sms_to = row[2].strip() or ''
                    account_sid = row[2].strip() or ''
                    to_city = row[2].strip() or ''
                    to_country = row[2].strip() or ''
                    from_city = row[2].strip() or ''
                    api_version = row[2].strip() or ''

                    twilio_rec_vals = {
                        'twilio_rec_old_id': twilio_rec_old_id,
                        'status': status,
                        'account_id': account_id,
                        'from_zip': from_zip,
                        'from_country': from_country,
                        'message_sid': message_sid,
                        'service_sid': service_sid,
                        'sms_from': sms_from,
                        'to_zip': to_zip,
                        'from_state': from_state,
                        'to_state': to_state,
                        'sms_body': sms_body,
                        'sms_to': sms_to,
                        'account_sid': account_sid,
                        'to_city': to_city,
                        'to_country': to_country,
                        'from_city': from_city,
                        'api_version': api_version,
                    }
                    twilio_rec_id = self.env['twilio.sms.received'].create(twilio_rec_vals)
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
        self.upload_error2 = base64.encodestring(bytes(file_data))
        self.upload_error_file_name2 = 'Twilio receive Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }
# funtion to import documents
    @api.multi
    def import_documents(self):
        csv_datas = self.upload_file2
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
                    _logger.error('------------rownum---------- %s', row_num)
                    document_old_id = row[0].strip()
                    name=row[6].strip() or ''
                    doc_sender_name=row[11].strip() or ''
                    sent_to_no=row[14].strip() or ''
                    sent_from_no=row[8].strip() or ''
                    duration=row[13].strip() or ''
                    page_count=row[9].strip() or ''
                    doc_type=row[5].strip() or ''
                    doc_type_id=self.env['document.type'].search([('document_type_old_id','=',doc_type)])
                    document_id=row[17].strip() or '' #INT Field
                    status=row[7].strip() or ''
                    status_id=self.env['document.status'].search([('document_status_old_id','=',status)])
                    platform_fax_id=row[12].strip() or ''
                    ready_to_send=row[15].strip() or ''
                    log_text=row[16].strip() or ''
                    company=row[10].strip() or ''
                    company_id=self.env['res.company'].search([('res_company_old_id','=',company)])

                    document_vals = {
                        'name': name,
                        'doc_sender_name': doc_sender_name,
                        'sent_to_no': sent_to_no,
                        'sent_from_no': sent_from_no,
                        'duration': duration,
                        'page_count': int(page_count) if page_count else 0,
                        'doc_type_id': doc_type_id.id,
                        'document_id': document_id,
                        'status_id': status_id.id,
                        'platform_fax_id': platform_fax_id,
                        'ready_to_send':True if ready_to_send=='t' else False,
                        'log_text': log_text,
                        'company_id': company_id.id,
                        'document_old_id':int(document_old_id) if document_old_id else 0,
                    }
                    document_new_id = self.env['document'].create(document_vals)
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
        self.upload_error2 = base64.encodestring(bytes(file_data))
        self.upload_error_file_name2 = 'Document Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }

    @api.multi
    def update_state_old(self):
        csv_datas = self.upload_file2
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
                    _logger.error('------------rownum---------- %s', row_num)
                    name = row[7].strip() or ''
                    state_id=self.env['res.country.state'].search([('name','=',name)])
                    old_id=row[0].strip() or 0
                    if state_id:
                        state_id[0].write({'state7_id':int(old_id)})
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
        self.upload_error2 = base64.encodestring(bytes(file_data))
        self.upload_error_file_name2 = 'Document Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }

    @api.multi
    def import_invocie(self):
        csv_datas = self.upload_file2
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
                    _logger.error('------------rownum---------- %s', row_num)
                    origin=row[0].strip() or ''
                    date_due=row[0].strip() or 0
                    check_total=row[0].strip() or 0
                    reference=row[0].strip() or ''
                    supplier_invoice_number=row[0].strip() or ''
                    number=row[0].strip() or 0
                    account_id=row[0].strip() or 0
                    company_id=row[0].strip() or 0
                    currency_id=row[0].strip() or 0
                    partner_id=row[0].strip() or 0
                    fiscal_position=row[0].strip() or 0
                    user_id=row[0].strip() or 0
                    partner_bank_id=row[0].strip() or 0
                    payment_term=row[0].strip() or 0
                    reference_type=row[0].strip() or ''
                    journal_id=row[0].strip() or 0
                    amount_tax=row[0].strip() or 0
                    state=row[0].strip() or ''
                    type=row[0].strip() or ''
                    internal_number=row[0].strip() or ''
                    reconciled=row[0].strip() or '' #boolean
                    residual=row[0].strip() or 0
                    move_name=row[0].strip() or ''
                    date_invoice=row[0].strip() or 0
                    period_id=row[0].strip() or 0
                    amount_untaxed=row[0].strip() or 0
                    move_id=row[0].strip() or 0
                    amount_total=row[0].strip() or 0
                    name=row[0].strip() or ''
                    comment=row[0].strip() or ''
                    sent=row[0].strip() or '' #boolean
                    commercial_partner_id=row[0].strip() or 0
                    auth_transaction_type=row[0].strip() or ''
                    customer_payment_profile_id=row[0].strip() or ''
                    cc_number=row[0].strip() or ''
                    auth_respmsg=row[0].strip() or ''
                    authorization_code=row[0].strip() or ''
                    capture_status=row[0].strip() or ''
                    invoice_original_id=row[0].strip() or 0
                    auth_transaction_id=row[0].strip() or ''
                    customer_profile_id=row[0].strip() or ''
                    amount_charged=row[0].strip() or 0
                    section_id=row[0].strip() or 0
                    Invoice_id=row[0].strip() or 0
                    contact_id=row[0].strip() or 0
                    language_id=row[0].strip() or 0
                    is_suppressed=row[0].strip() or '' #boolean
                    is_printed=row[0].strip() or '' #boolean
                    c_gpuid=row[0].strip() or ''
                    event_start=row[0].strip() or ''#time
                    c_csid=row[0].strip() or ''
                    ordering_contact_id=row[0].strip() or 0
                    entered_by_staffid=row[0].strip() or 0
                    project_name=row[0].strip() or ''
                    is_posted=row[0].strip() or '' #boolean
                    interpreter_id=row[0].strip() or 0
                    is_silent=row[0].strip() or '' #boolean
                    event_end=row[0].strip() or '' #time
                    ordering_partner_id=row[0].strip() or 0
                    is_notdiscount=row[0].strip() or '' #boolean
                    posted_by_staffid=row[0].strip() or 0
                    event_id=row[0].strip() or 0
                    location_id=row[0].strip() or 0
                    is_invoice_nocalc=row[0].strip() or '' #boolean
                    translator_id=row[0].strip() or 0
                    quickbooks_id=row[0].strip() or ''
                    doctor_id=row[0].strip() or 0
                    transporter_id=row[0].strip() or 0
                    invoice_id2=row[0].strip() or 0
                    invoice_ref=row[0].strip() or 0
                    claim_no=row[0].strip() or ''
                    check_no=row[0].strip() or ''
                    invoice_id=row[0].strip() or 0
                    patient_id=row[0].strip() or 0
                    department=row[0].strip() or ''
                    approving_manager=row[0].strip() or ''
                    nuid_code=row[0].strip() or ''
                    sales_representative=row[0].strip() or 0
                    gl_code=row[0].strip() or ''
                    project_name_id=row[0].strip() or 0
                    invoice_for=row[0].strip() or ''
                    sales_representative_id=row[0].strip() or 0
                    scheduler_id=row[0].strip() or 0
                    approving_mgr=row[0].strip() or ''
                    is_emailed=row[0].strip() or ''#boolean
                    is_mailed=row[0].strip() or ''#boolean
                    is_faxed=row[0].strip() or ''#boolean
                    is_monthly=row[0].strip() or ''#boolean
                    event_type=row[0].strip() or ''
                    month=row[0].strip() or ''
                    cust_gpuid=row[0].strip() or ''
                    year=row[0].strip() or ''
                    cust_csid=row[0].strip() or ''
                    event_start_date=row[0].strip() or 0 #date
                    ref=row[0].strip() or ''
                    internal_comment=row[0].strip() or ''
                    state_name_related=row[0].strip() or 0
                    invoice_vals={
                        'origin',origin,
                        'date_due',date_due,
                        'check_total',check_total,
                        'reference',reference,
                        'supplier_invoice_number',supplier_invoice_number,
                        'number',number,
                        'fiscal_position',fiscal_position,
                        'reference_type',reference_type,
                        'amount_tax',amount_tax,
                        'state',state,
                        'type',type,
                        'internal_number',internal_number,
                        'reconciled',reconciled,
                        'residual',residual,
                        'amount_untaxed',amount_untaxed,
                        'date_invoice',date_invoice,
                        'amount_total',amount_total,
                        'name',name,
                        'comment',comment,
                        'sent',sent,
                        'auth_transaction_type',auth_transaction_type,
                        'cc_number',cc_number,
                        'auth_respmsg',auth_respmsg,
                        'authorization_code',authorization_code,
                        'authorization_code',authorization_code,
                        'capture_status',capture_status,
                        'is_suppressed',is_suppressed,
                        'is_printed',is_printed,
                        'event_start',event_start,
                        'c_csid',c_csid,
                        'is_silent',is_silent,
                        'is_notdiscount',is_notdiscount,
                        'is_invoice_nocalc',is_invoice_nocalc,
                        'is_invoice_nocalc',is_invoice_nocalc,
                        'quickbooks_id',quickbooks_id,
                        'invoice_ref',invoice_ref,
                        'claim_no',claim_no,
                        'check_no',check_no,
                        'department',department,
                        'approving_manager',approving_manager,
                        'nuid_code',nuid_code,
                        'sales_representative',sales_representative,
                        'gl_code',gl_code,
                        'invoice_for',invoice_for,
                        'approving_mgr',approving_mgr,
                        'is_emailed',is_emailed,
                        'is_mailed',is_mailed,
                        'is_faxed',is_faxed,
                        'is_monthly',is_monthly,
                        'event_type',event_type,
                        'month',month,
                        'year',year,
                        'cust_gpuid',cust_gpuid,
                        'cust_csid',cust_csid,
                        'ref',ref,
                        'internal_comment',internal_comment,
                    }

                    invoice_new_id=self.env['account.invoice'].create(invoice_vals)
                    #update invoice line
                    invoice_line_new_id=self.env['account.invoice.line'].search([('account_invoice_line_old_id','=',invoice_id)])
                    invoice_line_new_id.write({'invoice_id':invoice_new_id})
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
        self.upload_error2 = base64.encodestring(bytes(file_data))
        self.upload_error_file_name2 = 'Invoice Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }

# function to map zone many2many
    @api.multi
    def map_zone_and_zipcode(self):
        csv_datas = self.upload_file2
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
        zip_header = ''
        for row in lis:
            try:
                temp = 0
                if row_num == 0:
                    header = row
                else:
                    if not row:
                        continue
                    _logger.error('------------rown---------- %s', row_num)
                    zip_code = row[2].strip() or 0
                    if zip_code:
                        zone = row[1].strip() or 0
                        if zone:
                            zone_id = self.env['zone'].search([('zone_old_id', '=', zone)])
                            zip_code = row[2].strip() or 0
                            zip_code_id = self.env['zip.code'].search([('zip_code_old_id', '=', zip_code)])
                            if zone_id:
                                test = zone_id.write({'zip_code_ids': [(4, zip_code_id.id)]})
                                # print test
                        else:
                            # zip_code = row[2].strip()
                            zip_code_id = self.env['zip.code'].search([('zip_code_old_id', '=', zip_code)])
                            if not zone and zip_code_id:
                                zone_id.write({'zip_code_ids': [(4, zip_code_id.id)]})
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
        self.upload_error2 = base64.encodestring(bytes(file_data))
        self.upload_error_file_name2 = 'Mapping zone & zipcode Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }
