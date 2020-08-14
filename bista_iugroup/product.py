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


from odoo import models, fields



#----------------------------------------------------------
# Products
#----------------------------------------------------------
class product_template(models.Model):
    _inherit = "product.template"
    _description = "Product Template"

    product_id=fields.Integer("IU Product Id")

    
#    def import_images(self , cr ,uid ,ids , context={}):
#        ''' Function to import Multi images . First put you images of products with the name of
#            default_code.jpg at "/web/static/src/img/image_multi/" '''
#        product_obj = self.pool.get('product.product')
#        prod_ids = product_obj.search(cr ,uid , [('active','=',True)])
#        for prod_id in prod_ids:
#            res = []
#            data = {}
#            product = product_obj.browse(cr ,uid ,prod_id )
#            data = {
#                "size":"108.20 Kb",
#                "name":"/web/static/src/img/image_multi/" + product.default_code +".jpg",
#                "content_type":"image/jpeg",
#                "date":"10/01/2014 11:00:00",
#                "orignal_name":product.default_code +".jpg",
#                "user":"Administrator"
#            }
#            print "data........",data
#            res.append(data)
#            print "res........",res
#            aaaaa
#            product_obj.write(cr , uid , [prod_id] ,{'multi_images': res} )
#        return True

class product_product(models.Model):
    _inherit = "product.product"

    service_type=fields.Selection([('ambulatory','Ambulatory'),
                                            ('wheelchair','Wheel Chair'),
                                            ('stretcher','Stretcher'),
                                            ('interpreter','Interpreter'),
                                            ('translator','Translator'),
                                            ('claim','Claim'),
                                            ])
