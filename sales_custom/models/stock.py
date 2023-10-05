from odoo import models, fields, api
from odoo.exceptions import UserError,AccessError
from ..controllers import main


class StockInh(models.Model):
    _inherit = 'stock.picking'

    address_customer = fields.Char(string='Address', compute='address_cust')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    state = fields.Selection(selection_add=[
        ('rpb','RPB'),
        ('deliverey', 'To Delivery'), ('done',)])
    temp_storage_show = fields.Boolean()
    is_invoice = fields.Char('Faktur',compute='is_invoices')
    count_rpb = fields.Integer(compute='_compute_ccount_rpb')
    desc_barang = fields.Char('Desc')
    city_cust = fields.Char('Kota',compute='address_city')


    def redirect_url_accurate(self):
        raise AccessError('https://account.accurate.id/oauth/authorize?client_id=8de2a1e6-4b1c-4ca2-8898-f0bd18ed0447'
                          '&response_type=token&redirect_uri=http://localhost:8069/web/assets/aol-oauth-callback'
                          '&scope=purchase_order_view+item_view+sales_order_view+customer_view+vendor_view')


    @api.depends('origin')
    def address_city(self):
        for value in self:
            address = self.env['res.partner'].search(
                [('name', '=', value.partner_id.id)], limit=1)
            value.city_cust = address.city



    def _compute_ccount_rpb(self):
        for line in self:
            a = self.env['rpb.rpb.view'].search([('stock_picking_id', '=', line.id)])
            list = []
            for i in a:
                list.append(i.id)
            self.count_rpb = len(list)

    def action_rpb_tree(self):
        active_ids = self.env.context.get('active_ids', [])
        picking_id = self.env['stock.picking'].search([('id', 'in', active_ids)])
        for i in self:
            i.move_lines._set_quantities_to_reservation()
        list = []
        for i in picking_id:
            list.append(i.state)
        print(list)
        if any(item == 'draft' or item == 'waiting' or item == 'done' or item == 'cancel' for item in list):
            raise UserError('Status Harus Siap Atau Menunggu!')
            print('l')
        a = self.env['rpb.rpb.view'].search([('stock_picking_id', 'in', active_ids)])
        for d in a:
            if d:
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
        for line in self:
            # raise UserError(line.id)
            # picking_id = self.env['rpb.rpb.view'].search([('stock_picking_id', '=', int(line.id))])
            return {
                "type": 'ir.actions.act_window',
                "name": 'RPB',
                "domain": [('stock_picking_id', '=', line.id)],
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
                [('name', '=', value.origin)],limit=1)
            value.address_customer = address.accurate_address

    @api.depends('origin')
    def is_invoices(self):
        for value in self:
            address = self.env['sale.order'].search(
                [('name', '=', value.origin)], limit=1)
            value.is_invoice = address.has_been_invoiced

    def update_customer_button(self):
        cust = main.SaleOrderController()
        cust.get_customer()

    def update_vendor_button(self):
        cust = main.SaleOrderController()
        cust.get_vendor()

    def update_product_button(self):
        product = main.SaleOrderController()
        product.get_product_accurate()
    
    def update_product_qty_button(self):
        product = main.SaleOrderController()
        product.get_product_accurate_qty()

    def sync_button(self):
        accurate = main.SaleOrderController()
        data = self.env['stock.picking'].search([('id', '=', self.ids)])
        so = self.env['sale.order'].search([('name', '=', data.origin)])
        accurate.accurate_so_sync(so.id,so.item_accurate_id)

class flettVolume(models.Model):
    _inherit = 'fleet.vehicle'

    length = fields.Float()
    height = fields.Float()
    width = fields.Float()
    volume = fields.Integer()
