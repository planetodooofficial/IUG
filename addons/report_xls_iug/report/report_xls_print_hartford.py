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

class account_invoice_line_xls_parser_hartford(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(account_invoice_line_xls_parser_hartford, self).__init__(cr, uid, name, context=context)
        self.env = Environment(cr, uid, context)
        invoice_line_obj = self.env['account.invoice.line']
        self.context = context
        wanted_list = self._report_xls_fields_hartford()
        template_changes = invoice_line_obj._report_xls_template_cobb()
        space_extra = invoice_line_obj._report_xls_render_space_extra_cobb()
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

    

    def _report_xls_fields_hartford(self):
        ''' List of Columns in the exported Excel with the sequence'''
        return [
            'vendor','claim_number','segment','claim_office','requestor_name','claim_handler_name','claim_name',
            'state','date_of_loss','service_type','service_language','language_interpretation_type','urgent_or_nonurgent','referral_date',
            'referral_time','telephonic_confirmation_date','email_confirm_date','claim_contact_date','claim_reconfirm_date','no_show','cancellation','cancellation_reason',
            'date_of_cancellation','cancellation_notice','date_summary_report_sent','date_of_service','invoice_number','invoice_date','invoice_submission_date',
            'invoice_amount','cancellation_fee','mileage'
        ]


class account_invoice_line_xls_hartford(report_xls):
    
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
        super(account_invoice_line_xls_hartford, self).__init__(name, table, rml, parser, header, store)

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

        self.col_specs_template_hartford = {
            'vendor': {
                'header': [1, 10, 'text', _render("_('Vendor')")],
                'lines': [1, 0, 'text', _render("line.invoice_id.partner_id and str(line.invoice_id.partner_id.complete_name or '') or ''")],
                'totals': [1, 0, 'text', None]},
            'claim_number': {
                'header': [1, 10, 'text', _render("_('Claim Number')")],
                'lines': [1, 0, 'text', _render("line.invoice_id.event_id and str(line.invoice_id.event_id.claim_no or '') or ''")],
                'totals': [1, 0, 'text', None]},
            'segment': {
                'header': [1, 13, 'text', _render("_('Segment')")],
                'lines': [1, 0, 'text', None],
                'totals': [1, 0, 'text', None]},
            'claim_office': {
                'header': [1, 20, 'text', _render("_('Claim Office')")],
                'lines': [1, 0, 'text', None],
                'totals': [1, 0, 'text', None]},
            'requestor_name': {
                'header': [1, 20, 'text', _render("_('Requestor Name')")],
                'lines': [1, 0, 'text',_render("line.invoice_id.event_id and line.invoice_id.event_id.ordering_partner_id and \
                                            str(line.invoice_id.event_id.ordering_partner_id.complete_name or '') or ''")],
                'totals': [1, 0, 'text', None]},
            'claim_handler_name': {
                'header': [1, 13, 'text', _render("_('Claim Handler Name')")],
                'lines': [1, 0, 'text', None],
                'totals': [1, 0, 'text', None]},
            'claim_name': {
                'header': [1, 15, 'text', _render("_('Claim Name')")],
                'lines': [1, 0, 'text', None],
                'totals': [1, 0, 'text', None]},
            'state': {
                'header': [1, 20, 'text', _render("_('State')")],
                'lines': [1, 0, 'text', _render("line.invoice_id.event_id and line.invoice_id.event_id.location_id and str(line.invoice_id.event_id.location_id.name or '') or ''")],
                'totals': [1, 0, 'text', None]},
            'date_of_loss': {
                'header': [1, 20, 'text', _render("_('Date Of Loss')")],
                'lines': [1, 0, 'text', None],
                'totals': [1, 0, 'text', None]},
            'service_type': {
                'header': [1, 13, 'text', _render("_('Service Type')")],
                'lines': [1, 0, 'text',  _render("line.invoice_id.event_id and line.invoice_id.event_id.event_type or ''")],
                'totals': [1, 0, 'text', None]},
            'service_language': {
                'header': [1, 20, 'text', _render("_('Service Language')")],
                'lines': [1, 0, 'text', _render("line.invoice_id.language_id and str(line.invoice_id.language_id.name or '') or ''")],
                'totals': [1, 0, 'text', None]},
            'language_interpretation_type': {
                'header': [1, 13, 'text', _render("_('Language Interpretation Type')")],
                'lines': [1, 0, 'text', _render("line.invoice_id.event_id and line.invoice_id.event_id.lang_service_type or ''")],
                'totals': [1, 0, 'text', None]},
            'urgent_or_nonurgent': {
                'header': [1, 30, 'text', _render("_('Urgent or Nonurgent')")],
                'lines': [1, 0, 'text', None],
                'totals': [1, 0, 'text', None]},
            'referral_date': {
                'header': [1, 13, 'text', _render("_('Referral Date')")],
                'lines': [1, 0, 'text', _render("line.invoice_id.event_id and str(line.invoice_id.event_id.event_start_date) or ''")],
                'totals': [1, 0, 'text', None]},
            'referral_time': {
                'header': [1, 10, 'text', _render("_('Referral Time')")],
                'lines': [1, 0, 'text', _render("line.invoice_id.event_id and str(line.invoice_id.event_id.event_start_hr or '') + ':' + str(line.invoice_id.event_id.event_start_min or '') + ' ' + str(line.invoice_id.event_id.am_pm or '') or '' ")],
                'totals': [1, 0, 'text', None]},
            'telephonic_confirmation_date': {
                'header': [1, 25, 'text', _render("_('Telephonic Confirmation Date')")],
                'lines': [1, 0, 'text',None],
                'totals': [1, 0, 'text', None]},
            'email_confirm_date': {
                'header': [1, 10, 'text', _render("_('Email Confirm Date')")],
                'lines': [1, 0, 'text', None],
                'totals': [1, 0, 'text', None]},
            'claim_contact_date': {
                'header': [1, 10, 'text', _render("_('Claim Contact Date')")],
                'lines': [1, 0, 'text', None],
                'totals': [1, 0, 'text', None]},
            'claim_reconfirm_date': {
                'header': [1, 10, 'text', _render("_('Claim Reconfirm Date')")],
                'lines': [1, 0,'text', None],
                'totals': [1, 0, 'text', None]},
            'claim_contact_date': {
                'header': [1, 10, 'text', _render("_('Claim Contact Date')")],
                'lines': [1, 0,'text', None],
                'totals': [1, 0, 'text', None]},
            'claim_reconfirm_date': {
                'header': [1, 10, 'text', _render("_('Claim Reconfirm Date')")],
                'lines': [1, 0,'text', None],
                'totals': [1, 0, 'text', None]},
            'no_show': {
                'header': [1, 13, 'text', _render("_('No Show')")],
                'lines': [1, 0, 'text', None], 
                'totals': [1, 0, 'text', None]},
            #datetime.strptime(datetime.strptime(dt_from,"%Y-%m-%d").strftime('%Y-%m-%d %H:%M:%S'), "%Y-%m-%d %H:%M:%S")
            'cancellation': {
                'header': [1, 13, 'text', _render("_('Cancellation')")],
                'lines': [1, 0, 'text', None],
                'totals': [1, 0, 'text', None]},
            'cancellation_reason': {
                'header': [1, 15, 'text', _render("_('Cancellation Reason')")],
                'lines': [1, 0, 'text', _render("line.invoice_id and line.invoice_id.event_id and str(line.invoice_id.event_id.cancel_reason_id.name or '') or ''")],
                'totals': [1, 0, 'text', None]},
            'date_of_cancellation': {
                'header': [1, 10, 'text', _render("_('Date Of Cancellation')")],
                'lines': [1, 0, 'text', None],
                'totals': [1, 0, 'text', None]},
            'cancellation_notice': {
                'header': [1, 13, 'text', _render("_('Cancellation Notice')")],
                'lines': [1, 0, 'text', None],
                'totals': [1, 0, 'text', None]},

            'date_summary_report_sent': {
                'header': [1, 10, 'text', _render("_('Date Summary Report Sent')")],
                'lines': [1, 0, 'text', None],
                'totals': [1, 0, 'text', None]},
            'date_of_service': {
                'header': [1, 10, 'text', _render("_('Date Of Service')"), None, self.rh_cell_style_right],
                'lines': [1, 0,'text', None],
                'totals': [1, 0, 'text', None]},
            'invoice_number': {
                'header': [1, 40, 'text', _render("_('Invoice Number')")],
                'lines': [1, 0, 'text',  _render("line.invoice_id and str(line.invoice_id.name or '')  or ''")],
                'totals': [1, 0, 'text', None]},
            'invoice_date': {
                'header': [1, 40, 'text', _render("_('Invoice Date')")],
                'lines': [1, 0, 'text', _render("line.invoice_id and str(line.invoice_id.date_invoice or '') or ''")],
                'totals': [1, 0, 'text', None]},
            'invoice_submission_date': {
                'header': [1, 40, 'text', _render("_('Invoice Submission Date')")],
                'lines': [1, 0, 'text', None],
                'totals': [1, 0, 'text', None]},
            'invoice_amount': {
                'header': [1, 40, 'text', _render("_('Invoice Amount')")],
                'lines': [1, 0, 'number', _render("line.price_subtotal  or ''")],
                'totals': [1, 0, 'text', None]},
            'cancellation_fee': {
                'header': [1, 40, 'text', _render("_('Cancellation Fee')")],
                'lines': [1, 0, 'number', None],
                'totals': [1, 0, 'text', None]},
            'mileage': {
                'header': [1, 40, 'text', _render("_('Mileage')")],
                'lines': [1, 0, 'number', _render("line.mileage  or 0.0")],
                'totals': [1, 0, 'text', None]},
        }

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        wanted_list = _p.wanted_list
        
        _ = _p._
        self.wanted_list = wanted_list
        self.col_specs_template_hartford.update(_p.template_changes)

        amount_pos = 'amount' in wanted_list and wanted_list.index('amount')
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
        c_specs = map(lambda x: self.render(x, self.col_specs_template_hartford, 'header', render_space={'_': _p._}), wanted_list)
        
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
#        row_data = []
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=self.rh_cell_style, set_column_size=True)
        ws.set_horz_split_pos(row_pos)
        aml_start_pos = row_pos
#        cnt = 0
        for line in objects:
#            cnt += 1
            amount_cell = rowcol_to_cell(row_pos, amount_pos)
            c_specs = map(lambda x: self.render(x, self.col_specs_template_hartford, 'lines'), wanted_list)
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=self.aml_cell_style)

        amount_start = rowcol_to_cell(aml_start_pos, amount_pos)
        amount_stop = rowcol_to_cell(row_pos - 1, amount_pos)
        amount_total_formula = 'SUM(%s:%s)' % (amount_start, amount_stop)

        amount_cell = rowcol_to_cell(row_pos, amount_pos)
        c_specs = map(lambda x: self.render(x, self.col_specs_template_hartford, 'totals'), wanted_list)
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=self.rt_cell_style_right)
        return True

account_invoice_line_xls_hartford('report.account.invoice.line.xls.print.hartford', 'account.invoice.line',
    parser=account_invoice_line_xls_parser_hartford)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
