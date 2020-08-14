from odoo import api, fields, models, _

class Event(models.Model):
    _inherit = 'event'

    globelink_id = fields.Integer('GlobeLink ID')
    interpreter_employment_category = fields.Selection([('contractor','Contractor'),
    	('full_time','Full Time Employee'),('part_time','Part Time Employee')],
    	 string='interpreter employment category')
