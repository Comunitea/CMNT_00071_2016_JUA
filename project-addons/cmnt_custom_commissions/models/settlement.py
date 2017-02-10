# -*- coding: utf-8 -*-
# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


class Settlement(models.Model):
    _inherit = "sale.commission.settlement"

    hour_lines = fields.One2many('hour.settlement.line', 'settlement',
                                 string="Settlement hour lines")
    total = fields.Float(compute="_compute_total", readonly=True, store=True)

    @api.depends('lines', 'lines.settled_amount',
                 'hour_lines', 'hour_lines.amount')
    def _compute_total(self):
        super(Settlement, self)._compute_total()
        for record in self:
            record.total = sum(x.settled_amount for x in record.lines) + \
                sum(x.amount for x in record.hour_lines)


class HourSettlementLine(models.TransientModel):
    _name = "hour.settlement.line"

    settlement = fields.Many2one("sale.commission.settlement", 'Settlement',
                                 readonly=True, ondelete="cascade",
                                 required=True)
    company_id = fields.Many2one('res.company', 'Company',
                                 related='settlement.company_id')

    task_id = fields.Many2one('acp_contrato.tarea', 'Task', readonly=True)
    hours = fields.Float('Hours', readonly=True)
    price_hour = fields.Float('Price hour', related='task_id.price_hour',
                              readonly=True)
    commission = fields.Many2one('sale.commission', 'Commission',
                                 readonly=True, related='task_id.commission')
    amount = fields.Float('Settled Amount')
