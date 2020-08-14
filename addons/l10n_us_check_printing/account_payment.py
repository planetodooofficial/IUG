# -*- coding: utf-8 -*-

from odoo import models, api, _,fields
from odoo.tools import amount_to_text_en, float_round
import math
from odoo.exceptions import UserError, ValidationError

class account_payment(models.Model):
    _inherit = "account.payment"

    check_done=fields.Boolean("Check Printed")
    state = fields.Selection(selection_add=[('cancel', 'Cancelled')])

    @api.multi
    def do_print_checks(self):
        us_check_layout = self[0].company_id.us_check_layout
        if us_check_layout != 'disabled':
            return self.env['report'].get_action(self, us_check_layout)
        return super(account_payment, self).do_print_checks()

    def _get_check_amount_in_words(self, amount):
        # TODO: merge, refactor and complete the amount_to_text and amount_to_text_en classes
        check_amount_in_words = amount_to_text_en.amount_to_text(amount, lang='en', currency='usd')
        if check_amount_in_words.find('usd') >= 1:
            check_amount_in_words = check_amount_in_words.replace('usd', 'Dollars')
        check_amount_in_words = check_amount_in_words.replace(' and Zero Cent', '') # Ugh
        #decimals = amount % 1
        #if decimals >= 10**-2:
        #    check_amount_in_words += _(' and %s Cents') % str(int(round(float_round(decimals*100, precision_rounding=1))))
        return check_amount_in_words

    @api.multi
    def print_stub(self):
        return self.env['report'].get_action(self, 'l10n_us_check_printing.ckus_stub_for_stub')

    @api.multi
    def cancel(self):
        for rec in self:
            for move in rec.move_line_ids.mapped('move_id'):
                if rec.invoice_ids:
                    move.line_ids.remove_move_reconcile()
                move.button_cancel()
                move.unlink()
            rec.state = 'cancel'

    @api.multi
    def draft(self):
        for rec in self:
            rec.state='draft'
