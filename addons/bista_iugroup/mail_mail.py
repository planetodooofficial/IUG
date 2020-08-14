
import datetime
import base64
import re
from odoo import tools
from odoo import SUPERUSER_ID
from odoo import fields,models,sql_db,api,_
import logging
_logger = logging.getLogger(__name__)

class mail_mail(models.Model):
    ''' Custom Field added to recognize Mail Type'''
    _inherit = "mail.mail"

    @api.depends('date')
    def _get_year(self):
        """ get year from date """
        for mail in self:
            DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            from_dt = datetime.datetime.strptime(str(mail.date), DATETIME_FORMAT)
            tm_tuple = from_dt.timetuple()
            year = tm_tuple.tm_year
            mail.year = year

    custom_type=fields.Selection([('fax','Fax'),('other','Other')],'Type',default='other')
    year=fields.Char(compute='_get_year', string='Year' , store=True)
    author_user_id=fields.Many2one('res.users', 'Sent By', index=1, ondelete='set null',
                            help="Author of the message .",default=lambda self: self.env.user.id)
    events=fields.Char(string='Events',default=False)

    
#    def send_get_email_dict(self, cr, uid, mail, partner=None, context=None):
#        """ Return a dictionary for specific email values, depending on a
#            partner, or generic to the whole recipients given by mail.email_to.
#
#            :param browse_record mail: mail.mail browse_record
#            :param browse_record partner: specific recipient partner
#        """
#        body = self.send_get_mail_body(cr, uid, mail, partner=partner, context=context)
#        subject = self.send_get_mail_subject(cr, uid, mail, partner=partner, context=context)
#        reply_to = self.send_get_mail_reply_to(cr, uid, mail, partner=partner, context=context)
#        body_alternative = tools.html2plaintext(body)
#
#        # generate email_to, heuristic:
#        # 1. if 'partner' is specified and there is a related document: Followers of 'Doc' <email>
#        # 2. if 'partner' is specified, but no related document: Partner Name <email>
#        # 3; fallback on mail.email_to that we split to have an email addresses list
#        if partner and mail.record_name:
#            sanitized_record_name = re.sub(r'[^\w+.]+', '-', mail.record_name)
#            email_to = [_('%s') % ( partner.email)]
#        elif partner:
#            email_to = ['%s' % ( partner.email)]
#        else:
#            email_to = tools.email_split(mail.email_to)
#
#        return {
#            'body': body,
#            'body_alternative': body_alternative,
#            'subject': subject,
#            'email_to': email_to,
#            'reply_to': reply_to,
#        }

    @api.multi
    def send_get_mail_body(self,partner=None):
        """ add a signin link inside the body of a mail.mail
            :param mail: mail.mail browse_record
            :param partner: browse_record of the specific recipient partner
            :return: the resulting body_html
        """
        partner_obj = self.env['res.partner']
        body = self.body_html
        if partner:
            self = self.with_context(signup_valid=True)
            partner = partner_obj.sudo().browse(partner.id)
            text = _("""<p>Access your messages and personal documents through <a href="%s">our Customer Portal</a></p>""") % partner.signup_url
            # partner is an user: add a link to the document if read access
            if partner.user_ids and self.model and self.res_id \
                    and self.check_access_rights('read', raise_exception=False):
                related_user = partner.user_ids[0]
                try:
                    self.env[self.model].check_access_rule('read')
                    if 'Your timesheet is pending' in body:
                        url=partner.with_context(signup_valid=True)._get_signup_url_for_action(
                            action='bista_iugroup.action_event_user_form_timesheet_language',
                            res_id=self.res_id, view_type='form',
                            model=self.model)[partner.id]
                    else:
                        url = partner.with_context(signup_valid=True)._get_signup_url_for_action(
                            action='',
                            res_id=self.res_id, view_type='form',
                            model=self.model)[partner.id]
                    text = _("""<p>Access this document <a href="%s">directly in IUX</a></p>""") % url
                except Exception, e:
                    pass
            body = tools.append_content_to_html(body, ("<div><p>%s</p></div>" % text), plaintext=False)
        return body
    
#     def send(self, cr, uid, ids, auto_commit=False, recipient_ids=None, context=None):
#         """ Function to send mail to the recipients   """
#         res = False
#         for mail in self.browse(cr, uid, ids, context=context):
# #            print "mail.recipient_ids.......",mail.partner_ids
#             recp_ids = [part.id for part in mail.partner_ids]
#             res = super(mail_mail, self).send(cr , uid, ids, auto_commit=False, recipient_ids=recp_ids, context=context)
#         return res
    
#    def _postprocess_sent_message(self, cr, uid, mail, context=None):
#        """Perform any post-processing necessary after sending ``mail``
#        successfully, including deleting it completely along with its
#        attachment if the ``auto_delete`` flag of the mail was set.
#        Overridden by subclasses for extra post-processing behaviors.
#
#        :param browse_record mail: the mail that was just sent
#        :return: True
#        """
##        if mail.auto_delete:
##            # done with SUPERUSER_ID to avoid giving large unlink access rights
##            self.unlink(cr, SUPERUSER_ID, [mail.id], context=context)
#        return True
    
class mail_template(models.Model):
    ''' Custom Field added to recognize Mail Type'''
    _inherit = "mail.template"


    @api.multi
    def send_mail(self, res_id, force_send=False, raise_exception=False, email_values=None):
        """Generates a new mail message for the given template and record,
           and schedules it for delivery through the ``mail`` module's scheduler.

           :param int res_id: id of the record to render the template with
                              (model is taken from the template)
           :param bool force_send: if True, the generated mail.message is
                immediately sent after being created, as if the scheduler
                was executed for this message only.
           :param dict email_values: if set, the generated mail.message is
                updated with given values dict
           :returns: id of the mail.message that was created
        """
        self.ensure_one()
        Mail = self.env['mail.mail']
        Attachment = self.env['ir.attachment']  # TDE FIXME: should remove dfeault_type from context

        # create a mail_mail based on values, without attachments
        values = self.generate_email(res_id)
        values['recipient_ids'] = [(4, pid) for pid in values.get('partner_ids', list())]
        values.update(email_values or {})
        attachment_ids = values.pop('attachment_ids', [])
        attachments = values.pop('attachments', [])
        # add a protection against void email_from
        if 'email_from' in values and not values.get('email_from'):
            values.pop('email_from')
        values['state']=False
        mail = Mail.create(values)

        # manage attachments
        for attachment in attachments:
            attachment_data = {
                'name': attachment[0],
                'datas_fname': attachment[0],
                'datas': attachment[1],
                'type': 'binary',
                'res_model': 'mail.message',
                'res_id': mail.mail_message_id.id,
            }
            attachment_ids.append(Attachment.create(attachment_data).id)
        if attachment_ids:
            values['attachment_ids'] = [(6, 0, attachment_ids)]
            mail.write({'attachment_ids': [(6, 0, attachment_ids)]})

        if force_send:
            mail.send(raise_exception=raise_exception)
        return mail.id  # TDE CLEANME: return mail + api.returns ?


    @api.multi
    def cancel_send_mail(self, res_id, force_send=False, raise_exception=False, email_values=None):
        """Generates a new mail message for the given template and record,
           and schedules it for delivery through the ``mail`` module's scheduler.

           :param int res_id: id of the record to render the template with
                              (model is taken from the template)
           :param bool force_send: if True, the generated mail.message is
                immediately sent after being created, as if the scheduler
                was executed for this message only.
           :param dict email_values: if set, the generated mail.message is
                updated with given values dict
           :returns: id of the mail.message that was created
        """
        _logger.info('i am in cancell_send_mail()+++++++++++--------------')
        self.ensure_one()
        Mail = self.env['mail.mail']
        Attachment = self.env['ir.attachment']  # TDE FIXME: should remove dfeault_type from context

        # create a mail_mail based on values, without attachments
        values = self.generate_email(res_id)
        _logger.info('i am in cancell_send_mail() context++++++++++++%s--------------',self._context)
        recipient_ids=self._context.get('recipient_ids')
        values['recipient_ids']=recipient_ids
    
        _logger.info('i am in cancell_send_mail value ()++++++++++++%s--------------',values)

        # values['recipient_ids'] = [(4, pid) for pid in values.get('partner_ids', list())]

        values.update(email_values or {})
        attachment_ids = values.pop('attachment_ids', [])
        attachments = values.pop('attachments', [])
        # add a protection against void email_from
        if 'email_from' in values and not values.get('email_from'):
            values.pop('email_from')
        values['state'] = False
        values['email_to']=recipient_ids
        mail = Mail.create(values)
        _logger.info('i am in cancell_send_mail mail ()++++++++++++%s--------------',mail)
        # manage attachments
        for attachment in attachments:
            attachment_data = {
                'name': attachment[0],
                'datas_fname': attachment[0],
                'datas': attachment[1],
                'type': 'binary',
                'res_model': 'mail.message',
                'res_id': mail.mail_message_id.id,
            }
            attachment_ids.append(Attachment.create(attachment_data).id)
        if attachment_ids:
            values['attachment_ids'] = [(6, 0, attachment_ids)]
            mail.write({'attachment_ids': [(6, 0, attachment_ids)]})

        if force_send:
            mail.send(raise_exception=raise_exception)
        return mail.id  # TDE CLEANME: return mail + api.returns ?
