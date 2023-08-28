from odoo import models, api, fields
from odoo.exceptions import UserError


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    limit_storage = fields.Integer('Limit Storage')
    fleet_order_line = fields.One2many('stock.picking', 'vehicle_id', 'Fleet Order Line')
    avail_storage = fields.Integer('Available', compute='calculate_storage', store=True)

    @api.depends('fleet_order_line')
    def calculate_storage(self):
        total_qty = []
        for value in self:
            if value.fleet_order_line:
                avail = value.fleet_order_line.move_line_ids
                for item in avail:
                    print(item.product_uom_qty)
                    total_qty.append(item.product_uom_qty)
                self.avail_storage = value.limit_storage - sum(total_qty)
                if self.avail_storage < 0:
                    raise UserError('Muatan Penuh')

    # @api.depends('state')
    # def compute_staging(self):
    #     for item in self.fleet_order_line:
    #         item.

