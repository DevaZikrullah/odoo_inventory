from odoo import models, api, http, fields


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
    demand = fields.Float()
    reserved = fields.Float()
    done = fields.Float()
    uom = fields.Many2one('uom.uom', string="Uom")
    vehicle_id = fields.Many2one('fleet.vehicle')
    driver_id = fields.Many2one('res.partner')
    picking_type_id = fields.Many2one('stock.picking.type')
    state_rpb = fields.Selection([
        ('draft', 'Draft'),
        ('post', 'Post')
    ], default="draft")
