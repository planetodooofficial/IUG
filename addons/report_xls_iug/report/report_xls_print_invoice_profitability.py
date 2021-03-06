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
from odoo.api import Environment
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError, RedirectWarning, ValidationError

_ir_translation_name = 'move.line.list.xls'


class account_invoice_xls_parser_invoice_profitability(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(account_invoice_xls_parser_invoice_profitability, self).__init__(cr, uid, name, context=context)
        self.env = Environment(cr, uid, context)
        inv_line_obj = self.env['account.invoice.line']
        self.context = context
        wanted_list = inv_line_obj._report_xls_fields_invoice_profitability()
        template_changes = inv_line_obj._report_xls_template_invoice_profitability()
        space_extra = inv_line_obj._report_xls_render_space_extra_invoice_profitability()
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


class account_invoice_xls_invoice_profitability(report_xls):

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
        super(account_invoice_xls_invoice_profitability, self).__init__(name, table, rml, parser, header, store)
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

        self.col_specs_template_invoice_profitability = {
            'id': {
                'header': [1, 10, 'text', _render("_('ID')")],
                'lines': [1, 0, 'number', _render("each_line.invoice_id.id ")],
                'totals': [1, 0, 'text', None]},
            'date_service': {
                'header': [1, 10, 'text', _render("_('Date Service')")],
                'lines': [1, 0, 'text', _render(
                    "each_line.invoice_id.event_id and str(each_line.invoice_id.event_id.event_start_date) or '' ")],
                'totals': [1, 0, 'text', None]},
            'language': {
                'header': [1, 13, 'text', _render("_('Language')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render(
                    "each_line.invoice_id.event_id and each_line.invoice_id.event_id.language_id and each_line.invoice_id.event_id.language_id.name or '' "))],
                'totals': [1, 0, 'text', None]},
            'interpretation_type': {
                'header': [1, 20, 'text', _render("_('Interpretation Type')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render(
                    "each_line.invoice_id.event_id and each_line.invoice_id.event_id.appointment_type_id and each_line.invoice_id.event_id.appointment_type_id.name or '' "))],
                'totals': [1, 0, 'text', None]},
            'interpreter': {
                'header': [1, 20, 'text', _render("_('Interpreter Name')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render(
                    "each_line.task_line_id and each_line.task_line_id.interpreter_id and each_line.task_line_id.interpreter_id.complete_name or '' "))],
                'totals': [1, 0, 'text', None]},
            'interpretation_city': {
                'header': [1, 13, 'text', _render("_('Interpretation City')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render(
                    "each_line.invoice_id.event_id and each_line.invoice_id.event_id.location_id and each_line.invoice_id.event_id.location_id.city or '' "))],
                'totals': [1, 0, 'text', None]},
           'interpretation_state': {
                'header': [1, 13, 'text', _render("_('Interpretation state')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render(
                    "each_line.invoice_id.event_id and each_line.invoice_id.event_id.location_id and each_line.invoice_id.event_id.location_id.state_id.name or '' "))],
                'totals': [1, 0, 'text', None]},
            'patient_name': {
                'header': [1, 15, 'text', _render("_('Patient Name')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render(
                    "each_line.invoice_id.event_id and each_line.invoice_id.event_id.patient_id and each_line.invoice_id.event_id.patient_id.complete_name or '' "))],
                'totals': [1, 0, 'text', None]},
            'requester': {
                'header': [1, 20, 'text', _render("_('Requester')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render(
                    "each_line.invoice_id.event_id and each_line.invoice_id.event_id.ordering_partner_id and each_line.invoice_id.event_id.ordering_partner_id.complete_name or '' "))],
                'totals': [1, 0, 'text', None]},
            'ordering_contact': {
                'header': [1, 20, 'text', _render("_('Ordering Contact')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render(
                    "each_line.invoice_id.event_id and each_line.invoice_id.event_id.ordering_contact_id and each_line.invoice_id.event_id.ordering_contact_id.complete_name or '' "))],
                'totals': [1, 0, 'text', None]},
            'ordering_contact_phone': {
                'header': [1, 20, 'text', _render("_('Phone No')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render(
                    "each_line.invoice_id.event_id and each_line.invoice_id.event_id.ordering_contact_id and each_line.invoice_id.event_id.ordering_contact_id.phone or each_line.invoice_id.event_id.ordering_contact_id.phone2 or '' "))],
                'totals': [1, 0, 'text', None]},
            'billing_customer': {
                'header': [1, 20, 'text', _render("_('Billing Customer')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render(
                    "each_line.invoice_id.event_id and each_line.invoice_id.event_id.partner_id and each_line.invoice_id.event_id.partner_id.complete_name or '' "))],
                'totals': [1, 0, 'text', None]},
            'billing_customer_ref': {
                'header': [1, 13, 'text', _render("_('Billing Customer Ref')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render(
                    "each_line.invoice_id.event_id and each_line.invoice_id.event_id.partner_id and each_line.invoice_id.event_id.partner_id.ref or '' "))],
                'totals': [1, 0, 'text', None]},
            'billing_contact': {
                'header': [1, 20, 'text', _render("_('Billing Contact')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render(
                    "each_line.invoice_id.event_id and each_line.invoice_id.event_id.contact_id and each_line.invoice_id.event_id.contact_id.complete_name or '' "))],
                'totals': [1, 0, 'text', None]},
            'billing_contact_ref': {
                'header': [1, 13, 'text', _render("_('Billing Contact Ref')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render(
                    "each_line.invoice_id.event_id and each_line.invoice_id.event_id.contact_id and each_line.invoice_id.event_id.contact_id.ref or ''"))],
                'totals': [1, 0, 'text', None]},
            #            'address': {
            #                'header': [1, 30, 'text', _render("_('Address')")],
            #                'lines': [1, 0, 'text', self.parse_address('',_render("line.invoice_id.partner_id.street or '' "),_render("line.invoice_id.partner_id.street2 or '' "))],
            #                'totals': [1, 0, 'text', None]},
            'address': {
                'header': [1, 30, 'text', _render("_('Address')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render("each_line.invoice_id.partner_id.street or '' "))],
                'totals': [1, 0, 'text', None]},
            'city': {
                'header': [1, 13, 'text', _render("_('City')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render("each_line.invoice_id.partner_id.city or '' "))],
                'totals': [1, 0, 'text', None]},
            'zip': {
                'header': [1, 10, 'text', _render("_('Zip')")],
                'lines': [1, 0, 'text', _render("each_line.invoice_id.partner_id.zip or '' ")],
                'totals': [1, 0, 'text', None]},
            'location': {
                'header': [1, 25, 'text', _render("_('Location Services Provided')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render(
                    "each_line.invoice_id.event_id and each_line.invoice_id.event_id.location_id and each_line.invoice_id.event_id.location_id.name or '' "))],
                #                                                _render("line.invoice_id.event_id and line.invoice_id.event_id.location_id and line.invoice_id.event_id.location_id.street or '' "),\
                #                                                _render("line.invoice_id.event_id and line.invoice_id.event_id.location_id and line.invoice_id.event_id.location_id.street2 or '' "))],
                'totals': [1, 0, 'text', None]},
            'street': {
                'header': [1, 25, 'text', _render("_('Street')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render(
                    "each_line.invoice_id.event_id and each_line.invoice_id.event_id.location_id and each_line.invoice_id.event_id.location_id.street or '' "))],
                'totals': [1, 0, 'text', None]},
            'street2': {
                'header': [1, 25, 'text', _render("_('Street2')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render(
                    "each_line.invoice_id.event_id and each_line.invoice_id.event_id.location_id and each_line.invoice_id.event_id.location_id.street2 or '' "))],
                'totals': [1, 0, 'text', None]},
            'start_time': {
                'header': [1, 10, 'text', _render("_('Start Time')")],
                'lines': [1, 0, 'text', _render("each_line.task_line_id and str(each_line.task_line_id.event_start_hr or '') + ':' + str(each_line.task_line_id.event_start_min or '') + ' ' + \
                                        str(each_line.task_line_id.am_pm or '') or '' #")],
                'totals': [1, 0, 'text', None]},

            'end_time': {
                'header': [1, 10, 'text', _render("_('End Time')")],
                'lines': [1, 0, 'text', _render("each_line.task_line_id and str(each_line.task_line_id.event_end_hr or '') + ':' + str(each_line.task_line_id.event_end_min or '') + ' ' + \
                                        str(each_line.task_line_id.am_pm2 or '') or '' #")],
                'totals': [1, 0, 'text', None]},
            'duration': {
                'header': [1, 10, 'text', _render("_('Duration')")],
                'lines': [1, 0, 'text', _render("each_line.task_line_id and each_line.task_line_id.time_spent and str(round(each_line.task_line_id.time_spent,2) or '')or ''")],
                'totals': [1, 0, 'text', None]},
            'rate': {
                'header': [1, 10, 'text', _render("_('Interpreter Rate')")],
                # 'lines': [1, 0, 'number', _render("line.price_unit and round(line.price_unit,2) or 0.0 ")],
                'lines': [1, 0, 'number', _render("rec_supplier_inv and round(rec_supplier_inv) or 0 ")],
                'totals': [1, 0, 'text', None]},
            'miles_driven': {
                'header': [1, 10, 'text', _render("_('Miles Driven')")],
                'lines': [1, 0, 'number', _render("each_line.miles_driven and round(each_line.miles_driven,2)or 0.0 ")],
                'totals': [1, 0, 'text', None]},
            'total_miles_rate': {
                'header': [1, 13, 'text', _render("_('Total Miles Rate')")],
                #'lines': [1, 0, 'number', _render("round(each_line.mileage * each_line.mileage_rate,2)  or 0.0 ")],
                'lines': [1, 0, 'number', _render("rec_supplier_mileage * rec_supplier_mileage_rate or 0.0 ")],
                'totals': [1, 0, 'text', None]},
            # datetime.strptime(datetime.strptime(dt_from,"%Y-%m-%d").strftime('%Y-%m-%d %H:%M:%S'), "%Y-%m-%d %H:%M:%S")
            'invoice_number': {
                'header': [1, 13, 'text', _render("_('Invoice Number')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render("str(each_line.invoice_id.number) or ''"))],
                'totals': [1, 0, 'text', None]},
            'office': {
                'header': [1, 15, 'text', _render("_('Office')")],
                'lines': [1, 0, 'text', None],
                'totals': [1, 0, 'text', None]},
            'interpreter_gender': {
                'header': [1, 10, 'text', _render("_('Intp Gender')")],
                'lines': [1, 0, 'text', _render("each_line.invoice_id.event_id and each_line.invoice_id.event_id.interpreter_id and \
                                        str(each_line.invoice_id.event_id.interpreter_id.gender) or ''")],
                'totals': [1, 0, 'text', None]},
            'po_no': {
                'header': [1, 13, 'text', _render("_('PO#')")],
                'lines': [1, 0, 'text', _render("each_line.invoice_id.event_id and each_line.invoice_id.event_id.po_no or ''")],
                'totals': [1, 0, 'text', None]},
            'medical_number': {
                'header': [1, 13, 'text', _render("_('Medical#')")],
                'lines': [1, 0, 'text', self.parse_unicode(
                    _render("each_line.invoice_id.event_id and each_line.invoice_id.event_id.medical_no or ''"))],
                'totals': [1, 0, 'text', None]},
            'contract_no': {
                'header': [1, 13, 'text', _render("_('Contract#')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render(
                    "each_line.invoice_id.ordering_partner_id and each_line.invoice_id.ordering_partner_id.contract_no or ''"))],
                'totals': [1, 0, 'text', None]},
            'date_invoice': {
                'header': [1, 10, 'text', _render("_('Invoice Date')")],
                'lines': [1, 0, 'text', _render("str(each_line.invoice_id.date_invoice or '') or ''")],
                'totals': [1, 0, 'text', None]},
            'amount': {
                'header': [1, 10, 'text', _render("_('Amount')"), None, self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render("each_line.price_subtotal and round(each_line.price_subtotal,2) or 0.0 ")],
                'totals': [1, 0, 'number', None, _render("amount_total_formula"), self.rt_cell_style_decimal]},
            'comment': {
                'header': [1, 40, 'text', _render("_('Comment')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render("each_line.invoice_id.comment or ''"))],
                'totals': [1, 0, 'text', None]},
            'event_purpose': {
                'header': [1, 13, 'text', _render("_('Event Purpose')")],
                'lines': [1, 0, 'text', _render(
                    "each_line.invoice_id.event_id and str(each_line.invoice_id.event_id.event_purpose or '') or ''")],
                'totals': [1, 0, 'text', None]},
            'cost_center': {
                'header': [1, 40, 'text', _render("_('Cost Center')")],
                'lines': [1, 0, 'text', self.parse_unicode(
                    _render("each_line.invoice_id.event_id and each_line.invoice_id.event_id.cost_center or ''"))],
                'totals': [1, 0, 'text', None]},
            'status': {
                'header': [1, 15, 'text', _render("_('Status')")],
                'lines': [1, 0, 'text', _render("each_line.invoice_id.state or '' ")],
                'totals': [1, 0, 'text', None]},
            'department': {
                'header': [1, 15, 'text', _render("_('Department')")],
                'lines': [1, 0, 'text', self.parse_unicode(
                    _render("each_line.invoice_id.event_id and each_line.invoice_id.event_id.department or '' "))],
                'totals': [1, 0, 'text', None]},
            'dr_name': {
                'header': [1, 15, 'text', _render("_('Doctor Name')")],
                'lines': [1, 0, 'text', self.parse_unicode(
                    _render("each_line.invoice_id.event_id and each_line.invoice_id.event_id.dr_name or '' "))],
                'totals': [1, 0, 'text', None]},
            'patient_medical_number': {
                'header': [1, 13, 'text', _render("_('Patient Medical#')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render(
                    "each_line.invoice_id.event_id and each_line.invoice_id.event_id.patient_id and each_line.invoice_id.event_id.patient_id.ssnid or ''"))],
                'totals': [1, 0, 'text', None]},
            'amount_total': {
                'header': [1, 16, 'text', _render("_('Total Vendor Pay')")],
                'lines': [1, 0, 'number', self.parse_unicode(_render("rec_supplier_total or 0.0 "))],
                'totals': [1, 0, 'text', None]},
            'sales_representative_id': {
                'header': [1, 13, 'text', _render("_('Sales Rep')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render(
                    "each_line.invoice_id.event_id and each_line.invoice_id.event_id.sales_representative_id and each_line.invoice_id.event_id.sales_representative_id.name or ''"))],
                'totals': [1, 0, 'text', None]},
            'sales_representative_id_for_billing_customer': {
                'header': [1, 13, 'text', _render("_('Sales Rep By Cust')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render(
                    "each_line.invoice_id.event_id and each_line.invoice_id.event_id.partner_id and each_line.invoice_id.event_id.partner_id.sales_representative_id and each_line.invoice_id.event_id.partner_id.sales_representative_id.name or ''"))],
                'totals': [1, 0, 'text', None]},
            'requester_create_date': {
                'header': [1, 20, 'text', _render("_('Requester Create Date')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render(
                    "datetime.strptime(each_line.invoice_id.event_id.ordering_partner_id.create_date,'%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y') if  each_line.invoice_id.event_id and each_line.invoice_id.event_id.ordering_partner_id and each_line.invoice_id.event_id.ordering_partner_id.create_date !='False' else ''"))],
                'totals': [1, 0, 'text', None]},
            'metazone': {
                'header': [1, 20, 'text', _render("_('Metazone')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render(
                    "each_line.invoice_id.event_id and each_line.invoice_id.event_id.zone_id and each_line.invoice_id.event_id.zone_id.name or ''"))],
                'totals': [1, 0, 'text', None]},
            'scheduler': {
                'header': [1, 20, 'text', _render("_('Scheduler')")],
                'lines': [1, 0, 'text', self.parse_unicode(_render(
                    "each_line.invoice_id.event_id and each_line.invoice_id.event_id.scheduler_id and each_line.invoice_id.event_id.scheduler_id.name or ''"))],
                'totals': [1, 0, 'text', None]},

        }

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        # print "generate_xls_report......data......",data,objects , wb
        wanted_list = _p.wanted_list
        # print "_p._......",_p._
        _ = _p._
        self.wanted_list = wanted_list
        self.col_specs_template_invoice_profitability.update(_p.template_changes)

        amount_pos = 'amount' in wanted_list and wanted_list.index('amount')
        if not (amount_pos) and 'amount' in wanted_list:
            raise UserError(_( "The 'Amount' field is a calculated XLS field requiring the presence of the 'Amount' field !"))
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
        c_specs = map(lambda x: self.render(x, self.col_specs_template_invoice_profitability, 'header', render_space={'_': _p._}),
                      wanted_list)
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=self.rh_cell_style, set_column_size=True)
        ws.set_horz_split_pos(row_pos)
        aml_start_pos = row_pos
        #        cnt = 0
        for each_line in objects:
            invoice_obj_srch = self.env['account.invoice'].search([('type', '=', 'in_invoice'),
                                                                                           ('event_id', '=',
                                                                                            each_line.invoice_id.event_id.id)])
            for each_supp_rec in invoice_obj_srch:
                rec_supplier_inv =each_supp_rec.invoice_line_ids and each_supp_rec.invoice_line_ids[0].price_unit or 0.0
                rec_supplier_total = each_supp_rec.amount_total
                rec_supplier_mileage = each_supp_rec.invoice_line_ids and each_supp_rec.invoice_line_ids[0].mileage or 0.0
                rec_supplier_mileage_rate = each_supp_rec.invoice_line_ids and each_supp_rec.invoice_line_ids[0].mileage_rate or 0.0
            #            cnt += 1
            amount_cell = rowcol_to_cell(row_pos, amount_pos)
            c_specs = map(lambda x: self.render(x, self.col_specs_template_invoice_profitability, 'lines'), wanted_list)
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=self.aml_cell_style)

        amount_start = rowcol_to_cell(aml_start_pos, amount_pos)
        amount_stop = rowcol_to_cell(row_pos - 1, amount_pos)
        amount_total_formula = 'SUM(%s:%s)' % (amount_start, amount_stop)

        # Actual data comes here
        amount_cell = rowcol_to_cell(row_pos, amount_pos)
        c_specs = map(lambda x: self.render(x, self.col_specs_template_invoice_profitability, 'totals'), wanted_list)
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=self.rt_cell_style_right)
        return True


account_invoice_xls_invoice_profitability('report.account.invoice.xls.print.invoice.profitability', 'account.invoice.line',
    parser=account_invoice_xls_parser_invoice_profitability)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
