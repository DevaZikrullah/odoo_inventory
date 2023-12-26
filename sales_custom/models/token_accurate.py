from odoo import models, api, http, fields


class TokenAccurate(models.Model):
    _name = 'token.accurate'

    name = fields.Char()