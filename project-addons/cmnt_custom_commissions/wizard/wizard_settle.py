# -*- coding: utf-8 -*-
# © 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>)
# © 2015 Pedro M. Baeza (<http://www.serviciosbaeza.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api, _
import time


class SaleCommissionMakeSettle(models.TransientModel):
    _inherit = "sale.commission.make.settle"

    @api.multi
    def action_settle(self):
        res = super(SaleCommissionMakeSettle, self).action_settle()

        t_h_obj = self.env['acp_contrato.tarea_horas']
        settlement_obj = self.env['sale.commission.settlement']
        hour_settlement_line_obj = self.env['hour.settlement.line']
        settlement_ids = []

        company = self.env['res.users'].browse(self._uid).company_id
        if not self.agents:
            self.agents = self.env['res.partner'].search(
                [('agent', '=', True)])
        date_to = fields.Date.from_string(self.date_to)
        for agent in self.agents:
            date_to_agent = self._get_period_start(agent, date_to)
            # Obtener tareas donde esté asignado el agente
            domain = [
                ('tarea_id.agent_id', '=', agent.id),
                ('tarea_id.company_id', '=', company.id),
                ('tarea_id.contrato_id.state', '=', 'confirmed'),
                ('fecha', '<=', date_to_agent),
                ('settled', '=', False)
            ]
            task_hours_objs = t_h_obj.search(domain)

            if not task_hours_objs:
                return res
            # Agrupamos las horas totales por tarea
            hours_by_task = {}
            for th in task_hours_objs:
                if th.tarea_id not in hours_by_task:
                    hours_by_task[th.tarea_id] = 0.0
                hours_by_task[th.tarea_id] += th.horas

            # Buscamos una liquidación ya creada para meter las lineas
            settlement = False
            if res.get('domain', False):
                settlement_ids = res['domain'][0][2]
                domain = [('agent', '=', agent.id),
                          ('id', 'in', settlement_ids)]
                settlement = settlement_obj.search(domain, limit=1)

            # Creamos la liquidación para el agente si no había otra creada
            if not settlement:
                vals = {
                    'agent': agent.id,
                    'date_from': time.strftime("%Y-%m-%d"),
                    'date_to': date_to_agent,
                    'company_id': company.id
                }
                settlement = settlement_obj.create(vals)
                settlement_ids.append(settlement.id)

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
        if not res.get('domain', False):
            res = {
                'name': _('Created Settlements'),
                'type': 'ir.actions.act_window',
                'views': [[False, 'list'], [False, 'form']],
                'res_model': 'sale.commission.settlement',
                'domain': [['id', 'in', settlement_ids]],
            }
        else:
            res['domain'] = [['id', 'in', settlement_ids]]
        return res
