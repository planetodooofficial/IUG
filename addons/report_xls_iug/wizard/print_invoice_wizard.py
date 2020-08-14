# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Noviat nv/sa (www.noviat.com). All rights reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo.tools.translate import _
from odoo import models, fields,api
import time
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError, RedirectWarning, ValidationError

class account_print_invoice_xls(models.TransientModel):
    _name = 'account.print.invoice.xls'
    _description = 'Print/Export Invoice'

    partner_id=fields.Many2one('res.partner',"Customer")
    partner_ids=fields.Many2many('res.partner', 'xls_partner_rel', 'xls_id', 'partner_id', 'Customers')
    multi_customers=fields.Boolean('Multiple Customers')
    date_from=fields.Date("Date From")
    date_to=fields.Date("Date To")
    state=fields.Selection([('all','All'),('draft','Draft'),('open','Open'),('paid','Paid')],'State', required=True,default='open')
    company_id=fields.Many2one('res.company', 'Company', required=True,default=lambda self: self.env['res.company']._company_default_get('account.print.invoice.xls'))
    report_type=fields.Selection([('kaiser','Kaiser Permanente'),('kaiser_compliance','Kaiser Compliance'),('kaiser_cancel_event','Kaiser Cancel Events'),('cobb','Cobb_DFCS'),('cdcr','CDCR-California_Rehabilitation_Ctr'),
                                    ('cst','CST Report for Health and Human Services'),('trans','Translations'),('vdss','VDSS Division of Finance - Budget'),('adp','ADP Total Source'),
                                    ('john_muir','John Muir'),('caloptima','CalOptima'),('sales_commission','Sales Commission'),('hartford','Hartford'),
                                    ('fcci_translation','FCCI Translation'),('fcci_transportation','FCCI Transportation'),
                                    ('acd','ACD'),('inv_profit','Invoice Profitability'),('hipaa','HIPAA')],'Report Type')

    @api.onchange('company_id')
    def onchange_company_id(self):
        ''' Empty some fields on change of company in the Report Form '''
        del_list = []
        for partner in self.partner_ids:
            del_list.append((3,partner.id))
        val = {
            'partner_ids': del_list,
        }
        return {'value': val}

    @api.multi
    def xls_export(self):
        return self.print_report()

    @api.multi
    def print_report(self):
        invoice_obj = self.env['account.invoice']
        event_obj = self.env['event']
        wiz_form = self

        if wiz_form.multi_customers:
            partner_ids = [partner.id for partner in wiz_form.partner_ids] if wiz_form.partner_ids else []
        else:
            partner_ids = wiz_form.partner_id and [wiz_form.partner_id.id] or []
        if not partner_ids:
            raise UserError(_('No Customer is selected , Please select one !'))
        company_id = wiz_form.company_id
        report_type = wiz_form.report_type
        datas = {
            'report_type': report_type
        }
        state_domain = []
        if wiz_form.state:
            if wiz_form.state == 'all':
                state_domain = ['draft','open','paid']
            else:
                state_domain.append(wiz_form.state)
        invoice_ids, invoice_line_ids = [], []
        if report_type and report_type in ('kaiser','fcci_translation','fcci_transportation','sales_commission'):
            if wiz_form.date_from and wiz_form.date_to:
                invoice_ids = invoice_obj.search([('event_start_date','>=',wiz_form.date_from),('event_start_date','<=', wiz_form.date_to),('state', 'in',tuple(state_domain)),
                                                        ('company_id','=',company_id and company_id.id or False),('residual','>',0),
                                                        ('partner_id','in',partner_ids)]).ids
            else:
                invoice_ids = invoice_obj.search([('state','in',tuple(state_domain)),('company_id','=',company_id and company_id.id or False),('residual','>',0),
                                                          ('partner_id','in',partner_ids)]).ids
            if not invoice_ids:
                raise UserError(_('No open Invoices for this Customer in this period .Please try another.'))
            datas.update({
                'model': 'account.invoice',
                'ids': invoice_ids,
            })
        elif report_type and report_type in ('kaiser_compliance', 'cobb', 'cdcr', 'cst', 'vdss', 'adp', 'trans', 'john_muir',
                                             'caloptima', 'hartford', 'acd', 'inv_profit','hipaa'):
            if wiz_form.date_from and wiz_form.date_to:
                self._cr.execute("""SELECT inv_line.id
                          FROM  account_invoice AS inv , account_invoice_line AS inv_line
                          WHERE (inv.id = inv_line.invoice_id) AND inv.company_id = %s AND inv.partner_id in %s
                          AND inv.state in %s AND inv.event_start_date >= %s AND inv.event_start_date <= %s
                          ORDER BY inv.event_start_date """, (company_id and company_id.id or False, tuple(partner_ids),
                                                          tuple(state_domain),wiz_form.date_from , wiz_form.date_to))
                invoice_line_ids = map(lambda x: x[0], self._cr.fetchall())
            else:
                self._cr.execute("""SELECT inv_line.id
                          FROM  account_invoice AS inv , account_invoice_line AS inv_line
                          WHERE (inv.id = inv_line.invoice_id) AND inv.company_id = %s AND inv.partner_id in %s
                          AND inv.state in %s ORDER BY inv.event_start_date 
                          """, (company_id and company_id.id or False,tuple(partner_ids),tuple(state_domain)))
                invoice_line_ids = map(lambda x: x[0], self._cr.fetchall())
            if not invoice_line_ids:
                raise UserError(_('No open Invoices for this Customer in this period .Please try another.'))
            datas.update({
                'model': 'account.invoice.line',
                'ids': invoice_line_ids,
            })
        if report_type and report_type  == 'kaiser_cancel_event':
            if wiz_form.date_from and wiz_form.date_to:
                event_ids = event_obj.search([('event_start_date','>=',wiz_form.date_from),('event_start_date','<=', wiz_form.date_to),('state','=','cancel'),
                                                        ('company_id','=',company_id and company_id.id or False),('partner_id','in',partner_ids)]).ids
            else:
                event_ids = event_obj.search([('company_id','=',company_id and company_id.id or False),
                                                        ('partner_id','in',partner_ids),('state','=','cancel')]).ids
            if not event_ids:
                raise UserError(_('No cancelled events for this Customer in this period.'))
            datas.update({
                'model': 'event',
                'ids': event_ids,
            })
        if report_type and report_type == 'kaiser':
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account.invoice.xls.print.kaiser',
                'datas': datas
            }
        elif report_type and report_type == 'kaiser_compliance':
            return { 
                'type': 'ir.actions.report.xml',
                'report_name': 'account.invoice.line.xls.print.kaiser.compliance',
                'datas': datas
            }
        elif report_type and report_type == 'kaiser_cancel_event':
            return { 
                'type': 'ir.actions.report.xml',
                'report_name': 'action.kaiser.cancel.event.xls',
                'datas': datas,
                'report_type':'xls'
            }
        elif report_type and report_type == 'cobb':
            return { 
                'type': 'ir.actions.report.xml',
                'report_name': 'account.invoice.xls.print.cobb',
                'datas': datas
            }
        elif report_type and report_type == 'cdcr':
            return { 
                'type': 'ir.actions.report.xml',
                'report_name': 'account.invoice.xls.print.cdcr',
                'datas': datas
            }
        elif report_type and report_type == 'adp':
            return { 'type': 'ir.actions.report.xml',
                     'report_name': 'account.invoice.xls.print.adp',
                     'datas': datas
                   }
        elif report_type and report_type == 'cst':
            if wiz_form.partner_id and wiz_form.partner_id.id==177990:
                return {'type': 'ir.actions.report.xml',
                        'report_name': 'account.invoice.xls.print.cst.org',
                        'datas': datas
                        }
            else:
                return { 'type': 'ir.actions.report.xml',
                     'report_name': 'account.invoice.xls.print.cst',
                     'datas': datas
                   }

        elif report_type and report_type == 'trans':
            if wiz_form.partner_id and wiz_form.partner_id.id==177990:
                return {'type': 'ir.actions.report.xml',
                        'report_name': 'account.invoice.xls.print.trans.org',
                        'datas': datas,
                        'context': {'translation': True},
                        }
            else:
                return { 'type': 'ir.actions.report.xml',
                     'report_name': 'account.invoice.xls.print.trans',
                     'datas': datas,
                         'context': {'translation': True},
                   }
        elif report_type and report_type == 'vdss':
            return { 'type': 'ir.actions.report.xml',
                     'report_name': 'account.invoice.xls.print.vdss',
                     'datas': datas
                   }
        elif report_type and report_type == 'john_muir':
            return { 'type': 'ir.actions.report.xml',
                     'report_name': 'account.invoice.xls.print.john.muir',
                     'datas': datas
                   }
        elif report_type and report_type == 'caloptima':
            return { 'type': 'ir.actions.report.xml',
                     'report_name': 'account.invoice.xls.print.caloptima',
                     'datas': datas
                   }
        elif report_type and report_type == 'sales_commission':
            return {'type': 'ir.actions.report.xml',
                    'report_name':'account.invoice.xls.print.sales.commission',
                    'datas': datas
                   }
        elif report_type and report_type == 'hartford':
            return { 'type': 'ir.actions.report.xml',
                     'report_name': 'account.invoice.line.xls.print.hartford',
                     'datas': datas
                   }
        elif report_type and report_type == 'fcci_translation':
            return {'type': 'ir.actions.report.xml',
                    'report_name':'account.invoice.xls.print.fcci_translation',
                    'datas': datas,
                    'context':{'translation':True},
                   }
        elif report_type and report_type == 'fcci_transportation':
            return {'type': 'ir.actions.report.xml',
                    'report_name':'account.invoice.xls.print.fcci_transportation',
                    'datas': datas,
                    'context':{'transportation':True},
                   }
        elif report_type and report_type == 'acd':
            return { 'type': 'ir.actions.report.xml',
                     'report_name': 'account.invoice.line.xls.print.acd',
                     'datas': datas
                }
        elif report_type and report_type == 'inv_profit':
            return {'type': 'ir.actions.report.xml',
                    'report_name': 'account.invoice.xls.print.invoice.profitability',
                    'datas': datas
                    }
        elif report_type and report_type == 'hipaa':
            return {'type': 'ir.actions.report.xml',
                    'report_name': 'account.invoice.xls.print.hipaa',
                    'datas': datas
                    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
