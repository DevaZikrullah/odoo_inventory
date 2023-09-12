from odoo import models, fields, api


class StockInhTyp(models.Model):
    _inherit = 'stock.picking.type'

    code = fields.Selection([
        ('incoming', 'Receipt'),
        ('outgoing', 'Delivery'),
        ('internal', 'Internal Transfer'),
        ('rpb', 'RPB')],
        string='Type of Operation',
        ondelete='cascade'  # Use 'cascade' as the ondelete policy
    )




