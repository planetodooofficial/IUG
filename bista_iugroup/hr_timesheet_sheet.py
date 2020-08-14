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
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools.sql import drop_view_if_exists
from odoo import fields, models,api,_
from odoo.exceptions import UserError, ValidationError
# from openerp.tools.translate import _
# from openerp import netsvc

class hr_timesheet_sheet(models.Model):
    _inherit = "hr_timesheet_sheet.sheet"

    @api.constrains('date_to', 'date_from', 'employee_id')
    def _check_sheet_date(self, forced_user_id=False):
        for sheet in self:
            employee_id = sheet.employee_id and sheet.employee_id.id
            if employee_id:
                self.env.cr.execute('SELECT id \
                                FROM hr_timesheet_sheet_sheet \
                                WHERE (date_from <= %s and %s <= date_to) \
                                    AND employee_id=%s \
                                    AND id <> %s', (sheet.date_to, sheet.date_from, employee_id, sheet.id))
                if any(self.env.cr.fetchall()):
                    raise ValidationError(_(
                        'You cannot have 2 timesheets that overlap!\nPlease use the menu \'My Current Timesheet\' to avoid this problem.'))


class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'

    interpreter_id=fields.Many2one("hr.employee","Responsible",)

class account_analytic_line(models.Model):
    _inherit = 'account.analytic.line'

    interpreter_id=fields.Many2one(related='account_id.interpreter_id', string='Interpreter',store=True)

    @api.depends('date', 'user_id', 'project_id', 'sheet_id_computed.date_to', 'sheet_id_computed.date_from',
                 'sheet_id_computed.employee_id')
    def _compute_sheet(self):
        """Links the timesheet line to the corresponding sheet
        """
        for ts_line in self:
            if not ts_line.project_id:
                continue
            sheets = self.env['hr_timesheet_sheet.sheet'].search(
                [('date_to', '>=', ts_line.date), ('date_from', '<=', ts_line.date),
                 ('employee_id', '=', ts_line.interpreter_id.id),
                 ('state', 'in', ['draft', 'new'])])
            if sheets:
                # [0] because only one sheet possible for an employee between 2 dates
                ts_line.sheet_id_computed = sheets[0]
                ts_line.sheet_id = sheets[0]

# class hr_analytic_timesheet(models.Model):
#     _inherit = "hr.analytic.timesheet"
#
#     def _sheet(self, cursor, user, ids, name, args, context=None):
#         sheet_obj = self.pool.get('hr_timesheet_sheet.sheet')
#         res = {}.fromkeys(ids, False)
#         for ts_line in self.browse(cursor, user, ids, context=context):
#             sheet_ids = sheet_obj.search(cursor, user,
#                 [('date_to', '>=', ts_line.date), ('date_from', '<=', ts_line.date),
#                  ('employee_id', '=', ts_line.interpreter_id.id)],
#                 context=context)
#             if sheet_ids:
#             # [0] because only one sheet possible for an employee between 2 dates
#                 res[ts_line.id] = sheet_obj.name_get(cursor, user, sheet_ids, context=context)[0]
#         return res
#     def _get_account_analytic_line(self, cr, uid, ids, context=None):
#         ts_line_ids = self.pool.get('hr.analytic.timesheet').search(cr, uid, [('line_id', 'in', ids)])
#         #print "ts_line_ids.an line....",ts_line_ids
#         return ts_line_ids
#     def _get_hr_timesheet_sheet(self, cr, uid, ids, context=None):
#         #print "going in........."
#         ts_line_ids = []
#         for ts in self.browse(cr, uid, ids, context=context):
# #            cr.execute("""
# #                    SELECT l.id
# #                        FROM hr_analytic_timesheet l
# #                    INNER JOIN account_analytic_line al
# #                        ON (l.line_id = al.id)
# #                    WHERE %(date_to)s >= al.date
# #                        AND %(date_from)s <= al.date
# #                        AND %(user_id)s = al.user_id
# #                    GROUP BY l.id""", {'date_from': ts.date_from,
# #                                        'date_to': ts.date_to,
# #                                        'user_id': ts.employee_id.user_id.id,})
#             cr.execute("""
#                     SELECT l.id
#                         FROM hr_analytic_timesheet l
#                     INNER JOIN account_analytic_line al
#                         ON (l.line_id = al.id)
#                     WHERE %(date_to)s >= al.date
#                         AND %(date_from)s <= al.date
#                         AND %(interpreter_id)s = al.interpreter_id
#                     GROUP BY l.id""", {'date_from': ts.date_from,
#                                         'date_to': ts.date_to,
#                                         'interpreter_id': ts.employee_id.id,})
#             ts_line_ids.extend([row[0] for row in cr.fetchall()])
# #        print "ts_line_ids.........",ts_line_ids
#         return ts_line_ids
#
#     _columns = {
#         #'line_id': fields.many2one('account.analytic.line', 'Analytic Line', ondelete='cascade', required=True),
#         #'partner_id': fields.related('account_id', 'partner_id', type='many2one', string='Partner', relation='res.partner', store=True),
#         #'account_id': fields.many2one('account.analytic.account', 'Analytic Account', required=True, ondelete='restrict', select=True, domain=[('type','<>','view')]),
#         'interpreter_id': fields.related('line_id', 'interpreter_id', type='many2one', string='Interpreter', relation='hr.employee',store=True),
#
#         'sheet_id': fields.function(_sheet, string='Sheet', select="1",
#             type='many2one', relation='hr_timesheet_sheet.sheet', ondelete="cascade",
#             store={
#                     'hr_timesheet_sheet.sheet': (_get_hr_timesheet_sheet, ['employee_id', 'date_from', 'date_to'], 10),
#                     'account.analytic.line': (_get_account_analytic_line, ['interpreter_id', 'date'], 10),
#                     'hr.analytic.timesheet': (lambda self,cr,uid,ids,context=None: ids, None, 10),
#                   },
#             ),
#     }


class hr_timesheet_sheet_sheet_account(models.Model):
    _inherit = "hr_timesheet_sheet.sheet.account"

    @api.model_cr
    def init(self):
        drop_view_if_exists(self._cr, 'hr_timesheet_sheet_sheet_account')
        self._cr.execute("""create view hr_timesheet_sheet_sheet_account as (
                select
                    min(l.id) as id,
                    l.account_id as name,
                    s.id as sheet_id,
                    sum(l.unit_amount) as total
                from
                    account_analytic_line l
                        LEFT JOIN hr_timesheet_sheet_sheet s
                            ON (s.date_to >= l.date
                                AND s.date_from <= l.date
                                AND s.employee_id = l.interpreter_id)
                group by l.account_id, s.id
            )""")


