from odoo import models, api, http, fields
from ..controllers import main
from odoo.http import request, _logger


class prbModelsClass(models.Model):
    _name = 'rpb.rpb'

    name = fields.Char()
    stock_picking_id = fields.Many2many('stock.picking')
    sale_id = fields.Many2many('sale.order')
    vehicle_id = fields.Many2one('fleet.vehicle')
    driver_id = fields.Many2one('res.partner')
    total_volume_product = fields.Integer()
    delivery_date = fields.Date()
    picking_type_id = fields.Many2one('stock.picking.type')
    rpb_line_ids = fields.One2many('rpb.line', 'rpb_id')
    state_rpb = fields.Selection([
        ('draft', 'Draft'),
        ('post', 'Post')
    ], default="draft")

    
    def write(self, vals):
        rpb_view = self.env['rpb.rpb.view'].search([('name', '=', self.name)])
        if 'driver_id' in vals:
            rpb_view.write({'driver_id': vals.get('driver_id')})
        elif 'vehicle_id' in vals:
            rpb_view.write({'vehicle_id': vals.get('vehicle_id')})
        return super(prbModelsClass, self).write(vals)
    
    def custom_report_download_rpb(self):
        report = main.CustomReportController()
        for line in self:
            record_id = [('id', int(line.id))]
            report.custom_report_download(record_id)
    
    def cek_qty(self):
        line_now = self.env['rpb.line'].search([('rpb_id', '=', self.id)])
        line_now.unlink()
        stock_move = self.env['stock.move'].search([('picking_id', 'in', self.stock_picking_id.ids)])
        # print(stock_move)
        # exit()
        list = []
        for j in stock_move:
            if not any(item['product_id'] == j.product_id.id for item in list):
                list.append({
                    'rpb_id': self.id,
                    'name': str(j.name),
                    'product_id': int(j.product_id),
                    'description': str(j.description_picking),
                    'date_scheduled': str(j.date),
                    'deadline': str(j.date_deadline),
                    'demand': j.product_uom_qty,
                    'reserved': j.forecast_availability,
                    'done': j.quantity_done,
                    'qty': int(j.product_uom)
                })
            else:
                for it in list:
                    if it[2]['product_id'] == j.product_id.id:
                        it[2]['demand'] += j.product_uom_qty
                        it[2]['done'] += j.quantity_done
        self.env['rpb.line'].create(list)


class rpbLineModels(models.Model):
    _name = 'rpb.line'

    name = fields.Char()
    product_id = fields.Many2one('product.product')
    description = fields.Text()
    date_scheduled = fields.Date()
    deadline = fields.Date()
    demand = fields.Float()
    reserved = fields.Float()
    done = fields.Float()
    qty = fields.Many2one('uom.uom', string="Uom")
    rpb_id = fields.Many2one('rpb.rpb')


class rpbModelView(models.Model):
    _name = 'rpb.rpb.view'

    name = fields.Char()
    stock_picking_id = fields.Many2one('stock.picking')
    source_document_id = fields.Many2one('sale.order')
    product_id = fields.Many2one('product.product')
    description = fields.Text()
    date_scheduled = fields.Date()
    total_volume_product = fields.Integer()
    deadline = fields.Date()
    demand = fields.Float(compute='_compute_demand', store=True)
    reserved = fields.Float(compute='_compute_demand',store=True)
    done = fields.Float(compute='_compute_demand',store=True)
    uom = fields.Many2one('uom.uom', string="Uom")
    vehicle_id = fields.Many2one('fleet.vehicle')
    driver_id = fields.Many2one('res.partner')
    picking_type_id = fields.Many2one('stock.picking.type')
    state_rpb = fields.Selection([
        ('being_delivered', 'Sedang Terkirim'),
        ('pending', 'Pending'),
        ('already_sent', 'Sudah Terkirim'),
    ], default="being_delivered")
    move_id = fields.Many2one('stock.move')

    def state_progress_failed_to_send(self):
        active_ids = self.env.context.get('active_ids', [])
        for value in active_ids:
            # print(value)
            self.env['rpb.rpb.view'].search([('id', '=', value)]).write({
                'state_rpb': 'pending'
            })

    def state_progress_already_sent(self):
        active_ids = self.env.context.get('active_ids', [])
        for value in active_ids:
            # print(value)
            self.env['rpb.rpb.view'].search([('id', '=', value)]).write({
                'state_rpb': 'already_sent'
            })
    def _compute_demand(self):
        for line in self:
            picking = self.env['stock.move'].search([('id', '=', line.move_id.id)])
            # set = picking.search([('product_id','=',self.product_id.id)])
            line.demand = picking.product_uom_qty
            line.reserved = picking.forecast_availability
            line.done = picking.quantity_done

    
    
    def move_update(self):
        pass
        # print('hasil tidak ada')
        # data = self.env['rpb.rpb.view'].search([])
        # for i in data:
        #     stok_move = self.env['stock.move'].search([('picking_id','=',int(i.stock_picking_id.id)),('product_id','=',int(i.product_id.id)),('product_uom_qty','=',i.demand)])
        #     print('UPDATE rpb_rpb_view SET move_id = '+str(stok_move.id)+' WHERE id = '+str(i.id)+';')
        
