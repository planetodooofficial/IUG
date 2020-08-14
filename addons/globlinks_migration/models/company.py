from odoo import api, fields, models , _
from odoo.exceptions import UserError


class Company(models.Model):
    _inherit = 'res.company'

    @api.model
    def get_migration_company_id(self):
        """

        :return:
        """
        name = "GlobeLink"
        search_domain = [
            ("name", "ilike", name)
        ]
        company_record = self.env['res.company'].sudo().search(search_domain, limit=1)
        if company_record.exists():
            company_id = company_record.id
        else:
            raise UserError(_('Please create a Company with the Name: %s' % str(name)))
        return company_id
