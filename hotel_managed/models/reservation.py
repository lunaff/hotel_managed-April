from odoo import models, fields, api

class Reservation(models.Model):
    _name = 'reservation.reservation'
    _description = 'Reservation'

    name = fields.Char(required=True, readonly=True, default='New')
    reservation_id = fields.Many2one('reservation.reservation', string='Reservation', required=True, ondelete='cascade')
    customer = fields.Many2one('res.partner', string='Customer', required=True)
    invoice_address = fields.Many2one('res.partner', string='Invoice Address', required=True)
    order_date = fields.Datetime(string='Order Date', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('check_in', 'Check In'),
        ('check_out', 'Check Out'),
        ('done', 'Done')
    ], string='Status', default="draft",required=True)
    room_id = fields.Many2one('configuration.room', string='Room', required=True)
    check_in = fields.Datetime(string='Check In', required=True)
    booking = fields.Datetime(string='Booking Date')
    check_out = fields.Datetime(string='Check Out', required=True)
    duration = fields.Float(string='Duration', compute='_compute_duration', store=True)
    unit_of_measure = fields.Many2one('uom.uom', string='Unit of Measure',  default=lambda self: self.env.ref('uom.product_uom_day').id)
    rent = fields.Float(string='Rent', required=True)
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)
    total = fields.Float(string='Total', compute='_compute_total', store=True, )

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('reservation.sequence')
        return super(Reservation, self).create(vals)

    def write(self, vals):
        if 'name' in vals and vals['name'] == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('reservation.sequence')
        return super(Reservation, self).write(vals)

    def action_check_in(self):
        for rec in self:
            rec.state = 'check_in'
            rec.room_id.state = 'reserved'  

    def action_check_out(self):
        for rec in self:
            rec.state = 'check_out'
            rec.room_id.state = 'available'  

    def action_done(self):
        for rec in self:
            rec.state = 'done'
            rec.room_id.state = 'available' 

    @api.depends('check_in', 'check_out')
    def _compute_duration(self):
        for record in self:
            if record.check_in and record.check_out:
                check_in_dt = fields.Datetime.from_string(record.check_in)
                check_out_dt = fields.Datetime.from_string(record.check_out)
                record.duration = (check_out_dt - check_in_dt).days

    @api.depends('duration', 'rent')
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = record.duration * record.rent

    @api.depends('subtotal')
    def _compute_total(self):
        for record in self:
            record.total = record.subtotal

    @api.onchange('room_id')
    def _onchange_room_id(self):
        if self.room_id:
            self.rent = self.room_id.rent 
    
    def action_create_invoice(self):
        for reservation in self:
            invoice_vals = {
                'partner_id': reservation.customer.id,
                'move_type': 'out_invoice',
                'invoice_date': fields.Date.context_today(self),
                'invoice_line_ids': [(0, 0, {
                    'name': reservation.name,
                    'quantity': 1,
                    'price_unit': reservation.total,
                })]
            }
            invoice = self.env['account.move'].create(invoice_vals)
            return {
                'name': 'Customer Invoice',
                'view_mode': 'form',
                'res_model': 'account.move',
                'res_id': invoice.id,
                'view_id': self.env.ref('account.view_move_form').id,
                'type': 'ir.actions.act_window',
                'target': 'current',
            }
