from odoo import fields,models,api
from odoo.tools.translate import _
import datetime
from dateutil import relativedelta
from odoo.exceptions import UserError

class upload_attachment_wizard_for_customers(models.TransientModel):
    ''' Class to upload the attachments to events for customers '''
    _name='upload.attachment.wizard.for.customers'

    name = fields.Char('Attachment Name', size=64)
    datas = fields.Binary('Attachment')
    company_id = fields.Many2one("res.company", "Company")

    @api.model
    def default_get(self, fields):
        res, document_type_ids, type = {}, [], False
        res = super(upload_attachment_wizard_for_customers, self).default_get(fields)
        active_ids = self._context.get('active_ids', [])
        if not active_ids or len(active_ids) != 1:
            return res
        active_id, = active_ids
        obj = self.env[self._context.get('active_model')].browse(active_id)
        if 'company_id' in fields:
            res.update(company_id=obj.company_id and obj.company_id.id or False)
        return res

    @api.multi
    def upload_attachment(self):
        obj = self
        #        active_id = context.get('active_id')
        file_name = 'Attachment'
        if not obj.datas:
            raise UserError(_('You must Upload the Attachment!'))
        if obj.name:
            if not obj.name.lower().endswith(('.jpg', '.tiff', '.gif', '.bmp', '.png',
                                                                     '.pdf')):
                raise UserError(_('Unsupported File Format.'))
        self = self.with_context(type='binary')
        return self.env['ir.attachment'].create({
            'name': obj.name or file_name,
            'datas': obj.datas,
            'datas_fname': obj.name or file_name,
            'res_model': self._context.get('active_model'),
            'res_id': self._context.get('active_ids')[0]})


