from odoo import models


class event(models.Model):
    _inherit = 'event'
    
    # allow inherited modules to extend the query
    def _report_xls_query_extra(self):
        select_extra = ""
        join_extra = ""
        where_extra = ""
        return (select_extra, join_extra, where_extra)

    # allow inherited modules to add document references
    def _report_xls_document_extra(self):
        return "''"

    # allow inherited modules to extend the render namespace
    def _report_xls_render_space_extra_kaiser(self):
        """
        extend render namespace for use in the template 'lines', e.g.
        space_extra = {
            'partner_obj': self.pool.get('res.partner'),
        }
        return space_extra
        """
        return None
    
    # override list in inherited module to add/drop columns or change order
    def _report_xls_fields_kaiser_cancel(self):
        ''' List of Columns in the exported Excel with the sequence'''
        return [
            'event_number', 'invoice_number', 'event_outcome', 'cancel_reason','create_date', 'less_than_24_notice', 'glcode', 'nuid', 'medical_number', 
            'interpreter', 'date_service', 'requested_start_time','requested_end_time', 'start_time', 'end_time','duration', 'requester', 'location', 
            'street', 'street2', 'interpretation_city', 'rate', 'total_interpretation_cost', 'amount', 'payment_received', 'status', 'multi_type', 'comments','interpretation_type', 
            'patient_name', 'language', 'po_no', 'ordering_contact', 'billing_customer', 'billing_contact',
            'contract_no','department', 'dr_name','miles_driven', 'total_miles_rate', 'comment','patient_medical_number'
        ]
    
    # Change/Add Template entries
    def _report_xls_template_kaiser(self):
        return {}
