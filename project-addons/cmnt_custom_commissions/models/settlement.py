# -*- coding: utf-8 -*-
# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields


class Settlement(models.Model):
    _inherit = "sale.commission.settlement"

    hour_lines = fields.One2many('hour.settlement.line', 'settlement',
                                 string="Settlement hour lines")


class HourSettlementLine(models.TransientModel):
    _name = "hour.settlement.line"

    settlement = fields.Many2one("sale.commission.settlement",
                                 readonly=True, ondelete="cascade",
                                 required=True)
    amount = fields.Float('Amount')
