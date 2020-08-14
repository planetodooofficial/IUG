
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def open_map(self):
        for partner in self:
            url="http://maps.google.com/maps?oi=map&q="
            if partner.street:
                url+=partner.street.replace(' ','+')
            if partner.city:
                url+='+'+partner.city.replace(' ','+')
            if partner.state_id:
                url+='+'+partner.state_id.name.replace(' ','+')
            if partner.country_id:
                url+='+'+partner.country_id.name.replace(' ','+')
            if partner.zip:
                url+='+'+partner.zip.replace(' ','+')
        return {'type': 'ir.actions.act_url','target': 'new','url':url}