# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo import osv
from odoo import SUPERUSER_ID
from odoo.tools.translate import _
import logging
_logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _name = 'hr.employee'
    _inherit = ['hr.employee', 'website.published.mixin','website.crm']

    public_info = fields.Text(string='Public Info', readonly=True)
    status = fields.Selection([('public', 'Public'),('private', 'Private')], string='Visibility',
                              help='Employee\'s visibility in the portal\'s contact page', defaults='private')

class crm_contact_us(models.Model):
    _name = 'crm.contact.us'
    _inherit = 'crm.lead'

    def _get_employee(self):
        r = self.env['hr.employee'].search([('visibility', '!=', 'private')])
        return r

    employee_ids = fields.Many2many('hr.employee', string='Employees', default=_get_employee,readonly=True)