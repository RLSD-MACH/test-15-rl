from datetime import datetime, timedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.osv import expression

TRANSPORT_TYPE_SELECTION = [
    ('draft', 'Draft'),
    ('underway', 'En route'),
    ('received', 'Received'),
    ('cancel', 'Cancelled'),
]

class ShippingOrder(models.Model):
    
    _name = 'shipping.order'
    _description = 'Shipping order'
    _order = 'create_date desc'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True,string='Order', readonly=True, states={'draft': [('readonly', True)]}, index=True, default=lambda self: _('New'))    
    user_id = fields.Many2one("res.users", string='Resposible',default=lambda self: self.env.uid,tracking=True, ondelete='restrict', required=True)

    origin_id = fields.Many2one("res.partner", string='Place of Origin', ondelete='restrict', required=False)
    destination_id = fields.Many2one("res.partner", string='Place of Destination', ondelete='restrict', required=False)

    stock_origin_id = fields.Many2one("stock.location", string='Stock of Origin', ondelete='restrict', required=False, domain="[('usage', '=', 'internal')]")
    stock_destination_id = fields.Many2one("stock.location", string='Stock of Destination', ondelete='restrict', required=False, domain="[('usage', '=', 'internal')]")

    loading_port_id = fields.Many2one('res.port', string='Port of Loading', ondelete='restrict')
    unloading_port_id = fields.Many2one('res.port', string='Port of Unloading', ondelete='restrict')

    shipping_company_id = fields.Many2one("res.partner", string='Shipper', help="Shipping Company", ondelete='restrict')

    picking_type_code = fields.Selection([
        ('incoming', 'IN'),
        ('outgoing', 'Out'),
        ('internal', 'Internal'),
        ], string='Picking Type', readonly=False, copy=False, index=True, tracking=3)

    shipping_type = fields.Selection([
        ('plain', 'Air'),
        ('ship', 'Sea'),
        ('truck', 'Land'),
        ('internal', 'Internal'),
        ('other', 'Other'),
        ], string='Type', readonly=False, copy=False, index=True, tracking=3)
        
    trackingnumber = fields.Char(string="Trackingnumber", tracking=True, required=False)
    b_l_number = fields.Char(string="B/L number", tracking=True, required=False)
    container_id = fields.Many2one('container', string='Container', copy=True)
    container = fields.Char(related='container_id.container')
    capacity_cubic_meter_total = fields.Float(related='container_id.capacity_cubic_meter_total')
    # line_ids = fields.One2many('shipping.order.line', 'order_id', 'Order lines')
    line_ids = fields.One2many('stock.quant', 'sale_order_id', 'Order lines')
    move_ids = fields.One2many('stock.move', 'shipping_order_id', string='Stock Moves')

    shipped = fields.Date(required=False, string='Shipped', readonly=True, tracking=True)    
    received = fields.Date(required=False, string='Received', readonly=True, tracking=True)    
    eta = fields.Datetime(required=False, string='ETA', help="Estimated time of arrival", readonly=False, tracking=True)
    etd = fields.Datetime(required=False, string='ETD', help="Estimated departure time", readonly=False, tracking=True)
    ett = fields.Char(required=False, string='ETT', help="Estimated Travel Time", readonly=True, compute="_compute_ett")
    shipping_manifest = fields.Binary("Shipping manifest")

    state = fields.Selection(TRANSPORT_TYPE_SELECTION, string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    active = fields.Boolean(required=True, string='Active', default=True, copy=False)
  
    def preview_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }
    
    @api.model    
    def create (self, vals):

        next_seq = self.env['ir.sequence'].next_by_code('shipping.order.sequence')

        if next_seq != False:

            vals['name'] = next_seq

        res = super(ShippingOrder, self).create(vals)

        return res
   

    @api.depends('eta','etd')
    def _compute_ett(self):

        for record in self:

            if record.eta and record.etd:

                t1=datetime.strptime(str(record.etd),'%Y-%m-%d %H:%M:%S')
                t2=datetime.strptime(str(record.eta),'%Y-%m-%d %H:%M:%S')
                t3=t2-t1
                hours = round((t3.seconds)/60/60)
                record.ett=str(t3.days) + ' D ' + str(hours) + ' H'
            
            else:

                record.ett = False

    def action_received(self):

        self.ensure_one()

        if self.received == False:

            self.received = datetime.today()
            self.state = 'received'

            message = 'Good work! Keep it up.'

            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': message,
                    'img_url': '/web/static/src/img/smile.svg',
                    'type': 'rainbow_man',
                }
            }

    def action_underway(self):

        self.ensure_one()

        self.shipped = datetime.today()
        self.state = 'underway'

        message = 'The goods are now under way - please correct the ETA if it is not correct: ' + str(self.eta)

        return {
            'effect': {
                'fadeout': 'slow',
                'message': message,
                'img_url': '/web/static/src/img/smile.svg',
                'type': 'rainbow_man',
            }
        }

    def action_cancel(self):

        self.ensure_one()

        if self.received == False:
            
            self.state = 'cancel'

        else:

            message = 'We cant cancel, when it is already received. Talk to Mads, to get this as a function.'

            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': message,
                    'img_url': '/web/static/src/img/smile.svg',
                    'type': 'rainbow_man',
                }
            }

