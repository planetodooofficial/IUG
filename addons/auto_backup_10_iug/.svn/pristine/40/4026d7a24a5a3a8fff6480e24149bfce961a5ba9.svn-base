    # -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import xmlrpclib
import socket
import requests
import os
import shutil
import functools
import time
import datetime
import base64
import re
import logging
import ftplib

import paramiko

from odoo import models, fields, api, tools, _
from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)

def execute(connector, method, *args):
    res = False
    try:        
        res = getattr(connector,method)(*args)
    except socket.error,e:        
            raise e
    return res

addons_path = tools.config['addons_path'] + '/auto_backup/DBbackups'

class db_backup(models.Model):
    _name = 'db.backup'

    @api.multi
    def get_db_list(self, host, port, context={}):
        uri = 'http://' + host + ':' + port
        conn = xmlrpclib.ServerProxy(uri + '/xmlrpc/db')
        db_list = execute(conn, 'list')
        return db_list

    @api.multi
    def _get_db_name(self):
        dbName = self._cr.dbname
        return dbName
        
    # Columns for local server configuration
    host = fields.Char('Host', size=100, required=True, default='localhost')
    port = fields.Char('Port', size=10, required=True, default=8069)
    name = fields.Char('Database', size=100, required=True, help='Database you want to schedule backups for', default=_get_db_name)
    folder = fields.Char('Backup Directory', size=100, help='Absolute path for storing the backups', required='True', default='/odoo/backups')


    @api.multi
    def _check_db_exist(self):
        self.ensure_one()
        db_list = self.get_db_list(self.host, self.port)
        if self.name in db_list:
            return True
        return False
    
    _constraints = [(_check_db_exist, _('Error ! No such database exists!'), [])]

    @api.multi
    def schedule_backup(self):
        conf_ids = self.search([])
        for rec in conf_ids:
            db_list = self.get_db_list(rec.host, rec.port)
            if rec.name in db_list:
                try:
                    if not os.path.isdir(rec.folder):
                        os.makedirs(rec.folder)
                except:
                    raise
                #Create name for dumpfile.
                bkp_file='%s_%s.sql' % (rec.name,time.strftime('%Y%m%d_%H_%M_%S'))
                file_path = os.path.join(rec.folder,bkp_file)
                fp = open(file_path, 'wb')
                uri = 'http://' + rec.host + ':' + rec.port
                conn = xmlrpclib.ServerProxy(uri + '/xmlrpc/db')
                try:
                    bkp_resp = requests.post(
                        uri + '/web/database/backup', stream=True,
                        data={
                            'master_pwd': tools.config['admin_passwd'],
                            'name': rec.name,
                            'backup_format': 'dump',
                        }
                    )
                    bkp_resp.raise_for_status()
                except:
                    _logger.info(
                        "Couldn't backup database %s. Bad database administrator password for server running at http://%s:%s" % (
                        rec.name, rec.host, rec.port))
                    continue
                bkp_resp.raw.read = functools.partial(
                    bkp_resp.raw.read, decode_content=True)
                shutil.copyfileobj(bkp_resp.raw, fp)
                fp.close()
            else:
                _logger.info("database %s doesn't exist on http://%s:%s" %(rec.name, rec.host, rec.port))

