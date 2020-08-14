# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-2013 Bluestar Solutions Sàrl (<http://www.blues2.ch>).
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

from odoo import fields,models,api
import phonenumbers

class bss_phonenumbers_converter(models.TransientModel):
    
    _name = 'bss.phonenumbers.converter'

    @staticmethod
    def _parse(vals, region=''):
        if isinstance(vals, dict):
            number = [vals['e164'], region]
        elif vals:
            if 'xxx' in vals:
                return vals
            number = vals.split(',')
            if len(number) == 1:
                number = [number[0], region]
        else :
            return None
        
        if not number[0] or number[0] == '':
            return None
        
        return phonenumbers.parse(*number)
