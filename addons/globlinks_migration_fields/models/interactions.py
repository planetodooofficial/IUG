from odoo import api, fields, models


class Interaction(models.Model):
    _inherit = 'interaction'

    globelink_id = fields.Integer('GlobeLinks ID')
    job_id = fields.Integer('Job ID')


