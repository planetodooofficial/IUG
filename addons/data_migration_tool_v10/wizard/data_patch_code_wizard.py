
from odoo import fields,models,api,_
import csv
import os
import StringIO
import logging
from tempfile import TemporaryFile
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.exceptions import UserError
import base64

_logger = logging.getLogger('patchcode_wiard')

class DataPatchCode(models.TransientModel):
    _name='data.patchcode.wizard'

    upload_file = fields.Binary(string='File URL')
    upload_error = fields.Binary(string='Click To Download Error Log')
    upload_error_file_name = fields.Char("File name")

    @api.multi
    def import_ir_attachment(self):
        error_list = []
        header_list = []
        path = '/home/iuadmin/ir_attachment'
        for filename in os.listdir(path):
            file_obj = path + '/' + filename
            _logger.error('------------file name---------- %s', file_obj)
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

                        _logger.error('------------row number---------- %s', key)
                        event_old_id = row[13].strip() or False
                        if event_old_id:
                            event_old_id = self.env['event'].search([('event_old_id', '=', int(event_old_id))],
                                                                    limit=1).id
                        company_id = row[4].strip() or False
                        if company_id:
                            company_id = self.env['res.company'].search([('res_company_old_id', '=', company_id)],
                                                                        limit=1).id
                        user_id = self.env['res.users'].search([('user_old_id', '=', int(row[1].strip()))], limit=1).id
                        old_res_id = int(row[7].strip()) if row[7].strip() else False
                        if old_res_id:
                            if row[3].strip():
                                if row[3].strip() == 'event':
                                    old_res_id = self.env[row[3].strip()].search([('event_old_id', '=', old_res_id)],
                                                                                 limit=1).id
                                elif row[3].strip() == 'select.interpreter.line':
                                    old_res_id = self.env[row[3].strip()].search(
                                        [('interpreter_line_old_id', '=', int(old_res_id))], limit=1).id
                                elif row[3].strip() == 'account.invoice':
                                    old_res_id = self.env[row[3].strip()].search(
                                        [('invoice_old_id', '=', int(old_res_id))],
                                        limit=1).id
                                elif row[3].strip() == 'project.task':
                                    old_res_id = self.env[row[3].strip()].search(
                                        [('project_task_old_id', '=', int(old_res_id))], limit=1).id
                                elif row[3].strip() == 'res.partner':
                                    old_res_id = self.env[row[3].strip()].search(
                                        [('customer_record_old_id', '=', int(old_res_id))], limit=1).id
                                elif row[3].strip() == 'patient':
                                    old_res_id = self.env[row[3].strip()].search(
                                        [('patient_old_id', '=', int(old_res_id))],
                                        limit=1).id
                                else:
                                    old_res_id = False
                            else:
                                old_res_id = False
                        res_model = row[3].strip() or ''
                        if not old_res_id:
                            res_model = False
                        # document_type_id = int(row[28].strip()) if row[28].strip() else False
                        # if document_type_id:
                        #     document_type_id = self.env['document.type'].search(
                        #         [('document_type_old_id', '=', document_type_id)], limit=1).id
                        # test=base64.b64encode((row[0]))
                        ir_attachment_vals = {
                            'name': row[9].strip() or '',
                            'datas_fname': row[2].strip() or '',
                            'res_model': res_model,
                            'res_id': old_res_id,
                            'create_uid': user_id,
                            'user_id': user_id,
                            'company_id': company_id,
                            'type': row[6].strip(),
                            'store_fname': row[8].strip() or '',
                            'index_content': row[12].strip() or '',
                            'attach': False if row[16].strip == 'f' else True,
                            'no_of_pages': int(row[14].strip()) if row[14].strip() else False,
                            'no_of_words': int(row[15].strip()) if row[15].strip() else False,
                            'event_id': event_old_id,
                            # 'in_fax_id' = fields.Many2one('incoming.fax', 'Incoming Fax')
                            # 'document_type_id': document_type_id,
                            'res_old_id': int(row[7].strip()) if row[7].strip() else False
                        }

                        attachment_id = self.env['ir.attachment'].create(ir_attachment_vals).id
                        if row[0]:
                            self._cr.execute(""" update ir_attachment set db_datas=%s where id =%s""",
                                             (row[0], attachment_id))
                        self._cr.commit()
                except Exception as e:
                    _logger.error('------------Error Exception---------- %s', e)
                    error_list.append(value)

        with open('/home/iuadmin/ir_attachment_error/ir_attachment_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

    #function to map interpreter line with event many2many field
    @api.multi
    def map_event_inter_line(self):
        error_list = []
        header_list = []
        file_obj = '/home/iuadmin/select_assign_rel.csv'
        lis=csv.reader(open(file_obj, 'rU'), delimiter=",")
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
                    row = value
                    _logger.error('------------row number---------- %s', key)
                    event_id = row[0].strip() or False
                    interpreter_line_old_id = row[1].strip() or False
                    if event_id:
                        self._cr.execute("select id from event where event_old_id=" + str(
                            event_id) + " limit 1")
                        event_id = self._cr.fetchone()
                        event_id = event_id and event_id[0] or False
                    if interpreter_line_old_id:
                        self._cr.execute("select id from select_interpreter_line where interpreter_line_old_id=" + str(
                            interpreter_line_old_id) + " limit 1")
                        interpreter_line_old_id = self._cr.fetchone()
                        interpreter_line_old_id = interpreter_line_old_id and interpreter_line_old_id[0] or False
                    if event_id and interpreter_line_old_id:
                        vals=(event_id,interpreter_line_old_id)
                        self._cr.execute(""" INSERT INTO select_assign_rel2 (wiz_id,interp_id) VALUES (%s,%s)""", vals)
                        self._cr.commit()
                    else:
                        _logger.error('--------Record missing-------- %s', key)
                        error_list.append(value)
            except Exception as e:
                self._cr.rollback()
                value.append(str(e))
                _logger.error('------------Error Exception---------- %s', e)
                error_list.append(value)

        with open('/home/iuadmin/map_event_inter_line.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

    @api.multi
    def map_event_translator_line(self):
        error_list = []
        header_list = []
        file_obj = '/home/iuadmin/select_translator_rel.csv'
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
                    row = value
                    _logger.error('------------row number---------- %s', key)
                    event_id = row[0].strip() or False
                    translator_line_id = row[1].strip() or False
                    if event_id:
                        self._cr.execute("select id from event where event_old_id=" + str(
                            event_id) + " limit 1")
                        event_id = self._cr.fetchone()
                        event_id = event_id and event_id[0] or False
                    if translator_line_id:
                        self._cr.execute("select id from select_translator_line where translator_line_old_id=" + str(
                            translator_line_id) + " limit 1")
                        translator_line_id = self._cr.fetchone()
                        translator_line_id = translator_line_id and translator_line_id[0] or False
                    if event_id and translator_line_id:
                        vals = (event_id, translator_line_id)
                        self._cr.execute(""" INSERT INTO select_translator_rel (wiz_id,translator_id) VALUES (%s,%s)""", vals)
                        self._cr.commit()
                    else:
                        _logger.error('--------Record missing-------- %s', key)
                        error_list.append(value)
            except Exception as e:
                self._cr.rollback()
                value.append(str(e))
                _logger.error('------------Error Exception---------- %s', e)
                error_list.append(value)

        with open('/home/iuadmin/select_translator_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

    @api.multi
    def map_event_assigned_interpreters(self):
        error_list = []
        header_list = []
        file_obj = '/home/iuadmin/event_assigned_interpreters.csv'
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
                    row = value
                    _logger.error('------------row number---------- %s', key)
                    event_id = row[0].strip() or False
                    if event_id:
                        self._cr.execute("select id from event where event_old_id=" + str(
                            event_id) + " limit 1")
                        event_id = self._cr.fetchone()
                        event_id = event_id and event_id[0] or False
                    interpreter_id = row[1].strip() or False
                    if interpreter_id:
                        self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                            interpreter_id) + " limit 1")
                        interpreter_id = self._cr.fetchone()
                        interpreter_id = interpreter_id and interpreter_id[0] or False
                    if event_id and interpreter_id:
                        vals = (event_id, interpreter_id)
                        self._cr.execute(""" INSERT INTO event_partner_rel (event_id,interpreter_id) VALUES (%s,%s)""",
                                         vals)
                        self._cr.commit()
                    else:
                        _logger.error('--------Record missing-------- %s', key)
                        error_list.append(value)
            except Exception as e:
                _logger.error('------------Error Exception---------- %s', e)
                self._cr.rollback()
                value.append(str(e))
                error_list.append(value)

        with open('/home/iuadmin/event_assigned_interpreters_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

    @api.multi
    def map_event_invoice(self):
        error_list = []
        header_list = []
        file_obj = '/home/iuadmin/event_invoice_interpreters.csv'
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
                    row = value
                    _logger.error('------------row number---------- %s', key)
                    event_old_id = row[0].strip() or 0
                    event_id = self.env['event'].search([('event_old_id', '=', int(event_old_id))], limit=1).id
                    invoice = row[1].strip() or ''
                    if invoice:
                        invoice_id = self.env['account.invoice'].search([('invoice_old_id', '=', invoice)],
                                                                        limit=1).id
                    else:
                        invoice_id = False
                    if event_old_id and invoice_id:
                        vals = (event_id, invoice_id)
                        self._cr.execute(""" INSERT INTO task_inv_rel (event_id,invoice_id) VALUES (%s,%s)""",
                                         vals)
                        self._cr.commit()
                    else:
                        _logger.error('--------Record missing-------- %s', key)
                        error_list.append(value)
            except Exception as e:
                _logger.error('------------Error Exception---------- %s', e)
                error_list.append(value)

        with open('/home/iuadmin/event_invoice_interpreters_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

    @api.multi
    def import_invoice(self):
        error_list = []
        header_list = []
        # path = '/home/abhishek/Desktop/IUG_master_data/invoice'
        path = '/home/iuadmin/invoices'
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
                        _logger.error('------------Current Progress---------- %s', key)
                        invoice_old_id= row[0].strip() or False
                        origin = row[5].strip() or ''
                        date_due = row[6].strip() or 0
                        # check_total = row[7].strip() or 0
                        reference = row[8].strip() or ''
                        # supplier_invoice_number = row[9].strip() or ''
                        number = row[10].strip() or 0
                        account_id = row[11].strip() or False
                        company_id = row[12].strip() or False
                        if company_id:
                            company_id = self.env['res.company'].search([('res_company_old_id', '=', company_id)],
                                                                        limit=1).id
                        else:
                            company_id = False
                        type = row[23].strip() or ''
                        if account_id:
                            self._cr.execute("select id from account_account where account_old_id=" + str(
                                account_id) + " limit 1")
                            account_id = self._cr.fetchone()
                            account_id = account_id and account_id[0] or False


                        # currency_id = row[13].strip() or 0
                        partner_id = row[14].strip() or False
                        if partner_id:
                            self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                                partner_id) + " limit 1")
                            partner_id = self._cr.fetchone()
                            partner_id = partner_id and partner_id[0] or False
                        fiscal_position = row[15].strip() or False
                        #fixit
                        user_id = row[16].strip() or False
                        if user_id:
                            self._cr.execute("select id from res_users where user_old_id=" + str(
                                user_id) + " limit 1")
                            user_id = self._cr.fetchone()
                            user_id = user_id and user_id[0] or False
                        # partner_bank_id = row[17].strip() or 0 empty
                        payment_term = row[18].strip() or False
                        #pt match with server
                        reference_type = row[19].strip() or ''
                        journal_id = row[20].strip() or False
                        if journal_id:
                            self._cr.execute("select id from account_journal where account_journal_old_id=" + str(
                                journal_id) + " limit 1")
                            journal_id = self._cr.fetchone()
                            journal_id = journal_id and journal_id[0] or False
                        amount_tax = row[21].strip() or 0
                        # state = row[22].strip() or ''
                        # internal_number = row[24].strip() or ''
                        reconciled = row[25].strip() or ''  # boolean
                        residual = row[26].strip() or 0
                        move_name = row[27].strip() or ''
                        date_invoice = row[28].strip() or 0
                        period_id = row[29].strip() or False
                        if period_id:
                            self._cr.execute("select id from account_period where period_old_id=" + str(
                                period_id) + " limit 1")
                            period_id = self._cr.fetchone()
                            period_id = period_id and period_id[0] or False
                        amount_untaxed = row[30].strip() or 0
                        # move_id = row[31].strip() or 0  #journal
                        amount_total = row[32].strip() or ''
                        name = row[33].strip() or ''
                        comment = row[34].strip() or ''
                        sent = row[35].strip() or ''  # boolean
                        commercial_partner_id = row[36].strip() or False #respartner
                        if commercial_partner_id:
                            self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                                commercial_partner_id) + " limit 1")
                            commercial_partner_id = self._cr.fetchone()
                            commercial_partner_id = commercial_partner_id and commercial_partner_id[0] or False
                        # auth_transaction_type = row[37].strip() or ''
                        # customer_payment_profile_id = row[38].strip() or ''  NA
                        # cc_number = row[39].strip() or ''
                        # auth_respmsg = row[40].strip() or ''
                        # authorization_code = row[41].strip() or ''
                        # capture_status = row[42].strip() or ''
                        # invoice_original_id = row[43].strip() or 0 less record
                        # auth_transaction_id = row[44].strip() or '' #NA
                        # customer_profile_id = row[45].strip() or '' empty
                        # amount_charged = row[46].strip() or 0
                        # section_id = row[47].strip() or 0 empty

                        contact_id = row[49].strip() or False #respartner
                        if contact_id:
                            self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                                contact_id) + " limit 1")
                            contact_id = self._cr.fetchone()
                            contact_id = contact_id and contact_id[0] or False
                        language_id = row[50].strip() or False
                        if language_id:
                            self._cr.execute("select id from language where language_old_id=" + str(
                                language_id) + " limit 1")
                            language_id = self._cr.fetchone()
                            language_id = language_id and language_id[0] or False
                        # is_suppressed = row[51].strip() or ''  # boolean
                        is_printed = row[52].strip() or ''  # boolean
                        # c_gpuid = row[53].strip() or ''
                        # event_start = row[54].strip() or ''  # time
                        # c_csid = row[55].strip() or ''
                        ordering_contact_id = row[56].strip() or False
                        if ordering_contact_id:
                            self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                                ordering_contact_id) + " limit 1")
                            ordering_contact_id = self._cr.fetchone()
                            ordering_contact_id = ordering_contact_id and ordering_contact_id[0] or False
                        # entered_by_staffid = row[57].strip() or 0
                        # project_name = row[58].strip() or ''
                        # is_posted = row[59].strip() or ''  # boolean
                        # interpreter_id = row[60].strip() or 0 #NA
                        # is_silent = row[61].strip() or ''  # boolean
                        # event_end = row[62].strip() or ''  # time
                        ordering_partner_id = row[63].strip() or False
                        if ordering_partner_id:
                            self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                                ordering_partner_id) + " limit 1")
                            ordering_partner_id = self._cr.fetchone()
                            ordering_partner_id = ordering_partner_id and ordering_partner_id[0] or False

                        # is_notdiscount = row[64].strip() or ''  # boolean
                        # posted_by_staffid = row[65].strip() or 0
                        event_id = row[66].strip() or False
                        if event_id:
                            self._cr.execute("select id from event where event_old_id=" + str(
                                event_id) + " limit 1")
                            event_id = self._cr.fetchone()
                            event_id = event_id and event_id[0] or False
                        location_id = row[67].strip() or False
                        if location_id:
                            self._cr.execute("select id from location where location_old_id=" + str(
                                location_id) + " limit 1")
                            location_id = self._cr.fetchone()
                            location_id = location_id and location_id[0] or False

                        # is_invoice_nocalc = row[68].strip() or ''  # boolean
                        # translator_id = row[69].strip() or 0 #NA
                        quickbooks_id = row[70].strip() or '' #CHAR
                        doctor_id = row[71].strip() or False
                        if doctor_id:
                            self._cr.execute("select id from doctor where doctor_old_id=" + str(
                                doctor_id) + " limit 1")
                            doctor_id = self._cr.fetchone()
                            doctor_id = doctor_id and doctor_id[0] or False
                        # transporter_id = row[72].strip() or 0
                        invoice_id2 = row[73].strip() or 0 #INT
                        invoice_ref = row[74].strip() or 0
                        claim_no = row[75].strip() or ''
                        check_no = row[76].strip() or ''
                        invoice_id = row[77].strip() or 0 #INT
                        patient_id = row[78].strip() or False
                        if patient_id:
                            self._cr.execute("select id from patient where patient_old_id=" + str(
                                patient_id) + " limit 1")
                            patient_id = self._cr.fetchone()
                            patient_id = patient_id and patient_id[0] or False

                        # department = row[79].strip() or ''
                        # approving_manager = row[80].strip() or ''
                        # nuid_code = row[81].strip() or ''
                        sales_representative = row[82].strip() or 0
                        # gl_code = row[83].strip() or ''
                        project_name_id = row[84].strip() or False
                        if project_name_id:
                            self._cr.execute("select id from project where iug_project_old_id=" + str(
                                project_name_id) + " limit 1")
                            project_name_id = self._cr.fetchone()
                            project_name_id = project_name_id and project_name_id[0] or False
                        invoice_for = row[85].strip() or ''
                        sales_representative_id = row[86].strip() or False
                        if sales_representative_id:
                            self._cr.execute("select id from res_users where user_old_id=" + str(
                                sales_representative_id) + " limit 1")
                            sales_representative_id = self._cr.fetchone()
                            sales_representative_id = sales_representative_id and sales_representative_id[0] or False


                        # scheduler_id = row[87].strip() or 0
                        # approving_mgr = row[88].strip() or '' #NA
                        is_emailed = row[89].strip() or ''  # boolean
                        is_mailed = row[90].strip() or ''  # boolean
                        is_faxed = row[91].strip() or ''  # boolean
                        is_monthly = row[92].strip() or ''  # boolean
                        # event_type = row[93].strip() or ''
                        month = row[94].strip() or ''
                        # cust_gpuid = row[95].strip() or ''
                        year = row[96].strip() or ''
                        # cust_csid = row[97].strip() or ''
                        # event_start_date = row[98].strip() or 0  # date
                        # ref = row[99].strip() or ''
                        internal_comment = row[100].strip() or ''
                        # state_name_related = row[101].strip() or 0
                        if partner_id:
                            invoice_vals = {
                                'month':month,
                                'year':year,
                                'invoice_old_id': invoice_old_id,
                                'origin': origin,
                                'date_due': date_due,
                                'reference': reference,
                                'sales_representative_id': sales_representative_id,
                                'invoice_old_number': number,
                                'account_id': account_id,
                                # 'invoice_id2': invoice_id2,
                                'patient_id': patient_id,
                                'company_id': company_id,
                                'currency_id': 3,
                                'partner_id': partner_id,
                                'doctor_id': doctor_id,
                                'fiscal_position_id': fiscal_position,
                                'user_id': user_id,
                                'payment_term_id': payment_term,
                                'reference_type': reference_type,
                                'ordering_partner_id': ordering_partner_id,
                                'period_id': period_id,
                                'journal_id': journal_id,
                                'location_id': location_id,
                                # 'amount_tax': amount_tax,
                                'type': type,
                                'event_id': event_id,
                                'reconciled': reconciled,
                                'residual': residual,
                                'move_name': move_name,
                                # 'amount_untaxed': amount_untaxed,
                                'date_invoice': date_invoice,
                                # 'amount_total': amount_total,
                                'name': name,
                                'ordering_contact_id' :ordering_contact_id,
                                'comment':comment ,
                                'sent': sent,
                                'commercial_partner_id': commercial_partner_id,
                                'is_printed': is_printed,
                                # 'quickbooks_id': quickbooks_id,
                                'claim_no': claim_no,
                                'check_no': check_no,
                                'invoice_for': invoice_for,
                                'is_emailed': is_emailed,
                                'is_mailed': is_mailed,
                                'is_faxed': is_faxed,
                                'is_monthly': is_monthly,
                                'internal_comment': internal_comment,
                                # 'invoice_id': invoice_id,
                                'contact_id': contact_id,
                                'language_id': language_id,
                                'project_name_id':project_name_id,
                            }
                            invoice_new_id=self.env['account.invoice'].search([('invoice_old_id','=',invoice_old_id)],limit=1)
                            if not invoice_new_id:
                                invoice_new_id = self.env['account.invoice'].create(invoice_vals)
                            else:
                                invoice_new_id.write(invoice_vals)
                            self._cr.commit()
                        else:

                            _logger.error('---------missing partner----------')
                            error_list.append(value)
                except Exception as e:
                    _logger.error('------------error log_id exception---------- %s', e)
                    value.append(str(e))
                    error_list.append(value)
                # with open('/home/abhishek/Desktop/output.csv', 'wb') as f:
        with open('/home/iuadmin/cust_upload_err/invoice_upload_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

    @api.multi
    def import_account_invoice_line(self):
        error_list = []
        header_list = []
        # path = '/home/abhishek/Desktop/IUG_master_data/invoice'
        path = '/home/iuadmin/ac_invoice_line'
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
                        _logger.error('---current progress -- %s -- sheet--%s', key,filename)
                        invoice_line_old_id = row[0].strip() or ''
                        company_id = row[13].strip() or False
                        if company_id:
                            company_id = self.env['res.company'].search([('res_company_old_id', '=', company_id)],limit=1).id
                        # if account_id and company_id:
                        #     account_id=self.env['account.account'].search([('code','=','101200'),('company_id','=',company_id)]).id
                        # else:
                        #     account_id=False

                        account_id = row[7].strip() or False
                        if account_id:
                            self._cr.execute("select id from account_account where account_old_id=" + str(
                                account_id) + " limit 1")
                            account_id = self._cr.fetchone()
                            account_id = account_id and account_id[0] or False
                        name = row[8].strip() or ''
                        sequence = row[9].strip() or ''
                        invoice_id = row[10].strip() or False
                        if invoice_id:
                            self._cr.execute("select id from account_invoice where invoice_old_id=" + str(
                                invoice_id) + " limit 1")
                            invoice_id = self._cr.fetchone()
                            invoice_id = invoice_id and invoice_id[0] or False
                        price_unit = row[11].strip() or ''
                        price_subtotal = row[12].strip() or ''
                        discount = row[14].strip() or ''
                        # account_analytic_id = row[15].strip() or ''#null
                        quantity = row[16].strip() or ''
                        partner_id = row[17].strip() or False
                        if partner_id:
                            self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                                partner_id) + " limit 1")
                            partner_id = self._cr.fetchone()
                            partner_id = partner_id and partner_id[0] or False
                        product_id = row[18].strip() or ''
                        if product_id:
                            self._cr.execute("select id from product_product where product_old_id=" + str(
                                product_id) + " limit 1")
                            product_id = self._cr.fetchone()
                            product_id = product_id and product_id[0] or False
                        # mileage_bill_rate = row[19].strip() or ''
                        # miles_pay_rate = row[20].strip() or ''
                        # amount_to_pay = row[21].strip() or ''
                        # mileage_pay_rate = row[22].strip() or ''
                        miscellaneous_bill = row[23].strip() or ''
                        # travel_pay_amount = row[24].strip() or ''
                        # mileage_to_pay = row[25].strip() or ''
                        # travel_bill_amount = row[26].strip() or ''
                        miles_driven = row[27].strip() or ''
                        # mileage_to_bill = row[28].strip() or ''
                        inc_min = row[29].strip() or ''
                        mileage = row[30].strip() or ''
                        mileage_rate = row[31].strip() or ''
                        pickup_fee = row[32].strip() or ''
                        after_hours = row[33].strip() or ''
                        gratuity = row[34].strip() or ''
                        wait_time = row[35].strip() or ''
                        event_out_come_id = row[36].strip() or ''
                        if event_out_come_id:
                            event_out_come_id=self.env['event.out.come'].search([('event_outcome_old_id','=',event_out_come_id)],limit=1).id
                        else:
                            event_out_come_id=False
                        task_line_id = row[37].strip() or False
                        if task_line_id:
                            self._cr.execute("select id from project_task_work where project_task_work_old_id=" + str(
                                task_line_id) + " limit 1")
                            task_line_id = self._cr.fetchone()
                            task_line_id = task_line_id and task_line_id[0] or False
                        travel_time = row[38].strip() or ''
                        total_editable = row[39].strip() or ''
                        travelling_rate = row[40].strip() or ''
                        if invoice_id:
                            invoice_line_vals = {
                                'invoice_line_old_id': invoice_line_old_id,
                                'account_id': account_id,
                                'name': name,
                                'sequence': sequence,
                                'invoice_id': invoice_id,
                                'price_unit': price_unit,
                                'price_subtotal': price_subtotal,
                                'company_id': company_id,
                                'discount': discount,
                                'quantity': quantity,
                                'partner_id': partner_id,
                                'product_id': product_id,
                                'miscellaneous_bill': miscellaneous_bill,
                                'miles_driven': miles_driven,
                                'inc_min': inc_min,
                                'mileage': mileage,
                                'mileage_rate': mileage_rate,
                                'pickup_fee': pickup_fee,
                                'after_hours': after_hours,
                                'gratuity': gratuity,
                                'wait_time': wait_time,
                                'event_out_come_id': event_out_come_id,
                                'task_line_id': task_line_id,
                                'travel_time': travel_time,
                                'total_editable': total_editable,
                                'travelling_rate': travelling_rate,
                            }
                            invoice_line_new_id = self.env['account.invoice.line'].search([('invoice_line_old_id','=',invoice_line_old_id)],limit=1)
                            if not invoice_line_new_id:
                                invoice_line_new_id = self.env['account.invoice.line'].create(invoice_line_vals)
                            else:
                                invoice_line_new_id.write(invoice_line_vals)
                            self._cr.commit()
                        else:
                            _logger.error('---Invoice not Found!!!-----')
                            error_list.append(value)

                except Exception as e:
                    _logger.error('------------error log_id exception---------- %s', e)
                    value.append(str(e))
                    error_list.append(value)
        # with open('/home/abhishek/Desktop/output.csv', 'wb') as f:
        with open('/home/iuadmin/cust_upload_err/invoice_line_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

    # function to import billing form
    @api.multi
    def import_billing_form(self):
        error_list = []
        header_list = []
        total_row = 0
        # file path should be server file path in server
        path = '/home/iuadmin/billing_form'
        # path = '/home/iuadmin/select_interpreter_line'
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
                        _logger.error('----------Row Number---------- %s', key)
                        billing_form_old_id= value[0].strip() or 0
                        bill_obj = self.env['billing.form'].search([('billing_form_old_id','=',billing_form_old_id)],limit=1)
                        if not bill_obj:
                            cust_invoice = value[5].strip() or False
                            if cust_invoice:
                                cust_invoice_id = self.env['account.invoice'].search([('invoice_old_id','=',cust_invoice)],limit=1).id
                            else:
                                cust_invoice_id = False

                            supp_invoice = value[10].strip() or ''
                            if supp_invoice:
                                supp_invoice_id2 = self.env['account.invoice'].search([('invoice_old_id','=',supp_invoice)],limit=1).id
                            else:
                                supp_invoice_id2 = False
                            event_line = value[24].strip() or ''
                            if event_line:
                                event_line_id = self.env['event.lines'].search([('event_lines_old_id','=',event_line)],limit=1).id
                            else:
                                event_line_id = False
                            user = value[7].strip() or ''
                            if user:
                                user_id = self.env['res.users'].search([('user_old_id','=',user)],limit=1).id
                            else:
                                user_id = False
                            event = value[13].strip() or ''
                            if event:
                                event_id = self.env['event'].search([('event_old_id','=',event)],limit=1).id
                            else:
                                event_id = False
                            company = value[9].strip() or ''
                            if company:
                                company_id = self.env['res.company'].search([('res_company_old_id','=',company)],limit=1).id
                            else:
                                company_id = False
                            selected_event = value[22].strip() or ''
                            if selected_event:
                                selected_event_id = self.env['event'].search([('event_old_id','=',selected_event)],limit=1).id
                            else:
                                selected_event_id = False
                            billing_form_vals = {
                                                'billing_form_old_id': value[0].strip() or 0,
                                                'cust_invoice_id': cust_invoice_id,
                                                'job_comment': value[25].strip() or '',
                                                'supp_invoice_id2': supp_invoice_id2,
                                                'event_comment': value[26].strip() or '',
                                                'event_line_id': event_line_id,
                                                'emergency_rate': value[30].strip() or False,
                                                'billing_comment': value[27].strip() or '',
                                                'event_end_min': int(value[12].strip()) if value[12].strip() else 0,
                                                'user_id': user_id,
                                                'event_id': event_id,
                                                'company_id': company_id,
                                                'event_start': value[15].strip() or False,
                                                'event_end':  value[14].strip() or False,
                                                'customer_timezone': value[16].strip() or '',
                                                'event_start_min': int(value[17].strip() ) if value[17].strip() else 0,
                                                'invoice_date': value[29].strip() or False,
                                                'event_start_hr': int(value[18].strip()) if value[18].strip() else 0,
                                                'event_end_hr':int(value[19].strip()) if value[19].strip()  else 0,
                                                'name':  value[8].strip() or '',
                                                'invoices_created': value[28].strip() or False,
                                                'am_pm': value[20].strip() or '',
                                                'invoice_exist': value[21].strip() or  False,
                                                'selected_event_id': selected_event_id,
                                                'am_pm2': value[11].strip() or '',
                                                'event_start_date': value[23].strip() or False,

                                                }

                            billing_form_new_id = self.env['billing.form'].create(billing_form_vals)
                            self._cr.commit()
                        else:
                            _logger.error('------already updated------')

                except Exception as e:
                    _logger.error('------------error log_id exception---------- %s', e)
                    error_list.append(value)
        # with open('/home/iuadmin/select_interpreter_line_error.csv', 'wb') as f:
        with open('/home/iuadmin/billing_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()


    # function to import account.journal
    @api.multi
    def import_account_journal(self):
        csv_datas = self.upload_file
        if not csv_datas:
            raise UserError(_("Choose the file before uploading!!!"))

        fileobj = TemporaryFile('w+')
        fileobj.write(base64.decodestring(csv_datas))
        fileobj.seek(0)
        str_csv_data = fileobj.read()
        lis = csv.reader(StringIO.StringIO(str_csv_data), delimiter=',')
        row_num = 0
        error_list = []
        header_list = []
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
                    row = value
                    _logger.error('----------Row Number---------- %s', key)

                    account_journal_old_id = row[0].strip()
                    code = row[6].strip()
                    company = row[20].strip()
                    if company:
                        company_id = self.env['res.company'].search([('res_company_old_id', '=', company)]).id
                    else:
                        company_id = False
                    journal_obj = self.env['account.journal'].search([('code','=',code),('company_id','=',company_id)])
                    if not journal_obj:
                        group_invoice_lines = row[18].strip()

                        profit_account = row[22].strip()
                        if profit_account:
                            profit_account_id = self.env['account.account'].search([('account_old_id','=',profit_account)],limit=1).id
                        else:
                            profit_account_id = False
                        default_debit_account = row[5].strip()
                        if default_debit_account:
                            default_debit_account_id = self.env['account.account'].search([('account_old_id','=',default_debit_account)],limit=1).id
                        else:
                            default_debit_account_id = False
                        default_credit_account = row[7].strip()
                        if default_credit_account:
                            default_credit_account_id = self.env['account.account'].search([('account_old_id','=',default_credit_account)],limit=1).id
                        else:
                            default_credit_account_id = False
                        loss_account = row[8].strip()
                        if loss_account:
                            loss_account_id = self.env['account.account'].search([('account_old_id','=',loss_account)],limit=1).id
                        else:
                            loss_account_id = False
                        update_posted = row[13].strip()
                        name = row[15].strip()
                        type = row[24].strip()
                        if type not in ['sale','purchase','cash','bank']:
                            type='general'
                        else:
                            type=type
                        show_hide = row[28].strip()

                        account_journal_vals = {
                            'account_journal_old_id': account_journal_old_id,
                            'code': code,
                            'currency_id': 3,
                            'group_invoice_lines': True if group_invoice_lines=='t' else False,
                            'company_id': company_id,
                            'profit_account_id': profit_account_id,
                            'default_debit_account_id': default_debit_account_id,
                            'default_credit_account_id': default_credit_account_id,
                            'loss_account_id': loss_account_id,
                            'update_posted': True if update_posted=='t' else False,
                            'name': name,
                            'type': type,
                            'show_hide': True if show_hide=='t' else False,
                        }

                        account_journal_new_id = self.env['account.journal'].create(account_journal_vals)
                        # /self._cr.commit()
                    else:
                        _logger.error('-----already present------')
            except Exception as e:
                _logger.error('------------Error Exception---------- %s', key)
                error_list.append(value)
        csvfile = StringIO.StringIO()
        w = csv.writer(csvfile, delimiter=',')
        w.writerow(header_list)
        w.writerows(error_list)
        file_data = csvfile.getvalue()
        self.upload_error = base64.encodestring(bytes(file_data))
        self.upload_error_file_name = 'journal Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }

# function to import event.line
    @api.multi
    def import_event_line(self):
        error_list = []
        header_list = []
        total_row = 0
        # file path should be server file path in server
        path = '/home/iuadmin/event_line'
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
                        _logger.error('----------Row Number---------- %s', key)
                        event_lines_old_id=value[0].strip()
                        event_line_obj=self.env['event.lines'].search([('event_lines_old_id','=',event_lines_old_id)],limit=1)
                        if not event_line_obj:
                            billing_form = value[5].strip() or ''
                            if billing_form:
                                billing_form_id = self.env['billing.form'].search([('billing_form_old_id','=',billing_form)],limit=1).id
                            else:
                                billing_form_id = False
                            event = value[9].strip() or ''
                            if event:
                                event_id = self.env['event'].search([('event_old_id','=',event)],limit=1).id
                            else:
                                event_id = False
                            user_id=value[7].strip() or False
                            if user_id:
                                user_id= self.env['res.users'].search([('user_old_id','=',user_id)],limit=1).id
                            event_line_vals = {
                                                'event_lines_old_id':value[0].strip(),
                                                'billing_form_id': billing_form_id,
                                                'name': value[11].strip() or '',
                                                'event_id': event_id,
                                                'selected': value[14].strip() or False,
                                                'event_type': value[8].strip(),
                                                'event_start_time': value[12].strip(),
                                                'user_id': user_id,
                                                'event_end_time': value[13].strip(),
                                                'event_start_date': value[6].strip(),
                                            }
                            event_line_new_id = self.env['event.lines'].create(event_line_vals)
                            self._cr.commit()
                        else:
                            _logger.error('-----Already added-------')
                except Exception as e:
                    _logger.error('------------error log_id exception---------- %s', e)
                    error_list.append(value)
            os.remove(file_obj)
        with open('/opt/home/iuadmin/uploading_error/event_line_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()



#function to import account period
    @api.multi
    def import_account_period(self):
        csv_datas = self.upload_file
        if not csv_datas:
            raise UserError(_("Choose the file before uploading!!!"))

        fileobj = TemporaryFile('w+')
        fileobj.write(base64.decodestring(csv_datas))
        fileobj.seek(0)
        str_csv_data = fileobj.read()
        lis = csv.reader(StringIO.StringIO(str_csv_data), delimiter=',')
        row_num = 0
        error_list = []
        header_list = []
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
                    row = value
                    _logger.error('----------Row Number---------- %s', key)
                    period_old_id = row[0].strip()
                    date_stop = row[5].strip() or ''
                    if date_stop:
                        date_stop = datetime.strptime(date_stop, "%Y-%m-%d").strftime(DF)
                    else:
                        date_stop = False
                    code = row[6].strip() or ''
                    name = row[7].strip() or ''
                    state = row[11].strip() or ''
                    date_start = row[8].strip() or ''
                    if date_start:
                        date_start = datetime.strptime(date_start, "%Y-%m-%d").strftime(DF)
                    else:
                        date_start = False
                    company_id = row[10].strip() or ''
                    if company_id:
                        company_id = self.env['res.company'].search([('res_company_old_id', '=', company_id)],limit=1).id
                    else:
                        company_id = False
                    fiscalyear_id = row[9].strip() or ''
                    if fiscalyear_id:
                        fiscalyear_id=self.env['account.fiscalyear'].search([('account_fiscalyear_old_id','=',fiscalyear_id)],limit=1).id
                    else:
                        fiscalyear_id=False
                    special = row[12].strip() or ''
                    period_vals = {
                        'period_old_id':int(period_old_id),
                        'date_stop':date_stop,
                        'code':code,
                        'name':name,
                        'state':state,
                        'date_start':date_start,
                        'company_id':company_id,
                        'fiscalyear_id':fiscalyear_id,
                        'special':True if special=='t' else False
                    }
                    period_new_id = self.env['account.period'].create(period_vals)

            except Exception as e:
                _logger.error('------------Error Exception---------- %s', key)
                error_list.append(value)
        csvfile = StringIO.StringIO()
        w = csv.writer(csvfile, delimiter=',')
        w.writerow(header_list)
        w.writerows(error_list)
        file_data = csvfile.getvalue()
        self.upload_error = base64.encodestring(bytes(file_data))
        self.upload_error_file_name = 'period Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
                    }
    @api.multi
    def import_account_fiscalyear(self):
        csv_datas = self.upload_file
        if not csv_datas:
            raise UserError(_("Choose the file before uploading!!!"))
        fileobj = TemporaryFile('w+')
        fileobj.write(base64.decodestring(csv_datas))
        fileobj.seek(0)
        str_csv_data = fileobj.read()
        lis = csv.reader(StringIO.StringIO(str_csv_data), delimiter=',')
        row_num = 0
        error_list = []
        header_list = []
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
                    row = value
                    _logger.error('------------rown---------- %s', key)
                    account_fiscalyear_old_id = row[0].strip()
                    date_stop = row[5].strip() or ''
                    if date_stop:
                        date_stop = datetime.strptime(date_stop, "%Y-%m-%d").strftime(DF)
                    else:
                        date_stop = False
                    code = row[6].strip() or ''
                    name = row[7].strip() or ''
                    state = row[11].strip() or ''
                    date_start = row[9].strip() or ''
                    if date_start:
                        date_start = datetime.strptime(date_start, "%Y-%m-%d").strftime(DF)
                    else:
                        date_start = False
                    company_id = row[10].strip() or ''
                    if company_id:
                        company_id = self.env['res.company'].search([('res_company_old_id', '=', company_id)],limit=1).id
                    else:
                        company_id = False
                    fiscalyear_vals = {
                        'account_fiscalyear_old_id':int(account_fiscalyear_old_id),
                        'date_stop':date_stop,
                        'code':code,
                        'name':name,
                        'state':state,
                        'date_start':date_start,
                        'company_id':company_id,
                    }
                    fiscalyear_vals_new_id = self.env['account.fiscalyear'].create(fiscalyear_vals)

            except Exception as e:
                _logger.error('------------Error Exception---------- %s', key)
                error_list.append(value)
        csvfile = StringIO.StringIO()
        w = csv.writer(csvfile, delimiter=',')
        w.writerow(header_list)
        w.writerows(error_list)
        file_data = csvfile.getvalue()
        self.upload_error = base64.encodestring(bytes(file_data))
        self.upload_error_file_name = 'Fiscal Year Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
                    }

        # function to import account.account
    @api.multi
    def import_account(self):
        csv_datas = self.upload_file
        if not csv_datas:
            raise UserError(_("Choose the file before uploading!!!"))
        fileobj = TemporaryFile('w+')
        fileobj.write(base64.decodestring(csv_datas))
        fileobj.seek(0)
        str_csv_data = fileobj.read()
        lis = csv.reader(StringIO.StringIO(str_csv_data), delimiter=',')
        row_num = 0
        error_list = []
        header_list = []
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
                    row = value
                    _logger.error('----------Row Number---------- %s', key)
                    name = row[12].strip()
                    account_old_id = row[0].strip()
                    code = row[7].strip()
                    company = row[14].strip()
                    if company:
                        company_id = self.env['res.company'].search([('res_company_old_id', '=', company)]).id
                    else:
                        company_id = False
                    acc_obj=self.env['account.account'].search([('code','=',code),('company_id','=',company_id)])
                    if not acc_obj:
                        note = row[16].strip()

                        # currency_id = row[0].strip() #always 3

                        user_type_old_id = row[10].strip()
                        user_type_id=0
                        user_type_old_id=int(user_type_old_id)
                        if user_type_old_id in [20, 2]:
                            user_type_id = 1
                        elif user_type_old_id in [25, 3]:
                            user_type_id = 2
                        elif user_type_old_id in [19, 5, 4]:
                            user_type_id = 3
                        elif user_type_old_id == 26:
                            user_type_id = 4
                        elif user_type_old_id == 18:
                            user_type_id = 5
                        elif user_type_old_id in [21, 17, 24, 27]:
                            user_type_id = 6
                        elif user_type_old_id == 16:
                            user_type_id = 7
                        elif user_type_old_id in [6, 12, 18, 22]:
                            user_type_id = 8
                        elif user_type_old_id in [7, 13, 28, 30, 14]:
                            user_type_id = 9
                        elif user_type_old_id == 29:
                            user_type_id = 10
                        elif user_type_old_id in [31, 15]:
                            user_type_id = 11
                        elif user_type_old_id in [1, 10, 33]:
                            user_type_id = 13
                        elif user_type_old_id in [32, 8]:
                            user_type_id = 14
                        elif user_type_old_id == 23:
                            user_type_id = 15
                        elif user_type_old_id in [9, 11, 34, 35]:
                            user_type_id = 16
                        elif user_type_old_id == 36:
                            user_type_id = 17
                        else:
                            _logger.error('---account type goes wrong-----')
                            error_list.append(value)
                        reconcile = row[8].strip()
                        account_vals = {
                            'account_old_id': account_old_id,
                            'note': note,
                            'name': name,
                            'company_id': company_id,
                            'currency_id': 3,
                            'code': code,
                            'user_type_id': user_type_id,
                            'reconcile': True if reconcile=='t' or user_type_id in [1, 2]  else False,
                        }

                        account_new_id = self.env['account.account'].create(account_vals)
                    else:
                        _logger.error('---account already exist----name: %s',acc_obj.name)
                        acc_obj.write({'account_old_id':account_old_id})
            except Exception as e:
                _logger.error('------------Error Exception---------- %s', key)
                error_list.append(value)
        csvfile = StringIO.StringIO()
        w = csv.writer(csvfile, delimiter=',')
        w.writerow(header_list)
        w.writerows(error_list)
        file_data = csvfile.getvalue()
        self.upload_error = base64.encodestring(bytes(file_data))
        self.upload_error_file_name = 'COA Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }

    @api.multi
    def update_customer_account(self):
        error_list = []
        header_list = []
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
                        header_list.append(value)
                    else:
                        row = value
                        customer_record_old_id = row[0].strip() or 0
                        cut_ob = self.env['res.partner'].search([('customer_record_old_id', '=', customer_record_old_id)])
                        if not cut_ob:
                            _logger.error('------------rown---------- %s', key)
                            company = row[14].strip() or False
                            if company:
                                company_id = self.env['res.company'].search([('res_company_old_id', '=', company)]).id

                except Exception as e:
                    _logger.error('------------Error Exception---------- %s', key)

    # @api.multi
    # def update_invoice(self):
    #     error_list = []
    #     header_list = []
    #     # file path should be server file path in server
    #     # path = '/home/abhishek/Desktop/IUG_master_data/invoice'
    #     path = '/home/iuadmin/invoices'
    #     for filename in os.listdir(path):
    #         # do your stuff
    #         file_obj = path + '/' + filename
    #         _logger.error('------------file name---------- %s', file_obj)
    #         target_doc = csv.reader(open(file_obj, 'rU'), delimiter=",")
    #         row_num = 0
    #         data_dict = {}
    #         for row in target_doc:
    #             data_dict.update({row_num: row})
    #             row.append(row_num)
    #             row_num += 1
    #         for key, value in data_dict.items():
    #             try:
    #                 if key == 0:
    #                     header_list.append(value)
    #                 else:
    #                     row = value
    #                     _logger.error('----------Row Number---------- %s', key)
    #                     invoice_old_id = row[0].strip()
    #                     invoice_type = row[23].strip() or ''
    #                     invoice_state=row[22].strip() or ''
    #                     # due_date=row[6].strip() or 0
    #                     # amount_total = row[32].strip() or ''
    #                     if invoice_old_id:
    #                         invoice_new_id=self.env['account.invoice'].search([('invoice_old_id', '=', invoice_old_id)], limit=1)
    #                     else:
    #                         invoice_new_id=False
    #                     if invoice_new_id:
    #                         if invoice_state=='open':
    #                             invoice_new_id.action_invoice_open()
    #                         elif invoice_state=='paid':
    #                             company_id=invoice_new_id.company_id.id
    #                             journal_id = self.env['account.journal'].search([('type', '=', 'cash'),
    #                                         ('company_id', '=',company_id),('account_journal_old_id','=',False)])
    #                             invoice_new_id.action_invoice_open()
    #                             invoice_new_id.pay_and_reconcile(journal_id, invoice_new_id.amount_total, invoice_new_id.date_due)
    #                     else:
    #                         _logger.error('--Invocie not Found!!-%s-',invoice_old_id)
    #                         error_list.append(value)
    #                     self._cr.commit()
    #             except Exception as e:
    #                 _logger.error('------------error log_id exception---------- %s', e)
    #                 error_list.append(value)
    #     # with open('/home/iuadmin/select_interpreter_line_error.csv', 'wb') as f:
    #     with open('/opt/home/iuadmin/event_line_error.csv', 'wb') as f:
    #         writer = csv.writer(f, delimiter=',')
    #         writer.writerows(header_list)
    #         writer.writerows(error_list)
    #         f.close()

    @api.multi
    def update_invoice(self):
        error_list = []
        header_list = []
        data_dict={}
        # file path should be server file path in server
        file_obj = '/home/iuadmin/customer_invoice.csv'
        lis = csv.reader(open(file_obj, 'rU'), delimiter=",")
        row_num = 0
        data_dict={}
        for row in lis:
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
                    invoice_old_id = row[0].strip()
                    invoice_state = row[1].strip() or ''
                    # due_date=row[6].strip() or 0
                    # amount_total = row[32].strip() or ''
                    if invoice_old_id:
                        invoice_new_id = self.env['account.invoice'].search(
                            [('invoice_old_id', '=', invoice_old_id)], limit=1)
                    else:
                        invoice_new_id = False
                    if invoice_new_id:
                        _logger.error('--------Invoice id ---------- %s', invoice_new_id.id)
                        if invoice_state == 'open':
                            if invoice_new_id.state == 'draft':
                                invoice_new_id.action_invoice_open()
                                self._cr.commit()
                        elif invoice_state == 'paid':
                            if invoice_new_id.state != 'paid':

                                if invoice_new_id.state == 'draft':
                                    invoice_new_id.action_invoice_open()
                                if invoice_new_id.residual:
                                    self._cr.execute(
                                        'select journal_id,payment_date from payment_date_update where invoice_id='+str(invoice_old_id)+' limit 1')
                                    rec = self._cr.dictfetchone()
                                    self._cr.execute('select id from account_journal where account_journal_old_id ='+str(rec['journal_id'])+' limit 1',)
                                    journal_id = self._cr.fetchone()
                                    journal_id = journal_id and journal_id[0] or False
                                    if journal_id:
                                        invoice_new_id.pay_and_reconcile(journal_id, invoice_new_id.residual,
                                                                         rec['payment_date'])
                                        self._cr.commit()
                    else:
                        _logger.error('--Invoice not Found!!-%s-', invoice_old_id)
                        value.append('Invoice not found')
                        error_list.append(value)
                    self._cr.commit()
            except Exception as e:
                _logger.error('------------error log_id exception---------- %s', e)
                value.append(e)
                error_list.append(value)
        # with open('/home/iuadmin/select_interpreter_line_error.csv', 'wb') as f:
        with open('/home/iuadmin/customer_invoices_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

    @api.multi
    def import_account_move(self):
        error_list = []
        header_list = []
        # path = '/home/abhishek/Desktop/IUG_master_data/move'
        path = '/home/iuadmin/acc_mov'
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
                        _logger.error('---current progress -- %s -- sheet--%s', key,filename)
                        company_id=self.env['res.company'].search([('res_company_old_id', '=', row[8].strip())],
                                                                  limit=1).id if row[8].strip() else False
                        journal_id=self.env['account.journal'].search([('account_journal_old_id', '=', row[9].strip())],
                                                                      limit=1).id if row[9].strip() else False
                        partner_id = self.env['res.partner'].search([('customer_record_old_id', '=', row[14].strip())],
                                                                    limit=1).id if row[14].strip() else False
                        period_id=self.env['account.period'].search([('period_old_id', '=', row[10].strip())],
                                                                    limit=1).id if row[10].strip() else False
                        journal_vals={
                            'account_mov_old_id':row[0].strip() or 0,
                            'name':row[5].strip() or '',
                            'state':row[6].strip() or '',
                            'ref':row[7].strip() or '',
                            'company_id':company_id,
                            'journal_id':journal_id,
                            'currency_id':3,
                            # 'amount':row[0].strip() or 0,
                            'narration':row[11].strip() or 0,
                            'date':row[12].strip() or 0,
                            'partner_id':partner_id,
                            'period_id':period_id
                        }
                        account_mov_id=self.env['account.move'].create(journal_vals)
                        self._cr.commit()
                except Exception as e:
                    _logger.error('------------error log_id exception---------- %s', e)
                    error_list.append(value)
        # with open('/home/abhishek/Desktop/output.csv', 'wb') as f:
        with open('/home/iuadmin/cust_upload_err/invoice_line_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()


    @api.multi
    def import_account_move_line(self):
        error_list = []
        header_list = []
        path = '/home/abhishek/Desktop/IUG_master_data/move_line'
        # path = '/home/iuadmin/acc_mov_line'
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
                        _logger.error('---current progress -- %s ', key,)

                        mov_line_id=self.env['account.move.line'].search([('move_line_old_id', '=', row[0].strip())],
                                                        limit=1).id if row[0].strip() else False
                        if not mov_line_id:
                            move_id = self.env['account.move'].search([('account_mov_old_id', '=', row[24].strip())],
                                                            limit=1).id if row[24].strip() else False
                            company_id=self.env['res.company'].search([('res_company_old_id', '=', row[14].strip())],
                                                                      limit=1).id if row[14].strip() else False
                            journal_id=self.env['account.journal'].search([('account_journal_old_id', '=', row[6].strip())],
                                                                          limit=1).id if row[6].strip() else False
                            partner_id = self.env['res.partner'].search([('customer_record_old_id', '=', row[9].strip())],
                                                                        limit=1).id if row[9].strip() else False
                            period_id=self.env['account.period'].search([('period_old_id', '=', row[21].strip())],
                                                                        limit=1).id if row[21].strip() else False

                            account_id=self.env['account.account'].search([('account_old_id','=',row[20].strip())],
                                                                          limit=1).id if row[20].strip() else False
                            product_id=self.env['product.product'].search([('product_old_id','=',row[28].strip())],
                                                                          limit=1).id if row[28].strip() else False
                            patient_id=self.env['patient'].search([('patient_old_id','=',row[40].strip())],
                                                                          limit=1).id if row[40].strip() else False
                            mov_line={
                                'move_line_old_id':row[0].strip() or 0,
                                # 'statement_id':row[5].strip() or '',
                                'journal_id':journal_id,
                                'currency_id':3,
                                'company_id':company_id,
                                'date_maturity':row[8].strip() or '',
                                'partner_id':partner_id,
                                'debit':float(row[17].strip()) or 0.0,
                                'ref':row[19].strip() or 0,
                                'account_id':account_id,
                                'date':row[23].strip() or 0,
                                'move_id':move_id,
                                'product_id':product_id,
                                # 'payment_id':payment_id,
                                'company_currency_id':3,
                                'name':row[25].strip() or '',
                                'credit':float(row[12].strip()) or 0.0,
                                # 'product_uom_id':product_uom_id,
                                # 'amount_currency':3,
                                'quantity':row[32].strip() or 0,
                                'period_id':period_id,
                                'reference':row[37].strip() or '',
                                # 'project_name_id':project_name_id,
                                'event_date':row[36].strip() or '',
                                'check_number':row[39].strip() or '',
                                'patient_id':patient_id
                            }
                            account_mov_line_id=self.env['account.move.line'].create(mov_line)
                            self._cr.commit()
                        else:
                            _logger.error('------line found------')
                except Exception as e:
                    _logger.error('------------error log_id exception---------- %s', e)
                    error_list.append(value)
            # with open('/home/abhishek/Desktop/output.csv', 'wb') as f:
        with open('/home/iuadmin/cust_upload_err/invoice_line_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

#function to update account_id in invoice line which ia updated incorrect during creation
    @api.multi
    def update_coa_invoice_line(self):
        error_list = []
        header_list = []
        # path = '/home/abhishek/Desktop/IUG_master_data/move'
        path = '/home/iuadmin/ac_invoice_line'
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
                        _logger.error('---current progress -- %s -- sheet--%s', key,filename)
                        invoice_line_id=self.env['account.invoice.line'].search([('invoice_line_old_id', '=', row[0].strip())],
                                                            limit=1) if row[0].strip() else False
                        if invoice_line_id:
                            account_id = self.env['account.account'].search([('account_old_id', '=', row[7].strip())],
                                                                        limit=1).id if row[7].strip() else False
                            invoice_line_id.write({'account_id':account_id})
                        else:
                            _logger.error('---invoice line not found---')

                except Exception as e:
                    _logger.error('------------error log_id exception---------- %s', e)
                    error_list.append(value)
        # with open('/home/abhishek/Desktop/output.csv', 'wb') as f:
        with open('/home/iuadmin/cust_upload_err/invoice_line_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()


#function to update invoice id in events
    @api.multi
    def update_invoice_id_in_event(self):
        error_list = []
        header_list = []
        # path = '/home/abhishek/Desktop/IUG_master_data/move'
        path = '/home/iuadmin/event_with_invoice'
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
                        _logger.error('---current progress -- %s -- sheet--%s', key,filename)
                        cust_invoice = row[65].strip() or ''
                        event = row[0].strip() or ''
                        cust_invoice_id = self.env['account.invoice'].search([('invoice_old_id','=',cust_invoice)],limit=1).id
                        if cust_invoice_id:
                            event_id = self.env['event'].search([('event_old_id','=',event)],limit=1).id
                            event_id_record = self.env['event'].browse(event_id)
                            event_id_record.write({'cust_invoice_id': cust_invoice_id})
                        else:
                            _logger.error('------------No invoice for event_id:----------- %s', event)

                except Exception as e:
                    _logger.error('------------error log_id exception---------- %s', e)
                    error_list.append(value)
        # with open('/home/abhishek/Desktop/output.csv', 'wb') as f:
        with open('/home/iuadmin/cust_upload_err/event_error_with_invoice.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

#function to update task_id in events
    @api.multi
    def update_task_id_in_event(self):
        error_list = []
        header_list = []
        # path = '/home/abhishek/Desktop/IUG_master_data/move'
        path = '/home/iuadmin/update_event'
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
                        _logger.error('---current progress -- %s -- sheet--%s', key,filename)
                        task_id = row[52].strip() or ''
                        event_id = row[0].strip() or ''
                        cust_invoice_id = row[65].strip() or ''
                        task_state = row[133].strip() or ''
                        if task_id:
                            self._cr.execute("select id from project_task where project_task_old_id=" + str(
                                task_id) + " limit 1")
                            task_id = self._cr.fetchone()
                            task_id = task_id and task_id[0] or False
                        if cust_invoice_id:
                            self._cr.execute("select id from account_invoice where invoice_old_id=" + str(
                                cust_invoice_id) + " limit 1")
                            cust_invoice_id = self._cr.fetchone()
                            cust_invoice_id = cust_invoice_id and cust_invoice_id[0] or False
                        if event_id:
                            self._cr.execute("select id from event where event_old_id=" + str(
                                event_id) + " limit 1")
                            event_id = self._cr.fetchone()
                            event_id = event_id and event_id[0] or False
                        if event_id:
                            if task_id and cust_invoice_id:
                                try:
                                    self._cr.execute(
                                        """ UPDATE event SET task_id=%s,cust_invoice_id=%s,task_state=%s where id=%s""",
                                        (task_id, cust_invoice_id, task_state,event_id))
                                    self._cr.commit()
                                except:
                                    self._cr.rollback()
                            elif cust_invoice_id:
                                try:
                                    self._cr.execute(
                                        """ UPDATE event SET cust_invoice_id=%s where id=%s""",
                                        (cust_invoice_id,event_id))
                                    self._cr.commit()
                                except:
                                    self._cr.rollback()
                            elif task_id:
                                try:
                                    self._cr.execute(
                                        """ UPDATE event SET task_id=%s,task_state=%s where id=%s""",
                                        (task_id,  task_state,event_id))
                                    self._cr.commit()
                                except:
                                    self._cr.rollback()
                except Exception as e:
                    _logger.error('------------error log_id exception---------- %s', e)
                    error_list.append(value)
        # with open('/home/abhishek/Desktop/output.csv', 'wb') as f:
        with open('/home/iuadmin/cust_upload_err/event_error_with_task_id.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()


#function to update related_company in res_partner (contacts)

            
    @api.multi
    def update_name_schedular_id(self):
        error_list = []
        header_list = []
        path = '/home/iuadmin/event_custom'
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
                        _logger.error('---current progress -- %s -- sheet--%s', key,filename)
                        event_id = row[0].strip()
                        name = row[1].strip() or False
                        scheduler_id = row[2].strip() or False
                        fee_note_status_id = row[3].strip() or False
                        appointment_type_id = row[4].strip() or False
                        sales_representative_id = row[5].strip() or False
                        all_interpreter_email=row[8].strip() or False
                        interpreters_phone=row[9].strip() or False
                        single_interpreter=row[6].strip() or False
                        project_name_id=row[7].strip() or False
                        if event_id:
                            event_id = self.env['event'].search([('event_old_id', '=', event_id)], limit=1)
                        else:
                            event_id = False
                        if event_id:
                            event_up_vals={}
                            if name:
                                event_up_vals.update({'name':name})
                            if fee_note_status_id:
                                fee_note_status_id=self.env['fee.note.status'].search(
                                    [('fee_note_status_old_id', '=', fee_note_status_id)], limit=1).id
                                event_up_vals.update({'fee_note_status_id': fee_note_status_id})
                            if appointment_type_id:
                                appointment_type_id = self.env['appointment.type'].search(
                                    [('app_type_old_id', '=', appointment_type_id)],
                                                                            limit=1).id
                                event_up_vals.update({'appointment_type_id':appointment_type_id})
                            if scheduler_id:
                                self._cr.execute("select id from res_users where user_old_id=" + str(
                                    scheduler_id) + " limit 1")
                                scheduler_id = self._cr.fetchone()
                                scheduler_id = scheduler_id and scheduler_id[0] or False
                                event_up_vals.update({'scheduler_id':scheduler_id})
                            if sales_representative_id:
                                self._cr.execute("select id from res_users where user_old_id=" + str(
                                    sales_representative_id) + " limit 1")
                                sales_representative_id = self._cr.fetchone()
                                sales_representative_id = sales_representative_id and sales_representative_id[0] or False
                                event_up_vals.update({'sales_representative_id': sales_representative_id})
                            if single_interpreter:
                                self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                                    single_interpreter) + " limit 1")
                                single_interpreter = self._cr.fetchone()
                                single_interpreter = single_interpreter and single_interpreter[0] or False
                                event_up_vals.update({'single_interpreter': single_interpreter})
                            if project_name_id:
                                project_id = self.env['project'].search(
                                    [('iug_project_old_id', '=', project_name_id)], limit=1).id
                                event_up_vals.update({'project_name_id': project_id})
                            if all_interpreter_email:
                                event_up_vals.update({'all_interpreter_email': all_interpreter_email})
                            if interpreters_phone:
                                event_up_vals.update({'interpreters_phone': interpreters_phone})
                            event_id.write(event_up_vals)
                            self._cr.commit()
                        else:
                            _logger.error('----already updated--------')

                except Exception as e:
                    self._cr.rollback()
                    _logger.error('------------error log_id exception---------- %s', e)
                    value.append(str(e))
                    error_list.append(value)
            os.remove(file_obj)
            _logger.error('----Removed File : %s-----',filename)
        with open('/home/iuadmin/cust_upload_err/event_update_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()
#function to import appointment type
    @api.multi
    def import_appointment_type(self):
        csv_datas = self.upload_file
        if not csv_datas:
            raise UserError(_("Choose the file before uploading!!!"))

        fileobj = TemporaryFile('w+')
        fileobj.write(base64.decodestring(csv_datas))
        fileobj.seek(0)
        str_csv_data = fileobj.read()
        lis = csv.reader(StringIO.StringIO(str_csv_data), delimiter=',')
        row_num = 0
        error_list = []
        header_list = []
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
                    row = value
                    _logger.error('----------Row Number---------- %s', key)
                    app_type_old_id = row[0].strip()
                    name = row[9].strip()
                    appointment_type_group_id = row[7].strip() or False
                    if appointment_type_group_id:
                        appointment_type_group_id = self.env['appointment.type.group'].search(
                            [('appointment_type_group_old_id', '=', appointment_type_group_id)],limit=1).id

                    appointment_type_id = row[5].strip()
                    is_medical_legal = row[6].strip()
                    company_id = row[8].strip() or False
                    if company_id:
                        company_id = self.env['res.company'].search(
                            [('res_company_old_id', '=', company_id)],limit=1).id
                    app_type_vals={
                        'app_type_old_id':app_type_old_id,
                        'name':name,
                        'appointment_type_group_id':appointment_type_group_id,
                        'appointment_type_id':appointment_type_id,
                        'is_medical_legal':is_medical_legal,
                        'company_id':company_id,
                    }
                    app_type_id=self.env['appointment.type'].create(app_type_vals)
            except Exception as e:
                _logger.error('------------Error Exception---------- %s', key)
                error_list.append(value)
        csvfile = StringIO.StringIO()
        w = csv.writer(csvfile, delimiter=',')
        w.writerow(header_list)
        w.writerows(error_list)
        file_data = csvfile.getvalue()
        self.upload_error = base64.encodestring(bytes(file_data))
        self.upload_error_file_name = 'Appointment type Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }

    @api.multi
    def import_appointment_type_group(self):
        csv_datas = self.upload_file
        if not csv_datas:
            raise UserError(_("Choose the file before uploading!!!"))

        fileobj = TemporaryFile('w+')
        fileobj.write(base64.decodestring(csv_datas))
        fileobj.seek(0)
        str_csv_data = fileobj.read()
        lis = csv.reader(StringIO.StringIO(str_csv_data), delimiter=',')
        row_num = 0
        error_list = []
        header_list = []
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
                    row = value
                    _logger.error('----------Row Number---------- %s', key)
                    appointment_type_group_old_id = row[0].strip()
                    name = row[7].strip()
                    appointment_type_group_id = row[5].strip()
                    company_id = row[6].strip() or False
                    if company_id:
                        company_id = self.env['res.company'].search([('res_company_old_id', '=', company_id)],
                                                                    limit=1).id
                    appointment_type_group_vals = {
                        'appointment_type_group_old_id': appointment_type_group_old_id,
                        'name': name,
                        'appointment_type_group_id': appointment_type_group_id,
                        'company_id': company_id,
                    }
                    app_type_id = self.env['appointment.type.group'].create(appointment_type_group_vals)

            except Exception as e:
                _logger.error('------------Error Exception---------- %s', key)
                error_list.append(value)
        csvfile = StringIO.StringIO()
        w = csv.writer(csvfile, delimiter=',')
        w.writerow(header_list)
        w.writerows(error_list)
        file_data = csvfile.getvalue()
        self.upload_error = base64.encodestring(bytes(file_data))
        self.upload_error_file_name = 'Appointment type Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }

    @api.multi
    def import_iug_project(self):
        csv_datas = self.upload_file
        if not csv_datas:
            raise UserError(_("Choose the file before uploading!!!"))

        fileobj = TemporaryFile('w+')
        fileobj.write(base64.decodestring(csv_datas))
        fileobj.seek(0)
        str_csv_data = fileobj.read()
        lis = csv.reader(StringIO.StringIO(str_csv_data), delimiter=',')
        row_num = 0
        error_list = []
        header_list = []
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
                    row = value
                    _logger.error('----------Row Number---------- %s', key)
                    iug_project_old_id = row[0].strip()
                    name = row[5].strip()
                    company_id = row[6].strip() or False
                    if company_id:
                        company_id = self.env['res.company'].search([('res_company_old_id', '=', company_id)],
                                                                    limit=1).id
                    iug_pro_vals = {
                        'iug_project_old_id': iug_project_old_id,
                        'name': name,
                        'company_id': company_id,
                    }
                    iug_pro_id = self.env['project'].create(iug_pro_vals)
            except Exception as e:
                _logger.error('------------Error Exception---------- %s', e)
                error_list.append(value)
        csvfile = StringIO.StringIO()
        w = csv.writer(csvfile, delimiter=',')
        w.writerow(header_list)
        w.writerows(error_list)
        file_data = csvfile.getvalue()
        self.upload_error = base64.encodestring(bytes(file_data))
        self.upload_error_file_name = 'Project Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }

    @api.multi
    def update_project_event(self):
        error_list = []
        header_list = []
        # path = '/home/abhishek/Desktop/IUG_master_data/move'
        path = '/home/iuadmin/iu_project_event'
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
                        project_name_id = row[96].strip() or ''
                        event = row[0].strip() or ''
                        project_id = self.env['project'].search(
                            [('iug_project_old_id', '=', project_name_id)], limit=1).id
                        if project_id:
                            event_id = self.env['event'].search([('event_old_id', '=', event)], limit=1)
                            event_id.write({'project_name_id': project_id})
                            self._cr.commit()
                        else:
                            _logger.error('----------------------- %s', event)
                            error_list.append(value)

                except Exception as e:
                    _logger.error('------------error log_id exception---------- %s', e)
                    error_list.append(value)
        # with open('/home/abhishek/Desktop/output.csv', 'wb') as f:
        with open('/home/iuadmin/cust_upload_err/event_error_with_project_name_id.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()
    @api.multi
    def update_project_invoice(self):
        error_list = []
        header_list = []
        # path = '/home/abhishek/Desktop/IUG_master_data/move'
        path = '/home/iuadmin/invoice_project'
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
                        project_name_id = row[1].strip() or ''
                        invoice_old_id = row[0].strip() or ''
                        project_id = self.env['project'].search(
                            [('iug_project_old_id', '=', project_name_id)], limit=1).id
                        if project_id:
                            invoice_obj = self.env['account.invoice'].search([('invoice_old_id', '=', invoice_old_id)], limit=1)
                            invoice_obj.write({'project_name_id': project_id})
                            self._cr.commit()
                        else:
                            _logger.error('--------no matching project----------')
                            error_list.append(value)

                except Exception as e:
                    _logger.error('------------error log_id exception---------- %s', e)
                    error_list.append(value)
        # with open('/home/abhishek/Desktop/output.csv', 'wb') as f:
        with open('/home/iuadmin/cust_upload_err/invoice_error_with_project_name_id.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()


    #function to import incoming Fax
    @api.multi
    def import_incoming_fax(self):
        error_list = []
        header_list = []
        # path = '/home/abhishek/Desktop/IUG_master_data/move'
        path = '/home/iuadmin/fax_in'
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
                        # partner = row[0].strip() or ''
                        # partner_id = self.env['res.partner'].search([('customer_record_old_id','=',partner)],limit=1).id
                        # event = row[0].strip() or ''
                        # event_id = self.env['event'].search([('event_old_id','=',event)],limit=1).id
                        company = row[12].strip() or ''
                        company_id = self.env['res.company'].search([('res_company_old_id','=',company)],limit=1).id
                        company2 = row[15].strip() or ''
                        company_id2 = self.env['res.company'].search([('res_company_old_id', '=', company2)], limit=1).id
                        fax_attachment = row[29].strip() or ''
                        fax_attachment_id = self.env['ir.attachment'].search([('res_old_id','=',fax_attachment)],limit=1).id
                        document_type = row[30].strip() or ''
                        document_type_id = self.env['document.type'].search([('document_type_old_id','=',document_type)],limit=1).id
                        fax_in_vals={
                                    'fax_in_old_id':row[0].strip() or '',
                                    'name':row[10].strip() or '',
                                    'date':row[8].strip() or '',
                                    'fax':row[6].strip() or '',
                                    'attach_to':row[11].strip() or '',
                                    'doc_type':row[16].strip() or '',
                                    # 'partner_id':partner_id, not having values in it
                                    # 'event_id':event_id, not having values in it
                                    # 'partner_ids':row[0].strip() or '', Many2many field not having any data
                                    # 'event_ids':row[0].strip() or '',Many2many field need to import after creation
                                    'company_id':company_id,
                                    'company_id2':company_id2,
                                    # 'fax_attachment_ids':row[0].strip() or '', One2many Field
                                    'fax_attachment_id':fax_attachment_id,
                                    'document_type_id':document_type_id,
                                    'attached':True if row[27].strip()=='t' else False,
                                    'msg_id':int(row[17].strip()) if row[17].strip() else 0,
                                    'ph_no':row[21].strip() or '',
                                    'csid':row[23].strip() or '',
                                    'msg_stat':row[20].strip() or '',
                                    'pages':int(row[26].strip()) if row[26].strip() else 0,
                                    'msg_size':int(row[24].strip()) if row[24].strip() else 0,
                                    'msg_type':row[18].strip() or '',
                                    'rcv_time':row[19].strip() or '',
                                    'caller_id':row[7].strip() or '',
                                    'rec_duration':row[22].strip() or '',
                                    'received_status':row[25].strip() or '',
                                    'state':row[31].strip() or '',
                                    }
                        incoming_fax_new_id=self.env['incoming.fax'].create(fax_in_vals)
                        self._cr.commit()

                except Exception as e:
                    _logger.error('------------error log_id exception---------- %s', e)
                    error_list.append(value)
        # with open('/home/abhishek/Desktop/output.csv', 'wb') as f:
        with open('/home/iuadmin/uploading_error/fax_in_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

#function to update event_ids many@many field
    @api.multi
    def update_events_ids_in_fax_in(self):
        error_list = []
        header_list = []
        # path = '/home/abhishek/Desktop/IUG_master_data/move'
        path = '/home/iuadmin/map_fax_event'
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
                        fax = row[0].strip() or ''
                        fax_id = self.env['incoming.fax'].search([('fax_in_old_id','=',fax)],limit=1).id
                        event = row[1].strip() or ''
                        event_id = self.env['event'].search([('event_old_id','=',event)],limit=1).id
                        if fax_id and event_id:
                            vals = (fax_id, event_id)
                            self._cr.execute(""" INSERT INTO fax_event_rel (fax_id,event_id) VALUES (%s,%s)""",vals)
                            self._cr.commit()
                except Exception as e:
                    _logger.error('------------error log_id exception---------- %s', e)
                    error_list.append(value)
        with open('/home/iuadmin/uploading_error/event_id_in_fax_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

#function to update partner_id in rate
    @api.multi
    def update_partner_id_in_rate(self):
        error_list = []
        header_list = []
        # path = '/home/abhishek/Desktop/IUG_master_data/move'
        path = '/home/iuadmin/map_partner_rate'
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
                        partner = row[0].strip() or ''
                        partner_id = self.env['res.partner'].search([('customer_record_old_id','=',partner)],limit=1).id
                        if partner_id:
                            rate = row[0].strip() or ''
                            rate_id = self.env['rate'].search([('rate_old_id', '=', rate)],limit=1)
                            rate_id.write({'partner_id':partner_id})
                        else:
                            pass
                        self._cr.commit()
                except Exception as e:
                    _logger.error('------------error log_id exception---------- %s', e)
                    error_list.append(value)
        with open('/home/iuadmin/uploading_error/partner_in_rate_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

    # function to import Assign Translator History
    @api.multi
    def import_assign_translator_history(self):
        error_list = []
        header_list = []
        # path = '/home/abhishek/Desktop/IUG_master_data/move'
        path = '/home/iuadmin/assign_translator_history'
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
                        name_id = row[10].strip() or ''
                        if name_id:
                            self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                                name_id) + " limit 1")
                            name_id = self._cr.fetchone()
                            name_id = name_id and name_id[0] or False
                        event_id = row[6].strip() or ''
                        if event_id:
                            self._cr.execute("select id from event where event_old_id=" + str(
                                event_id) + " limit 1")
                            event_id = self._cr.fetchone()
                            event_id = event_id and event_id[0] or False
                        partner_id = value[9].strip() or False
                        if partner_id:
                            self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                                partner_id) + " limit 1")
                            partner_id = self._cr.fetchone()
                            partner_id = partner_id and partner_id[0] or False
                        if name_id and partner_id:
                            as_trans_his_vals = {
                                            'assign_trans_his_old_id':row[0].strip() or '',
                                            'name':name_id,
                                            'partner_id': partner_id,
                                            'event_date': row[8].strip() or '',
                                            'event_id': event_id,
                                            'state': row[7].strip() or '',
                                            'schedule_translator_event_time': row[5].strip() or '',
                                            }
                            assign_trans_his_new_id = self.env['assign.translator.history'].search([('assign_trans_his_old_id','=',row[0].strip())],limit=1)
                            if not assign_trans_his_new_id:
                                assign_trans_his_new_id = self.env['assign.translator.history'].create(as_trans_his_vals)
                            else:
                                assign_trans_his_new_id.write(as_trans_his_vals)
                            self._cr.commit()
                        else:
                            _logger.error('------No Partner found !!------')
                            error_list.append(value)
                except Exception as e:
                    self._cr.rollback()
                    _logger.error('------------error log_id exception---------- %s', e)
                    value.append(str(e))
                    error_list.append(value)
        # with open('/home/abhishek/Desktop/output.csv', 'wb') as f:
        with open('/home/iuadmin/uploading_error/assign_translator_history_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

    @api.multi
    def map_journal_for_invoices(self):
        error_list = []
        header_list = []
        # path = '/home/abhishek/Desktop/IUG_master_data/move'
        file_obj = '/home/iuadmin/invoice_journal_account.csv'
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
                    invoice= row[1].strip()
                    invoice_id = self.env['account.invoice'].search([('invoice_old_id', '=', invoice),('event_id','!=',False)], limit=1).id
                    if invoice_id:
                        journal = row[0].strip()
                        journal_id = self.env['account.journal'].search([('account_journal_old_id', '=', journal)], limit=1).id
                        self._cr.execute(""" update account_move set journal_id =%s where id= (select move_id from account_move_line where account_move_line.invoice_id=%s limit 1)""",
                                         (journal_id,invoice_id))
                        account_old=row[2].strip()
                        account_old_id = self.env['account.account'].search([('account_old_id', '=', account_old)], limit=1).id
                        if account_old_id:
                            self._cr.execute(""" update account_move_line set account_id =%s where id= (select id from account_move_line where invoice_id=%s and event_date is null limit 1)""",
                                (account_old_id, invoice_id))
                        self._cr.commit()
                    else:
                        _logger.error('------No invoice found !!------')
                        error_list.append(value)
            except Exception as e:
                _logger.error('------------error log_id exception---------- %s', e)
                error_list.append(value)
        # with open('/home/abhishek/Desktop/output.csv', 'wb') as f:
        with open('/home/iuadmin/invoice_journal_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

    @api.multi
    def map_journal_for_payments(self):
        error_list = []
        header_list = []
        # path = '/home/abhishek/Desktop/IUG_master_data/move'
        file_obj = '/home/iuadmin/invoice_payment.csv'
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
                    _logger.error('---current payment journal update -- %s', key)
                    invoice = row[1].strip()
                    invoice_id = self.env['account.invoice'].search(
                        [('invoice_old_id', '=', invoice)], limit=1).id
                    if invoice_id:
                        self._cr.execute("select payment_id from account_invoice_payment_rel where invoice_id="+str(invoice_id)+" limit 1")
                        payment_id=self._cr.fetchone()
                        payment_id=payment_id and payment_id[0] or False
                        if payment_id:
                            journal = row[0].strip()
                            journal_id = self.env['account.journal'].search([('account_journal_old_id', '=', journal)],limit=1).id
                            self._cr.execute(""" update account_move set journal_id =%s where id= (select move_id from account_move_line where payment_id=%s limit 1)""",(journal_id, payment_id))
                            self._cr.commit()
                    else:
                        _logger.error('------No invoice found !!------')
                        error_list.append(value)
            except Exception as e:
                _logger.error('------------error log_id exception---------- %s', e)
                error_list.append(value)
        # with open('/home/abhishek/Desktop/output.csv', 'wb') as f:
        with open('/home/iuadmin/payment_journal_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()



    @api.multi
    def map_check_number_for_payments(self):
        error_list = []
        header_list = []
        # path = '/home/abhishek/Desktop/IUG_master_data/move'
        file_obj = '/home/iuadmin/invoice_check_numbers.csv'
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
                    _logger.error('---current payment check number update -- %s', key)
                    invoice = row[1].strip()
                    invoice_id = self.env['account.invoice'].search(
                        [('invoice_old_id', '=', invoice)], limit=1).id
                    if invoice_id:
                        self._cr.execute("select payment_id from account_invoice_payment_rel where invoice_id="+str(invoice_id)+" limit 1")
                        payment_id=self._cr.fetchone()
                        payment_id=payment_id and payment_id[0] or False
                        if payment_id:
                            check_number = row[0].strip()
                            self._cr.execute(""" update account_payment set check_number_string =%s where id= %s""",(check_number, payment_id))
                            self._cr.commit()
                    else:
                        _logger.error('------No invoice found !!------')
                        error_list.append(value)
            except Exception as e:
                _logger.error('------------error log_id exception---------- %s', e)
                error_list.append(value)
        # with open('/home/abhishek/Desktop/output.csv', 'wb') as f:
        with open('/home/iuadmin/payment_journal_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

    @api.multi
    def import_payment_terms(self):
        error_list = []
        header_list = []
        data_dict = {}
        # file path should be server file path in server
        file_obj = '/home/iuadmin/property_payment_terms.csv'
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
                    row = value
                    partner_id = row[0].strip() or False
                    if partner_id:
                        partner_id = self.env['res.partner'].search(
                            [('customer_record_old_id', '=', partner_id)], limit=1).id
                    company_id = value[2].strip() or False
                    if company_id:
                        company_id = self.env['res.company'].search([('res_company_old_id', '=', company_id)], limit=1).id
                    field = self.env['ir.model.fields'].search(
                        [('model', '=', 'res.partner'), ('name', '=', 'property_supplier_payment_term_id')])
                    self.env['ir.property'].create({
                        'name': 'property_supplier_payment_term_id',
                        'company_id': company_id,
                        'value_reference': 'account.payment.term,%s' % row[1].strip(),
                        'fields_id': field.id,
                        'res_id':'res.partner,%s' %partner_id
                    })
                    self._cr.commit()
            except Exception as e:
                _logger.error('------------error log_id exception---------- %s', e)
                value.append(e)
                error_list.append(value)
        # with open('/home/iuadmin/select_interpreter_line_error.csv', 'wb') as f:
        with open('/home/iuadmin/payment_terms_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()
    
    @api.multi
    def import_block_inter_ids(self):
        csv_datas = self.upload_file
        if not csv_datas:
            raise UserError(_("Choose the file before uploading!!!"))

        fileobj = TemporaryFile('w+')
        fileobj.write(base64.decodestring(csv_datas))
        fileobj.seek(0)
        str_csv_data = fileobj.read()
        lis = csv.reader(StringIO.StringIO(str_csv_data), delimiter=',')
        row_num = 0
        error_list = []
        header_list = []
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
                    _logger.error('----------Row Number---------- %s', key)
                    part_id = value[0].strip() or False
                    if part_id:
                        self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                            part_id) + " limit 1")
                        part_id = self._cr.fetchone()
                        part_id = part_id and part_id[0] or False
                    cust_id = value[1].strip() or False
                    if cust_id:
                        self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                            cust_id) + " limit 1")
                        cust_id = self._cr.fetchone()
                        cust_id = cust_id and cust_id[0] or False
                    if part_id and cust_id:
                        vals=(part_id,cust_id)
                        self._cr.execute(""" INSERT INTO part_cust_rel (part_id,cust_id) VALUES (%s,%s)""", vals)
                        self._cr.commit()
            except Exception as e:
                self._cr.rollback()
                _logger.error('------------Error Exception---------- %s', key)
                error_list.append(value)
        csvfile = StringIO.StringIO()
        w = csv.writer(csvfile, delimiter=',')
        w.writerow(header_list)
        w.writerows(error_list)
        file_data = csvfile.getvalue()
        self.upload_error = base64.encodestring(bytes(file_data))
        self.upload_error_file_name = 'block_inter_ids.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }

    @api.multi
    def update_payment_term(self):
        error_list = []
        header_list = []
        path = '/home/iuadmin/invoice_custom'
        account_invoice_obj = self.env['account.invoice']
        for filename in os.listdir(path):
            file_obj = path + '/' + filename
            target_doc = csv.reader(open(file_obj, 'rU'), delimiter=",")
            row_num = 0
            data_dict = {}
            for row in target_doc:
                try:
                    invoice_id = row[0].strip()
                    if invoice_id:
                        invoice_obj = account_invoice_obj.browse(int(invoice_id))
                    if invoice_obj:
                        invoice_obj._onchange_payment_term_date_invoice()
                except Exception as e:
                    _logger.error('------------error log_id exception---------- %s', e)
                    error_list.append(row)
                    os.remove(file_obj)
    # with open('/home/abhishek/Desktop/output.csv', 'wb') as f:
        with open('/home/iuadmin/cust_upload_err/invoice_update_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

    @api.multi
    def cancel_payments(self):
        error_list = []
        header_list = []
        file_obj = '/home/iuadmin/cancel_payments.csv'
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
                    _logger.error('---current payment check number update -- %s', key)
                    payment = row[0].strip()
                    payment_id = self.env['account.payment'].browse(int(payment))
                    if payment_id:
                        if payment_id.state== 'posted':
                            payment_id.cancel()
                    else:
                        pass
            except Exception as e:
                _logger.error('------------error log_id exception---------- %s', e)
                error_list.append(value)
        # with open('/home/abhishek/Desktop/output.csv', 'wb') as f:
        with open('/home/iuadmin/payment_cancel_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

