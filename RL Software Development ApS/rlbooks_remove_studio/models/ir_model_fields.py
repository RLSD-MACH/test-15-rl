from odoo import api, fields, models


class IrModelFields(models.Model):
    
    _inherit = 'ir.model.fields'

    state = fields.Selection(readonly=False)
    modules = fields.Char(readonly=False)

    def init(self): 

        for record in self:

            if record.state == 'manual':

                
                if record.model_id.state == 'manual':

                
                    record.model_id.update({
                        
                        'state': 'base',
                        'modules': 'rlbooks_imp_sale'

                    })


    def action_update_fields_to_base(self): 
        
        for record in self:

            if record.state == 'manual':

                
                if record.model_id.state == 'manual':

                
                    record.model_id.update({
                        
                        'state': 'base',
                        'modules': 'rlbooks_imp_sale'

                    })

  