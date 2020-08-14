from odoo import fields,models,api
from lxml import etree


class attach_documents_wizard(models.TransientModel):
    ''' Fax In Attachments to be attached to Event or Partner '''
    _name = 'attach.documents.wizard'

    attach_to=fields.Selection([('event','Event'),('partner','Partner')],'Attach To',default='event')
    doc_type=fields.Selection([('fee_note','Fee Note'),('saf','SAF')],'Doc Type')
    partner_id=fields.Many2one('res.partner','Partner')
    event_id=fields.Many2one('event','Event')
    company_id=fields.Many2one('res.company', 'Company',default=lambda self: self.env['res.company']._company_default_get('attach.documents.wizard'))
    mail_message_id=fields.Many2one('mail.message','Mail Message')

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        '''Function overridden to put domain on event_id field based on dates and authorisation '''
        res = super(attach_documents_wizard, self).fields_view_get(view_id, view_type, toolbar, submenu)
        company_id = self._context.get('company_id', False)
        attach_to = self._context.get('attach_to', False)
        if attach_to and attach_to == 'event':
            event_ids = []
            if company_id:
                event_ids = self.env['event'].search([('event_start_date','>=','2015-01-01'),('company_id','=',company_id),('state','not in',('done','cancel','unbilled','invoiced'))])
            else:
                event_ids = self.env['event'].search([('event_start_date','>=','2015-01-01'),('state','not in',('done','cancel','unbilled','invoiced'))])
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='event_id']"):
                if event_ids:
                    node.set('domain', "[('id', 'in', %s)]" %(event_ids))
            res['arch'] = etree.tostring(doc)
        return res

    @api.multi
    def attach_documents(self):
       ''' Function to attach incoming Documents to any event or Partner '''
       ir_attachment = self.env['ir.attachment']
       mail_message = self.env['mail.message']
       if not self.mail_message_id:
           return True
       message_obj = mail_message.browse(self.mail_message_id.id)
       for cur in self:
           if cur.attach_to == 'event' and cur.event_id:
               for attach in message_obj.fax_attachment_ids:
                   if attach.attach:
                       attachment_data = {
                           'name': attach.name,
                           'datas_fname': attach.datas_fname,
                           'datas': attach.datas,
                           'document_type_id': attach.doc_type_id and attach.doc_type_id.id or False,
                           'res_model':'event',
                           'res_id':cur.event_id.id,
                           'res_name':cur.event_id.name
                       }
                       ir_attachment.create(attachment_data)
           elif cur.attach_to == 'partner' and cur.partner_id:
               for attach in message_obj.fax_attachment_ids:
                   if attach.attach:
                       attachment_data = {
                           'name': attach.name,
                           'datas_fname': attach.datas_fname,
                           'datas': attach.datas,
                           'document_type_id': attach.doc_type_id and attach.doc_type_id.id or False,
                           'res_model':'res.partner',
                           'res_id':cur.partner_id.id,
                           'res_name':cur.partner_id.name,
                       }
                       ir_attachment.create(attachment_data)
           if cur.doc_type and cur.doc_type == 'fee_note':
               cur.event_id.write({'fee_note_test':True})
           elif cur.doc_type and cur.doc_type == 'saf':
               cur.event_id.write({'order_note_test':True})
       return True

    @api.onchange('company_id')
    def onchange_company_id(self):
        val={
            'partner_id': False,
            'event_id': False,
            }
        return {'value': val}