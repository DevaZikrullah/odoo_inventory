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
                'state': 'delivered',
                'picking_type_id': 7
            })

    def _get_record_line(self):
        order_line = []
        product_data = {}  # Dictionary to store product data
        all_so_numbers = set()  # To store distinct Sales Order numbers

        for active_id in self.env.context.get('data'):
            record = self.env['stock.picking'].search([('id', '=', active_id)])
            sale_order_line = self.env['sale.order.line'].search([('order_id', '=', record.sale_id.id)])
            for value in sale_order_line:
                sale_order_name = self.env['sale.order'].search([('id', '=', value.order_id.id)])
                product_id = value.product_id.id
                product_qty = value.product_uom_qty
                all_so_numbers.add(sale_order_name.name)  # Collect distinct SO numbers

                if product_id in product_data:
                    product_data[product_id]['qty'] += product_qty
                    product_data[product_id]['so'].add(sale_order_name.name)
                    product_data[product_id]['customer'].add(sale_order_name.customer)
                else:
                    product_data[product_id] = {
                        'name': value.name,
                        'qty': product_qty,
                        'so': {sale_order_name.name},
                        'customer': {sale_order_name.customer}
                    }

        so_headers = ", ".join([f"SO={so}" for so in all_so_numbers])

        table_rows = ""
        for product_id, data in product_data.items():
            qty = data['qty']
            so_list = ", ".join(data['so'])
            customer_list = ", ".join(data['customer'])

            table_rows += f"""
            <tr>
                <td>{data['name']}</td>
                <td>{product_id}</td>
                <td>{qty}</td>
                <td>{so_list}</td>
                <td>{customer_list}</td>
            </tr>
            """

        table = f"""
        <table>
            <tr>
                <th colspan="5">Sales Orders: {so_headers}</th>
            </tr>
            <tr>
                <th>Product</th>
                <th>Product ID</th>
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
