from openerp.osv import fields, osv
from openerp.tools.translate import _
import datetime
import openerp.tools as tools

class process_voucher(osv.osv_memory):
    _name='process.voucher'
    
    def default_get(self, cr, uid, fields, context=None):
        res = {}
        res = super(process_voucher, self).default_get(cr, uid, fields, context=context)
        active_ids = context.get('active_ids',False)
        if isinstance(active_ids, (int,long)): active_ids = [active_ids]
#        voucher_obj = self.pool.get('account.voucher')
#        for voucher_brw in voucher_obj.browse(cr, uid, context['active_ids']):
#            if voucher_brw.type != 'posted':
#                raise osv.except_osv(_('Warning !!'), _('One of the voucher is not posted!'))
            
        return res
    
    def complete_unreconcile(self, cr, uid, ids, context):
        ''' Function to Complete Unreconcile all selected Posted vouchers '''
        voucher_obj = self.pool.get('account.voucher')
        active_ids = context.get('active_ids',False)
        if not active_ids:
            return True
        for voucher in voucher_obj.browse(cr, uid, active_ids):
            if voucher.state == 'posted':
                voucher.cancel_voucher(context=context)
                voucher.action_cancel_draft(context=context)
            elif voucher.state == 'cancel':
#                voucher.cancel_voucher(context=context)
                voucher.action_cancel_draft(context=context)
            
        res = {
            'domain': str([('id','in',active_ids)]),
            'name': 'Payments',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.voucher',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
        return res
    
    def cancel_voucher(self, cr, uid, ids, context):
        ''' Function to Cancel all selected vouchers '''
        voucher_obj = self.pool.get('account.voucher')
        active_ids = context.get('active_ids',False)
        if not active_ids:
            return True
        for voucher in voucher_obj.browse(cr, uid, active_ids):
            if voucher.state == 'posted':
                voucher.cancel_voucher(context=context)
        res = {
            'domain': str([('id','in',active_ids)]),
            'name': 'Payments',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.voucher',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
        return res
    
    def reset_to_draft(self, cr, uid, ids, context):
        ''' Function to Set to Draft all selected cancel vouchers '''
        voucher_obj = self.pool.get('account.voucher')
        active_ids = context.get('active_ids',False)
        if not active_ids:
            return True
        for voucher in voucher_obj.browse(cr, uid, active_ids):
            if voucher.state == 'cancel':
                voucher.action_cancel_draft(context=context)
        res = {
            'domain': str([('id','in',active_ids)]),
            'name': 'Payments',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.voucher',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
        return res
    
process_voucher()

