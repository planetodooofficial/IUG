    
from odoo import models, fields,api


class account_payment(models.Model):
    ''' Fields added for the IUX system Fields '''
    _inherit = "account.payment"


    event_date=fields.Date('Date Of Service')
    patient_id=fields.Many2one('patient', 'Patient/Client', )
    reference=fields.Char('Reference', size=64, index=1)
    project_name_id=fields.Many2one('project', 'Project')
    period_id=fields.Many2one('account.period', 'Period',readonly=True,
                                 states={'draft': [('readonly', False)]})
    internal_notes=fields.Text('Internal Notes')
    check_number_string=fields.Char('Check Number(with alphabets)')

    @api.model
    def fields_get(self, fields=None, attributes=None):
        res = super(account_payment, self).fields_get(fields, attributes=attributes)
        for field in res:
            if field == 'check_number':
                res[field]['sortable'] = True
                res[field]['searchable'] = True
        return res
