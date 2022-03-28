# -*- coding: utf-8 -*-

from collections import OrderedDict
import random
import string
import uuid

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import xml.etree.ElementTree as ET


class BaseDynNameMiddle(models.Model):
    _name = "base.dyn.name.middle"
    _description = "Base Dyn Name Middle"
    _order = 'sequence'

    sequence = fields.Integer(
        string='Sequence',
        help="Determine the display order")
    res_id = fields.Integer(
        string='Related Document ID',
        index=True)
    model = fields.Char(
        string='Related Document Model',
        index=True)
    dyn_attr_line_id = fields.Many2one(
        comodel_name='base.dyn.attr.line',
        string='Field')
    complete_name = fields.Char(
        related="dyn_attr_line_id.complete_name",
        string="Display Name.")
    field_description = fields.Char(
        related="dyn_attr_line_id.field_description",
        string="Field Label")
    delimeter_type = fields.Selection(
        [('after', 'After'),
         ('before', 'Before'),
         ('between', 'Between')],
        string='Delimeter Type')
    name_delimeter = fields.Char(
        string='Delimeter')
    p_type = fields.Selection(
        [('product_name', 'Name'),
         ('product_ref', 'Ref.')],
        string="Type",
        default='product_name')


class BaseDynNameGen(models.AbstractModel):
    _name = "base.dyn.name.generator"
    _description = "Base Dyn Name Generator"

    name_generator_line = fields.One2many(
        comodel_name='base.dyn.name.middle',
        inverse_name='res_id',
        string='Name Generator',
        domain=lambda self: [('model', '=', self._name)],
        auto_join=True)
    is_product_name = fields.Boolean(
        string='Auto-Generate Product Name')
    is_product_code = fields.Boolean(
        string='Auto-Generate Product Ref.')


class BaseDynMiddle(models.Model):
    _name = "base.dyn.middle"
    _description = "Base Dyn Middle"
    _order = 'sequence'

    sequence = fields.Integer(
        string='Sequence',
        help="Determine the display order")
    res_id = fields.Integer(
        string='Related Document ID',
        index=True)
    model = fields.Char(
        string='Related Document Model',
        index=True)
    dyn_attr_line_id = fields.Many2one(
        comodel_name='base.dyn.attr.line',
        string='Field')
    complete_name = fields.Char(
        related="dyn_attr_line_id.complete_name",
        string="Display Name.")
    ttype = fields.Selection(
        related="dyn_attr_line_id.ttype",
        string="Field Type")
    field_description = fields.Char(
        related="dyn_attr_line_id.field_description",
        string="Field Label")


class BaseDynAttrSet(models.AbstractModel):
    _name = "base.dyn.attr.set"
    _description = "Base Dyn Attribute Set"

    name = fields.Char(
        string='Name',
        required=True)
    attribute_line = fields.One2many(
        comodel_name='base.dyn.middle',
        inverse_name='res_id',
        string='Middleware',
        domain=lambda self: [('model', '=', self._name)],
        auto_join=True)
    map_view_id = fields.Many2one(
        comodel_name='ir.ui.view',
        string='Mapped View')
    dyn_view_id = fields.Many2one(
        comodel_name='ir.ui.view')
    rel_field = fields.Char(
        string='Related Field')
    parent_field = fields.Char(
        string='Parent Field')

    def set_view_ref(self, view_id, field_name):
        if view_id:
            self.map_view_id = view_id
        if field_name:
            self.rel_field = field_name
        return True

    def get_view_ref(self):
        return self.map_view_id and self.map_view_id.id or False

    def update_fields(self):
        model_id = self.env['ir.model'].sudo().search([
            ('model', '=', self.map_view_id.model)])[0]
        for obj in self:
            for ff in self.attribute_line:
                line = ff.dyn_attr_line_id
                if line.ttype == 'caption':
                    continue
                group_ids = []
                fields_val = self.env['ir.model.fields'].sudo().search([
                    ('name', '=', line.name), ('model_id', '=', model_id.id)])
                group_ids = []
                if line.groups:
                    group_ids = [x.id for x in line.groups]
                sel_list = []
                if line.selection:
                    for s in line.selection:
                        sel_list.append((s.int_name, s.name))
                fl_vals = {
                    'model_id': model_id.id,
                    'name': line.name,
                    'ttype': line.ttype,
                    'field_description': line.field_description,
                    'state': 'manual',
                    'store': True,
                    'required': line.required or False,
                    'readonly': line.readonly or False,
                    'index': line.index or False,
                    'copied': line.copy or False,
                    'relation': line.relation or '',
                    'on_delete': line.on_delete or False,
                    'domain': line.domain or '[]',
                    'selection': str(sel_list),
                    'size': line.size or 0,
                    'translate': line.translate or '',
                    'groups': [[6, 0, group_ids]],
                    'help': line.help
                }
                if not fields_val:
                    self.env['ir.model.fields'].sudo().create(fl_vals)
                else:
                    if self.map_view_id.model == 'product.product':
                        continue
                    fields_val[0].write(fl_vals)
#                     fields_val[0].groups = [[6, 0, group_ids]]
#                     fields_val[0].selection = str(sel_list)
        return True

    def action_get_view(self, view_datas, values):
        root = ET.fromstring(view_datas)
        val = root
        if values:
            temp = True
            while temp:
                is_child = False
                for child in val:
                    is_child = True
                    val = child
                if not is_child:
                    for key in values.keys():
                        if values[key]['type'] == 'caption':
                            inv_domain = "[('%s', 'not in', %s)]" % (
                                self.rel_field, str(values[key]['attrs_ids']))
                            if self._name not in (
                                'product.masterdata',
                                    'product.product.masterdata'):
                                inv_attr = "'invisible': %s" % inv_domain
                                attrs = 'attrs = "{%s}"' % (inv_attr)
                                val.append(
                                    (ET.fromstring(
                                        '<separator string="%s"\
                                         colspan="2" %s />'
                                        % (values[key]['string'],
                                           attrs)))
                                )
                            else:
                                val.append(
                                    (ET.fromstring(
                                        '<separator string="%s" colspan="2" />'
                                        % (values[key]['string'])))
                                )
                        else:
                            read_str = 'readonly = "%s"'\
                                % values[key]['readonly']
                            com_name = 'string = "%s"'\
                                % values[key]['string']
                            widget_name = 'widget = "%s"'\
                                % values[key]['widget']
                            domain = 'domain = "%s"' % values[key]['domain']
                            inv_domain = "[('%s', 'not in', %s)]" % (
                                self.rel_field, str(values[key]['attrs_ids']))
                            inv_attr = "'invisible': %s" % inv_domain
                            req_attr = ''
                            if values[key]['required'] == 1:
                                req_domain = "[('%s', 'in', %s)]" % (
                                    self.rel_field,
                                    str(values[key]['attrs_ids']))
                                req_attr = "'required': %s" % req_domain

                            if self._name not in (
                                'product.masterdata',
                                    'product.product.masterdata'):
                                if req_attr:
                                    attrs = 'attrs = "{%s, %s}"' % (
                                        inv_attr, req_attr)
                                else:
                                    attrs = 'attrs = "{%s}"' % (inv_attr)
                                if values[key]['widget']:
                                    if domain == 'domain = "[]"':
                                        val.append(
                                            (
                                                ET.fromstring(
                                                    '<field name="%s" %s\
                                                     %s %s %s />' % (
                                                        values[key]['name'],
                                                        read_str, attrs,
                                                        com_name,
                                                        widget_name)))
                                        )
                                    else:
                                        val.append(
                                            (
                                                ET.fromstring(
                                                    '<field name="%s" %s %s\
                                                     %s %s %s />' % (
                                                        values[key]['name'],
                                                        read_str, domain, attrs,
                                                        com_name,
                                                        widget_name)))
                                        )
                                else:
                                    if domain == 'domain = "[]"':
                                        val.append((
                                            ET.fromstring(
                                                '<field name="%s" %s \
                                                 %s %s />' % (
                                                    values[key]['name'],
                                                    read_str, attrs, com_name))))
                                    else:
                                        val.append(
                                            (
                                                ET.fromstring(
                                                    '<field name="%s" %s %s\
                                                     %s %s />' % (
                                                        values[key]['name'],
                                                        read_str, domain,attrs, com_name)))
                                        )
                            else:
                                if values[key]['widget']:
                                    if domain == 'domain = "[]"':
                                        val.append(
                                            (
                                                ET.fromstring(
                                                    '<field name="%s" %s\
                                                     %s %s />' % (
                                                        values[key]['name'],
                                                        read_str, com_name,
                                                        widget_name)))
                                        )
                                    else:
                                        val.append(
                                            (
                                                ET.fromstring(
                                                    '<field name="%s" %s %s\
                                                     %s %s />' % (
                                                        values[key]['name'],
                                                        read_str,
                                                        domain, com_name,
                                                        widget_name)))
                                        )
                                else:
                                    if domain == 'domain = "[]"':
                                        val.append(
                                            (ET.fromstring(
                                                '<field name="%s" %s %s />' % (
                                                    values[key]['name'], read_str,
                                                    com_name)))
                                        )
                                    else:
                                        val.append(
                                            (ET.fromstring(
                                                '<field name="%s" %s %s %s />' % (
                                                    values[key]['name'], read_str,
                                                    domain, com_name)))
                                        )
                    temp = False
        return ET.tostring(root, method='xml')

    def action_bind_view(self):
        self.ensure_one()
        if not self.attribute_line:
            return True
        if not self.map_view_id:
            raise UserError(_('You must have to set/map view'))
        if not self.rel_field:
            raise UserError(_('You must have to set/map related field'))
        self.update_fields()
        conf_val = self.map_view_id.model + '.dynamic.view'
        conf_val = conf_val + '.' + str(self.map_view_id.id)
        parameter_id = self.env['ir.config_parameter'].sudo().search(
            [('key', '=', conf_val)])
        if parameter_id:
            view_datas = parameter_id[0].value
        else:
            view_datas = self.map_view_id.arch
            self.env['ir.config_parameter'].sudo().create({
                'key': conf_val,
                'value': view_datas
            })
        values = OrderedDict({})
        for dyn_view in self.sudo().search([
                ('map_view_id', '=', self.map_view_id.id),
                ('rel_field', '=', self.rel_field)],
                order="id asc"):
            parent_ids = [dyn_view.id]
            if self._name not in ('product.masterdata',
                                  'product.product.masterdata'):
                view_ids = self.env[self._name].search([
                    ('parent_id', '=', dyn_view.id)]).ids
                while view_ids:
                    for view in view_ids:
                        parent_ids.append(view)
                    view_ids = self.sudo().search([
                        ('parent_id', 'in', view_ids)
                    ]).ids
            for ff in dyn_view.attribute_line:
                line = ff.dyn_attr_line_id
                required = 0
                if line.required:
                    required = 1
                readonly = 0
                if line.readonly:
                    readonly = 1
                domain = line.domain or '[]'
                dic_key = uuid.uuid4().hex
                values.update({
                    dic_key: {
                        'name': line.name,
                        'required': required,
                        'readonly': readonly,
                        'domain': domain,
                        'attrs_ids': parent_ids,
                        'string': line.field_description,
                        'type': line.ttype,
                        'widget': line.widget_name
                    }
                })
        final_data = self.action_get_view(view_datas, values)
        self.map_view_id.arch = final_data
        return True


class AttrMapView(models.Model):
    _name = 'attr.map.view'
    _description = "Attr Map View"

    inherit_view_id = fields.Many2one(
        comodel_name='ir.ui.view',
        string='Inherited View')
    dyn_view_id = fields.Many2one(
        comodel_name='ir.ui.view',
        string='Dynamic View')
    dyn_attr_id = fields.Many2one(
        comodel_name='base.dyn.attr.set',
        string='Attribute')


class SelectionTypeField(models.Model):
    _name = 'selection.type.field'
    _description = "Selection Type Field"
    _order = 'sequence'

    sequence = fields.Integer(
        string='Sequence',
        help="Determine the display order")
    int_name = fields.Char(
        string='Internal Name')
    name = fields.Char(
        string='Name')
    attr_line_id = fields.Many2one(
        comodel_name='base.dyn.attr.line')


class BaseDynAttrLine(models.Model):
    _name = "base.dyn.attr.line"
    _description = "Base Dyn Attr Line"
    _rec_name = 'complete_name'

    name = fields.Char(
        string='Field Name',
        default='x_',
        index=True)
    complete_name = fields.Char(
        index=True,
        string="Display Name.")
    relation = fields.Char(
        string='Object Relation',
        help="For relationship fields, the technical name of the target model")
    relation_field = fields.Char(
        help="For one2many fields, the field on the target model \
        that implement the opposite many2one relationship")
    model_id = fields.Many2one(
        comodel_name='ir.model',
        string='Model',
        index=True,
        ondelete='cascade',
        help="The model this field belongs to")
    field_description = fields.Char(
        string='Field Label',
        default='',
        translate=True)
    help = fields.Text(
        string='Field Help',
        translate=True)
    ttype = fields.Selection(
        selection='_get_field_types',
        string='Field Type')
    selection = fields.One2many(
        comodel_name='selection.type.field',
        inverse_name='attr_line_id',
        string='Selection Options')
    copy = fields.Boolean(
        string='Copied',
        help="Whether the value is copied when "
            "duplicating a record.")
    related = fields.Char(
        string='Related Field',
        help="The corresponding related field, if any. This must be a "
             "dot-separated list of field names.")
    required = fields.Boolean()
    readonly = fields.Boolean()
    index = fields.Boolean(
        string='Indexed')
    translate = fields.Boolean(
        string='Translatable',
        help="Whether values for this field can be "
            "translated (enables the translation "
            "mechanism for that field)")
    size = fields.Integer()
    state = fields.Selection(
        [('manual', 'Custom Field'),
         ('base', 'Base Field')],
        string='Type',
        default='manual',
        readonly=True,
        index=True)
    on_delete = fields.Selection(
        [('cascade', 'Cascade'),
         ('set null', 'Set NULL'),
         ('restrict', 'Restrict')],
        string='On Delete',
        default='set null',
        help='On delete property for many2one fields')
    domain = fields.Char(
        default="[]",
        help="The optional domain to restrict possible values "
            "for relationship fields, specified as a Python "
            "expression defining a list of triplets. "
            "For example: [('color','=','red')]")
    groups = fields.Many2many(
        comodel_name='res.groups',
        relation='ir_model_fields_group_rel_pim',
        column1='field_id',
        column2='group_id')
    selectable = fields.Boolean(
        default=True)
    relation_table = fields.Char(
        help="Used for custom many2many fields to define a custom "
             "relation table name")
    widget_name = fields.Char(
        string='Widget name')

    @api.model
    def _get_field_types(self):
        # retrieve the possible field types from the field classes' metaclass
        val = sorted((key, key) for key in fields.MetaField.by_type)
        val.append(('caption', 'caption'))
        return val

    @api.model
    def create(self, vals):
        if vals.get('ttype') and vals['ttype'] == 'caption':
            vals['name'] = "x_" + \
                ''.join(random.choice(string.ascii_lowercase)
                        for i in range(5))
        return super(BaseDynAttrLine, self).create(vals)


class ProductAttributevalue(models.Model):
    _inherit = "product.attribute.value"

    def name_get(self):
        res = super(ProductAttributevalue, self).name_get()
        return [(value.id, "%s" % (value.name)) for value in self]
