from odoo import api, fields, models


class InteractionCategory(models.Model):
    _name = 'interaction.category'
    _rec_name = 'name'
    _description = 'Interaction Category'

    name = fields.Char(string="Name", required=False)
    sequence = fields.Integer(string="Sequence", required=False)
    active = fields.Boolean(string="Active", default=True)

    @api.model
    def get_category_id_by_name(self, name=False):
        """

        :return:
        """
        record_id = False
        if name:
            search_domain = [
                ('name', '=', name),
            ]
            record_set = self.search(search_domain, limit=1)
            if record_set.exists():
                record_id = record_set.id
            else:
                record = self.create({"name": name})
                record_id = record.id
        return record_id


class InteractionSubCategory(models.Model):
    _name = 'interaction.sub.category'
    _rec_name = 'name'
    _description = 'Interaction Sub Category'

    name = fields.Char(string="Name", required=False)
    sequence = fields.Integer(string="Sequence", required=False)
    category_id = fields.Many2one(comodel_name="interaction.category", string="Category", required=False, )
    active = fields.Boolean(string="Active", default=True)

    @api.model
    def get_sub_category_id_by_name(self, name=False):
        """

        :return:
        """
        record_id = False
        if name:
            search_domain = [
                ('name', '=', name),
            ]
            record_set = self.search(search_domain, limit=1)
            if record_set.exists():
                record_id = record_set.id
            else:
                record = self.create({"name": name})
                record_id = record.id
        return record_id


class InteractionOutCome(models.Model):
    _name = 'interaction.outcome'
    _rec_name = 'name'
    _description = 'Interaction Out Come'

    name = fields.Char(string="Name", required=False)
    sequence = fields.Integer(string="Sequence", required=False)
    active = fields.Boolean(string="Active", default=True)

    @api.model
    def get_outcome_id_by_name(self, name=False):
        """

        :return:
        """
        record_id = False
        if name:
            search_domain = [
                ('name', '=', name),
            ]
            record_set = self.search(search_domain, limit=1)
            if record_set.exists():
                record_id = record_set.id
            else:
                record = self.create({"name": name})
                record_id = record.id
        return record_id
