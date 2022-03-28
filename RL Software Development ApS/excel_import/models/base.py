# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import Warning

class BaseInherit(models.AbstractModel):

    _inherit = 'base'

    def costume_btn_import_line(self):

        self.ensure_one()

        ctx = self._context.copy()

        field_name = ctx.get('one2many_field')

        if not field_name:

            raise Warning(_('The field of lines is not found !'))

        args = [('model', '=', self._name),
                ('name', '=', field_name)]

        one2many_field = self.env['ir.model.fields'].search(args, limit=1)

        if not one2many_field:
            raise Warning(_('The field of lines does not correct !'))

        if one2many_field.ttype != 'one2many':
            raise Warning(_('Type of field is not a one2many !'))

        ctx.update({
            'relation_field': one2many_field.relation_field,
            'relation_field_value': self.id
        })

        res = {

            'type': 'ir.actions.client',
            'tag': 'import',
            'params': {

                'model': one2many_field.relation,
                'context': ctx,

            }

        }

        return res

    @api.model
    def create(self, vals):

        ctx = self._context

        if ctx.get('relation_field') and ctx.get('relation_field_value') and \
                ctx.get('import_file'):
            vals.update({ctx['relation_field']: ctx['relation_field_value']})

        res = super(BaseInherit, self).create(vals)
        
        return res