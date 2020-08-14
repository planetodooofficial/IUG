from odoo import fields,models,api
from odoo.tools.translate import _
import datetime
from dateutil import relativedelta
from odoo.exceptions import UserError

class upload_attachment_wizard(models.TransientModel):
    ''' Class to upload the attachments with the document Type '''
    _name='upload.attachment.wizard'

    name=fields.Char('Attachment Name', size=64)
    datas=fields.Binary('Attachment')
    company_id=fields.Many2one("res.company", "Company")
    document_type_id=fields.Many2one('document.type','Document Action')

    @api.model
    def default_get(self, fields):
        res, document_type_ids, type = {}, [], False
        res = super(upload_attachment_wizard , self).default_get(fields)
        active_ids = self._context.get('active_ids', [])
        if not active_ids or len(active_ids) != 1:
            return res
        active_id, = active_ids
        obj = self.env[self._context.get('active_model')].browse(active_id)
        if 'company_id' in fields:
            res.update(company_id = obj.company_id and obj.company_id.id or False)
        return res

    @api.multi
    def upload_attachment(self):
        obj = self
#        active_id = context.get('active_id')
        file_name = 'Attachment'
        if not obj.datas:
            raise UserError(_('You must Upload the Attachment!'))
        self=self.with_context(type='binary')
        return self.env['ir.attachment'].create({
            'name': obj.name or file_name,
            'datas': obj.datas,
            'datas_fname': obj.name or file_name,
            'document_type_id': obj.document_type_id and obj.document_type_id.id or False,
            'res_model': self._context.get('active_model'),
            'res_id': self._context.get('active_ids')[0]})
    

