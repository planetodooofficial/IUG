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

# import openerp
# from openerp import pooler, tools
from odoo import fields,models,api,_
from odoo import SUPERUSER_ID, tools
# from openerp.tools import flatten

class mail_message(models.Model):
    _inherit = 'mail.message'

    attach_to=fields.Selection([('event','Event'),('partner','Partner')],'Attach To',default='event')
    partner_id=fields.Many2one('res.partner','Partner')
    event_id=fields.Many2one('event','Event')
    company_id=fields.Many2one('res.company', 'Company', index=1,default=lambda self: self.env['res.company']._company_default_get('mail.message'))

    @api.onchange('attach_to')
    def onchange_attach_to(self):
        ''' Onchange Function to bring Fax from partner '''
        if self.attach_to and self.attach_to == 'event':
            val={
                'partner_id': False,
                }
        else:
            val={
                'event_id': False,
                }
        return {'value': val}

    @api.multi
    def attach_documents(self):
        ''' Function to attach incoming Documents to any event or Partner '''
        for cur in self:
            if cur.attach_to == 'event' and cur.event_id:
                for attach in cur.attachment_ids:
                    if attach.attach:
                        attach.sudo().write({'res_model':'event', 'res_id':cur.event_id.id,'res_name':cur.event_id.name})
                        cur.event_id.sudo().write({'fee_note_test':True})
            elif cur.attach_to == 'partner' and cur.partner_id:
                for attach in cur.attachment_ids:
                    if attach.attach:
                        attach.sudo().write({'res_model':'res.partner', 'res_id':cur.partner_id.id,'res_name':cur.partner_id.name})
        return True

