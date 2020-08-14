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
import base64
import psycopg2

_logger = logging.getLogger('mapping_code')

class DataMappingCode(models.TransientModel):
    _name='data.mappingcode.wizard'

    upload_file = fields.Binary(string='File URL')
    upload_error = fields.Binary(string='Click To Download Error Log')
    upload_error_file_name = fields.Char("File name")

    @api.multi
    def map_event_followers(self):
        error_list = []
        header_list = []
        file_obj = '/home/iuadmin/event_followers_rel1.csv'
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
                    event_id = row[0].strip() or 0
                    user_id = row[1].strip() or 0
                    if event_id:
                        self._cr.execute("select id from event where event_old_id=" + str(
                            event_id) + " limit 1")
                        event_id = self._cr.fetchone()
                        event_id = event_id and event_id[0] or False
                    if user_id:
                        self._cr.execute("select id from res_users where user_old_id=" + str(
                            user_id) + " limit 1")
                        user_id = self._cr.fetchone()
                        user_id = user_id and user_id[0] or False
                    if event_id and user_id:
                        vals = (event_id, user_id)
                        self._cr.execute(""" INSERT INTO event_followers_rel1 (event_id,user_id) VALUES (%s,%s)""", vals)
                        self._cr.commit()
                    else:
                        _logger.error('--------Record missing------')
                        error_list.append(value)
            except Exception as e:
                self._cr.rollback()
                value.append(str(e))
                _logger.error('------------Error Exception---------- %s', e)
                error_list.append(value)

        with open('/home/iuadmin/map_event_followers.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

    @api.multi
    def update_inactive_contact(self):
        error_list = []
        header_list = []
        path = '/home/iuadmin/partner_inactive'
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
                        partner_id = row[0]
                        partner_obj = self.env['res.partner'].search(
                            [('customer_record_old_id', '=', partner_id)],limit=1)
                        if partner_obj:
                            partner_obj.write({'active': False})
                            self._cr.commit()
                        else:
                            _logger.error('------Customer Not Found-----')
                            error_list.append(value)
                except Exception as e:
                    _logger.error('------------error log_id exception---------- %s', e)

    @api.multi
    def update_interpreter_event(self):
        error_list = []
        header_list = []
        # path = '/home/abhishek/Desktop/IUG_master_data/move'
        path = '/home/iuadmin/evnt'
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
                        event_old_id = row[0].strip()
                        single_interpreter=row[139].strip() or False
                        event_id = self.env['event'].search(
                            [('event_old_id', '=', event_old_id)], limit=1)
                        if event_id:
                            single_interpreter = self.env['res.partner'].search(
                                [('customer_record_old_id', '=', single_interpreter)], limit=1).id
                            event_id.write({'single_interpreter': single_interpreter})
                            self._cr.commit()
                        else:
                            _logger.error('------event not found----------')
                            error_list.append(value)
                except Exception as e:
                    _logger.error('------------error log_id exception---------- %s', e)
                    error_list.append(value)
        with open('/home/iuadmin/cust_upload_err/update_interpreter_event_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

    @api.multi
    def update_fields_invoice(self):
        error_list = []
        header_list = []
        # path = '/home/abhishek/Desktop/IUG_master_data/move'
        path = '/home/iuadmin/invoice_custom'
        # path = '/home/abhishek/Desktop/IUG_Update_Data/cust'
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
                        _logger.error('---current progress -- %s---------sheet:%s', key,filename)
                        invoice_old_id = row[0].strip() or ''
                        project_name_id = row[1].strip() or ''
                        month=row[2].strip() or False
                        year=row[3].strip() or False
                        invoice_number=row[4].strip() or False
                        invoice_obj = self.env['account.invoice'].search([('invoice_old_id', '=', invoice_old_id)],limit=1)
                        invoice_vals={}
                        if invoice_obj and not invoice_obj.invoice_old_number:
                            if project_name_id:
                                project_id = self.env['project'].search(
                                    [('iug_project_old_id', '=', project_name_id)], limit=1).id
                                invoice_vals.update({'project_name_id': project_id})
                            if month:
                                invoice_vals.update({'month':month})
                            if year:
                                invoice_vals.update({'year':year})
                            if invoice_number:
                                invoice_vals.update({'invoice_old_number': invoice_number})
                            invoice_obj.write(invoice_vals)
                        else:
                            _logger.error('--------no invoice----------')
                            error_list.append(value)
                        self._cr.commit()
                except Exception as e:
                    _logger.error('------------error log_id exception---------- %s', e)
                    error_list.append(value)
            os.remove(file_obj)
        # with open('/home/abhishek/Desktop/output.csv', 'wb') as f:
        with open('/home/iuadmin/cust_upload_err/invoice_update_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

    @api.multi
    def update_group_old_id(self):
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
                    group_old_id = row[0].strip()
                    name = row[1].strip()
                    group_obj= self.env['res.groups'].search([('name', '=', name)],limit=1)
                    if group_obj:
                        group_obj.write({'group_old_id':group_old_id})
                    else:
                        _logger.error('-----group unidentified-------')
                    self._cr.commit()
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
    def map_user_group(self):
        error_list = []
        header_list = []
        path = '/home/iuadmin/group_rel'
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
                        _logger.error('---current progress -- %s', key)
                        user_id = value[0].strip() or False
                        group_id = value[1].strip() or False

                        u_id = self.env['res.users'].search([('user_old_id', '=', user_id)], limit=1).id
                        g_id = self.env['res.groups'].search([('group_old_id', '=', group_id)], limit=1).id
                        if g_id and u_id :
                            # u_id.write({'groups_id':[(3, g_id)]})
                            # u_id.write({'groups_id':[(4, g_id)]})
                            vals = (u_id, g_id)
                            self._cr.execute(""" INSERT INTO res_groups_users_rel (uid,gid) VALUES (%s,%s)""",vals)
                        else:
                            _logger.error('--------Record missing--------')
                            error_list.append(value)
                        self._cr.commit()
                except Exception as e:
                    _logger.error('------------error log_id exception---------- %s', e)
                    self._cr.rollback()
                    error_list.append(value)
        with open('/home/iuadmin/cust_upload_err/map_group_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

    @api.multi
    def update_user_id_partners(self):
        error_list = []
        header_list = []
        # path = '/home/abhishek/Desktop/IUG_master_data/move'
        path = '/home/iuadmin/cust_upload/cust_update_upload'
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
                        _logger.error('---current progress -- %s -- sheet--%s', key, filename)
                        customer_record_old_id = row[0].strip() or 0
                        user_id = row[17].strip() or ''
                        billing_contact_id=row[73].strip() or False
                        meta_zone_id=row[74].strip() or False
                        zone_id=row[110].strip() or False
                        language_id=row[136].strip() or False
                        billing_partner_id=row[146].strip() or False
                        sales_representative_id=row[165].strip() or False
                        scheduler_id=row[172].strip() or False
                        head_contact_id=row[173].strip() or False
                        active=row[13].strip()
                        partner_obj = self.env['res.partner'].search(
                            [('customer_record_old_id', '=', customer_record_old_id)], limit=1)

                        if partner_obj:
                            partner_vals={}
                            parent_id = row[22].strip() or False
                            if parent_id:
                                parent_id = self.env['res.partner'].search([('customer_record_old_id', '=', parent_id)],
                                                                           limit=1).id
                                partner_vals.update({'parent_id': parent_id})
                            if billing_contact_id:
                                billing_contact_id = self.env['res.partner'].search([('customer_record_old_id', '=', billing_contact_id)],
                                                                   limit=1).id
                                partner_vals.update({'billing_contact_id':billing_contact_id})
                            if meta_zone_id:
                                meta_zone_id=self.env['meta.zone'].search([('meta_zone_old_id', '=', meta_zone_id)],
                                                                   limit=1).id
                                partner_vals.update({'meta_zone_id':meta_zone_id})
                            if zone_id:
                                zone_id=self.env['zone'].search([('zone_old_id', '=', zone_id)],
                                                                   limit=1).id
                                partner_vals.update({'zone_id':zone_id})

                            if language_id:
                                language_id=self.env['language'].search([('language_old_id', '=', language_id)],
                                                                   limit=1).id
                                partner_vals.update({'language_id':language_id})
                            if billing_partner_id:
                                billing_partner_id = self.env['res.partner'].search(
                                    [('customer_record_old_id', '=', billing_partner_id)],limit=1).id
                                partner_vals.update({'billing_partner_id':billing_partner_id})
                            if sales_representative_id:
                                sales_representative_id = self.env['res.users'].search(
                                    [('user_old_id', '=', sales_representative_id)], limit=1).id
                                partner_vals.update({'sales_representative_id':sales_representative_id})
                            if  scheduler_id:
                                scheduler_id = self.env['res.users'].search(
                                    [('user_old_id', '=', scheduler_id)], limit=1).id
                                partner_vals.update({'scheduler_id':scheduler_id})

                            if head_contact_id:
                                head_contact_id = self.env['res.partner'].search(
                                    [('customer_record_old_id', '=', head_contact_id)], limit=1).id
                                partner_vals.update({'head_contact_id':head_contact_id})
                            if user_id:
                                user_id = self.env['res.users'].search([('user_old_id', '=', user_id)], limit=1).id
                                partner_vals.update({'user_id':user_id})
                            if active=='f':
                                partner_vals.update({'active': False})
                            partner_obj.write(partner_vals)
                        else:
                            _logger.error('-----Customer Not found------')
                        self._cr.commit()
                except Exception as e:
                    self._cr.rollback()
                    value.append(str(e))
                    _logger.error('------------error log_id exception---------- %s', e)
                    error_list.append(value)
        # with open('/home/abhishek/Desktop/output.csv', 'wb') as f:
        with open('/home/iuadmin/cust_upload_err/partner_error_with_parent_id.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

    @api.multi
    def update_user_id_partners_all(self):
        error_list = []
        header_list = []
        # path = '/home/abhishek/Desktop/IUG_master_data/move'
        path = '/home/iuadmin/res_partner_all'
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
                        _logger.error('---current progress -- %s -- sheet--%s-- value -- %s', key, filename,value)
                        customer_record_old_id = row[0].strip() or False
                        user_id = row[1].strip() or False
                        sales_representative_id = row[2].strip() or False
                        scheduler_id = row[3].strip() or False
                        partner_obj = self.env['res.partner'].search(
                            [('customer_record_old_id', '=', customer_record_old_id)], limit=1)
                        if partner_obj:
                            partner_vals = {}
                            if sales_representative_id:
                                self._cr.execute("select id from res_users where user_old_id=" + str(
                                    sales_representative_id) + " limit 1")
                                sales_representative_id = self._cr.fetchone()
                                sales_representative_id = sales_representative_id and sales_representative_id[0] or False
                                partner_vals.update({'sales_representative_id': sales_representative_id})
                            if scheduler_id:
                                self._cr.execute("select id from res_users where user_old_id=" + str(
                                    scheduler_id) + " limit 1")
                                scheduler_id = self._cr.fetchone()
                                scheduler_id = scheduler_id and scheduler_id[0] or False
                                partner_vals.update({'scheduler_id': scheduler_id})
                            if user_id:
                                self._cr.execute("select id from res_users where user_old_id=" + str(
                                    user_id) + " limit 1")
                                user_id = self._cr.fetchone()
                                user_id = user_id and user_id[0] or False
                                partner_vals.update({'user_id': user_id})
                            partner_obj.write(partner_vals)
                        else:
                            _logger.error('-----Customer Not found------')
                            value.append('Customer not found')
                            error_list.append(value)
                        self._cr.commit()
                except Exception as e:
                    self._cr.rollback()
                    value.append(str(e))
                    _logger.error('------------error log_id exception---------- %s', e)
                    error_list.append(value)
        # with open('/home/abhishek/Desktop/output.csv', 'wb') as f:
        with open('/home/iuadmin/res_partner_all_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

    # @api.multi
    # def map_event_followers(self):
    #     error_list = []
    #     header_list = []
    #     file_obj = '/home/iuadmin/event_followers/event_follower_rel.csv'
    #     lis = csv.reader(open(file_obj, 'rU'), delimiter=",")
    #     row_num = 0
    #     data_dict = {}
    #     for row in lis:
    #         data_dict.update({row_num: row})
    #         row.append(row_num)
    #         row_num += 1
    #     for key, value in data_dict.items():
    #         try:
    #             if key == 0:
    #                 header_list.append(value)
    #             else:
    #                 row = value
    #                 _logger.error('------------row number---------- %s', key)
    #                 event_old_id = row[0].strip() or False
    #                 user_id = row[1].strip() or False
    #                 event_id = self.env['event'].search([('event_old_id', '=', event_old_id)], limit=1).id
    #                 user_id = self.env['res.users'].search([('user_old_id', '=', user_id)],limit=1).id
    #                 if event_id and user_id:
    #                     vals = (event_id, user_id)
    #                     self._cr.execute(""" INSERT INTO event_followers_rel1 (event_id,user_id) VALUES (%s,%s)""",
    #                                      vals)
    #                     self._cr.commit()
    #                 else:
    #                     _logger.error('--------Record missing-------- %s', key)
    #                     error_list.append(value)
    #         except Exception as e:
    #             _logger.error('------------Error Exception---------- %s', e)
    #             value.append(e)
    #             self._cr.rollback()


    @api.multi
    def update_login_users(self):
        error_list = []
        header_list = []
        file_obj = '/home/iuadmin/users.csv'
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
                    _logger.error('------------row number---------- %s', key)
                    user_old_id = value[0].strip() or False
                    login=value[2].strip() or ''
                    password=value[3].strip() or ''
                    active=value[1].strip() or ''
                    user_obj = self.env['res.users'].search([('user_old_id', '=', user_old_id)], limit=1)
                    user_vals={}
                    if user_obj:
                        if login:
                            user_vals.update({'login':login})
                        if password:
                            user_vals.update({'password': password})
                        if active=='f':
                            user_vals.update({'active':False})
                        user_obj.write(user_vals)
                        self._cr.commit()
                    else:
                        _logger.error('-----User Not Found!!-------')

            except Exception as e:
                _logger.error('------------Error Exception---------- %s', e)
                value.append(e)
                error_list.append(value)
        with open('/home/iuadmin/user_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

    @api.multi
    def add_user(self):
        error_list = []
        header_list = []
        file_obj = '/home/iuadmin/users.csv'
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
                    _logger.error('------------row number---------- %s', key)
                    user_old_id = value[0].strip() or False
                    login=value[2].strip() or ''
                    password=value[3].strip() or ''
                    active=value[1].strip() or ''
                    company = value[4].strip() or False
                    if company:
                        company_id = self.env['res.company'].search([('res_company_old_id', '=', company)], limit=1).id
                    else:
                        company_id=False
                    partner_id = value[5].strip() or False
                    if partner_id:
                        self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                            partner_id) + " limit 1")
                        partner_id = self._cr.fetchone()
                        partner_id = partner_id and partner_id[0] or False
                    login_date = value[11].strip() or ''
                    if login_date:
                        login_date = datetime.strptime(login_date, "%Y-%m-%d").strftime(DF)
                    else:
                        login_date = False
                    signature = value[12].strip() or ''
                    share = value[15].strip() or ''  # bool
                    user_type = value[20].strip() or ''
                    entity_id = value[17].strip() or ''  # int
                    mail_group = value[18].strip() or ''
                    login_id = value[19].strip() or ''  # int
                    require_to_reset = value[22].strip() or ''
                    zone_id = value[24].strip() or False
                    if zone_id:
                        zone_id = self.env['zone'].search([('zone_old_id', '=', zone_id)])
                    user_obj = self.env['res.users'].search([('user_old_id', '=', user_old_id)], limit=1)
                    if not user_obj:
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
                        user_id=self.env['res.users'].create(user_vals)
                        self._cr.commit()
                    else:
                        _logger.error('-----User Found!!-------')

            except Exception as e:
                _logger.error('------------Error Exception---------- %s', e)
                value.append(e)
                self._cr.rollback()
                error_list.append(value)
        with open('/home/iuadmin/user_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

    @api.multi
    def update_related_user(self):
        error_list = []
        header_list = []
        # path = '/home/abhishek/Desktop/IUG_master_data/move'
        path = '/home/iuadmin/res_partner'
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

                        _logger.error('---current progress -- %s', key)
                        partner_old_id = value[0].strip() or ''
                        user_id = value[17].strip() or ''
                        partner_obj = self.env['res.partner'].search(
                            [('customer_record_old_id', '=', partner_old_id)], limit=1)
                        user_id = self.env['res.users'].search([('user_old_id', '=', user_id)],
                                                                     limit=1).id
                        if partner_obj and user_id:
                            partner_obj.write({'user_id': user_id})
                        elif partner_obj:
                            partner_obj.write({'user_id': 1})
                        else:
                            _logger.error('----partner not found!!-------')
                            error_list.append(value)
                        self._cr.commit()
                except Exception as e:
                    _logger.error('------------error log_id exception---------- %s', e)
                    error_list.append(value)
        with open('/home/iuadmin/cust_upload_err/res_error.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

    @api.multi
    def import_interpreter_history(self):
        error_list = []
        header_list = []
        path = '/home/iuadmin/interpreter_his'
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
                        _logger.error('---current progress -- %s -- sheet--%s', key, filename)
                        inter_his_old_id = value[0].strip()
                        inter_ob=self.env['interpreter.history'].search([('inter_his_old_id','=',inter_his_old_id)],limit=1)
                        state = value[11].strip()
                        name = value[5].strip() or False
                        if name:
                            self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                                name) + " limit 1")
                            name = self._cr.fetchone()
                            name = name and name[0] or False

                        task_id = value[6].strip() or False
                        if task_id:
                            self._cr.execute("select id from task where project_task_old_id=" + str(
                                task_id) + " limit 1")
                            task_id = self._cr.fetchone()
                            task_id = task_id and task_id[0] or False
                        event_id = value[7].strip() or False
                        if event_id:
                            self._cr.execute("select id from event where event_old_id=" + str(
                                event_id) + " limit 1")
                            event_id = self._cr.fetchone()
                            event_id = event_id and event_id[0] or False
                        language_id = value[8].strip() or False
                        if language_id:
                            language_id= self.env['language'].search([('language_old_id','=',language_id)],limit=1).id
                        company_id = value[9].strip() or False
                        if company_id:
                            company_id=self.env['res.company'].search([('res_company_old_id','=',company_id)],limit=1).id
                        voicemail_msg = value[10].strip()

                        event_date = value[12].strip()
                        event_start_time = value[13].strip()
                        event_end_time = value[14].strip()
                        inter_his_vals={
                            'inter_his_old_id':inter_his_old_id,
                            'name':name,
                            'task_id':task_id,
                            'event_id':event_id,
                            'language_id':language_id,
                            'company_id':company_id,
                            'voicemail_msg':voicemail_msg,
                            'state':state,
                            'event_date':event_date,
                            'event_start_time':event_start_time,
                            'event_end_time':event_end_time,
                        }
                        if not inter_ob:
                            inter_his_id=self.env['interpreter.history'].create(inter_his_vals)
                            self._cr.commit()
                        else:
                            inter_ob.write(inter_his_vals)
                            self._cr.commit()
                            _logger.error('----already created-------')
                except Exception as e:
                    self._cr.rollback()
                    _logger.error('------------error log_id exception---------- %s', e)
                    value.append(str(e))
                    error_list.append(value)
        with open('/home/iuadmin/cust_upload_err/interpreter_history_er.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

    @api.multi
    def map_doctor_location_rel(self):
        error_list = []
        header_list = []
        file_obj = '/home/iuadmin/doctor_location_rel.csv'
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
                    doctor_id = row[0].strip() or False
                    location_id = row[1].strip() or False
                    if doctor_id:
                        self._cr.execute("select id from doctor where doctor_old_id=" + str(
                            doctor_id) + " limit 1")
                        doctor_id = self._cr.fetchone()
                        doctor_id = doctor_id and doctor_id[0] or False
                    if location_id:
                        self._cr.execute("select id from location where location_old_id=" + str(
                            location_id) + " limit 1")
                        location_id = self._cr.fetchone()
                        location_id = location_id and location_id[0] or False
                    if doctor_id and location_id:
                        vals = (doctor_id, location_id)
                        self._cr.execute(""" INSERT INTO doctor_location_rel (doctor_id,location_id) VALUES (%s,%s)""",vals)
                        self._cr.commit()
                    else:
                        _logger.error('--------Record missing-------- %s', key)
                        error_list.append(value)
            except Exception as e:
                self._cr.rollback()
                _logger.error('------------Error Exception---------- %s', e)

    @api.multi
    def map_translator_software_rel(self):
        error_list = []
        header_list = []
        file_obj = '/home/iuadmin/translator_software_rel.csv'
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
                    translator_id = row[0].strip() or 0
                    software_id = row[1].strip() or 0
                    trans_id = self.env['res.partner'].search(
                        [('customer_record_old_id', '=', translator_id)], limit=1).id
                    soft_id = self.env['software'].search(
                        [('software_old_id', '=', software_id)], limit=1).id
                    if trans_id and soft_id:
                        vals = (trans_id, soft_id)
                        self._cr.execute(""" INSERT INTO translator_software_rel (translator_id,software_id) VALUES (%s,%s)""",
                                         vals)
                        self._cr.commit()
                    else:
                        _logger.error('--------Record missing-------- %s', key)
                        error_list.append(value)
            except Exception as e:
                _logger.error('------------Error Exception---------- %s', e)

    @api.multi
    def map_translator_affiliation_rel(self):
        error_list = []
        header_list = []
        file_obj = '/home/iuadmin/translator_affiliation_rel.csv'
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
                    translator_id = row[0].strip() or 0
                    affiliation_id = row[1].strip() or 0
                    trans_id = self.env['res.partner'].search(
                        [('customer_record_old_id', '=', translator_id)], limit=1).id
                    aff_id = self.env['affiliation'].search(
                        [('affiliation_old_id', '=', affiliation_id)], limit=1).id
                    if trans_id and aff_id:
                        vals = (trans_id, aff_id)
                        self._cr.execute(
                            """ INSERT INTO translator_affiliation_rel (translator_id,affiliation_id) VALUES (%s,%s)""",
                            vals)
                        self._cr.commit()
                    else:
                        _logger.error('--------Record missing-------- %s', key)
                        error_list.append(value)
            except Exception as e:
                _logger.error('------------Error Exception---------- %s', e)


    @api.multi
    def update_user_access(self):
            try:
                user_obj = self.env['res.users'].search([('user_type','in',['vendor','contact'])])
                vendor_list=[19,1,960,100]
                contact_list=[1,962,100]
                for user in user_obj:
                    uid = (user.id,)
                    if user.user_type=='vendor':
                        try:
                            self._cr.execute(""" DELETE FROM res_groups_users_rel WHERE uid=(%s)""",uid)
                            for item in vendor_list:
                                vals=(item,user.id)
                                self._cr.execute(""" INSERT INTO res_groups_users_rel (gid,uid) VALUES (%s,%s)""",vals)
                        except:
                            self._cr.rollback()
                    if user.user_type=='contact':
                        try:
                            self._cr.execute(""" DELETE FROM res_groups_users_rel WHERE uid=(%s)""", uid)
                            for item in contact_list:
                                vals = (item, user.id)
                                self._cr.execute(""" INSERT INTO res_groups_users_rel (gid,uid) VALUES (%s,%s)""", vals)
                        except:
                            self._cr.rollback()
                    self._cr.commit()
                    _logger.error('-----user updated------')
            except Exception as e:
                _logger.error('------------Error Exception---------- %s', e)

    @api.multi
    def update_latitude_interpreter(self):
        file_obj = '/home/iuadmin/interpreter.csv'
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
                   pass
                else:
                    _logger.error('------------row number---------- %s', key)
                    partner_old_id = value[0].strip() or False
                    latitude = value[1].strip() or False
                    longitude = value[2].strip() or False
                    if partner_old_id:
                        partner_id = self.env['res.partner'].search([('customer_record_old_id', '=', partner_old_id)],
                                                                    limit=1).id
                        if partner_id and latitude and longitude:
                            try:
                                self._cr.execute(""" UPDATE res_partner SET latitude=%s,longitude=%s where id=%s""",
                                                 latitude, longitude, partner_id)
                                self._cr.commit()
                                _logger.error('------interpreter updated------')
                            except:
                                self._cr.rollback()
            except Exception as e:
                _logger.error('------------Error Exception---------- %s', e)

    @api.multi
    def map_billing_inv_rel(self):
        error_list = []
        header_list = []
        file_obj = '/home/iuadmin/m2m_rel/billing_inv_rel.csv'
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
                    billing_form_id = row[0].strip() or 0
                    invoice_id = row[1].strip() or 0
                    bill_id = self.env['billing.form'].search(
                        [('billing_form_old_id', '=', billing_form_id)], limit=1).id
                    inv_id = self.env['account.invoice'].search(
                        [('invoice_old_id', '=', invoice_id)], limit=1).id
                    if bill_id and inv_id:
                        vals = (bill_id, inv_id)
                        self._cr.execute(
                            """ INSERT INTO billing_inv_rel (bill_form_id,invoice_id) VALUES (%s,%s)""",
                            vals)
                        self._cr.commit()
                    else:
                        _logger.error('--------Record missing-------- %s', key)
                        error_list.append(value)
            except Exception as e:
                _logger.error('------------Error Exception---------- %s', e)

    @api.multi
    def map_project_task_inv_rel(self):
        error_list = []
        header_list = []
        file_obj = '/home/iuadmin/m2m_rel/project_task_inv_rel.csv'
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
                    task_id = row[0].strip() or 0
                    invoice_id = row[1].strip() or 0
                    tk_id = self.env['project.task'].search(
                        [('project_task_old_id', '=', task_id)], limit=1).id
                    inv_id = self.env['account.invoice'].search(
                        [('invoice_old_id', '=', invoice_id)], limit=1).id
                    if tk_id and inv_id:
                        vals = (tk_id, inv_id)
                        self._cr.execute(
                            """ INSERT INTO project_task_inv_rel (task_id,invoice_id) VALUES (%s,%s)""",vals)
                        self._cr.commit()
                    else:
                        _logger.error('--------Record missing-------- %s', key)
                        error_list.append(value)
            except Exception as e:
                self._cr.rollback()
                _logger.error('------------Error Exception---------- %s', e)

    @api.multi
    def map_partner_project_group_rel(self):
        error_list = []
        header_list = []
        file_obj = '/home/iuadmin/m2m_rel/partner_project_group_rel.csv'
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
                    project_id = row[0].strip() or False
                    partner_id = row[1].strip() or False
                    if project_id:
                        self._cr.execute("select id from project where iug_project_old_id=" + str(
                            project_id) + " limit 1")
                        project_id = self._cr.fetchone()
                        project_id = project_id and project_id[0] or False
                    if partner_id:
                        self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                            partner_id) + " limit 1")
                        partner_id = self._cr.fetchone()
                        partner_id = partner_id and partner_id[0] or False
                    if project_id and partner_id:
                        vals = (project_id, partner_id)
                        self._cr.execute(
                            """ INSERT INTO partner_project_group_rel (partner_id,project_id) VALUES (%s,%s)""",vals)
                        self._cr.commit()
                    else:
                        _logger.error('--------Record missing-------- %s', key)
                        self._cr.rollback()
                        value.append(str(e))
                        error_list.append(value)
            except Exception as e:
                _logger.error('------------Error Exception---------- %s', e)
                self._cr.rollback()
                value.append(str(e))
        with open('/home/iuadmin/map_partner_project_group_rel.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

    @api.multi
    def map_customer_billing_rule_rel(self):
        error_list = []
        header_list = []
        file_obj = '/home/iuadmin/m2m_rel/customer_billing_rule_rel.csv'
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
                    partner_id = row[0].strip() or False
                    bill_rule_id = row[1].strip() or False
                    if partner_id:
                        self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                            partner_id) + " limit 1")
                        partner_id = self._cr.fetchone()
                        partner_id = partner_id and partner_id[0] or False
                    if bill_rule_id:
                        self._cr.execute("select id from billing_rule where billing_rule_old_id=" + str(
                            bill_rule_id) + " limit 1")
                        bill_rule_id = self._cr.fetchone()
                        bill_rule_id = bill_rule_id and bill_rule_id[0] or False
                    if partner_id and bill_rule_id:
                        vals = (partner_id, bill_rule_id)
                        self._cr.execute(
                            """ INSERT INTO customer_billing_rule_rel (customer_id,billing_rule_id) VALUES (%s,%s)""", vals)
                        self._cr.commit()
                    else:
                        _logger.error('--------Record missing-------- %s', key)
                        error_list.append(value)
            except Exception as e:
                _logger.error('------------Error Exception---------- %s', e)

    @api.multi
    def map_project_task_partner_rel(self):
        error_list = []
        header_list = []
        file_obj = '/home/iuadmin/m2m_rel/project_task_partner_rel.csv'
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
                    task_id = row[0].strip() or 0
                    interpreter_id = row[1].strip() or 0
                    if task_id:
                        self._cr.execute("select id from project_task where project_task_old_id=" + str(
                            task_id) + " limit 1")
                        task_id = self._cr.fetchone()
                        task_id = task_id and task_id[0] or False
                    if interpreter_id:
                        self._cr.execute("select id from res_partner where customer_record_old_id=" + str(
                            interpreter_id) + " limit 1")
                        interpreter_id = self._cr.fetchone()
                        interpreter_id = interpreter_id and interpreter_id[0] or False
                    if task_id and interpreter_id:
                        vals = (task_id, interpreter_id)
                        self._cr.execute(
                            """ INSERT INTO project_task_partner_rel (task_id,interpreter_id) VALUES (%s,%s)""",
                            vals)
                        self._cr.commit()
                    else:
                        _logger.error('--------Record missing-------- %s', key)
                        error_list.append(value)
            except Exception as e:
                self._cr.rollback()
                _logger.error('------------Error Exception---------- %s', e)

    @api.multi
    def update_partner_id_user(self):
        error_list = []
        header_list = []
        file_obj = '/home/iuadmin/users.csv'
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
                    _logger.error('------------row number---------- %s', key)
                    user_old_id = value[0].strip() or False
                    partner_id = value[5].strip() or False
                    if partner_id:
                        partner_id = self.env['res.partner'].search([('customer_record_old_id', '=', partner_id)],limit=1).id
                        user_obj = self.env['res.users'].search([('user_old_id', '=', user_old_id)], limit=1)
                        if user_obj and partner_id:
                            user_obj.write({'partner_id':partner_id})
                        else:
                            _logger.error('--------exception----------')

            except Exception as e:
                _logger.error('--------exception---------- %s', e)
        self._cr.commit()
    @api.multi
    def update_sheduler_event(self):
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
                        event_old_id = row[0].strip()
                        event_id = self.env['event'].search([('event_old_id', '=', event_old_id),'|',('scheduler_id','=',False),('sales_representative_id','=',False)], limit=1).id
                        if event_id:
                            scheduler_id = row[2].strip() or False
                            if scheduler_id:
                                if scheduler_id==1:
                                    pass
                                else:
                                    self._cr.execute(
                                        """SELECT id from res_users where user_old_id=%s limit 1""",
                                        (scheduler_id,))
                                    scheduler_id = self._cr.fetchone()
                            sales_representative_id = row[5].strip() or False
                            if sales_representative_id:
                                if sales_representative_id==1:
                                    pass
                                else:
                                    self._cr.execute(
                                        """SELECT id from res_users where user_old_id=%s limit 1""",
                                        (sales_representative_id,))
                                    sales_representative_id = self._cr.fetchone()

                            if scheduler_id and sales_representative_id:
                                try:
                                    self._cr.execute(""" UPDATE event SET scheduler_id=%s,sales_representative_id=%s where id=%s""",
                                                     (scheduler_id[0], sales_representative_id[0], event_id))
                                    self._cr.commit()
                                    _logger.error('------updated scheduler and sale------')
                                except:
                                    self._cr.rollback()
                            elif scheduler_id:
                                try:
                                    self._cr.execute(""" UPDATE event SET scheduler_id=%s where id=%s""",(scheduler_id[0], event_id))
                                    self._cr.commit()
                                    _logger.error('------scheduler updated------')
                                except:
                                    self._cr.rollback
                            elif sales_representative_id:
                                try:
                                    self._cr.execute(
                                        """ UPDATE event SET sales_representative_id=%s where id=%s""",(sales_representative_id[0], event_id))
                                    self._cr.commit()
                                    _logger.error('------sales representative updated------')
                                except:
                                    self._cr.rollback
                            else:
                                _logger.error('------no matching------')
                        self._cr.commit()
                except Exception as e:
                    _logger.error('------------error log_id exception---------- %s', e)

    @api.multi
    def update_event_line_billing_form(self):
        header_list = []
        file_obj = '/home/iuadmin/billing_form_event.csv'
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
                    _logger.error('------------row number---------- %s', key)
                    billing_form_old_id = value[0].strip() or False
                    event_line_old_id = value[24].strip() or False
                    if event_line_old_id:
                        billing_form_obj = self.env['billing.form'].search(
                            [('billing_form_old_id', '=', billing_form_old_id)],
                            limit=1)
                        event_line_id=self.env['event.lines'].search([('event_line_old_id', '=', event_line_old_id)],
                                                              limit=1).id
                        if event_line_id:
                            billing_form_obj.write({'event_line_id': event_line_id})
                        else:
                            _logger.error('--------no record----------')

            except Exception as e:
                _logger.error('--------exception---------- %s', e)
        self._cr.commit()

    @api.multi
    def map_task_invoice_rel(self):
        error_list = []
        header_list = []
        file_obj = '/home/iuadmin/task_inv_rel.csv'
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
                    event_id = row[0].strip() or 0
                    invoice_id = row[1].strip() or 0
                    evnt_id = self.env['event'].search(
                        [('event_old_id', '=', event_id)], limit=1).id
                    inv_id = self.env['account.invoice'].search(
                        [('invoice_old_id', '=', invoice_id)], limit=1).id
                    if evnt_id and inv_id:
                        vals = (evnt_id, inv_id)
                        try:
                            self._cr.execute(
                                """ INSERT INTO task_inv_rel (event_id,invoice_id) VALUES (%s,%s)""", vals)
                            self._cr.commit()
                        except:
                            self._cr.rollback()
                            _logger.error('-------already updated')
                    else:
                        _logger.error('--------Record missing-------- %s', key)
                        error_list.append(value)
            except Exception as e:
                _logger.error('------------Error Exception---------- %s', e)