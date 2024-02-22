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
    stock_ordered = fields.Integer(compute='_compute_stock_orderd',store=True)

    @api.depends('qty_available')
    def _compute_stock_orderd(self):
        for record in self:
            record.stock_ordered = record.qty_available - record.virtual_available


    def test(self):
        print('pk')


class StockQuantCustom(models.Model):
    _inherit = 'stock.quant'

    item_accurate_no = fields.Char('Accurate ID',compute="item_accurate_no_compute")

    @api.depends('product_id')
    def item_accurate_no_compute(self):
        for value in self:
            value.item_accurate_no = value.product_id.item_accurate_number
            

class ProductProductCustom(models.Model):
    _inherit = 'product.product'

    default_code_temp = fields.Char(compute='_compute_default_code',store=True)

    @api.depends('name')
    def _compute_default_code(self):
        for record in self:
            accurate_no = record.product_tmpl_id.item_accurate_number
            record.default_code_temp = accurate_no
            record.default_code = accurate_no