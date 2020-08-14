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


class account_invoice_xls_parser_fcci_translation(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(account_invoice_xls_parser_fcci_translation, self).__init__(cr, uid, name, context=context)
        self.env = Environment(cr, uid, context)
        invoice_obj = self.env['account.invoice']
        self.context = context

        if context.get('translation', False):
            wanted_list = self._report_xls_fields_fcci_translation()
        elif context.get('transportation', False):
            wanted_list = self._report_xls_fields_fcci_transportation()
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

    def _report_xls_fields_fcci_translation(self):
        ''' List of Columns in the exported Excel with the sequence'''
        return [
            'id', 'invoice_number', 'payer', 'branch', 'date_of_service', 'claimant', 'adjuster', 'job_outcome',
            'claim_number', 'stardard', 'billed', 'saving', 'referral_state', 'description', 'langauge_service_type',
            'facility'

        ]

    def _report_xls_fields_fcci_transportation(self):
        ''' List of Columns in the exported Excel with the sequence'''
        return [
            'id', 'invoice_number', 'payer', 'branch', 'date_of_service', 'claimant', 'adjuster', 'job_outcome',
            'transport_type',
            'claim_number', 'stardard', 'billed', 'saving', 'vehicle_type', 'referral_state', 'description',
            'facility'

        ]


class account_invoice_xls_fcci_translation(report_xls):

    def parse_unicode(self, val):
        try:
            if val:
                val = val.encode('utf-8', 'ignore')
                try:
                    val = unicode(val, "ascii", 'ignore')
                except UnicodeError:
                    val = unicode(val, "utf-8", 'ignore').decode('ascii')
            else:
                val = ''
        except Exception:
            pass
        return val

    def __init__(self, name, table, rml=False, parser=False, header=True, store=False):
        super(account_invoice_xls_fcci_translation, self).__init__(name, table, rml, parser, header, store)

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
        self.aml_cell_style_decimal = xlwt.easyxf(aml_cell_format + _xs['right'],
                                                  num_format_str=report_xls.decimal_format)
        # totals
        rt_cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
        self.rt_cell_style = xlwt.easyxf(rt_cell_format)
        self.rt_cell_style_right = xlwt.easyxf(rt_cell_format + _xs['right'])
        self.rt_cell_style_decimal = xlwt.easyxf(rt_cell_format + _xs['right'],
                                                 num_format_str=report_xls.decimal_format)

        self.col_specs_template = {
            'id': {
                'header': [1, 10, 'text', _render("_('ID')")],
                'lines': [1, 0, 'number', _render("line.id  ")],
                'totals': [1, 0, 'text', None]},
            'invoice_number': {
                'header': [1, 15, 'text', _render("_('Invoice Number')")],
                'lines': [1, 0, 'text', _render("line.name or ''")],
                'totals': [1, 0, 'text', None]},
            'payer': {
                'header': [1, 12, 'text', _render("_('Payer')")],
                'lines': [1, 0, 'text', _render("line.partner_id and str(line.partner_id.name or '') or ''")],
                'totals': [1, 0, 'text', None]},
            'branch': {
                'header': [1, 12, 'text', _render("_('Branch')")],
                'lines': [1, 0, 'text', None],
                'totals': [1, 0, 'text', None]},
            'date_of_service': {
                'header': [1, 10, 'text', _render("_('Date of Service')")],
                'lines': [1, 0, 'text', None],
                'totals': [1, 0, 'text', None]},
            'claimant': {
                'header': [1, 10, 'text', _render("_('Claimant')")],
                'lines': [1, 0, 'text', _render(
                    "line.event_id and line.event_id.patient_id and str(line.event_id.patient_id.complete_name or '')  or '' ")],
                'totals': [1, 0, 'text', None]},

            'adjuster': {
                'header': [1, 15, 'text', _render("_('Adjuster')")],
                'lines': [1, 0, 'text', _render("line.event_id and line.event_id.contact_id and \
                                                str(line.event_id.contact_id.complete_name) or ''")],
                'totals': [1, 0, 'text', None]},

            'job_outcome': {
                'header': [1, 10, 'text', _render("_('Job Outcome')")],
                'lines': [1, 0, 'text', _render("line.event_id and line.event_id.event_out_come_id and \
                                                str(line.event_id.event_out_come_id.name) or ''")],
                'totals': [1, 0, 'number', None, None]},

            'transport_type': {
                'header': [1, 10, 'text', _render("_('Transport Type')")],
                'lines': [1, 0, 'text',
                          _render("line.event_id and str(line.event_id.transportation_type or '') or ''")],
                'totals': [1, 0, 'text', None, None]},

            'claim_number': {
                'header': [1, 15, 'text', _render("_('Claim Number')")],
                'lines': [1, 0, 'text', _render("line.event_id and str(line.event_id.claim_no or '') or ''")],
                'totals': [1, 0, 'text', None]},

            'stardard': {
                'header': [1, 15, 'text', _render("_('Stardard')")],
                'lines': [1, 0, 'text', None],
                'totals': [1, 0, 'text', None]},

            'billed': {
                'header': [1, 15, 'text', _render("_('Billed')")],
                'lines': [1, 0, 'text', None],
                'totals': [1, 0, 'text', None]},

            'saving': {
                'header': [1, 10, 'text', _render("_('Saving')"), None, self.rh_cell_style_right],
                'lines': [1, 0, 'text', None],
                'totals': [1, 0, 'number', None, _render("amount_total_formula"), self.rt_cell_style_decimal]},

            'vehicle_type': {
                'header': [1, 10, 'text', _render("_('Vehicle Type')")],
                'lines': [1, 0, 'text', None],
                'totals': [1, 0, 'text', None, None]},

            'referral_state': {
                'header': [1, 15, 'text', _render("_('Referral State')")],
                'lines': [1, 0, 'text', None],
                'totals': [1, 0, 'text', None]},

            'description': {
                'header': [1, 15, 'text', _render("_('Description')")],
                'lines': [1, 0, 'text', _render("str(line.comment or '') or ''")],
                'totals': [1, 0, 'text', None]},

            'langauge_service_type': {
                'header': [1, 15, 'text', _render("_('Langauge Service Type')")],
                'lines': [1, 0, 'text', _render("line.event_id and line.event_id.lang_service_type or ''")],
                'totals': [1, 0, 'text', None]},
            'facility': {
                'header': [1, 15, 'text', _render("_('Facility')")],
                'lines': [1, 0, 'text', None],
                'totals': [1, 0, 'text', None]},

        }

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        # print "generate_xls_report......data......",data,objects , wb
        wanted_list = _p.wanted_list
        # print "_p._......",_p._
        _ = _p._

        self.wanted_list = wanted_list
        self.col_specs_template.update(_p.template_changes)

        amount_pos = 'amount' in wanted_list and wanted_list.index('amount')
        payment_pos = 'payment_received' in wanted_list and wanted_list.index('payment_received')
        if not (amount_pos) and 'amount' in wanted_list:
            raise UserError(
                _("The 'Amount' field is a calculated XLS field requiring the presence of the 'Amount' field !"))
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
        c_specs = map(lambda x: self.render(x, self.col_specs_template, 'header', render_space={'_': _p._}),
                      wanted_list)
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
        #        payment_total_formula = 'SUM(%s:%s)' % (payment_start, payment_stop)
        amount_cell = rowcol_to_cell(row_pos, amount_pos)
        payment_cell = rowcol_to_cell(row_pos, payment_pos)
        c_specs = map(lambda x: self.render(x, self.col_specs_template, 'totals'), wanted_list)
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=self.rt_cell_style_right)
        return True


account_invoice_xls_fcci_translation('report.account.invoice.xls.print.fcci_translation', 'account.invoice',
                                     parser=account_invoice_xls_parser_fcci_translation)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


