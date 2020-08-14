# -*- coding: utf-8 -*-

from odoo.osv import osv
from odoo.report import report_sxw
from odoo.tools.translate import _

LINE_FILLER = '*'
INV_LINES_PER_STUB = 9
import logging
_logger = logging.getLogger(__name__)

class report_print_check(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(report_print_check, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'pages': self.get_pages,
        })

    def fill_line(self, amount_str):
        return amount_str and (amount_str+' ').ljust(200, LINE_FILLER) or ''

    def get_pages(self, payment):
        """ Returns the data structure used by the template : a list of dicts containing what to print on pages.
        """
        stub_pages = self.make_stub_pages(payment)
        multi_stub = payment.company_id.us_check_multi_stub
        partner_name=payment.partner_id.name
        if payment.partner_id.last_name:
            partner_name += ' ' + payment.partner_id.last_name
        address=payment.partner_id
        pages = []
        for i in range(0, stub_pages != None and len(stub_pages) or 1):
            page_dict={
                'sequence_number': payment.check_number_string or payment.check_number or False,
                'payment_date': payment.payment_date,
                'partner_name': partner_name,
                'currency': payment.currency_id,
                'amount': payment.amount if i == 0 else 'VOID',
                'amount_in_word': self.fill_line(payment.check_amount_in_words) if i == 0 else 'VOID',
                'memo': payment.communication,
                # If the payment does not reference an invoice, there is no stub line to display
                'stub_lines': stub_pages != None and stub_pages[i],
                'address':address,
            }
            if len(payment.line_ids):
               count=0
               for rec in payment.line_ids:
                  if rec.allocation > 0.0:
                     count+=1
               page_dict.update({'stub_cropped': not multi_stub and count > INV_LINES_PER_STUB})
            else:
               page_dict.update({'stub_cropped': not multi_stub and len(payment.invoice_ids) > INV_LINES_PER_STUB})
            pages.append(page_dict)
        return pages

    def make_stub_pages(self, payment):
        """ The stub is the summary of paid invoices. It may spill on several pages, in which case only the check on
            first page is valid. This function returns a list of stub lines per page.
        """
        if len(payment.invoice_ids) == 0 and len(payment.line_ids) == 0:
            return None

        multi_stub = payment.company_id.us_check_multi_stub

        if len(payment.line_ids) == 0:
            invoices = payment.invoice_ids.sorted(key=lambda r: r.date_due)
            # debits = invoices.filtered(lambda r: r.type == 'in_invoice')
            # credits = invoices.filtered(lambda r: r.type == 'in_refund')
            stub_lines = [self.make_stub_line(payment, inv) for inv in invoices]
        else:
            invoices = payment.line_ids.sorted(key=lambda r: r.due_date)
            invoices=invoices.filtered(lambda r: r.allocation != 0.0)
            # debits = invoices.filtered(lambda r: r.type == 'in_invoice')
            # credits = invoices.filtered(lambda r: r.type == 'in_refund')
            stub_lines = [self.make_stub_line_for_line_ids(payment, inv) for inv in invoices]

        # Prepare the stub lines
        # if not credits:


        # else:
        #     stub_lines = [{'header': True, 'name': "Bills"}]
        #     stub_lines += [self.make_stub_line(payment, inv) for inv in debits]
        #     stub_lines += [{'header': True, 'name': "Refunds"}]
        #     stub_lines += [self.make_stub_line(payment, inv) for inv in credits]

        # Crop the stub lines or split them on multiple pages
        if not multi_stub:
            # If we need to crop the stub, leave place for an ellipsis line
            num_stub_lines = len(stub_lines) > INV_LINES_PER_STUB and INV_LINES_PER_STUB-1 or INV_LINES_PER_STUB
            stub_pages = [stub_lines[:num_stub_lines]]
        else:
            stub_pages = []
            i = 0
            while i < len(stub_lines):
                # Make sure we don't start the credit section at the end of a page
                if len(stub_lines) >= i+INV_LINES_PER_STUB and stub_lines[i+INV_LINES_PER_STUB-1].get('header'):
                    num_stub_lines = INV_LINES_PER_STUB-1 or INV_LINES_PER_STUB
                else:
                    num_stub_lines = INV_LINES_PER_STUB
                stub_pages.append(stub_lines[i:i+num_stub_lines])
                i += num_stub_lines

        return stub_pages

    def make_stub_line(self, payment, invoice):
        """ Return the dict used to display an invoice/refund in the stub
        """
        # Find the account.partial.reconcile which are common to the invoice and the payment
        if invoice.type in ['in_invoice', 'out_refund']:
            invoice_sign = 1
            invoice_payment_reconcile = invoice.move_id.line_ids.mapped('matched_debit_ids').filtered(lambda r: r.debit_move_id in payment.move_line_ids)
        else:
            invoice_sign = -1
            invoice_payment_reconcile = invoice.move_id.line_ids.mapped('matched_credit_ids').filtered(lambda r: r.credit_move_id in payment.move_line_ids)

        if payment.currency_id != payment.journal_id.company_id.currency_id:
            amount_paid = abs(sum(invoice_payment_reconcile.mapped('amount_currency')))
        else:
            amount_paid = abs(sum(invoice_payment_reconcile.mapped('amount')))

        return {
            'due_date': invoice.event_id and invoice.event_id.event_start_date or '',
            'number': invoice.reference and invoice.number + ' - ' + invoice.reference or invoice.number,
            'amount_total': invoice_sign * invoice.amount_total,
            'amount_residual': invoice_sign * invoice.residual,
            'amount_paid': invoice_sign * amount_paid,
            'currency': invoice.currency_id,
        }

    def make_stub_line_for_line_ids(self, payment, invoice):
        """ Return the dict used to display an invoice/refund in the stub
        """
        # Find the account.partial.reconcile which are common to the invoice and the payment
        if invoice.invoice_id.type in ['in_invoice', 'out_refund']:
            invoice_sign = 1
            invoice_payment_reconcile = invoice.invoice_id.move_id.line_ids.mapped('matched_debit_ids').filtered(lambda r: r.debit_move_id in payment.move_line_ids)
        else:
            invoice_sign = -1
            invoice_payment_reconcile = invoice.invoice_id.move_id.line_ids.mapped('matched_credit_ids').filtered(lambda r: r.credit_move_id in payment.move_line_ids)

        if payment.currency_id != payment.journal_id.company_id.currency_id:
            amount_paid = abs(sum(invoice_payment_reconcile.mapped('amount_currency')))
        else:
            amount_paid = abs(sum(invoice_payment_reconcile.mapped('amount')))

        return {
            'due_date': invoice.invoice_id and invoice.invoice_id.event_id and invoice.invoice_id.event_id.event_start_date or '',
            'number': invoice.invoice_id.reference and invoice.invoice_id.number + ' - ' + invoice.invoice_id.reference or invoice.invoice_id.number,
            'amount_total': invoice_sign * invoice.invoice_id.amount_total,
            'amount_residual': invoice_sign * invoice.invoice_id.residual,
            'amount_paid': invoice_sign * amount_paid,
            'currency': invoice.invoice_id.currency_id,
        }


class print_check_top(osv.AbstractModel):
    _name = 'report.l10n_us_check_printing.print_check_top'
    _inherit = 'report.abstract_report'
    _template = 'l10n_us_check_printing.print_check_top'
    _wrapped_report_class = report_print_check

class print_check_middle(osv.AbstractModel):
    _name = 'report.l10n_us_check_printing.print_check_middle'
    _inherit = 'report.abstract_report'
    _template = 'l10n_us_check_printing.print_check_middle'
    _wrapped_report_class = report_print_check

class print_check_bottom(osv.AbstractModel):
    _name = 'report.l10n_us_check_printing.print_check_bottom'
    _inherit = 'report.abstract_report'
    _template = 'l10n_us_check_printing.print_check_bottom'
    _wrapped_report_class = report_print_check

class report_print_stub(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(report_print_stub, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'pages': self.get_pages,
        })

    def fill_line(self, amount_str):
        return amount_str and (amount_str+' ').ljust(200, LINE_FILLER) or ''

    def get_pages(self, payment):
        """ Returns the data structure used by the template : a list of dicts containing what to print on pages.
        """
        stub_pages = self.make_stub_pages(payment)
        multi_stub = payment.company_id.us_check_multi_stub
        partner_name=payment.partner_id.name
        if payment.partner_id.last_name:
            partner_name += ' ' + payment.partner_id.last_name
        address=payment.partner_id
        pages = []
        _logger.info('----------------check_number --------------------- %s',payment.check_number)
        for i in range(0, stub_pages != None and len(stub_pages) or 1):

            pages.append({
                'sequence_number': payment.check_number_string or payment.check_number or False,
                'payment_date': payment.payment_date,
                'partner_name': partner_name,
                'currency': payment.currency_id,
                'amount': payment.amount if i == 0 else 'VOID',
                'amount_in_word': self.fill_line(payment.check_amount_in_words) if i == 0 else 'VOID',
                'memo': payment.communication,
                'stub_cropped': False,
                # If the payment does not reference an invoice, there is no stub line to display
                'stub_lines': stub_pages != None and stub_pages[i],
                'address':address,
            })
            _logger.info('--------------------pages----------------%s',pages)
        return pages

    def make_stub_pages(self, payment):
        """ The stub is the summary of paid invoices. It may spill on several pages, in which case only the check on
            first page is valid. This function returns a list of stub lines per page.
        """
        if len(payment.invoice_ids) == 0 and len(payment.line_ids) == 0:
            return None

        multi_stub = payment.company_id.us_check_multi_stub

        if len(payment.line_ids) == 0:
            invoices = payment.invoice_ids.sorted(key=lambda r: r.date_due)
            # debits = invoices.filtered(lambda r: r.type == 'in_invoice')
            # credits = invoices.filtered(lambda r: r.type == 'in_refund')
            stub_lines = [self.make_stub_line(payment, inv) for inv in invoices]
        else:
            invoices = payment.line_ids.sorted(key=lambda r: r.due_date)
            invoices=invoices.filtered(lambda r: r.allocation != 0.0)
            # debits = invoices.filtered(lambda r: r.type == 'in_invoice')
            # credits = invoices.filtered(lambda r: r.type == 'in_refund')
            stub_lines = [self.make_stub_line_for_line_ids(payment, inv) for inv in invoices]

        # Prepare the stub lines
        # if not credits:


        # else:
        #     stub_lines = [{'header': True, 'name': "Bills"}]
        #     stub_lines += [self.make_stub_line(payment, inv) for inv in debits]
        #     stub_lines += [{'header': True, 'name': "Refunds"}]
        #     stub_lines += [self.make_stub_line(payment, inv) for inv in credits]

        # Crop the stub lines or split them on multiple pages
        # if not multi_stub:
        #     # If we need to crop the stub, leave place for an ellipsis line
        #     num_stub_lines = len(stub_lines) > INV_LINES_PER_STUB and INV_LINES_PER_STUB-1 or INV_LINES_PER_STUB
        #     stub_pages = [stub_lines[:num_stub_lines]]
        # else:
        stub_pages = []
        stub_pages.append(stub_lines)
        # i = 0
        # while i < len(stub_lines):
        #     # Make sure we don't start the credit section at the end of a page
        #     if len(stub_lines) >= i+INV_LINES_PER_STUB and stub_lines[i+INV_LINES_PER_STUB-1].get('header'):
        #         num_stub_lines = INV_LINES_PER_STUB-1 or INV_LINES_PER_STUB
        #     else:
        #         num_stub_lines = INV_LINES_PER_STUB
        #     stub_pages.append(stub_lines[i:i+num_stub_lines])
        #     i += num_stub_lines

        return stub_pages

    def make_stub_line(self, payment, invoice):
        """ Return the dict used to display an invoice/refund in the stub
        """
        # Find the account.partial.reconcile which are common to the invoice and the payment
        if invoice.type in ['in_invoice', 'out_refund']:
            invoice_sign = 1
            invoice_payment_reconcile = invoice.move_id.line_ids.mapped('matched_debit_ids').filtered(lambda r: r.debit_move_id in payment.move_line_ids)
        else:
            invoice_sign = -1
            invoice_payment_reconcile = invoice.move_id.line_ids.mapped('matched_credit_ids').filtered(lambda r: r.credit_move_id in payment.move_line_ids)

        if payment.currency_id != payment.journal_id.company_id.currency_id:
            amount_paid = abs(sum(invoice_payment_reconcile.mapped('amount_currency')))
        else:
            amount_paid = abs(sum(invoice_payment_reconcile.mapped('amount')))

        return {
            'due_date': invoice.event_id and invoice.event_id.event_start_date or '',
            'number': invoice.reference and invoice.number + ' - ' + invoice.reference or invoice.number,
            'amount_total': invoice_sign * invoice.amount_total,
            'amount_residual': invoice_sign * invoice.residual,
            'amount_paid': invoice_sign * amount_paid,
            'currency': invoice.currency_id,
        }

    def make_stub_line_for_line_ids(self, payment, invoice):
        """ Return the dict used to display an invoice/refund in the stub
        """
        # Find the account.partial.reconcile which are common to the invoice and the payment
        if invoice.invoice_id.type in ['in_invoice', 'out_refund']:
            invoice_sign = 1
            invoice_payment_reconcile = invoice.invoice_id.move_id.line_ids.mapped('matched_debit_ids').filtered(lambda r: r.debit_move_id in payment.move_line_ids)
        else:
            invoice_sign = -1
            invoice_payment_reconcile = invoice.invoice_id.move_id.line_ids.mapped('matched_credit_ids').filtered(lambda r: r.credit_move_id in payment.move_line_ids)

        if payment.currency_id != payment.journal_id.company_id.currency_id:
            amount_paid = abs(sum(invoice_payment_reconcile.mapped('amount_currency')))
        else:
            amount_paid = abs(sum(invoice_payment_reconcile.mapped('amount')))

        return {
            'due_date': invoice.invoice_id and invoice.invoice_id.event_id and invoice.invoice_id.event_id.event_start_date or '',
            'number': invoice.invoice_id.reference and invoice.invoice_id.number + ' - ' + invoice.invoice_id.reference or invoice.invoice_id.number,
            'amount_total': invoice_sign * invoice.invoice_id.amount_total,
            'amount_residual': invoice_sign * invoice.invoice_id.residual,
            'amount_paid': invoice_sign * amount_paid,
            'currency': invoice.invoice_id.currency_id,
        }




class ckus_stub_for_stub(osv.AbstractModel):
    _name = 'report.l10n_us_check_printing.ckus_stub_for_stub'
    _inherit = 'report.abstract_report'
    _template = 'l10n_us_check_printing.ckus_stub_for_stub'
    _wrapped_report_class = report_print_stub



