from odoo import models, fields, api
from odoo.exceptions import UserError
import datetime
import pytz



class UpdateStock(models.Model):
    _name = 'update.stock.wizard'

    product_target = fields.Many2one('product.template', 'Product', required=True)
    qty = fields.Integer('Total Barang Masuk', required=True)

    def button_confirm(self):
        indonesia_timezone = pytz.timezone('Asia/Jakarta')
        current_datetime = datetime.datetime.now(indonesia_timezone)
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        stock_move = self.env['stock.move.line']

        item_adjustment_accurate_in = self.env['stock.picking'].create({
            'name': 'BM/' + formatted_datetime.replace(' ', '/'),
            'origin': 'BM/' + formatted_datetime.replace(' ', '/'),
            'desc_barang': 'Barang Masuk',
            'picking_type_id': 9,
            'location_id': 14,
            'location_dest_id': 8,
            'state': 'assigned'
        })

        stock_move.create({
            'product_id': int(self.product_target),
            'product_uom_qty': int(self.qty),
            'picking_id': item_adjustment_accurate_in.id,
            'product_uom_id': self.product_target.uom_id.id,
            'location_id': item_adjustment_accurate_in.location_id.id,
            'location_dest_id': item_adjustment_accurate_in.location_dest_id.id,
            'qty_done': int(self.qty),
        })

        if item_adjustment_accurate_in and item_adjustment_accurate_in.move_lines:
            item_adjustment_accurate_in.write({
                'desc_barang': 'Barang Masuk',
                'state': 'assigned'
            })

        item_adjustment_accurate_in.button_validate()
