from odoo import models, fields,api


class StockInh(models.Model):
    _inherit = 'stock.picking'

    address_customer = fields.Char(string='Address Customer',compute='address_cust')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    state = fields.Selection(selection_add=[
        ('delivery', 'Delivery'), ('done',)
    ])

    def delivered(self):
        active_ids = self.env.context.get('active_ids', [])
        return {
            'type': 'ir.actions.act_window',
            'name': 'Delivered',
            'res_model': 'delivered.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'data': active_ids
            }
        }

    @api.depends('origin')
    def address_cust(self):
        for value in self:
            address = self.env['sale.order'].search(
                [('name', '=', value.origin)])
            value.address_customer = address.accurate_address

    # @api.depends('state')
    # def vehicle_compute(self):
    #     if self.state == 'done':
    #         print(self)
    #         # self.vehicle_id = None

