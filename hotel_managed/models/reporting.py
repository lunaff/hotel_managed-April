from odoo import models, fields, api
import xlsxwriter
import base64
from io import BytesIO


class ReportingWizard(models.TransientModel):
    _name = 'reporting.reporting'
    _description = 'Reporting Wizard'

    room_id = fields.Many2one('configuration.room', string="Room", required=True)
    customer = fields.Many2one('res.partner', string="Guest Name", related='reservation_id.customer', store=True, readonly=True) 
    check_in = fields.Datetime(string="Check In", required=True)
    check_out = fields.Datetime(string="Check Out", required=True)
    reservation_id = fields.Many2one('reservation.reservation', string="Reservation Reference")
    file_data = fields.Binary(string="File Data", readonly=True)
    file_name = fields.Char(string="File Name", readonly=True)
    def action_export_excel(self):
        domain = []

        # Apply filtering based on the room, customer, and reservation name
        if self.room_id:
            domain.append(('room_id', '=', self.room_id.id))
        if self.customer:
            domain.append(('customer', '=', self.customer.id))
        if self.name:
            domain.append(('name', 'ilike', self.name))

        # Filter based on the range between check_in and check_out
        if self.check_in and self.check_out:
            domain.extend([
                '|',  # OR condition
                '&', ('check_in', '<=', self.check_out), ('check_in', '>=', self.check_in),  # Condition 1
                '&', ('check_out', '>=', self.check_in), ('check_out', '<=', self.check_out)  # Condition 2
            ])

        reservations = self.env['reservation.reservation'].search(domain)

        output = BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()

        headers = ['No', 'Guest Name', 'Room', 'Check In', 'Check Out', 'Reservation Reference']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)

        for row_num, record in enumerate(reservations, start=1):
            worksheet.write(row_num, 0, row_num)  # No column
            worksheet.write(row_num, 1, record.customer.name if record.customer else '')  # Guest Name
            worksheet.write(row_num, 2, record.room_id.name if record.room_id else '')  # Room
            worksheet.write(row_num, 3, record.check_in.strftime('%Y-%m-%d %H:%M:%S') if record.check_in else '')  # Check In
            worksheet.write(row_num, 4, record.check_out.strftime('%Y-%m-%d %H:%M:%S') if record.check_out else '')  # Check Out
            worksheet.write(row_num, 5, record.name if record.name else '')  # Reservation Reference

        workbook.close()

        output.seek(0)
        file_data = base64.b64encode(output.read())
        output.close()

        self.write({
            'file_data': file_data,
            'file_name': "room_booking_report.xlsx"
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content?model={self._name}&id={self.id}&field=file_data&filename_field=file_name&download=true',
            'target': 'new',
        }

    # def action_generate_report(self):
    #     domain = []
        
    #     if self.room_id:
    #         domain.append(('room_id', '=', self.room_id.id))
    #     if self.customer:
    #         domain.append(('customer', '=', self.customer.id))        
    #     if self.name:
    #         domain.append(('name', 'ilike', self.name))        
    #     if self.check_in and self.check_out:
    #         domain.append('&') 
    #         domain.extend([
    #             ('check_in', '<=', self.check_out),   
    #             ('check_out', '>=', self.check_in),
    #         ])

    #     reservations = self.env['reporting.reporting'].search(domain)

    #     data = {
    #         'docs': reservations,
    #         'room_id': self.room_id.name if self.room_id else '',
    #         'customer': self.customer.name if self.customer else '',
    #         'check_in': self.check_in,
    #         'check_out': self.check_out,
    #         'name': self.name,
    #     }       

    #     return self.env.ref('hotel_managed.action_report_pdf_template').report_action(self, data=data)
