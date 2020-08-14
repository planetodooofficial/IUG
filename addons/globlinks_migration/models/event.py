from odoo import api, fields, models


class Event(models.Model):
    _inherit = 'event'

    @api.model
    def get_event_id_by_migration_id(self, migration_id):
        event_id = False
        if migration_id:
            event_record = self.search([("globelink_id", "=", migration_id)], limit=1)
            if event_record.exists():
                event_id = event_record.id
        return event_id
