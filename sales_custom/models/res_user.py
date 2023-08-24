from odoo import models, api, http, fields


class resPartner(models.Model):
    _inherit = 'res.partner'
    #
    # customer_accurate_id = fields.Char('Accurate ID Customer')
    # customer_accurate_no = fields.Char()
