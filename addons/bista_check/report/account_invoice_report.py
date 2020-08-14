import time
from odoo.report import report_sxw
from odoo import models
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError, RedirectWarning, ValidationError

class sale_invoice_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(sale_invoice_report, self).__init__(cr, uid, name, context=context)
        active_model = self._context.get('active_model',False)
        active_ids = self._context.get('active_ids',False)
        if active_ids:
            actives = self.env[active_model].browse(active_ids)
            for active in actives:
                if active.type == 'in_invoice':
                    raise UserError(('You cannot generate customer invoice report in supplier invoice'))
        self.localcontext.update({
            'time': time,
            'total_qty':self.total_qty,
            'get_lot':self.get_lot,
            'total_weight':self.total_weight,
            'get_address':self._get_address,
	    'get_line_item_notes':self.get_line_item_notes,
            'get_order_level_notes':self.get_order_level_notes,
        })

    def _get_address(self,invoice_obj):
        address = ""
        for company_brw in invoice_obj.company_id:
            if company_brw.street != False:
                street = company_brw.street
            else:
                street = ""
            if company_brw.street2 != False:
                street2 = company_brw.street2
            else:
                street2 = ""
            if company_brw.city != False:
                city = company_brw.city
            else:
                city = ""
            if company_brw.state_id.code != None:
                state = company_brw.state_id.code
            else:
                state = ""
            if company_brw.zip != False:
                zip = company_brw.zip
            else:
                zip = ""
            address = street + ',' + street2 + ',' + city + ',' + state + ' ' + zip
        new_address = address.replace(',,',',')
        new_address = new_address.replace(',,,',',')
        new_address = new_address.replace(',,,,','')
        return new_address

    def total_qty(self,o):
        final_qty=0.0
        for line in o.invoice_line_ids:
            final_qty = line.quantity + final_qty
        final_qty=str(final_qty)[-2:] == '.0' and str(final_qty)[:-2] or str(final_qty)
        return final_qty

    def get_lot(self,o,product_id):
        picking_obj = self.env['stock.picking']
        lot_details = ""
        if o.sale_invoice_id.id:
            search_picking = picking_obj.search([('sale_id','=',o.sale_invoice_id.id)])
            for picking_brw in search_picking:
                for each_move in picking_brw.move_lines:
                    for each_lot in each_move.move_lot_ids:
                        if each_lot.lot_id.product_id.id == product_id:
                            lot_details += str(each_lot.lot_id.name)+":-"+str(each_lot.quantity)+"\n"
        return lot_details

    def total_weight(self,o):
        all_weight=[]
        final_weight=0.0
        for line in o.invoice_line_ids:
            product_weight=line.product_id.weight
            total_product_weight=line.quantity * product_weight
            final_weight +=total_product_weight
        return final_weight

    def get_line_item_notes(self,line):
        desc ,sale_order_line= '',self.env['sale.order.line']
        if line.saleline_invoice_id:
            sale_order_line_brw = sale_order_line.browse(self.cr,self.uid,line.saleline_invoice_id)
            for line_item_note in sale_order_line_brw.line_item_note_ids:
                if line_item_note.invoice_note == True:
                    desc +=line_item_note.line_item_note
        return desc

    def get_order_level_notes(self,invoice):
        desc = ''
        if invoice.sale_invoice_id.id:
            if invoice.sale_invoice_id.order_level_notes_ids:
                for order_level_note in invoice.sale_invoice_id.order_level_notes_ids:
                    if order_level_note.order_invoice_note == True:
                        desc +=order_level_note.order_item_note
        return desc

report_sxw.report_sxw(
    'report.sale.invoice.customer',
    'account.invoice',
    'custom_addons/bista_check/report/account_invoice_report.rml',
    parser=sale_invoice_report,header=False
)
