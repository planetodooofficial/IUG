# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class MultiImages(models.Model):
    _name = "multi.images"

    user=fields.Many2one('res.users',default=lambda self: self.env.uid)
    image_name=fields.Char('File Name')
    image = fields.Binary('Images')
    description = fields.Char('Description')
    title = fields.Char('Title')
    product_template_id = fields.Many2one('product.template', 'Product')


class ProductTemplate(models.Model):
    _inherit = "product.template"

    multi_images = fields.One2many('multi.images', 'product_template_id',
                                   'Multi Images')
