# -*- coding: utf-8 -*-
# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


class Settlement(models.Model):
    _inherit = "sale.commission.settlement"

    hour_lines = fields.One2many('hour.settlement.line', 'settlement',
                                 string="Settlement hour lines")
    pending_line_ids = \
        fields.One2many('pending.sale.commission.settlement.line',
                        'settlement', string='Pending commission lines')
    total = fields.Float(compute="_compute_total", string="To invoice total",
                         readonly=True, store=True)
    total_pending = fields.Float(compute="_compute_total",
                                 string="Pending Total",
                                 readonly=True)
    total_and_pending = fields.Float(compute="_compute_total",
                                     string="Settlement total",
                                     readonly=True)

    @api.depends('lines', 'lines.settled_amount',
                 'hour_lines', 'hour_lines.amount',
                 'pending_line_ids', 'pending_line_ids.settled_amount')
    def _compute_total(self):
        super(Settlement, self)._compute_total()
        for record in self:
            record.total = sum(x.settled_amount for x in record.lines) + \
                sum(x.amount for x in record.hour_lines)

            record.total_pending = \
                sum(x.settled_amount for x in record.pending_line_ids)
            record.total_and_pending = record.total + record.total_pending
            record.total_and_pending = record.total + record.total_pending


class HourSettlementLine(models.Model):
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


class PendingSettlementLine(models.Model):
    _name = "pending.sale.commission.settlement.line"

    settlement = fields.Many2one(
        "sale.commission.settlement", readonly=True, ondelete="cascade",
        required=True)
    pending_agent_line = fields.Many2many(
        comodel_name='account.invoice.line.agent',
        relation='pending_settlement_pending_agent_line_rel',
        column1='settlement_id', column2='pending_pending_agent_line_id',
        copy=False)
    date = fields.Date(related="pending_agent_line.invoice_date", store=True)
    invoice_line = fields.Many2one(
        comodel_name='account.invoice.line', store=True,
        related='pending_agent_line.invoice_line')
    invoice = fields.Many2one(
        comodel_name='account.invoice', store=True, string="Invoice",
        related='invoice_line.invoice_id')
    agent = fields.Many2one(
        comodel_name="res.partner", readonly=True,
        related="pending_agent_line.agent",
        store=True)
    settled_amount = fields.Float(
        related="pending_agent_line.amount", readonly=True, store=True)
    commission = fields.Many2one(
        comodel_name="sale.commission",
        related="pending_agent_line.commission")
    company_id = fields.Many2one('res.company', 'Company',
                                 related="settlement.company_id", store=True)
