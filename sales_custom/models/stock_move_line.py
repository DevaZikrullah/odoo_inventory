from odoo import models, api, http, fields
from odoo.http import request


class StockMoveLines(models.Model):
    _inherit = 'stock.move.line'

    no_accurate_product = fields.Char('kode', compute='code_product_compute')

    @api.depends('product_id')
    def code_product_compute(self):
        for value in self:
            if value.product_id:
                # Use product_id.id to get the ID of the product template
                product_template_id = value.product_id.id
                code_product = self.env['product.template'].search([('id', '=', product_template_id)])
                if code_product:
                    # Assuming item_accurate_number is a field on product.template
                    value.no_accurate_product = code_product.item_accurate_number
                else:
                    value.no_accurate_product = False
            else:
                value.no_accurate_product = False


class StockMoveCustom(models.Model):
    _inherit = 'stock.move'

    origin = fields.Char('Origin', compute='compute_origin')
    cust = fields.Char('Customer', compute='compute_cust')
    have_rpb = fields.Boolean()

    @api.depends('product_id')
    def compute_origin(self):
        for value in self:
            value.origin = value.picking_id.origin

    @api.depends('product_id')
    def compute_cust(self):
        for value in self:
            value.cust = value.picking_id.partner_id.name

    @api.depends('product_id')
    def compute_have_rpb(self):
        for value in self:
            stock_picking_rpb = value.picking_id.count_rpb

            if stock_picking_rpb > 0:
                value.have_rpb = True
            else:
                value.have_rpb = False
