# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    check_editable_name = fields.Boolean('Check Editable name', default=False)
    check_editable_ref = fields.Boolean('Check Editable Ref.', default=False)

    @api.onchange('categ_id')
    def _onchange_categ_id(self):
        if self.categ_id:
            self.check_editable_name = self.categ_id.state == 'confirm' and self.categ_id.is_product_name or False
            self.check_editable_ref = self.categ_id.state == 'confirm' and self.categ_id.is_product_code or False

    @api.model
    def create(self, vals):
        if vals.get('check_editable_name', False) or vals.get('check_editable_ref', False):
            vals.update(self._update_name_code_details(vals, vals['check_editable_name'], vals['check_editable_ref']))
        res = super(ProductTemplate, self).create(vals)
        return res

    def write(self, vals):
        vals.update(self._update_name_code_details(vals, vals.get('check_editable_name', False) or self.check_editable_name, vals.get('check_editable_ref', False) or self.check_editable_ref))
        res = super(ProductTemplate, self).write(vals)
        return res

    def _update_name_code_details(self, vals, name=False, code=False):
        res = {}
        if vals.get('categ_id', False):
            categ_obj = self.env['product.category'].browse(vals['categ_id'])
        else:
            categ_obj = self.categ_id
        if name:
            p_name = ''
            for line in categ_obj.name_generator_line:
                if line.p_type == 'product_name':
                    if vals.get(line.dyn_attr_line_id.name, False) or self[line.dyn_attr_line_id.name]:
                        p_name += vals.get(line.dyn_attr_line_id.name, False) and str(vals[line.dyn_attr_line_id.name]) or str(self[line.dyn_attr_line_id.name])
                        if line.delimeter_type in ('after', 'between'):
                            p_name += line.name_delimeter and line.name_delimeter or ''
                        elif line.delimeter_type == 'before':
                            pass
                    else:
                        raise UserError(_('You have to fill %s field') % (line.dyn_attr_line_id.complete_name))
            if p_name:
                res.update({'name': p_name})
        if code:
            p_code = ''
            for line in categ_obj.name_generator_line:
                if line.p_type == 'product_ref':
                    if vals.get(line.dyn_attr_line_id.name, False) or self[line.dyn_attr_line_id.name]:
                        p_code += vals.get(line.dyn_attr_line_id.name, False) and str(vals[line.dyn_attr_line_id.name]) or str(self[line.dyn_attr_line_id.name])
                        if line.delimeter_type in ('after', 'between'):
                            p_code += line.name_delimeter and line.name_delimeter or ''
                        elif line.delimeter_type == 'before':
                            pass
                    else:
                        raise UserError(_('You have to fill %s field') % (line.dyn_attr_line_id.complete_name))
            if p_code:
                res.update({'default_code': p_code})
        return res
