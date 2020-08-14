# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2009-today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

import base64
import datetime
import dateutil
import email
import logging
import pytz
import re
import time
import xmlrpclib
from email.message import Message

from openerp import tools
from openerp import SUPERUSER_ID
from openerp.addons.mail.mail_message import decode
from openerp.osv import fields, osv, orm
from openerp.osv.orm import browse_record, browse_null
from openerp.tools.safe_eval import safe_eval as eval
from openerp.tools.translate import _


# +++++++++++++++++ Not used yet ++++++++++++++++++++++

class mail_thread(osv.AbstractModel):
    _inherit = 'mail.thread'
    
    def unlink(self, cr, uid, ids, context=None):
        """ Overriden  to rectify error of domain while searching """
        if isinstance(ids, (int, long)): ids = [ids]
        msg_obj = self.pool.get('mail.message')
        fol_obj = self.pool.get('mail.followers')
        # delete messages and notifications
        msg_ids = msg_obj.search(cr, uid, [('model', '=', self._name), ('res_id', 'in', ids)], context=context)
        msg_obj.unlink(cr, uid, msg_ids, context=context)
        # delete
        res = super(mail_thread, self).unlink(cr, uid, ids, context=context)
        # delete followers
        fol_ids = fol_obj.search(cr, SUPERUSER_ID, [('res_model', '=', self._name), ('res_id', 'in', ids)], context=context)
        fol_obj.unlink(cr, SUPERUSER_ID, fol_ids, context=context)
        return res