import base64
import logging
from openerp import netsvc
from openerp.osv import osv, fields
from openerp.osv import fields
from openerp import tools
from openerp.tools.translate import _
from urllib import urlencode, quote as quote

_logger = logging.getLogger(__name__)

class email_template(osv.osv):
    '''Templates for sending email '''
    _inherit = "email.template"
    
#     def send_mail_custom(self, cr, uid, template_id, res_id, force_send=False, obj=False, context=None):
#         """ Custom Function to  Generates a new mail message (For Fax) for the given template and record,
#            and schedules it for delivery through the ``mail`` module's scheduler.
#
#            :param int template_id: id of the template to render
#            :param int res_id: id of the record to render the template with
#                               (model is taken from the template)
#            :param bool force_send: if True, the generated mail.message is
#                 immediately sent after being created, as if the scheduler
#                 was executed for this message only.
#            :returns: id of the mail.message that was created
#         """
#         if context is None:
#             context = {}
#         mail_mail = self.pool.get('mail.mail')
#         ir_attachment = self.pool.get('ir.attachment')
#
#         # create a mail_mail based on values, without attachments
#         values = self.generate_email(cr, uid, template_id, res_id, context=context)
#         if not values.get('email_from'):
#             raise osv.except_osv(_('Warning!'),_("Sender email is missing or empty after template rendering. Specify one to deliver your message"))
#         # process email_recipients field that is a comma separated list of partner_ids -> recipient_ids
#         # NOTE: only usable if force_send is True, because otherwise the value is
#         # not stored on the mail_mail, and therefore lost -> fixed in v8
#         recipient_ids = []
#         email_recipients = values.pop('email_recipients', '')
#         if email_recipients:
#             for partner_id in email_recipients.split(','):
#                 if partner_id:  # placeholders could generate '', 3, 2 due to some empty field values
#                     recipient_ids.append(int(partner_id))
#
#         attachment_ids = []
# #        attachments = values.pop('attachments', [])
#         msg_id = mail_mail.create(cr, uid, values, context=context)
#         mail = mail_mail.browse(cr, uid, msg_id, context=context)
#
#
# #        # manage attachments
#         if obj:
#            for attachment in obj.send_attachment_ids:
#                 attachment_data = {
#                     'name': attachment.name,
#                     'datas_fname': attachment.name,
#                     'datas': attachment.datas,
#                     'res_model': 'mail.message',
#                     'res_id': mail.mail_message_id.id,
#                 }
#                 attachment_ids.append(ir_attachment.create(cr, uid, attachment_data, context=context))
#         #print "attachment_ids.......",attachment_ids
#         if attachment_ids:
#             values['attachment_ids'] = [(6, 0, attachment_ids)]
#             mail_mail.write(cr, uid, [msg_id], {'attachment_ids': [(6, 0, attachment_ids)]}, context=context)
#         mail_mail.write(cr, uid, [msg_id], {'custom_type': 'fax'}, context=context)
#         if force_send:
#             mail_mail.send(cr, uid, [msg_id], recipient_ids=recipient_ids, context=context)
#         return msg_id

    def send_mail(self,res_id, force_send=True, raise_exception=False, email_values=None):
        """Generates a new mail message for the given template and record,
           and schedules it for delivery through the ``mail`` module's scheduler.
           
           :param int template_id: id of the template to render
           :param int res_id: id of the record to render the template with
                              (model is taken from the template)
           :param bool force_send: if True, the generated mail.message is
                immediately sent after being created, as if the scheduler
                was executed for this message only.
           :returns: id of the mail.message that was created
        """
        self.ensure_one()
        Mail = self.env['mail.mail']
        Attachment = self.env['ir.attachment']  # TDE FIXME: should remove dfeault_type from context

        # create a mail_mail based on values, without attachments
        values = self.generate_email(cr, uid, template_id, res_id, context=context)
        if not values.get('email_from'):
            raise osv.except_osv(_('Warning!'),_("Sender email is missing or empty after template rendering. Specify one to deliver your message"))
        # process email_recipients field that is a comma separated list of partner_ids -> recipient_ids
        # NOTE: only usable if force_send is True, because otherwise the value is
        # not stored on the mail_mail, and therefore lost -> fixed in v8
        recipient_ids = []
        email_recipients = values.pop('email_recipients', '')
        if email_recipients:
            for partner_id in email_recipients.split(','):
                if partner_id:  # placeholders could generate '', 3, 2 due to some empty field values
                    recipient_ids.append(int(partner_id))
###########Commented while doing change for 2 interpreters, sonu checking on this###############
#        if context.get('interpreter_id',False):
#            recp_id=context.get('interpreter_id').id
#            recipient_ids.append(recp_id)
#        if context.get('email_to'):

        attachment_ids = values.pop('attachment_ids', [])
        attachments = values.pop('attachments', [])
        msg_id = mail_mail.create(cr, uid, values, context=context)
        mail = mail_mail.browse(cr, uid, msg_id, context=context)

        # manage attachments
        for attachment in attachments:
            attachment_data = {
                'name': attachment[0],
                'datas_fname': attachment[0],
                'datas': attachment[1],
                'res_model': 'mail.message',
                'res_id': mail.mail_message_id.id,
            }
            context.pop('default_type', None)
            attachment_ids.append(ir_attachment.create(cr, uid, attachment_data, context=context))
        if attachment_ids:
            values['attachment_ids'] = [(6, 0, attachment_ids)]
            mail_mail.write(cr, uid, msg_id, {'attachment_ids': [(6, 0, attachment_ids)]}, context=context)

        if force_send:
            mail_mail.send(cr, uid, [msg_id], recipient_ids=recipient_ids, context=context)
        return msg_id

#    def cancel_send_mail(self, res_id, force_send=True, raise_exception=False, email_values=None):
            """Generates a new mail message for the given template and record,
               and schedules it for delivery through the ``mail`` module's scheduler.

               :param int template_id: id of the template to render
               :param int res_id: id of the record to render the template with
                                  (model is taken from the template)
               :param bool force_send: if True, the generated mail.message is
                    immediately sent after being created, as if the scheduler
                    was executed for this message only.
               :returns: id of the mail.message that was created
            """
 #           self.ensure_one()
  #          Mail = self.env['mail.mail']
   #         Attachment = self.env['ir.attachment']  # TDE FIXME: should remove dfeault_type from context

            # create a mail_mail based on values, without attachments
    #      values = self.generate_email(cr, uid, template_id, res_id, context=context)
     #       if not values.get('email_from'):
      #          raise osv.except_osv(_('Warning!'), _(
     #               "Sender email is missing or empty after template rendering. Specify one to deliver your message"))
            # process email_recipients field that is a comma separated list of partner_ids -> recipient_ids
            # NOTE: only usable if force_send is True, because otherwise the value is
            # not stored on the mail_mail, and therefore lost -> fixed in v8
      #      _logger.info('i am in cancell_send_mail() context++++++++++++%s--------------'context)
       #     recipient_ids = []
        #    email_recipients = values.pop('email_recipients', '')
#            _logger.info('i am in cancell_send_mail()++++++++++++%s--------------'email_recipients)
 #           if context.get('recipient_ids'):
  #              recipient_ids.append(context.get('recipient_ids').id)
   #             _logger.info('i am in cancell_send_mail recipent_ids()++++++++++++%s--------------'recipient_ids)

            # if email_recipients:
            #     for partner_id in email_recipients.split(','):
            #         if partner_id:  # placeholders could generate '', 3, 2 due to some empty field values
            #             recipient_ids.append(int(partner_id))
            ###########Commented while doing change for 2 interpreters, sonu checking on this###############
            #        if context.get('interpreter_id',False):
            #            recp_id=context.get('interpreter_id').id
            #            recipient_ids.append(recp_id)
            #        if context.get('email_to'):

    #        attachment_ids = values.pop('attachment_ids', [])
     #       attachments = values.pop('attachments', [])
      #      msg_id = mail_mail.create(cr, uid, values, context=context)
       #     mail = mail_mail.browse(cr, uid, msg_id, context=context)

            # manage attachments
     #       for attachment in attachments:
      #          attachment_data = {
       #             'name': attachment[0],
        #            'datas_fname': attachment[0],
         #           'datas': attachment[1],
       #             'res_model': 'mail.message',
        #            'res_id': mail.mail_message_id.id,
         #       }
          #      context.pop('default_type', None)
           #     attachment_ids.append(ir_attachment.create(cr, uid, attachment_data, context=context))
        #    if attachment_ids:
         #       values['attachment_ids'] = [(6, 0, attachment_ids)]
          #      mail_mail.write(cr, uid, msg_id, {'attachment_ids': [(6, 0, attachment_ids)]}, context=context)

           # if force_send:
            #    mail_mail.send(cr, uid, [msg_id], recipient_ids=recipient_ids, context=context)
           # return msg_id
