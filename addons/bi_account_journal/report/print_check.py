# -*- coding: utf-8 -*-

from odoo.osv import osv
from odoo.report import report_sxw
from odoo.tools.translate import _

LINE_FILLER = '*'
INV_LINES_PER_STUB = 9
import logging
_logger = logging.getLogger('mapping_code')

class report_print_check_receipt(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(report_print_check_receipt, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'pages': self.get_pages,
        })

    def fill_line(self, amount_str):
        return amount_str and (amount_str+' ').ljust(200, LINE_FILLER) or ''

    def get_pages(self, receipt):
        """ Returns the data structure used by the template : a list of dicts containing what to print on pages.
        """
        stub_pages = self.make_stub_pages(receipt)
        multi_stub = receipt.company_id.us_check_multi_stub
        pages = []
        partner_name = receipt.customer.name
        if receipt.customer.last_name:
            partner_name += ' ' + receipt.customer.last_name
        address = receipt.customer
        for i in range(0, stub_pages != None and len(stub_pages) or 1):
            pages.append({
                'sequence_number': receipt.check_number \
                    if (receipt.journal_id.check_manual_sequencing and receipt.check_number != 0) \
                    else False,
                'payment_date': receipt.receipt_date,
                'partner_name': partner_name,
                'currency': receipt.currency_id,
                'amount': receipt.total if i == 0 else 'VOID',
                'amount_in_word': self.fill_line(
                    receipt.get_check_amount_in_words(receipt.total)) if i == 0 else 'VOID',
                'memo': receipt.communication,
                'stub_cropped': not multi_stub and len(receipt.receipt_ids) > INV_LINES_PER_STUB,
                # If the payment does not reference an invoice, there is no stub line to display
                'stub_lines': stub_pages != None and stub_pages[i],
                'address': address
            })
        return pages

    def make_stub_pages(self, receipt):
        """ The stub is the summary of paid invoices. It may spill on several pages, in which case only the check on
            first page is valid. This function returns a list of stub lines per page.
        """
        if len(receipt.receipt_ids) == 0:
            return None

        multi_stub = receipt.company_id.us_check_multi_stub

        receipts = receipt.receipt_ids

        stub_lines = [self.make_stub_line(receipt, rec) for rec in receipts]


        # Crop the stub lines or split them on multiple pages
        if not multi_stub:
            # If we need to crop the stub, leave place for an ellipsis line
            num_stub_lines = len(stub_lines) > INV_LINES_PER_STUB and INV_LINES_PER_STUB-1 or INV_LINES_PER_STUB
            stub_pages = [stub_lines[:num_stub_lines]]
        else:
            stub_pages = []
            i = 0
            while i < len(stub_lines):
                num_stub_lines = INV_LINES_PER_STUB
                stub_pages.append(stub_lines[i:i+num_stub_lines])
                i += num_stub_lines

        return stub_pages

    def make_stub_line(self, receipt, rec):
        """ Return the dict used to display an invoice/refund in the stub
        """

        return {
            'due_date': '',
            'number': rec.name,
            'amount_total': 0.0,
            'amount_residual': rec.price_subtotal,
            'amount_paid':  rec.price_subtotal,
            'currency': receipt.currency_id,
        }


class print_check_top_receipt(osv.AbstractModel):
    _name = 'report.bi_account_journal.print_check_top_receipt'
    _inherit = 'report.abstract_report'
    _template = 'bi_account_journal.print_check_top_receipt'
    _wrapped_report_class = report_print_check_receipt

class print_check_middle_receipt(osv.AbstractModel):
    _name = 'report.bi_account_journal.print_check_middle_receipt'
    _inherit = 'report.abstract_report'
    _template = 'bi_account_journal.print_check_middle_receipt'
    _wrapped_report_class = report_print_check_receipt

class print_check_bottom_receipt(osv.AbstractModel):
    _name = 'report.bi_account_journal.print_check_bottom_receipt'
    _inherit = 'report.abstract_report'
    _template = 'bi_account_journal.print_check_bottom_receipt'
    _wrapped_report_class = report_print_check_receipt

class report_print_check_payment(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(report_print_check_payment, self).__init__(cr, uid, name, context)
        _logger.error('--------in init------')
        self.localcontext.update({
            'pages': self.get_pages,
        })

    def fill_line(self, amount_str):
        return amount_str and (amount_str+' ').ljust(200, LINE_FILLER) or ''

    def get_pages(self, payment):
        """ Returns the data structure used by the template : a list of dicts containing what to print on pages.
        """
        _logger.error('--------in get pages------')
        stub_pages = self.make_stub_pages(payment)
        _logger.error('--------in get stub_pages%s------',stub_pages)
        credit_stub_page=self.credit_make_stub_pages(payment)
        _logger.error('--------in get credit_stub_page%s------',credit_stub_page)
        multi_stub = payment.company_id.us_check_multi_stub
        partner_name = payment.customer.name
        if payment.customer.last_name:
            partner_name += ' ' + payment.customer.last_name
        address = payment.customer
        pages = []
        pages1=[]
        for i in range(0, credit_stub_page != None and len(credit_stub_page) or 1):
            if credit_stub_page != None:
                pages1.append(credit_stub_page[i])
        for i in range(0, stub_pages != None and len(stub_pages) or 1):
            pages.append({
                'sequence_number': payment.check_number_string or payment.check_number or False,
                'payment_date': payment.payment_date,
                'partner_name': partner_name,
                'currency': payment.currency_id,
                'amount': (payment.total-payment.credit_total) if i == 0 else 'VOID',
                'amount_in_word': self.fill_line(payment.get_check_amount_in_words(payment.total-payment.credit_total)) if i == 0 else 'VOID',
                'memo': payment.communication,
                'stub_cropped': not multi_stub and len(payment.payment_ids) > INV_LINES_PER_STUB,
                # If the payment does not reference an invoice, there is no stub line to display
                'stub_lines': stub_pages != None and stub_pages[i],
                'credit_stub_lines': pages1[0],
                'address':address
            })
        _logger.error('--------in get pages------%s',pages)
        return pages

    def make_stub_pages(self, payment):
        """ The stub is the summary of paid invoices. It may spill on several pages, in which case only the check on
            first page is valid. This function returns a list of stub lines per page.
        """
        if len(payment.payment_ids) == 0:
            return None

        multi_stub = payment.company_id.us_check_multi_stub

        payments = payment.payment_ids

        stub_lines = [self.make_stub_line(payment, pay) for pay in payments]

        # Crop the stub lines or split them on multiple pages
        if not multi_stub:
            # If we need to crop the stub, leave place for an ellipsis line
            num_stub_lines = len(stub_lines) > INV_LINES_PER_STUB and INV_LINES_PER_STUB - 1 or INV_LINES_PER_STUB
            stub_pages = [stub_lines[:num_stub_lines]]
        else:
            stub_pages = []
            i = 0
            while i < len(stub_lines):
                num_stub_lines = INV_LINES_PER_STUB
                stub_pages.append(stub_lines[i:i + num_stub_lines])
                i += num_stub_lines

        return stub_pages
    def credit_make_stub_pages(self, payment):
        """ The stub is the summary of paid invoices. It may spill on several pages, in which case only the check on
            first page is valid. This function returns a list of stub lines per page.
        """
        if len(payment.credit_ids) == 0:
            return None
        _logger.error('--------in get credit------')
        multi_stub = payment.company_id.us_check_multi_stub

        credits = payment.credit_ids

        credits_stub_lines = [self.credit_make_stub_line(payment, pay) for pay in credits]
        # Crop the stub lines or split them on multiple pages
        if not multi_stub:
            # If we need to crop the stub, leave place for an ellipsis line
            num_stub_lines = len(credits_stub_lines) > INV_LINES_PER_STUB and INV_LINES_PER_STUB - 1 or INV_LINES_PER_STUB
            credits_stub_pages = [credits_stub_lines[:num_stub_lines]]
        else:
            credits_stub_pages = []
            i = 0
            while i < len(credits_stub_lines):
                num_stub_lines = INV_LINES_PER_STUB
                credits_stub_pages.append(credits_stub_lines[i:i + num_stub_lines])
                i += num_stub_lines
        return credits_stub_pages

    def make_stub_line(self, payment, pay):
        """ Return the dict used to display an invoice/refund in the stub
        """
        return {
            'due_date': '',
            'number': pay.name,
            'amount_total': 0.0,
            'amount_residual': pay.price_subtotal,
            'amount_paid': pay.price_subtotal,
            'currency': payment.currency_id,
        }
    def credit_make_stub_line(self, payment, pay):
        """ Return the dict used to display an invoice/refund in the stub
        """
        _logger.error('--------in get credit lines------')
        return {
            'due_date': '',
            'number': pay.name,
            'amount_total': 0.0,
            'amount_residual': -(pay.price_subtotal),
            'amount_paid': -(pay.price_subtotal),
            'currency': payment.currency_id,
        }



class print_check_top_payment(osv.AbstractModel):
    _name = 'report.bi_account_journal.print_check_top_payment'
    _inherit = 'report.abstract_report'
    _template = 'bi_account_journal.print_check_top_payment'
    _wrapped_report_class = report_print_check_payment

class print_check_middle_payment(osv.AbstractModel):
    _name = 'report.bi_account_journal.print_check_middle_payment'
    _inherit = 'report.abstract_report'
    _template = 'bi_account_journal.print_check_middle_payment'
    _wrapped_report_class = report_print_check_payment

class print_check_bottom_payment(osv.AbstractModel):
    _name = 'report.bi_account_journal.print_check_bottom_payment'
    _inherit = 'report.abstract_report'
    _template = 'bi_account_journal.print_check_bottom_payment'
    _wrapped_report_class = report_print_check_payment
