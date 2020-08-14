from odoo import models, fields,api
from odoo import netsvc

class update_invoice(models.TransientModel):
    """ Update Invoices for various status as mailed, printed, """
    _name = "update.invoice"
    _description = "Update Invoices"

    @api.multi
    def mark_as_printed(self):
        ''' For Marking selected Invoices '''
        inv_obj = self.env['account.invoice']
#        for cur_obj in self.browse(cr, uid, ids):
        if self._context.get('active_ids',[]):
            for invoice in inv_obj.browse(self._context['active_ids']):
                invoice.write({'is_printed': True})
        return True

    @api.multi
    def validate_invoices(self):
        ''' For Validating selected Invoices '''
        inv_obj = self.env['account.invoice']
        if self._context.get('active_ids',[]):
            for invoice in inv_obj.browse(self._context['active_ids']):
                if invoice.state == 'draft':
                    invoice.action_invoice_open()
        return True

    @api.multi
    def reset_to_draft(self):
        ''' For reset to draft selected open Invoices '''
        inv_obj = self.env['account.invoice']
        if self._context.get('active_ids',[]):
            for invoice in inv_obj.browse(self._context['active_ids']):
                if invoice.state == 'open':
                    invoice.reset_to_draft_iu()
        return True

