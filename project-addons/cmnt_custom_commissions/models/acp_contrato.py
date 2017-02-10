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
        agent = commission = False
        price_hour = 0.0
        if tarea.tipo_servicio.name == 'Actuaciones Profesionales':
            if tarea.user_seg_id.partner_id.agent:
                # Asigno el agente
                agent = tarea.user_seg_id.partner_id
                product_prices_dic = tarea._get_expedient_products()
                orig = tarea.partner_id.origen_cliente_id or False

                # Busco el primer producto que esté en e plan, y devuelvc
                # la comisión en función del origen
                for product_id in product_prices_dic:
                    commission = \
                        agent.plan_id.get_product_commission(product_id,
                                                             origin_id=orig,
                                                             exp=True)
                    # Si el primero de los productos está en el plan para
                    if commission:
                        price_hour = product_prices_dic[product_id]
                        break

        if agent and commission:
            tarea.write({'commission': commission.id,
                         'agent_id': agent.id,
                         'price_hour': price_hour})
        return tarea


class TareaHoras(models.Model):

    _inherit = 'acp_contrato.tarea_horas'

    settled = fields.Boolean('Settled', readonly=True)
