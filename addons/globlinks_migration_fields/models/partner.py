from odoo import api, fields, models, _


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    globelink_id = fields.Integer('GlobeLinks ID')
