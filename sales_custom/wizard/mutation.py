from odoo import models, fields


class Mutation(models.Model):
    _name = 'mutation.wizard'

    # def _get_product(self):
    #     domain = [('id', '=', -1)]
    #     employee_list = []
    #     some_model = self.env['some.model'].search([('field', '=', 'value')])
    #     for each in some_model:
    #         employee_list.append(each.employee_id.id)
    #     if employee_list:
    #         domain = [('id', 'in', employee_list)]
    #         return domain
    #     return domain

    product_target = fields.Many2one('product.template', 'Product')
    product_dest = fields.Many2one('product.template','Product Destination')
