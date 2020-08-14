# -*- coding: utf-8 -*-
from odoo.tools import ustr
from odoo import models, fields, _, api
from odoo.exceptions import UserError


class object_merger(models.TransientModel):
    
    _name = 'object.merger'
    _description = 'Merge objects'

    name = fields.Char()

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(object_merger, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=False)
        object_ids = self.env.context.get('active_ids',[])
        active_model = self.env.context.get('active_model')
        field_name = 'x_' + (active_model and active_model.replace('.', '_') or '') + '_id'
        res_fields = res['fields']
        if object_ids:
            view_part = """<label for='""" + field_name + """'/>
                    <div>
                        <field name='""" + field_name + \
                        """' required="1" domain="[(\'id\', \'in\', """ + \
                        str(object_ids) + """)]"/>
                    </div>"""
            res['arch'] = res['arch'].decode('utf8').replace(
                    """<separator string="to_replace"/>""", view_part)
            field = self.fields_get([field_name])
            res_fields.update(field)
            res['fields'] = res_fields
            res['fields'][field_name]['domain'] = [('id', 'in', object_ids)]
            res['fields'][field_name]['required'] = True
        return res

    @api.multi
    def action_merge(self):
        
        cr = self._cr
        active_model = self.env.context.get('active_model')
        if not active_model:
            raise UserError(_('The is no active model defined!'))
        model_env = self.env[active_model]
        object_ids = self.env.context.get('active_ids',[])
        field_to_read = self.env.context.get('field_to_read')
        field_list = field_to_read and [field_to_read] or []
        object = self.read(field_list)[0]
        if object and field_list and object[field_to_read]:
            object_id = object[field_to_read][0]
        else:
            raise UserError(_('Please select one value to keep'))
        cr.execute("SELECT name, model FROM ir_model_fields WHERE relation=%s "
                   "and ttype not in ('many2many', 'one2many');", (active_model, ))
        for name, model_raw in cr.fetchall():
            if hasattr(self.env[model_raw], '_auto'):
                if not self.env[model_raw]._auto:
                    continue
            if hasattr(self.env[model_raw], '_check_time'):
                continue
            else:
                if hasattr(self.env[model_raw], '_fields'):
                    model_raw_obj = self.env[model_raw]
                    if model_raw_obj._fields.get(name, False) and \
                            model_raw_obj._fields[name].type == 'many2one' and model_raw_obj._fields[name].store:
                        if hasattr(self.env[model_raw], '_table'):
                            model = self.env[model_raw]._table
                        else:
                            model = model_raw.replace('.', '_')
                        requete = "UPDATE %s SET %s = %s WHERE " \
                            "%s IN %s;" % (model, name, str(object_id),
                                           ustr(name), str(tuple(object_ids)))
                        cr.execute(requete)

        cr.execute("SELECT name, model FROM ir_model_fields WHERE "
                   "relation=%s AND ttype IN ('many2many');", (active_model,))
        for field, model in cr.fetchall():
            model_obj = self.env[model]
            field_data = model_obj._fields.get(field, False) \
                    and model_obj._fields[field].type == 'many2many' and model_obj._fields[field].store and model_obj._fields[field] or False
            if field_data:
                model_m2m, rel1, rel2 = field_data.relation, field_data.column1, field_data.column2
                requete = "UPDATE %s SET %s=%s WHERE %s " \
                    "IN %s AND %s NOT IN (SELECT DISTINCT(%s) " \
                    "FROM %s WHERE %s = %s);" % (model_m2m, rel2,
                                                 str(object_id),
                                                 ustr(rel2),
                                                 str(tuple(object_ids)),
                                                 rel1, rel1, model_m2m,
                                                 rel2, str(object_id))
                cr.execute(requete)
        cr.execute("SELECT name, model FROM ir_model_fields WHERE "
                   "name IN ('res_model', 'model');")
        for field, model in cr.fetchall():
            model_obj = self.env[model]
            if not model_obj:
                continue
            if field == 'model' and model_obj._fields.get('res_model', False):
                continue
            res_id = model_obj._fields.get('res_id')
            if res_id:
                requete = False
                if res_id.type == 'integer' or res_id.type == 'many2one':
                    requete = "UPDATE %s SET res_id = %s " \
                    "WHERE res_id IN %s AND " \
                    "%s = '%s';" % (model_obj._table,
                                    str(object_id),
                                    str(tuple(object_ids)),
                                    field,
                                    active_model)
                elif res_id.type == 'char':
                    requete = "UPDATE %s SET res_id = '%s' " \
                    "WHERE res_id IN %s AND " \
                    "%s = '%s';" % (model_obj._table,
                                    str(object_id),
                                    str(tuple([str(x) for x in object_ids])),
                                    field,
                                    active_model)
                if requete:
                    cr.execute(requete)
        unactive_object_ids = model_env.search([
            ('id', 'in', object_ids),
            ('id', '<>', object_id),
        ])
        if hasattr(model_env,'active'):
            unactive_object_ids.write({'active': False})

        return {'type': 'ir.actions.act_window_close'}

