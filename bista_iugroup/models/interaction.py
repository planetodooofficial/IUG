from odoo import api, fields, models


class Interaction(models.Model):
    _name = 'interaction'
    _rec_name = 'name'
    _description = 'Interaction'
    _inherit = ['mail.thread']
    _order = "create_date desc"

    STATUS = [
        ("open", "Open"),
        ("closed", "Closed")
    ]
    name = fields.Char(string="Name", readonly=True, copy=False, default='New')
    event_id = fields.Many2one(comodel_name="event", string="Event", required=False, track_visibility='onchange')
    contact_id = fields.Many2one(comodel_name="res.partner", string="Contact", required=False, track_visibility='onchange')
    customer_id = fields.Many2one(comodel_name="res.partner", string="Customer", required=False, track_visibility='onchange')
    interpreter_id = fields.Many2one(comodel_name="res.partner", string="Interpreter", required=False, track_visibility='onchange')
    category_id = fields.Many2one(comodel_name="interaction.category", string="Category", required=False, track_visibility='onchange')
    sub_category_id = fields.Many2one(comodel_name="interaction.sub.category", string="Sub Category", required=False, track_visibility='onchange')
    outcome_id = fields.Many2one(comodel_name="interaction.outcome", string="OutCome", required=False, track_visibility='onchange')
    status = fields.Selection(string="Status", selection=STATUS, required=False, track_visibility='onchange')
    description = fields.Text(string="Description", required=False, track_visibility='onchange')
    resolution = fields.Text(string="Resolution", required=False, track_visibility='onchange')
    disciplinary_date = fields.Date(string="Disciplinary Date", required=False, track_visibility='onchange')
    close_datetime = fields.Datetime(string="Close DateTime", required=False, track_visibility='onchange')
    language_id = fields.Many2one(comodel_name="language", string="Language", required=False, track_visibility='onchange')
    company_id = fields.Many2one(comodel_name="res.company", string="Company", required=False, track_visibility='onchange', default=lambda self: self.env.user.company_id)
    active = fields.Boolean(string="Active", default=True, track_visibility='onchange')

    @api.model
    def create(self, values):
        result = super(Interaction, self).create(values)
        company_name = result.company_id and result.company_id.name or False
        name = self.get_sequence_for_partner(company_name)
        result.write({'name': name})
        return result

    @api.model
    def get_sequence_for_partner(self, company_name):
        """Function to get company wise sequence"""
        ref = 'New'
        sequence_obj = self.env['ir.sequence']
        if company_name:
            if company_name.strip().upper() == 'IUG-SD':
                ref = sequence_obj.next_by_code('interactions.iug.sd') or 'New'

            elif company_name.strip().upper() == 'ASIT':
                ref = sequence_obj.next_by_code('interactions.asit') or 'New'

            elif company_name.strip().upper() == 'ACD':
                ref = sequence_obj.next_by_code('interactions.acd') or 'New'

            elif company_name.strip().upper() == 'ALBORS AND ALNET':
                ref = sequence_obj.next_by_code('interactions.aa') or 'New'
            elif company_name.strip().upper() == 'GLOBELINK FOREGIN LANGUAGE CENTER':
                ref = sequence_obj.next_by_code('interactions.gl') or 'New'
            else:
                ref = sequence_obj.next_by_code('interactions.iug') or 'New'
        return ref






