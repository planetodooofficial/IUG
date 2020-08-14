import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class Interaction(models.Model):
    _inherit = 'interaction'

    @staticmethod
    def map_interaction_sheet_header_to_field():
        migration_field_name = "globelink_id"
        header_to_fields_list = [
            {
                "excel_header_name": "Interaction ID",
                "model_field_name": migration_field_name,
                "function_call": False,
                "data_type": int,
                "default_value": False
            },
            {
                "excel_header_name": "Category",
                "model_field_name": "category_id",
                "function_call": "self.env['interaction.category'].get_category_id_by_name(column_value)",
                "data_type": int,
                "default_value": False
            },
            {
                "excel_header_name": "Sub Category",
                "model_field_name": "sub_category_id",
                "function_call": "self.env['interaction.sub.category'].get_sub_category_id_by_name(column_value)",
                "data_type": int,
                "default_value": False
            },

            {
                "excel_header_name": "Customer",
                "model_field_name": "customer_id",
                "function_call": "self.env['res.partner'].get_customer_id_by_name(column_value)",
                "data_type": int,
                "default_value": False
            },

            {
                "excel_header_name": "Description",
                "model_field_name": "description",
                "function_call": False,
                "data_type": str,
                "default_value": False
            },
            {
                "excel_header_name": "Interpreter ID",
                "model_field_name": "interpreter_id",
                "function_call": "self.env['res.partner'].get_interpreter_id_by_migration_id(column_value)",
                "data_type": int,
                "default_value": False
            },
            {
                "excel_header_name": "Active Status",
                "model_field_name": "active",
                "function_call": False,
                "data_type": bool,
                "default_value": True
            },

            {
                "excel_header_name": "Interaction Status",
                "model_field_name": "status",
                "function_call": False,
                "data_type": str,
                "default_value": False
            },
            {
                "excel_header_name": "Language",
                "model_field_name": "language_id",
                "function_call": "self.env['language'].get_language_id_by_name(column_value)",
                "data_type": int,
                "default_value": False
            },

            {
                "excel_header_name": "Job Ref",
                "model_field_name": "job_id",
                "function_call": False,
                "data_type": int,
                "default_value": False
            },
            {
                "excel_header_name": "Job Ref",
                "model_field_name": "event_id",
                "function_call": "self.env['event'].get_event_id_by_migration_id(column_value)",
                "data_type": int,
                "default_value": False
            },
            {
                "excel_header_name": "Outcome",
                "model_field_name": "outcome_id",
                "function_call": "self.env['interaction.outcome'].get_outcome_id_by_name(column_value)",
                "data_type": int,
                "default_value": False
            },

            {
                "excel_header_name": "Resolution",
                "model_field_name": "resolution",
                "function_call": False,
                "data_type": str,
                "default_value": False
            },
            # Default Data
            {
                "excel_header_name": False,
                "model_field_name": "company_id",
                "function_call": "self.env['res.company'].get_migration_company_id()",
                "data_type": int,
                "default_value": False
            }

        ]
        return header_to_fields_list

    @api.model
    def upload_data(self, list_dictionary):
        created_entries = []
        updated_entries = []
        count = 1
        total_count = len(list_dictionary)
        for record in list_dictionary:
            _logger.info("Interactions row number  %s out of %s" % (str(count), str(total_count)))
            interaction_record = self
            if record["globelink_id"]:
                globe_link_id = record["globelink_id"]
                interaction_record = self.search([('globelink_id', '=', globe_link_id)])
            if "status" in record and record['status']:
                record['status'] = record['status'].lower()

            if interaction_record.exists():
                interaction_record.write(record)
                updated_entries.append(interaction_record.id)
            else:
                interaction_record = self.create(record)
                created_entries.append(interaction_record.id)
            count += 1
        return created_entries, updated_entries
