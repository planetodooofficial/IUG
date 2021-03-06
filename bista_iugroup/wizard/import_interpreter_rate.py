import xlrd
import base64
from odoo.tools.translate import _
from odoo import models, fields,api
from odoo.exceptions import UserError


class import_interpreter_rate(models.TransientModel):
    """ Import Inerpreter Rate Excel sheet to corresponding rates """
    _name = "import.interpreter.rate"
    _description = "Import Interperter Rates"

    excel_file=fields.Binary('Excel file', required=True)
    file_name=fields.Char('Attachment Name', size=64)

    @api.model
    def get_test_file_path(self):
        """Return the test file path"""
        proxy = self.env['ir.config_parameter']
        file_path = proxy.sudo().get_param('test_file_path')
        if not file_path:
            raise UserError(_('Please configure test_file_path as "/home/openerp/" in config parameters.'))
        if file_path.endswith('/'):
            file_path += 'test.xls'
        else:
            file_path += '/test.xls'
        return file_path

    @api.model
    def mark_health_and_human(self):
        '''Code to import excel of Health & Human List and Set order note and Mental Program'''
        data = self
        if not data.excel_file:
            raise UserError(_('Please select a Excel file'))
        if data.file_name:
            if not data.file_name.lower().endswith(('.xls', '.xlsx')):
                raise UserError(_('Unsupported File Format.'))
        module_data = data.excel_file
        file = base64.decodestring(module_data)
        part_ids = []
        iug_part_fail_ids = []
        asit_part_fail_ids = []
        
        partner_obj = self.env['res.partner']
#        rate_obj = self.pool.get('rate')
        file_path = self.get_test_file_path()
        fp = open(file_path,'wb')
        fp.write(file)
        fp.close()
        book=xlrd.open_workbook(file_path,encoding_override='utf8')
        sh=book.sheet_by_index(0)
        
        customer_name = 0
        customer_id = 1
        contact_name = 2
        contact_id = 3
        if not self._context.get('mental_prog',False):
            return True
        mental_prog = self._context.get('mental_prog','adult')
        print "Health and Human sh.nrows..........",sh.nrows
        for line in range (1,sh.nrows):
            print "line.........",line
            row = sh.row_values(line)
            if row !='':
                partner_ids = []

                cust_id = row[customer_id]
                try:
                    cust_id = int(float(cust_id))
                except Exception , e:
                    print "Customer Id is not present in line no %s , so skipping. ",line
                    continue
#          ++++++++++ For IUG-SD Company +++++++++++++++++
                partner_ids = partner_obj.search([('customer_id','=',int(cust_id)),('company_id','=',6),('active','in',('False','True'))])
                print "IUG-SD partner_ids..........",partner_ids
                if partner_ids != []:
                    part_ids.append(partner_ids[0].id)
                    partner_ids[0].write({'order_note': True, 'mental_prog': mental_prog})
                else:
                    iug_part_fail_ids.append(line)
#          ++++++++++ For ASIT Company +++++++++++++++++
                partner_ids = partner_obj.search([('customer_id','=',int(cust_id)),('company_id','=',4),('active','in',('False','True'))])
                print "ASIT partner_ids..........",partner_ids
                if partner_ids != []:
                    part_ids.append(partner_ids[0].id)
                    partner_ids[0].write({'order_note': True, 'mental_prog': mental_prog})
                else:
                    asit_part_fail_ids.append(line)
                if int(line) % 100 == 0:
                    print "line  commit ...",line
                    self._cr.commit()
        print "asit_part_fail_ids.......",asit_part_fail_ids
        print "iug_part_fail_ids.......",iug_part_fail_ids
        res = {
            'domain': str([('id','in',part_ids)]),
            'name': 'Customers',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'res.partner',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
        return res

    @api.model
    def import_excel_interpreter(self):
        '''Code to import excel of interpreter rates and enter those into corresponding rates'''
        data = self
        if not data.excel_file:
            raise UserError(_('Please select a Excel file'))
        if data.file_name:
            if not data.file_name.lower().endswith(('.xls', '.xlsx')):
                raise UserError(_('Unsupported File Format.'))
        module_data = data.excel_file
        file = base64.decodestring(module_data)
        
        part_ids = []
        iug_part_fail_ids = []
        asit_part_fail_ids = []

        partner_obj = self.env['res.partner']
#        rate_obj = self.pool.get('rate')
        file_path = self.get_test_file_path()
        fp = open(file_path,'wb' )
        fp.write(file)
        fp.close()
        book=xlrd.open_workbook(file_path ,encoding_override='utf8')
        sh=book.sheet_by_index(0)
#        print "sh+++++++",sh.colinfo_map
#        row = sh.row_values(2)
#        print "row1+++++++++++",row
        inactive = 0
        vid = 1
        name = 2
        
        n_base_hour = 3
        n_base_min = 4
        n_rate_default = 5
        n_rate_exotic_certified = 6
        n_rate_exotic_high = 7
        n_rate_exotic_middle = 8
        n_rate_exotic_regular = 9
        n_rate_spanish_certified = 10
        n_rate_spanish_licenced = 11
        n_rate_spanish_regular = 12
        
        m_base_hour = 13
        m_base_min = 14
        m_rate_default = 15
        m_rate_exotic_certified = 16
        m_rate_exotic_high = 17
        m_rate_exotic_middle = 18
        m_rate_exotic_regular = 19
        m_rate_spanish_certified = 20
        m_rate_spanish_licenced = 21
        m_rate_spanish_regular = 22

        d_base_hour = 23
        d_base_min = 24
        d_rate_default = 25
        d_rate_exotic_certified = 26
        d_rate_exotic_high = 27
        d_rate_exotic_middle = 28
        d_rate_exotic_regular = 29
        d_rate_spanish_certified = 30
        d_rate_spanish_licenced = 31
        d_rate_spanish_regular = 32
        
        c_base_hour = 33
        c_base_min = 34
        c_rate_default = 35
        c_rate_exotic_certified = 36
        c_rate_exotic_high = 37
        c_rate_exotic_middle = 38
        c_rate_exotic_regular = 39
        c_rate_spanish_certified = 40
        c_rate_spanish_licenced = 41
        c_rate_spanish_regular = 42

        print "Interpreter Rate sh.nrows..........",sh.nrows
        for line in range (1,sh.nrows):
                print "line.........",line
#            try:
                row = sh.row_values(line)
                #print "row............",row
#                row2 = [str(x).encode('utf-8', 'replace') for x in row]
#                row2 = []
#                count = 0
#                for x in row:
#                    count += 1
#                    if count == 1:
#                        row2.append('ID')
#                    elif count == 3:
#                        row2.append('name')
#                    else:
#                        row2.append(x)
                #print "row2...........",row2
#                row = [str(x).encode('utf-8', 'replace') for x in row2]
#                print "row........",row
                #print "row[vid]...........",row[vid],type(row[vid])
                if row !='':
                    partner_ids = []

                    v_id = row[vid]
                    try:
                        v_id = int(float(v_id))
                    except Exception , e:
                        print "Vendor Id is not present in line no %s , so skipping. ",line
                        continue
#          ++++++++++ For IUG-SD Company +++++++++++++++++
                    is_active = False if row[inactive] == 1 else True
                    partner_ids = partner_obj.search([('vendor_id','=',int(v_id)),('company_id','=',6),('active','in',('False','True'))])
                    print "IUG-SD Vendor_ids..........",partner_ids
                    if partner_ids != []:
                        part_ids.append(partner_ids[0].id)
#                       +++++++++++++++++ Normal +++++++++++++
                        dummy_base_hour = int(float(row[n_base_hour])) or 0
                        dummy_base_min =  int(float(row[n_base_min])) or 0
                        #print "normal_base_hour....normal_base_min...",dummy_base_hour,dummy_base_min
                        hour , min , base_hour , base_min = 0 , 0 , False , False
                        if dummy_base_hour > 0:
                            hour = int(dummy_base_hour / 60)
                        else:
                            hour = 0
                        if hour == 0:
                            base_hour = False
                        elif hour == 1:
                            base_hour = '1hour'
                        elif hour == 2:
                            base_hour = '2hour'
                        else:
                            base_hour = '3hour'
                        
                        if dummy_base_min > 0:
                            min = int(dummy_base_min / 15)
                        else:
                            min = 0
                        if min == 0:
                            base_min = False
                        elif min == 1:
                            base_min = '15min'
                        else:
                            base_min = '30min'
                        #print "base_hour..base_min........",base_hour,base_min
                        res = {
                              'base_hour':        base_hour or False,
                              'inc_min':          base_min or '30min',
                              'rate_type':        'normal',
                              'default_rate' :    float(row[n_rate_default]) or 0.0,
                              'spanish_regular':  float(row[n_rate_spanish_regular]) or 0.0,
                              'spanish_licenced': float(row[n_rate_spanish_licenced]) or 0.0,
                              'spanish_certified':float(row[n_rate_spanish_certified]) or 0.0,
                              'exotic_regular':   float(row[n_rate_exotic_regular]) or 0.0,
                              'exotic_certified': float(row[n_rate_exotic_certified]) or 0.0,
                              'exotic_middle':    float(row[n_rate_exotic_middle]) or 0.0,
                              'exotic_high':      float(row[n_rate_exotic_high]) or 0.0,
                        }
                        partner_ids[0].write({'is_interpretation_active': is_active, 'rate_ids': [(0, False, res)]})
#       ++++++++++++++++++++++++ Medical  +++++++++++++++++
                        dummy_base_hour , dummy_base_min = 0 , 0
                        dummy_base_hour = int(float(row[m_base_hour])) or 0
                        dummy_base_min =  int(float(row[m_base_min])) or 0
                        #print "medical_base_hour....medical_base_min...",dummy_base_hour,dummy_base_min
                        hour , min , base_hour , base_min = 0 , 0 , False , False
                        if dummy_base_hour > 0:
                            hour = int(dummy_base_hour / 60)
                        else:
                            hour = 0
                        if hour == 0:
                            base_hour = False
                        elif hour == 1:
                            base_hour = '1hour'
                        elif hour == 2:
                            base_hour = '2hour'
                        else:
                            base_hour = '3hour'
                        
                        if dummy_base_min > 0:
                            min = int(dummy_base_min / 15)
                        else:
                            min = 0
                        if min == 0:
                            base_min = False
                        elif min == 1:
                            base_min = '15min'
                        else:
                            base_min = '30min'
                        #print " medical base_hour..base_min........",base_hour,base_min
                        partner_ids[0].write({'is_interpretation_active': is_active, 'rate_ids': [(0,False,{
                              'base_hour':        base_hour or False ,
                              'inc_min':          base_min or '30min',
                              'rate_type':        'medical',
                              'default_rate' :    float(row[m_rate_default]) or 0.0,
                              'spanish_regular':  float(row[m_rate_spanish_regular]) or 0.0,
                              'spanish_licenced': float(row[m_rate_spanish_licenced]) or 0.0,
                              'spanish_certified':float(row[m_rate_spanish_certified]) or 0.0,
                              'exotic_regular':   float(row[m_rate_exotic_regular]) or 0.0,
                              'exotic_certified': float(row[m_rate_exotic_certified]) or 0.0,
                              'exotic_middle':    float(row[m_rate_exotic_middle]) or 0.0,
                              'exotic_high':      float(row[m_rate_exotic_high]) or 0.0,
                        })]})
#       ++++++++++++++++++++++++ Deposition  +++++++++++++++++
                        dummy_base_hour , dummy_base_min = 0 , 0
                        dummy_base_hour = int(float(row[d_base_hour])) or 0
                        dummy_base_min =  int(float(row[d_base_min])) or 0
                        #print "depos_base_hour....depos_base_min...",dummy_base_hour,dummy_base_min
                        hour , min , base_hour , base_min = 0 , 0 , False , False
                        if dummy_base_hour > 0:
                            hour = int(dummy_base_hour / 60)
                        else:
                            hour = 0
                        if hour == 0:
                            base_hour = False
                        elif hour == 1:
                            base_hour = '1hour'
                        elif hour == 2:
                            base_hour = '2hour'
                        else:
                            base_hour = '3hour'

                        if dummy_base_min > 0:
                            min = int(dummy_base_min / 15)
                        else:
                            min = 0
                        if min == 0:
                            base_min = False
                        elif min == 1:
                            base_min = '15min'
                        else:
                            base_min = '30min'
                        #print " Depos base_hour..base_min........",base_hour,base_min
#                        res = partner_obj.read(cr, uid, [partner_ids[0]], ['company_id'], context)
                        partner_ids[0].write({'is_interpretation_active': is_active, 'rate_ids': [(0,False,{
                              'base_hour':        base_hour or False ,
                              'inc_min':          base_min or '30min',
                              'rate_type':        'deposition',
                              'default_rate' :    float(row[d_rate_default]) or 0.0,
                              'spanish_regular':  float(row[d_rate_spanish_regular]) or 0.0,
                              'spanish_licenced': float(row[d_rate_spanish_licenced]) or 0.0,
                              'spanish_certified':float(row[d_rate_spanish_certified]) or 0.0,
                              'exotic_regular':   float(row[d_rate_exotic_regular]) or 0.0,
                              'exotic_certified': float(row[d_rate_exotic_certified]) or 0.0,
                              'exotic_middle':    float(row[d_rate_exotic_middle]) or 0.0,
                              'exotic_high':      float(row[d_rate_exotic_high]) or 0.0,
                        })]})

#       ++++++++++++++++++++++++ Conf Call  +++++++++++++++++
                        dummy_base_hour , dummy_base_min = 0 , 0
                        dummy_base_hour = int(float(row[c_base_hour])) or 0
                        dummy_base_min =  int(float(row[c_base_min])) or 0
                        #print "Conf Call base_hour....base_min...",dummy_base_hour,dummy_base_min
                        hour , min , base_hour , base_min = 0 , 0 , False , False
                        if dummy_base_hour > 0:
                            hour = int(dummy_base_hour / 60)
                        else:
                            hour = 0
                        if hour == 0:
                            base_hour = False
                        elif hour == 1:
                            base_hour = '1hour'
                        elif hour == 2:
                            base_hour = '2hour'
                        else:
                            base_hour = '3hour'

                        if dummy_base_min > 0:
                            min = int(dummy_base_min / 15)
                        else:
                            min = 0
                        if min == 0:
                            base_min = False
                        elif min == 1:
                            base_min = '15min'
                        else:
                            base_min = '30min'
                        #print " Conf Call base_hour..base_min........",base_hour,base_min
#                        res = partner_obj.read(cr, uid, [partner_ids[0]], ['company_id'], context)
                        partner_ids[0].write({'is_interpretation_active': is_active, 'rate_ids': [(0, False ,{
                              'base_hour':        base_hour or False ,
                              'inc_min':          base_min or '30min',
                              'rate_type':        'conf_call',
                              'default_rate' :    float(row[c_rate_default]) or 0.0,
                              'spanish_regular':  float(row[c_rate_spanish_regular]) or 0.0,
                              'spanish_licenced': float(row[c_rate_spanish_licenced]) or 0.0,
                              'spanish_certified':float(row[c_rate_spanish_certified]) or 0.0,
                              'exotic_regular':   float(row[c_rate_exotic_regular]) or 0.0,
                              'exotic_certified': float(row[c_rate_exotic_certified]) or 0.0,
                              'exotic_middle':    float(row[c_rate_exotic_middle]) or 0.0,
                              'exotic_high':      float(row[c_rate_exotic_high]) or 0.0,
                        })]})
                    else:
                        iug_part_fail_ids.append(line)
#  For Company ASIT ++++++++++++++++++++++++++++++++
                    partner_ids = []
                    partner_ids = partner_obj.search([('vendor_id','=',int(v_id)),('company_id','=',4),('active','in',('False','True'))])
                    print "ASIT vendor_ids..........",partner_ids
                    if partner_ids != []:
                        part_ids.append(partner_ids[0].id)
#                       +++++++++++++++++ Normal +++++++++++++
                        dummy_base_hour = int(float(row[n_base_hour])) or 0
                        dummy_base_min =  int(float(row[n_base_min])) or 0
                        #print "normal_base_hour....normal_base_min...",dummy_base_hour,dummy_base_min
                        hour , min , base_hour , base_min = 0 , 0 , False , False
                        if dummy_base_hour > 0:
                            hour = int(dummy_base_hour / 60)
                        else:
                            hour = 0
                        if hour == 0:
                            base_hour = False
                        elif hour == 1:
                            base_hour = '1hour'
                        elif hour == 2:
                            base_hour = '2hour'
                        else:
                            base_hour = '3hour'

                        if dummy_base_min > 0:
                            min = int(dummy_base_min / 15)
                        else:
                            min = 0
                        if min == 0:
                            base_min = False
                        elif min == 1:
                            base_min = '15min'
                        else:
                            base_min = '30min'
                        #print "base_hour..base_min........",base_hour,base_min
#                        res = partner_obj.read(cr, uid, [partner_ids[0]], ['company_id'], context)
                        partner_ids[0].write({'is_interpretation_active': is_active, 'rate_ids':  [(0,False,{
                              'base_hour':        base_hour or False ,
                              'inc_min':          base_min or '30min',
                              'rate_type':        'normal',
                              'default_rate' :    float(row[n_rate_default]) or 0.0,
                              'spanish_regular':  float(row[n_rate_spanish_regular]) or 0.0,
                              'spanish_licenced': float(row[n_rate_spanish_licenced]) or 0.0,
                              'spanish_certified':float(row[n_rate_spanish_certified]) or 0.0,
                              'exotic_regular':   float(row[n_rate_exotic_regular]) or 0.0,
                              'exotic_certified': float(row[n_rate_exotic_certified]) or 0.0,
                              'exotic_middle':    float(row[n_rate_exotic_middle]) or 0.0,
                              'exotic_high':      float(row[n_rate_exotic_high]) or 0.0,
#                              'company_id': res['company_id'],
                              })]})
#       ++++++++++++++++++++++++ Medical  +++++++++++++++++
                        dummy_base_hour , dummy_base_min = 0 , 0
                        dummy_base_hour = int(float(row[m_base_hour])) or 0
                        dummy_base_min =  int(float(row[m_base_min])) or 0
                        #print "medical_base_hour....medical_base_min...",dummy_base_hour,dummy_base_min
                        hour , min , base_hour , base_min = 0 , 0 , False , False
                        if dummy_base_hour > 0:
                            hour = int(dummy_base_hour / 60)
                        else:
                            hour = 0
                        if hour == 0:
                            base_hour = False
                        elif hour == 1:
                            base_hour = '1hour'
                        elif hour == 2:
                            base_hour = '2hour'
                        else:
                            base_hour = '3hour'

                        if dummy_base_min > 0:
                            min = int(dummy_base_min / 15)
                        else:
                            min = 0
                        if min == 0:
                            base_min = False
                        elif min == 1:
                            base_min = '15min'
                        else:
                            base_min = '30min'
                        #print " medical base_hour..base_min........",base_hour,base_min
#                        res = partner_obj.read(cr, uid, [partner_ids[0]], ['company_id'], context)
                        partner_ids[0].write({'is_interpretation_active': is_active, 'rate_ids': [(0 ,False ,{
                              'base_hour':        base_hour or False ,
                              'inc_min':          base_min or '30min',
                              'rate_type':        'medical',
                              'default_rate' :    float(row[m_rate_default]) or 0.0,
                              'spanish_regular':  float(row[m_rate_spanish_regular]) or 0.0,
                              'spanish_licenced': float(row[m_rate_spanish_licenced]) or 0.0,
                              'spanish_certified':float(row[m_rate_spanish_certified]) or 0.0,
                              'exotic_regular':   float(row[m_rate_exotic_regular]) or 0.0,
                              'exotic_certified': float(row[m_rate_exotic_certified]) or 0.0,
                              'exotic_middle':    float(row[m_rate_exotic_middle]) or 0.0,
                              'exotic_high':      float(row[m_rate_exotic_high]) or 0.0,
#                              'company_id': res['company_id'],
                        })]})
#       ++++++++++++++++++++++++ Deposition  +++++++++++++++++
                        dummy_base_hour , dummy_base_min = 0 , 0
                        dummy_base_hour = int(float(row[d_base_hour])) or 0
                        dummy_base_min =  int(float(row[d_base_min])) or 0
                        #print "depos_base_hour....depos_base_min...",dummy_base_hour,dummy_base_min
                        hour , min , base_hour , base_min = 0 , 0 , False , False
                        if dummy_base_hour > 0:
                            hour = int(dummy_base_hour / 60)
                        else:
                            hour = 0
                        if hour == 0:
                            base_hour = False
                        elif hour == 1:
                            base_hour = '1hour'
                        elif hour == 2:
                            base_hour = '2hour'
                        else:
                            base_hour = '3hour'

                        if dummy_base_min > 0:
                            min = int(dummy_base_min / 15)
                        else:
                            min = 0
                        if min == 0:
                            base_min = False
                        elif min == 1:
                            base_min = '15min'
                        else:
                            base_min = '30min'
                        #print " Depos base_hour..base_min........",base_hour,base_min
#                        res = partner_obj.read(cr, uid, [partner_ids[0]], ['company_id'], context)
                        partner_ids[0].write({'is_interpretation_active': is_active, 'rate_ids': [(0 ,False ,{
                              'base_hour':        base_hour or False ,
                              'inc_min':          base_min or '30min',
                              'rate_type':        'deposition',
                              'default_rate' :    float(row[d_rate_default]) or 0.0,
                              'spanish_regular':  float(row[d_rate_spanish_regular]) or 0.0,
                              'spanish_licenced': float(row[d_rate_spanish_licenced]) or 0.0,
                              'spanish_certified':float(row[d_rate_spanish_certified]) or 0.0,
                              'exotic_regular':   float(row[d_rate_exotic_regular]) or 0.0,
                              'exotic_certified': float(row[d_rate_exotic_certified]) or 0.0,
                              'exotic_middle':    float(row[d_rate_exotic_middle]) or 0.0,
                              'exotic_high':      float(row[d_rate_exotic_high]) or 0.0,
#                              'company_id': res['company_id'],
                        })]})

#       ++++++++++++++++++++++++ Conf Call  +++++++++++++++++
                        dummy_base_hour , dummy_base_min = 0 , 0
                        dummy_base_hour = int(float(row[c_base_hour])) or 0
                        dummy_base_min =  int(float(row[c_base_min])) or 0
                        #print "Conf Call base_hour....base_min...",dummy_base_hour,dummy_base_min
                        hour , min , base_hour , base_min = 0 , 0 , False , False
                        if dummy_base_hour > 0:
                            hour = int(dummy_base_hour / 60)
                        else:
                            hour = 0
                        if hour == 0:
                            base_hour = False
                        elif hour == 1:
                            base_hour = '1hour'
                        elif hour == 2:
                            base_hour = '2hour'
                        else:
                            base_hour = '3hour'

                        if dummy_base_min > 0:
                            min = int(dummy_base_min / 15)
                        else:
                            min = 0
                        if min == 0:
                            base_min = False
                        elif min == 1:
                            base_min = '15min'
                        else:
                            base_min = '30min'
                        #print " Conf Call base_hour..base_min........",base_hour,base_min
#                        res = partner_obj.read(cr, uid, [partner_ids[0]], ['company_id'], context)
                        partner_ids[0].write({'is_interpretation_active': is_active, 'rate_ids': [(0 ,False ,{
                              'base_hour':        base_hour or False ,
                              'inc_min':          base_min or '30min',
                              'rate_type':        'conf_call',
                              'default_rate' :    float(row[c_rate_default]) or 0.0,
                              'spanish_regular':  float(row[c_rate_spanish_regular]) or 0.0,
                              'spanish_licenced': float(row[c_rate_spanish_licenced]) or 0.0,
                              'spanish_certified':float(row[c_rate_spanish_certified]) or 0.0,
                              'exotic_regular':   float(row[c_rate_exotic_regular]) or 0.0,
                              'exotic_certified': float(row[c_rate_exotic_certified]) or 0.0,
                              'exotic_middle':    float(row[c_rate_exotic_middle]) or 0.0,
                              'exotic_high':      float(row[c_rate_exotic_high]) or 0.0,
#                              'company_id': res['company_id'],
                        })]})
                    else:
                        asit_part_fail_ids.append(line)
                if int(line) % 100 == 0:
                    print "line  commit ...",line
                    self._cr.commit()
#            except Exception , e:
#                print "Exception .........",e.args
        print "asit_part_fail_ids.......",asit_part_fail_ids
        print "iug_part_fail_ids.......",iug_part_fail_ids
        res = {
            'domain': str([('id','in',part_ids)]),
            'name': 'Interpreters',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'res.partner',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
        return res

    @api.model
    def import_excel_customer(self):
        '''Code to import excel of Customer rates and enter those into corresponding rates'''
        data = self
        if not data.excel_file:
            raise UserError(_('Please select a Excel file'))
        if data.file_name:
            if not data.file_name.lower().endswith(('.xls', '.xlsx')):
                raise UserError(_('Unsupported File Format.'))
        module_data = data.excel_file
        file = base64.decodestring(module_data)

        part_ids = []
        iug_part_fail_ids = []
        asit_part_fail_ids = []

        partner_obj = self.env['res.partner']
#        rate_obj = self.pool.get('rate')
        file_path = self.get_test_file_path()
        fp=open(file_path,'wb' )
        fp.write(file)
        fp.close()
        book=xlrd.open_workbook(file_path ,encoding_override='utf8')
        sh=book.sheet_by_index(0)
        
        inactive = 0
        vid = 1
        name = 2
        
        n_base_hour = 3
        n_base_min = 4
        n_rate_default = 5
        n_rate_exotic_certified = 6
        n_rate_exotic_high = 7
        n_rate_exotic_middle = 8
        n_rate_exotic_regular = 9
        n_rate_spanish_certified = 10
        n_rate_spanish_licenced = 11
        n_rate_spanish_regular = 12

        m_base_hour = 13
        m_base_min = 14
        m_rate_default = 15
        m_rate_exotic_certified = 16
        m_rate_exotic_high = 17
        m_rate_exotic_middle = 18
        m_rate_exotic_regular = 19
        m_rate_spanish_certified = 20
        m_rate_spanish_licenced = 21
        m_rate_spanish_regular = 22

        d_base_hour = 23
        d_base_min = 24
        d_rate_default = 25
        d_rate_exotic_certified = 26
        d_rate_exotic_high = 27
        d_rate_exotic_middle = 28
        d_rate_exotic_regular = 29
        d_rate_spanish_certified = 30
        d_rate_spanish_licenced = 31
        d_rate_spanish_regular = 32
        
        c_base_hour = 33
        c_base_min = 34
        c_rate_default = 35
        c_rate_exotic_certified = 36
        c_rate_exotic_high = 37
        c_rate_exotic_middle = 38
        c_rate_exotic_regular = 39
        c_rate_spanish_certified = 40
        c_rate_spanish_licenced = 41
        c_rate_spanish_regular = 42
        
        print "Customer rate sh.nrows..........",sh.nrows
        for line in range (1,sh.nrows):
                print "line.........",line
#            try:
                row = sh.row_values(line)
                #print "row............",row
#                row2 = [str(x).encode('utf-8', 'replace') for x in row]
#                row2 = []
#                count = 0
#                for x in row:
#                    count += 1
#                    if count == 1:
#                        row2.append('ID')
#                    elif count == 3:
#                        row2.append('name')
#                    else:
#                        row2.append(x)
                #print "row2...........",row2
#                row = [str(x).encode('utf-8', 'replace') for x in row2]
#                print "row........",row
                print "row[vid]...........",row[vid],type(row[vid])
                if row !='':
                    partner_ids = []
                    v_id = row[vid]
                    try:
                        v_id = int(float(v_id))
                    except Exception , e:
                        print "Partner Id is not present in line no %s , so skipping. ",line
                        continue
#          ++++++++++ For IUG-SD Company +++++++++++++++++
                    is_active = False if row[inactive] == 1 else True
                    partner_ids = partner_obj.search([('customer_id','=',int(v_id)),('company_id','=',6),('active','in',('False','True'))])
                    print "IUG-SD partner_ids..........",partner_ids
                    if partner_ids != []:
                        part_ids.append(partner_ids[0].id)
#                       +++++++++++++++++ Normal +++++++++++++
                        dummy_base_hour = int(float(row[n_base_hour])) or 0
                        dummy_base_min =  int(float(row[n_base_min])) or 0
                        #print "normal_base_hour....normal_base_min...",dummy_base_hour,dummy_base_min
                        hour , min , base_hour , base_min = 0 , 0 , False , False
                        if dummy_base_hour > 0:
                            hour = int(dummy_base_hour / 60)
                        else:
                            hour = 0
                        if hour == 0:
                            base_hour = False
                        elif hour == 1:
                            base_hour = '1hour'
                        elif hour == 2:
                            base_hour = '2hour'
                        else:
                            base_hour = '3hour'

                        if dummy_base_min > 0:
                            min = int(dummy_base_min / 15)
                        else:
                            min = 0
                        if min == 0:
                            base_min = False
                        elif min == 1:
                            base_min = '15min'
                        else:
                            base_min = '30min'
                        #print "base_hour..base_min........",base_hour,base_min
                        res = {
                          'base_hour':        base_hour or False ,
                          'inc_min':          base_min or '30min',
                          'rate_type':        'normal',
                          'default_rate' :    float(row[n_rate_default]) or 0.0,
                          'spanish_regular':  float(row[n_rate_spanish_regular]) or 0.0,
                          'spanish_licenced': float(row[n_rate_spanish_licenced]) or 0.0,
                          'spanish_certified':float(row[n_rate_spanish_certified]) or 0.0,
                          'exotic_regular':   float(row[n_rate_exotic_regular]) or 0.0,
                          'exotic_certified': float(row[n_rate_exotic_certified]) or 0.0,
                          'exotic_middle':    float(row[n_rate_exotic_middle]) or 0.0,
                          'exotic_high':      float(row[n_rate_exotic_high]) or 0.0,
                        }
                        partner_ids[0].write({'active': is_active, 'rate_ids': [(0, False, res)]})
#       ++++++++++++++++++++++++ Medical  +++++++++++++++++
                        dummy_base_hour , dummy_base_min = 0 , 0
                        dummy_base_hour = int(float(row[m_base_hour])) or 0
                        dummy_base_min =  int(float(row[m_base_min])) or 0
                        #print "medical_base_hour....medical_base_min...",dummy_base_hour,dummy_base_min
                        hour , min , base_hour , base_min = 0 , 0 , False , False
                        if dummy_base_hour > 0:
                            hour = int(dummy_base_hour / 60)
                        else:
                            hour = 0
                        if hour == 0:
                            base_hour = False
                        elif hour == 1:
                            base_hour = '1hour'
                        elif hour == 2:
                            base_hour = '2hour'
                        else:
                            base_hour = '3hour'

                        if dummy_base_min > 0:
                            min = int(dummy_base_min / 15)
                        else:
                            min = 0
                        if min == 0:
                            base_min = False
                        elif min == 1:
                            base_min = '15min'
                        else:
                            base_min = '30min'
                        #print " medical base_hour..base_min........",base_hour,base_min
#                        res = partner_obj.read(cr, uid, [partner_ids[0]], ['company_id'], context)
                        partner_ids[0].write({'active': is_active, 'rate_ids': [(0 ,False ,{
                              'base_hour':    base_hour or False ,
                              'inc_min':      base_min or '30min',
                              'rate_type':        'medical',
                              'default_rate' :    float(row[m_rate_default]) or 0.0,
                              'spanish_regular':  float(row[m_rate_spanish_regular]) or 0.0,
                              'spanish_licenced': float(row[m_rate_spanish_licenced]) or 0.0,
                              'spanish_certified':float(row[m_rate_spanish_certified]) or 0.0,
                              'exotic_regular':   float(row[m_rate_exotic_regular]) or 0.0,
                              'exotic_certified': float(row[m_rate_exotic_certified]) or 0.0,
                              'exotic_middle':    float(row[m_rate_exotic_middle]) or 0.0,
                              'exotic_high':      float(row[m_rate_exotic_high]) or 0.0,
                        })]})
#       ++++++++++++++++++++++++ Deposition  +++++++++++++++++
                        dummy_base_hour , dummy_base_min = 0 , 0
                        dummy_base_hour = int(float(row[d_base_hour])) or 0
                        dummy_base_min =  int(float(row[d_base_min])) or 0
                        #print "depos_base_hour....depos_base_min...",dummy_base_hour,dummy_base_min
                        hour , min , base_hour , base_min = 0 , 0 , False , False
                        if dummy_base_hour > 0:
                            hour = int(dummy_base_hour / 60)
                        else:
                            hour = 0
                        if hour == 0:
                            base_hour = False
                        elif hour == 1:
                            base_hour = '1hour'
                        elif hour == 2:
                            base_hour = '2hour'
                        else:
                            base_hour = '3hour'

                        if dummy_base_min > 0:
                            min = int(dummy_base_min / 15)
                        else:
                            min = 0
                        if min == 0:
                            base_min = False
                        elif min == 1:
                            base_min = '15min'
                        else:
                            base_min = '30min'
                        #print " Depos base_hour..base_min........",base_hour,base_min
                        partner_ids[0].write({'active': is_active, 'rate_ids': [(0,False,{
                              'base_hour':        base_hour or False ,
                              'inc_min':          base_min or '30min' ,
                              'rate_type':        'deposition',
                              'default_rate' :    float(row[d_rate_default]) or 0.0,
                              'spanish_regular':  float(row[d_rate_spanish_regular]) or 0.0,
                              'spanish_licenced': float(row[d_rate_spanish_licenced]) or 0.0,
                              'spanish_certified':float(row[d_rate_spanish_certified]) or 0.0,
                              'exotic_regular':   float(row[d_rate_exotic_regular]) or 0.0,
                              'exotic_certified': float(row[d_rate_exotic_certified]) or 0.0,
                              'exotic_middle':    float(row[d_rate_exotic_middle]) or 0.0,
                              'exotic_high':      float(row[d_rate_exotic_high]) or 0.0,
                        })]})

#       ++++++++++++++++++++++++ Conf Call  +++++++++++++++++
                        dummy_base_hour , dummy_base_min = 0 , 0
                        dummy_base_hour = int(float(row[c_base_hour])) or 0
                        dummy_base_min =  int(float(row[c_base_min])) or 0
                        #print "Conf Call base_hour....base_min...",dummy_base_hour,dummy_base_min
                        hour , min , base_hour , base_min = 0 , 0 , False , False
                        if dummy_base_hour > 0:
                            hour = int(dummy_base_hour / 60)
                        else:
                            hour = 0
                        if hour == 0:
                            base_hour = False
                        elif hour == 1:
                            base_hour = '1hour'
                        elif hour == 2:
                            base_hour = '2hour'
                        else:
                            base_hour = '3hour'
                        
                        if dummy_base_min > 0:
                            min = int(dummy_base_min / 15)
                        else:
                            min = 0
                        if min == 0:
                            base_min = False
                        elif min == 1:
                            base_min = '15min'
                        else:
                            base_min = '30min'
                        #print " Conf Call base_hour..base_min........",base_hour,base_min
#                        res = partner_obj.read(cr, uid, [partner_ids[0]], ['company_id'], context)
                        partner_ids[0].write({'active': is_active, 'rate_ids': [(0,False,{
                              'base_hour':        base_hour or False ,
                              'inc_min':          base_min or '30min',
                              'rate_type':        'conf_call',
                              'default_rate' :    float(row[c_rate_default]) or 0.0,
                              'spanish_regular':  float(row[c_rate_spanish_regular]) or 0.0,
                              'spanish_licenced': float(row[c_rate_spanish_licenced]) or 0.0,
                              'spanish_certified':float(row[c_rate_spanish_certified]) or 0.0,
                              'exotic_regular':   float(row[c_rate_exotic_regular]) or 0.0,
                              'exotic_certified': float(row[c_rate_exotic_certified]) or 0.0,
                              'exotic_middle':    float(row[c_rate_exotic_middle]) or 0.0,
                              'exotic_high':      float(row[c_rate_exotic_high]) or 0.0,
                        })]})
                    else:
                        iug_part_fail_ids.append(line)
#  For Company ASIT ++++++++++++++++++++++++++++++++
                    partner_ids = []
                    partner_ids = partner_obj.search([('customer_id','=',int(v_id)),('company_id','=',4),('active','in',('False','True'))])
                    print "ASIT partner_ids..........",partner_ids
                    if partner_ids != []:
                        part_ids.append(partner_ids[0].id)
#                       +++++++++++++++++ Normal +++++++++++++
                        dummy_base_hour = int(float(row[n_base_hour])) or 0
                        dummy_base_min =  int(float(row[n_base_min])) or 0
                        #print "normal_base_hour....normal_base_min...",dummy_base_hour,dummy_base_min
                        hour , min , base_hour , base_min = 0 , 0 , False , False
                        if dummy_base_hour > 0:
                            hour = int(dummy_base_hour / 60)
                        else:
                            hour = 0
                        if hour == 0:
                            base_hour = False
                        elif hour == 1:
                            base_hour = '1hour'
                        elif hour == 2:
                            base_hour = '2hour'
                        else:
                            base_hour = '3hour'

                        if dummy_base_min > 0:
                            min = int(dummy_base_min / 15)
                        else:
                            min = 0
                        if min == 0:
                            base_min = False
                        elif min == 1:
                            base_min = '15min'
                        else:
                            base_min = '30min'
                        #print "base_hour..base_min........",base_hour,base_min
#                        res = partner_obj.read(cr, uid, [partner_ids[0]], ['company_id'], context)
                        partner_ids[0].write({'active': is_active, 'rate_ids':  [(0 ,False ,{
                              'base_hour':        base_hour or False ,
                              'inc_min':          base_min or '30min',
                              'rate_type':        'normal',
                              'default_rate' :    float(row[n_rate_default]) or 0.0,
                              'spanish_regular':  float(row[n_rate_spanish_regular]) or 0.0,
                              'spanish_licenced': float(row[n_rate_spanish_licenced]) or 0.0,
                              'spanish_certified':float(row[n_rate_spanish_certified]) or 0.0,
                              'exotic_regular':   float(row[n_rate_exotic_regular]) or 0.0,
                              'exotic_certified': float(row[n_rate_exotic_certified]) or 0.0,
                              'exotic_middle':    float(row[n_rate_exotic_middle]) or 0.0,
                              'exotic_high':      float(row[n_rate_exotic_high]) or 0.0,
                              })]})
#       ++++++++++++++++++++++++ Medical  +++++++++++++++++
                        dummy_base_hour , dummy_base_min = 0 , 0
                        dummy_base_hour = int(float(row[m_base_hour])) or 0
                        dummy_base_min =  int(float(row[m_base_min])) or 0
                        #print "medical_base_hour....medical_base_min...",dummy_base_hour,dummy_base_min
                        hour , min , base_hour , base_min = 0 , 0 , False , False
                        if dummy_base_hour > 0:
                            hour = int(dummy_base_hour / 60)
                        else:
                            hour = 0
                        if hour == 0:
                            base_hour = False
                        elif hour == 1:
                            base_hour = '1hour'
                        elif hour == 2:
                            base_hour = '2hour'
                        else:
                            base_hour = '3hour'

                        if dummy_base_min > 0:
                            min = int(dummy_base_min / 15)
                        else:
                            min = 0
                        if min == 0:
                            base_min = False
                        elif min == 1:
                            base_min = '15min'
                        else:
                            base_min = '30min'
                        #print " medical base_hour..base_min........",base_hour,base_min
#                        res = partner_obj.read(cr, uid, [partner_ids[0]], ['company_id'], context)
                        partner_ids[0].write({'active': is_active, 'rate_ids': [(0,False,{
                              'base_hour':        base_hour or False ,
                              'inc_min':          base_min or '30min',
                              'rate_type':        'medical',
                              'default_rate' :    float(row[m_rate_default]) or 0.0,
                              'spanish_regular':  float(row[m_rate_spanish_regular]) or 0.0,
                              'spanish_licenced': float(row[m_rate_spanish_licenced]) or 0.0,
                              'spanish_certified':float(row[m_rate_spanish_certified]) or 0.0,
                              'exotic_regular':   float(row[m_rate_exotic_regular]) or 0.0,
                              'exotic_certified': float(row[m_rate_exotic_certified]) or 0.0,
                              'exotic_middle':    float(row[m_rate_exotic_middle]) or 0.0,
                              'exotic_high':      float(row[m_rate_exotic_high]) or 0.0,
                        })]})
#       ++++++++++++++++++++++++ Deposition  +++++++++++++++++
                        dummy_base_hour , dummy_base_min = 0 , 0
                        dummy_base_hour = int(float(row[d_base_hour])) or 0
                        dummy_base_min =  int(float(row[d_base_min])) or 0
                        #print "depos_base_hour....depos_base_min...",dummy_base_hour,dummy_base_min
                        hour , min , base_hour , base_min = 0 , 0 , False , False
                        if dummy_base_hour > 0:
                            hour = int(dummy_base_hour / 60)
                        else:
                            hour = 0
                        if hour == 0:
                            base_hour = False
                        elif hour == 1:
                            base_hour = '1hour'
                        elif hour == 2:
                            base_hour = '2hour'
                        else:
                            base_hour = '3hour'

                        if dummy_base_min > 0:
                            min = int(dummy_base_min / 15)
                        else:
                            min = 0
                        if min == 0:
                            base_min = False
                        elif min == 1:
                            base_min = '15min'
                        else:
                            base_min = '30min'
                        #print " Depos base_hour..base_min........",base_hour,base_min
                        partner_ids[0].write({'active': is_active, 'rate_ids': [(0,False,{
                              'base_hour':        base_hour or False ,
                              'inc_min':          base_min or '30min' ,
                              'rate_type':        'deposition',
                              'default_rate' :    float(row[d_rate_default]) or 0.0,
                              'spanish_regular':  float(row[d_rate_spanish_regular]) or 0.0,
                              'spanish_licenced': float(row[d_rate_spanish_licenced]) or 0.0,
                              'spanish_certified':float(row[d_rate_spanish_certified]) or 0.0,
                              'exotic_regular':   float(row[d_rate_exotic_regular]) or 0.0,
                              'exotic_certified': float(row[d_rate_exotic_certified]) or 0.0,
                              'exotic_middle':    float(row[d_rate_exotic_middle]) or 0.0,
                              'exotic_high':      float(row[d_rate_exotic_high]) or 0.0,
                        })]})

#       ++++++++++++++++++++++++ Conf Call  +++++++++++++++++
                        dummy_base_hour , dummy_base_min = 0 , 0
                        dummy_base_hour = int(float(row[c_base_hour])) or 0
                        dummy_base_min =  int(float(row[c_base_min])) or 0
                        #print "Conf Call base_hour....base_min...",dummy_base_hour,dummy_base_min
                        hour , min , base_hour , base_min = 0 , 0 , False , False
                        if dummy_base_hour > 0:
                            hour = int(dummy_base_hour / 60)
                        else:
                            hour = 0
                        if hour == 0:
                            base_hour = False
                        elif hour == 1:
                            base_hour = '1hour'
                        elif hour == 2:
                            base_hour = '2hour'
                        else:
                            base_hour = '3hour'

                        if dummy_base_min > 0:
                            min = int(dummy_base_min / 15)
                        else:
                            min = 0
                        if min == 0:
                            base_min = False
                        elif min == 1:
                            base_min = '15min'
                        else:
                            base_min = '30min'
                        #print " Conf Call base_hour..base_min........",base_hour,base_min
                        partner_ids[0].write({'active': is_active, 'rate_ids': [(0,False,{
                              'base_hour':        base_hour or False ,
                              'inc_min':          base_min or '30min' ,
                              'rate_type':        'conf_call',
                              'default_rate' :    float(row[c_rate_default]) or 0.0,
                              'spanish_regular':  float(row[c_rate_spanish_regular]) or 0.0,
                              'spanish_licenced': float(row[c_rate_spanish_licenced]) or 0.0,
                              'spanish_certified':float(row[c_rate_spanish_certified]) or 0.0,
                              'exotic_regular':   float(row[c_rate_exotic_regular]) or 0.0,
                              'exotic_certified': float(row[c_rate_exotic_certified]) or 0.0,
                              'exotic_middle':    float(row[c_rate_exotic_middle]) or 0.0,
                              'exotic_high':      float(row[c_rate_exotic_high]) or 0.0,
#                              'company_id': res['company_id'],
                        })]})
                    else:
                        asit_part_fail_ids.append(line)
#            except Exception , e:
#                print "Exception .........",e.args
                if int(line) % 100 == 0:
                    self._cr.commit()
        print "asit_part_fail_ids.......",asit_part_fail_ids
        print "iug_part_fail_ids.......",iug_part_fail_ids
        res = {
            'domain': str([('id','in',part_ids)]),
            'name': 'Interpreters',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'res.partner',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
        return res