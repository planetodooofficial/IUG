# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2004-2012 OpenERP S.A. (<http://openerp.com>).
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

import logging
_logger = logging.getLogger(__name__)

import re
from odoo import models, fields,api,_
from bss_phonumbers_fields import bss_phonenumbers_converter as phonumbers_converter
import phonenumbers
from odoo.exceptions import UserError, RedirectWarning, ValidationError

class hr_department(models.Model):
    ''' adds extra fields to Department'''
    _inherit = "hr.department"

    department=fields.Integer('IU Department Id')


class hr_employee(models.Model):
    ''' adds extra fields to Employee'''
    _inherit = "hr.employee"

    birthdate=fields.Char('Birthdate', size=64)
    end_date=fields.Char('End Date')
    hire_date=fields.Char('Hire Date')
    email2=fields.Char('Email2', size=240)
    is_alert=fields.Boolean('Alert', help="Select if on alert")
    middle_name=fields.Char('Middle Name', size=128, index=True)
    last_name=fields.Char('Last Name', size=128, index=True)
    rating_id=fields.Many2one('rating',"Rating")
    suffix=fields.Char('Suffix', size=64, index=True)
    due_days=fields.Integer("Due Days")
    zone_id=fields.Many2one("zone","Zone",)
    modem=fields.Char('Modem', size=64,)
    phone2=fields.Char('Phone 2', size=64)
    meta_zone_id=fields.Many2one('meta.zone',"Meta Zone")
    staff_id=fields.Integer("IU Staff ID")
    vendor_id2=fields.Integer("IU Vendor ID")
    is_schedular=fields.Boolean('Is Schedular', help="")
    short_name=fields.Char('Short Name', size=100, index=True)

    _constraints = [
        (models.BaseModel._check_recursion, 'You cannot create recursive Interpreter hierarchies.', ['parent_id']),
    ]

    @api.model
    def get_default_country(self):
        """Return the Default Country """
        proxy = self.env['ir.config_parameter']
        default_country = proxy.sudo().get_param('default_country')
        if not default_country:
            raise UserError('Please use Default Country as US in config parameters.')
        return default_country.strip()

    @api.onchange('phone2','work_phone','mobile_phone')
    def onchange_phone(self):
        ''' function to change in the format of selected default country '''
        result = {}
        result['value'] = {}
        def_country = self.get_default_country()
        new_phone = ''
        if self.work_phone:
            try:
                pn = phonumbers_converter._parse(self.work_phone, def_country)
                if  pn:
                    new_phone = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.E164)
                else:
                    new_phone = None
            except phonenumbers.NumberParseException:
                phone = None
                pass
            result['value']['work_phone'] = new_phone
        new_phone = ''
        if self.phone2:
            try:
                pn = phonumbers_converter._parse(self.phone2, def_country)
                if  pn:
                    new_phone = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.E164)
                else:
                    new_phone = None
            except phonenumbers.NumberParseException:
                phone2 = None
                pass
            result['value']['phone2'] = new_phone
        if self.mobile_phone:
            try:
                pn = phonumbers_converter._parse(self.mobile_phone, def_country)
                if  pn:
                    new_phone = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.E164)
                else:
                    new_phone = None
            except phonenumbers.NumberParseException:
                phone3 = None
                pass
            result['value']['mobile_phone'] = new_phone
        return result

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = ''
            name = record.name
            name = name + ' ' + (record.middle_name or '')
            name = name + ' ' + (record.last_name or '')
            if self._context.get('show_email') and record.email:
                name = "%s <%s>" % (name, record.email)
            res.append((record.id, name))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        #print "operator.....name....args..",operator,name,args
        if not args:
            args = []
        if name:
            ids = self.search([('name','=',name)]+ args, limit=limit)
            if not ids:
                ids = self.search([('middle_name','=',name)]+ args, limit=limit)
            if not ids:
                ids = self.search([('last_name','=',name)]+ args, limit=limit)
            if not ids:
                # Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
                # on a database with thousands of matching products, due to the huge merge+unique needed for the
                # OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
                # Performing a quick memory merge of ids in Python will give much better performance
                ids = set()
                ids.update(self.search(args + [('name',operator,name)], limit=limit))
                ids.update(self.search(args + [('middle_name',operator,name)], limit=limit))
                ids.update(self.search(args + [('last_name',operator,name)], limit=limit))
                if not limit or len(ids) < limit:
                    # we may underrun the limit because of dupes in the results, that's fine
                    ids.update(self.search(args + [('name',operator,name)], limit=(limit and (limit-len(ids)) or False)))
                #print "ids5.............",ids
            if not ids:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    ids = self.search([('name','=', res.group(2))] + args, limit=limit)
                #print "ids6.............",ids
        else:
            ids = self.search(args, limit=limit)
            #print "ids7.............",ids
        result = ids.name_get()
        return result
