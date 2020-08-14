from odoo import api, fields, models


class Country(models.Model):
    _inherit = 'res.country'

    @api.model
    def get_country_id_by_name_code(self, name=False):
        """

        :return:
        """
        country_id = False
        if not name:
            name = "US"
        search_domain = [
            '|',
            ('code', '=ilike', name),
            ('name', '=ilike', name)
        ]
        country_record = self.search(search_domain, limit=1)
        if country_record.exists():
            country_id = country_record.id
        return country_id


class State(models.Model):
    _inherit = 'res.country.state'

    @api.model
    def get_state_id_by_name_code(self, name=False):
        """

        :return:
        """
        state_id = False
        if name:
            search_domain = [
                '|',
                ('code', '=ilike', name),
                ('name', '=ilike', name)
            ]
            record_set = self.search(search_domain, limit=1)
            if record_set.exists():
                state_id = record_set.id
        return state_id
