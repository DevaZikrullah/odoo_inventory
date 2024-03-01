from odoo import models, api, http, fields


class temporaryStock(models.Model):
    _name = 'temp.stock'

    name = fields.Char()
    reference = fields.Char()
    date = fields.Date()
    move_id = fields.Many2one('stock.move')
    product_id = fields.Many2one('product.product')
    location_id = fields.Many2one('stock.location')
    location_dest_id = fields.Many2one('stock.location')
    qty = fields.Integer()
    origin = fields.Char()
    cust_address = fields.Char()
    is_addition = fields.Boolean()
    is_subtraction = fields.Boolean()
    is_pending = fields.Boolean()
    is_mutation_in = fields.Boolean()
    is_mutation_out = fields.Boolean()
    initial_stock = fields.Integer()
    stock_in = fields.Integer()
    stock_out = fields.Integer()
    mutation_in = fields.Integer()
    mutation_out = fields.Integer()
    final_stock = fields.Integer()
    pending_stock = fields.Integer()





