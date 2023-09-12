from odoo import models, api, http, fields
from odoo.http import request


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    item_accurate_id = fields.Char('Accurate ID')
    accurate_status = fields.Char()
    vendor_accurate = fields.Char()
