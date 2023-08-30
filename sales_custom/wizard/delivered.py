from odoo import models, fields


class Delivered(models.Model):
    _name = 'delivered.wizard'

    vehicle_id = fields.Many2one('fleet.vehicle')
    cust_temp = fields.Char('Customer')
    display_order_line = fields.Char(default=lambda self: self._get_record_line())

    def delivered_button(self):
        next_stages_id = []
        for active_id in self.env.context.get('data'):
            stock_picking = self.env['stock.picking'].search([('id', '=', active_id)])
            stock_picking.write({
                'name': stock_picking.name + '/' + self.vehicle_id.name,
                'vehicle_id': int(self.vehicle_id),
                'state': 'draft',
            })
            next_stages_id.append(active_id)
        for value_id in next_stages_id:
            stock_picking = self.env['stock.picking'].search([('id', '=', value_id)])
            stock_picking.write({
                'state': 'loading',
                'picking_type_id': 8
            })

    def _get_record_line(self):
        order_line = []
        so = []
        for active_id in self.env.context.get('data'):
            record = self.env['stock.picking'].search([('id', '=', active_id)])
            # for item in record.sale_id.id:
            #     so.append(item)
            # # print(record.sale_id.id)
            sale_order_line = self.env['sale.order.line'].search([('order_id', '=', record.sale_id.id)])
            for value in sale_order_line:
                sale_order_name = self.env['sale.order'].search([('id', '=', value.order_id.id)])
                formatted_data = {
                    'Product': value.name,
                    'Qty': value.product_uom_qty,
                    'SO':sale_order_name.name,
                    'Customer':sale_order_name.customer
                }
                order_line.append(formatted_data)
        print(order_line)

        table_rows = ""
        for data in order_line:
            table_rows += f"""
            <tr>
                <td>{data['Product']}</td>
                <td>{data['Qty']}</td>
                <td>{data['SO']}</td>
                <td>{data['Customer']}</td>
            </tr>
            """

        table = f"""
        <table>
            <tr>
                <th>Product</th>
                <th>Quantity</th>
                <th>SO</th>
                <th>Customer</th>
            </tr>
            {table_rows}
        </table>
        """

        return table

    def cancel_button(self):
        for active_id in self.env.context.get('data'):
            stock_picking = self.env['stock.picking'].search([('id', '=', active_id)])
            stock_picking.write({
                'temp_storage_show': False
            })
        return {'type': 'ir.actions.act_window_close'}
