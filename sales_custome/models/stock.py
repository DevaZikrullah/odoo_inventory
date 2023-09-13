from odoo import models, fields, api
from odoo.exceptions import UserError
from ..controllers import main


class StockInh(models.Model):
    _inherit = 'stock.picking'

    address_customer = fields.Char(string='Address Customer', compute='address_cust')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    state = fields.Selection(selection_add=[
        ('rpb', 'RPB'),
        ('deliverey', 'To Delivery'), ('done',)])
    temp_storage_show = fields.Boolean()
    count_rpb = fields.Integer(compute='_compute_ccount_rpb')

    @api.depends('address_customer','vehicle_id','state','temp_storage_show','count_rpb')
    def _compute_ccount_rpb(self):
        active_ids = self.env.context.get('active_ids', [])
        a = self.env['rpb.rpb.view'].search([('stock_picking_id', 'in', self.ids)])
        list = []
        for i in a:
            list.append(i.id)
        self.count_rpb = len(list)

    def action_rpb_tree(self):
        active_ids = self.env.context.get('active_ids', [])
        picking_id = self.env['stock.picking'].search([('id', 'in', active_ids)])
        list = []
        for i in picking_id:
            list.append(i.state)
        print(list)
        if any(item != 'assigned' for item in list):
            raise UserError('Status Harus Ready!')
            print('l')
        a = self.env['rpb.rpb.view'].search([('stock_picking_id', 'in', active_ids)])
        for d in a:
            if d:
                raise UserError('RPB sudah dibuat')
        else:
            self.move_lines._set_quantities_to_reservation()
            return {
                'type': 'ir.actions.act_window',
                'name': 'Create RPB',
                'res_model': 'wizard.rpb',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
            }

    def action_rpb_form(self):
        print(self.count_rpb)
        active_ids = self.env.context.get('active_ids', [])[0]
        self.move_lines._set_quantities_to_reservation()
        a = self.env['rpb.rpb.view'].search([('stock_picking_id', '=', int(self.id))])
        if a:
            raise UserError('RPB sudah dibuat')
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Create RPB',
                'res_model': 'wizard.rpb',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
            }

    def action_create_rpb(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create RPB',
            'res_model': 'wizard.rpb',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('sales_custome.wizard_rpb_form_view')
        }

    def action_count(self):
        active_ids = self.env.context.get('active_ids', [])
        picking_id = self.env['rpb.rpb.view'].search([('stock_picking_id', 'in', self.ids)])
        return {
            "type": 'ir.actions.act_window',
            "name": 'RPB',
            "domain": [('id', 'in', picking_id.ids)],
            "res_model": 'rpb.rpb.view',
            "view_mode": 'tree,form'}

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
            value.address_customer = address.accurate_address

    def update_customer_button(self):
        cust = main.SaleOrderController()
        cust.get_customer()

    def update_product_button(self):
        product = main.SaleOrderController()
        product.get_product_accurate()

    def sync_button(self):
        accurate = main.SaleOrderController()
        # print(self.ids)
        data = self.env['stock.picking'].search([('id', '=', self.ids)])
        so = self.env['sale.order'].search[(['name', '=', data.origin])]
        print()
        # accurate.accurate_so_sync()
        # print('mantap')


class flettVolume(models.Model):
    _inherit = 'fleet.vehicle'

    length = fields.Float()
    height = fields.Float()
    width = fields.Float()
    volume = fields.Integer()
