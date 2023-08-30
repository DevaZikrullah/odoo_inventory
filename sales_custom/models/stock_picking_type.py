from odoo import models, fields, api


class StockInh(models.Model):
    _inherit = 'stock.picking.type'

    # code = fields.Selection(selection_add=[('onloading', 'On Loading')],
    #                         ondelete={'onloading': 'set default'})


