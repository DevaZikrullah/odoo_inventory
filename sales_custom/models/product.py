from odoo import models, api, http, fields
from odoo.http import request


class ProductCustom(models.Model):
    _inherit = 'product.template'

    item_accurate_id = fields.Char('Accurate ID')
    item_accurate_number = fields.Char('Accurate Number')
