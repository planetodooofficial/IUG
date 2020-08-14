from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import amount_to_text_en, float_round
import odoo.addons.decimal_precision as dp


# ==================================================
# Class : BiAccountReceipt
# Description : Account Receipt Details
# ==================================================
class BiAccountReceipt(models.Model):
    _name = "bi.account.receipt"
    _description = "Account Receipt Details"

    @api.depends('receipt_ids.price_total')
    def _compute_total(self):
        for receipt in self:
            amount_untaxed = amount_tax = 0.0
            for line in receipt.receipt_ids:
                amount_untaxed += line.price_subtotal
                # FORWARDPORT UP TO 10.0
                if receipt.company_id.tax_calculation_rounding_method == 'round_globally':
                    taxes = line.tax_id.compute_all(line.amount, line.currency_id, 1, product=False, partner=False)
                    amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                else:
                    amount_tax += line.price_tax
            receipt.update({
                'subtotal': receipt.currency_id.round(amount_untaxed),
                'amount_tax': receipt.currency_id.round(amount_tax),
                'total': amount_untaxed + amount_tax,
            })

    name = fields.Char(string="Sequence No", required=True, Index=True, default=lambda self: ('New'), readonly=True,
                       states={'draft': [('readonly', False)]})
    receipt_date = fields.Date(string="Receipt Date", default=fields.Date.context_today, required=True, readonly=True,
                               states={'draft': [('readonly', False)]})
    customer = fields.Many2one('res.partner', string="Customer", readonly=True, states={'draft': [('readonly', False)]})
    journal_id = fields.Many2one('account.journal', string="Journal ID", required=True, readonly=True,
                                 states={'draft': [('readonly', False)]}, domain=[('type', 'in', ('bank', 'cash'))])
    account_id = fields.Many2one('account.account', string="Account ID", required=True, readonly=True,
                                 states={'draft': [('readonly', False)]})
    narration = fields.Text(string="Narration")
    receipt_ids = fields.One2many('bi.account.receipt.line', 'receipt_id', string="Accounts")
    user_id = fields.Many2one('res.users', string='Username', default=lambda self: self.env.user)
    move_id = fields.Many2one('account.move', string='Journal Entry', readonly=True, index=True, ondelete='restrict',
                              copy=False,
                              help="Link to the automatically generated Journal Items.")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('post', 'Posted'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('sale.order'),
                                 states={'post': [('readonly', True)]})
    total = fields.Monetary(compute='_compute_total', string='Total', readonly=True, store=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id)
    amount_tax = fields.Monetary(string='Amount Tax', store=True, readonly=True, compute='_compute_total',
                                 digits_compute=dp.get_precision('Product Price'))
    subtotal = fields.Monetary(string='Sub Total', store=True, readonly=True, compute='_compute_total',
                               digits_compute=dp.get_precision('Product Price'))
    bank_type = fields.Selection([('cheque', 'Cheque'), ('ntfs', 'NTFS'), ('cash', 'Cash'), ('others', 'Others')],
                                 string="Payment Type", readonly=True, states={'draft': [('readonly', False)]})
    cheque_no = fields.Char("Cheque Number")
    Cheque_date = fields.Date("Cheque Date")
    communication = fields.Char('Memo')
    reference = fields.Char('Reference')
    check_number = fields.Integer(string="Check Number", readonly=False, copy=False,
                                  help="The selected journal is configured to print check numbers. If your pre-printed check paper already has numbers "
                                       "or if the current numbering is wrong, you can change it in the journal configuration page.")

    @api.onchange('journal_id')
    def onchange_journal_id(self):
        if self.journal_id:
            self.account_id = self.journal_id.default_debit_account_id

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    'bi.account.receipt') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('bi.account.receipt') or _('New')

        result = super(BiAccountReceipt, self).create(vals)
        return result


    @api.multi
    def button_post(self):
        aml_dict = {}
        total=0.0
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        for receipt in self:
            dst_move = self.env['account.move'].create({
    													'date': receipt.receipt_date,
    													'ref':'Receipt',
    													'company_id': receipt.company_id.id,
    													'journal_id':receipt.journal_id.id,
    													})
            for line in receipt.receipt_ids:
                i=1
                aml_dict={
    					'name':line.name and str(line.name) or '',
    					'account_id': line.account_id.id,
    					'currency_id': receipt.currency_id.id,
    					'journal_id': receipt.journal_id.id,
    					'debit':0.0,
    					'analytic_account_id':line.analytic_account_id and line.analytic_account_id.id or False,
    					'credit':line.price_subtotal,
    					'partner_id':receipt.customer.id,
    					'move_id':dst_move.id,
    				}
                total = total + line.price_subtotal
                aml_obj.create(aml_dict)
                if line.tax_id:
                    for tax in line.tax_id.compute_all(line.amount, line.currency_id, 1)['taxes']:
                        aml_dict={
    					'name':_('Tax') + ' ' + tax['name'],
    					'account_id': tax['account_id'],
    					'debit': ((tax['amount'] < 0) and -tax['amount']) or 0.0,
    					'credit': ((tax['amount'] > 0) and tax['amount']) or 0.0,
    					'move_id':dst_move.id,
    					'analytic_account_id': tax['analytic'] and line.analytic_account_id.id or False,
    					}
                        aml_obj.create(aml_dict)
                        total = total + tax['amount']

            if total> 0:
                aml_dict.update({
    				'name': line.name and str(line.name) or '',
    				'account_id': receipt.journal_id.default_debit_account_id.id,
    				'currency_id': receipt.currency_id.id,
    				'journal_id': receipt.journal_id.id,
    				'credit':0.0,
    				'debit':total,
    				'analytic_account_id':False,
    				'partner_id':receipt.customer.id,
    				'move_id':dst_move.id})
                aml_obj.create(aml_dict)
            dst_move.post()
            receipt.write({'state':'post','move_id':dst_move.id})

    @api.multi
    def do_print_checks(self):
        return self.env['report'].get_action(self, 'bi_account_journal.print_check_top_receipt')

    @api.multi
    def print_checks(self):
        """ Check that the recordset is valid, set the payments state to sent and call print_checks() """
        # Since this method can be called via a client_action_multi, we need to make sure the received records are what we expect
        self = self.filtered(lambda r: r.state not in ('post','cancel'))

        if len(self) == 0:
            raise UserError(_("To print checks for journal vouchers ,they should not be posted or cancelled "))
        if any(payment.journal_id != self[0].journal_id for payment in self):
            raise UserError(_("In order to print multiple checks at once, they must belong to the same bank journal."))

        if not self[0].journal_id.check_manual_sequencing:
            list_check_number = []
            # The wizard asks for the number printed on the first pre-printed check
            # so payments are attributed the number of the check the'll be printed on.
            last_printed_check_for_bi_acc_receipt = self.search([
                ('journal_id', '=', self[0].journal_id.id),
                ('check_number', '!=', 0)], order="check_number desc", limit=1)
            list_check_number.append(last_printed_check_for_bi_acc_receipt.check_number or 1)
            #last_printed_check_for_bi_acc_payment = self.env['bi.account.payment'].search([
            #    ('journal_id', '=', self[0].journal_id.id),
            #    ('check_number', '!=', 0)], order="check_number desc", limit=1)
            #list_check_number.append(last_printed_check_for_bi_acc_payment.check_number or 1)
            #last_printed_check = self.env['account.payment'].search([
            #    ('journal_id', '=', self[0].journal_id.id),
            #    ('check_number', '!=', 0)], order="check_number desc", limit=1)
            #list_check_number.append(last_printed_check.check_number or 1)
            max_check_number = max(list_check_number)
            next_check_number = max_check_number + 1 if max_check_number else 1
            return {
                'name': _('Print Pre-numbered Checks'),
                'type': 'ir.actions.act_window',
                'res_model': 'print.prenumbered.receipts',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'payment_ids': self.ids,
                    'default_next_check_number': next_check_number,
                }
            }
        else:
            self.filtered(lambda r: r.state == 'draft').button_post()
            return self.do_print_checks()


    @api.multi
    def button_cancel(self):
        if self.move_id:
            self.move_id.button_cancel()
            move_id = self.move_id
            self.write({'state': 'cancel', 'move_id': False})
            move_id.unlink()


    @api.multi
    def button_draft(self):
        self.write({'state': 'draft'})


    @api.multi
    def unlink(self):
        for order in self:
            if order.state not in ('draft'):
                raise UserError(_('You can not delete receipt voucher'))
        return super(BiAccountReceipt, self).unlink()


    @api.multi
    def get_check_amount_in_words(self, amount):
        # TODO: merge, refactor and complete the amount_to_text and amount_to_text_en classes
        check_amount_in_words = amount_to_text_en.amount_to_text(amount, lang='en', currency='')
        check_amount_in_words = check_amount_in_words.replace('Cents', ' Only')  # Ugh
        check_amount_in_words = check_amount_in_words.replace('Cent', ' Only')
        decimals = amount % 1
        # if decimals >= 10**-2:
        # 	check_amount_in_words += _(' and %s/100') % str(int(round(float_round(decimals*100, precision_rounding=1))))
        return check_amount_in_words


    @api.onchange('account_id')
    def OnchangeAccount(self):
        for x in self:
         x.tax_id = self.account_id.tax_ids


# ==================================================
# Class : BiAccountReceiptLine
# Description : Account Receipt Line
# ==================================================
class BiAccountReceiptLine(models.Model):
    _name = "bi.account.receipt.line"
    _description = "Account Receipt Line"

    @api.depends('amount', 'tax_id')
    def _compute_amount(self):
        for line in self:
            taxes = line.tax_id.compute_all(line.amount, line.currency_id, 1, product=False, partner=False)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    receipt_id = fields.Many2one('bi.account.receipt', string="Receipt")
    tax_id = fields.Many2many('account.tax', string='Taxes',
                              domain=['|', ('active', '=', False), ('active', '=', True)])
    account_id = fields.Many2one('account.account', domain=[], string="Account ID", required=True)
    analytic_account_id = fields.Many2one('account.analytic.account', "Analytic Account")
    name = fields.Char(string="Description", required=True)
    amount = fields.Float(string="Amount", required=True)
    currency_id = fields.Many2one('res.currency', related='receipt_id.currency_id', store=True, related_sudo=False)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    price_tax = fields.Monetary(compute='_compute_amount', string='Tax', store=True)


# ==================================================
# Class : BiAccountPayment
# Description : Account Payment Details
# ==================================================
class BiAccountPayment(models.Model):
    _name = "bi.account.payment"
    _description = "Account Payment Details"

    @api.depends('payment_ids.price_total')
    def _compute_total(self):
        for payment in self:
            amount_untaxed = amount_tax = 0.0
            for line in payment.payment_ids:
                amount_untaxed += line.price_subtotal
                # FORWARDPORT UP TO 10.0
                if payment.company_id.tax_calculation_rounding_method == 'round_globally':
                    taxes = line.tax_id.compute_all(line.amount, line.currency_id, 1, product=False, partner=False)
                    amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                else:
                    amount_tax += line.price_tax
            payment.update({
                'subtotal': payment.currency_id.round(amount_untaxed),
                'amount_tax': payment.currency_id.round(amount_tax),
                'total': amount_untaxed + amount_tax,
            })
    @api.depends('credit_ids.price_total')
    def _compute_credit_total(self):
        for credit in self:
            amount_untaxed = amount_tax = 0.0
            for line in credit.credit_ids:
                amount_untaxed += line.price_subtotal
                # FORWARDPORT UP TO 10.0
                if credit.company_id.tax_calculation_rounding_method == 'round_globally':
                    taxes = line.tax_id.compute_all(line.amount, line.currency_id, 1, product=False, partner=False)
                    amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                else:
                    amount_tax += line.price_tax
            credit.update({
                'credit_total': amount_untaxed + amount_tax,
            })

    name = fields.Char(string="Sequence No", required=True, Index=True, default=lambda self: ('New'), readonly=True,
                       states={'draft': [('readonly', False)]})
    payment_date = fields.Date(string="Payment Date", default=fields.Date.context_today, required=True, readonly=True,
                               states={'draft': [('readonly', False)]})
    customer = fields.Many2one('res.partner', string="Customer", readonly=True, states={'draft': [('readonly', False)]})
    journal_id = fields.Many2one('account.journal', string="Journal ID", required=True, readonly=True,
                                 states={'draft': [('readonly', False)]}, domain=[('type', 'in', ('bank', 'cash'))])
    account_id = fields.Many2one('account.account', string="Account ID", required=True, readonly=True,
                                 states={'draft': [('readonly', False)]})
    narration = fields.Text(string="Narration")
    user_id = fields.Many2one('res.users', string='Username', default=lambda self: self.env.user)
    payment_ids = fields.One2many('bi.account.voucher.payment.line', 'receipt_id', string="Debit")
    credit_ids = fields.One2many('bi.account.voucher.credit.line', 'credit_id', string="Credit")
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id)
    move_id = fields.Many2one('account.move', string='Journal Entry', readonly=True, index=True, ondelete='restrict',
                              copy=False,
                              help="Link to the automatically generated Journal Items.")
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('sale.order'),
                                 states={'post': [('readonly', True)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('post', 'Posted'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
    total = fields.Monetary(compute='_compute_total', string='Total', readonly=True, store=True)
    credit_total = fields.Monetary(compute='_compute_credit_total', string='Total', readonly=True, store=True)
    amount_tax = fields.Monetary(string='Amount Tax', store=True, readonly=True, compute='_compute_total',
                                 digits_compute=dp.get_precision('Product Price'))
    subtotal = fields.Monetary(string='Sub Total', store=True, readonly=True, compute='_compute_total',
                               digits_compute=dp.get_precision('Product Price'))
    bank_type = fields.Selection([('cheque', 'Cheque'), ('ntfs', 'NTFS'), ('cash', 'Cash'), ('others', 'Others')],
                                 string="Payment Type", states={'draft': [('readonly', False)]})
    cheque_no = fields.Char("Cheque Number")
    check_number = fields.Integer(string="Check Number", readonly=False, copy=False,
                                  help="The selected journal is configured to print check numbers. If your pre-printed check paper already has numbers "
                                       "or if the current numbering is wrong, you can change it in the journal configuration page.")
    Cheque_date = fields.Date("Cheque Date")
    communication = fields.Char('Memo')
    reference = fields.Char('Reference')
    check_number_string=fields.Char('Check Number(with alphabets)')

    @api.onchange('journal_id')
    def onchange_journal_id(self):
        if self.journal_id:
            self.account_id = self.journal_id.default_credit_account_id
        if self.journal_id and self.journal_id.check_manual_sequencing:
            self.check_number = self.journal_id.check_sequence_id.number_next_actual

    @api.multi
    def button_cancel(self):
        if self.move_id:
            self.move_id.button_cancel()
            move_id = self.move_id
            self.write({'state': 'cancel', 'move_id': False})
            move_id.unlink()

    @api.multi
    def do_print_checks(self):
        return self.env['report'].get_action(self,'bi_account_journal.print_check_top_payment')


    @api.multi
    def print_checks(self):
        """ Check that the recordset is valid, set the payments state to sent and call print_checks() """
        # Since this method can be called via a client_action_multi, we need to make sure the received records are what we expect
        self = self.filtered(lambda r: r.state not in ('post','cancel') )

        if len(self) == 0:
            raise UserError(_("To print checks for journal vouchers ,they should not be posted or cancelled "))
        if any(payment.journal_id != self[0].journal_id for payment in self):
            raise UserError(_("In order to print multiple checks at once, they must belong to the same bank journal."))

        if not self[0].journal_id.check_manual_sequencing:
            list_check_number = []
            # The wizard asks for the number printed on the first pre-printed check
            # so payments are attributed the number of the check the'll be printed on.
            last_printed_check_for_bi_acc_payment = self.search([
                ('journal_id', '=', self[0].journal_id.id),
                ('check_number', '!=', 0)], order="check_number desc", limit=1)
            list_check_number.append(last_printed_check_for_bi_acc_payment.check_number or 1)
            #last_printed_check_for_bi_acc_receipt = self.env['bi.account.receipt'].search([
            #    ('journal_id', '=', self[0].journal_id.id),
            #    ('check_number', '!=', 0)], order="check_number desc", limit=1)
            #list_check_number.append(last_printed_check_for_bi_acc_receipt.check_number or 1)
            last_printed_check = self.env['account.payment'].search([
                ('journal_id', '=', self[0].journal_id.id),
                ('check_number', '!=', 0)], order="check_number desc", limit=1)
            list_check_number.append(last_printed_check.check_number or 1)
            max_check_number = max(list_check_number)
            next_check_number = max_check_number + 1 if max_check_number else 1
            return {
                'name': _('Print Pre-numbered Checks'),
                'type': 'ir.actions.act_window',
                'res_model': 'print.prenumbered.payments',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'payment_ids': self.ids,
                    'default_next_check_number': next_check_number,
                }
            }
        else:
            self.filtered(lambda r: r.state == 'draft').button_post()
            return self.do_print_checks()

    @api.multi
    def button_draft(self):
        self.write({'state': 'draft'})

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    'bi.account.payment') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('bi.account.payment') or _('New')

        result = super(BiAccountPayment, self).create(vals)
        return result

    @api.multi
    def button_post(self):
        aml_dict = {}
        total_credit,total_debit = 0.0,0.0
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        for payment in self:
            dst_move = self.env['account.move'].create({
                # 'name': payment.name,
                'date': payment.payment_date,
                'ref': 'Payment',
                'company_id': payment.company_id.id,
                'journal_id': payment.journal_id.id,
            })
            payment.write({'move_id': dst_move.id})
            for line in payment.payment_ids:
                    aml_dict = {
                        'name': line.name and str(line.name) or '',
                        'account_id': line.account_id.id,
                        'currency_id': payment.currency_id.id,
                        'journal_id': payment.journal_id.id,
                        'debit': line.price_subtotal,
                        'analytic_account_id': line.analytic_account_id and line.analytic_account_id.id or False,
                        'credit': 0.0,
                        'partner_id': payment.customer.id,
                        'move_id': dst_move.id,
                    }
                    total_debit = total_debit + line.price_subtotal
                    aml_obj.create(aml_dict)
            for line in payment.credit_ids:
                    aml_dict = {
                        'name': line.name and str(line.name) or '',
                        'account_id': payment.journal_id.default_debit_account_id.id,
                        'currency_id': payment.currency_id.id,
                        'journal_id': payment.journal_id.id,
                        'debit': 0.0,
                        'analytic_account_id': line.analytic_account_id and line.analytic_account_id.id or False,
                        'credit': line.price_total,
                        'partner_id': payment.customer.id,
                        'move_id': dst_move.id,
                    }
                    total_credit = total_credit + line.price_total
                    aml_obj.create(aml_dict)
        if total_debit:
            aml_dict = {
                'name': line.name and str(line.name) or '',
                'account_id': payment.journal_id.default_debit_account_id.id,
                'currency_id': payment.currency_id.id,
                'journal_id': payment.journal_id.id,
                'credit': total_debit,
                'debit': 0.0,
                'analytic_account_id': False,
                'partner_id': payment.customer.id,
                'move_id': dst_move.id}
            aml_obj.create(aml_dict)
        if total_credit:
                aml_dict = {
                    'name': line.name and str(line.name) or '',
                    'account_id': line.account_id.id,
                    'currency_id': payment.currency_id.id,
                    'journal_id': payment.journal_id.id,
                    'credit': 0.0,
                    'debit': total_credit,
                    'analytic_account_id': False,
                    'partner_id': payment.customer.id,
                    'move_id': dst_move.id}
                aml_obj.create(aml_dict)
        dst_move.post()
        payment.write({'state': 'post', 'move_id': dst_move.id})
        self.write({'state': 'post'})


    
    @api.multi
    def button_test(self):
        aml_dict = {}
        total = 0.0
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        for payment in self:
            dst_move = self.env['account.move'].create({
                # 'name': payment.name,
                'date': payment.payment_date,
                'ref': 'Payment',
                'company_id': payment.company_id.id,
                'journal_id': payment.journal_id.id,
            })
            for line in payment.payment_ids:
                i = 1
                aml_dict = {
                    'name': line.name and str(line.name) or '',
                    'account_id': line.account_id.id,
                    'currency_id': payment.currency_id.id,
                    'journal_id': payment.journal_id.id,
                    'debit': line.price_subtotal,
                    'analytic_account_id': line.analytic_account_id and line.analytic_account_id.id or False,
                    'credit': 0.0,
                    'partner_id': payment.customer.id,
                    'move_id': dst_move.id,
                }
                total = total + line.price_subtotal
                aml_obj.create(aml_dict)
                if line.tax_id:
                    for tax in line.tax_id.compute_all(line.amount, line.currency_id, 1)['taxes']:
                        aml_dict = {
                            'name': _('Tax') + ' ' + tax['name'],
                            'account_id': tax['account_id'],
                            'debit': ((tax['amount'] > 0) and tax['amount']) or 0.0,
                            'credit': ((tax['amount'] < 0) and -tax['amount']) or 0.0,
                            'move_id': dst_move.id,
                            'analytic_account_id': tax['analytic'] and line.analytic_account_id.id or False,
                        }
                        aml_obj.create(aml_dict)
                        total = total + tax['amount']
            if total > 0:
                aml_dict.update({
                    'name': line.name and str(line.name) or '',
                    'account_id': payment.journal_id.default_debit_account_id.id,
                    'currency_id': payment.currency_id.id,
                    'journal_id': payment.journal_id.id,
                    'credit': total,
                    'debit': 0.0,
                    'analytic_account_id': False,
                    'partner_id': payment.customer.id,
                    'move_id': dst_move.id})
                aml_obj.create(aml_dict)
            dst_move.post()
            payment.write({'state': 'post', 'move_id': dst_move.id})

    @api.multi
    def unlink(self):
        for order in self:
            if order.state not in ('draft'):
                raise UserError(_('You can not delete payment voucher'))
        return super(BiAccountPayment, self).unlink()

    @api.multi
    def get_check_amount_in_words(self, amount):
        # TODO: merge, refactor and complete the amount_to_text and amount_to_text_en classes
        check_amount_in_words = amount_to_text_en.amount_to_text(amount, lang='en', currency='')
        check_amount_in_words = check_amount_in_words.replace('Cents', ' Only')  # Ugh
        check_amount_in_words = check_amount_in_words.replace('Cent', ' Only')
        decimals = amount % 1
        # if decimals >= 10**-2:
        # 	check_amount_in_words += _(' and %s/100') % str(int(round(float_round(decimals*100, precision_rounding=1))))
        return check_amount_in_words

    @api.onchange('account_id')
    def OnchangeAccount(self):
        for x in self:
            x.tax_id = self.account_id.tax_ids

# ==================================================
# Class : BiAccountCreditLine
# Description : Account Credit Line
# ==================================================
class BiAccountVoucherCreditLine(models.Model):
    _name = "bi.account.voucher.credit.line"
    _description = "Account Credit Line"

    @api.depends('amount', 'tax_id')
    def _compute_amount(self):
        for line in self:
            taxes = line.tax_id.compute_all(line.amount, line.currency_id, 1, product=False, partner=False)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    credit_id = fields.Many2one('bi.account.payment', string="Receipt")
    analytic_account_id = fields.Many2one('account.analytic.account', "Analytic Account")
    tax_id = fields.Many2many('account.tax', string='Taxes',
                              domain=['|', ('active', '=', False), ('active', '=', True)])
    account_id = fields.Many2one('account.account', domain=[], string="Account ID", required=True)
    name = fields.Char(string="Description", required=True)
    amount = fields.Float(string="Amount", required=True)
    currency_id = fields.Many2one('res.currency', related='credit_id.currency_id', store=True, related_sudo=False)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    price_tax = fields.Monetary(compute='_compute_amount', string='Tax', store=True)


# ==================================================
# Class : BiAccountPaymentLine
# Description : Account Payment Line
# ==================================================
class BiAccountVoucherPaymentLine(models.Model):
    _name = "bi.account.voucher.payment.line"
    _description = "Account Payment Line"

    @api.depends('amount', 'tax_id')
    def _compute_amount(self):
        for line in self:
            taxes = line.tax_id.compute_all(line.amount, line.currency_id, 1, product=False, partner=False)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    receipt_id = fields.Many2one('bi.account.payment', string="Receipt")
    analytic_account_id = fields.Many2one('account.analytic.account', "Analytic Account")
    tax_id = fields.Many2many('account.tax', string='Taxes',
                              domain=['|', ('active', '=', False), ('active', '=', True)])
    account_id = fields.Many2one('account.account', domain=[], string="Account ID", required=True)
    name = fields.Char(string="Description", required=True)
    amount = fields.Float(string="Amount", required=True)
    currency_id = fields.Many2one('res.currency', related='receipt_id.currency_id', store=True, related_sudo=False)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    price_tax = fields.Monetary(compute='_compute_amount', string='Tax', store=True)
    #credit_or_debit = fields.Selection([('credit', 'Credit'), ('debit', 'Debit')], string='Credit/Debit')


class account_payment(models.Model):
    _inherit = "account.payment"

    @api.multi
    def print_checks(self):
        """ Check that the recordset is valid, set the payments state to sent and call print_checks() """
        # Since this method can be called via a client_action_multi, we need to make sure the received records are what we expect
        self = self.filtered(lambda r: r.payment_method_id.code == 'check_printing' and r.state != 'reconciled')

        if len(self) == 0:
            raise UserError(_("Payments to print as a checks must have 'Check' selected as payment method and "
                              "not have already been reconciled"))
        if any(payment.journal_id != self[0].journal_id for payment in self):
            raise UserError(_("In order to print multiple checks at once, they must belong to the same bank journal."))

        if not self[0].journal_id.check_manual_sequencing:
            # The wizard asks for the number printed on the first pre-printed check
            # so payments are attributed the number of the check the'll be printed on.
            list_check_number = []
            # The wizard asks for the number printed on the first pre-printed check
            # so payments are attributed the number of the check the'll be printed on.
            last_printed_check = self.search([
                ('journal_id', '=', self[0].journal_id.id),
                ('check_number', '!=', 0)], order="check_number desc", limit=1)
            list_check_number.append(last_printed_check.check_number or 1)
            #last_printed_check_for_bi_acc_receipt = self.env['bi.account.receipt'].search([
            #    ('journal_id', '=', self[0].journal_id.id),
            #    ('check_number', '!=', 0)], order="check_number desc", limit=1)
            #list_check_number.append(last_printed_check_for_bi_acc_receipt.check_number or 1)
            last_printed_check_for_bi_acc_payment = self.env['bi.account.payment'].search([
                ('journal_id', '=', self[0].journal_id.id),
                ('check_number', '!=', 0)], order="check_number desc", limit=1)
            list_check_number.append(last_printed_check_for_bi_acc_payment.check_number or 1)
            max_check_number = max(list_check_number)
            next_check_number = max_check_number + 1 if max_check_number else 1
            return {
                'name': _('Print Pre-numbered Checks'),
                'type': 'ir.actions.act_window',
                'res_model': 'print.prenumbered.checks',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'payment_ids': self.ids,
                    'default_next_check_number': next_check_number,
                }
            }
        else:
            self.filtered(lambda r: r.state == 'draft').post()
            return self.do_print_checks()
