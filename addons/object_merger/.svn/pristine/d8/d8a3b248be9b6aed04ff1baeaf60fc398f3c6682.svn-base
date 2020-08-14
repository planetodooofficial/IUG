# -*- coding: utf-8 -*-
import copy
from odoo import api, models, fields, SUPERUSER_ID, _


class ir_model(models.Model):
    _inherit = 'ir.model'

    object_merger_model = fields.Boolean('Merging Objects', default=False,
                                         help='If checked, by default the Object '
                                         'Merger configuration will get this '
                                         'module in the list')


class object_merger_settings(models.TransientModel):
    _name = 'object.merger.settings'
    _inherit = 'res.config.settings'

    @api.model
    def _get_default_object_merger_models(self):
        return self.env['ir.model'].search([('object_merger_model', '=', True)])

    models_ids = fields.Many2many('ir.model',
                                  'object_merger_settings_model_rel',
                                  'object_merger_id', 'model_id', 'Models',
                                  domain=[('transient', '=', False)],default=_get_default_object_merger_models)

    @api.model
    def update_field(self, vals):
        
        model_ids = []
        model_obj = self.env['ir.model']
        action_obj = self.env['ir.actions.act_window']
        value_obj = self.env['ir.values']
        field_obj = self.env['ir.model.fields']
        
        if not vals or not vals.get('models_ids', False):
            return False
        elif vals.get('models_ids') or model_ids[0][2]:
            model_ids = vals.get('models_ids')
            if isinstance(model_ids[0], (list)):
                model_ids = model_ids[0][2]
        
        unlink_ids = action_obj.search([('res_model' , '=', 'object.merger')])
        for unlink_id in unlink_ids:
            unlink_id.unlink()
            value_obj.search([
                ('value', '=', "ir.actions.act_window," + str(unlink_id.id))]).unlink()
        
        model_not_merge_ids = model_obj.search([
            ('id', 'not in', model_ids),
            ('object_merger_model', '=', True),
            ])
        model_not_merge_ids.write({'object_merger_model' : False})
        read_datas=model_obj.browse(model_ids)
        read_datas.write({'object_merger_model' : True})
        object_merger_ids = model_obj.search([('model', '=', 'object.merger')]).ids
        for model in read_datas:
            field_name = 'x_' + model.model.replace('.','_') + '_id'
            act_id = action_obj.create({
                 'name': "%s " % model.name + _("Merger"),
                 'type': 'ir.actions.act_window',
                 'res_model': 'object.merger',
                 'src_model': model.model,
                 'view_type': 'form',
                 'context': "{'field_to_read':'%s'}" % field_name,
                 'view_mode':'form',
                 'target': 'new',
            }).id
            value_obj.create({
                 'name': "%s " % model.name + _("Merger"),
                 'model': model.model,
                 'key2': 'client_action_multi',
                 'value': "ir.actions.act_window," + str(act_id),
            })
            field_name = 'x_' + model.model.replace('.','_') + '_id'
            if not field_obj.search( [
                ('name', '=', field_name),
                ('model', '=', 'object.merger')]):
                field_data = {
                    'model': 'object.merger',
                    'model_id': object_merger_ids and object_merger_ids[0] or False,
                    'name': field_name,
                    'relation': model.model,
                    'field_description': "%s " % model.name + _('To keep'),
                    'state': 'manual',
                    'ttype': 'many2one',
                }
                field_obj.sudo().create(field_data)
        return True

    @api.model
    def create(self,vals):
        """ create method """
        vals2 = copy.deepcopy(vals)
        result = super(object_merger_settings, self).create(vals2)
        
        self.update_field(vals)
        return result

    @api.multi
    def install(self):        
        """ install method """
        for vals in self.read([]):
            self.update_field(vals)
        return {
                'type': 'ir.actions.client',
                'tag': 'reload',
                }


