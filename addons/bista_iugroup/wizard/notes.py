from odoo import fields,models,api
from odoo.tools.translate import _
from odoo.exceptions import UserError

class event_notes(models.TransientModel):
    _name='event.notes'

    event_fee_note=fields.Binary('Event Fee Note')
    event_order_note=fields.Binary('SAF')
    name=fields.Char('Attachment Name', size=64)
    company_id=fields.Many2one("res.company", "Company" )
    document_type_id=fields.Many2one('document.type','Document Action')

    @api.model
    def default_get(self, fields):
        res, document_type_ids, type = {}, [], False
        res = super(event_notes , self).default_get(fields)
        event_ids = self._context.get('active_ids', [])
        if not event_ids or len(event_ids) != 1:
            return res
        event_id, = event_ids
        event = self.env['event'].browse(event_id)
        if 'company_id' in fields:
            res.update(company_id = event.company_id and event.company_id.id or False)
        if 'document_type_id' in fields:
            if self._context.get('order_note1',False):
                type = 'Pre-SAF'
            if self._context.get('fee_note1',False):
                type = 'Fee Note'
            if type:
                if event.company_id:
                    document_type_ids = self.env['document.type'].search([('name','=',type),('company_id','=', event.company_id.id )]).ids
                else:
                    document_type_ids = self.env['document.type'].search([('name','=',type)]).ids
            if document_type_ids:
                res.update(document_type_id = document_type_ids[0])
        return res

    @api.multi
    def upload_notes(self):
        event_obj = self.env['event']
        obj = self
        active_id = self._context.get('active_id')
        result, file_name = False, 'Attachment'
        if obj.event_fee_note:
            result = obj.event_fee_note
            file_name = 'Fee Note'
            event_obj.browse(active_id).write({'fee_note_test':True})
        if obj.event_order_note:
            result = obj.event_order_note
            file_name='Order Note'
            event_obj.browse(active_id).write({'order_note_test':True})
        if not result:
            raise UserError(_('You must Upload the Notes'))
        
        return self.env['ir.attachment'].create({
                'name': obj.name or file_name,
                'datas': result,
                'datas_fname': obj.name or file_name,
                'document_type_id': obj.document_type_id and obj.document_type_id.id or False,
                'res_model': self._context.get('active_model'),
                'res_id': self._context.get('active_ids')[0]})
    

