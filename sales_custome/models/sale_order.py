from odoo import models, api, http, fields
from odoo.http import request


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    item_accurate_id = fields.Char('Accurate ID')
    accurate_status = fields.Char()
    customer = fields.Char()
    no_accurate = fields.Char()
    accurate_address = fields.Char()
