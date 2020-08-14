# -*- coding: utf-8 -*-
from odoo import fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    opt_for_sms=fields.Boolean('Opt for SMS service')

