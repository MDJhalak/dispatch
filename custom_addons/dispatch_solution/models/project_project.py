
# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProjectExt(models.Model):
    _inherit = "project.project"

    fee_ids = fields.One2many(
        comodel_name='project.fees.schedule', inverse_name='project_id',
        string='Fees & Schedule')
    amount_total = fields.Float(string='Total Fees', compute='_compute_total', store=True)

    @api.depends('fee_ids')
    def _compute_total(self):
        for rec in self:
            rec.amount_total = sum(rec.fee_ids.mapped("amount_subtotal"))


class ProjectFeesSchedule(models.Model):
    _name = "project.fees.schedule"
    _description = "Task Material Used"

    @api.depends('unit_price', 'quantity')
    def _compute_subtotal(self):
        for rec in self:
            rec.amount_subtotal = rec.unit_price * rec.quantity

    project_id = fields.Many2one(
        comodel_name='project.project', string='Project', ondelete='cascade',
        required=True)
    product_id = fields.Many2one(
        comodel_name='product.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity')
    unit_price = fields.Float(string='Fee')
    amount_subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)

    @api.onchange('product_id')
    def on_product_change(self):
        self.unit_price = self.product_id.list_price
