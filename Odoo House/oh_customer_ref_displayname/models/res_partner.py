# -*- coding: utf-8 -*-

from odoo import models


class Partner(models.Model):
    _inherit = "res.partner"

    def name_get(self):
        result = []
        if self._context.get('name_display'):
            for partner in self:
                name = partner.name
                if partner.ref:
                    name = str(name) + "-" + str(partner.ref)
                result.append((partner.id, name))
        else:
            result = super().name_get()
        return result
