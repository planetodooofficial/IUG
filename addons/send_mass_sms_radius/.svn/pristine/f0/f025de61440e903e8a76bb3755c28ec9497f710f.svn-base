##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>)
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
from odoo import models,fields, api
from odoo.tools.translate import _
from odoo import SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)
from pyzipcode import ZipCodeDatabase,ZipNotFoundException
zcdb = ZipCodeDatabase()
import datetime
from dateutil import relativedelta
from odoo.exceptions import UserError, RedirectWarning, ValidationError,AccessDenied

class res_partner(models.Model):
    _inherit = 'res.partner'

    partner_id_sms=fields.Many2one('sms.mass.radius',string='Partner Sms')


class sms_mass_radius(models.Model):
    _name = 'sms.mass.radius'

    name=fields.Char('',default='Mass Sms')
    zip=fields.Integer('Zip')
    radius=fields.Integer('Radius')
    body=fields.Text('Text',size=160)
    interpreter_ids=fields.One2many("res.partner", 'partner_id_sms',string='Recipients',readonly=1 )
    language_id=fields.Many2one('language', 'Language')
    state_id=fields.Many2one("res.country.state", string='State')
    label_flag=fields.Boolean("Flag")
    flag=fields.Boolean("Flag")
    gender=fields.Selection([('male','Male'),('female','Female')],"Gender")
    age_from=fields.Integer('Age From')
    age_to=fields.Integer('Age To')
    certification_level_id=fields.Many2one("certification.level","Certification Level")
    is_simultaneous=fields.Boolean("Is Simultaneous")
    
    @api.multi
    def sms_mass_radius(self):
        body2 = self.body
        if body2 == False:
            raise UserError(_('Please Enter Message'))
        else:
            try:
                for partner in self.interpreter_ids:
                    if partner.phone:
                        sms_vals = {'sms_body': body2, 'sms_to': partner.phone}
                        message = self.env['twilio.sms.send'].create(sms_vals)
            except:
                pass
            self._cr.execute('''delete from sms_mass_radius where id != %s'''%self.id)
            self._cr.commit()
            raise UserError(_('Messages Sent'))
    
    @api.multi
    def show_recipients(self):
            zip2=self.zip
            language_id2 = self.language_id.id
            state_id2 = self.state_id.id
            radius2 = self.radius
            notify_pids = []
            partner_obj=self.env['res.partner']
            domain=[('cust_type','=','interpreter'),('name','!=',''),('is_interpretation_active','=',True)]
            if state_id2:
                domain.append(('state_id','=',state_id2))
            if zip2 and not radius2:
                domain.append(('zip', '=', zip2))
            if self.gender:
                domain.append(('gender', '=', self.gender))
            if self.age_from and self.age_to:
                cur=((datetime.datetime.now())-relativedelta.relativedelta(years=self.age_from)).strftime('%Y-%m-%d')
                domain.append(('dob','<=',cur))
            if self.age_from and not self.age_to:
                raise UserError(_('Please specify Age to as well'))
            if not self.age_from and self.age_to:
                raise UserError(_('Please specify Age From as well'))
            if self.age_to and self.age_from:
                if self.age_to < self.age_from:
                    raise UserError(_('Age to should be greater than Age From'))
                else:
                    cur = ((datetime.datetime.now()) - relativedelta.relativedelta(years=self.age_to)).strftime(
                        '%Y-%m-%d')
                    domain.append(('dob', '>=', cur))
            logger = logging.getLogger('test2')
            logger.info("This is notify pids------->%s " % str((domain)))
            partner_ids = partner_obj.search(domain)
            if partner_ids:
                if not radius2 and not language_id2:
                    notify_pids=partner_ids.ids
                elif zip2 and radius2 and not language_id2:
                    for partner in partner_ids:
                        select_interpreter=False
                        if partner.zip:
                             try:
                                 zips = [z.zip for z in zcdb.get_zipcodes_around_radius(zip2, radius2)]
                                 for myzip in zips:
                                     if partner.zip in myzip:
                                         notify_pids.append(partner.id)
                                         continue
                             except ZipNotFoundException:
                                 raise UserError(_('Please Enter valid ZIPCODE'))
                elif not radius2 and language_id2:
                    if self.certification_level_id and not self.is_simultaneous:
                        for partner in partner_ids:
                            select_interpreter=False
                            if partner.language_lines:
                                for rec in partner.language_lines:
                                    if language_id2 == rec.name.id:
                                        if rec.certification_level_id == self.certification_level_id:
                                            notify_pids.append(partner.id)
                                            continue
                    elif not self.certification_level_id and self.is_simultaneous:
                        for partner in partner_ids:
                            select_interpreter=False
                            if partner.language_lines:
                                for rec in partner.language_lines:
                                    if language_id2 == rec.name.id:
                                        if rec.is_simultaneous:
                                            notify_pids.append(partner.id)
                                            continue
                    elif self.certification_level_id and self.is_simultaneous:
                        for partner in partner_ids:
                            select_interpreter=False
                            if partner.language_lines:
                                for rec in partner.language_lines:
                                    if language_id2 == rec.name.id:
                                        if rec.certification_level_id == self.certification_level_id and rec.is_simultaneous:
                                            notify_pids.append(partner.id)
                                            continue
                    else:
                        for partner in partner_ids:
                            select_interpreter=False
                            if partner.language_lines:
                                for rec in partner.language_lines:
                                    if language_id2 == rec.name.id:
                                            notify_pids.append(partner.id)
                                            continue
                elif zip2 and radius2 and language_id2:
                    notify_pids_all=[]
                    for partner in partner_ids:
                        select_interpreter=False
                        if partner.zip:
                             try:
                                 zips = [z.zip for z in zcdb.get_zipcodes_around_radius(zip2, radius2)]
                                 for myzip in zips:
                                     if partner.zip in myzip:
                                         notify_pids_all.append(partner.id)
                                         continue
                             except ZipNotFoundException:
                                 raise UserError(_('Please Enter valid ZIPCODE'))
                    if self.certification_level_id and not self.is_simultaneous:
                        for partner in partner_obj.browse(notify_pids_all):
                            select_interpreter=False
                            if partner.language_lines:
                                for rec in partner.language_lines:
                                    if language_id2 == rec.name.id:
                                        if rec.certification_level_id == self.certification_level_id:
                                            notify_pids.append(partner.id)
                                            continue
                    elif not self.certification_level_id and self.is_simultaneous:
                        for partner in partner_obj.browse(notify_pids_all):
                            select_interpreter=False
                            if partner.language_lines:
                                for rec in partner.language_lines:
                                    if language_id2 == rec.name.id:
                                        if rec.is_simultaneous:
                                            notify_pids.append(partner.id)
                                            continue
                    elif self.certification_level_id and self.is_simultaneous:
                        for partner in partner_obj.browse(notify_pids_all):
                            select_interpreter=False
                            if partner.language_lines:
                                for rec in partner.language_lines:
                                    if language_id2 == rec.name.id:
                                        if rec.certification_level_id == self.certification_level_id and rec.is_simultaneous:
                                            notify_pids.append(partner.id)
                                            continue
                    else:
                        for partner in partner_obj.browse(notify_pids_all):
                            select_interpreter=False
                            if partner.language_lines:
                                for rec in partner.language_lines:
                                    if language_id2 == rec.name.id:
                                            notify_pids.append(partner.id)
                                            continue
            if not notify_pids:
                logger = logging.getLogger('test2')
                logger.info("This is notify pids no------->%s " % str(len(notify_pids)))
                self.write({'label_flag': True, 'flag': False})
                self._cr.commit()
            else:
                logger = logging.getLogger('test2')
                logger.info("This is notify pids yes------->%s " % str(len(notify_pids)))
                result=self.write({'interpreter_ids': [(6,0,notify_pids)],'label_flag': False, 'flag': True})
                self._cr.commit()
            return True





# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
