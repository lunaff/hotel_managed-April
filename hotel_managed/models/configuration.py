from odoo import fields, models, api

class ConfigurationFloor(models.Model):
    _name = "configuration.floor"
    _description = "Floor"

    name = fields.Char(string="Name", required=True)
    manager = fields.Char(string="Manager", required=True)
    description = fields.Text()

    _sql_constraints = [
        ("name_uniq", "unique(name)", "The floor name must be unique"),
    ]

class ConfigurationService(models.Model):
    _name = "configuration.service"
    _description = "Service"

    name = fields.Char(string="Name", required=True)
    price = fields.Float(string="Price", required=True)
    description = fields.Text()

    _sql_constraints = [
        ("name_uniq", "unique(name)", "The service name must be unique"),
    ]

class ConfigurationAmenity(models.Model):
    _name = "configuration.amenity"
    _description = "Amenity"

    name = fields.Char(string="Name", required=True)
    icon = fields.Binary(string="Icon", required=True)
    description = fields.Text()
    quantity = fields.Integer(string="Quantity", default=1)
    price = fields.Float(string="Price", default=0.0)
    subtotal = fields.Float(string="Subtotal", compute="_compute_subtotal", store=True)
    product_id = fields.Many2one('product.product', string="Related Product", readonly=True)

    _sql_constraints = [
        ("name_uniq", "unique(name)", "The Amenity name must be unique"),
    ]

    @api.model
    def create(self, vals):
        product_vals = {
            'name' : vals['name'], 
            'detailed_type' : 'product',
            'sale_ok' : True,
            'purchase_ok' : False,
            'image_1920' : vals.get('icon')
        }
        product = self.env['product.product'].create(product_vals)
        vals['product_id'] = product.id
        return super(ConfigurationAmenity, self).create(vals)

    @api.depends('quantity', 'price')
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = record.quantity * record.price

class ConfigurationRoom(models.Model):
    _name = "configuration.room"
    _description = "Rooms"

    name = fields.Char(string="Name", required=True)
    icon = fields.Binary(string="Icon", required=True)
    state = fields.Selection([
        ("available", "Available"), 
         ("reserved", "Reserved"), 
         ("occupied", "Occupied")
         ],
        default="available",
        string="Status"
    )
    capacity = fields.Integer(string='Capacity')  # Definisikan field capacity di sini
    floor_id = fields.Many2one('configuration.floor', string='Floor')
    manager_id = fields.Many2one('res.users', string='Room Manager')
    room_type = fields.Selection([
        ('single', 'Single'),
        ('double', 'Double'),
        ('suite', 'Suite'),
    ], string='Room Type', required=True)
    rent = fields.Float(string='Rent')
    persons = fields.Integer(string='Number of Person')
    cost = fields.Float(string='Cost')
    amenity_ids = fields.Many2many('configuration.amenity', string='Amenities')
    description = fields.Text()
    reservation_ids = fields.One2many('reservation.reservation', 'room_id', string='Reservations')

    _sql_constraints = [
        ("name_uniq", "unique(name)", "The Room name must be unique"),
    ]

    @api.depends('reservation_ids.state')
    def _compute_state(self):
        """Compute the state of the room based on the associated reservations."""
        for room in self:
            if room.reservation_ids.filtered(lambda r: r.state == 'check_in'):
                room.state = 'reserved'
            elif room.reservation_ids.filtered(lambda r: r.state == 'check_out'):
                room.state = 'available'
            else:
                room.state = 'occupied'