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

#
# Please note that these reports are not multi-currency !!!
#
from odoo import fields,models,api
from odoo.tools.translate import _
from odoo import tools

class report_event(models.Model):
    _name = "report.event"
    _description = "Tasks by interpreter and project"
    _auto = False

    name=fields.Char('Task Summary', size=128, readonly=True)
    day=fields.Char('Day', size=128, readonly=True)
    year=fields.Char('Year', size=64, required=False, readonly=True)
    user_id=fields.Many2one('res.users', 'Assigned To', readonly=True)
    interpreter_id=fields.Many2one("res.partner","Responsible",readonly=True)
    event_id=fields.Many2one("event","Event",readonly=True ,)
    language_id=fields.Many2one("language" ,"Language",readonly=True)
    doctor_id=fields.Many2one("doctor",'Doctor/Location',readonly=True )
    date_start=fields.Date('Starting Date',readonly=True)
    no_of_days=fields.Integer('# of Days', size=128, readonly=True)
    date_end=fields.Date('Ending Date', readonly=True)
    date_deadline=fields.Date('Deadline', readonly=True)
    project_id=fields.Many2one('project.project', 'Project', readonly=True)
    hours_planned=fields.Float('Planned Hours', readonly=True)
    hours_effective=fields.Float('Effective Hours', readonly=True)
    hours_delay=fields.Float('Avg. Plan.-Eff.', readonly=True)
    remaining_hours=fields.Float('Remaining Hours', readonly=True)
    progress=fields.Float('Progress', readonly=True, group_operator='avg')
    total_hours=fields.Float('Total Hours', readonly=True)
    closing_days=fields.Float('Days to Close', digits=(16,2), readonly=True, group_operator="avg",
                                   help="Number of Days to close the task")
    opening_days=fields.Float('Days to Open', digits=(16,2), readonly=True, group_operator="avg",
                                   help="Number of Days to Open the task")
    delay_endings_days=fields.Float('Overpassed Deadline', digits=(16,2), readonly=True)
    nbr=fields.Integer('# of tasks', readonly=True)
    priority=fields.Selection([('4','Very Low'), ('3','Low'), ('2','Medium'), ('1','Urgent'),
                                ('0','Very urgent')], 'Priority', readonly=True)
    month=fields.Selection([('01','January'), ('02','February'), ('03','March'), ('04','April'), ('05','May'), ('06','June'), ('07','July'), ('08','August'), ('09','September'), ('10','October'), ('11','November'), ('12','December')], 'Month', readonly=True)
    state=fields.Selection([('draft', 'Draft'), ('open', 'In Progress'), ('pending', 'Pending'), ('cancelled', 'Cancelled'), ('done', 'Done')],'Status', readonly=True)
    company_id=fields.Many2one('res.company', 'Company', readonly=True)
    partner_id=fields.Many2one('res.partner', 'Contact', readonly=True)
    event_state=fields.Selection([
        ('draft', 'Unscheduled'),
        ('scheduled', 'Scheduled'),
        ('allocated', 'Allocated'),
        ('confirmed', 'Confirmed'),
        ('unbilled', 'Unbilled'),
        ('cancel','Cancelled'),
        ('done', 'Done')],
        'Status', readonly=True, required=True, )
    task_date_from=fields.Date(compute=lambda *a,**k:{}, method=True, type='date',string="Task date from")
    task_date_to=fields.Date(compute=lambda *a,**k:{}, method=True, type='date',string="Task date to")

    _order = 'name desc, project_id'


    def init(self):
        tools.drop_view_if_exists(self._cr, 'report_event')
        self._cr.execute("""
            CREATE or REPLACE view report_event as
              SELECT
                    (select 1 ) AS nbr,
                    t.id as id,
                    to_char(date_start, 'YYYY') as year,
                    to_char(date_start, 'MM') as month,
                    to_char(date_start, 'YYYY-MM-DD') as day,
                    date_trunc('day',t.date_start) as date_start,
                    date_trunc('day',t.date_end) as date_end,
                    to_date(to_char(t.date_deadline, 'dd-MM-YYYY'),'dd-MM-YYYY') as date_deadline,
--                    sum(cast(to_char(date_trunc('day',t.date_end) - date_trunc('day',t.date_start),'DD') as int)) as no_of_days,
                    abs((extract('epoch' from (t.date_end-t.date_start)))/(3600*24))  as no_of_days,
                    t.view_interpreter,
                    t.user_id,
                    t.event_id,
                    progress as progress,
                    t.project_id,
                    e.language_id,
                    e.doctor_id,
                    e.state as event_state,
                    t.state,
                    t.effective_hours as hours_effective,
                    t.priority,
                    t.name as name,
                    t.company_id,
                    t.partner_id,
                    t.stage_id,
                    remaining_hours as remaining_hours,
                    total_hours as total_hours,
                    t.delay_hours as hours_delay,
                    planned_hours as hours_planned,
                    (extract('epoch' from (t.date_end-t.create_date)))/(3600*24)  as closing_days,
                    (extract('epoch' from (t.date_start-t.create_date)))/(3600*24)  as opening_days,
                    abs((extract('epoch' from (t.date_deadline-t.date_end)))/(3600*24))  as delay_endings_days
              FROM project_task t
                join event e on (t.event_id=e.id)
                WHERE t.active = 'true'
                GROUP BY
                    t.id,
                    remaining_hours,
                    t.effective_hours,
                    progress,
                    total_hours,
                    planned_hours,
                    hours_delay,
                    year,
                    month,
                    day,
                    t.create_date,
                    date_start,
                    date_end,
                    date_deadline,
                    t.view_interpreter,
                    t.event_id,
                    t.project_id,
                    e.language_id,
                    e.doctor_id,
                    e.state,
                    t.state,
                    t.priority,
                    t.name,
                    t.company_id,
                    t.partner_id,
                    t.stage_id

        """)


