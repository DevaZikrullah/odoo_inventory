from odoo import models, fields, api,_
from odoo.exceptions import UserError
import random
import datetime

class wizardRpb(models.TransientModel):
    _name = 'wizard.rpb'

    name = fields.Char(string="Name", index=True, default=lambda self: _('New'),compute='_compute_name')
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
        limit_volume  = self.env['fleet.vehicle'].search([('id', '=', self.vehicle_id.id)])
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
                i.demand)
        # raise UserError(a)
        rpb_car = self.env['rpb.rpb.view'].search(
            [('state_rpb', '=', 'draft'), ('vehicle_id', 'in', self.vehicle_id.ids), ('create_date','=',datetime.datetime.now())])
        
        print(rpb_car)
        print(datetime.datetime.now())
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

    @api.onchange('rpb_line_id')
    def _compute_name(self):
        for record in self:
            interval = self.env['count.wizard'].search([],order='id asc',limit=1)
            date = datetime.datetime.now()
            record.name = 'RPB.'+str(date.year).zfill(4)+'.'+str(date.month).zfill(2)+"."+str(interval.id_interval).zfill(5)

    @api.onchange('stock_picking_id')
    def _compute_stock_picking(self):
        active_ids = self.env.context.get('id_active')
        stock_picking = self.env['stock.picking'].search([('sale_id', 'in', active_ids)])
        list = []
        for i in stock_picking:
            data = {
                "id": i.id
            }
            list.append(data['id'])
        self.stock_picking_id = list

    @api.onchange('sale_id')
    def _compute_sale_id(self):
        active_ids = self.env.context.get('id_active')
        stock_picking = self.env['stock.picking'].search([('sale_id', 'in', active_ids)])
        list = []
        for i in stock_picking:
            data = {
                "sale_id": i.sale_id.id
            }
            list.append(data['sale_id'])
        self.sale_id = list

    # @api.onchange('picking_type_id')
    def domain_picking_type(self):
        active_ids = self.env.context.get('id_active')
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
        active_ids = self.env.context.get('id_active')
        picking_ids = []
        for record in active_ids:
            picking_ids.append(self.env['stock.picking'].search([('sale_id', '=', record)]).id)

        stock_move = self.env['stock.move'].search([('picking_id', 'in', picking_ids)])
        list = []
        for i in stock_move:
            if not any(item[2]['product_id'] == i.product_id.id for item in list):
                res = 'Available'
                if i.forecast_availability < 1:
                    res = 'Not Available'
                deadline = ''
                scdule = ''
                if i.date_deadline:
                    deadline = i.date_deadline
                if i.date:
                    scdule = i.date
                data = {
                    'id': int(i.id),
                    'name': str(i.name) or '',
                    'product_id': int(i.product_id) or 0,
                    'description': str(i.description_picking) or '',
                    'date_scheduled': str(scdule) or '',
                    'deadline': str(deadline) or '',
                    'demand': i.product_uom_qty or 0,
                    'reserved': res or 0,
                    'done': i.quantity_done or 0,
                    'qty': i.product_uom or 0
                }
                list.append((0, 0, data))
            else:
                for it in list:
                    if it[2]['product_id'] == i.product_id.id:
                        it[2]['demand'] += i.product_uom_qty
                        it[2]['done'] += i.quantity_done
        self.rpb_line_id = list
        self.picking_type_id = 2
        # self.picking_type_id = int(stock_picking.picking_type_id)

    def rpb_button(self):
        active_id = self.env.context.get('id_active')
        active_ids = []
        for sale_id in active_id:
            quotations = self.env['sale.order'].search([('id', '=', sale_id)])
            quotations.action_confirm()
            picking_id = self.env['stock.picking'].search([('sale_id', '=', sale_id)])
            active_ids.append(picking_id.id)

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
            b += int(self.env['product.template'].search([('id', '=', i.product_id.product_tmpl_id.id)]).volume) * int(i.done)
        for save in stock_move:
            deadline = datetime.datetime.now()
            scdule = datetime.datetime.now()
            str_date = scdule.strftime("%Y-%m-%d")

            if save.date_deadline:
                deadline = save.date_deadline
            if save.date:
                scdule = save.date

            list_rpb_view.append({
                "name": ''+str(self.name),
                "stock_picking_id": int(save.picking_id),
                "source_document_id": int(save.picking_id.sale_id),
                "product_id": int(save.product_id),
                "description": save.description_picking,
                "date_scheduled": str(str_date),
                'total_volume_product' : b,
                "deadline": str(deadline),
                "demand": save.product_uom_qty,
                "reserved": save.forecast_availability,
                "done": save.quantity_done,
                "uom": save.product_uom.id,
                "vehicle_id": self.vehicle_id.id,
                "driver_id": self.driver_id.id,
                "picking_type_id": self.picking_type_id.id,
                "state_rpb":'being_delivered',
                "origin":save.origin
            })
        rpb_list.create(list_rpb_view)
        jumlah_barang = self.rpb_line_id
        a = 0
        for i in jumlah_barang:
            a += int(self.env['product.template'].search([('id', '=', i.product_id.product_tmpl_id.id)]).volume) * int(
                i.demand)
        
        print('aowkowakowakwaokwao')
        print(a)
        list = []
        for j in stock_move:
            if not any(item[2]['product_id'] == j.product_id.id for item in list):
                deadline = datetime.datetime.now()
                scdule = datetime.datetime.now()
                if j.date_deadline:
                    deadline = j.date_deadline
                if j.date:
                    scdule = j.date
                res = 'Available'
                if j.forecast_availability < 1:
                    res = 'Not Available'
                list.append((0, 0, {
                    'name': str(j.name),
                    'product_id': int(j.product_id),
                    'description': str(j.description_picking),
                    'date_scheduled': str(scdule) ,
                    'deadline': str(deadline),
                    'demand': j.product_uom_qty,
                    'reserved': j.forecast_availability,
                    'done': j.quantity_done,
                    'qty': int(j.product_uom)
                }))
            else:
                for it in list:
                    if it[2]['product_id'] == j.product_id.id:
                        it[2]['demand'] += j.product_uom_qty
                        it[2]['done'] += j.quantity_done
            
            # rpb_line.create(data_line)
        for value in active_ids:
            stock_pick = self.env['stock.picking'].search([('id', '=', value)])
            stock_pick.write({
                'state': 'rpb'
            })
        data = {
            'name': ''+str(self.name),
            'stock_picking_id': self.stock_picking_id,
            'sale_id': self.sale_id,
            'vehicle_id': self.vehicle_id.id,
            'driver_id': self.driver_id.id,
            'total_volume_product': a,
            'delivery_date': self.delivery_date,
            'picking_type_id': self.picking_type_id.id,
            'rpb_line_ids': list
        }
        interval = self.env['count.wizard'].search([], order='id asc', limit=1)
        count = int(interval.id_interval) + 1
        interval.write({
            'id_interval': count
        })
        rpb.create(data)



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
    lack_qty = fields.Float('Kekurangan', compute='_compute_lack_qty', store=True)

    @api.depends('demand', 'done')
    def _compute_lack_qty(self):
        for record in self:
            record.lack_qty = record.demand - record.done

    @api.depends('demand', 'done')
    def _compute_date(self):
        for record in self:
            record.date_scheduled = record.rpb_id.delivery_date


class employeeOrker(models.TransientModel):
    _name = 'employee.wizard'

    employee_id = fields.Many2one('hr.employee')
    worked_hours = fields.Float(string="Work Hours", store="true")
    rpb_id = fields.Many2one('wizard.rpb')

class Count(models.TransientModel):
    _name = 'count.wizard'

    id_interval = fields.Integer()
