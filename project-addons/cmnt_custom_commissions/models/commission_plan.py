# -*- coding: utf-8 -*-
# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


class CommissionPlan(models.Model):

    _name = 'commission.plan'

    name = fields.Char(required=True)
    lines = fields.One2many('commission.plan.line', 'plan_id')

    @api.model
    def get_product_commission(self, product_id, origin_id=False,
                               exp=False):
        res = False
        # Busco lineas para el producto dado
        lines = self.lines.filtered(
            lambda l: l.product_id.id == product_id and
            l.expedient == exp)
        if not lines:
            return False

        # De las anteriores busco lineas con el origen o sin el, si no tiene
        if origin_id:
            lines = lines.filtered(lambda l: l.origin_id.id == origin_id)
        else:
            lines = lines.filtered(lambda l: l.origin_id.id is False)

        if lines:
            res = lines[0].commission
        return res


class SaleAgentPlanLine(models.Model):

    _name = 'commission.plan.line'

    plan_id = fields.Many2one('commission.plan', 'Commission Plan')
    product_id = fields.Many2one('product.product', 'Product', required=True)
    origin_id = fields.Many2one('acp_yanez.origen_cliente', 'Customer Origin')
    commission = fields.Many2one('sale.commission', 'Commission',
                                 required=True)
    expedient = fields.Boolean('Apply to expedient')
