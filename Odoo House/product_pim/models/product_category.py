# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductCategory(models.Model):
    _name = 'product.category'
    _inherit = ['product.category', 'base.dyn.attr.set']

    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirm', 'Confirm')],
        string='State',
        default="draft")

    def action_confirm(self):
        view_id = self.env.ref(
            'product_pim.view_product_template_inherit_form').id
        for obj in self:
            if not obj.attribute_line:
                obj.state = 'confirm'
                continue
            obj.set_view_ref(view_id, 'categ_id')
            obj.action_bind_view()
            obj.state = 'confirm'
        return True

    def action_draft(self):
        self.ensure_one()
        if not self.attribute_line:
            self.state = 'draft'
            return True
        conf_val = self.map_view_id.model + \
            '.dynamic.view.' + str(self.map_view_id.id)
        view_id = self.map_view_id
        self.map_view_id = False
        self.rel_field = False
        self.state = 'draft'
        confirm_ids = self.search([('state', '=', 'confirm')])
        if confirm_ids:
            confirm_ids[0].action_confirm()
        else:
            parameter_id = self.env['ir.config_parameter'].sudo().search(
                [('key', '=', conf_val)])
            view_id.arch = parameter_id.value
        return True
