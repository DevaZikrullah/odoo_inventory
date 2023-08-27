from odoo import models, fields
from ..controllers import main
import requests


class transDate(models.Model):
    _name = 'trans.date.wizard'

    date_from = fields.Date()
    date_to = fields.Date()

    def update_accurate_button(self):
        formatted_date_from = self.date_from.strftime('%d/%m/%Y')
        formatted_date_to = self.date_to.strftime('%d/%m/%Y')

        accurate = main.SaleOrderController()
        accurate.get_data_accurate(formatted_date_from, formatted_date_to)
