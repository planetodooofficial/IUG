# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from odoo.report import report_sxw

class account_invoice(report_sxw.rml_parse):
#    _inherit='account.invoice'
#    _name = 'account.invoice'
    def __init__(self, cr, uid, name, context):
        super(account_invoice, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'print_fun':self.print_fun,
            'print_comp':self.print_company_data,
        })

        
        
    def print_company_data(self,model_id):
        
        tagline='Payment reminder Please include invoice number that your are paying on your check.Thank you we are going green please provide us with your contact address {}of payment details to receive future invoice with email'.format(model_id.company_id.partner_id.email)
        return [tagline]

        
    def print_fun(self,model_id):
        res=[]
        medical_file_no, birthdate = 'Medical file no: ', 'DOB: '
        try:
            date_invoice='Invoice Date: '+model_id.date_invoice
        except Exception as e:
            date_invoice='Invoice Date: '
        try:
            if model_id.event_id:
                res['reference'] = model_id.event_id.ref or ''
            else:
                res['reference'] = ''
        except Exception as e:
            res['reference'] = ''
        try:
            if model_id.event_id:
                res['medical_no'] = model_id.event_id.medical_no or ''
            else:
                res['medical_no'] = ''
        except Exception as e:
            res['medical_no'] = ''
        try:
            if model_id.event_id and model_id.event_id.appointment_type_id:
                res['appointment_type'] = model_id.event_id.appointment_type_id.name or ''
            else:
                res['appointment_type'] = ''
        except Exception as e:
            res['appointment_type'] = ''
        try:
            interpreter='Interpretee: '+model_id.interpreter_id.name
        except Exception as e:
            interpreter='Interpretee: '
        try:
            pat_id = model_id.event_id and model_id.event_id.patient_id or False
            medical_file_no = 'Medical file no: '
            birthdate = 'DOB: '
            if pat_id:
#                if claims_val.get('claim_number'):
#                    medical_file_no='Medical file no: '+claims_val.get('claim_number')
#                elif claims_val.get('claim_no'):
#                    medical_file_no='Medical file no: '+claims_val.get('claim_no')
#                elif claims_val.get('claim_no2'):
#                    medical_file_no='Medical file no: '+claims_val.get('claim_no2')
#                else:
#                    medical_file_no='Medical file no: '
                if pat_id.birthdate:
                    birthdate='DOB: '+pat_id.birthdate
            
        except Exception as e: 
            medical_file_no='Medical file no: '
            birthdate='DOB: '
        try:
            language= 'Language: '+model_id.language_id.name
        except Exception as e:    
            language= 'Language: '

        try:
            date_of_service='Date Of Service: '+model_id.event_id.event_start_date    

        except Exception as e:      
            date_of_service='Date Of Service: '

        try:    
            service='Service: '+model_id.event_id.event_purpose
        except Exception as e:         
            service='Service: '

        try:      
            location='Location: '+model_id.location_id.name+model_id.location_id.street+model_id.location_id.country_id.name\
            +model_id.location_id.zip
        
        except Exception as e:
            location='Location: '
        try:
            requested_by='Requested by: '+model_id.event_id.ordering_partner_id.name
        except Exception as e:                    


        
            requested_by='Requested by: '        
        try:       
           
                #import ipdb;ipdb.set_trace()  
                if model_id.comment:
                    notes='Notes: '+model_id.comment 
                else:
                    notes='Notes: '
            
            
        except Exception as e:
             notes='Notes: '
        
        
                   
        res.extend([date_invoice,interpreter,medical_file_no,birthdate,language,date_of_service,service,\
                           location,requested_by])
        

        return res 
    
        
report_sxw.report_sxw(
    'report.account.invoice.translator',
    'account.invoice',
    'custom_addons/bista_iugroup/report/translator_invoice.rml',
    parser=account_invoice
)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
