# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Agile Business Group sagl (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from odoo import models, fields, api
from odoo import osv
from datetime import datetime


class network_audit_log(models.Model):
    _name = 'network.audit.log'
    
    
    # @api.depends('name')
    def _calculate_month(self):
        if self.name:
            tm_tuple = datetime.strptime(self.name, '%Y-%m-%d').strftime('%b')
            self.month = tm_tuple  
    
    # @api.depends('name')
    def _calculate_year(self):
        if self.name:
            tm_tuple = datetime.strptime(self.name, '%Y-%m-%d').strftime('%Y')
            self.year = tm_tuple
    
    name = fields.Date(string='Creation Date', readonly=True, required=True)
    log_line = fields.One2many('network.audit.log.line', 'log_id',  string='Logs')
    month = fields.Char(compute='_calculate_month',string='Month',size=4,store=True)
    year = fields.Char(compute='_calculate_year',string='Year',size=5,store=True)
         
    _sql_constraints = [
        ('number_uniq', 'unique(name)', 'Log date must be unique per day.!'),
                        ]
    #user_id = fields.Many2one('network.audit.log.line', related='user_id.user_id',string='User Name', readonly=True)
    #name_log_line = fields.Many2one('network.audit.log.line',related='name_log_line.name_log_line',string='Login DateTime', readonly=True)
    #logout = fields.Many2one('network.audit.log.line',related='logout.logout',string='Logout DateTime', readonly=True)
    #user_ip = fields.Many2one('network.audit.log.line',related='user_ip.user_ip',string='User IP',size=20,readonly=True)
    #session_id = fields.Many2one('network.audit.log.line',related='session_id.session_id',string='Session ID',size=250,readonly=True)
    
class network_audit_log_line(models.Model):
    _name = 'network.audit.log.line'
    _order = 'user_id,name'
	
    # @api.depends('name')
    def _calculate_month(self):
        if self.name:
            tm_tuple = datetime.strptime(self.name, '%Y-%m-%d').strftime('%b')
            self.month = tm_tuple  
    
    # @api.depends('name')
    def _calculate_year(self):
        if self.name:
            tm_tuple = datetime.strptime(self.name, '%Y-%m-%d').strftime('%Y')
            self.year = tm_tuple
			
    name = fields.Datetime(string='Login DateTime', readonly=True, required=True)
    logout = fields.Datetime(string='Logout DateTime', readonly=True)
    log_id = fields.Many2one('network.audit.log',string='Log Id', ondelete='cascade')
    user_ip = fields.Char(string='User IP',size=20,readonly=True)
    session_id = fields.Char(string='Session ID',size=250,readonly=True)
    user_id = fields.Many2one('res.users', string='User Name', readonly=True)
    month = fields.Char(compute='_calculate_month',string='Month',size=4,store=True)
    year = fields.Char(compute='_calculate_year',string='Year',size=5,store=True)
    creation_date = fields.Date(string="Creation Date",  readonly=True,related='log_id.name')

#class network_audit_log(models.Model):
    #_inherit = 'network.audit.log'
    #log_line = fields.One2many('network.audit.log.line',  string='Logs')
    #user_id = fields.Many2one('network.audit.log.line', string='User Name', readonly=True)
    #name_log_line = fields.Many2one('network.audit.log.line',string='Login DateTime', readonly=True)
    #logout = fields.Many2one('network.audit.log.line',string='Logout DateTime', readonly=True)
    #user_ip = fields.Many2one('network.audit.log.line',string='User IP',size=20,readonly=True)
    #session_id = fields.Many2one('network.audit.log.line',string='Session ID',size=250,readonly=True)
  