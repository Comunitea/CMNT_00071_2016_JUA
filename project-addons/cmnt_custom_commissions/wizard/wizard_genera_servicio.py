# -*- coding: utf-8 -*-
# © 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>)
# © 2015 Pedro M. Baeza (<http://www.serviciosbaeza.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api, _
import time
from datetime import date, timedelta


class acp_contrato_genera_servicio(models.TransientModel):
    _inherit = "acp_contrato.genera_servicio"

    @api.multi
    def _get_inv_line_values(self, fact_lin, line_name, res, factprog):
        res_vals = super(acp_contrato_genera_servicio, self).\
            _get_inv_line_values(fact_lin, line_name, res, factprog)

        partner_id =  factprog.get('cliente_direccion_id', False)
        product_id =  res_vals.get('product_id', False)

        if partner_id and product_id:
            plan_obj = self.env['commission.plan']
            agent_list = []
            partner = self.env["res.partner"].browse(partner_id)
            origin_id = partner.origen_cliente_id.id or False

            plan_line = plan_obj.get_line(product_id, origin_id)
            if plan_line:
                agent_list.append({'agent': plan_line.agent_id.id,
                                  'commission': plan_line.commission.id})
                res_vals.update({'agents': [(0, 0, x) for x in agent_list]})
        # res.update({})
        return res_vals
