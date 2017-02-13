# -*- coding: utf-8 -*-
# © 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>)
# © 2015 Pedro M. Baeza (<http://www.serviciosbaeza.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api, _
import time
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


class SaleCommissionMakeSettle(models.TransientModel):
    _inherit = "sale.commission.make.settle"

    @api.multi
    def action_settle(self):
        """
        Sobrescribimos la función para poder agrupar en una liquidación,
        todas las lineas de liquidación del agente.
        """
        self.ensure_one()
        agent_line_obj = self.env['account.invoice.line.agent']
        settlement_obj = self.env['sale.commission.settlement']
        settlement_line_obj = self.env['sale.commission.settlement.line']

        t_h_obj = self.env['acp_contrato.tarea_horas']
        settlement_obj = self.env['sale.commission.settlement']
        hour_settlement_line_obj = self.env['hour.settlement.line']
        settlement_ids = []
        if not self.agents:
            self.agents = self.env['res.partner'].search(
                [('agent', '=', True)])
        date_to = fields.Date.from_string(self.date_to)
        for agent in self.agents:
            date_to_agent = self._get_period_start(agent, date_to)
            # Get non settled invoices
            agent_lines = agent_line_obj.search(
                [('invoice_date', '<', date_to_agent),
                 ('agent', '=', agent.id),
                 ('settled', '=', False)], order='invoice_date')
            for company in agent_lines.mapped('invoice_line.company_id'):
                agent_lines_company = agent_lines.filtered(
                    lambda r: r.invoice_line.company_id == company)
                if agent_lines_company:
                    pos = 0
                    sett_to = fields.Date.to_string(date(year=1900,
                                                         month=1,
                                                         day=1))
                    while pos < len(agent_lines_company):
                        if (agent.commission.invoice_state == 'paid' and
                                agent_lines_company[pos].invoice.state !=
                                'paid'):
                            pos += 1
                            continue
                        if agent_lines_company[pos].invoice_date > sett_to:
                            sett_from = self._get_period_start(
                                agent,
                                agent_lines_company[pos].invoice_date)
                            sett_to = fields.Date.to_string(
                                self._get_next_period_date(agent,
                                                           sett_from) -
                                timedelta(days=1))
                            sett_from = fields.Date.to_string(sett_from)
                            settlement = settlement_obj.create(
                                {'agent': agent.id,
                                 'date_from': sett_from,
                                 'date_to': sett_to,
                                 'company_id': company.id})
                            settlement_ids.append(settlement.id)
                        settlement_line_obj.create(
                            {'settlement': settlement.id,
                             'agent_line': [(6, 0,
                                             [agent_lines_company[pos].id])
                                            ]})
                        pos += 1

                # Obtener tareas donde esté asignado el agente
                date_to_agent = self._get_period_start(agent, date_to)
                domain = [
                    ('tarea_id.agent_id', '=', agent.id),
                    ('tarea_id.company_id', '=', company.id),
                    ('tarea_id.contrato_id.state', '=', 'confirmed'),
                    ('fecha', '<=', date_to_agent),
                    ('settled', '=', False)
                ]
                task_hours_objs = t_h_obj.search(domain)

                if not task_hours_objs:
                    continue
                # Agrupamos las horas totales por tarea
                hours_by_task = {}
                for th in task_hours_objs:
                    if th.tarea_id not in hours_by_task:
                        hours_by_task[th.tarea_id] = 0.0
                    hours_by_task[th.tarea_id] += th.horas

                # Creamos una linea de liquidación por las horas de cada tarea
                for task in hours_by_task:
                    hours = hours_by_task[task]
                    amount = \
                        hours * task.price_hour * (task.commission.fix_qty / 100.0)
                    vals = {
                        'settlement': settlement.id,
                        'task_id': task.id,
                        'hours': hours_by_task[task],
                        'amount': amount
                    }
                    hour_settlement_line_obj.create(vals)
                # Marcamos las horas como liquidadas
                task_hours_objs.write({'settled': True})

        # go to results
        if len(settlement_ids):
            res = {
                'name': _('Created Settlements'),
                'type': 'ir.actions.act_window',
                'views': [[False, 'list'], [False, 'form']],
                'res_model': 'sale.commission.settlement',
                'domain': [['id', 'in', settlement_ids]],
            }

        else:
            res = {'type': 'ir.actions.act_window_close'}
        return res

