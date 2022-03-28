from datetime import datetime, timedelta

from odoo import api, fields, models, _

class ResPort(models.Model):
    
    _name = 'res.port'
    _description = 'Port'
    _order = 'name asc'

    name = fields.Char(required=True, string='Name')
    country_id = fields.Many2one('res.country', string='Country', required=True,)
    active = fields.Boolean(required=True, string='Active', default=True, copy=False)  
   

    # @api.depends(lambda self: (self._rec_name,) if self._rec_name else ())
    # def _compute_display_name(self):

    #     names = dict(self.name_get())

    #     for record in self:

    #         if record.country_id:

    #             record.display_name = names.get(record.id, False) + ", " + record.country_id.name
            
    #         else:

    #             record.display_name = names.get(record.id, False)

    def name_get(self):

        result = []

        for record in self:

            name = record.name

            if record.country_id:

                name = name + ", " + record.country_id.name            
            
            result.append((record.id, name))


        return result