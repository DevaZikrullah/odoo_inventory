from odoo import models, api, http, fields


class ProductCustom(models.Model):
    _inherit = 'product.template'

    item_accurate_id = fields.Char('Accurate ID')
    item_accurate_number = fields.Char('Accurate Number')
    # accurate_warehouse = fields.Char('Warehouse')
    panjang = fields.Integer('Panjang')
    lebar = fields.Integer('Lebar')
    tinggi = fields.Integer('Tinggi')
    volume = fields.Integer()


    def test(self):
        print('pk')