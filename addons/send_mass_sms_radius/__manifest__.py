# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Stanislav Silnitskiy <user@mailgate.us>
#    Copyright (C) Stanislav Silnitskiy
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

{
        "name" : "Send Mass SMS Radius",
        "version" : "1.0",
        "website" : "",
        "category" : "Tools",
        "description": """  Send Mass SMS based on Radius  """,
        "depends" : ['base', 'web','twilio_sms','bista_iugroup'],
        "data" : ['sms_mass_radius.xml','ir.model.access.csv'],
        "active" : True,
        "application" : True,
        "installable" : True,
        "auto_install" : False,
        
} 

