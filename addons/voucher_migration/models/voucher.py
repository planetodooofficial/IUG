from odoo import api,models,fields,_

class Voucher(models.Model):

    _name = 'mi.account.voucher'

    old_id = fields.Integer()
    name = fields.Char('Partner')
    journal = fields.Char('Journal')
    ref = fields.Char('Ref #')
    date = fields.Date('Date')
    type = fields.Selection([
        ('payment', 'Payment'),
        ('receipt', 'Receipt'),
        ('sale', 'Sale'),
        ('purchase', 'Purchase'),
    ],'Type')
    number = fields.Char('Number')
    move_id = fields.Many2one('account.move','Move')
    period = fields.Char('Period')
    old_move = fields.Integer()
    memo = fields.Char('Memo')
    check_no = fields.Char('Check No')
    line_ids = fields.One2many('mi.account.voucher.line','voucher_id')
    company_id=fields.Many2one('res.company','Company Id')
    total=fields.Float('Total')


class VoucherLine(models.Model):

    _name = 'mi.account.voucher.line'

    name = fields.Char('Name')
    account= fields.Char('Account')
    amount = fields.Integer('Amount')
    amount_total = fields.Float('Amount')
    type = fields.Selection([
        ('dr', 'Debit'),
        ('cr', 'Credit'),
    ], 'Type')
    old_voucher= fields.Integer()
    voucher_id = fields.Many2one('mi.account.voucher')
    ref=fields.Char('Event')


