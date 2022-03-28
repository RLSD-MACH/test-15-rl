from odoo import models, fields, api
from datetime import datetime

class ShipShippingOrderWizard(models.TransientModel):

    _name = 'shipping.order.ship.wizard'
    _description = 'Shipping order sent'

    def _get_default_order_id(self):
        default_order_id = self.env.context.get('default_order_id')
        return [default_order_id] if default_order_id else None
  
    order_id = fields.Many2one("shipping.order", string='Shipping Order', ondelete='restrict',required=True, default=_get_default_order_id, readonly=True)
    date = fields.Date(required=True, string='Date of departure', tracking=True, default= datetime.today())    

    def action_underway(self):
                
        order = self.env['shipping.order'].browse(self.order_id.id)
        
        order.shipped = self.date
        order.state = 'underway'

        message = 'The goods are now under way - please correct the ETA if it is not correct: ' + str(order.eta)

        return {
            'effect': {
                'fadeout': 'slow',
                'message': message,
                'img_url': '/web/static/src/img/smile.svg',
                'type': 'rainbow_man',
            }
        }

        pass
        



    

