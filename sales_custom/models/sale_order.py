from odoo import models, api, http, fields
from odoo.http import request
from odoo.exceptions import UserError, AccessError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    item_accurate_id = fields.Char('Accurate ID')
    accurate_status = fields.Char()
    customer = fields.Char()
    no_accurate = fields.Char()
    accurate_address = fields.Char()
    has_been_invoiced = fields.Char()
    salesman = fields.Char()
    rute = fields.Char()

    def create_rpb(self):
        active_ids = self.env.context.get('active_ids', [])
        sale_id = []
        for record in active_ids:
            quotations = self.env['sale.order'].search([('id', '=', record)])
            if quotations.state != 'draft':
                raise UserError("status harus Quotations")
            sale_id.append(quotations.id)

        # for dt in sale_id:
        #     picking_id = self.env['stock.picking'].search([('sale_id', '=', dt)])
        #
        #     for i in picking_id:
        #
        #         if i.state in ['draft', 'waiting', 'done', 'cancel']:
        #             raise UserError('Status Harus Siap Atau Menunggu!')
        #
        #
        #         stock = self.env['stock.picking'].search([('id', '=', i.id)])
        #
        #         excep = self.env['rpb.rpb.view'].search([('origin', '=', stock.origin)])
        #
        #         if excep:
        #             raise UserError('RPB sudah dibuat')

        # Issue 4: Use 'return' to open a new form view
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create RPB',
            'res_model': 'wizard.rpb',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'id_active': active_ids
            }
        }
