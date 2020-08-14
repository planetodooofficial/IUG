# -*- coding: utf-8 -*-
# Copyright 2017 Jarvis (www.odoomod.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo
from odoo import api, models, _, fields, osv
from odoo.exceptions import UserError


class AccountPeriod(models.Model):
    _name = "account.period"
    _description = "Account period"
    _order = "date_start, special desc"

    name = fields.Char('Period Name', required=True)
    code = fields.Char('Code', size=12)
    special = fields.Boolean('Opening/Closing Period', help="These periods can overlap.")
    date_start = fields.Date('Start of Period', required=True, states={'done': [('readonly', True)]})
    date_stop = fields.Date('End of Period', required=True, states={'done': [('readonly', True)]})
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Fiscal Year', required=True,
                                    states={'done': [('readonly', True)]}, index=True)
    state = fields.Selection([('draft', 'Open'), ('done', 'Closed')], 'Status', readonly=True, copy=False,
                             default='draft',
                             help='When monthly periods are created. The status is \'Draft\'. At the end of monthly period it is in \'Done\' status.')
    company_id = fields.Many2one('res.company', related='fiscalyear_id.company_id', string='Company', store=True,
                                 readonly=True)

    @api.model
    def find(self,dt=None):
        if not dt:
            dt = fields.Date.context_today(self)
        args = [('date_start', '<=' ,dt), ('date_stop', '>=', dt)]
        if self._context.get('company_id', False):
            args.append(('company_id', '=', self._context['company_id']))
        else:
            company_id = self.env['res.users'].browse(self._uid).company_id.id
            args.append(('company_id', '=', company_id))
        result = []
        #WARNING: in next version the default value for account_periof_prefer_normal will be True
        if self._context.get('account_period_prefer_normal'):
            # look for non-special periods first, and fallback to all if no result is found
            result = self.search(args + [('special', '=', False)])
        if not result:
            result = self.search(args)
        if not result:
            raise UserError(_('There is no period defined for this date: %s.\nPlease create one.')%dt)
        return result