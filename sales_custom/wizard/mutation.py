from odoo import models, fields
from odoo.exceptions import UserError
import datetime
import pytz



class Mutation(models.Model):
    _name = 'mutation.wizard'

    product_target = fields.Many2one('product.template', 'Product',required=True)
    product_dest = fields.Many2one('product.template', 'Product Destination',required=True)
    qty = fields.Integer('Total Qty Yang Akan di Mutasi',required=True)
    qty_dest = fields.Integer('Total Pcs Yang akan di Masukan',required=True)

    def button_confirm(self):
        indonesia_timezone = pytz.timezone('Asia/Jakarta')
        current_datetime = datetime.datetime.now(indonesia_timezone)
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        stock_move = self.env['stock.move.line']

        item_adjustment_accurate_in = self.env['stock.picking'].create({
            'name': 'BM/' + formatted_datetime.replace(' ', '/'),
            'origin': 'BM/' + formatted_datetime.replace(' ', '/'),
            'desc_barang': 'Barang Masuk Mutasi',
            'picking_type_id': 9,
            'location_id': 14,
            'location_dest_id': 8,
            'state': 'assigned'
        })

        stock_move.create({
            'product_id': int(self.product_dest),
            'product_uom_qty': int(self.qty_dest),
            'picking_id': item_adjustment_accurate_in.id,
            'product_uom_id': self.product_dest.uom_id.id,
            'location_id':             item_adjustment_accurate_in.location_id.id,
            'location_dest_id': item_adjustment_accurate_in.location_dest_id.id,
            'qty_done': int(self.qty_dest),
        })

        if item_adjustment_accurate_in and item_adjustment_accurate_in.move_lines:
            item_adjustment_accurate_in.write({
                'state': 'assigned'
            })

        item_adjustment_accurate_out = self.env['stock.picking'].create({
            'name': 'BK/' + formatted_datetime.replace(' ', '/'),
            'origin': 'BK/' + formatted_datetime.replace(' ', '/'),
            'desc_barang': 'Barang Keluar Mutasi',
            'picking_type_id': 10,
            'location_id': 8,
            'location_dest_id': 14,
        })

        stock_move.create({
            'product_id': int(self.product_target),
            'picking_id': item_adjustment_accurate_out.id,
            'product_uom_id': self.product_target.uom_id.id,
            'location_id': item_adjustment_accurate_out.location_id.id,
            'location_dest_id': item_adjustment_accurate_out.location_dest_id.id,
            'qty_done': int(self.qty),
        })

        if item_adjustment_accurate_out and item_adjustment_accurate_out.move_lines:
            item_adjustment_accurate_out.write({
                'state': 'assigned'
            })

        item_adjustment_accurate_in.button_validate()
        item_adjustment_accurate_out.button_validate()

