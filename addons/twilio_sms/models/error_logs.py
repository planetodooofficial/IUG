# -*- coding: utf-8 -*-
from odoo import fields, models



class twilio_error_logs(models.Model):
    _name ='twilio.error.logs'
    _description = 'Twilio Error Logs'

    status=fields.Char('Status', readonly=True)
    message=fields.Text('Message', readonly=True)
    code=fields.Char('Code', readonly=True)
    more_info=fields.Char('More Info', readonly=True)

