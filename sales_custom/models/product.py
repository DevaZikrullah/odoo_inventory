from odoo import models, api, http, fields


class ProductCustom(models.Model):
    _inherit = 'product.template'

    item_accurate_id = fields.Char('Accurate ID')
    item_accurate_number = fields.Char('Accurate Number')
    panjang = fields.Integer('Panjang')
    lebar = fields.Integer('Lebar')
    tinggi = fields.Integer('Tinggi')
