# -*- coding: utf-8 -*-
# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


class Tarea(models.Model):

    _inherit = 'acp_contrato.tarea'

    commission = fields.Many2one('sale.commission', 'Commission')
    agent_id = fields.Many2one('res.partner', string="Agent",
                               domain=[('agent', '=', True)])
    price_hour = fields.Float('Price Hour')

    @api.multi
    def _get_expedient_products(self):
        """
        Busco productos asociado a la facturación automática en el expediente
        padre si lo hay, y devuelvo un diccionario con sus productos y sus
        precios
        """
        self.ensure_one()
        res = {}
        # Solo busco roductos del expediente padre
        if self.contrato_id.parent_id and \
                self.contrato_id.parent_id.facturacion_lineas:
            for fl in self.contrato_id.parent_id.facturacion_lineas:
                for c in fl.conceptos_lineas:
                    res[c.product_id.id] = c.importe
        return res

    @api.model
    def create(self, vals):
        """
        Al crear la tarea asigno agente y comisión correspondiente
        """
        tarea = super(Tarea, self).create(vals)
        plan_obj = self.env['commission.plan']
        agent = line = False
        price_hour = 0.0
        if tarea.tipo_servicio.name == 'Actuaciones Profesionales':
            if tarea.user_seg_id.partner_id.agent:
                # Asigno el agente
                agent = tarea.user_seg_id.partner_id
                product_prices_dic = tarea._get_expedient_products()
                orig_id = tarea.partner_id.origen_cliente_id.id or False

                # Busco el primer producto que esté en e plan, y devuelvo
                # la comisión en función del origen
                for product_id in product_prices_dic:
                    line = plan_obj.get_line(product_id, orig_id, agent.id)
                    # Si el primero de los productos está en el plan para
                    if line:
                        price_hour = product_prices_dic[product_id]
                        break

        if agent and line:
            tarea.write({'commission': line.commission.id,
                         'agent_id': agent.id,
                         'price_hour': price_hour})
        return tarea


class TareaHoras(models.Model):

    _inherit = 'acp_contrato.tarea_horas'

    settled = fields.Boolean('Settled', readonly=True)
