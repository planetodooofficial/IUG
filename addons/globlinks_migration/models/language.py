from odoo import api, fields, models


class Language(models.Model):
    _inherit = 'language'

    @api.model
    def get_language_id_by_name(self, name=False):
        """

        :return:
        """
        company_id = self.env["res.company"].get_migration_company_id()
        language_id = False
        if name:
            search_domain = [
                ('name', '=', name),
                ('company_id', '=', company_id)
            ]
            record_set = self.search(search_domain, limit=1)
            if record_set.exists():
                language_id = record_set.id
            else:
                language_record = self.create({"name": name, "lang_group": "spanish_regular", "company_id": company_id, "active_custom": True})
                language_id = language_record.id
        return language_id
