from odoo import models, fields, api
from ..controllers import main


class StockInh(models.Model):
    _inherit = 'stock.picking'

    address_accurate = fields.Char(string='Address', compute='address_cust')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    state = fields.Selection(selection_add=[
        ('rpb','RPB'),
        ('deliverey', 'To Delivery'), ('done',)])
    temp_storage_show = fields.Boolean()

    def delivered(self):
        active_ids = self.env.context.get('active_ids', [])
        for value in active_ids:
            self.env['stock.picking'].search([('id', '=', value)]).write({
                'temp_storage_show': True
            })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Delivered',
            'res_model': 'delivered.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'data': active_ids
            }
        }

    def rpb(self):
        active_ids = self.env.context.get('active_ids', [])
        for value in active_ids:
            self.env['stock.picking'].search([('id', '=', value)]).write({
                'temp_storage_show': True
            })
        return {
            'type': 'ir.actions.act_window',
            'name': 'RPB',
            'res_model': 'rpb.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'data': active_ids
            }
        }


    @api.depends('origin')
    def address_cust(self):
        for value in self:
            address = self.env['sale.order'].search(
                [('name', '=', value.origin)])
            value.address_accurate = address.accurate_address

    def update_customer_button(self):
        cust = main.SaleOrderController()
        cust.get_customer()

    def update_vendor_button(self):
        cust = main.SaleOrderController()
        cust.get_vendor()

    def update_product_button(self):
        product = main.SaleOrderController()
        product.get_product_accurate()
    def sync_button(self):
        accurate = main.SaleOrderController()
        # print(self.ids)
        data = self.env['stock.picking'].search([('id', '=', self.ids)])
        so = self.env['sale.order'].search[(['name','=',data.origin])]
        print()
        # accurate.accurate_so_sync()
        # print('mantap')

