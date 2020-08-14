from odoo import api, fields, models,osv, _
from odoo.tools.translate import _
from odoo import SUPERUSER_ID
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import time
from . import format_common
import cStringIO
import base64
import xlwt
from odoo.exceptions import UserError

class contact_lines(models.Model):
    _name = 'contact.lines'

    contact_id = fields.Many2one('contact.list.dashboard', 'Contact ')
    interp_contact_id = fields.Many2one('interp.contact.list.dashboard', 'Contact ')
    event_id = fields.Char('Event Id')
    cust_inv_amt = fields.Float('Customer Invoice Amount')
    interp_inv_amt = fields.Float('Interpreter Invoice Amount')
    ref = fields.Char('Reference')
    complete_name = fields.Char('Contact Name')
    event_create_date = fields.Char('Event Date')
    actives = fields.Char('Active')
    type = fields.Char('Type')
    company_id = fields.Many2one('res.company', 'Company')
    title = fields.Char('Title')
    gender = fields.Char('Gender')
    contract_no = fields.Char('Contract No')
    related_company_id = fields.Many2one('res.partner', 'Related Company')
    interpreter = fields.Many2one('res.partner', 'Event Interpreter')
    language = fields.Many2one('language', 'Event Language')
    function = fields.Char('Job Position')
    department = fields.Char('Department')
    sales_representative_id = fields.Many2one('res.users', 'Event Sales Representative')
    phone = fields.Char('Phone')
    phone2 = fields.Char('Phone2')
    email = fields.Char('Email')
    fax = fields.Char('Fax')

class contact_list_dashboard(models.Model):
    _name = 'contact.list.dashboard'

    name = fields.Char('Ordering Contacts Report-Customer',default='Ordering Contacts Report Based on Customer')
    from_date = fields.Date('From Date',default=lambda *a: time.strftime('%Y-%m-01'))
    to_date = fields.Date('To Date',default=lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
    company_id = fields.Many2one('res.company', 'Company')
    contact = fields.Many2one('res.partner', 'Contact')
    customer = fields.Many2one('res.partner', 'Customer Name')
    contact_line_ids = fields.One2many('contact.lines', 'contact_id', 'Contact Lines')

    @api.multi
    def search_contacts(self):
        cur_obj = self
        contact_line = cur_obj.contact_line_ids
        self.env['contact.lines'].unlink(contact_line)

        from_date = "'" + cur_obj.from_date + "'"
        to_date = "'"+cur_obj.to_date+"'"
        company_id = cur_obj.company_id.id
        query = """
                SELECT res_partner.name,event.name AS event_id,event.language_id AS language,res_partner.ref,
                res_partner.complete_name,res_partner.active,res_partner.cust_type,res_partner.title,res_partner.gender,
                res_partner.contract_no,res_partner.function,res_partner.department,res_partner.phone,res_partner.phone2,
                res_partner.email,res_partner.fax,event.sales_representative_id,account_invoice.amount_total,
                res_partner.parent_id AS related_company,res_partner.company_id AS company_id,
                event_partner_rel.interpreter_id AS interpreter,event.event_date,account_invoice.type
                FROM res_partner
                LEFT JOIN event ON event.ordering_contact_id = res_partner.id
                LEFT JOIN event_partner_rel ON event_partner_rel.event_id = event.id
                LEFT JOIN account_invoice ON account_invoice.id = event.cust_invoice_id
                WHERE res_partner.company_id = %s and event.event_start_date BETWEEN %s AND %s""" \
                % (str(company_id), from_date, to_date)

        where = ""

        if cur_obj.contact and cur_obj.contact != False:
            where += " and res_partner.id = "+str(cur_obj.contact.id)
        if cur_obj.customer and cur_obj.customer != False:
            where += " and account_invoice.partner_id = "+str(cur_obj.customer.id)

        self._cr.execute(query+where+";")
        data = self._cr.fetchall()
        if not data:
            raise UserError(_('No data available for selected filters'))
        else:
            for res in data:
                if res[5] == True:
                    active = 'True'
                else:
                    active = 'False'
                self.write({'contact_line_ids': [(0, False, {'complete_name': res[4], 'title':res[7],
                    'type': res[6], 'company_id':res[19], 'event_id':res[1], 'event_create_date':res[21],
                    'interpreter':res[20], 'language':res[2], 'cust_inv_amt':res[17],
                    'sales_representative_id':res[16], 'ref':res[3], 'related_company_id':res[18], 'gender':res[8],
                    'phone':res[12], 'phone2':res[13], 'email':res[14], 'fax':res[15], 'contract_no':res[9],
                    'function':res[10], 'department':res[11], 'actives':active})]})
        return True

    @api.multi
    def print_xls_report(self):
        self.search_contacts()
        cur_obj = self

        header_tstyle_c = format_common.font_style(position='center', bold=1, border=1, fontos='black', font_height=150, color='grey')
        other_tstyle_c = format_common.font_style(position='center', fontos='black', font_height=200)
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('Ordering Contact List')
        sheet.row(0).height = 256 * 3
        sheet.normal_magn = 120
        sheet.write_merge(0, 0, 0, 4, 'Report for : Ordering Contact List  Customerwise (' + cur_obj.company_id.name + ')', header_tstyle_c)

        row = 5
        sheet.write(row, 0, 'Name', header_tstyle_c)
        sheet.write(row, 1, 'Title', header_tstyle_c)
        sheet.write(row, 2, 'Type', header_tstyle_c)
        sheet.write(row, 3, 'Company', header_tstyle_c)
        sheet.write(row, 4, 'Event Id', header_tstyle_c)
        sheet.write(row, 5, 'Event Date', header_tstyle_c)
        sheet.write(row, 6, 'Event Interpreter', header_tstyle_c)
        sheet.write(row, 7, 'Event Language', header_tstyle_c)
        sheet.write(row, 8, 'Customer Invoice Amount', header_tstyle_c)
        sheet.write(row, 9, 'Event Sales Representative', header_tstyle_c)
        sheet.write(row, 10, 'Reference', header_tstyle_c)
        sheet.write(row, 11, 'Related Company', header_tstyle_c)
        sheet.write(row, 12, 'Gender', header_tstyle_c)
        sheet.write(row, 13, 'Phone', header_tstyle_c)
        sheet.write(row, 14, 'Phone2', header_tstyle_c)
        sheet.write(row, 15, 'Email', header_tstyle_c)
        sheet.write(row, 16, 'Fax', header_tstyle_c)
        sheet.write(row, 17, 'Contract No', header_tstyle_c)
        sheet.write(row, 18, 'Job Position', header_tstyle_c)
        sheet.write(row, 19, 'Department', header_tstyle_c)
        sheet.write(row, 20, 'Active', header_tstyle_c)

        row = 6
        for data in cur_obj.contact_line_ids:
            sheet.write(row, 0, data.complete_name or None, other_tstyle_c)
            sheet.write(row, 1, data.title or None, other_tstyle_c)
            sheet.write(row, 2, data.type or None, other_tstyle_c)
            sheet.write(row, 3, data.company_id.name or None, other_tstyle_c)
            sheet.write(row, 4, data.event_id or None, other_tstyle_c)
            sheet.write(row, 5, data.event_create_date or None, other_tstyle_c)
            sheet.write(row, 6, data.interpreter.name or None, other_tstyle_c)
            sheet.write(row, 7, data.language.name or None, other_tstyle_c)
            sheet.write(row, 8, data.cust_inv_amt or None, other_tstyle_c)
            sheet.write(row, 9, data.sales_representative_id.name or None, other_tstyle_c)
            sheet.write(row, 10, data.ref or None, other_tstyle_c)
            sheet.write(row, 11, data.related_company_id.name or None, other_tstyle_c)
            sheet.write(row, 12, data.gender or None, other_tstyle_c)
            sheet.write(row, 13, data.phone or None, other_tstyle_c)
            sheet.write(row, 14, data.phone2 or None, other_tstyle_c)
            sheet.write(row, 15, data.email or None, other_tstyle_c)
            sheet.write(row, 16, data.fax or None, other_tstyle_c)
            sheet.write(row, 17, data.contract_no or None, other_tstyle_c)
            sheet.write(row, 18, data.function or None, other_tstyle_c)
            sheet.write(row, 19, data.department or None, other_tstyle_c)
            sheet.write(row, 20, data.actives or None, other_tstyle_c)
            row += 1

        stream = cStringIO.StringIO()
        workbook.save(stream)
        attach_id = self.env['print.xls.cols'].create({'name': 'Ordering Contact List Based on Customer.xls',
                                                                'xls_output': base64.encodestring(stream.getvalue())})
        return {
            'name': ('Notification'),
            'context': self._context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'print.xls.cols',
            'res_id': attach_id.id,
            'type': 'ir.actions.act_window',
            'target': 'new'
        }


class interp_contact_list_dashboard(models.Model):
    _name = 'interp.contact.list.dashboard'

    name = fields.Char('Ordering Contacts Report-Interpreter',default='Ordering Contacts Report Based on Interpreter')
    from_date = fields.Date('From Date',default=lambda *a: time.strftime('%Y-%m-01'))
    to_date = fields.Date('To Date',default=lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
    company_id = fields.Many2one('res.company', 'Company')
    contact = fields.Many2one('res.partner', 'Contact')
    interpreter = fields.Many2one('res.partner', 'Interpreter Name')
    contact_line_ids = fields.One2many('contact.lines', 'interp_contact_id', 'Contact Lines')

    @api.multi
    def search_contacts_interp(self):
        cur_obj = self
        contact_line = cur_obj.contact_line_ids
        contact_lines = map(lambda x: x.id, contact_line)
        self.env['contact.lines'].unlink(contact_lines)

        from_date = "'" + cur_obj.from_date + "'"
        to_date = "'"+cur_obj.to_date+"'"
        company_id = cur_obj.company_id.id
        query = """
                SELECT res_partner.name,event.name AS event_id,event.language_id AS language,res_partner.ref,
                res_partner.complete_name,res_partner.active,res_partner.cust_type,res_partner.title,res_partner.gender,
                res_partner.contract_no,res_partner.function,res_partner.department,res_partner.phone,res_partner.phone2,
                res_partner.email,res_partner.fax,event.sales_representative_id,account_invoice.amount_total,
                res_partner.parent_id AS related_company,res_partner.company_id AS company_id,
                event_partner_rel.interpreter_id AS interpreter, event.event_date,account_invoice.type
                FROM res_partner
                LEFT JOIN event ON event.ordering_contact_id = res_partner.id
                LEFT JOIN event_partner_rel ON event_partner_rel.event_id = event.id
                LEFT JOIN task_inv_rel ON task_inv_rel.event_id = event.id
                LEFT JOIN account_invoice ON account_invoice.id = task_inv_rel.invoice_id
                WHERE res_partner.company_id = %s and event.event_start_date BETWEEN %s AND %s""" % (str(company_id), from_date, to_date)

        where = ""

        if cur_obj.contact and cur_obj.contact != False:
            where += " and res_partner.id = "+str(cur_obj.contact.id)
        if cur_obj.interpreter and cur_obj.interpreter != False:
            where += " and event_partner_rel.interpreter_id = "+str(cur_obj.interpreter.id)

        self._cr.execute(query+where+";")
        data = self._cr.fetchall()
        if not data:
            raise UserError(_('No data available for selected filters'))
        else:
            for res in data:
                if res[5] == True:
                    active = 'True'
                else:
                    active = 'False'
                self.write( {'contact_line_ids': [(0, False, {'complete_name': res[4], 'title':res[7],
                    'type': res[6], 'company_id':res[19], 'event_id':res[1], 'event_create_date':res[21],
                    'interpreter':res[20], 'language':res[2], 'interp_inv_amt':res[17], 'sales_representative_id':res[16],
                    'ref':res[3], 'related_company_id':res[18], 'gender':res[8], 'phone':res[12], 'phone2':res[13],
                    'email':res[14], 'fax':res[15], 'contract_no':res[9], 'function':res[10], 'department':res[11],
                    'actives':active})]})
        return True

    @api.multi
    def print_xls_report_interp(self):
        self.search_contacts_interp()
        cur_obj = self

        header_tstyle_c = format_common.font_style(position='center', bold=1, border=1, fontos='black', font_height=150, color='grey')
        other_tstyle_c = format_common.font_style(position='center', fontos='black', font_height=200)
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('Ordering Contact List')
        sheet.row(0).height = 256 * 3
        sheet.normal_magn = 120
        sheet.write_merge(0, 0, 0, 4, 'Report for : Ordering Contact List Interpreterwise (' + cur_obj.company_id.name + ')', header_tstyle_c)

        row = 5
        sheet.write(row, 0, 'Name', header_tstyle_c)
        sheet.write(row, 1, 'Title', header_tstyle_c)
        sheet.write(row, 2, 'Type', header_tstyle_c)
        sheet.write(row, 3, 'Company', header_tstyle_c)
        sheet.write(row, 4, 'Event Id', header_tstyle_c)
        sheet.write(row, 5, 'Event Date', header_tstyle_c)
        sheet.write(row, 6, 'Event Interpreter', header_tstyle_c)
        sheet.write(row, 7, 'Event Language', header_tstyle_c)
        sheet.write(row, 8, 'Interpreter Invoice Amount', header_tstyle_c)
        sheet.write(row, 9, 'Event Sales Representative', header_tstyle_c)
        sheet.write(row, 10, 'Reference', header_tstyle_c)
        sheet.write(row, 11, 'Related Company', header_tstyle_c)
        sheet.write(row, 12, 'Gender', header_tstyle_c)
        sheet.write(row, 13, 'Phone', header_tstyle_c)
        sheet.write(row, 14, 'Phone2', header_tstyle_c)
        sheet.write(row, 15, 'Email', header_tstyle_c)
        sheet.write(row, 16, 'Fax', header_tstyle_c)
        sheet.write(row, 17, 'Contract No', header_tstyle_c)
        sheet.write(row, 18, 'Job Position', header_tstyle_c)
        sheet.write(row, 19, 'Department', header_tstyle_c)
        sheet.write(row, 20, 'Active', header_tstyle_c)

        row = 6
        for data in cur_obj.contact_line_ids:
            sheet.write(row, 0, data.complete_name or None, other_tstyle_c)
            sheet.write(row, 1, data.title or None, other_tstyle_c)
            sheet.write(row, 2, data.type or None, other_tstyle_c)
            sheet.write(row, 3, data.company_id.name or None, other_tstyle_c)
            sheet.write(row, 4, data.event_id or None, other_tstyle_c)
            sheet.write(row, 5, data.event_create_date or None, other_tstyle_c)
            sheet.write(row, 6, data.interpreter.name or None, other_tstyle_c)
            sheet.write(row, 7, data.language.name or None, other_tstyle_c)
            sheet.write(row, 8, data.interp_inv_amt or None, other_tstyle_c)
            sheet.write(row, 9, data.sales_representative_id.name or None, other_tstyle_c)
            sheet.write(row, 10, data.ref or None, other_tstyle_c)
            sheet.write(row, 11, data.related_company_id.name or None, other_tstyle_c)
            sheet.write(row, 12, data.gender or None, other_tstyle_c)
            sheet.write(row, 13, data.phone or None, other_tstyle_c)
            sheet.write(row, 14, data.phone2 or None, other_tstyle_c)
            sheet.write(row, 15, data.email or None, other_tstyle_c)
            sheet.write(row, 16, data.fax or None, other_tstyle_c)
            sheet.write(row, 17, data.contract_no or None, other_tstyle_c)
            sheet.write(row, 18, data.function or None, other_tstyle_c)
            sheet.write(row, 19, data.department or None, other_tstyle_c)
            sheet.write(row, 20, data.actives or None, other_tstyle_c)
            row += 1

        stream = cStringIO.StringIO()
        workbook.save(stream)
        attach_id = self.env['print.xls.cols'].create({'name': 'Ordering Contact List Based on Interpreter.xls',
                                                                'xls_output': base64.encodestring(stream.getvalue())})
        return {
            'name': ('Notification'),
            'context': self._context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'print.xls.cols',
            'res_id': attach_id.id,
            'type': 'ir.actions.act_window',
            'target': 'new'
        }


