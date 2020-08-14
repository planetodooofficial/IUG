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

from odoo import api, fields, models,tools, _

class document_configuration(models.TransientModel):
    _name='document.configuration'
    _description = 'Directory Configuration'
    _inherit = 'res.config'

    def execute(self):
        dir_pool = self.env['document.directory']
        data_pool = self.env['ir.model.data']
        model_pool = self.env['ir.model']
        content_pool = self.env['document.directory.content']
        if self.env['sale.order']:
            # Sale order
            dir_data_id = data_pool._get_id('document.directory', 'dir_sale_order_all')
            if dir_data_id:
                sale_dir_id = data_pool.browse(dir_data_id).res_id
            else:
                sale_dir_id = data_pool.create({'name': 'Sale Orders'}).id
            mid = model_pool.search([('model','=','sale.order')]).id
            sale_dir_rec=dir_pool.browse(sale_dir_id)
            sale_dir_rec.write({
                'type':'ressource',
                'ressource_type_id': mid,
                'domain': '[]',
            })
            # Qutation
            dir_data_id = data_pool._get_id('document.directory', 'dir_sale_order_quote')
            if dir_data_id:
                quta_dir_id = data_pool.browse(dir_data_id).res_id
            else:
                quta_dir_id = data_pool.create({'name': 'Sale Quotations'}).id
            quta_dir_rec=dir_pool.browse(quta_dir_id)
            quta_dir_rec.write({
                'type':'ressource',
                'ressource_type_id': mid,
                'domain': "[('state','=','draft')]",
            })
            # Sale Order Report
            order_report_data_id = data_pool._get_id('sale', 'report_sale_order')
            if order_report_data_id:
                order_report_id = data_pool.browse(order_report_data_id).res_id

                content_pool.create({
                    'name': "Print Order",
                    'suffix': "_print",
                    'report_id': order_report_id,
                    'extension': '.pdf',
                    'include_name': 1,
                    'directory_id': sale_dir_id,
                })

                content_pool.create({
                    'name': "Print Quotation",
                    'suffix': "_print",
                    'report_id': order_report_id,
                    'extension': '.pdf',
                    'include_name': 1,
                    'directory_id': quta_dir_id,
                })


        if self.env['product.product']:
            # Product
            dir_data_id = data_pool._get_id('document.directory', 'dir_product')
            if dir_data_id:
                product_dir_id = data_pool.browse(dir_data_id).res_id
            else:
                product_dir_id = data_pool.create({'name': 'Products'}).id

            mid = model_pool.search([('model','=','product.product')]).id
            product_dir_rec=dir_pool.browse(product_dir_id)
            product_dir_rec.write({
                'type':'ressource',
                'ressource_type_id': mid,
            })

        if self.env['account.analytic.account']:
            # Project
            dir_data_id = data_pool._get_id('document.directory', 'dir_project')
            if dir_data_id:
                project_dir_id = data_pool.browse(dir_data_id).res_id
            else:
                project_dir_id = data_pool.create({'name': 'Projects'}).id
            project_dir_rec=dir_pool.browse(project_dir_id)
            mid = model_pool.search([('model','=','account.analytic.account')]).id
            project_dir_rec.write({
                'type':'ressource',
                'ressource_type_id': mid,
                'domain': '[]',
                'ressource_tree': 1
        })


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
