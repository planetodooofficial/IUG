from odoo import api,fields,models

class Res_company(models.Model):
    _inherit="res.company"

    res_company_old_id=fields.Integer("Company Old ID:",index=True)

class Customer_group(models.Model):
    _inherit="customer.group"

    customer_group_old_id=fields.Integer("Customer Group Old ID:",index=True)

class Document_status(models.Model):
    _inherit="document.status"

    document_status_old_id=fields.Integer("Document Status Old ID:",index=True)

class Appointment_group_type(models.Model):
    _inherit="appointment.type.group"

    appointment_type_group_old_id=fields.Integer("Appointment Type Group Old ID:",index=True)

class Certification_level(models.Model):
    _inherit="certification.level"

    certification_level_old_id=fields.Integer("Certification Level Old ID:",index=True)

class Document_to_event(models.Model):
    _inherit="document.to.event"

    document_to_event_old_id=fields.Integer("Document Event Old ID:",index=True)

class Event_out_come(models.Model):
    _inherit="event.out.come"

    event_outcome_old_id=fields.Integer("Event Outcome Old ID:",index=True)

class Iu_contract(models.Model):
    _inherit="iu.contract"

    iu_contract_old_id=fields.Integer("IU Contract Old ID:",index=True)

class Document_type(models.Model):
    _inherit="document.type"

    document_type_old_id=fields.Integer("Document Type Old ID:",index=True)

class Document(models.Model):
    _inherit="document"

    document_old_id=fields.Integer("Document Old ID:",index=True)

class ResTitle(models.Model):
    _inherit="res.partner.title"

    res_title_old_id=fields.Integer("Title Old ID:",index=True)

class StateCustom(models.Model):
    _inherit = "res.country.state"

    state7_id=fields.Integer("State Old ID",index=True)

class Zip_code(models.Model):
    _inherit="zip.code"

    zip_code_old_id=fields.Integer("Zip Code Old ID:",index=True)

class Degree_type(models.Model):
    _inherit="degree.type"

    degree_type_old_id=fields.Integer("Degree Type Old ID:",index=True)

class Degree_subject(models.Model):
    _inherit="degree.subject"

    degree_subject_old_id=fields.Integer("Degree Subject Old ID:",index=True)

class Rate(models.Model):
    _inherit="rate"

    rate_old_id=fields.Integer("Rate Old ID:",index=True)

class Language(models.Model):
    _inherit = "language"

    language_old_id = fields.Integer("Language Old ID:",index=True)

class Zone(models.Model):
    _inherit = "zone"

    zone_old_id = fields.Integer("Zone Old ID:",index=True)

class Meta_zone(models.Model):
    _inherit = "meta.zone"

    meta_zone_old_id = fields.Integer("Meta-Zone Old ID:",index=True)

class Hr_employee(models.Model):
    _inherit='hr.employee'

    employee_old_id = fields.Integer("employee Old ID:",index=True)

class Fee_note_status(models.Model):
    _inherit = "fee.note.status"

    fee_note_status_old_id = fields.Integer("Fee Note Status Old ID:",index=True)


class ResPartnerCustomNew(models.Model):
    _inherit = "res.partner"

    customer_record_old_id = fields.Integer("Customer Old ID:",index=True)
    opt_for_sms=fields.Boolean('opt for sms')

class AccountInvoiceLineCust(models.Model):
    _inherit = "account.invoice.line"

    invoice_line_old_id = fields.Integer("Account Invoice line Old ID:",index=True)


class Doctor(models.Model):
    _inherit = "doctor"

    doctor_old_id = fields.Integer("Doctor Old ID:",index=True)

class Speciality(models.Model):
    _inherit = "speciality"

    speciality_old_id = fields.Integer("Speciality Old ID:",index=True)

class Locations(models.Model):
    _inherit = "location"
    location_old_id = fields.Integer("Location Old ID:",index=True)

class Patient(models.Model):
    _inherit = "patient"

    patient_old_id = fields.Integer("Patient Old ID:",index=True)

class TrasporterHistory(models.Model):
    _inherit = "transporter.alloc.history"

    transporter_alloc_history_old_id = fields.Integer("TrasporterHistory Old ID:",index=True)

class CancelReason(models.Model):
    _inherit = "cancel.reason"

    cancel_reason_old_id = fields.Integer("TrasporterHistory Old ID:",index=True)

class AssignTranslatorHis(models.Model):
    _inherit = "assign.translator.history"

    assign_translator_history_old_id = fields.Integer("Assign Translator His Old ID:",index=True)

class EventCust(models.Model):
    _inherit = "event"

    event_old_id = fields.Integer("Assign Translator His Old ID:",index=True)

class Translator_language(models.Model):
    _inherit = "translator.language"

    translator_language_old_id = fields.Integer("Translator Language Old ID:",index=True)


class Translator_certification(models.Model):
    _inherit = "translator.certification"

    translator_certification_old_id = fields.Integer("Translator Certification Old ID:",index=True)

class Software(models.Model):
    _inherit = "software"

    software_old_id = fields.Integer("Software Old ID:",index=True)

class Interpreter_language(models.Model):
    _inherit = "interpreter.language"

    interpret_language_old_id = fields.Integer("Interpreter Language Old ID:",index=True)

class CancelledEvent(models.Model):
    _inherit = "cancelled.event"

    cancel_event_old_id = fields.Integer("Cancelled Event Old ID:",index=True)

class PhoneType(models.Model):

    _inherit="phone.type"

    phone_type_old_id=fields.Integer("Phone Type Old ID:",index=True)

class Zip_time_zone(models.Model):
    _inherit = "zip.time.zone"

    zip_time_zone_old_id = fields.Integer("Zip Time Zone Old ID:",index=True)

class Resource(models.Model):
    _inherit = "resource.resource"

    resource_old_id = fields.Integer("Resource Old ID:",index=True)


class Twilio_acciunt(models.Model):
    _inherit = "twilio.accounts"

    twilio_acc_old_id = fields.Integer("Twilio Acc Old ID:",index=True)

class Twilio_sms_send(models.Model):
    _inherit = "twilio.sms.send"

    twilio_sms_send_old_id = fields.Integer("Twilio Sms Send Old ID:",index=True)

class Twilio_sms_received(models.Model):
    _inherit = "twilio.sms.received"

    twilio_sms_received_old_id = fields.Integer("Twilio Sms Received Old ID:", index=True)

class Mail_message(models.Model):
    _inherit = "mail.message"

    mail_message_old_id = fields.Integer("Mail Message Old ID:", index=True)

class Select_interpreter_line(models.Model):
    _inherit = "select.interpreter.line"

    interpreter_line_old_id = fields.Integer("Interpreter Line Old ID:", index=True)

class Select_translator_line(models.Model):
    _inherit = "select.translator.line"

    translator_line_old_id = fields.Integer("Translator Line Old ID:",index=True)

class Interpreter_alloc_history(models.Model):
    _inherit = "interpreter.alloc.history"

    interpreter_alloc_his_old_id = fields.Integer("Interpreter Alloc History Old ID:", index=True)

class Translator_alloc_history(models.Model):
    _inherit = "translator.alloc.history"

    translator_alloc_his_old_id = fields.Integer("Translator Alloc History Old ID:", index=True)

class Project_task(models.Model):
    _inherit = "project.task"

    project_task_old_id = fields.Integer("Project Task Old ID:", index=True)
    priority = fields.Selection([('4', 'Very Low'), ('3', 'Low'), ('2', 'Medium'), ('1', 'Important'), ('0', 'Very important')], 'Priority',index=True)

class ResUserCust(models.Model):
    _inherit='res.users'

    user_old_id=fields.Integer("User Old ID:", index=True)

class Account_invoice(models.Model):
    _inherit = "account.invoice"

    invoice_old_id = fields.Integer("Invoice Old ID:", index=True)
    invoice_old_number=fields.Char("Old Invoice Number")


class Project_task_work(models.Model):
    _inherit = "project.task.work"

    project_task_work_old_id = fields.Integer("Project Task Work Old ID:", index=True)

class Project_task_type(models.Model):
    _inherit = "project.task.type"

    project_task_type_old_id = fields.Integer("Project Task Type Old ID:", index=True)

class Account(models.Model):
    _inherit = "account.account"

    account_old_id = fields.Integer("Account Old ID:", index=True)

class Account_journal(models.Model):
    _inherit = "account.journal"

    account_journal_old_id = fields.Integer("Account Journal Old ID:", index=True)

class Billing_form(models.Model):
    _inherit = "billing.form"

    billing_form_old_id = fields.Integer("Billing Form Old ID:", index=True)

class Event_lines(models.Model):
    _inherit = "event.lines"

    event_lines_old_id = fields.Integer("Event Lines Old ID:", index=True)

class AccPeriod(models.Model):
    _inherit='account.period'

    period_old_id=fields.Integer("Period Old ID:", index=True)

class AccFiscalYear(models.Model):
    _inherit='account.fiscalyear'

    account_fiscalyear_old_id=fields.Integer("Fiscal Year Old ID:", index=True)

class Ir_Attachment(models.Model):
    _inherit = "ir.attachment"

    res_old_id = fields.Integer("Res Old ID:", index=True)
    ir_attach_old_id=fields.Integer("Ir attachment old id", index=True)

class ProductTemp(models.Model):
    _inherit='product.product'

    product_old_id=fields.Integer("Product Old ID:", index=True)

class AccMove(models.Model):
    _inherit='account.move'
    account_mov_old_id=fields.Integer("Account Move Old ID:", index=True)

class AccMoveLine(models.Model):
    _inherit='account.move.line'
    move_line_old_id=fields.Integer("Account Move Line Old ID:", index=True)

class AppointmentType(models.Model):
    _inherit='appointment.type'
    app_type_old_id=fields.Integer("Appointment Type Old ID:", index=True)

class Project(models.Model):
    _inherit='project'
    iug_project_old_id=fields.Integer("IUG Project Old ID:", index=True)

class Group(models.Model):
    _inherit='res.groups'
    group_old_id=fields.Integer("Group Old ID:", index=True)

class InterHistory(models.Model):
    _inherit='interpreter.history'
    inter_his_old_id=fields.Integer("Interpreter History Old ID:", index=True)

class Affliation(models.Model):
    _inherit='affiliation'
    affiliation_old_id = fields.Integer("Interpreter History Old ID:", index=True)

class Incoming_fax(models.Model):
    _inherit='incoming.fax'
    fax_in_old_id=fields.Integer("Group Old ID:", index=True)

class Assign_translator_history(models.Model):
    _inherit='assign.translator.history'
    assign_trans_his_old_id=fields.Integer("Group Old ID:", index=True)

class Iu_message(models.Model):
    _inherit='iu.message'
    iu_message_old_id=fields.Integer("Iu Message Old ID:", index=True)

class Document_sender(models.Model):
    _inherit='document.sender'
    document_sender_old_id=fields.Integer("Document Sender Old ID:", index=True)

class Document_recipient (models.Model):
    _inherit='document.recipient'
    document_recipient_old_id=fields.Integer("Document Recipient Old ID:", index=True)

class EventInterCalendar (models.Model):
    _inherit='event.interpreter.calendar'
    event_intr_calendar_old_id=fields.Integer("Event Interpreter Calendar Old ID:", index=True)

class BilingRule (models.Model):
    _inherit='billing.rule'
    billing_rule_old_id=fields.Integer("Billing Rule Old ID:", index=True)

class AccountPayment(models.Model):
    _inherit='account.payment'

    sync=fields.Boolean("Synced", index=True)

