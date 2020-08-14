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

from odoo import fields,models,api
from odoo.tools.translate import _
from odoo.exceptions import UserError

class custom_timesheet_open(models.TransientModel):
    _name = 'custom.timesheet.open'
    _description = 'custom.timesheet.open'

    @api.multi
    def open_timesheet(self):
        ts = self.env['timesheet']
        view_type = 'form,tree'

        user_ids = self.env['res.partner'].search([('user_id','=',self.env.uid)])
        if not len(user_ids):
            raise UserError(_('Please create an employee and associate it with this user.'))
        ids = ts.search([('user_id','=',self.env.uid),('state','in',('draft','new')),('date_from','<=',fields.Date.context_today(self)),
                                ('date_to','>=',fields.Date.context_today(self))]).ids
        if len(ids) > 1:
            view_type = 'tree,form'
            domain = "[('id','in',["+','.join(map(str, ids))+"]),('user_id', '=', uid)]"
        elif len(ids)==1:
            domain = "[('user_id', '=', uid)]"
        else:
            domain = "[('user_id', '=', uid)]"
        value = {
            'domain': domain,
            'name': _('Open Timesheet'),
            'view_type': 'form',
            'view_mode': view_type,
            'res_model': 'timesheet',
            'view_id': False,
            'type': 'ir.actions.act_window'
        }
        if len(ids) == 1:
            value['res_id'] = ids[0]
        return value

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
