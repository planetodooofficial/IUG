from datetime import datetime, date
# import time
import datetime
from datetime import timedelta, date
# from dateutil import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from io import BytesIO
import xlrd
import base64
# import urllib
import logging
import pytz
# from pytz import timezone
# from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare

_logger = logging.getLogger(__name__)


def _convert_object(input_type, value):
    result = False
    if input_type == int:
        result = int(value)
    elif input_type == str:
        result = str(value).strip()
    elif input_type == bool:
        if value in ["Active", "Y", "y", 1, "true", "YES", "Yes", "yes"]:
            result = True
        elif value in ["Inactive", "N", "n", 0, "false", "NO", "No", "no"]:
            result = False
        else:
            result = bool(value)
    return result


class ImportHistory(models.Model):
    _name = 'import.history'
    _order = "start_datetime desc"

    start_date = fields.Datetime('Start date')
    upload_type = fields.Selection(
        [('customer', 'Customer'), ('contact', 'Contact'),
         ('event', 'Event'), ('interpreter', 'Interpreter'), ('interaction', 'Interaction')],
        string='Upload Type', default='customer')
    status = fields.Text('Status')
    start_datetime = fields.Datetime(string="Start DateTime", required=False, )
    end_datetime = fields.Datetime(string="End DateTime", required=False, )


class DataWiz(models.TransientModel):
    _name = 'data.wiz'

    text_message = fields.Text('Message')


class ImportDataXLXInherit(models.Model):
    '''
      This class to provide wizard to upload xlx file
    '''
    _name = 'import.data'

    file_path = fields.Char(string='File Path', size=256)
    is_local = fields.Boolean(string="Is Local")
    xls_file = fields.Binary(attachment=True, string='XLS File')
    upload_type = fields.Selection([('customer', 'Customer'), ('contact', 'Contact'), ('interpreter', 'Interpreter'),
                                    ('event', 'Event'), ('interaction', 'Interaction')], string='Upload Type', default='customer')
    filename = fields.Char()

    def read_xlx_file(self):
        '''
         cursereate Temp xlx file
        '''
        file_data = self.xls_file
        if not file_data:
            raise UserError(_('Error!', "Please Select a File"))
        else:
            val = base64.decodestring(file_data)
            tempfile = BytesIO()
            tempfile.write(val)
            work_book = xlrd.open_workbook(file_contents=tempfile.getvalue())
        return work_book

    # import script

    def upload_data(self):
        '''
          This function is to read data from xls.
        '''
        start_datetime = datetime.datetime.now()
        if self.is_local:
            file_location = "//home/ali/Documents/workspace/odoo10/custom_modules/iug_erp_kastech/addons/globlinks_migration/data/bookings-9001-10000.xlsx"
            work_book = xlrd.open_workbook(file_location)
        else:
            work_book = self.read_xlx_file()
        sheet_list = work_book.sheet_names()
        created_entries = []
        updated_entries = []
        invalid_entries = []
        company_id = self.get_globe_link_company_id()

        if self.upload_type == 'customer':
            if 'All-Customers' in sheet_list:
                sheet = work_book.sheet_by_name('All-Customers')
            else:
                raise UserError(_("There is no sheet of name 'All-Customers',\
                Please make sure your Excel file having sheet with Name 'All-Customers'."))
            partner_object = self.env["res.partner"]
            header_to_fields_list = partner_object.map_customer_sheet_header_to_field()
            header_to_fields_list_with_index = self.get_index_from_sheet(
                sheet, header_to_fields_list)
            list_dictionary = self.map_sheet_data(
                sheet, header_to_fields_list_with_index)
            customer_type = 'customer'
            created_entries, updated_entries = partner_object.upload_data(
                list_dictionary, customer_type=customer_type)
            self.call_message_wiz(created_entries, updated_entries, [], upload_type=customer_type,
                                  start_datetime=start_datetime)

            # n_rows = sheet.nrows
            # self.update_customer_data(
            #     n_rows, updated_entries, created_entries, sheet, company_id)
        elif self.upload_type == 'contact':

            if 'contacts' in sheet_list:
                sheet = work_book.sheet_by_name('contacts')
            else:
                raise UserError(_("There is no sheet of name 'contacts',\
                Please make sure your Excel file having sheet with Name 'contacts'."))
            partner_object = self.env["res.partner"]
            header_to_fields_list = partner_object.map_contact_sheet_header_to_field()
            header_to_fields_list_with_index = self.get_index_from_sheet(
                sheet, header_to_fields_list)
            list_dictionary = self.map_sheet_data(
                sheet, header_to_fields_list_with_index)
            customer_type = 'contact'
            created_entries, updated_entries = partner_object.upload_data(
                list_dictionary, customer_type=customer_type)
            self.call_message_wiz(created_entries, updated_entries, [], upload_type=customer_type,
                                  start_datetime=start_datetime)
            # n_rows = sheet.nrows
            # self.update_contacts_data(
            #     n_rows, updated_entries, created_entries, sheet, company_id)

        elif self.upload_type == 'interpreter':
            if 'intepreter_booking' in sheet_list:
                sheet = work_book.sheet_by_name('intepreter_booking')
            else:
                raise UserError(_("There is no sheet of name 'intepreter_booking',\
                Please make sure your Excel file having sheet with Name 'interpreters'."))
            partner_object = self.env["res.partner"]
            header_to_fields_list = partner_object.map_interpreter_sheet_header_to_field()
            header_to_fields_list_with_index = self.get_index_from_sheet(
                sheet, header_to_fields_list)
            list_dictionary = self.map_sheet_data(
                sheet, header_to_fields_list_with_index)
            customer_type = 'interpreter'
            created_entries, updated_entries = partner_object.upload_data(
                list_dictionary, customer_type=customer_type)
            self.call_message_wiz(created_entries, updated_entries, [], upload_type=customer_type,
                                  start_datetime=start_datetime)

            # n_rows = sheet.nrows
            # self.update_interpreters_data(
            #     n_rows, created_entries, updated_entries, sheet, company_id)
        elif self.upload_type == 'event':
            if 'Jobs' in sheet_list:
                sheet = work_book.sheet_by_name('Jobs')
            else:
                raise UserError(_("There is no sheet of name 'Jobs',\
                Please make sure your Excel file having sheet with Name 'Jobs'."))
            n_rows = sheet.nrows
            self.update_event_data(
                n_rows, updated_entries, created_entries, sheet, company_id, invalid_entries)
        elif self.upload_type == 'interaction':
            if 'Interactions' in sheet_list:
                sheet = work_book.sheet_by_name('Interactions')
            else:
                raise UserError(_("There is no sheet of name 'Interactions',\
                Please make sure your Excel file having sheet with Name 'Interactions'."))

            interaction_object = self.env["interaction"]
            header_to_fields_list = interaction_object.map_interaction_sheet_header_to_field()
            header_to_fields_list_with_index = self.get_index_from_sheet(
                sheet, header_to_fields_list)
            list_dictionary = self.map_sheet_data(
                sheet, header_to_fields_list_with_index)
            created_entries, updated_entries = interaction_object.upload_data(list_dictionary)
            self.call_message_wiz(created_entries, updated_entries, [], upload_type="interaction",
                                  start_datetime=start_datetime)

    def call_message_wiz(self, created_entries, updated_entries, invalid_entries, upload_type, start_datetime):
        error_data1 = '\n\n Created entries are %s.' % created_entries
        error_data2 = '\n\n\n\n Updated entries are %s. \n\n' % updated_entries
        error_data3 = '\n\n\n\n Invalid entries are %s. \n\n' % invalid_entries
        error_data = error_data1 + error_data2 + error_data3
        message_wiz_id = self.env['data.wiz'].create(
            {'text_message': error_data})
        self.env['import.history'].create({
            'start_datetime': start_datetime,
            'end_datetime': datetime.datetime.now(),
            'start_date': datetime.datetime.now(),
            'upload_type': upload_type,
            'status': error_data
        })
        return {'name': _("Update Information"),
                'view_mode': 'form',
                'view_id': False,
                'res_model': 'data.wiz',
                'res_id': message_wiz_id.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'domain': '[]',
                }

    @staticmethod
    def get_index_from_sheet(sheet, header_to_fields_list):
        header_row_list = sheet.row_values(0)
        header_row_list = [str(header) for header in header_row_list]
        header_to_fields_list_with_index = []
        for header_to_fields in header_to_fields_list:
            if header_to_fields["excel_header_name"] and header_to_fields["excel_header_name"] in header_row_list:
                header_to_fields["index"] = header_row_list.index(
                    header_to_fields["excel_header_name"])
            else:
                header_to_fields["index"] = False
            header_to_fields_list_with_index.append(header_to_fields)
        return header_to_fields_list_with_index

    @api.model
    def map_sheet_data(self, sheet, header_to_fields_list_with_index):
        n_rows = sheet.nrows
        list_record = []
        for row in range(1, n_rows):
            line = sheet.row_values(row)
            record = {}
            for header_to_fields in header_to_fields_list_with_index:
                column_value = header_to_fields["default_value"]
                if header_to_fields["index"] is not False and len(line) > header_to_fields["index"]:
                    column_value = line[header_to_fields["index"]]
                if header_to_fields["function_call"]:
                    column_value = eval(header_to_fields["function_call"])
                if column_value:
                    column_value = _convert_object(
                        header_to_fields["data_type"], column_value)
                record[header_to_fields["model_field_name"]] = column_value
            list_record.append(record)
        return list_record

    def get_globe_link_company_id(self):
        """

        :return:
        """
        name = "Globe"
        search_domain = [
            ("name", "ilike", name)
        ]
        company_record = self.env['res.company'].sudo().search(
            search_domain, limit=1)
        if company_record.exists():
            company_id = company_record.id
        else:
            raise UserError(
                _('Please create a Company with the Name: %s' % str(name)))
        return company_id

    def update_event_data(self, n_rows, updated_entries, created_entries, sheet, company_id, invalid_entries):
        event_obj = self.env['event']
        start_datetime = datetime.datetime.now()
        # res_company_obj = self.env['res.company']
        user_obj = self.env['res.users']
        location_obj = self.env['location']
        state_obj = self.env['res.country.state']
        partner_obj = self.env['res.partner']
        patient_obj = self.env['patient']
        language_obj = self.env['language']
        country_obj = self.env['res.country']
        tz = pytz.timezone('US/Pacific') or pytz.utc
        tz2 = tz
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        certification_level_obj = self.env['certification.level']
        for row in range(1, n_rows):
            _logger.info("\n\n\n Event row number  %s out of %s \n" %
                         (str(row), str(n_rows - 1)))
            job_id = int(float(str(sheet.row_values(row)[0]).strip()))
            user_id = user_obj.sudo().search(
                [('name', '=ilike', str(sheet.row_values(row)[4]).strip())])
            # company_id = res_company_obj.search(
            #     [('name', '=ilike', 'GlobeLinks')])
            event_note = ''
            interpretor_note = ''
            interpretor_note = str(sheet.row_values(row)[73]).strip(
            ) or False + str(sheet.row_values(row)[175]).strip() or False + str(
                sheet.row_values(row)[254]).strip() or False
            event_note = str(sheet.row_values(row)[19]).strip(
            ) + str(sheet.row_values(row)[76]).strip() + str(sheet.row_values(row)[172]).strip(
            ) + str(sheet.row_values(row)[173]).strip() + str(sheet.row_values(row)[174]).strip(
            ) + str(sheet.row_values(row)[252]).strip() + "offer Date/Time" + str(
                sheet.row_values(row)[183]).strip(
            ) or False + "Interpretor Assignment date/time" + str(sheet.row_values(row)[185]).strip() or False
            customer_id = partner_obj.sudo().search([('name', '=ilike', str(
                sheet.row_values(row)[21]).strip()), ('cust_type', '=', 'customer'), ('company_id', '=', company_id)], limit=1)
            ordering_partner_id = partner_obj.sudo().search([('name', '=ilike', str(
                sheet.row_values(row)[28]).strip()), ('cust_type', '=', 'customer'), ('company_id', '=', company_id)], limit=1)
            patient_id = False
            if str(sheet.row_values(row)[30]).strip():
                patient = str(sheet.row_values(row)[30]).strip().split(' ')
                patient_id = patient_obj.sudo().search(
                    [('name', '=ilike', patient[0]), ('company_id', '=', company_id)])
                if not patient_id:
                    patient_obj.create({
                        'name': patient[0],
                        'active': True,
                        'company_id': company_id,
                        'phone': patient[1]
                    })
            if str(sheet.row_values(row)[43]).strip():
                contact = str(sheet.row_values(row)[43]).strip().split(' ')
                _logger.info("contact %s" % str(contact))
                ordering_contact_id = partner_obj.sudo().search(
                    [('name', '=ilike', contact[0]), ('cust_type', '=', 'contact'), ('company_id', '=', company_id)], limit=1)
                if not ordering_contact_id:
                    ordering_contact_id = partner_obj.sudo().create({
                        'name': contact[0],
                        'last_name': contact[1],
                        'phone': contact[2],
                        'company_id': company_id,
                        'active': True,
                        'cust_type': 'contact',
                        'customer': True,
                        'is_company': False
                    })
            language_id = language_obj.get_language_id_by_name(str(sheet.row_values(row)[47]).strip())
            # language_id = language_obj.search(
            #     [('name', '=ilike', str(sheet.row_values(row)[47]).strip())])
            certification_level_id = certification_level_obj.sudo().search(
                [('name', '=ilike', str(sheet.row_values(row)[153]).strip()), ("company_id", "=", company_id)], limit=1)
            if not certification_level_id:
                certification_level_id = certification_level_obj.sudo().create(
                    {'name': str(sheet.row_values(row)[153]).strip(), 'active': True, "company_id": company_id})
            appointment_type_id = self.env['appointment.type'].sudo().search(
                [('name', '=ilike', str(sheet.row_values(row)[71]).strip()), ("company_id", "=", company_id)], limit=1)
            if not appointment_type_id:
                appointment_type_id = self.env['appointment.type'].sudo().create({
                    'name': str(sheet.row_values(row)[71]).strip(),
                    "company_id": company_id
                })
            location_id = location_obj.search(
                [('name', '=ilike', str(sheet.row_values(row)[33]).strip())], limit=1)
            state_id = state_obj.sudo().search(['|', ('name', '=ilike', str(sheet.row_values(row)[37]).strip()),
                                                ('code', '=ilike', str(sheet.row_values(row)[37]).strip())])
            default_country_id = country_obj.sudo().search(
                [('code', '=', 'US')])
            country_id = country_obj.sudo().search(
                ['|', ('code', '=ilike', str(sheet.row_values(row)[27]).strip()),
                 ('name', '=ilike', str(sheet.row_values(row)[39]).strip())])
            if not location_id:
                location_id = location_obj.sudo().create({
                    'name': str(sheet.row_values(row)[33]).strip(),
                    'street': str(sheet.row_values(row)[35]).strip() or False,
                    'city': str(sheet.row_values(row)[36]).strip() or False,
                    'state_id': state_id[0].id if state_id else False,
                    'country_id': country_id.id if country_id else default_country_id.id,
                    'zip': str(sheet.row_values(row)[38]).strip() or False,
                    'active': True,
                    'comment': str(sheet.row_values(row)[42]).strip() + str(sheet.row_values(row)[45]).strip() or False
                })
            actual_start_date = str(sheet.row_values(row)[15]).strip()
            utc_actual_dt = ''
            actual_start_hr2 = ['', '']
            actual_start_am_pm = ''
            if actual_start_date:
                actual_start_date = datetime.datetime.strptime(
                    actual_start_date, "%m/%d/%y").strftime("%Y-%m-%d")
                actual_start_hr_set = str(sheet.row_values(row)[16]).strip()
                actual_hr_time = actual_start_hr_set.split(' ')
                actual_start_hr2 = actual_hr_time[0].split(':')
                actual_start_hour = int(actual_start_hr2[0])
                # print "actual_hr_time",actual_hr_time
                if actual_hr_time[1] and actual_hr_time[1] == 'PM':
                    actual_start_am_pm = "pm"
                    if actual_start_hour < 12:
                        actual_start_hour += 12

                    # if not int(actual_start_hr2[0]):
                    #     actual_start_hr2[0] = int(actual_start_hr2[0]) + 12
                elif actual_hr_time[1] and actual_hr_time[1] == 'AM':
                    actual_start_am_pm = "am"
                    if actual_start_hour == 12:
                        actual_start_hour = 0
                actual_start = str(actual_start_date) + ' ' + \
                               str(actual_start_hour) + ':' + str(actual_start_hr2[1]) + ':00'
                actual_local_dt = tz.localize(datetime.datetime.strptime(
                    actual_start, DATETIME_FORMAT), is_dst=None)
                utc_actual_dt = actual_local_dt.astimezone(
                    pytz.utc).strftime(DATETIME_FORMAT)

            actual_end_date = str(sheet.row_values(row)[17]).strip()
            utc_actual_end_dt = ''
            actual_end_hr2 = ['', '']
            actual_end_am_pm = ''
            if actual_end_date:
                actual_end_date = datetime.datetime.strptime(
                    actual_end_date, "%m/%d/%y").strftime("%Y-%m-%d")
                actual_end_hr_set = str(sheet.row_values(row)[18]).strip()
                actual_end_hr_time = actual_end_hr_set.split(' ')
                actual_end_hr2 = actual_end_hr_time[0].split(':')
                actual_end_hour = int(actual_end_hr2[0])
                # print "actual_end_hr_time", actual_end_hr_time
                if actual_end_hr_time[1] and actual_end_hr_time[1] == 'PM':
                    actual_end_am_pm = "pm"
                    if actual_end_hour < 12:
                        actual_end_hour += 12
                    # if not int(actual_end_hr2[0]) == 12:
                    #     actual_end_hr2[0] = int(actual_end_hr2[0]) + 12
                elif actual_end_hr_time[1] and actual_end_hr_time[1] == 'AM':
                    actual_end_am_pm = "am"
                    if actual_end_hour == 12:
                        actual_end_hr2[0] = 0
                actual_end = str(actual_end_date) + ' ' + \
                             str(actual_end_hour) + ':' + \
                             str(actual_end_hr2[1]) + ':00'
                actual_end_local_dt = tz.localize(datetime.datetime.strptime(
                    actual_end, DATETIME_FORMAT), is_dst=None)
                utc_actual_end_dt = actual_end_local_dt.astimezone(
                    pytz.utc).strftime(DATETIME_FORMAT)

            event_start_date = str(sheet.row_values(row)[9]).strip()
            if event_start_date:
                event_start_date = datetime.datetime.strptime(
                    event_start_date, "%m/%d/%y").strftime("%Y-%m-%d")
                start_hr_set = str(sheet.row_values(row)[10]).strip()
                start_hr_time = start_hr_set.split(' ')
                start_hr2 = start_hr_time[0].split(':')
                start_hour = int(start_hr2[0])
                if start_hr_time[1]:
                    if start_hr_time[1] == 'PM':
                        am_pm = 'pm'
                        if start_hour < 12:
                            start_hour += 12
                    if start_hr_time[1] == 'AM':
                        am_pm = 'am'
                        if start_hour == 12:
                            start_hour = 0

                event_start = str(event_start_date) + ' ' + \
                              str(start_hour) + ':' + str(start_hr2[1]) + ':00'
                local_dt = tz.localize(datetime.datetime.strptime(
                    event_start, DATETIME_FORMAT), is_dst=None)
                utc_dt = local_dt.astimezone(
                    pytz.utc).strftime(DATETIME_FORMAT)
            event_end_date = str(sheet.row_values(row)[11]).strip()
            if event_end_date:
                event_end_date = datetime.datetime.strptime(
                    event_end_date, "%m/%d/%y").strftime("%Y-%m-%d")
                end_hr_set = str(sheet.row_values(row)[12]).strip()
                end_hr_time = end_hr_set.split(' ')
                end_hr2 = end_hr_time[0].split(':')
                end_hour = int(end_hr2[0])
                if end_hr_time[1]:
                    if end_hr_time[1] == 'PM':
                        end_am_pm = 'pm'
                        if end_hour < 12:
                            end_hour += 12
                    if end_hr_time[1] == 'AM':
                        end_am_pm = 'am'
                        if end_hour == 12:
                            end_hour = 0

                event_end = str(event_end_date) + ' ' + \
                            str(end_hour) + ':' + str(end_hr2[1]) + ':00'
                local_dt1 = tz2.localize(datetime.datetime.strptime(
                    event_end, DATETIME_FORMAT), is_dst=None)
                utc_dt1 = local_dt1.astimezone(
                    pytz.utc).strftime(DATETIME_FORMAT)
            interpretor1 = interpretor2 = False
            if str(sheet.row_values(row)[48]).strip():
                interpretor1 = str(sheet.row_values(row)[48]).strip().split(' ')
                interpretor1 = interpretor1[-1]
                interpretor1 = interpretor1.replace('(', '')
                interpretor1 = interpretor1.replace(')', '')
                interpretor1 = int(interpretor1)
            if str(sheet.row_values(row)[50]).strip():
                interpretor2 = str(sheet.row_values(row)[50]).strip().split(' ')
                interpretor2 = interpretor2[-1]
                interpretor2 = interpretor2.replace('(', '')
                interpretor2 = interpretor2.replace(')', '')
                interpretor2 = int(interpretor2)
            interpretor_id = partner_obj.search(['|', ('globelink_id', '=', interpretor1), (
                'globelink_id', '=', interpretor2), ('cust_type', '=', 'interpreter')])
            if interpretor_id and language_id:
                interpretor_lang_id = self.env['interpreter.language'].sudo().search(
                    [('name', '=', language_id), ('interpreter_id', '=', interpretor_id[0].id)])
                if not interpretor_lang_id:
                    self.env['interpreter.language'].create({
                        'name': language_id,
                        'interpreter_id': interpretor_id[0].id,
                        'company_id': company_id
                    })

            # state = False
            # if str(sheet.row_values(row)[115]).strip() == 'Cancelled':
            #     state = 'cancel'
            # if not str(sheet.row_values(row)[48]).strip() and not str(sheet.row_values(row)[48]).strip() and str(sheet.row_values(row)[115]).strip() == 'Open':
            #     state = 'draft'
            event_dict = {
                'user_id': user_id.id if user_id else False,
                'company_id': company_id,
                'event_note': event_note,
                'interpreter_note': interpretor_note,
                'partner_id': customer_id.id if customer_id else False,
                'ordering_partner_id': ordering_partner_id.id if ordering_partner_id else False,
                'patient_id': patient_id.id if patient_id else patient_obj.search([])[0].id,
                'ordering_contact_id': ordering_contact_id[0].id if ordering_contact_id else False,
                'language_id': language_id or False,
                'medical_no': str(sheet.row_values(row)[115]).strip() or False,
                'certification_level_id': certification_level_id.id if certification_level_id else False,
                'appointment_type_id': appointment_type_id.id if appointment_type_id else False,
                'comment': str(sheet.row_values(row)[176]).strip() or False,
                'cust_note': str(sheet.row_values(row)[253]).strip() or False,
                'event_start_date': event_start_date or False,
                'event_end_date': event_end_date or False,
                'event_start': utc_dt or False,
                'event_end': utc_dt1 or False,
                'event_start_hr': str(start_hr2[0]) or False,
                'event_start_min': str(start_hr2[1]) or False,
                'am_pm': am_pm or False,
                'event_end_hr': str(end_hr2[0]) or False,
                'event_end_min': str(end_hr2[1]) or False,
                'am_pm2': end_am_pm or False,
                'customer_timezone': 'US/Pacific',
                'actual_event_start': utc_actual_dt or False,
                'actual_event_end': utc_actual_end_dt or False,
                'actual_start_date': actual_start_date or False,
                'actual_start_hr': str(actual_start_hr2[0]) or False,
                'actual_start_min': str(actual_start_hr2[1]) or False,
                'actual_start_am_pm': actual_start_am_pm or False,
                'actual_end_date': actual_end_date or False,
                'actual_end_hr': str(actual_end_hr2[0]) or False,
                'actual_end_min': str(actual_end_hr2[1]) or False,
                'actual_end_am_pm': actual_end_am_pm or False,
                'location_id': location_id.id if location_id else False,
                'interpreter_id2': interpretor_id[0].id if interpretor_id.exists() else False,
                'assigned_interpreters': [(6, 0, [interpretor_id[0].id])] if interpretor_id.exists() else [],
                'scheduler_id': user_obj.get_migration_user_id()
                # 'state': state or False
            }
            print "event_dict",event_dict

            invoice_status = str(sheet.row_values(row)[192]).strip()
            invoice_number = str(sheet.row_values(row)[193]).strip()
            project_date_time_result = False
            # print 'event_dict["actual_start_am_pm"]', event_dict["actual_start_am_pm"]
            # print 'event_dict["actual_end_am_pm"]', event_dict["actual_end_am_pm"]
            # print 'event_dict["assigned_interpreters"]', event_dict["assigned_interpreters"]
            if actual_start_date:
                project_date_time_result = self.compare_project_date_time(actual_start_date,
                                                                          int(event_dict["actual_start_hr"]),
                                                                          int(event_dict["actual_start_min"]),
                                                                          event_dict["actual_start_am_pm"],
                                                                          int(event_dict["actual_end_hr"]),
                                                                          int(event_dict["actual_end_min"]),
                                                                          event_dict["actual_end_am_pm"])
            # event_overlap = self.event_overlap(event_dict["event_start_date"], event_dict["event_start"], event_dict["event_end"], event_dict["interpreter_id2"], company_id)
            # if event_overlap:
            #     invalid_entries.append(str(row) + ": Event Interperter Overlap")
            # el
            if not project_date_time_result and event_dict["actual_event_start"] and event_dict["actual_event_end"] and event_dict["actual_event_start"] < event_dict["actual_event_end"]:
                processed_dt = self.process_dates(event_dict["actual_event_start"], event_dict["actual_event_end"])
                if processed_dt:
                    event_dict['actual_event_start'] = processed_dt["start_dt"]
                    event_dict['actual_start_date'] = processed_dt["start_date"]
                    event_dict['actual_start_hr'] = processed_dt["start_hr"]
                    event_dict['actual_start_min'] = processed_dt["start_min"]
                    event_dict['actual_start_am_pm'] = processed_dt["start_am_pm"]
                    event_dict['actual_event_end'] = processed_dt["end_dt"]
                    event_dict['actual_end_date'] = processed_dt["end_date"]
                    event_dict['actual_end_hr'] = processed_dt["end_hr"]
                    event_dict['actual_end_min'] = processed_dt["end_min"]
                    event_dict['actual_end_am_pm'] = processed_dt["end_am_pm"]

                processed_dt = self.process_dates(event_dict["event_start"], event_dict["event_end"])
                if processed_dt:
                    event_dict['event_start'] = processed_dt["start_dt"]
                    event_dict['event_start_date'] = processed_dt["start_date"]
                    event_dict['event_start_hr'] = processed_dt["start_hr"]
                    event_dict['event_start_min'] = processed_dt["start_min"]
                    event_dict['am_pm'] = processed_dt["start_am_pm"]
                    event_dict['event_end'] = processed_dt["end_dt"]
                    event_dict['event_end_date'] = processed_dt["end_date"]
                    event_dict['event_end_hr'] = processed_dt["end_hr"]
                    event_dict['event_end_min'] = processed_dt["end_min"]
                    event_dict['am_pm2'] = processed_dt["end_am_pm"]

                project_date_time_result = self.compare_project_date_time(actual_start_date,
                                                                          int(event_dict["actual_start_hr"]),
                                                                          int(event_dict["actual_start_min"]),
                                                                          event_dict["actual_start_am_pm"],
                                                                          int(event_dict["actual_end_hr"]),
                                                                          int(event_dict["actual_end_min"]),
                                                                          event_dict["actual_end_am_pm"])

                if not project_date_time_result:
                    invalid_entries.append(str(row) + ": Event(2 days) project_date_time")
            if not language_id:
                invalid_entries.append(str(job_id) + " Language")
            elif event_dict["event_end"] <= event_dict["event_start"] or (event_dict["actual_event_end"] and event_dict["actual_event_end"] <= event_dict["actual_event_start"]):
                invalid_entries.append(str(job_id) + ": Event end <= event start")
            elif not event_dict["partner_id"]:
                invalid_entries.append(str(job_id) + ": Customer does not exists- column number 21")
            else:
                event_id = event_obj.sudo().search([('globelink_id', '=', job_id)])

                if event_id:
                    event_obj.write(event_dict)
                    if str(sheet.row_values(row)[60]).strip() == 'Cancelled':
                        event_id.sudo().write({'state': 'cancel'})
                    else:
                        self.update_event_details(event_id, event_dict, invoice_status, invoice_number, sheet, row)
                        # if str(sheet.row_values(row)[48]).strip() or str(sheet.row_values(row)[50]).strip():
                        #     project_task_id = self.env['project.task'].search(
                        #         [('event_id', '=', event_id.id), ('company_id', '=', company_id)])
                        #     # ------change code for 2 interpretor
                        #     project_task_work_id = self.env['project.task.work'].sudo().search(
                        #         [('task_id', '=', project_task_id.id), ('company_id', '=', company_id)])
                        #     event_out_come_id = self.env['event.out.come'].sudo().search([])
                        #     if not event_out_come_id:
                        #         event_out_come_id = self.env['event.out.come'].sudo().create({
                        #             'name': 'pass'
                        #         })
                        #     project_task_work_id.sudo().write({
                        #         'event_start_date': event_start_date,
                        #         'event_start_hr': str(start_hr2[0]),
                        #         'event_start_min': str(start_hr2[1]),
                        #         'am_pm': am_pm,
                        #         'event_end_hr': str(end_hr2[0]),
                        #         'event_end_min': str(end_hr2[1]),
                        #         'am_pm2': end_am_pm,
                        #         'event_out_come_id': event_out_come_id[0].id
                        #     })
                        #     event_id.sudo().view_event_billing_form()
                        #     billing_form_id = self.env['billing.form'].search(
                        #         [('event_id', '=', event_id.id)])
                        #     event_lines_id = self.env['event.lines'].search(
                        #         [('event_id', '=', event_id.id), ('billing_form_id', '=', billing_form_id[0].id)])
                        #     if event_lines_id.exists():
                        #         event_lines_id[0].select_event()
                        #         if str(sheet.row_values(row)[192]).strip() == 'Invoiced':
                        #             if event_id.cust_invoice_id.exists() or event_id.supp_invoice_ids.exists() or event_id.supp_invoice_id2.exists() or event_id.state == 'invoiced':
                        #                 pass
                        #             else:
                        #                 event_lines_id.sudo().billing_form_id.create_invoices()
                    updated_entries.append(event_id.id)
                else:
                    event_dict.update({'globelink_id': job_id})
                    event_id = event_obj.create(event_dict)
                    if str(sheet.row_values(row)[60]).strip() == 'Cancelled':
                        event_id.write({'state': 'cancel'})
                    elif str(sheet.row_values(row)[60]).strip() == 'New':
                        event_id.write({'state': 'draft'})
                    elif str(sheet.row_values(row)[60]).strip() in (
                            'Open', 'Assigned', 'Confirmed', 'Closed', 'Offered', 'Unfulfilled', 'Non-Attendance'):
                        self.update_event_details(event_id, event_dict, invoice_status, invoice_number, sheet, row)
                        # # if str(sheet.row_values(row)[48]).strip() or str(sheet.row_values(row)[50]).strip():
                        # if event_dict["interpreter_id2"]:
                        #     event_id.assign_interpeter_manual()
                        #     _logger.info("\n\n Assigning the Interpreter %s for the event %s" % (str(event_dict["interpreter_id2"]), str(event_id) ))
                        #     event_id.write({'assigned_interpreters': [
                        #         (6, 0, [event_dict["interpreter_id2"]])]})
                        #     event_id.confirm_event()
                        #     if event_dict["actual_event_start"] and event_dict["actual_event_end"]:
                        #         event_id.enter_timesheet()
                        #         project_task_id = self.env['project.task'].sudo().search(
                        #             [('event_id', '=', event_id.id), ('company_id', '=', company_id)])
                        #         # ------change code for 2 interpretor
                        #         project_task_work_id = self.env['project.task.work'].sudo().search(
                        #             [('task_id', '=', project_task_id.id), ('company_id', '=', company_id)])
                        #         event_out_come_id = self.env['event.out.come'].sudo().search([])
                        #         if not event_out_come_id:
                        #             event_out_come_id = self.env['event.out.come'].sudo().create({
                        #                 'name': '1 Normal completion'
                        #             })
                        #             # start_hr2[1]), str(end_hr2[0]), str(end_hr2[1]))
                        #         project_task_work_id.sudo().write({
                        #             'event_start_date': event_start_date,
                        #             # 'task_id':project_task_id.id,
                        #             'event_start_hr': str(start_hr2[0]),
                        #             'event_start_min': str(start_hr2[1]),
                        #             'am_pm': am_pm,
                        #             'event_end_hr': str(end_hr2[0]),
                        #             'event_end_min': str(end_hr2[1]),
                        #             'am_pm2': end_am_pm,
                        #             'event_out_come_id': event_out_come_id[0].id
                        #         })
                        #         event_id.sudo().view_event_billing_form()
                        #         billing_form_id = self.env['billing.form'].sudo().search(
                        #             [('event_id', '=', event_id.id)])
                        #         event_lines_id = self.env['event.lines'].sudo().search(
                        #             [('event_id', '=', event_id.id), ('billing_form_id', '=', billing_form_id[0].id)])
                        #         if event_lines_id.exists():
                        #             event_lines_id[0].select_event()
                        #             # need to add invoice number also
                        #             if str(sheet.row_values(row)[192]).strip() == 'Invoiced':
                        #                 if event_id.cust_invoice_id.exists() or event_id.supp_invoice_ids.exists() or event_id.supp_invoice_id2.exists() or event_id.state == 'invoiced':
                        #                     pass
                        #                 else:
                        #                     event_lines_id.billing_form_id.sudo().create_invoices()
                    created_entries.append(event_id.id)
        self.call_message_wiz(
            updated_entries, created_entries, invalid_entries, upload_type='event', start_datetime=start_datetime)

    def update_event_details(self, event_id, event_dict, invoice_status, invoice_number, sheet, row):
        result = True
        # if event_dict["interpreter_id2"]:
        #     all_interpreter_list = event_id.interpreter_ids + event_id.interpreter_ids2
        #     for select_line in all_interpreter_list:
        #         if select_line.interpreter_id:
        #             if select_line.state in (
        #             'draft', 'voicemailsent') and select_line.interpreter_id.id == event_id.interpreter_id2.id:
        #                 result = False
        #     if result:
        # event_id.assign_interpeter_manual()
        # select_obj = self.env['select.interpreter.line']
        # int_line_id = select_obj.create(
        #     {'interpreter_id': event_id.interpreter_id2.id, 'rate': categ_rate, 'event_id': event.id,
        #      'visited': False, 'visited_date': False,
        #      'state': 'draft', 'voicemail_msg': ''})
        # _logger.info('--------------------------------assign_interpeter manual -------------------')
        # res = event_id.write({'state': 'scheduled', 'interpreter_ids2': [(4, int_line_id.id)]})
        #
        # _logger.info("\n\n Assigning the Interpreter %s for the event %s" % (
        #     str(event_dict["interpreter_id2"]), str(event_id)))
        # event_id.write({'assigned_interpreters': [
        #     (6, 0, [event_dict["interpreter_id2"]])]})
        event_id.confirm_event()
        if event_dict["actual_event_start"] and event_dict["actual_event_end"]:
            event_id.enter_timesheet()
            project_task_id = self.env['project.task'].sudo().search(
                [('event_id', '=', event_id.id), ('company_id', '=', event_dict["company_id"])], limit=1)
            # ------change code for 2 interpretor
            project_task_work_id = self.env['project.task.work'].sudo().search(
                [('task_id', '=', project_task_id.id), ('company_id', '=', event_dict["company_id"])])
            event_out_come_id = self.env['event.out.come'].sudo().search([])
            if not event_out_come_id:
                event_out_come_id = self.env['event.out.come'].sudo().create({
                    'name': '1 Normal completion'
                })
            _logger.info('event_dict["actual_start_date"] %s' % str(event_dict["actual_start_date"]))
            project_task_work_id.sudo().write({
                'event_start_date': event_dict["actual_start_date"],
                'event_start_hr': event_dict["actual_start_hr"],
                'event_start_min': event_dict["actual_start_min"],
                'am_pm': event_dict["actual_start_am_pm"],
                'event_end_hr': event_dict["actual_end_hr"],
                'event_end_min': event_dict["actual_end_min"],
                'am_pm2': event_dict["actual_end_am_pm"],
                'event_out_come_id': event_out_come_id[0].id,
            })
            event_id.sudo().view_event_billing_form()
            billing_form_id = self.env['billing.form'].sudo().search(
                [('event_id', '=', event_id.id)])
            event_lines_id = self.env['event.lines'].sudo().search(
                [('event_id', '=', event_id.id), ('billing_form_id', '=', billing_form_id[0].id)])
            if event_lines_id.exists():
                event_lines_id[0].select_event()
                # need to add invoice number also
                if invoice_status == 'Invoiced':
                    if not event_id.cust_invoice_id.exists() and not event_id.supp_invoice_ids.exists() and not event_id.supp_invoice_id2.exists() and event_id.state != 'invoiced':
                        event_lines_id.billing_form_id.sudo().create_invoices()
                        if invoice_number:
                            event_id.write({'state': 'invoiced'})
                            invoice_id = self.env['account.invoice'].search([('event_id', '=', event_id.id)])
                            for invoice in invoice_id:
                                invoice.write({'quick_id': invoice_number})
                                inv_line_id = self.env['account.invoice.line'].search([('invoice_id','=',invoice.id)])
                                for inv_line in inv_line_id:
                                    if inv_line.invoice_id.type == 'out_invoice':
                                        inv_line.write({'price_unit': str(sheet.row_values(row)[196]).strip()})
                                    elif inv_line.invoice_id.type == 'in_invoice':
                                        inv_line.write({'price_unit': str(sheet.row_values(row)[225]).strip()})
                                    
        return result

    def compare_project_date_time(self, event_start_date, event_start_hr, event_start_min, am_pm, event_end_hr,
                                  event_end_min, am_pm2):
        result = True
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if event_start_hr and event_start_hr > 12:
            result = False
        if event_start_min and event_start_min > 59:
            result = False
        if event_end_hr and event_end_hr > 12:
            result = False
        if event_end_min and event_end_min > 59:
            result = False
        if event_start_hr < 1 and event_start_min < 1:
            result = False
        if event_end_hr < 1 and event_end_min < 1:
            result = False
        if am_pm and am_pm == 'pm':
            if event_start_hr < 12:
                event_start_hr += 12
        if am_pm and am_pm == 'am':
            if event_start_hr == 12:
                event_start_hr = 0
        if event_start_hr == 24:  # for the 24 hour format
            event_start_hr = 23
            event_start_min = 59
        event_start = str(event_start_date) + ' ' + str(event_start_hr) + ':' + str(event_start_min) + ':00'
        if am_pm2 and am_pm2 == 'pm':
            if event_end_hr < 12:
                event_end_hr += 12
        if am_pm2 and am_pm2 == 'am':
            if event_end_hr == 12:
                event_end_hr = 0
        if event_end_hr == 24:  # for the 24 hour format
            event_end_hr = 23
            event_end_min = 59
        event_end = str(event_start_date) + ' ' + str(event_end_hr) + ':' + str(event_end_min) + ':00'
        if datetime.datetime.strptime(event_end, DATETIME_FORMAT) < datetime.datetime.strptime(event_start,
                                                                                               DATETIME_FORMAT):
            result = False
        elif datetime.datetime.strptime(event_end, DATETIME_FORMAT) == datetime.datetime.strptime(event_start,
                                                                                                  DATETIME_FORMAT):
            result = False
        return result

    @staticmethod
    def process_dates(start_dt, end_dt):
        dt = {}
        # print "end_dt", end_dt
        # print "start_dt", start_dt
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if start_dt and end_dt and start_dt < end_dt:
            start_dt = datetime.datetime.strptime(start_dt, DATETIME_FORMAT)
            end_dt = datetime.datetime.strptime(end_dt, DATETIME_FORMAT)
            end_date = end_dt.date()
            end_start_datetime = datetime.datetime.strptime(end_date.strftime('%Y-%m-%d') + " 00:00:00",
                                                            '%Y-%m-%d %H:%M:%S')
            diff = end_dt - end_start_datetime
            start_dt -= diff
            end_dt -= diff
            start_dt = start_dt + timedelta(minutes=1)
            end_dt = end_dt - timedelta(minutes=1)



            dt["start_date"] = start_dt.date().strftime("%Y-%m-%d")
            dt["start_hr"] = start_dt.strftime("%I")
            dt["start_min"] = start_dt.strftime("%M")
            dt["start_am_pm"] = start_dt.strftime("%p").lower()
            tz = pytz.timezone('US/Pacific') or pytz.utc
            actual_start_local_dt = tz.localize(start_dt, is_dst=None)
            utc_actual_start_dt = actual_start_local_dt.astimezone(
                pytz.utc).strftime(DATETIME_FORMAT)
            dt["start_dt"] = utc_actual_start_dt
            dt["end_date"] = end_dt.date().strftime("%Y-%m-%d")
            dt["end_hr"] = end_dt.strftime("%I")
            dt["end_min"] = end_dt.strftime("%M")
            dt["end_am_pm"] = end_dt.strftime("%p").lower()
            actual_end_local_dt = tz.localize(end_dt, is_dst=None)
            utc_actual_end_dt = actual_end_local_dt.astimezone(
                pytz.utc).strftime(DATETIME_FORMAT)
            dt["end_dt"] = utc_actual_end_dt
        # print "dt", dt
        return dt

    # def event_overlap(self, event_start_date, event_start, event_end, interpreter_id2, company_id):
    #     overlap = False

    #     history_obj = self.env['interpreter.alloc.history']
    #     history_ids2 = history_obj.sudo().search(
    #         [('name', '=', interpreter_id2), ('state', 'in', ('confirm', 'allocated')),
    #          ('company_id', '=', company_id), ('cancel_date', '=', False),
    #          ('event_start_date', '=', event_start_date)])
    #     for history_browse in history_ids2:
    #         if (event_start > history_browse.event_start and event_end < history_browse.event_end):
    #             overlap = True
    #         elif (event_start > history_browse.event_start and event_start < history_browse.event_end):
    #             overlap = True
    #         elif (event_end > history_browse.event_start and event_end < history_browse.event_end):
    #             overlap = True
    #         elif (event_start == history_browse.event_start or event_end == history_browse.event_end):
    #             overlap = True
    #         elif (history_browse.event_start > event_start and history_browse.event_start < event_end):
    #             overlap = True
    #         elif (history_browse.event_end < event_end and history_browse.event_end > event_start):
    #             overlap = True
    #     return overlap

