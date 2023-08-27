from odoo import models, fields


class Delivered(models.Model):
    _name = 'delivered.wizard'

    vehicle_id = fields.Many2one('fleet.vehicle')

    def delivered_button(self):
        for active_id in self.env.context.get('data'):
            stock_picking = self.env['stock.picking'].search([('id', '=', active_id)])
            stock_picking.write({
                'vehicle_id': int(self.vehicle_id)
            })
