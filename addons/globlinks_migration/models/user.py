from odoo import api, fields, models , _
from odoo.exceptions import UserError


class Company(models.Model):
    _inherit = 'res.users'

    @api.model
    def get_migration_user_id(self):
        """

        :return:
        """
        name = "globelinkuser@iugroup.com"
        search_domain = [
            ("login", "=", name)
        ]
        user_record = self.sudo().search(search_domain, limit=1)
        if user_record.exists():
            user_id = user_record.id
        else:
            raise UserError(_('Please create default user with the login: %s and user_type as "staff"' % str(name)))
        return user_id
