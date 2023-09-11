from odoo import models, fields,api
from ..controllers import main
import requests


class transDate(models.Model):
    _name = 'trans.date.wizard'

    date_from = fields.Date()
    date_to = fields.Date(default=fields.Date.today())
    active_ids = fields.Integer('Active Id',compute='_compute_is_active_id')


    @api.depends('date_to')
    def _compute_is_active_id(self):
        for record in self:
            record.active_ids = self.env.context.get('id_active')


    def update_accurate_button(self):
        formatted_date_from = self.date_from.strftime('%d/%m/%Y')
        formatted_date_to = self.date_to.strftime('%d/%m/%Y')

        accurate = main.SaleOrderController()
        accurate.get_data_accurate(formatted_date_from, formatted_date_to)

    def update_accurate_button_po(self):
        formatted_date_from = self.date_from.strftime('%d/%m/%Y')
        formatted_date_to = self.date_to.strftime('%d/%m/%Y')

        accurate = main.SaleOrderController()
        accurate.get_po_accurate(formatted_date_from, formatted_date_to)


