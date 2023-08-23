from odoo import models, api, http, fields
from odoo.http import request


class StockInh(models.Model):
    _inherit = 'stock.picking.type'

    # item_accurate_id = fields.Char('Accurate ID')
    # accurate_status = fields.Char()
    # customer = fields.Char()
    # no_accurate = fields.Char()

    def action_accurate(self):
        return "po"
