# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2004-2012 OpenERP S.A. (<http://openerp.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time
import datetime
import re

from odoo import models, fields,api


#class account_tax(osv.osv):
#    '''Inherited for the purpose of tax calculation on  invoice line for mileage'''
#    _inherit="account.tax"
#    _description = 'Tax'
#
#    def _compute(self, cr, uid, taxes, price_unit, quantity, product=None, partner=None, precision=None):
#        print "_compute.account_tax......."
#        """
#        Compute tax values for given PRICE_UNIT, QUANTITY and a buyer/seller ADDRESS_ID.
#
#        RETURN:
#            [ tax ]
#            tax = {'name':'', 'amount':0.0, 'account_collected_id':1, 'account_paid_id':2}
#            one tax for each tax id in IDS and their children
#        """
#        if not precision:
#            precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
#        res = self._unit_compute(cr, uid, taxes, price_unit, product, partner, quantity)
#        total = 0.0
#        for r in res:
#            if r.get('balance',False):
#                r['amount'] = round(r.get('balance', 0.0) * quantity, precision) - total
#            else:
#                r['amount'] = round(r.get('amount', 0.0) * quantity, precision)
#                total += r['amount']
#        return res
#
#    def compute_all(self, cr, uid, taxes, price_unit, quantity, product=None, partner=None, force_excluded=False):
#        print "compute_all..account_tax...taxes......",taxes
#        """
#        :param force_excluded: boolean used to say that we don't want to consider the value of field price_include of
#            tax. It's used in encoding by line where you don't matter if you encoded a tax with that boolean to True or
#            False
#        RETURN: {
#                'total': 0.0,                # Total without taxes
#                'total_included: 0.0,        # Total with taxes
#                'taxes': []                  # List of taxes, see compute for the format
#            }
#        """
#
#        # By default, for each tax, tax amount will first be computed
#        # and rounded at the 'Account' decimal precision for each
#        # PO/SO/invoice line and then these rounded amounts will be
#        # summed, leading to the total amount for that tax. But, if the
#        # company has tax_calculation_rounding_method = round_globally,
#        # we still follow the same method, but we use a much larger
#        # precision when we round the tax amount for each line (we use
#        # the 'Account' decimal precision + 5), and that way it's like
#        # rounding after the sum of the tax amounts of each line
#        precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
#        tax_compute_precision = precision
#        if taxes and taxes[0].company_id.tax_calculation_rounding_method == 'round_globally':
#            tax_compute_precision += 5
#        totalin = totalex = float_round(price_unit * quantity, precision)
#        tin = []
#        tex = []
#        for tax in taxes:
#            if not tax.price_include or force_excluded:
#                tex.append(tax)
#            else:
#                tin.append(tax)
#        tin = self.compute_inv(cr, uid, tin, price_unit, quantity, product=product, partner=partner, precision=tax_compute_precision)
#        for r in tin:
#            totalex -= r.get('amount', 0.0)
#        totlex_qty = 0.0
#        try:
#            totlex_qty = totalex/quantity
#        except:
#            pass
#        tex = self._compute(cr, uid, tex, totlex_qty, quantity, product=product, partner=partner, precision=tax_compute_precision)
#        for r in tex:
#            totalin += r.get('amount', 0.0)
#        return {
#            'total': totalex,
#            'total_included': totalin,
#            'taxes': tin + tex
#        }

class account_invoice_tax(models.Model):
    '''Inherited for the purpose of tax calculation on  invoice line for mileage '''
    _inherit = "account.invoice.tax"
    _description = "Invoice Tax"

    @api.model
    def compute(self, cr, uid, invoice_id, context=None):
        tax_grouped = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
        cur = inv.currency_id
        company_currency = self.pool['res.company'].browse(cr, uid, inv.company_id.id).currency_id.id
        for line in inv.invoice_line:
            for tax in tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, (line.price_subtotal ), 1.0, line.product_id, inv.partner_id)['taxes']:
                val={}
                val['invoice_id'] = inv.id
                val['name'] = tax['name']
                val['amount'] = tax['amount']
                val['manual'] = False
                val['sequence'] = tax['sequence']
                val['base'] = cur_obj.round(cr, uid, cur, tax['price_unit'] * line['quantity'])

                if inv.type in ('out_invoice','in_invoice'):
                    val['base_code_id'] = tax['base_code_id']
                    val['tax_code_id'] = tax['tax_code_id']
                    val['base_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['base'] * tax['base_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                    val['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['amount'] * tax['tax_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                    val['account_id'] = tax['account_collected_id'] or line.account_id.id
                    val['account_analytic_id'] = tax['account_analytic_collected_id']
                else:
                    val['base_code_id'] = tax['ref_base_code_id']
                    val['tax_code_id'] = tax['ref_tax_code_id']
                    val['base_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['base'] * tax['ref_base_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                    val['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['amount'] * tax['ref_tax_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
                    val['account_id'] = tax['account_paid_id'] or line.account_id.id
                    val['account_analytic_id'] = tax['account_analytic_paid_id']

                key = (val['tax_code_id'], val['base_code_id'], val['account_id'], val['account_analytic_id'])
                if not key in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += val['base']
                    tax_grouped[key]['base_amount'] += val['base_amount']
                    tax_grouped[key]['tax_amount'] += val['tax_amount']
#                print "val 1.......",val
#            for tax in tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, (line.mileage_rate* (1-(line.discount or 0.0)/100.0)), line.mileage, line.product_id, inv.partner_id)['taxes']:
#                print "tax........",tax
#                val={}
#                val['invoice_id'] = inv.id
#                val['name'] = tax['name']
#                val['amount'] = tax['amount']
#                val['manual'] = False
#                val['sequence'] = tax['sequence']
#                val['base'] = cur_obj.round(cr, uid, cur, tax['price_unit'] * line['quantity'])
#
#                if inv.type in ('out_invoice','in_invoice'):
#                    val['base_code_id'] = tax['base_code_id']
#                    val['tax_code_id'] = tax['tax_code_id']
#                    val['base_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['base'] * tax['base_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
#                    val['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['amount'] * tax['tax_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
#                    val['account_id'] = tax['account_collected_id'] or line.account_id.id
#                    val['account_analytic_id'] = tax['account_analytic_collected_id']
#                else:
#                    val['base_code_id'] = tax['ref_base_code_id']
#                    val['tax_code_id'] = tax['ref_tax_code_id']
#                    val['base_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['base'] * tax['ref_base_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
#                    val['tax_amount'] = cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, val['amount'] * tax['ref_tax_sign'], context={'date': inv.date_invoice or time.strftime('%Y-%m-%d')}, round=False)
#                    val['account_id'] = tax['account_paid_id'] or line.account_id.id
#                    val['account_analytic_id'] = tax['account_analytic_paid_id']
#
#                key = (val['tax_code_id'], val['base_code_id'], val['account_id'], val['account_analytic_id'])
#                if not key in tax_grouped:
#                    tax_grouped[key] = val
#                else:
#                    tax_grouped[key]['amount'] += val['amount']
#                    tax_grouped[key]['base'] += val['base']
#                    tax_grouped[key]['base_amount'] += val['base_amount']
#                    tax_grouped[key]['tax_amount'] += val['tax_amount']
#                print "val 2.......",val
        for t in tax_grouped.values():
            t['base'] = cur_obj.round(cr, uid, cur, t['base'])
            t['amount'] = cur_obj.round(cr, uid, cur, t['amount'])
            t['base_amount'] = cur_obj.round(cr, uid, cur, t['base_amount'])
            t['tax_amount'] = cur_obj.round(cr, uid, cur, t['tax_amount'])
        return tax_grouped