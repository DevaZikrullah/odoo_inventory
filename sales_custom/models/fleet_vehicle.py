from odoo import models, api, fields
from odoo.exceptions import UserError


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    set_limit = fields.Integer()
    limit_storage = fields.Integer('Limit Storage',compute="_compute_limit_srorage")
    fleet_order_line = fields.One2many('stock.picking', 'vehicle_id', 'Fleet Order Line')
    avail_storage = fields.Integer('Available', compute="_compute_avail_srorage")

    @api.onchange('set_limit')
    def onchange_limit(self):
        total = self.volume
        self.limit_storage = total * self.set_limit / 100

    @api.depends('limit_storage')
    def _compute_avail_srorage(self):
        for i in self:
            data = self.env['rpb.rpb'].search(
                [('state_rpb', '=', 'draft'), ('vehicle_id', 'in', self.ids)])
            count = 0
            for stor in data:
                count += stor.total_volume_product
            print(count)
            aa = i.limit_storage - count
            i.avail_storage = aa

    @api.depends('fleet_order_line')
    def calculate_storage(self):
        total_qty = []
        for value in self:
            if value.fleet_order_line:
                avail = value.fleet_order_line.move_line_ids
                for item in avail:
                    total_qty.append(item.product_uom_qty)
                self.avail_storage = value.limit_storage - sum(total_qty)
                if self.avail_storage < 0:
                    raise UserError('Muatan Penuh')

    @api.depends('volume')
    def _compute_limit_srorage(self):
        for i in self:
            i.limit_storage = i.volume


    # @api.depends('state')
    # def compute_staging(self):
    #     for item in self.fleet_order_line:
    #         item.
