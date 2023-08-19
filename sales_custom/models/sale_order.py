from odoo import models, api, http, fields
from odoo.http import request


class SaleOrder(models.Model):
    _inherit = 'sale.order'


