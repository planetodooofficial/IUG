# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from odoo.report import report_sxw

class event_approval(report_sxw.rml_parse):
#    _inherit='account.invoice'
#    _name = 'account.invoice'
    def __init__(self, cr, uid, name, context):
        super(event_approval, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,

        })

report_sxw.report_sxw(
    'report.event.approval.report',
    'event',
    'custom_addons/bista_iugroup/report/event_approval_report.rml',
    parser=event_approval
)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

