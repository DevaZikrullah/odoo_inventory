from odoo import models, fields, api
from odoo.exceptions import UserError,AccessError
from ..controllers import main
from terbilang import Terbilang



class StockInh(models.Model):
    _inherit = 'stock.picking'

    address_customer = fields.Char(string='Address', compute='address_cust')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    state = fields.Selection(selection_add=[
            ('rpb', 'RPB'),('done',)])
    temp_storage_show = fields.Boolean()
    is_invoice = fields.Char('Faktur',compute='is_invoices')
    count_rpb = fields.Integer(compute='_compute_ccount_rpb')
    desc_barang = fields.Char('Desc')
    city_cust = fields.Char('Kota',compute='address_city')
    rute_so = fields.Char(string="Rute")


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

    def convert_amount_to_words(self):
        t = Terbilang()
        t.parse(int(self.sale_id.amount_total))
        return t.getresult()

    def cancel_so(self):
        for data in self:
            data.write({
                'state' : 'assigned'
            })
            rpb = self.env['rpb.rpb'].search(
                [('sale_id', '=', data.sale_id.id)])
            list_sale = []
            list_stock_picking = []
            for value in rpb.sale_id:
                if value.id != data.sale_id.id:
                    list_sale.append(value.id)
            for value in rpb.stock_picking_id:
                if value.id != data.id:
                    list_stock_picking.append(value.id)
            rpb_view = self.env['rpb.rpb.view'].search(
                [('source_document_id', '=', data.sale_id.id)])
            rpb_view.unlink()


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

        # Issue 1: 'list' variable should not be shadowed
        status_list = []  # Renamed 'list' to 'status_list'
        for i in picking_id:
            status_list.append(i.state)

        # Issue 2: The condition should be 'or', not 'or' in list
        if any(item in ['draft', 'waiting', 'done', 'cancel'] for item in status_list):
            raise UserError('Status Harus Siap Atau Menunggu!')

        a = self.env['rpb.rpb.view'].search([('stock_picking_id', 'in', active_ids)])

        # Issue 3: Correct the condition for 'state_rpb'
        if any(d.state_rpb in ['being_delivered', 'already_sent'] for d in a):
            raise UserError('RPB sudah dibuat')

        # Issue 4: Use 'return' to open a new form view
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
        print(a)
        exit()
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
