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

class DataMigration(models.TransientModel):
    _name='data.migration.wizard'

    upload_file = fields.Binary(string='File URL')
    upload_error= fields.Binary(string='Click To Download Error Log')
    upload_error_file_name=fields.Char("File name")
# export rate under configuration from rate.csv
    @api.multi
    def import_rate(self):
        file_obj = '/home/iuadmin/rate_210317.csv'
        lis = csv.reader(open(file_obj, 'rU'), delimiter=",")
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
                    rate_id=self.env['rate'].search([('rate_old_id','=',row[9].strip() or '')],limit=1)
                    company=row[9].strip() or ''
                    customer=row[23].strip() or ''
                    uom = row[11].strip() or ''
                    name = row[17].strip() or ''
                    is_billing_rate = row[8].strip() or ''
                    default_rate = row[10].strip() or 0.00
                    spanish_regular = row[15].strip() or 0.00
                    spanish_licenced = row[13].strip() or 0.00
                    spanish_certified = row[16].strip() or 0.00
                    exotic_certified = row[12].strip() or 0.00
                    exotic_high = row[5].strip() or 0.00
                    exotic_regular = row[7].strip() or 0.00
                    exotic_middle = row[6].strip() or 0.00
                    rateid=row[14].strip() or ''
                    base_hour=row[24].strip() or ''
                    inc_min=row[22].strip() or ''
                    rate_type=row[25].strip() or 0.0
                    partner_id=self.env['res.partner'].search([('customer_record_old_id','=',customer)],limit=1)
                    # company_id=self.env['res.company'].search([('res_company_old_id','=',company)])
                    # uom_id=self.env['product.uom'].search([('','=',uom)])
                    rate_vals={
                        'partner_id':partner_id.id if partner_id else False ,
                        # 'company_id':company_id.id if company_id else False ,
                        'name':name,
                        'is_billing_rate':False if is_billing_rate=='False' else True,
                        'default_rate':default_rate,
                        'spanish_licenced':spanish_licenced,
                        'exotic_regular':exotic_regular,
                        'exotic_middle':exotic_middle,
                        'uom_id':uom if uom else False,
                        'spanish_regular':spanish_regular,
                        'spanish_certified':spanish_certified,
                        'exotic_certified':exotic_certified,
                        'exotic_high':exotic_high,
                        'base_hour':base_hour,
                        'inc_min':inc_min,
                        'rate_type':rate_type,
                        'rate_id':int(rateid) if rateid else 0,
                        'rate_old_id':row[0].strip() or ''
                    }
                    if rate_id:
                        rate_id.write(rate_vals)
                    else:
                        rate_id = self.env['rate'].create(rate_vals)
                    self._cr.commit()
            except Exception as e:
                self._cr.rollback()
                _logger.error('------------error log_id exception---------- %s', e)
                row.append(row_num)
                row.append(e)
                faulty_rows.append(row)
            row_num += 1
        csvfile = StringIO.StringIO()
        w = csv.writer(csvfile, delimiter=',')
        w.writerow(header)
        w.writerows(faulty_rows)
        file_data = csvfile.getvalue()
        self.upload_error = base64.encodestring(bytes(file_data))
        self.upload_error_file_name = 'Rate Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }

# function to import zip code has relation with other model
    @api.multi
    def import_zipcode(self):
        csv_datas = self.upload_file
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
                    zip_code_old_id = row[0].strip()
                    name = row[6].strip() or ''
                    city = row[5].strip() or ''
                    state = row[11].strip() or 0.00
                    time_zone = row[9].strip() or 0.00
                    latitude = row[10].strip() or 0.00
                    longitude = row[8].strip() or 0.00
                    latitude_rad = row[13].strip() or 0.00
                    longtitude_rad = row[14].strip() or ''
                    zip_code_id = row[12].strip() or ''
                    company = row[7].strip() or ''
                    company_id = self.env['res.company'].search([('res_company_old_id', '=', company)])
                    state_id = self.env['res.country.state'].search([('state7_id', '=', state)])
                    # code here

                    zip_code_vals = {
                        'zip_code_old_id': zip_code_old_id,
                        'name': name,
                        'city': city,
                        'state_id': state_id.id,
                        'time_zone': time_zone,
                        'latitude': float(latitude) if latitude else 0.0,
                        'longitude': float(longitude) if longitude else 0.0,
                        'latitude_rad': float(latitude_rad) if latitude_rad else 0.0,
                        'longtitude_rad': float(longtitude_rad) if longtitude_rad else 0.0,
                        'zip_code_id': int(zip_code_id) if zip_code_id else 0,
                        'company_id': company_id.id,
                    }
                    zip_code_new_id = self.env['zip.code'].create(zip_code_vals)
                    _logger.error('------------zip_code_new_id---------- %s', zip_code_new_id)

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
        self.upload_error = base64.encodestring(bytes(file_data))
        self.upload_error_file_name = 'zip code Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }

    # function for IU Contract import
    @api.multi
    def import_iucontract(self):
        csv_datas = self.upload_file
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
                    iu_contract_old_id = row[0].strip()
                    name = row[5].strip() or ''
                    start_date = row[11].strip() or ''
                    end_date = row[6].strip() or ''
                    amount = row[10].strip() or ''
                    notes = row[7].strip() or ''
                    accumulator = row[9].strip() or 0.00
                    contract_id = row[12].strip() or 0.00
                    company=row[8].strip() or ''
                    company_id=self.env['res.company'].search([('res_company_old_id','=',company)])
                    if start_date:
                        start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime(DF)
                    else:
                        start_date = False
                    if end_date:
                        end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime(DF)
                    else:
                        end_date = False
                    iucontract_vals={
                        'name':name,
                        'start_date':start_date,
                        'end_date':end_date,
                        'amount':amount,
                        'notes':notes,
                        'accumulator':accumulator,
                        'contract_id':contract_id,
                        'company_id':company_id.id,
                        'iu_contract_old_id':int(iu_contract_old_id),
                    }
                    iucontract_id=self.env['iu.contract'].create(iucontract_vals)

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
        self.upload_error = base64.encodestring(bytes(file_data))
        self.upload_error_file_name = 'IU Contract Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }
# function for appointment type, before create appointment create group
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
                    name = row[1].strip() or ''
                    appointment_type_group = row[2].strip() or ''
                    appointment_type_id = row[3].strip() or 0.0
                    is_medical_legal = row[4].strip() or ''
                    company = row[8].strip() or ''
                    appointment_type_group_id=self.env['appointment.type.group'].search([('name','=',appointment_type_group)])
                    company_id = self.env['res.company'].search(['name', '=', company])
                    appoint_type_vals={
                        'name':name,
                        'appointment_type_group_id':appointment_type_group_id.id,
                        'appointment_type_id':appointment_type_id,
                        'is_medical_legal':False if is_medical_legal=='False' else True,
                        'company_id':company_id.id
                    }
                    appointment_type_new_id=self.env['appointment.type'].create(appoint_type_vals)

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
        self.upload_error = base64.encodestring(bytes(file_data))
        self.upload_error_file_name = 'Appointment Type Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }
# function for importing degree subject
    @api.multi
    def import_degree_subject(self):
        csv_datas = self.upload_file
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
                    name = row[1].strip() or ''
                    degree_subject_id = row[2].strip() or 0.0
                    company = row[3].strip() or ''
                    company_id = self.env['res.company'].search(['name', '=', company])
                    degree_subject_vals = {
                        'name': name,
                        'degree_subject_id': degree_subject_id,
                        'company_id': company_id.id
                    }
                    degree_subject_new_id = self.env['degree.subject'].create(degree_subject_vals)

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
        self.upload_error = base64.encodestring(bytes(file_data))
        self.upload_error_file_name = 'degree subject Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }
# function to import cancel reason, dumb data found
    @api.multi
    def import_cancel_reason(self):
        csv_datas = self.upload_file
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
                    cancel_reason_old_id = row[0].strip() or ''
                    name = row[6].strip() or ''
                    do_active = row[8].strip() or 0.0
                    cancel_reason_id = row[5].strip() or 0.0
                    company = row[7].strip() or ''
                    company_id = self.env['res.company'].search([('res_company_old_id','=',company)],limit=1).id
                    cancel_reason_vals = {
                        'cancel_reason_old_id':int(cancel_reason_old_id),
                        'name': name,
                        'do_active': False if do_active=='f' else True,
                        'company_id': company_id,
                        'cancel_reason_id':int(cancel_reason_id),
                    }
                    cancel_reason_new_id = self.env['cancel.reason'].create(cancel_reason_vals)

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
        self.upload_error = base64.encodestring(bytes(file_data))
        self.upload_error_file_name = 'Cancel reason Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }
# function to import degree type, dumb data found
    @api.multi
    def import_degree_type(self):
        csv_datas = self.upload_file
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
                    name = row[1].strip() or ''
                    degree_type_id = row[2].strip() or 0.0
                    company = row[4].strip() or ''
                    company_id = self.env['res.company'].search(['name', '=', company])
                    degree_type_vals = {
                        'name': name,
                        'degree_type_id': degree_type_id,
                        'company_id': company_id.id
                    }
                    degree_type_new_id = self.env['degree.type'].create(degree_type_vals)

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
        self.upload_error = base64.encodestring(bytes(file_data))
        self.upload_error_file_name = 'Degree Type Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }
# function to import certification level no relation except company
    @api.multi
    def import_certification_level(self):
        csv_datas = self.upload_file
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
                    certification_level_old_id = row[0].strip()
                    name = row[1].strip() or ''
                    is_required_certification = row[2].strip() or 0.0
                    certification_level_id = row[2].strip() or 0.0
                    active = row[2].strip() or ''
                    company = row[4].strip() or ''
                    company_id = self.env['res.company'].search(['name', '=', company])
                    certification_level_vals = {
                        'certification_level_old_id':certification_level_old_id,
                        'name': name,
                        'is_required_certification': True if is_required_certification=='True' else False,
                        'certification_level_id':certification_level_id,
                        'active':True if active=='True' else False,
                        'company_id': company_id.id
                    }
                    certification_level_new_id = self.env['certification.level'].create(certification_level_vals)

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
        self.upload_error = base64.encodestring(bytes(file_data))
        self.upload_error_file_name = 'Certification Level Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }
# function to import zone
    @api.multi
    def import_zone(self):
        csv_datas = self.upload_file
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
                    zone_old_id = row[0].strip()
                    name = row[8].strip() or ''
                    meta_zone = row[5].strip() or 0.0
                    meta_zone_id = self.env['meta.zone'].search([('meta_zone_old_id', '=', meta_zone)])
                    company = row[7].strip() or ''
                    company_id = self.env['res.company'].search([('res_company_old_id', '=', company)])
                    zone_id = row[6].strip() or 0.0
                    zone_vals = {
                        'zone_old_id': zone_old_id,
                        'name': name,
                        'meta_zone_id': meta_zone_id.id,
                        'zone_id': int(zone_id) if zone_id else 0,
                        'company_id': company_id.id

                    }
                    zone_new_id = self.env['zone'].create(zone_vals)


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
        self.upload_error = base64.encodestring(bytes(file_data))
        self.upload_error_file_name = 'zone Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }
#function to import meta zone
    @api.multi
    def import_metazone(self):
        csv_datas = self.upload_file
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
                    meta_zone_old_id = row[0].strip()
                    name = row[6].strip() or ''
                    meta_zone_id = row[5].strip() or 0.0
                    company = row[7].strip() or ''
                    company_id = self.env['res.company'].search([('res_company_old_id', '=', company)])
                    meta_zone_vals = {
                        'meta_zone_old_id': meta_zone_old_id,
                        'name': name,
                        'meta_zone_id': int(meta_zone_id) if meta_zone_id else 0,
                        'company_id': company_id.id,
                    }
                    meta_zone_new_id = self.env['meta.zone'].create(meta_zone_vals)

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
        self.upload_error = base64.encodestring(bytes(file_data))
        self.upload_error_file_name = 'meta zone Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }
# function to import COA account type mismatch has to be mapped
    @api.multi
    def import_chartofaccount(self):
        csv_datas = self.upload_file
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
                    code = row[1].strip() or ''
                    name = row[2].strip() or 0.0
                    type = row[4].strip() or ''
                    tax_ids = row[4].strip() or ''
                    # currency_id = row[1].strip() or ''
                    reconcile = row[1].strip() or 0.0
                    company = row[4].strip() or ''
                    company_id = self.env['res.company'].search(['name', '=', company])
                    type_id=self.env['account.account.type'].search(['name', '=', type])
                    currency_id=self.env['res.currency'].search(['name', '=', 'USD'])
                    coa_vals={
                        'code':code,
                        'name':name,
                        'type':type_id.id,
                        'currency_id':currency_id.id,
                        'reconcile':True if reconcile=='True' else False,
                        'company_id':company_id.id
                    }
                    coa_id=self.env['account.account'].create(coa_vals)


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
        self.upload_error = base64.encodestring(bytes(file_data))
        self.upload_error_file_name = 'COA Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }
 # function to import journals and data field mismatch from v7
    @api.multi
    def import_journals(self):
        csv_datas = self.upload_file
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
                    _logger.error('------------row_num---------- %s', row_num)
                    name = row[1].strip() or ''
                    type = row[2].strip() or 0.0
                    code = row[3].strip() or ''
                    default_debit = row[4].strip() or ''
                    default_credit = row[5].strip() or ''
                    company=row[5].strip() or ''
                    company_id = self.env['res.company'].search(['name', '=', company])
                    default_debit_account_id=self.env['account.account'].search(['name', '=', default_debit])
                    default_credit_account_id=self.env['account.account'].search(['name', '=', default_credit])
                    journal_vals = {
                        'name': name,
                        'type': type,
                        'code': code,
                        'default_debit_account_id': default_debit_account_id.id,
                        'default_credit_account_id': default_credit_account_id.id,
                        'company_id': company_id.id
                    }
                    journal_id = self.env['account.journal'].create(journal_vals)

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
        self.upload_error = base64.encodestring(bytes(file_data))
        self.upload_error_file_name = 'Journal Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }
# function to import interpreter zip code most of the data are related
    @api.multi
    def import_interpreter_zip_code(self):
        csv_datas = self.upload_file
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
                    _logger.error('------------row_num---------- %s', row_num)
                    zip_code = row[1].strip() or ''
                    interpreter = row[2].strip() or 0.0
                    language = row[3].strip() or 0.0
                    certification_level = row[4].strip() or 0.0
                    company = row[5].strip() or ''
                    company_id = self.env['res.company'].search(['name', '=', company])
                    zip_code_id = self.env['zip.code'].search(['name', '=', zip_code])
                    interpreter_id = self.env['res.partner'].search(['name', '=', interpreter])
                    language_id = self.env['language'].search(['name', '=', language])
                    certification_level_id = self.env['certification.level'].search(['name', '=', certification_level])
                    interpreter_zip_code_vals = {
                        'zip_code_id': zip_code_id.id,
                        'interpreter_id': interpreter_id.id,
                        'language_id': language_id.id,
                        'certification_level_id': certification_level_id.id,
                        'company_id': company_id.id
                    }
                    interpreter_zip_code_id = self.env['interpreter.zip.code'].create(interpreter_zip_code_vals)

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
        self.upload_error = base64.encodestring(bytes(file_data))
        self.upload_error_file_name = 'Degree Type Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }
# function for importing speciality
    @api.multi
    def import_speciality(self):
        csv_datas = self.upload_file
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
                    _logger.error('------------row_num---------- %s', row_num)
                    speciality_old_id = row[0].strip()
                    name = row[6].strip() or ''
                    doctor_id = row[5].strip() or ''
                    company = row[7].strip() or ''
                    company_id = self.env['res.company'].search([('res_company_old_id', '=', int(company))])

                    speciality_vals = {
                        'speciality_old_id':int(speciality_old_id),
                        'name': name,
                        'doctor_id': int(doctor_id) if doctor_id else 0,
                        'company_id': company_id.id,
                    }
                    speciality_id = self.env['speciality'].create(speciality_vals)
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
        self.upload_error = base64.encodestring(bytes(file_data))
        self.upload_error_file_name = 'Speciality Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }
# function to import language  no relation except company
    @api.multi
    def import_language(self):
        csv_datas = self.upload_file
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
                    is_certified_lang = row[1].strip() or ''
                    language_code = row[2].strip() or ''
                    language_id = row[3].strip() or ''
                    iscourt_certified_lang = row[4].strip() or ''
                    active_custom = row[5].strip() or ''
                    company = row[6].strip() or ''
                    name = row[7].strip() or ''
                    lang_group = row[8].strip() or ''
                    company_id = self.env['res.company'].search(['name', '=', company])

                    language_vals = {
                        'name':name,
                        'lang_group':lang_group,
                        'is_certified_lang': True if is_certified_lang=='True' else False,
                        'language_code': language_code,
                        'language_id': language_id,
                        'iscourt_certified_lang': True if iscourt_certified_lang=='True' else False,
                        'active_custom': True if active_custom=='True' else False,
                        'company_id': company_id
                    }
                    language_id = self.env['language'].create(language_vals)
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
        self.upload_error = base64.encodestring(bytes(file_data))
        self.upload_error_file_name = 'Speciality Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }
# function to import doctor
    @api.multi
    def import_doctor(self):
        csv_datas = self.upload_file
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
                    doctor_old_id = row[0].strip()
                    name = row[26].strip() or ''
                    date = row[11].strip() or ''
                    title = row[14].strip() or ''
                    ref = row[17].strip() or ''
                    user = row[13].strip() or ''
                    website = row[19].strip() or ''
                    comment = row[5].strip() or ''
                    active = row[23].strip() or ''
                    function1 = row[15].strip() or ''
                    email = row[12].strip() or ''
                    phone = row[22].strip() or ''
                    fax = row[20].strip() or ''
                    mobile = row[27].strip() or ''
                    birthdate = row[30].strip() or ''
                    phone2 = row[21].strip() or ''
                    email2 = row[12].strip() or ''
                    is_alert = row[32].strip() or ''
                    middle_name = row[24].strip() or ''
                    last_name = row[6].strip() or ''
                    complete_name = row[33].strip() or ''
                    speciality = row[7].strip() or ''
                    gender = row[28].strip() or ''
                    doctor_id = row[31].strip() or ''
                    # city = row[24].strip() or ''
                    # state = row[25].strip() or ''
                    last_update_date = row[35].strip() or ''
                    company_name = row[34].strip() or ''
                    contact = row[36].strip() or ''
                    company = row[16].strip() or ''
                    title_id = self.env['res.partner.title'].search([('res_title_old_id', '=', title)])
                    speciality_id = self.env['speciality'].search([('speciality_old_id', '=', speciality)])
                    # user_id = self.env['res.users'].search(['name', '=', user])
                    company_id = self.env['res.company'].search([('res_company_old_id', '=', company)])
                    if last_update_date:
                        last_update_date = datetime.strptime(last_update_date,"%Y-%m-%d").strftime(DF)
                    else:
                        last_update_date = False
                    if date:
                        date_format = datetime.strptime(date, "%d/%m/%Y %H:%M:%S").strftime(DF)
                    else:
                        date_format = False
                    doc_vals = {
                        'doctor_old_id': int(doctor_old_id),
                        'name': name,
                        'date': date_format,
                        'title': title_id.id,
                        'ref': ref,
                        # 'user_id': user_id.id,
                        'website': website,
                        'comment': comment,
                        'active': True if active == 't' else False,
                        'function': function1,
                        'email': email,
                        'phone': phone,
                        'fax': fax,
                        'mobile': mobile,
                        'birthdate': birthdate,
                        'phone2': phone2,
                        'email2': email2,
                        'is_alert': True if is_alert == 't' else False,
                        'middle_name': middle_name,
                        'last_name': last_name,
                        'complete_name': complete_name,
                        'speciality': speciality_id.id,
                        'gender': gender,
                        'doctor_id': int(doctor_id),
                        # 'city':city,
                        # 'state':state,
                        'last_update_date': last_update_date,
                        'company_name': company_name,
                        'contact': contact,
                        'company_id': company_id.id,
                    }
                    doctor_new_id = self.env['doctor'].create(doc_vals)
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
        self.upload_error = base64.encodestring(bytes(file_data))
        self.upload_error_file_name = 'Doctor Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }
# function to import patient
    @api.multi
    def import_patient(self):
        error_list = []
        header_list = []
        path = '/home/iuadmin/patient_upload'
        # path = '/home/iuadmin/cust_upload/cust_upload'
        for filename in os.listdir(path):
            file_obj = path + '/' + filename
            target_doc = csv.reader(open(file_obj, 'rU'), delimiter=",")
            row_num = 0
            data_dict = {}
            for row in target_doc:
                data_dict.update({row_num: row})
                row.append(row_num)
                row_num += 1
            # faulty_rows = []
            # header = ''
            for key, value in data_dict.items():
                try:
                    if key == 0:
                        header_list.append(value)
                    else:
                        row=value
                        _logger.error('------------rown---------- %s', key)
                        patient_old_id = row[0].strip()
                        patient_obj=self.env['patient'].search([('patient_old_id', '=', patient_old_id)],limit=1)
                        name = row[36].strip() or ''
                        last_name = row[6].strip() or ''
                        complete_name = row[21].strip() or ''
                        user = row[15].strip() or ''
                        # user_id = self.env['res.user'].search([('name', '=', user)])
                        comment = row[5].strip() or ''
                        active = row[34].strip() or ''
                        street = row[9].strip() or ''
                        street2 = row[31].strip() or ''
                        zip = row[38].strip() or ''
                        city = row[13].strip() or ''
                        state = row[50].strip() or ''
                        state_id = self.env['res.country.state'].search([('state7_id', '=', state)],limit=1).id
                        country = row[17].strip() or ''
                        # country_id = self.env['res.country'].search([('id', '=', country)])
                        email = row[25].strip() or ''
                        email2 = row[12].strip() or ''
                        phone = row[33].strip() or ''
                        phone2 = row[29].strip() or ''
                        phone3 = row[30].strip() or ''
                        phone4 = row[32].strip() or ''
                        fax = row[19].strip() or ''
                        mobile = row[27].strip() or ''
                        is_alert = row[37].strip() or ''
                        ssnid = row[41].strip() or ''
                        sinid = row[51].strip() or ''
                        latitude = row[23].strip() or ''
                        longitude = row[10].strip() or ''
                        gender = row[40].strip() or ''
                        company_name = row[22].strip() or ''
                        function = row[26].strip() or ''
                        birthdate = row[42].strip() or ''
                        if birthdate:
                            birthdate_format = datetime.strptime(birthdate, "%Y-%m-%d").strftime(DF)
                        else:
                            birthdate_format =False
                        injury_date = row[19].strip() or ''
                        if injury_date:
                            injury_date_format = datetime.strptime(injury_date, "%Y-%m-%d").strftime(DF)
                        else:
                            injury_date_format=False
                        patient_id = row[43].strip() or ''
                        company = row[18].strip() or ''
                        if company:
                            company_id = self.env['res.company'].search([('res_company_old_id', '=', company)],limit=1).id
                        else:
                            company_id=False
                        website = row[20].strip() or ''
                        date = row[8].strip() or ''
                        if date:
                            date_format = datetime.strptime(date, "%Y-%m-%d").strftime(DF)
                        else:
                            date_format =False
                        last_update_date = row[56].strip() or ''
                        if last_update_date:
                            last_update_date_format = datetime.strptime(last_update_date, "%Y-%m-%d").strftime(DF)
                        else:
                            last_update_date_format=False
                        employer = row[11].strip() or ''
                        employer_contact = row[16].strip() or ''
                        # case_manager = row[47].strip() or ''
                        case_manager_id = row[52].strip() or ''
                        if case_manager_id:
                            case_manager_search_id = self.env['hr.employee'].search([('employee_old_id', '=', case_manager_id)],limit=1).id
                        else:
                            case_manager_search_id=False
                        claim_number = row[44].strip() or ''
                        claim_no = row[14].strip() or ''
                        claim_no2 = row[28].strip() or ''
                        field_case_mgr = row[53].strip() or ''
                        if field_case_mgr:
                            field_case_mgr_id = self.env['hr.employee'].search([('employee_old_id', '=', field_case_mgr)],limit=1).id
                        else:
                            field_case_mgr_id=False
                        referrer = row[49].strip() or ''
                        billing_partner_id = row[7].strip() or False
                        if billing_partner_id:
                            self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                                billing_partner_id) + " limit 1")
                            billing_partner_id = self._cr.fetchone()
                            billing_partner_id = billing_partner_id and billing_partner_id[0] or False
                        billing_contact_id = row[46].strip() or False
                        if billing_contact_id:
                            self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                                billing_contact_id) + " limit 1")
                            billing_contact_id = self._cr.fetchone()
                            billing_contact_id = billing_contact_id and billing_contact_id[0] or False
                        # patient_history = row[46].strip() or ''
                        # patient_auth_history = row[47].strip() or ''
                        interpreter_id = row[54].strip() or False
                        if interpreter_id:
                            self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                                interpreter_id) + " limit 1")
                            interpreter_id = self._cr.fetchone()
                            interpreter_id = interpreter_id and interpreter_id[0] or False
                        # interpreter_history = row[49].strip() or ''
                        ordering_partner_id = row[55].strip() or False
                        if ordering_partner_id:
                            self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                                ordering_partner_id) + " limit 1")
                            ordering_partner_id = self._cr.fetchone()
                            ordering_partner_id = ordering_partner_id and ordering_partner_id[0] or False
                        patient_vals = {
                            'patient_old_id': int(patient_old_id),
                            'name': name,
                            'last_name': last_name,
                            'complete_name': complete_name,
                            # 'user_id': user_id.id,
                            'comment': comment,
                            'active': True if active == 't' else False,
                            'street': street,
                            'street2': street2,
                            'company_id':company_id,
                            'zip': zip,
                            'city': city,
                            'state_id': state_id,
                            'country_id': 235,
                            'email': email,
                            'email2': email2,
                            'phone': phone,
                            'phone2': phone2,
                            'phone3': phone3,
                            'phone4': phone4,
                            'fax': fax,
                            'mobile': mobile,
                            'is_alert': True if is_alert == 't' else False,
                            'ssnid': ssnid,
                            'sinid': sinid,
                            'latitude': float(latitude) if latitude else 0.0,
                            'longitude': float(longitude) if longitude else 0.0,
                            'gender': 'male' if gender=='M' else 'female',
                            'company_name': company_name,
                            'function': function,
                            'birthdate': birthdate_format ,
                            'injury_date': injury_date_format,
                            'patient_id': patient_id,
                            'website': website,
                            'date': date_format if date else '',
                            'last_update_date': last_update_date_format,
                            'employer': employer,
                            'employer_contact': employer_contact,
                            # 'case_manager': case_manager,
                            'case_manager_id': case_manager_search_id,
                            'claim_number': claim_number,
                            'claim_no': claim_no,
                            'claim_no2': claim_no2,
                            'field_case_mgr_id': field_case_mgr_id,
                            'referrer': referrer,
                            'billing_partner_id': billing_partner_id,
                            'billing_contact_id': billing_contact_id,
                            # 'patient_history':patient_history,
                            # 'patient_auth_history':patient_auth_history,
                            # 'location_ids':location_ids,
                            'interpreter_id': interpreter_id,
                            # 'interpreter_history': interpreter_history,
                            'ordering_partner_id': ordering_partner_id,
                        }

                        if not patient_obj:
                            patient_new_id = self.env['patient'].create(patient_vals)
                            self._cr.commit()
                        else:
                            patient_obj.write(patient_vals)
                            self._cr.commit()
                            _logger.error('--Patient Already Found-- %s', key)
                except Exception as e:
                    _logger.error('------------error log_id exception---------- %s', e)
                    value.append(str(e))
                    error_list.append(value)
        with open('/home/iuadmin/cust_upload_err/patient_error.csv', 'wb') as f:
        # with open('/home/iuadmin/cust_upload_err/cust_upload_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

#function to import Employeesvn
    @api.multi
    def import_employee(self):
        csv_datas = self.upload_file
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
                    employee_old_id = row[0].strip()
                    name = row[47].strip()
                    work_email = row[23].strip()
                    name_related = row[26].strip()
                    # resource_id = row[7].strip()
                    ssnid = row[27].strip()
                    # uom_id = row[32].strip()
                    # journal_id = row[33].strip()
                    # product_id = row[34].strip()
                    is_schedular = row[39].strip()
                    # visibility = row[36].strip()
                    last_name = row[40].strip()
                    staff_id = row[43].strip()
                    end_date = row[45].strip()
                    hire_date = row[50].strip()
                    meta_zone = row[51].strip()
                    middle_name = row[44].strip()
                    vendor_id2 = row[54].strip()
                    is_alert = row[52].strip()

                    meta_zone_id = self.env['meta.zone'].search([('meta_zone_old_id','=',meta_zone)])
                    if end_date:
                        end_date_format = datetime.strptime(end_date.split(" ")[0], "%Y-%m-%d").strftime(DF)
                    if hire_date:
                        hire_date_format = datetime.strptime(hire_date.split(" ")[0], "%Y-%m-%d").strftime(DF)

                    employee_vals = {'employee_old_id':int(employee_old_id),
                                     'name':name,
                                     'work_email':work_email,
                                     # 'resource_id':resource_id.id,
                                     'name_related':name_related,
                                     'ssnid':ssnid,
                                     # 'uom_id':uom_id,
                                     # 'journal_id':journal_id,
                                     # 'product_id':product_id,
                                     # 'visibility':visibility,
                                     'is_schedular':True if is_schedular=='t' else False,
                                     'is_alert':True if is_alert=='t' else False,
                                     'last_name':last_name,
                                     'staff_id':int(staff_id) if staff_id else 0,
                                     'middle_name':middle_name,
                                     'end_date':end_date_format if end_date else '',
                                     'hire_date':hire_date_format if hire_date else '',
                                     'meta_zone_id':meta_zone_id.id,
                                     'vendor_id2':int(vendor_id2) if vendor_id2 else 0,
                    }
                    employer_id = self.env['hr.employee'].create(employee_vals)
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
        self.upload_error = base64.encodestring(bytes(file_data))
        self.upload_error_file_name = 'Employee Uploading Error.csv'
        csvfile.close()
        return {
            "type": "ir.actions.do_nothing",
        }