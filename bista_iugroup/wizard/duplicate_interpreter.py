from odoo import fields,models,api
from odoo.tools.translate import _
import datetime
from dateutil import relativedelta
from odoo import SUPERUSER_ID, tools
from odoo.exceptions import UserError

class duplicate_interpreter(models.TransientModel):
    _name='duplicate.interpreter'

    company_id=fields.Many2one('res.company','Select Company')

    @api.multi
    def get_company(self):
        current_id = self._context.get('active_ids')
        company_obj = self
        partner_obj = self.env['res.partner']
        certificate_level = self.env['certification.level']
        lang = self.env['language']
        rating = self.env['rating']
        phone_type = self.env['phone.type']
        partner_data = partner_obj.sudo().browse(current_id[0])
        default = {}
        language_details = []
        rate_details=[]
        certify_obj = ''
        ceritfy_ids = ''
        rating_id = phone_type_id1 = phone_type_id2 = phone_type_id3 = phone_type_id4 = ''
        partner_ids = partner_obj.sudo().search([('complete_name','=',partner_data.complete_name),('company_id','=',company_obj.company_id.id)])
        if partner_ids:
            raise UserError(_('The selected company already possess the interpreter named '+partner_data.complete_name))
        else:
            for data in partner_data.language_lines:
                if data.certification_level_id:
                    certify_obj = data.certification_level_id
                    ceritfy_ids= certificate_level.sudo().search([('name','=',certify_obj.name),('company_id','=',company_obj.company_id.id)])
                lang_ids = lang.sudo().search([('name','=',data.name.name),('company_id','=',company_obj.company_id.id)])
                if lang_ids:
                    language_details.append((0,0, {
                                        'interpreter_id': current_id[0],
                                        'name':lang_ids and lang_ids[0].id  or '',
                                        'certification_level_id':ceritfy_ids and ceritfy_ids[0].id or '',
                                        'specialization':data.specialization or '',
                                        'certification_code':data.certification_code or '',
                                        'company_id':company_obj.company_id.id or '',
                                        'is_simultaneous':data.is_simultaneous or '',
                                 }))
            for rat in partner_data.rate_ids:
                if rat:
                    rate_details.append((0,0, {
                                        'partner_id': current_id[0],
                                        'rate_type':rat.rate_type or '',
                                        'base_hour':rat.base_hour or '',
                                        'inc_min':rat.inc_min or '',
                                        'default_rate':rat.default_rate or '',
                                        'spanish_regular':rat.spanish_regular or '',
                                        'spanish_licenced':rat.spanish_licenced or '',
                                        'spanish_certified':rat.spanish_certified or '',
                                        'exotic_regular':rat.exotic_regular or '',
                                        'exotic_certified':rat.exotic_certified or '',
                                        'exotic_middle':rat.exotic_middle or '',
                                        'exotic_high':rat.exotic_high or '',
                        'company_id': company_obj.company_id.id or '',
                                 }))
            if partner_data.rating_id:
                rating_id = rating.sudo().search([('name','=',partner_data.rating_id.name),('company_id','=',company_obj.company_id.id)])

            if partner_data.phone_type_id1:
                phone_type_id1 = phone_type.sudo().search([('name','=',partner_data.phone_type_id1.name),('company_id','=',company_obj.company_id.id)])
            if partner_data.phone_type_id2:
                phone_type_id2 = phone_type.sudo().search([('name','=',partner_data.phone_type_id2.name),('company_id','=',company_obj.company_id.id)])
            if partner_data.phone_type_id3:
                phone_type_id3 = phone_type.sudo().search([('name','=',partner_data.phone_type_id3.name),('company_id','=',company_obj.company_id.id)])
            if partner_data.phone_type_id4:
                phone_type_id4 = phone_type.sudo().search([('name','=',partner_data.phone_type_id4.name),('company_id','=',company_obj.company_id.id)])

            default.update({
                'company_id':company_obj.company_id and company_obj.company_id.id,
                'user_id':False,
                'user_ids':'',
                'language_lines': tuple(language_details),
                'rate_ids':tuple(rate_details),
                'rating_id':rating_id and rating_id[0].id or '',
                'phone_type_id1':phone_type_id1 and phone_type_id1[0].id or '',
                'phone_type_id2':phone_type_id2 and phone_type_id2[0].id or '',
                'phone_type_id3':phone_type_id3 and  phone_type_id3[0].id or '',
                'phone_type_id4':phone_type_id4 and  phone_type_id4[0].id or '',
                'name':partner_data and partner_data.name or '',
                'complete_name':partner_data and partner_data.complete_name or '',
                })
            partner_data.sudo().copy(default)
            return True
