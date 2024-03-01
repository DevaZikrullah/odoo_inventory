from odoo import models, fields, api
from ..controllers import main
import requests

picking_type_list = [10, 9, 2]


class stockReportWizard(models.TransientModel):
    _name = 'stock.report.wizard'

    date_from = fields.Date()
    date_to = fields.Date(default=fields.Date.today())

    def button_execute(self):
        self._cr.execute('DELETE FROM temp_stock ')
        date_from = self.date_from.strftime('%Y-%m-%d')
        date_to = self.date_to.strftime('%Y-%m-%d')
        stock_move = self.env['stock.move'].search([('date', '>=', date_from), ('date', '<=', date_to)],
                                                   order='product_id asc')
        temp_stock = self.env['temp.stock']
        previous_record_vals = None
        for record in stock_move:
            picking_id = record.picking_id
            exist_rpb = self.env['rpb.rpb.view'].search([('stock_picking_id', '=', picking_id.id)])
            picking_type = picking_id.picking_type_id

            record_vals = {
                'reference': picking_id.name,
                'date': record.date,
                'name': record.product_id.product_tmpl_id.name,
                'product_id': record.product_id.id,
                'move_id': record.id,
                'qty': record.product_qty,
                'location_id': record.location_id.id,
                'location_dest_id': record.location_dest_id.id
            }
            if previous_record_vals:
                if previous_record_vals['product_id'] == record.product_id.id:
                    previous_record_vals
                    # print(previous_record_vals)
                    # print(record_vals)
                    # exit()


            if picking_type.id in picking_type_list:
                if picking_type.id == 2 and exist_rpb:
                    record_vals['is_subtraction'] = True
                    record_vals['stock_out'] = record.product_qty
                    temp_stock.sudo().create(record_vals)
                elif picking_type.id != 2:
                    if picking_type.id == 9:
                        record_vals['is_addition'] = True
                        record_vals['stock_in'] = record.product_qty
                    elif picking_type.id == 10:
                        record_vals['is_subtraction'] = True
                        record_vals['stock_in'] = record.product_qty
                    temp_stock.sudo().create(record_vals)
                    


            previous_record_vals = record_vals
