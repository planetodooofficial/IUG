import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


@staticmethod
def convert_object(input_type, value):
    result = False
    if input_type == int:
        result = int(value)
    return result


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    create_login = fields.Boolean(string="Create Login", default=True)

    @api.multi
    def create_interpreter_login(self):
        for partner in self:
            if partner.create_login:
                super(ResPartnerInherit, self).create_interpreter_login()
        return True

    @api.model
    def get_contact_parent_id_by_migration_id(self, migration_id):
        contact_parent_id = False
        if migration_id:
            customer_record = self.search([("globelink_id", "=", migration_id), ('cust_type', '=', "customer")],
                                          limit=1)
            if customer_record.exists():
                contact_parent_id = customer_record.id
        return contact_parent_id

    @api.model
    def get_customer_id_by_name(self, name):
        customer_id = False
        if name:
            customer_record = self.search([("name", "=", name), ('cust_type', '=', "customer")],
                                          limit=1)
            if customer_record.exists():
                customer_id = customer_record.id
        return customer_id

    @api.model
    def get_interpreter_id_by_migration_id(self, migration_id):
        interpreter_id = False
        if migration_id:
            interpreter_record = self.search([("globelink_id", "=", migration_id), ('cust_type', '=', "interpreter")],
                                          limit=1)
            if interpreter_record.exists():
                interpreter_id = interpreter_record.id
        return interpreter_id

    @staticmethod
    def map_customer_sheet_header_to_field():
        migration_field_name = "globelink_id"
        header_to_fields_list = [
            {
                "excel_header_name": "ID",
                "model_field_name": migration_field_name,
                "function_call": False,
                "data_type": int,
                "default_value": False
            },
            {
                "excel_header_name": "Customer Name",
                "model_field_name": "name",
                "function_call": False,
                "data_type": str,
                "default_value": False
            },
            {
                "excel_header_name": "Website",
                "model_field_name": "website",
                "function_call": False,
                "data_type": str,
                "default_value": False
            },

            {
                "excel_header_name": "Billing Email",
                "model_field_name": "email",
                "function_call": False,
                "data_type": str,
                "default_value": False
            },
            {
                "excel_header_name": "Contact Phone Number",
                "model_field_name": "phone",
                "function_call": False,
                "data_type": str,
                "default_value": False
            },
            {
                "excel_header_name": "Customer Notes",
                "model_field_name": "comment",
                "function_call": False,
                "data_type": str,
                "default_value": False
            },
            # Address
            {
                "excel_header_name": "Street",
                "model_field_name": "street",
                "function_call": False,
                "data_type": str,
                "default_value": False
            },
            {
                "excel_header_name": "Street2",
                "model_field_name": "street2",
                "function_call": False,
                "data_type": str,
                "default_value": False
            },
            {
                "excel_header_name": "City",
                "model_field_name": "city",
                "function_call": False,
                "data_type": str,
                "default_value": False
            },
            {
                "excel_header_name": "State",
                "model_field_name": "state_id",
                "function_call": "self.env['res.country.state'].get_state_id_by_name_code(column_value)",
                "data_type": int,
                "default_value": False
            },
            {
                "excel_header_name": "Country",
                "model_field_name": "country_id",
                "function_call": "self.env['res.country'].get_country_id_by_name_code(column_value)",
                "data_type": int,
                "default_value": False
            },
            {
                "excel_header_name": "Zip",
                "model_field_name": "zip",
                "function_call": False,
                "data_type": str,
                "default_value": False
            },
            # Default Data
            {
                "excel_header_name": False,
                "model_field_name": "customer",
                "function_call": False,
                "data_type": bool,
                "default_value": True
            },
            {
                "excel_header_name": False,
                "model_field_name": "sales_representative_id",
                "function_call": False,
                "data_type": bool,
                "default_value": False
            },
            {
                "excel_header_name": False,
                "model_field_name": "supplier",
                "function_call": False,
                "data_type": bool,
                "default_value": False
            },
            {
                "excel_header_name": False,
                "model_field_name": "cust_type",
                "function_call": False,
                "data_type": str,
                "default_value": "customer"
            },
            {
                "excel_header_name": False,
                "model_field_name": "company_id",
                "function_call": "self.env['res.company'].get_migration_company_id()",
                "data_type": int,
                "default_value": False
            },
            {
                "excel_header_name": False,
                "model_field_name": "user_id",
                "function_call": False,
                "data_type": bool,
                "default_value": False
            }
        ]
        return header_to_fields_list

    @staticmethod
    def map_contact_sheet_header_to_field():
        migration_field_name = "globelink_id"
        # company_id = self.env['res.company'].get_migration_company_id()
        header_to_fields_list = [
            {
                "excel_header_name": "Requestor ID",
                "model_field_name": migration_field_name,
                "function_call": False,
                "data_type": int,
                "default_value": False
            },
            {
                "excel_header_name": "Full Name",
                "model_field_name": "login_name",
                "function_call": False,
                "data_type": str,
                "default_value": False
            },
            {
                "excel_header_name": "First Name",
                "model_field_name": "name",
                "function_call": False,
                "data_type": str,
                "default_value": False
            },
            {
                "excel_header_name": "Last Name",
                "model_field_name": "last_name",
                "function_call": False,
                "data_type": str,
                "default_value": False
            },
            {
                "excel_header_name": "Email",
                "model_field_name": "email",
                "function_call": False,
                "data_type": str,
                "default_value": False
            },
            {
                "excel_header_name": "Phone Number",
                "model_field_name": "phone",
                "function_call": False,
                "data_type": str,
                "default_value": False
            },
            {
                "excel_header_name": "Fax Number",
                "model_field_name": "fax",
                "function_call": False,
                "data_type": str,
                "default_value": False
            },
            {
                "excel_header_name": "Active?",
                "model_field_name": "active",
                "function_call": False,
                "data_type": bool,
                "default_value": True
            },
            {
                "excel_header_name": "Enabled?",
                "model_field_name": "login",
                "function_call": False,
                "data_type": bool,
                "default_value": False
            },
            {
                "excel_header_name": "Customer ID",
                "model_field_name": "parent_id",
                "function_call": "self.env['res.partner'].get_contact_parent_id_by_migration_id(column_value)",
                "data_type": int,
                "default_value": False
            },
            {
                "excel_header_name": False,
                "model_field_name": "customer",
                "function_call": False,
                "data_type": bool,
                "default_value": True
            },
            {
                "excel_header_name": False,
                "model_field_name": "sales_representative_id",
                "function_call": False,
                "data_type": bool,
                "default_value": False
            },
            {
                "excel_header_name": False,
                "model_field_name": "supplier",
                "function_call": False,
                "data_type": bool,
                "default_value": False
            },
            {
                "excel_header_name": False,
                "model_field_name": "cust_type",
                "function_call": False,
                "data_type": str,
                "default_value": "contact"
            },
            {
                "excel_header_name": False,
                "model_field_name": "company_id",
                "function_call": "self.env['res.company'].get_migration_company_id()",
                "data_type": int,
                "default_value": False
            },
            {
                "excel_header_name": False,
                "model_field_name": "user_id",
                "function_call": False,
                "data_type": bool,
                "default_value": False
            }
        ]
        return header_to_fields_list

    @staticmethod
    def map_interpreter_sheet_header_to_field():
        migration_field_name = "globelink_id"
        header_to_fields_list = [
            {
                "excel_header_name": "ID Code",
                "model_field_name": migration_field_name,
                "function_call": False,
                "data_type": int,
                "default_value": False
            },

            {
                "excel_header_name": "First Name",
                "model_field_name": "name",
                "function_call": False,
                "data_type": str,
                "default_value": False
            },
            {
                "excel_header_name": "Middle Name",
                "model_field_name": "middle_name",
                "function_call": False,
                "data_type": str,
                "default_value": False
            },
            {
                "excel_header_name": "Last Name",
                "model_field_name": "last_name",
                "function_call": False,
                "data_type": str,
                "default_value": False
            },
            {
                "excel_header_name": "Gender",
                "model_field_name": "gender",
                "function_call": False,
                "data_type": str,
                "default_value": False
            },
            {
                "excel_header_name": "Active Note",
                "model_field_name": "comment",
                "function_call": False,
                "data_type": str,
                "default_value": False
            },
            {
                "excel_header_name": "Language 1",
                "model_field_name": "language_1",
                "function_call": "self.env['language'].get_language_id_by_name(column_value)",
                "data_type": int,
                "default_value": False
            },
            {
                "excel_header_name": "Language 2",
                "model_field_name": "language_2",
                "function_call": "self.env['language'].get_language_id_by_name(column_value)",
                "data_type": int,
                "default_value": False
            },
            {
                "excel_header_name": "Language 3",
                "model_field_name": "language_3",
                "function_call": "self.env['language'].get_language_id_by_name(column_value)",
                "data_type": int,
                "default_value": False
            },
            {
                "excel_header_name": "Language 4",
                "model_field_name": "language_4",
                "function_call": "self.env['language'].get_language_id_by_name(column_value)",
                "data_type": int,
                "default_value": False
            },
            {
                "excel_header_name": "Language 5",
                "model_field_name": "language_5",
                "function_call": "self.env['language'].get_language_id_by_name(column_value)",
                "data_type": int,
                "default_value": False
            },
            {
                "excel_header_name": "Email Address",
                "model_field_name": "email",
                "function_call": False,
                "data_type": str,
                "default_value": False
            },
            {
                "excel_header_name": "Contact Number",
                "model_field_name": "phone",
                "function_call": False,
                "data_type": str,
                "default_value": False
            },
            {
                "excel_header_name": "Status",
                "model_field_name": "is_interpretation_active",
                "function_call": False,
                "data_type": bool,
                "default_value": True
            },
            # Address
            {
                "excel_header_name": "Street",
                "model_field_name": "street",
                "function_call": False,
                "data_type": str,
                "default_value": False
            },
            {
                "excel_header_name": "Street2",
                "model_field_name": "street2",
                "function_call": False,
                "data_type": str,
                "default_value": False
            },
            {
                "excel_header_name": "City",
                "model_field_name": "city",
                "function_call": False,
                "data_type": str,
                "default_value": False
            },
            {
                "excel_header_name": "State",
                "model_field_name": "state_id",
                "function_call": "self.env['res.country.state'].get_state_id_by_name_code(column_value)",
                "data_type": int,
                "default_value": False
            },
            {
                "excel_header_name": "Country",
                "model_field_name": "country_id",
                "function_call": "self.env['res.country'].get_country_id_by_name_code(column_value)",
                "data_type": int,
                "default_value": False
            },
            {
                "excel_header_name": "Zip",
                "model_field_name": "zip",
                "function_call": False,
                "data_type": str,
                "default_value": False
            },
            {
                "excel_header_name": False,
                "model_field_name": "is_agency",
                "function_call": False,
                "data_type": bool,
                "default_value": True
            },
            # Default Data
            {
                "excel_header_name": False,
                "model_field_name": "customer",
                "function_call": False,
                "data_type": bool,
                "default_value": True
            },
            {
                "excel_header_name": False,
                "model_field_name": "sales_representative_id",
                "function_call": False,
                "data_type": bool,
                "default_value": False
            },
            {
                "excel_header_name": False,
                "model_field_name": "supplier",
                "function_call": False,
                "data_type": bool,
                "default_value": True
            },
            {
                "excel_header_name": False,
                "model_field_name": "cust_type",
                "function_call": False,
                "data_type": str,
                "default_value": "interpreter"
            },
            {
                "excel_header_name": False,
                "model_field_name": "company_id",
                "function_call": "self.env['res.company'].get_migration_company_id()",
                "data_type": int,
                "default_value": False
            },
            {
                "excel_header_name": False,
                "model_field_name": "user_id",
                "function_call": False,
                "data_type": bool,
                "default_value": False
            },
            {
                "excel_header_name": False,
                "model_field_name": "create_login",
                "function_call": False,
                "data_type": bool,
                "default_value": False
            }

        ]
        return header_to_fields_list

    # @api.model
    # def upload_data(self, list_dictionary, customer_type=False):
    #     created_entries = []
    #     updated_entries = []
    #     count = 1
    #     total_count = len(list_dictionary)
    #     for record in list_dictionary:
    #         _logger.info("%s row number  %s out of %s" % (str(customer_type), str(count), str(total_count)))
    #         if "name" in record and record["name"]:
    #             record["name"] = record["name"].title()
    #         if "middle_name" in record and record["middle_name"]:
    #             record["middle_name"] = record["middle_name"].title()
    #         if "last_name" in record and record["last_name"]:
    #             record["last_name"] = record["last_name"].title()
    #         if "gender" in record and record['gender']:
    #             record['gender'] = record['gender'].lower()
    #         if "zip" in record and record['zip']:
    #             record['zip'] = record['zip'].split(".")[0]
    #         if "email" in record and record['email']:
    #             record['email'] = record['email'].lower()
    #         partner_record = self
    #         if record["globelink_id"]:
    #             globe_link_id = record["globelink_id"]
    #             partner_record = self.search([('globelink_id', '=', globe_link_id), ('cust_type', '=', customer_type)])
    #         if partner_record.exists():
    #             partner_record.write(record)
    #             updated_entries.append(partner_record.id)
    #         else:
    #             partner_record = self.create(record)
    #             created_entries.append(partner_record.id)
    #         user_dictionary = {}
    #         model_data_object = self.env['ir.model.data']
    #         if customer_type == "contact" and record["login"] and record["email"]:
    #             group_ids = []
    #             try:
    #                 dummy, group_id = model_data_object.sudo().get_object_reference('bista_iugroup',
    #                                                                                 'group_iu_customer')
    #                 group_ids.append(group_id)
    #             except ValueError:
    #                 pass
    #             user_dictionary["name"] = record["login_name"].title()
    #             user_dictionary["user_type"] = "contact"
    #             user_dictionary["groups_id"] = [(6, 0, group_ids)]
    #             user_object = self.env["res.users"]
    #
    #             email = record["email"]
    #             user_record = user_object.sudo().search([("login", "=", email)])
    #             menu_id = False
    #             try:
    #                 model, menu_id = model_data_object.get_object_reference('base', 'action_menu_admin')
    #                 if model != 'ir.actions.act_window':
    #                     menu_id = False
    #             except ValueError:
    #                 pass
    #             if not user_record.exists():
    #                 user_dictionary["partner_id"] = partner_record.id
    #                 user_dictionary["login"] = email.lower()
    #                 user_dictionary["password"] = "iux@pass"
    #                 user_dictionary["state"] = "active"
    #                 user_dictionary["email"] = email.lower()
    #                 user_dictionary["action_id"] = menu_id
    #                 user_dictionary["require_to_reset"] = True
    #                 user_dictionary["company_id"] = record["company_id"]
    #                 user_dictionary["company_ids"] = [(6, 0, [record["company_id"]])]
    #                 try:
    #                     user_record = user_object.sudo().create(user_dictionary)
    #                     time_zone = self.sudo().get_timezone_for_partner()
    #                     partner_record.write({"user_id": user_record.id, 'has_login': True, 'tz': time_zone})
    #                 except Exception, e:
    #                     pass
    #
    #         count += 1
    #     return created_entries, updated_entries

    @api.model
    def upload_data(self, list_dictionary, customer_type=False):
        created_entries = []
        updated_entries = []
        count = 1
        total_count = len(list_dictionary)
        user_object = self.env["res.users"]
        for record in list_dictionary:
            _logger.info("%s row number  %s out of %s" % (str(customer_type), str(count), str(total_count)))
            if "name" in record and record["name"]:
                record["name"] = record["name"].title()
            if "middle_name" in record and record["middle_name"]:
                record["middle_name"] = record["middle_name"].title()
            if "last_name" in record and record["last_name"]:
                record["last_name"] = record["last_name"].title()
            if "gender" in record and record['gender']:
                record['gender'] = record['gender'].lower()
            if "zip" in record and record['zip']:
                record['zip'] = record['zip'].split(".")[0]
            if "email" in record and record['email']:
                record['email'] = record['email'].lower()
            partner_record = self
            email = record["email"]
            user_record = user_object.sudo().search([("login", "=", email)])
            if record["globelink_id"]:
                globe_link_id = record["globelink_id"]
                partner_record = self.search([('globelink_id', '=', globe_link_id), ('cust_type', '=', customer_type)])

            if partner_record.exists():
                partner_record.write(record)
                updated_entries.append(partner_record.id)

            else:
                partner_record = self.create(record)
                created_entries.append(partner_record.id)
            process_user = False
            user_dictionary = {}
            model_data_object = self.env['ir.model.data']
            if customer_type == "contact" and record["login"] and record["email"]:
                group_ids = []
                try:
                    dummy, group_id = model_data_object.sudo().get_object_reference('bista_iugroup',
                                                                                    'group_iu_customer')
                    group_ids.append(group_id)
                except Exception as e:
                    pass
                user_dictionary["name"] = record["login_name"].title()
                user_dictionary["user_type"] = "contact"
                user_dictionary["groups_id"] = [(6, 0, group_ids)]
                process_user = True

            elif customer_type == "interpreter" and "is_interpretation_active" in record and record["is_interpretation_active"]:

                if record["email"]:
                    # User
                    group_ids = []
                    try:
                        dummy, group_id = model_data_object.sudo().get_object_reference('bista_iugroup',
                                                                                        'group_iu_portal')
                        group_ids.append(group_id)
                    except ValueError:
                        pass
                    user_dictionary["name"] = record["name"].title()
                    user_dictionary["user_type"] = "vendor"
                    user_dictionary["groups_id"] = [(6, 0, group_ids)]
                    process_user = True
                #  languages
                list_languages = []
                if record["language_1"]:
                    list_languages.append(record["language_1"])
                if record["language_2"]:
                    list_languages.append(record["language_2"])
                if record["language_3"]:
                    list_languages.append(record["language_3"])
                if record["language_4"]:
                    list_languages.append(record["language_4"])
                if record["language_5"]:
                    list_languages.append(record["language_5"])
                self.env["interpreter.language"].process_interpreter_languages(partner_record.id,
                                                                               languages_list=list_languages)
            if process_user:
                user_object = self.env["res.users"]

                email = record["email"]
                user_record = user_object.sudo().search([("login", "=", email)])
                menu_id = False
                try:
                    model, menu_id = model_data_object.get_object_reference('base', 'action_menu_admin')
                    if model != 'ir.actions.act_window':
                        menu_id = False
                except ValueError:
                    pass
                if user_record.exists():
                    if record["company_id"] not in user_record.company_ids.ids:
                        company_ids = [(4, record["company_id"])]
                        user_record.sudo().write(
                            {
                                "company_ids": company_ids,
                                "state": "active",
                                "user_type": user_dictionary["user_type"]
                            }
                        )
                else:

                    user_dictionary["partner_id"] = partner_record.id
                    user_dictionary["login"] = email.lower()
                    user_dictionary["password"] = "iux@pass"
                    user_dictionary["state"] = "active"
                    user_dictionary["email"] = email.lower()
                    user_dictionary["action_id"] = menu_id
                    user_dictionary["require_to_reset"] = True
                    user_dictionary["company_id"] = record["company_id"]
                    user_dictionary["company_ids"] = [(6, 0, [record["company_id"]])]
                    try:
                        user_record = user_object.sudo().create(user_dictionary)

                    except Exception, e:
                        pass
                time_zone = self.sudo().get_timezone_for_partner()
                partner_record.write({"user_id": user_record.id, 'has_login': True, 'tz': time_zone})
            count += 1
        return created_entries, updated_entries


class InterpreterLanguage(models.Model):
    _inherit = 'interpreter.language'

    @api.model
    def process_interpreter_languages(self, interpreter_id, languages_list):
        """

        :return:
        """
        result = True
        company_id = self.env["res.company"].get_migration_company_id()
        if languages_list:
            search_domain = [('interpreter_id', '=', interpreter_id)]
            record_set = self.search(search_domain)
            if record_set.exists():
                for record in record_set:
                    if record.name.id in languages_list:
                        languages_list.remove(record.name.id)
                    if not languages_list:
                        break
        for language in languages_list:
            self.create(
                {"name": language, "company_id": company_id, "interpreter_id": interpreter_id}
            )
        return result
