# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PrintPreNumberedPayments(models.TransientModel):
    _name = 'print.prenumbered.receipts'
    _description = 'Print Pre-numbered Receipts'

    next_check_number = fields.Integer('Next Check Number', required=True)

    @api.multi
    def print_checks(self):
        check_number = self.next_check_number
        payments = self.env['bi.account.receipt'].browse(self.env.context['payment_ids'])
        payments.filtered(lambda r: r.state == 'draft').button_post()
        for payment in payments:
            payment.check_number = check_number
            check_number += 1
            payment.journal_id.check_sequence_id.number_next_actual = check_number
        return payments.do_print_checks()
