# -*- coding: utf-8 -*-
# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api, _


class CommissionPlan(models.Model):

    _name = 'commission.plan'
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product', 'Product', required=True)
    lines = fields.One2many('commission.plan.line', 'plan_id')
    exp = fields.Boolean('Apply in expedient')

    _sql_constraints = [(
        'plan_product_unique', 'unique(product_id)',
        _('Ya tienes un plan de comisiones definido para este producto'))
    ]

    @api.model
    def get_line(self, product_id, origin_id, exp=False, agent_id=False):
        lines = False
        domain = [('product_id', '=', product_id), ('exp', '=', exp)]
        plan_obj = self.search(domain, limit=1)
        if plan_obj and plan_obj.lines:
            if origin_id:
                lines = plan_obj.lines.filtered(
                    lambda l: l.origin_id.id == origin_id)
            else:
                lines = plan_obj.lines.filtered(
                    lambda l: l.origin_id.id is False)

            if lines and agent_id:
                lines = lines.filtered(
                    lambda l: l.agent_id.id == agent_id)
        return lines and lines[0] or False


class SaleAgentPlanLine(models.Model):

    _name = 'commission.plan.line'

    plan_id = fields.Many2one('commission.plan', 'Commission Plan')
    agent_id = fields.Many2one('res.partner', 'Agent', required=True)
    origin_id = fields.Many2one('acp_yanez.origen_cliente', 'Customer Origin')
    commission = fields.Many2one('sale.commission', 'Commission',
                                 required=True)
