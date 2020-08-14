from odoo import api,fields,models
import xmlrpclib

class Sync_Records(models.Model):
    _name="sync.records"

    @api.model
    def sync_invoice_records(self):
        model_ids=self.env['ir.model'].search([('model','in',['account.invoice','account.invoice.line','account.payment'])]).ids
        recs_to_sync=self.env['auditlog.log'].search([('sync','=',False),('error','=',False),('model_id','in',model_ids)],order='create_date asc')
        if recs_to_sync:
            config_obj = self.env['server.config']
            config_ids = config_obj.search([])
            if not config_ids:
                raise UserError(_('No Active server config found!'))
            config = config_ids[0]
            ip = config.host  # Host
            port = config.port  # Port
            username = config.username  # the userl
            pwd = config.password  # the password of the user
            dbname = config.dbname  # the db name
            sock_common = xmlrpclib.ServerProxy('http://' + ip + ':' + port + '/xmlrpc/common')
            d_uid = sock_common.login(dbname, username, pwd)
            sock = xmlrpclib.ServerProxy('http://' + ip + ':' + port + '/xmlrpc/object')
            for rec in recs_to_sync:
                if rec.method == 'create':
                    if rec.model_id.model == 'account.invoice':
                        try:
                            invoice_rec =self.env['account.invoice'].browse(rec.res_id)
                            if invoice_rec.partner_id:
                                partner_id = invoice_rec.partner_id.customer_record_old_id
                            else:
                                partner_id=False
                            if invoice_rec.sales_representative_id:
                                sales_representative_id=invoice_rec.sales_representative_id.user_old_id
                            else:
                                sales_representative_id=False
                            if invoice_rec.account_id:
                                account_id=invoice_rec.account_id.account_old_id
                            else:
                                account_id=False
                            if invoice_rec.patient_id:
                                patient_id=invoice_rec.patient_id.patient_old_id
                            else:
                                patient_id=False
                            if invoice_rec.company_id:
                                company_id=invoice_rec.company_id.res_company_old_id
                            else:
                                company_id=False
                            if invoice_rec.doctor_id:
                                doctor_id = invoice_rec.doctor_id.doctor_old_id
                            else:
                                doctor_id=False
                            if invoice_rec.ordering_partner_id:
                                ordering_partner_id=invoice_rec.ordering_partner_id.customer_record_old_id
                            else:
                                ordering_partner_id=False
                            if invoice_rec.journal_id:
                                journal_id=invoice_rec.journal_id.account_journal_old_id
                            else:
                                journal_id=False
                            if invoice_rec.location_id:
                                location_id= invoice_rec.location_id.location_old_id
                            else:
                                location_id=False
                            if invoice_rec.event_id:
                                event_id=invoice_rec.event_id.event_old_id
                            else:
                                event_id=False
                            if invoice_rec.ordering_contact_id:
                                ordering_contact_id=invoice_rec.ordering_contact_id.customer_record_old_id
                            else:
                                ordering_contact_id=False
                            if invoice_rec.commercial_partner_id:
                                commercial_partner_id=invoice_rec.commercial_partner_id.customer_record_old_id
                            else:
                                commercial_partner_id=False
                            if invoice_rec.contact_id:
                                contact_id=invoice_rec.contact_id.customer_record_old_id
                            else:
                                contact_id=False
                            if invoice_rec.language_id:
                                language_id=invoice_rec.language_id.language_old_id
                            else:
                                language_id=False
                            if invoice_rec.project_name_id:
                                project_name_id = invoice_rec.project_name_id.iug_project_old_id
                            else:
                                project_name_id=False
                            invoice_vals = {
                                    # 'month':invoice_rec.month,
                                    # 'year':invoice_rec.year,
                                    # 'invoice_old_id': invoice_old_id,
                                    'origin': invoice_rec.origin,
                                    'date_due': invoice_rec.date_due,
                                    'reference': invoice_rec.reference,
                                    'sales_representative_id': sales_representative_id,
                                    # 'invoice_old_number': number,
                                    'account_id': account_id,
                                    # 'invoice_id2': invoice_id2,
                                    'patient_id': patient_id,
                                    'company_id': company_id,
                                    'currency_id': 3,
                                    'partner_id': partner_id,
                                    'doctor_id': doctor_id,
                                    # 'fiscal_position_id': fiscal_position,
                                    'user_id': 1,
                                    'payment_term': invoice_rec.payment_term_id and invoice_rec.payment_term_id.id or False,
                                    'reference_type': invoice_rec.reference_type,
                                    'ordering_partner_id': ordering_partner_id,
                                    # 'period_id': period_id,
                                    'journal_id': journal_id,
                                    'location_id': location_id,
                                    # 'amount_tax': amount_tax,
                                    'type': invoice_rec.type,
                                    'event_id': event_id,
                                    # 'reconciled': invoice_rec.reconciled,
                                    # 'residual': residual,
                                    'move_name': invoice_rec.move_name,
                                    # 'amount_untaxed': amount_untaxed,
                                    'date_invoice': invoice_rec.date_invoice,
                                    # 'amount_total': amount_total,
                                    # 'name': name,
                                    'ordering_contact_id' :ordering_contact_id,
                                    'comment':invoice_rec.comment,
                                    'sent': invoice_rec.sent,
                                    'commercial_partner_id': commercial_partner_id,
                                    'is_printed': invoice_rec.is_printed,
                                    # 'quickbooks_id': quickbooks_id,
                                    'claim_no': invoice_rec.claim_no,
                                    'check_no': invoice_rec.check_no,
                                    'invoice_for': invoice_rec.invoice_for,
                                    'is_emailed': invoice_rec.is_emailed,
                                    'is_mailed': invoice_rec.is_mailed,
                                    'is_faxed': invoice_rec.is_faxed,
                                    'is_monthly': invoice_rec.is_monthly,
                                    'internal_comment': invoice_rec.internal_comment,
                                    # 'invoice_id': invoice_id,
                                    'contact_id': contact_id,
                                    'language_id': language_id,
                                    'project_name_id':project_name_id,
                            }
                            invoice_old_id = sock.execute(dbname, d_uid, pwd, 'account.invoice', 'create', invoice_vals)
                            invoice_rec.write({'invoice_old_id':invoice_old_id})
                            self._cr.commit()
                            for invoice_line_rec in invoice_rec.invoice_line_ids:
                                if invoice_line_rec.company_id:
                                    company_id = invoice_line_rec.company_id.res_company_old_id
                                else:
                                    company_id = False
                                if invoice_line_rec.account_id:
                                    account_id = invoice_line_rec.account_id.account_old_id
                                else:
                                    account_id = False
                                if invoice_line_rec.invoice_id:
                                    invoice_id = invoice_line_rec.invoice_id.invoice_old_id
                                else:
                                    invoice_id = False
                                if invoice_line_rec.partner_id:
                                    partner_id = invoice_line_rec.partner_id.customer_record_old_id
                                else:
                                    partner_id = False
                                if invoice_line_rec.product_id:
                                    product_id = invoice_line_rec.product_id.product_old_id
                                else:
                                    product_id = False
                                if invoice_line_rec.event_out_come_id:
                                    event_out_come_id = invoice_line_rec.event_out_come_id.event_outcome_old_id
                                else:
                                    event_out_come_id = False
                                if invoice_line_rec.task_line_id:
                                    task_line_id = invoice_line_rec.task_line_id.project_task_work_old_id
                                else:
                                    task_line_id = False
                                invoice_line_vals = {
                                    'account_id': account_id,
                                    'name': invoice_line_rec.name,
                                    'sequence': invoice_line_rec.sequence,
                                    'invoice_id': invoice_id,
                                    'price_unit': invoice_line_rec.price_unit,
                                    # 'price_subtotal': invoice_line_rec.price_subtotal,
                                    'company_id': company_id,
                                    'discount': invoice_line_rec.discount,
                                    'quantity': invoice_line_rec.quantity,
                                    'partner_id': partner_id,
                                    'product_id': product_id,
                                    'miscellaneous_bill': invoice_line_rec.miscellaneous_bill,
                                    'miles_driven': invoice_line_rec.miles_driven,
                                    'inc_min': invoice_line_rec.inc_min,
                                    'mileage': invoice_line_rec.mileage,
                                    'mileage_rate': invoice_line_rec.mileage_rate,
                                    'pickup_fee': invoice_line_rec.pickup_fee,
                                    'after_hours': invoice_line_rec.after_hours,
                                    'gratuity': invoice_line_rec.gratuity,
                                    'wait_time': invoice_line_rec.wait_time,
                                    'event_out_come_id': event_out_come_id,
                                    'task_line_id': task_line_id,
                                    'travel_time': invoice_line_rec.travel_time,
                                    'total_editable': invoice_line_rec.total_editable,
                                    'travelling_rate': invoice_line_rec.travelling_rate,
                                }
                                invoice_line_old_id = sock.execute(dbname, d_uid, pwd, 'account.invoice.line', 'create',
                                                                   invoice_line_vals)
                                invoice_line_rec.write({'invoice_line_old_id': invoice_line_old_id})
                            rec.write({'sync':True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model=='account.invoice.line':
                        try:
                            invoice_line_rec = self.env['account.invoice.line'].browse(rec.res_id)
                            invoice_line_rec_exists=sock.execute(dbname, d_uid, pwd, 'account.invoice.line', 'search',
                                                                 [('id', '=',invoice_line_rec.invoice_line_old_id )])
                            if not invoice_line_rec_exists:
                                if invoice_line_rec.company_id:
                                    company_id = invoice_line_rec.company_id.res_company_old_id
                                else:
                                    company_id = False
                                if invoice_line_rec.account_id:
                                    account_id = invoice_line_rec.account_id.account_old_id
                                else:
                                    account_id = False
                                if invoice_line_rec.invoice_id:
                                    invoice_id = invoice_line_rec.invoice_id.invoice_old_id
                                else:
                                    invoice_id = False
                                if invoice_line_rec.partner_id:
                                    partner_id = invoice_line_rec.partner_id.customer_record_old_id
                                else:
                                    partner_id = False
                                if invoice_line_rec.product_id:
                                    product_id = invoice_line_rec.product_id.product_old_id
                                else:
                                    product_id = False
                                if invoice_line_rec.event_out_come_id:
                                    event_out_come_id = invoice_line_rec.event_out_come_id.event_outcome_old_id
                                else:
                                    event_out_come_id = False
                                if invoice_line_rec.task_line_id:
                                    task_line_id = invoice_line_rec.task_line_id.project_task_work_old_id
                                else:
                                    task_line_id = False
                                invoice_line_vals = {
                                    'account_id': account_id,
                                    'name': invoice_line_rec.name,
                                    'sequence': invoice_line_rec.sequence,
                                    'invoice_id': invoice_id,
                                    'price_unit': invoice_line_rec.price_unit,
                                    # 'price_subtotal': invoice_line_rec.price_subtotal,
                                    'company_id': company_id,
                                    'discount': invoice_line_rec.discount,
                                    'quantity': invoice_line_rec.quantity,
                                    'partner_id': partner_id,
                                    'product_id': product_id,
                                    'miscellaneous_bill': invoice_line_rec.miscellaneous_bill,
                                    'miles_driven': invoice_line_rec.miles_driven,
                                    'inc_min': invoice_line_rec.inc_min,
                                    'mileage': invoice_line_rec.mileage,
                                    'mileage_rate': invoice_line_rec.mileage_rate,
                                    'pickup_fee': invoice_line_rec.pickup_fee,
                                    'after_hours': invoice_line_rec.after_hours,
                                    'gratuity': invoice_line_rec.gratuity,
                                    'wait_time': invoice_line_rec.wait_time,
                                    'event_out_come_id': event_out_come_id,
                                    'task_line_id': task_line_id,
                                    'travel_time': invoice_line_rec.travel_time,
                                    'total_editable': invoice_line_rec.total_editable,
                                    'travelling_rate': invoice_line_rec.travelling_rate,
                                }
                                invoice_line_old_id = sock.execute(dbname, d_uid, pwd, 'account.invoice.line', 'create', invoice_line_vals)
                                invoice_line_rec.write({'invoice_line_old_id': invoice_line_old_id})
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error':e})
                            self._cr.commit()
                elif rec.method == 'write':
                    if rec.model_id.model == 'account.invoice':
                        try:
                            invoice_rec =self.env['account.invoice'].browse(rec.res_id)
                            if invoice_rec.partner_id:
                                partner_id = invoice_rec.partner_id.customer_record_old_id
                            else:
                                partner_id=False
                            if invoice_rec.sales_representative_id:
                                sales_representative_id=invoice_rec.sales_representative_id.user_old_id
                            else:
                                sales_representative_id=False
                            if invoice_rec.account_id:
                                account_id=invoice_rec.account_id.account_old_id
                            else:
                                account_id=False
                            if invoice_rec.patient_id:
                                patient_id=invoice_rec.patient_id.patient_old_id
                            else:
                                patient_id=False
                            if invoice_rec.company_id:
                                company_id=invoice_rec.company_id.res_company_old_id
                            else:
                                company_id=False
                            if invoice_rec.doctor_id:
                                doctor_id = invoice_rec.doctor_id.doctor_old_id
                            else:
                                doctor_id=False
                            if invoice_rec.ordering_partner_id:
                                ordering_partner_id=invoice_rec.ordering_partner_id.customer_record_old_id
                            else:
                                ordering_partner_id=False
                            if invoice_rec.journal_id:
                                journal_id=invoice_rec.journal_id.account_journal_old_id
                            else:
                                journal_id=False
                            if invoice_rec.location_id:
                                location_id= invoice_rec.location_id.location_old_id
                            else:
                                location_id=False
                            if invoice_rec.event_id:
                                event_id=invoice_rec.event_id.event_old_id
                            else:
                                event_id=False
                            if invoice_rec.ordering_contact_id:
                                ordering_contact_id=invoice_rec.ordering_contact_id.customer_record_old_id
                            else:
                                ordering_contact_id=False
                            if invoice_rec.commercial_partner_id:
                                commercial_partner_id=invoice_rec.commercial_partner_id.customer_record_old_id
                            else:
                                commercial_partner_id=False
                            if invoice_rec.contact_id:
                                contact_id=invoice_rec.contact_id.customer_record_old_id
                            else:
                                contact_id=False
                            if invoice_rec.language_id:
                                language_id=invoice_rec.language_id.language_old_id
                            else:
                                language_id=False
                            if invoice_rec.project_name_id:
                                project_name_id = invoice_rec.project_name_id.iug_project_old_id
                            else:
                                project_name_id=False
                            invoice_vals = {
                                    # 'month':invoice_rec.month,
                                    # 'year':invoice_rec.year,
                                    # 'invoice_old_id': invoice_old_id,
                                    'origin': invoice_rec.origin,
                                    'date_due': invoice_rec.date_due,
                                    'reference': invoice_rec.reference,
                                    'sales_representative_id': sales_representative_id,
                                    # 'invoice_old_number': number,
                                    'account_id': account_id,
                                    # 'invoice_id2': invoice_id2,
                                    'patient_id': patient_id,
                                    'company_id': company_id,
                                    'currency_id': 3,
                                    'partner_id': partner_id,
                                    'doctor_id': doctor_id,
                                    # 'fiscal_position_id': fiscal_position,
                                    'user_id': 1,
                                    'payment_term': invoice_rec.payment_term_id and invoice_rec.payment_term_id.id or False,
                                    'reference_type': invoice_rec.reference_type,
                                    'ordering_partner_id': ordering_partner_id,
                                    # 'period_id': period_id,
                                    'journal_id': journal_id,
                                    'location_id': location_id,
                                    # 'amount_tax': amount_tax,
                                    'type': invoice_rec.type,
                                    'event_id': event_id,
                                    # 'reconciled': invoice_rec.reconciled,
                                    # 'residual': residual,
                                    'move_name': invoice_rec.move_name,
                                    # 'amount_untaxed': amount_untaxed,
                                    'date_invoice': invoice_rec.date_invoice,
                                    # 'amount_total': amount_total,
                                    # 'name': name,
                                    'ordering_contact_id' :ordering_contact_id,
                                    'comment':invoice_rec.comment,
                                    'sent': invoice_rec.sent,
                                    'commercial_partner_id': commercial_partner_id,
                                    'is_printed': invoice_rec.is_printed,
                                    # 'quickbooks_id': quickbooks_id,
                                    'claim_no': invoice_rec.claim_no,
                                    'check_no': invoice_rec.check_no,
                                    'invoice_for': invoice_rec.invoice_for,
                                    'is_emailed': invoice_rec.is_emailed,
                                    'is_mailed': invoice_rec.is_mailed,
                                    'is_faxed': invoice_rec.is_faxed,
                                    'is_monthly': invoice_rec.is_monthly,
                                    'internal_comment': invoice_rec.internal_comment,
                                    # 'invoice_id': invoice_id,
                                    'contact_id': contact_id,
                                    'language_id': language_id,
                                    'project_name_id':project_name_id,
                            }
                            result = sock.execute(dbname, d_uid, pwd, 'account.invoice', 'write',[invoice_rec.invoice_old_id], invoice_vals)
                            for line in rec.line_ids:
                                if line.field_name=='state':
                                    if line.new_value_text == 'open':
                                        result = sock.execute(dbname, d_uid, pwd, 'account.invoice', 'validate',
                                                              [invoice_rec.invoice_old_id])

                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model=='account.invoice.line':
                        try:
                            invoice_line_rec = self.env['account.invoice.line'].browse(rec.res_id)
                            if invoice_line_rec.company_id:
                                company_id = invoice_line_rec.company_id.res_company_old_id
                            else:
                                company_id = False
                            if invoice_line_rec.account_id:
                                account_id = invoice_line_rec.account_id.account_old_id
                            else:
                                account_id = False
                            if invoice_line_rec.invoice_id:
                                invoice_id = invoice_line_rec.invoice_id.invoice_old_id
                            else:
                                invoice_id = False
                            if invoice_line_rec.partner_id:
                                partner_id = invoice_line_rec.partner_id.customer_record_old_id
                            else:
                                partner_id = False
                            if invoice_line_rec.product_id:
                                product_id = invoice_line_rec.product_id.product_old_id
                            else:
                                product_id = False
                            if invoice_line_rec.event_out_come_id:
                                event_out_come_id = invoice_line_rec.event_out_come_id.event_outcome_old_id
                            else:
                                event_out_come_id = False
                            if invoice_line_rec.task_line_id:
                                task_line_id = invoice_line_rec.task_line_id.project_task_work_old_id
                            else:
                                task_line_id = False
                            invoice_line_vals = {
                                'account_id': account_id,
                                'name': invoice_line_rec.name,
                                'sequence': invoice_line_rec.sequence,
                                'invoice_id': invoice_id,
                                'price_unit': invoice_line_rec.price_unit,
                                # 'price_subtotal': invoice_line_rec.price_subtotal,
                                'company_id': company_id,
                                'discount': invoice_line_rec.discount,
                                'quantity': invoice_line_rec.quantity,
                                'partner_id': partner_id,
                                'product_id': product_id,
                                'miscellaneous_bill': invoice_line_rec.miscellaneous_bill,
                                'miles_driven': invoice_line_rec.miles_driven,
                                'inc_min': invoice_line_rec.inc_min,
                                'mileage': invoice_line_rec.mileage,
                                'mileage_rate': invoice_line_rec.mileage_rate,
                                'pickup_fee': invoice_line_rec.pickup_fee,
                                'after_hours': invoice_line_rec.after_hours,
                                'gratuity': invoice_line_rec.gratuity,
                                'wait_time': invoice_line_rec.wait_time,
                                'event_out_come_id': event_out_come_id,
                                'task_line_id': task_line_id,
                                'travel_time': invoice_line_rec.travel_time,
                                'total_editable': invoice_line_rec.total_editable,
                                'travelling_rate': invoice_line_rec.travelling_rate,
                            }
                            result = sock.execute(dbname, d_uid, pwd, 'account.invoice.line', 'write',
                                                  [invoice_line_rec.invoice_line_old_id], invoice_line_vals)
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model=='account.payment':
                        try:
                            for line in rec.line_ids:
                                if line.field_name == 'state':
                                    if line.new_value_text == 'posted':
                                            payment_rec = self.env['account.payment'].browse(rec.res_id)
                                            if payment_rec.sync == False:
                                                for invoice in payment_rec.invoice_ids:
                                                    if invoice.state=='open':
                                                        if invoice.type == 'out_invoice':
                                                            result=sock.execute(dbname, d_uid, pwd, 'account.invoice', 'pay_customer_invoice', [invoice.id],
                                                                    payment_rec.journal_id.account_journal_old_id, payment_rec.amount, {})
                                                        else:
                                                            result = sock.execute(dbname, d_uid, pwd, 'account.invoice',
                                                                                  'pay_supplier_invoice', [invoice.id],
                                                                                  payment_rec.journal_id.account_journal_old_id,
                                                                                  payment_rec.amount, {})
                                                payment_rec.write({'sync': True})
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                elif rec.method == 'unlink':
                    if rec.model_id.model == 'account.invoice':
                        try:
                            invoice_rec =self.env['account.invoice'].browse(rec.res_id)
                            result = sock.execute(dbname, d_uid, pwd, 'account.invoice', 'unlink',[invoice_rec.invoice_old_id])
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model=='account.invoice.line':
                        try:
                            invoice_line_rec = self.env['account.invoice.line'].browse(rec.res_id)
                            result = sock.execute(dbname, d_uid, pwd, 'account.invoice.line', 'unlink',
                                                  [invoice_line_rec.invoice_line_old_id])
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()

    @api.model
    def sync_other_records(self):
        model_ids = self.env['ir.model'].search(
            [('model', 'in', ['rate', 'twilio.sms.send', 'twilio.sms.received','patient','interpreter.language','location','project','incoming.fax'])]).ids
        recs_to_sync = self.env['auditlog.log'].search(
            [('sync', '=', False), ('error', '=', False), ('model_id', 'in', model_ids)], order='create_date asc')
        if recs_to_sync:
            config_obj = self.env['server.config']
            config_ids = config_obj.search([])
            if not config_ids:
                raise UserError(_('No Active server config found!'))
            config = config_ids[0]
            ip = config.host  # Host
            port = config.port  # Port
            username = config.username  # the userl
            pwd = config.password  # the password of the user
            dbname = config.dbname  # the db name
            sock_common = xmlrpclib.ServerProxy('http://' + ip + ':' + port + '/xmlrpc/common')
            d_uid = sock_common.login(dbname, username, pwd)
            sock = xmlrpclib.ServerProxy('http://' + ip + ':' + port + '/xmlrpc/object')
            for rec in recs_to_sync:
                if rec.method == 'create':
                    if rec.model_id.model == 'rate':
                        try:
                            rate_rec = self.env['rate'].browse(rec.res_id)
                            if rate_rec.partner_id:
                                partner_id = rate_rec.partner_id.customer_record_old_id
                            else:
                                partner_id=False
                            rate_vals = {
                                'partner_id': partner_id,
                                'name': rate_rec.name,
                                'is_billing_rate': rate_rec.is_billing_rate,
                                'default_rate': rate_rec.default_rate,
                                'spanish_licenced': rate_rec.spanish_licenced,
                                'exotic_regular': rate_rec.exotic_regular,
                                'exotic_middle': rate_rec.exotic_middle,
                                'uom_id': rate_rec.uom_id and rate_rec.uom_id.id or False,
                                'spanish_regular': rate_rec.spanish_regular,
                                'spanish_certified': rate_rec.spanish_certified,
                                'exotic_certified': rate_rec.exotic_certified,
                                'exotic_high': rate_rec.exotic_high,
                                'base_hour': rate_rec.base_hour,
                                'inc_min': rate_rec.inc_min,
                                'rate_type': rate_rec.rate_type,
                                'rate_id': rate_rec.rate_id or 0,
                            }
                            rate_old_id = sock.execute(dbname, d_uid, pwd, 'rate', 'create',
                                                               rate_vals)
                            rate_rec.write({'rate_old_id': rate_old_id})
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model == 'twilio.sms.send':
                        try:
                            twilio_send_rec = self.env['twilio.sms.send'].browse(rec.res_id)
                            twilio_send_vals = {
                                'status': twilio_send_rec.status,
                                'direction': twilio_send_rec.direction,
                                'account_id': 1,
                                'price': twilio_send_rec.price,
                                'message_sid': twilio_send_rec.message_sid,
                                'sms_to': twilio_send_rec.sms_to,
                                'sms_from': twilio_send_rec.sms_from,
                                'error_msg': twilio_send_rec.error_msg,
                                'sms_body': twilio_send_rec.sms_body,
                                'account_sid': twilio_send_rec.account_sid,
                                'error_code': twilio_send_rec.error_code,
                                'price_unit': twilio_send_rec.price_unit,
                            }
                            twilio_send_old_id = sock.execute(dbname, d_uid, pwd, 'twilio.sms.send', 'create',
                                                               twilio_send_vals)
                            twilio_send_rec.write({'twilio_send_old_id':twilio_send_old_id})
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model == 'twilio.sms.received':
                        try:
                            twilio_receive_rec = self.env['twilio.sms.received'].browse(rec.res_id)
                            twilio_rec_vals = {
                                'status': twilio_receive_rec.status,
                                'account_id': 1,
                                'from_zip': twilio_receive_rec.from_zip,
                                'from_country': twilio_receive_rec.from_country,
                                'message_sid': twilio_receive_rec.message_sid,
                                'service_sid': twilio_receive_rec.service_sid,
                                'sms_from': twilio_receive_rec.sms_from,
                                'to_zip': twilio_receive_rec.to_zip,
                                'from_state': twilio_receive_rec.from_state,
                                'to_state': twilio_receive_rec.to_state,
                                'sms_body': twilio_receive_rec.sms_body,
                                'sms_to': twilio_receive_rec.sms_to,
                                'account_sid': twilio_receive_rec.account_sid,
                                'to_city': twilio_receive_rec.to_city,
                                'to_country': twilio_receive_rec.to_country,
                                'from_city': twilio_receive_rec.from_city,
                                'api_version': twilio_receive_rec.api_version,
                            }
                            twilio_rec_old_id = sock.execute(dbname, d_uid, pwd, 'twilio.sms.received', 'create',
                                                               twilio_rec_vals)
                            twilio_receive_rec.write({'twilio_rec_old_id':twilio_rec_old_id})
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model == 'patient':
                        try:
                            patient_rec = self.env['patient'].browse(rec.res_id)
                            if patient_rec.state_id:
                                state_id = patient_rec.state_id.state7_id
                            else:
                                state_id=False
                            if patient_rec.company_id:
                                company_id = patient_rec.company_id.res_company_old_id
                            else:
                                company_id = False
                            if patient_rec.case_manager_id:
                                case_manager_search_id = patient_rec.case_manager_id.employee_old_id
                            else:
                                case_manager_search_id = False
                            if patient_rec.field_case_mgr_id:
                                field_case_mgr_id = patient_rec.field_case_mgr_id.employee_old_id
                            else:
                                field_case_mgr_id = False
                            if patient_rec.billing_partner_id:
                                billing_partner_id = patient_rec.billing_partner_id.customer_record_old_id
                            else:
                                billing_partner_id = False
                            if patient_rec.billing_contact_id:
                                billing_contact_id = patient_rec.billing_contact_id.customer_record_old_id
                            else:
                                billing_contact_id = False

                            if patient_rec.interpreter_id:
                                interpreter_id = patient_rec.billing_contact_id.customer_record_old_id
                            else:
                                interpreter_id = False
                            if patient_rec.ordering_partner_id:
                                ordering_partner_id = patient_rec.ordering_partner_id.customer_record_old_id
                            else:
                                ordering_partner_id = False
                            patient_vals = {
                                'name': patient_rec.name,
                                'last_name': patient_rec.last_name,
                                'complete_name': patient_rec.complete_name,
                                # 'user_id': user_id.id,
                                'comment': patient_rec.comment,
                                'active': patient_rec.active,
                                'street': patient_rec.street,
                                'street2': patient_rec.street2,
                                'company_id': company_id,
                                'zip': patient_rec.zip,
                                'city': patient_rec.city,
                                'state_id': state_id,
                                'country_id': 235,
                                'email': patient_rec.email,
                                'email2': patient_rec.email2,
                                'phone': patient_rec.phone,
                                'phone2': patient_rec.phone2,
                                'phone3': patient_rec.phone3,
                                'phone4': patient_rec.phone4,
                                'fax': patient_rec.fax,
                                'mobile': patient_rec.mobile,
                                'is_alert': patient_rec.is_alert,
                                'ssnid': patient_rec.ssnid,
                                'sinid': patient_rec.sinid,
                                'latitude': patient_rec.latitude,
                                'longitude': patient_rec.longitude,
                                'gender': patient_rec.gender,
                                'company_name': patient_rec.company_name,
                                'function': patient_rec.function,
                                'birthdate': patient_rec.birthdate,
                                'injury_date': patient_rec.injury_date,
                                'patient_id': patient_rec.patient_id,
                                'website': patient_rec.website,
                                'date': patient_rec.date,
                                'last_update_date': patient_rec.last_update_date,
                                'employer': patient_rec.employer,
                                'employer_contact': patient_rec.employer_contact,
                                # 'case_manager': case_manager,
                                'case_manager_id': case_manager_search_id,
                                'claim_number': patient_rec.claim_number,
                                'claim_no': patient_rec.claim_no,
                                'claim_no2': patient_rec.claim_no2,
                                'field_case_mgr_id': field_case_mgr_id,
                                'referrer': patient_rec.referrer,
                                'billing_partner_id': billing_partner_id,
                                'billing_contact_id': billing_contact_id,
                                # 'patient_history':patient_history,
                                # 'patient_auth_history':patient_auth_history,
                                # 'location_ids':location_ids,
                                'interpreter_id': interpreter_id,
                                # 'interpreter_history': interpreter_history,
                                'ordering_partner_id': ordering_partner_id,
                            }
                            patient_old_id = sock.execute(dbname, d_uid, pwd, 'patient', 'create',
                                                               patient_vals)
                            patient_rec.write({'patient_old_id':patient_old_id})
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model == 'interpreter.language':
                        try:
                            interpreter_language_rec = self.env['interpreter.language'].browse(rec.res_id)
                            if interpreter_language_rec.name:
                                language_id = interpreter_language_rec.name.language_old_id
                            else:
                                language_id = False
                            if interpreter_language_rec.certification_level_id:
                                certification_level_id = interpreter_language_rec.certification_level_id.certification_level_old_id
                            else:
                                certification_level_id = False
                            if interpreter_language_rec.interpreter_id:
                                interpreter_id = interpreter_language_rec.interpreter_id.customer_record_old_id
                            else:
                                interpreter_id = False
                            interpreter_language_vals = {
                                'name': language_id,
                                'sort_order': interpreter_language_rec.sort_order,
                                'is_simultaneous': interpreter_language_rec.is_simultaneous,
                                'specialization': interpreter_language_rec.specialization,
                                'certification_code': interpreter_language_rec.certification_code,
                                'certification_level_id': certification_level_id,
                                'interpreter_id': interpreter_id,
                            }
                            interpret_language_old_id = sock.execute(dbname, d_uid, pwd, 'interpreter.language',
                                                                     'create',
                                                                     interpreter_language_vals)
                            interpreter_language_rec.write({'interpret_language_old_id': interpret_language_old_id})
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model == 'location':
                        try:
                            location_rec = self.env['location'].browse(rec.res_id)
                            if location_rec.doctor_id:
                                doc_id = location_rec.doctor_id.doctor_old_id
                            else:
                                doc_id = False
                            if location_rec.patient_id:
                                pat_id = location_rec.patient_id.patient_old_id
                            else:
                                pat_id = False
                            if location_rec.state_id:
                                state = location_rec.state_id.state7_id
                            else:
                                state = False
                            if location_rec.zone_id:
                                zone = location_rec.zone_id.zone_old_id
                            else:
                                zone = False
                            if location_rec.ordering_partner_id:
                                partner = location_rec.ordering_partner_id.customer_record_old_id
                            else:
                                partner = False
                            if location_rec.company_id:
                                company = location_rec.company_id.res_company_old_id
                            else:
                                company = False
                            location_vals = {
                                # 'location_old_id': location_old_id,
                                'doctor_id': doc_id,
                                'patient_id': pat_id,
                                'name': location_rec.name,
                                'actual_name': location_rec.actual_name,
                                'date': location_rec.date,
                                'ref': location_rec.ref,
                                # 'user_id': user,
                                'location_type':location_rec.location_type,
                                'comment': location_rec.comment,
                                'active': location_rec.active,
                                'street': location_rec.street,
                                'is_alert': location_rec.is_alert,
                                'street2': location_rec.street2,
                                'zip': location_rec.zip,
                                'city': location_rec.city,
                                'state_id': state,
                                'country_id': 235,
                                'email': location_rec.email,
                                'phone': location_rec.phone,
                                'fax': location_rec.fax,
                                'mobile': location_rec.mobile,
                                'phone2': location_rec.phone2,
                                'is_sdhhs': location_rec.is_sdhhs,
                                'location_id': location_rec.location_id,
                                'location_id2': location_rec.location_id2,
                                'zone_id': zone,
                                'latitude': location_rec.latitude,
                                'longitude': location_rec.longitude,
                                'date_localization': location_rec.date_localization,
                                'is_geo': location_rec.is_geo,
                                'last_update_date': location_rec.last_update_date,
                                'land_mark': location_rec.land_mark,
                                'complete_name': location_rec.complete_name,
                                'is_pat_loc': location_rec.is_pat_loc,
                                # 'address_type_id': address_type_id,
                                'ordering_partner_id': partner,
                                'timezone': location_rec.timezone,
                                'company_id': company,
                            }
                            location_old_id = sock.execute(dbname, d_uid, pwd, 'location', 'create',
                                                               location_vals)
                            location_rec.write({'location_old_id': location_old_id})
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model == 'project':
                        try:
                            project_rec = self.env['project'].browse(rec.res_id)
                            if project_rec.company_id:
                                company_id = project_rec.company_id.res_company_old_id
                            else:
                                company_id=False
                            partner_ids=[]
                            for partner_id in project_rec.partner_proj_ids:
                                partner = partner_id.customer_record_old_id
                                if partner:
                                    partner_ids.append(partner)
                            iug_pro_vals = {
                                'name': project_rec.name,
                                'company_id': company_id,
                                'partner_proj_ids':[(6, 0, partner_ids)]
                            }
                            iug_project_old_id = sock.execute(dbname, d_uid, pwd, 'project', 'create',
                                                           iug_pro_vals)
                            project_rec.write({'iug_project_old_id': iug_project_old_id})
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model == 'incoming.fax':
                        try:
                            incoming_fax_rec = self.env['incoming.fax'].browse(rec.res_id)
                            if incoming_fax_rec.company_id:
                                company_id = incoming_fax_rec.company_id.res_company_old_id
                            else:
                                company_id=False
                            if incoming_fax_rec.company_id2:
                                company_id2 = incoming_fax_rec.company_id2.res_company_old_id
                            else:
                                company_id2=False
                            if incoming_fax_rec.fax_attachment_id:
                                fax_attachment_id = incoming_fax_rec.fax_attachment_id.res_old_id
                            else:
                                fax_attachment_id=False
                            if incoming_fax_rec.document_type_id:
                                document_type_id = incoming_fax_rec.document_type_id.document_type_old_id
                            else:
                                document_type_id =False
                            fax_in_vals = {
                                # '': row[0].strip() or '',
                                'name': incoming_fax_rec.name,
                                'date': incoming_fax_rec.date,
                                'fax': incoming_fax_rec.fax,
                                'attach_to': incoming_fax_rec.attach_to,
                                'doc_type': incoming_fax_rec.doc_type,
                                'company_id': company_id,
                                'company_id2': company_id2,
                                'fax_attachment_id': fax_attachment_id,
                                'document_type_id': document_type_id,
                                'attached': incoming_fax_rec.attached,
                                'msg_id': incoming_fax_rec.msg_id,
                                'ph_no': incoming_fax_rec.ph_no,
                                'csid': incoming_fax_rec.csid,
                                'msg_stat': incoming_fax_rec.msg_stat,
                                'pages': incoming_fax_rec.pages,
                                'msg_size': incoming_fax_rec.msg_size,
                                'msg_type': incoming_fax_rec.msg_type,
                                'rcv_time': incoming_fax_rec.rcv_time,
                                'caller_id': incoming_fax_rec.caller_id,
                                'rec_duration': incoming_fax_rec.rec_duration,
                                'received_status': incoming_fax_rec.received_status,
                                'state': incoming_fax_rec.state,
                            }
                            fax_in_old_id = sock.execute(dbname, d_uid, pwd, 'incoming.fax', 'create',
                                                         fax_in_vals)
                            incoming_fax_rec.write({'fax_in_old_id': fax_in_old_id})
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                elif rec.method == 'write':
                    if rec.model_id.model == 'rate':
                        try:
                            rate_rec = self.env['rate'].browse(rec.res_id)
                            if rate_rec.partner_id:
                                partner_id = rate_rec.partner_id.customer_record_old_id
                            else:
                                partner_id=False
                            rate_vals = {
                                'partner_id': partner_id,
                                'name': rate_rec.name,
                                'is_billing_rate': rate_rec.is_billing_rate,
                                'default_rate': rate_rec.default_rate,
                                'spanish_licenced': rate_rec.spanish_licenced,
                                'exotic_regular': rate_rec.exotic_regular,
                                'exotic_middle': rate_rec.exotic_middle,
                                'uom_id': rate_rec.uom_id and rate_rec.uom_id.id or False,
                                'spanish_regular': rate_rec.spanish_regular,
                                'spanish_certified': rate_rec.spanish_certified,
                                'exotic_certified': rate_rec.exotic_certified,
                                'exotic_high': rate_rec.exotic_high,
                                'base_hour': rate_rec.base_hour,
                                'inc_min': rate_rec.inc_min,
                                'rate_type': rate_rec.rate_type,
                                'rate_id': rate_rec.rate_id or 0,
                            }
                            result = sock.execute(dbname, d_uid, pwd, 'rate', 'write',
                                                               [rate_rec.rate_old_id],rate_vals)
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model == 'twilio.sms.send':
                        try:
                            twilio_send_rec = self.env['twilio.sms.send'].browse(rec.res_id)
                            twilio_send_vals = {
                                'status': twilio_send_rec.status,
                                'direction': twilio_send_rec.direction,
                                'account_id': 1,
                                'price': twilio_send_rec.price,
                                'message_sid': twilio_send_rec.message_sid,
                                'sms_to': twilio_send_rec.sms_to,
                                'sms_from': twilio_send_rec.sms_from,
                                'error_msg': twilio_send_rec.error_msg,
                                'sms_body': twilio_send_rec.sms_body,
                                'account_sid': twilio_send_rec.account_sid,
                                'error_code': twilio_send_rec.error_code,
                                'price_unit': twilio_send_rec.price_unit,
                            }
                            result = sock.execute(dbname, d_uid, pwd, 'twilio.sms.send', 'write',[twilio_send_rec.twilio_send_old_id],
                                                               twilio_send_vals)
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model == 'twilio.sms.received':
                        try:
                            twilio_receive_rec = self.env['twilio.sms.received'].browse(rec.res_id)
                            twilio_rec_vals = {
                                'status': twilio_receive_rec.status,
                                'account_id': 1,
                                'from_zip': twilio_receive_rec.from_zip,
                                'from_country': twilio_receive_rec.from_country,
                                'message_sid': twilio_receive_rec.message_sid,
                                'service_sid': twilio_receive_rec.service_sid,
                                'sms_from': twilio_receive_rec.sms_from,
                                'to_zip': twilio_receive_rec.to_zip,
                                'from_state': twilio_receive_rec.from_state,
                                'to_state': twilio_receive_rec.to_state,
                                'sms_body': twilio_receive_rec.sms_body,
                                'sms_to': twilio_receive_rec.sms_to,
                                'account_sid': twilio_receive_rec.account_sid,
                                'to_city': twilio_receive_rec.to_city,
                                'to_country': twilio_receive_rec.to_country,
                                'from_city': twilio_receive_rec.from_city,
                                'api_version': twilio_receive_rec.api_version,
                            }
                            result = sock.execute(dbname, d_uid, pwd, 'twilio.sms.received', 'write',[twilio_receive_rec.twilio_rec_old_id],
                                                               twilio_rec_vals)
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model == 'patient':
                        try:
                            patient_rec = self.env['patient'].browse(rec.res_id)
                            if patient_rec.state_id:
                                state_id = patient_rec.state_id.state7_id
                            else:
                                state_id=False
                            if patient_rec.company_id:
                                company_id = patient_rec.company_id.res_company_old_id
                            else:
                                company_id = False
                            if patient_rec.case_manager_id:
                                case_manager_search_id = patient_rec.case_manager_id.employee_old_id
                            else:
                                case_manager_search_id = False
                            if patient_rec.field_case_mgr_id:
                                field_case_mgr_id = patient_rec.field_case_mgr_id.employee_old_id
                            else:
                                field_case_mgr_id = False
                            if patient_rec.billing_partner_id:
                                billing_partner_id = patient_rec.billing_partner_id.customer_record_old_id
                            else:
                                billing_partner_id = False
                            if patient_rec.billing_contact_id:
                                billing_contact_id = patient_rec.billing_contact_id.customer_record_old_id
                            else:
                                billing_contact_id = False

                            if patient_rec.interpreter_id:
                                interpreter_id = patient_rec.billing_contact_id.customer_record_old_id
                            else:
                                interpreter_id = False
                            if patient_rec.ordering_partner_id:
                                ordering_partner_id = patient_rec.ordering_partner_id.customer_record_old_id
                            else:
                                ordering_partner_id = False
                            patient_vals = {
                                'name': patient_rec.name,
                                'last_name': patient_rec.last_name,
                                'complete_name': patient_rec.complete_name,
                                # 'user_id': user_id.id,
                                'comment': patient_rec.comment,
                                'active': patient_rec.active,
                                'street': patient_rec.street,
                                'street2': patient_rec.street2,
                                'company_id': company_id,
                                'zip': patient_rec.zip,
                                'city': patient_rec.city,
                                'state_id': state_id,
                                'country_id': 235,
                                'email': patient_rec.email,
                                'email2': patient_rec.email2,
                                'phone': patient_rec.phone,
                                'phone2': patient_rec.phone2,
                                'phone3': patient_rec.phone3,
                                'phone4': patient_rec.phone4,
                                'fax': patient_rec.fax,
                                'mobile': patient_rec.mobile,
                                'is_alert': patient_rec.is_alert,
                                'ssnid': patient_rec.ssnid,
                                'sinid': patient_rec.sinid,
                                'latitude': patient_rec.latitude,
                                'longitude': patient_rec.longitude,
                                'gender': patient_rec.gender,
                                'company_name': patient_rec.company_name,
                                'function': patient_rec.function,
                                'birthdate': patient_rec.birthdate,
                                'injury_date': patient_rec.injury_date,
                                'patient_id': patient_rec.patient_id,
                                'website': patient_rec.website,
                                'date': patient_rec.date,
                                'last_update_date': patient_rec.last_update_date,
                                'employer': patient_rec.employer,
                                'employer_contact': patient_rec.employer_contact,
                                # 'case_manager': case_manager,
                                'case_manager_id': case_manager_search_id,
                                'claim_number': patient_rec.claim_number,
                                'claim_no': patient_rec.claim_no,
                                'claim_no2': patient_rec.claim_no2,
                                'field_case_mgr_id': field_case_mgr_id,
                                'referrer': patient_rec.referrer,
                                'billing_partner_id': billing_partner_id,
                                'billing_contact_id': billing_contact_id,
                                # 'patient_history':patient_history,
                                # 'patient_auth_history':patient_auth_history,
                                # 'location_ids':location_ids,
                                'interpreter_id': interpreter_id,
                                # 'interpreter_history': interpreter_history,
                                'ordering_partner_id': ordering_partner_id,
                            }
                            result= sock.execute(dbname, d_uid, pwd, 'patient', 'write',[patient_rec.patient_old_id],
                                                               patient_vals)
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model == 'interpreter.language':
                        try:
                            interpreter_language_rec = self.env['interpreter.language'].browse(rec.res_id)
                            if interpreter_language_rec.name:
                                language_id = interpreter_language_rec.name.language_old_id
                            else:
                                language_id = False
                            if interpreter_language_rec.certification_level_id:
                                certification_level_id = interpreter_language_rec.certification_level_id.certification_level_old_id
                            else:
                                certification_level_id = False
                            if interpreter_language_rec.interpreter_id:
                                interpreter_id = interpreter_language_rec.interpreter_id.customer_record_old_id
                            else:
                                interpreter_id = False
                            interpreter_language_vals = {
                                'name': language_id,
                                'sort_order': interpreter_language_rec.sort_order,
                                'is_simultaneous': interpreter_language_rec.is_simultaneous,
                                'specialization': interpreter_language_rec.specialization,
                                'certification_code': interpreter_language_rec.certification_code,
                                'certification_level_id': certification_level_id,
                                'interpreter_id': interpreter_id,
                            }
                            result = sock.execute(dbname, d_uid, pwd, 'interpreter.language', 'write',
                                                  [interpreter_language_rec.interpret_language_old_id],
                                                  interpreter_language_vals)
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model == 'location':
                        try:
                            location_rec = self.env['location'].browse(rec.res_id)
                            if location_rec.doctor_id:
                                doc_id = location_rec.doctor_id.doctor_old_id
                            else:
                                doc_id = False
                            if location_rec.patient_id:
                                pat_id = location_rec.patient_id.patient_old_id
                            else:
                                pat_id = False
                            if location_rec.state_id:
                                state = location_rec.state_id.state7_id
                            else:
                                state = False
                            if location_rec.zone_id:
                                zone = location_rec.zone_id.zone_old_id
                            else:
                                zone = False
                            if location_rec.ordering_partner_id:
                                partner = location_rec.ordering_partner_id.customer_record_old_id
                            else:
                                partner = False
                            if location_rec.company_id:
                                company = location_rec.company_id.res_company_old_id
                            else:
                                company = False
                            location_vals = {
                                'doctor_id': doc_id,
                                'patient_id': pat_id,
                                'name': location_rec.name,
                                'actual_name': location_rec.actual_name,
                                'date': location_rec.date,
                                'ref': location_rec.ref,
                                # 'user_id': user,
                                'location_type':location_rec.location_type,
                                'comment': location_rec.comment,
                                'active': location_rec.active,
                                'street': location_rec.street,
                                'is_alert': location_rec.is_alert,
                                'street2': location_rec.street2,
                                'zip': location_rec.zip,
                                'city': location_rec.city,
                                'state_id': state,
                                'country_id': 235,
                                'email': location_rec.email,
                                'phone': location_rec.phone,
                                'fax': location_rec.fax,
                                'mobile': location_rec.mobile,
                                'phone2': location_rec.phone2,
                                'is_sdhhs': location_rec.is_sdhhs,
                                'location_id': location_rec.location_id,
                                'location_id2': location_rec.location_id2,
                                'zone_id': zone,
                                'latitude': location_rec.latitude,
                                'longitude': location_rec.longitude,
                                'date_localization': location_rec.date_localization,
                                'is_geo': location_rec.is_geo,
                                'last_update_date': location_rec.last_update_date,
                                'land_mark': location_rec.land_mark,
                                'complete_name': location_rec.complete_name,
                                'is_pat_loc': location_rec.is_pat_loc,
                                # 'address_type_id': address_type_id,
                                'ordering_partner_id': partner,
                                'timezone': location_rec.timezone,
                                'company_id': company,
                            }
                            result = sock.execute(dbname, d_uid, pwd, 'location', 'write',
                                                               [location_rec.location_old_id],location_vals)
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model == 'project':
                        try:
                            project_rec = self.env['project'].browse(rec.res_id)
                            if project_rec.company_id:
                                company_id = project_rec.company_id.res_company_old_id
                            else:
                                company_id=False
                            partner_ids = []
                            for partner_id in project_rec.partner_proj_ids:
                                partner = partner_id.customer_record_old_id
                                if partner:
                                    partner_ids.append(partner)
                            iug_pro_vals = {
                                'name': project_rec.name,
                                'company_id': company_id,
                                'partner_proj_ids': [(6, 0, partner_ids)]
                            }
                            result = sock.execute(dbname, d_uid, pwd, 'project', 'write',[project_rec.iug_project_old_id],
                                                           iug_pro_vals)
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model == 'incoming.fax':
                        try:
                            incoming_fax_rec = self.env['incoming.fax'].browse(rec.res_id)
                            if incoming_fax_rec.company_id:
                                company_id = incoming_fax_rec.company_id.res_company_old_id
                            else:
                                company_id=False
                            if incoming_fax_rec.company_id2:
                                company_id2 = incoming_fax_rec.company_id2.res_company_old_id
                            else:
                                company_id2=False
                            if incoming_fax_rec.fax_attachment_id:
                                fax_attachment_id = incoming_fax_rec.fax_attachment_id.res_old_id
                            else:
                                fax_attachment_id=False
                            if incoming_fax_rec.document_type_id:
                                document_type_id = incoming_fax_rec.document_type_id.document_type_old_id
                            else:
                                document_type_id =False
                            fax_in_vals = {
                                # '': row[0].strip() or '',
                                'name': incoming_fax_rec.name,
                                'date': incoming_fax_rec.date,
                                'fax': incoming_fax_rec.fax,
                                'attach_to': incoming_fax_rec.attach_to,
                                'doc_type': incoming_fax_rec.doc_type,
                                'company_id': company_id,
                                'company_id2': company_id2,
                                'fax_attachment_id': fax_attachment_id,
                                'document_type_id': document_type_id,
                                'attached': incoming_fax_rec.attached,
                                'msg_id': incoming_fax_rec.msg_id,
                                'ph_no': incoming_fax_rec.ph_no,
                                'csid': incoming_fax_rec.csid,
                                'msg_stat': incoming_fax_rec.msg_stat,
                                'pages': incoming_fax_rec.pages,
                                'msg_size': incoming_fax_rec.msg_size,
                                'msg_type': incoming_fax_rec.msg_type,
                                'rcv_time': incoming_fax_rec.rcv_time,
                                'caller_id': incoming_fax_rec.caller_id,
                                'rec_duration': incoming_fax_rec.rec_duration,
                                'received_status': incoming_fax_rec.received_status,
                                'state': incoming_fax_rec.state,
                            }
                            result = sock.execute(dbname, d_uid, pwd, 'incoming.fax', 'write',[incoming_fax_rec.fax_in_old_id],
                                                         fax_in_vals)
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                elif rec.method == 'unlink':
                    if rec.model_id.model == 'rate':
                        try:
                            rate_rec = self.env['rate'].browse(rec.res_id)
                            result = sock.execute(dbname, d_uid, pwd, 'rate', 'unlink',
                                              [rate_rec.rate_old_id])
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model == 'twilio.sms.send':
                        try:
                            twilio_send_rec = self.env['twilio.sms.send'].browse(rec.res_id)
                            result = sock.execute(dbname, d_uid, pwd, 'twilio.sms.send', 'unlink',
                                              [twilio_send_rec.twilio_send_old_id])
                            rec.write({'sync': True})
                        except Exception as e:
                            rec.write({'error': str(e)})
                    elif rec.model_id.model == 'twilio.sms.received':
                        try:
                            twilio_receive_rec = self.env['twilio.sms.received'].browse(rec.res_id)
                            result = sock.execute(dbname, d_uid, pwd, 'twilio.sms.received', 'unlink',
                                              [twilio_receive_rec.twilio_rec_old_id])
                            rec.write({'sync': True})
                        except Exception as e:
                            rec.write({'error': str(e)})
                    elif rec.model_id.model == 'patient':
                        try:
                            patient_rec = self.env['patient'].browse(rec.res_id)
                            result = sock.execute(dbname, d_uid, pwd, 'patient', 'unlink',
                                              [patient_rec.patient_old_id])
                            rec.write({'sync': True})
                        except Exception as e:
                            rec.write({'error': str(e)})
                    elif rec.model_id.model == 'interpreter.language':
                        try:
                            interpreter_language_rec = self.env['interpreter.language'].browse(rec.res_id)
                            result = sock.execute(dbname, d_uid, pwd, 'interpreter.language', 'unlink',
                                                  [interpreter_language_rec.interpret_language_old_id])
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model == 'location':
                        try:
                            location_rec = self.env['location'].browse(rec.res_id)
                            result = sock.execute(dbname, d_uid, pwd, 'location', 'unlink',
                                                  [location_rec.location_old_id])
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model == 'project':
                        try:
                            project_rec = self.env['project'].browse(rec.res_id)
                            result = sock.execute(dbname, d_uid, pwd, 'project', 'unlink',[project_rec.iug_project_old_id])
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model == 'incoming.fax':
                        try:
                            incoming_fax_rec = self.env['incoming.fax'].browse(rec.res_id)
                            result = sock.execute(dbname, d_uid, pwd, 'incoming.fax', 'unlink',[incoming_fax_rec.fax_in_old_id])
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()

    @api.model
    def sync_project_related_records(self):
        model_ids = self.env['ir.model'].search(
            [('model', 'in',
              ['project.task','project.task.work'])]).ids
        recs_to_sync = self.env['auditlog.log'].search(
            [('sync', '=', False), ('error', '=', False), ('model_id', 'in', model_ids)], order='create_date asc')
        if recs_to_sync:
            config_obj = self.env['server.config']
            config_ids = config_obj.search([])
            if not config_ids:
                raise UserError(_('No Active server config found!'))
            config = config_ids[0]
            ip = config.host  # Host
            port = config.port  # Port
            username = config.username  # the userl
            pwd = config.password  # the password of the user
            dbname = config.dbname  # the db name
            sock_common = xmlrpclib.ServerProxy('http://' + ip + ':' + port + '/xmlrpc/common')
            d_uid = sock_common.login(dbname, username, pwd)
            sock = xmlrpclib.ServerProxy('http://' + ip + ':' + port + '/xmlrpc/object')
            for rec in recs_to_sync:
                if rec.method == 'create':
                    if rec.model_id.model == 'project.task':
                        try:
                            project_task_rec =self.env['project.task'].browse(rec.res_id)
                            if project_task_rec.partner_id:
                                partner_id = project_task_rec.partner_id.customer_record_old_id
                            else:
                                partner_id = False
                            if project_task_rec.user_id:
                                user_id = project_task_rec.user_id.user_old_id
                            else:
                                user_id = False
                            if project_task_rec.company_id:
                                company_id = project_task_rec.company_id.res_company_old_id
                            else:
                                company_id=False
                            if project_task_rec.stage_id:
                                stage_id = project_task_rec.stage_id.project_task_type_old_id
                            else:
                                stage_id = False
                            if project_task_rec.event_id:
                                event_id = project_task_rec.event_id.event_old_id
                            else:
                                event_id = False
                            if project_task_rec.user_id_int:
                                user_id_int_id = project_task_rec.user_id_int.user_old_id
                            else:
                                user_id_int_id = False
                            if project_task_rec.view_interpreter:
                                view_interpreter = project_task_rec.view_interpreter.customer_record_old_id
                            else:
                                view_interpreter = False
                            interpreter_ids=[]
                            for interpreter_id in project_task_rec.assigned_interpreters:
                                assigned_partner_id = interpreter_id.customer_record_old_id
                                if assigned_partner_id:
                                    interpreter_ids.append(assigned_partner_id)
                            supp_invoice_ids=[]
                            for supp_invoice in project_task_rec.supp_invoice_ids:
                                supp_invoice_id=supp_invoice.invoice_old_id
                                if supp_invoice_id:
                                    supp_invoice_ids.append(supp_invoice_id)
                            if project_task_rec.cust_invoice_id:
                                cust_invoice_id=project_task_rec.cust_invoice_id.invoice_old_id
                            else:
                                cust_invoice_id=False
                            if project_task_rec.supp_invoice_id2:
                                supp_invoice_id2=project_task_rec.supp_invoice_id2.invoice_old_id
                            else:
                                supp_invoice_id2=False
                            if project_task_rec.transporter_id:
                                transporter_id = project_task_rec.transporter_id.customer_record_old_id
                            else:
                                transporter_id = False
                            project_task_vals = {
                                                # 'project_task_old_id': project_task_old_id,
                                                 # 'sequence': sequence,
                                                'assigned_interpreters':[(6, 0, interpreter_ids)],
                                                'supp_invoice_ids':[(6, 0, supp_invoice_ids)],
                                                 'color': project_task_rec.color,
                                                 'date_end': project_task_rec.date_end,
                                                 'planned_hours': project_task_rec.planned_hours,
                                                 'partner_id': partner_id,
                                                 'user_id': user_id,
                                                 'date_start': project_task_rec.date_start,
                                                 'company_id': company_id,
                                                 'priority': project_task_rec.priority,
                                                 'state': project_task_rec.state,
                                                 'description': project_task_rec.description,
                                                 'kanban_state': project_task_rec.kanban_state,
                                                 'active': project_task_rec.active,
                                                 'stage_id': stage_id,
                                                 'name': project_task_rec.name,
                                                 'date_deadline': project_task_rec.date_deadline,
                                                 'notes': project_task_rec.notes,
                                                 'event_type': project_task_rec.event_type,
                                                 # 'task_id': task_id,
                                                 'event_id': event_id,
                                                 'transporter_id': transporter_id,
                                                 'billing_state': project_task_rec.billing_state,
                                                 'cust_invoice_id': cust_invoice_id,
                                                 'supp_invoice_id2': supp_invoice_id2,
                                                 'user_id_int': user_id_int_id,
                                                 'view_interpreter': view_interpreter,
                                                 'current_time': project_task_rec.current_time,
                                                 # 'timesheet_attachment': timesheet_attachment,
                                                 'attachment_filename': project_task_rec.attachment_filename,
                                                     }
                            project_task_old_id = sock.execute(dbname, d_uid, pwd, 'project.task', 'create', project_task_vals)
                            project_task_rec.write({'project_task_old_id':project_task_old_id})
                            self._cr.commit()
                            for task_work_id in project_task_rec.work_ids:

                                if task_work_id.task_id:
                                    task_id = task_work_id.task_id.project_task_old_id
                                else:
                                    task_id = False
                                if task_work_id.company_id:
                                    company_id = task_work_id.company_id.res_company_old_id
                                else:
                                    company_id = False

                                if task_work_id.interpreter_id:
                                    interpreter_id = task_work_id.interpreter_id.customer_record_old_id
                                else:
                                    interpreter_id = False
                                if task_work_id.event_out_come_id:
                                    event_out_come_id = task_work_id.event_out_come_id.event_outcome_old_id
                                else:
                                    event_out_come_id = False
                                if task_work_id.user_id:
                                    user_id = task_work_id.user_id.user_old_id
                                else:
                                    user_id=False
                                project_task_work_vals = {
                                      'user_id': user_id,
                                      'name': task_work_id.name,
                                      'task_id': task_id,
                                      'date': task_work_id.date,
                                      'company_id': company_id,
                                      'total_mileage_covered': task_work_id.total_mileage_covered,
                                      'hours_spend': task_work_id.hours_spend,
                                      'event_start_time': task_work_id.event_start_time,
                                      'event_end_time': task_work_id.event_end_time,
                                      'task_for': task_work_id.task_for,
                                      'am_pm2': task_work_id.am_pm2,
                                      'am_pm': task_work_id.am_pm,
                                      'event_start_date': task_work_id.event_start_date,
                                      'wait_time_bill': task_work_id.wait_time_bill,
                                      'wait_time': task_work_id.wait_time,
                                      'interpreter_id': interpreter_id,
                                      'event_out_come_id': event_out_come_id,
                                      'event_start_hr': task_work_id.event_start_hr,
                                      'event_end_hr': task_work_id.event_end_hr,
                                      'event_end_min': task_work_id.event_end_min,
                                      'event_start_min': task_work_id.event_start_min,
                                      'edited': task_work_id.edited,
                                      'travel_time': task_work_id.travel_time,
                                      }
                                project_task_work_old_id = sock.execute(dbname, d_uid, pwd, 'project.task.work', 'create',
                                                                        project_task_work_vals)
                                task_work_id.write({'project_task_work_old_id': project_task_work_old_id})
                            rec.write({'sync':True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model=='project.task.work':
                        try:
                            task_work_id = self.env['project.task.work'].browse(rec.res_id)
                            project_task_work_rec_exists=sock.execute(dbname, d_uid, pwd, 'project.task.work', 'search',
                                                                 [('id', '=',task_work_id.project_task_work_old_id)])
                            if not project_task_work_rec_exists:
                                if task_work_id.task_id:
                                    task_id = task_work_id.task_id.project_task_old_id
                                else:
                                    task_id = False
                                if task_work_id.company_id:
                                    company_id = task_work_id.company_id.res_company_old_id
                                else:
                                    company_id = False

                                if task_work_id.interpreter_id:
                                    interpreter_id = task_work_id.interpreter_id.customer_record_old_id
                                else:
                                    interpreter_id = False
                                if task_work_id.event_out_come_id:
                                    event_out_come_id = task_work_id.event_out_come_id.event_outcome_old_id
                                else:
                                    event_out_come_id = False
                                if task_work_id.user_id:
                                    user_id = task_work_id.user_id.user_old_id
                                else:
                                    user_id=False
                                project_task_work_vals = {
                                    'user_id': user_id,
                                    'name': task_work_id.name,
                                    'task_id': task_id,
                                    'date': task_work_id.date,
                                    'company_id': company_id,
                                    'total_mileage_covered': task_work_id.total_mileage_covered,
                                    'hours_spend': task_work_id.hours_spend,
                                    'event_start_time': task_work_id.event_start_time,
                                    'event_end_time': task_work_id.event_end_time,
                                    'task_for': task_work_id.task_for,
                                    'am_pm2': task_work_id.am_pm2,
                                    'am_pm': task_work_id.am_pm,
                                    'event_start_date': task_work_id.event_start_date,
                                    'wait_time_bill': task_work_id.wait_time_bill,
                                    'wait_time': task_work_id.wait_time,
                                    'interpreter_id': interpreter_id,
                                    'event_out_come_id': event_out_come_id,
                                    'event_start_hr': task_work_id.event_start_hr,
                                    'event_end_hr': task_work_id.event_end_hr,
                                    'event_end_min': task_work_id.event_end_min,
                                    'event_start_min': task_work_id.event_start_min,
                                    'edited': task_work_id.edited,
                                    'travel_time': task_work_id.travel_time,
                                }
                                project_task_work_old_id = sock.execute(dbname, d_uid, pwd, 'project.task.work',
                                                                        'create',
                                                                        project_task_work_vals)
                                task_work_id.write({'project_task_work_old_id': project_task_work_old_id})
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error':e})
                            self._cr.commit()
                elif rec.method == 'write':
                    if rec.model_id.model == 'project.task':
                        try:
                            project_task_rec =self.env['project.task'].browse(rec.res_id)
                            if project_task_rec.partner_id:
                                partner_id = project_task_rec.partner_id.customer_record_old_id
                            else:
                                partner_id = False
                            if project_task_rec.user_id:
                                user_id = project_task_rec.user_id.user_old_id
                            else:
                                user_id = False
                            if project_task_rec.company_id:
                                company_id = project_task_rec.company_id.res_company_old_id
                            else:
                                company_id=False
                            if project_task_rec.stage_id:
                                stage_id = project_task_rec.stage_id.project_task_type_old_id
                            else:
                                stage_id = False
                            if project_task_rec.event_id:
                                event_id = project_task_rec.event_id.event_old_id
                            else:
                                event_id = False
                            if project_task_rec.user_id_int:
                                user_id_int_id = project_task_rec.user_id_int.user_old_id
                            else:
                                user_id_int_id = False
                            if project_task_rec.view_interpreter:
                                view_interpreter = project_task_rec.view_interpreter.customer_record_old_id
                            else:
                                view_interpreter = False
                            interpreter_ids=[]
                            for interpreter_id in project_task_rec.assigned_interpreters:
                                assigned_partner_id = interpreter_id.customer_record_old_id
                                if assigned_partner_id:
                                    interpreter_ids.append(assigned_partner_id)
                            supp_invoice_ids=[]
                            for supp_invoice in project_task_rec.supp_invoice_ids:
                                supp_invoice_id=supp_invoice.invoice_old_id
                                if supp_invoice_id:
                                    supp_invoice_ids.append(supp_invoice_id)
                            if project_task_rec.cust_invoice_id:
                                cust_invoice_id=project_task_rec.cust_invoice_id.invoice_old_id
                            else:
                                cust_invoice_id=False
                            if project_task_rec.supp_invoice_id2:
                                supp_invoice_id2=project_task_rec.supp_invoice_id2.invoice_old_id
                            else:
                                supp_invoice_id2=False
                            if project_task_rec.transporter_id:
                                transporter_id = project_task_rec.transporter_id.customer_record_old_id
                            else:
                                transporter_id = False
                            project_task_vals = {
                                                # 'project_task_old_id': project_task_old_id,
                                                 # 'sequence': sequence,
                                                'assigned_interpreters': [(6, 0, interpreter_ids)],
                                                'supp_invoice_ids': [(6, 0, supp_invoice_ids)],
                                                 'color': project_task_rec.color,
                                                 'date_end': project_task_rec.date_end,
                                                 'planned_hours': project_task_rec.planned_hours,
                                                 'partner_id': partner_id,
                                                 'user_id': user_id,
                                                 'date_start': project_task_rec.date_start,
                                                 'company_id': company_id,
                                                 'priority': project_task_rec.priority,
                                                 'state': project_task_rec.state,
                                                 'description': project_task_rec.description,
                                                 'kanban_state': project_task_rec.kanban_state,
                                                 'active': project_task_rec.active,
                                                 'stage_id': stage_id,
                                                 'name': project_task_rec.name,
                                                 'date_deadline': project_task_rec.date_deadline,
                                                 'notes': project_task_rec.notes,
                                                 'event_type': project_task_rec.event_type,
                                                 # 'task_id': task_id,
                                                 'event_id': event_id,
                                                 'transporter_id': transporter_id,
                                                 'billing_state': project_task_rec.billing_state,
                                                 'cust_invoice_id': cust_invoice_id,
                                                 'supp_invoice_id2': supp_invoice_id2,
                                                 'user_id_int': user_id_int_id,
                                                 'view_interpreter': view_interpreter,
                                                 'current_time': project_task_rec.current_time,
                                                 # 'timesheet_attachment': timesheet_attachment,
                                                 'attachment_filename': project_task_rec.attachment_filename,
                                                     }
                            result = sock.execute(dbname, d_uid, pwd, 'project.task', 'write',[project_task_rec.project_task_old_id], project_task_vals)
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model=='project.task.work':
                        try:
                            task_work_id = self.env['project.task.work'].browse(rec.res_id)
                            if task_work_id.task_id:
                                task_id = task_work_id.task_id.project_task_old_id
                            else:
                                task_id = False
                            if task_work_id.company_id:
                                company_id = task_work_id.company_id.res_company_old_id
                            else:
                                company_id = False

                            if task_work_id.interpreter_id:
                                interpreter_id = task_work_id.interpreter_id.customer_record_old_id
                            else:
                                interpreter_id = False
                            if task_work_id.event_out_come_id:
                                event_out_come_id = task_work_id.event_out_come_id.event_outcome_old_id
                            else:
                                event_out_come_id = False
                            if task_work_id.user_id:
                                user_id = task_work_id.user_id.user_old_id
                            else:
                                user_id = False
                            project_task_work_vals = {
                                'user_id': user_id,
                                'name': task_work_id.name,
                                'task_id': task_id,
                                'date': task_work_id.date,
                                'company_id': company_id,
                                'total_mileage_covered': task_work_id.total_mileage_covered,
                                'hours_spend': task_work_id.hours_spend,
                                'event_start_time': task_work_id.event_start_time,
                                'event_end_time': task_work_id.event_end_time,
                                'task_for': task_work_id.task_for,
                                'am_pm2': task_work_id.am_pm2,
                                'am_pm': task_work_id.am_pm,
                                'event_start_date': task_work_id.event_start_date,
                                'wait_time_bill': task_work_id.wait_time_bill,
                                'wait_time': task_work_id.wait_time,
                                'interpreter_id': interpreter_id,
                                'event_out_come_id': event_out_come_id,
                                'event_start_hr': task_work_id.event_start_hr,
                                'event_end_hr': task_work_id.event_end_hr,
                                'event_end_min': task_work_id.event_end_min,
                                'event_start_min': task_work_id.event_start_min,
                                'edited': task_work_id.edited,
                                'travel_time': task_work_id.travel_time,
                            }
                            result = sock.execute(dbname, d_uid, pwd, 'project.task.work',
                                                                    'write',[task_work_id.project_task_work_old_id],
                                                                    project_task_work_vals)

                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error':e})
                            self._cr.commit()
                elif rec.method == 'unlink':
                    if rec.model_id.model == 'project.task':
                        try:
                            project_task_rec = self.env['project.task'].browse(rec.res_id)
                            result = sock.execute(dbname, d_uid, pwd, 'project.task', 'unlink',
                                              [project_task_rec.project_task_old_id])
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
                    elif rec.model_id.model == 'project.task.work':
                        try:
                            task_work_id = self.env['project.task.work'].browse(rec.res_id)
                            result = sock.execute(dbname, d_uid, pwd, 'project.task.work', 'unlink',
                                              [task_work_id.project_task_work_old_id])
                            rec.write({'sync': True})
                            self._cr.commit()
                        except Exception as e:
                            rec.write({'error': str(e)})
                            self._cr.commit()
