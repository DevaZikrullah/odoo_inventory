from odoo import models, fields, api
from odoo.exceptions import UserError
import random


class wizardRpb(models.TransientModel):
    _name = 'wizard.rpb'

    name = fields.Char(string="Name", compute='_compute_name')
    stock_picking_id = fields.Many2many('stock.picking', compute='_compute_stock_picking')
    sale_id = fields.Many2many('sale.order', compute='_compute_sale_id')
    vehicle_id = fields.Many2one('fleet.vehicle')
    driver_id = fields.Many2one('res.partner')
    delivery_date = fields.Date(default=fields.Date.today)
    picking_type_id = fields.Many2one('stock.picking.type')
    rpb_line_id = fields.One2many('wizard.rpb.line', 'rpb_id', compute='domain_rpb_line')
    isi_mobil = fields.Char()
    state_available = fields.Selection([
        ('available', 'Available'),
        ('full', 'Full Space')
    ])
    employee_line_ids = fields.One2many('employee.wizard', 'rpb_id')

    total_volume_product = fields.Integer()
    volume_available = fields.Integer()

            # @api.depends('vehicle_id')
            # def _compute_available_vehicle(self):
            #     for i in self:
            #         i.volume_available = 0
            #         if i.vehicle_id:
            #             limit_volume = self.env['fleet.vehicle'].search([('id', '=', i.vehicle_id.id)])
            #             rpb_car = self.env['rpb.rpb'].search([('state_rpb', '=', 'draft'), ('vehicle_id', '=', i.vehicle_id.id)]).total_volume_product
            #             total = limit_volume.limit_storage - rpb_car
            #             i.volume_available = total

    @api.onchange('vehicle_id')
    def vihaacle(self):
        self.driver_id = False
        if self.vehicle_id:
            self.driver_id = int(self.vehicle_id.driver_id)
        limit_volume = self.env['fleet.vehicle'].search([('id', '=', self.vehicle_id.id)])
        jumlah_barang = self.rpb_line_id


        # tamp_prd = []
        #
        # for prod in jumlah_barang:
        #     tamp_prd.append(int(prod.product_tmpl_id))

        # product = self.env['product.template'].search([('id', 'in', tamp_prd)])
        # print(tamp_prd)
        a = 0
        for i in jumlah_barang:
            a += int(self.env['product.template'].search([('id', '=', i.product_id.product_tmpl_id.id)]).volume) * int(
                i.done)
        rpb_car = self.env['rpb.rpb.view'].search(
            [('state_rpb', '=', 'draft'), ('vehicle_id', 'in', self.vehicle_id.ids)])
        print(rpb_car)
        print(limit_volume.limit_storage)
        rpb_car_count = 0
        for car in rpb_car:
            rpb_car_count += int(car.total_volume_product)
        volume_saat_ini = 0
        if self.vehicle_id:
            volume_saat_ini = a
        total = limit_volume.limit_storage - rpb_car_count - volume_saat_ini
        print(total)
        self.volume_available = total
        if a > int(total):
            self.total_volume_product = a
            self.state_available = 'full'
            # raise UserError('melebihi batas maximum')
            # self.vehicle_id = False
        else:
            self.total_volume_product = a
            self.state_available = 'available'





    @api.depends('stock_picking_id')
    def _compute_name(self):
        active_ids = self.env.context.get('active_ids', [])[0]
        self.name = "RPB/WHOUT/" + str(active_ids) + ""

    @api.onchange('stock_picking_id')
    def _compute_stock_picking(self):
        active_ids = self.env.context.get('active_ids', [])
        stock_picking = self.env['stock.picking'].search([('id', 'in', active_ids)])
        list = []
        for i in stock_picking:
            data = {
                "id": i.id
            }
            list.append(data['id'])
        self.stock_picking_id = list

    @api.onchange('sale_id')
    def _compute_sale_id(self):
        active_ids = self.env.context.get('active_ids', [])
        stock_picking = self.env['stock.picking'].search([('id', 'in', active_ids)])
        list = []
        for i in stock_picking:
            data = {
                "sale_id": i.sale_id.id
            }
            list.append(data['sale_id'])
        self.sale_id = list

    # @api.onchange('picking_type_id')
    def domain_picking_type(self):
        active_ids = self.env.context.get('active_ids', [])
        stock_picking = self.env['stock.picking'].search([('id', 'in', active_ids)])
        list = []
        for i in stock_picking:
            data = {
                "id": i.picking_type_id
            }
            list.append(data['id'])
        self.picking_type_id = list

    # @api.onchange('delivery_date')
    # def domain_delivery_date(self):
    #     active_ids = self.env.context.get('active_ids', [])
    #     stock_picking = self.env['stock.picking'].search([('id', 'in', active_ids)])
    #     self.delivery_date = stock_picking.scheduled_date

    @api.onchange('rpb_line_id')
    def domain_rpb_line(self):
        active_ids = self.env.context.get('active_ids', [])
        stock_move = self.env['stock.move'].search([('picking_id', 'in', active_ids)])
        list = []
        for i in stock_move:
            if not any(item[2]['product_id'] == i.product_id.id for item in list):
                res = 'Available'
                if i.forecast_availability < 1:
                    res = 'Not Available'
                data = {
                    'id': int(i.id),
                    'name': str(i.name),
                    'product_id': int(i.product_id),
                    'description': str(i.description_picking),
                    'date_scheduled': str(i.date),
                    'deadline': str(i.date_deadline),
                    'demand': i.product_uom_qty,
                    'reserved': res,
                    'done': i.quantity_done,
                    'qty': i.product_uom
                }
                list.append((0, 0, data))
            else:
                for it in list:
                    if it[2]['product_id'] == i.product_id.id:
                        it[2]['demand'] += i.product_uom_qty
                        it[2]['done'] += i.quantity_done

        print(list)
        self.rpb_line_id = list
        self.picking_type_id = 2
        # self.picking_type_id = int(stock_picking.picking_type_id)

    def rpb_button(self):
        active_ids = self.env.context.get('active_ids', [])
        rpb = self.env['rpb.rpb'].search([])
        rpb_cek = self.env['stock.picking'].search([('id', 'in', active_ids)])
        rpb_line = self.env['rpb.line'].search([])
        stock_move = self.env['stock.move'].search([('picking_id', 'in', active_ids)])
        list_rpb_view = []
        rpb_list = self.env['rpb.rpb.view'].search([])
        andom_number = random.randint(10, 100)
        jumlah_barang_b = self.rpb_line_id
        b = 0
        for i in jumlah_barang_b:
            b += int(self.env['product.template'].search([('id', '=', i.product_id.product_tmpl_id.id)]).volume) * int(
                i.done)
        for save in stock_move:
            list_rpb_view.append({
                "name": ''+str(self.name)+'/'+str(self.id)+'',
                "stock_picking_id": int(save.picking_id),
                "source_document_id": int(save.picking_id.sale_id),
                "product_id": int(save.product_id),
                "description": save.description_picking,
                "date_scheduled": save.date,
                'total_volume_product' : b,
                "deadline": save.date_deadline,
                "demand": save.product_uom_qty,
                "reserved": save.forecast_availability,
                "done": save.quantity_done,
                "uom": save.product_uom.id,
                "vehicle_id": self.vehicle_id.id,
                "driver_id": self.driver_id.id,
                "picking_type_id": self.picking_type_id.id
            })
        rpb_list.create(list_rpb_view)
        jumlah_barang = self.rpb_line_id
        # tamp_prd = []
        #
        # for prod in jumlah_barang:
        #     tamp_prd.append(int(prod.product_tmpl_id))

        # product = self.env['product.template'].search([('id', 'in', tamp_prd)])
        # print(tamp_prd)
        a = 0
        for i in jumlah_barang:
            a += int(self.env['product.template'].search([('id', '=', i.product_id.product_tmpl_id.id)]).volume) * int(
                i.done)
        list = []
        for j in stock_move:
            if not any(item[2]['product_id'] == j.product_id.id for item in list):
                res = 'Available'
                if j.forecast_availability < 1:
                    res = 'Not Available'
                list.append((0, 0, {
                    'name': str(j.name),
                    'product_id': int(j.product_id),
                    'description': str(j.description_picking),
                    'date_scheduled': str(j.date),
                    'deadline': str(j.date_deadline),
                    'demand': j.product_uom_qty,
                    'reserved': j.forecast_availability,
                    'done': j.quantity_done,
                    'qty': int(j.product_uom)
                }))
                # data = {
                #     'id': int(i.id),
                #     'name': str(i.name),
                #     'product_id': int(i.product_id),
                #     'description': str(i.description_picking),
                #     'date_scheduled': str(i.date),
                #     'deadline': str(i.date_deadline),
                #     'demand': i.product_uom_qty,
                #     'reserved': res,
                #     'done': i.quantity_done,
                #     'qty': i.product_uom
                # }
                # list.append((0, 0, data))
            else:
                for it in list:
                    if it[2]['product_id'] == j.product_id.id:
                        it[2]['demand'] += j.product_uom_qty
                        it[2]['done'] += j.quantity_done
            
            # rpb_line.create(data_line)
        data = {
            'name': ''+str(self.name)+'/'+str(self.id)+'',
            'stock_picking_id': self.stock_picking_id,
            'sale_id': self.sale_id,
            'vehicle_id': self.vehicle_id.id,
            'driver_id': self.driver_id.id,
            'total_volume_product': a,
            'delivery_date': self.delivery_date,
            'picking_type_id': self.picking_type_id.id,
            'rpb_line_ids': list
        }
        rpb.create(data)

        print(active_ids)

    def cancel_button(self):
        return {'type': 'ir.actions.act_window_close'}


class wizardRpbLine(models.TransientModel):
    _name = 'wizard.rpb.line'

    name = fields.Char()
    product_id = fields.Many2one('product.product')
    description = fields.Text()
    date_scheduled = fields.Date()
    deadline = fields.Date()
    demand = fields.Float()
    reserved = fields.Char()
    done = fields.Float()
    qty = fields.Many2one('uom.uom', string="Uom")
    rpb_id = fields.Many2one('wizard.rpb')


class employeeOrker(models.TransientModel):
    _name = 'employee.wizard'

    employee_id = fields.Many2one('hr.employee')
    worked_hours = fields.Float(string="Work Hours", store="true")
    rpb_id = fields.Many2one('wizard.rpb')