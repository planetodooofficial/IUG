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

import xlwt
import time
from datetime import datetime
from odoo import models
from odoo.report import report_sxw
from odoo.addons.report_xls.report_xls import report_xls
from odoo.addons.report_xls.utils import rowcol_to_cell, _render
from odoo.tools.translate import translate, _
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from odoo.api import Environment
_ir_translation_name = 'move.line.list.xls'

class account_invoice_xls_parser_kaiser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(account_invoice_xls_parser_kaiser, self).__init__(cr, uid, name, context=context)
        self.env = Environment(cr, uid, context)
        invoice_obj = self.env['account.invoice']
        self.context = context
        wanted_list = invoice_obj._report_xls_fields_kaiser()
        template_changes = invoice_obj._report_xls_template_kaiser()
        space_extra = invoice_obj._report_xls_render_space_extra_kaiser()
        self.localcontext.update({
            'datetime': datetime,
            'wanted_list': wanted_list,
            'template_changes': template_changes,
            'space_extra': space_extra,
            '_': self._,
        })

    def _(self, src):
        lang = self.context.get('lang', 'en_US')
        return translate(self.cr, _ir_translation_name, 'report', lang, src) or src


class account_invoice_xls_kaiser(report_xls):
    
    def parse_unicode(self, val):
        try:
            if val:
                val = val.encode('utf-8', 'ignore')
                try:
                    val = unicode(val, "ascii",'ignore')
                except UnicodeError:
                    val = unicode(val, "utf-8", 'ignore').decode('ascii')
            else:
                val = ''
        except Exception:
            pass
        return val
    
    def __init__(self, name, table, rml=False, parser=False, header=True, store=False):
        super(account_invoice_xls_kaiser, self).__init__(name, table, rml, parser, header, store)

        # Cell Styles
        _xs = self.xls_styles
        # header
        rh_cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
        self.rh_cell_style = xlwt.easyxf(rh_cell_format)
        self.rh_cell_style_center = xlwt.easyxf(rh_cell_format + _xs['center'])
        self.rh_cell_style_right = xlwt.easyxf(rh_cell_format + _xs['right'])
        # lines
        aml_cell_format = _xs['borders_all']
        self.aml_cell_style = xlwt.easyxf(aml_cell_format)
        self.aml_cell_style_center = xlwt.easyxf(aml_cell_format + _xs['center'])
        self.aml_cell_style_date = xlwt.easyxf(aml_cell_format + _xs['left'], num_format_str=report_xls.date_format)
        self.aml_cell_style_decimal = xlwt.easyxf(aml_cell_format + _xs['right'], num_format_str=report_xls.decimal_format)
        # totals
        rt_cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
        self.rt_cell_style = xlwt.easyxf(rt_cell_format)
        self.rt_cell_style_right = xlwt.easyxf(rt_cell_format + _xs['right'])
        self.rt_cell_style_decimal = xlwt.easyxf(rt_cell_format + _xs['right'], num_format_str=report_xls.decimal_format)

        self.col_specs_template = {
            'id': {
                'header': [1, 10, 'text', _render("_('ID')")],
                'lines': [1, 0, 'number', _render("line.id  ")],
                'totals': [1, 0, 'text', None]},
            'invoice_number': {
                'header': [1, 15, 'text', _render("_('Invoice Number')")],
                'lines': [1, 0, 'text', _render("line.number or ''")],
                'totals': [1, 0, 'text', None]},
            'date_service': {
                'header': [1, 12, 'text', _render("_('Date Service')")],
                'lines': [1, 0, 'text', _render("line.event_id and str(line.event_id.event_start_date) or ''")],
                'totals': [1, 0, 'text', None]},
            'date_invoice': {
                'header': [1, 12, 'text', _render("_('Invoice Date')")],
                'lines': [1, 0, 'text', _render("line.date_invoice or ''")],
                'totals': [1, 0, 'text', None]},
            'event_ref': {
                'header': [1, 10, 'text', _render("_('Event No')")],
                'lines': [1, 0, 'text', _render("line.event_id and line.event_id.name or ''")],
                'totals': [1, 0, 'text', None]},
            'language': {
                'header': [1, 15, 'text', _render("_('Language')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render("line.event_id and line.event_id.language_id and line.event_id.language_id.name or '' "))],
                'totals': [1, 0, 'text', None]},
            'amount': {
                'header': [1, 10, 'text', _render("_('Amount')"), None, self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render("round(line.residual,2) or 0.0 ")],
                'totals': [1, 0, 'number', None, _render("amount_total_formula"), self.rt_cell_style_decimal]},
            'payment_received': {
                'header': [1, 10, 'text', _render("_('Payment Received')")],
                'lines': [1, 0, 'number', _render("round(line.amount_total - line.residual,2) or 0.0 ")],
                'totals': [1, 0, 'number', None, _render("payment_total_formula"), self.rt_cell_style_decimal]},
            'address': {
                'header': [1, 30, 'text', _render("_('Address')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render("line.partner_id and line.partner_id.street or '' "))],
                'totals': [1, 0, 'text', None]},
            'city': {
                'header': [1, 13, 'text', _render("_('City')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render("line.partner_id and line.partner_id.city or '' "))],
                'totals': [1, 0, 'text', None]},
            'zip': {
                'header': [1, 10, 'text', _render("_('Zip')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render("line.partner_id and line.partner_id.zip or '' "))],
                'totals': [1, 0, 'text', None]},
            'service_area': {
                'header': [1, 15, 'text', _render("_('Service Area')")],
                'lines': [1, 0, 'text', None],
                'totals': [1, 0, 'text', None]},
            'gl': {
                'header': [1, 15, 'text', _render("_('GL#')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render("line.event_id and line.event_id.cust_gpuid or '' "))],
                'totals': [1, 0, 'text', None]},
            'nud': {
                'header': [1, 15, 'text', _render("_('NUD#')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render("line.event_id and line.event_id.cust_csid or '' "))],
                'totals': [1, 0, 'text', None]},
            'approving_mgr': {
                'header': [1, 15, 'text', _render("_('Approving Mgr')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render("line.event_id and line.event_id.approving_mgr or '' "))],
                'totals': [1, 0, 'text', None]},
            'department': {
                'header': [1, 15, 'text', _render("_('Department')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render("line.event_id and line.event_id.department or '' "))],
                'totals': [1, 0, 'text', None]},
            'check': {
                'header': [1, 10, 'text', _render("_('Check#')")],
                'lines': [1, 0, 'text', None],
                'totals': [1, 0, 'text', None]},
            'check_date': {
                'header': [1, 10, 'text', _render("_('Check date')")],
                'lines': [1, 0, 'text', None],
                'totals': [1, 0, 'text', None]},
            'status': {
                'header': [1, 15, 'text', _render("_('Status')")],
                'lines': [1, 0, 'text', _render("line.state or '' ")],
                'totals': [1, 0, 'text', None]},
            'po_no': {
                'header': [1, 13, 'text', _render("_('PO#')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render("line.event_id and line.event_id.po_no or ''"))],
                'totals': [1, 0, 'text', None]},
            'contract_no': {
                'header': [1, 13, 'text', _render("_('Contract#')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render("line.ordering_partner_id and line.ordering_partner_id.contract_no or '' "))],
                'totals': [1, 0, 'text', None]},
            'iu_actions': {
                'header': [1, 42, 'text', _render("_('IU Actions')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render("line.comment or '' "))],
                'totals': [1, 0, 'text', None]},
            'event_purpose': {
                'header': [1, 13, 'text', _render("_('Event Purpose')")],
                'lines': [1, 0, 'text', _render("line.event_id and str(line.event_id.event_purpose or '') or ''")],
                'totals': [1, 0, 'text', None]},
            'department': {
                'header': [1, 15, 'text', _render("_('Department')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render("line.event_id and line.event_id.department or '' "))],
                'totals': [1, 0, 'text', None]},
            'dr_name': {
                'header': [1, 15, 'text', _render("_('Doctor Name')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render("line.event_id and line.event_id.dr_name or '' "))],
                'totals': [1, 0, 'text', None]},
            'patient_medical_number': {
                'header': [1, 13, 'text', _render("_('Patient Medical#')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render("line.event_id and line.event_id.patient_id and line.event_id.patient_id.ssnid or ''"))],
                'totals': [1, 0, 'text', None]},
        }
        
    def generate_xls_report(self, _p, _xs, data, objects, wb):
        wanted_list = _p.wanted_list
        _ = _p._
        self.wanted_list = wanted_list
        self.col_specs_template.update(_p.template_changes)
        
        amount_pos = 'amount' in wanted_list and wanted_list.index('amount')
        payment_pos = 'payment_received' in wanted_list and wanted_list.index('payment_received')
        if not (amount_pos ) and 'amount' in wanted_list:
            raise UserError(_("The 'Amount' field is a calculated XLS field requiring the presence of the 'Amount' field !"))
        report_name = "Report Sheet"
        ws = wb.add_sheet(report_name[:31])
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        row_pos = 0

        # set print header/footer
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']

        # Title
#        cell_style = xlwt.easyxf(_xs['xls_title'])
#        c_specs = [
#            ('report_name', 1, 0, 'text', 'Report for Kaiser'),
#        ]
#        row_data = self.xls_row_template(c_specs, ['report_name'])
#        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style)
#        row_pos += 1
        # Column headers
        c_specs = map(lambda x: self.render(x, self.col_specs_template, 'header', render_space={'_': _p._}), wanted_list)
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=self.rh_cell_style, set_column_size=True)
        ws.set_horz_split_pos(row_pos)
        aml_start_pos = row_pos
#        cnt = 0
        for line in objects:
#            cnt += 1
            amount_cell = rowcol_to_cell(row_pos, amount_pos)
            payment_cell = rowcol_to_cell(row_pos, payment_pos)
            c_specs = map(lambda x: self.render(x, self.col_specs_template, 'lines'), wanted_list)
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=self.aml_cell_style)
        
        amount_start = rowcol_to_cell(aml_start_pos, amount_pos)
        amount_stop = rowcol_to_cell(row_pos - 1, amount_pos)
        amount_total_formula = 'SUM(%s:%s)' % (amount_start, amount_stop)
        payment_start = rowcol_to_cell(aml_start_pos, payment_pos)
        payment_stop = rowcol_to_cell(row_pos - 1, payment_pos)
        payment_total_formula = 'SUM(%s:%s)' % (payment_start, payment_stop)
        amount_cell = rowcol_to_cell(row_pos, amount_pos)
        payment_cell = rowcol_to_cell(row_pos, payment_pos)
        c_specs = map(lambda x: self.render(x, self.col_specs_template, 'totals'), wanted_list)
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=self.rt_cell_style_right)
        return True

account_invoice_xls_kaiser('report.account.invoice.xls.print.kaiser', 'account.invoice',
    parser=account_invoice_xls_parser_kaiser)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
