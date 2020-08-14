# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
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
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import logging
_logger = logging.getLogger(__name__)

class project_task(models.Model):
    _inherit = "project.task"

    work_ids=fields.One2many('project.task.work', 'task_id', 'Work done')
    

class project_work(models.Model):
    _name = "project.task.work"
    _description = "Project Task Work"
    _order = "date desc"

    name=fields.Char('Work summary', size=128)
    date=fields.Datetime('Date', index="1",default=lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
    task_id=fields.Many2one('project.task', 'Task', ondelete='cascade', required=True, index="1")
    hours=fields.Float('Time Spent')
    user_id=fields.Many2one('res.users', 'Done by', required=False, index="1",default=False)
    company_id=fields.Many2one(related='task_id.company_id', string='Company', store=True, readonly=True)

    @api.model
    def create(self,vals):
        if 'hours' in vals and (not vals['hours']):
            vals['hours'] = 0.00
        if 'task_id' in vals:
            self._cr.execute('update project_task set remaining_hours=remaining_hours - %s where id=%s', (vals.get('hours',0.0), vals['task_id']))
        return super(project_work,self).create(vals)

    @api.multi
    def write(self,vals):
        res=super(project_work, self).write(vals)
        if 'hours' in vals and (not vals['hours']):
            vals['hours'] = 0.00
        if 'hours' in vals:
            for work in self:
                self._cr.execute('update project_task set remaining_hours=remaining_hours - %s + (%s) where id=%s', (vals.get('hours',0.0), work.hours, work.task_id.id))
        return res

    @api.multi
    def unlink(self):
        for work in self:
            self._cr.execute('update project_task set remaining_hours=remaining_hours + %s where id=%s', (work.hours, work.task_id.id))
        return super(project_work,self).unlink()
