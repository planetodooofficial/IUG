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
    _name = 'data.voucher.wizard'

    upload_file = fields.Binary(string='File URL')
    upload_error = fields.Binary(string='Click To Download Error Log')
    upload_error_file_name = fields.Char("File name")

    @api.multi
    def map_voucher(self):
        error_list = []
        header_list = []
        file_obj = '/home/iuadmin/account_voucher11_new.csv'
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
                    id = row[0].strip() or 0
                    name = row[1].strip() or 0
                    journal = row[2].strip() or 'Null'
                    reference = row[3].strip() or 'Null'
                    date = row[4].strip() or False
                    type = row[5].strip() or False

                    company = row[6].strip() or 0
                    number = row[7].strip() or False
                    period = row[8].strip() or False
                    memo = row[9].strip() or 'Null'
                    check = row[10].strip() or 'Null'

                    if company:
                        self._cr.execute("select id from res_company where res_company_old_id=" + str(
                            company) + " limit 1")
                    company = self._cr.fetchone()
                    company = company and company[0] or False

                    vals = (id, name, journal, reference, date, type, number, period, memo, check, company)
                    self._cr.execute(
                        """ INSERT INTO mi_account_voucher (old_id,name,journal,ref,date,type,number,period,memo,check_no,company_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                        vals)
                    self._cr.commit()

            except Exception as e:
                self._cr.rollback()
                value.append(str(e))
                _logger.error('------------Error Exception---------- %s', e)
                error_list.append(value)

        with open('/home/iuadmin/err_voucher.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()

    @api.multi
    def map_voucher_line(self):
        error_list = []
        header_list = []
        file_obj = '/home/iuadmin/account_voucher_line_wd_Account.csv'
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
                    name = row[0].strip() or ''
                    account = row[1].strip() or ''
                    amount = row[2].strip() or 0.0
                    type = row[3].strip() or ''
                    voucher = row[4].strip() or 0
                    ref=row[5].strip() or ''

                    if voucher:
                        self._cr.execute("select id from mi_account_voucher where old_id=" + str(
                            voucher) + " limit 1")
                        voucher_id = self._cr.fetchone()
                        voucher_id=voucher_id and voucher_id[0] or False


                        vals = (name, account, amount, type,voucher_id,ref)
                        self._cr.execute(
                            """ INSERT INTO mi_account_voucher_line (name,account,amount_total,type,voucher_id,ref) VALUES (%s,%s,%s,%s,%s,%s)""",
                            vals)
                        self._cr.commit()

            except Exception as e:
                self._cr.rollback()
                value.append(str(e))
                _logger.error('------------Error Exception---------- %s', e)
                error_list.append(value)

        with open('/home/iuadmin/error_line_voucher.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()


    @api.multi
    def map_voucher_memo(self):

        error_list = []
        header_list = []
        file_obj = '/home/iuadmin/account_voucher_memo_check.csv'
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
                    id = row[0].strip() or 0
                    memo = row[1].strip() or 'Null'
                    check = row[2].strip() or 'Null'
                    self._cr.execute("select id from mi_account_voucher where old_id=" + str(
                        id) + " limit 1")
                    voucher_id = self._cr.fetchone()
                    voucher_id = voucher_id and voucher_id[0] or False
                    if voucher_id:
                        vals = (memo,check,voucher_id)
                        self._cr.execute(""" update mi_account_voucher set memo=%s and check_no=%s where id =%s""",
                                         vals)
                        self._cr.commit()

            except Exception as e:
                self._cr.rollback()
                value.append(str(e))
                _logger.error('------------Error Exception---------- %s', e)
                error_list.append(value)

        with open('/home/iuadmin/err_voucher_memo.csv', 'wb') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerows(header_list)
            writer.writerows(error_list)
            f.close()
