# -*- coding: utf-8 -*-
# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def _default_agents(self):
        super(SaleOrderLine, self)._default_agents()
        agents = []
        # Dependemos del producto así que no ponemos agentes
        return [(0, 0, x) for x in agents]

    @api.depends('price_subtotal', 'exempt_price')
    def _compute_base_commisison(self):
        for line in self:
            line.commission_base = line.price_subtotal - line.exempt_price

    agents = fields.One2many(default=_default_agents)
    exempt_price = fields.Float('Exempt Commisison')
    commission_base = fields.Float("Base Commission",
                                   compute="_compute_base_commisison")

    @api.multi
    def product_id_change(self, pricelist, product, qty=0,
                          uom=False, qty_uos=0, uos=False, name='',
                          partner_id=False, lang=False, update_tax=True,
                          date_order=False, packaging=False,
                          fiscal_position=False, flag=False):

        res = super(SaleOrderLine, self).product_id_change(
            pricelist, product, qty=qty, uom=uom, qty_uos=qty_uos, uos=uos,
            name=name, partner_id=partner_id, lang=lang, update_tax=update_tax,
            date_order=date_order, packaging=packaging,
            fiscal_position=fiscal_position, flag=flag)
        plan_obj = self.env['commission.plan']
        if partner_id and product:
            agent_list = []
            partner = self.env["res.partner"].browse(partner_id)
            origin_id = partner.origen_cliente_id.id or False

            plan_line = plan_obj.get_line(product, origin_id)
            if plan_line:
                agent_list.append({'agent': plan_line.agent_id.id,
                                  'commission': plan_line.commission.id})
                res['value']['agents'] = [(0, 0, x) for x in agent_list]
        return res

    @api.model
    def _prepare_order_line_invoice_line(self, line, account_id=False):
        vals = super(SaleOrderLine, self)._prepare_order_line_invoice_line(
            line, account_id=account_id)
        vals['exempt_price'] = line.exempt_price
        return vals


class SaleOrderLineAgent(models.Model):
    _inherit = "sale.order.line.agent"

    @api.depends('sale_line.price_subtotal', 'sale_line.exempt_price')
    def _compute_amount(self):
        """
        Repetimos el cálculo de la comisión en el agente descontando el campo
        exento de comisión
        """
        super(SaleOrderLineAgent, self)._compute_amount()
        for line in self:
            line.amount = 0.0
            if (not line.sale_line.product_id.commission_free and
                    line.commission):
                l = line.sale_line
                subtotal = l.tax_id.compute_all(
                    (l.price_unit * (1 - (l.discount or 0.0) / 100.0)),
                    l.product_uom_qty, l.product_id, l.order_id.partner_id)

                if line.commission.amount_base_type == 'net_amount':
                    subtotal = subtotal['total']

                else:
                    subtotal = subtotal['total_included']

                # Modifico el subtotal sobre el que calcular comisiones
                subtotal -= l.exempt_price

                if line.commission.commission_type == 'fixed':
                    line.amount = subtotal * (line.commission.fix_qty / 100.0)
                else:
                    line.amount = line.commission.calculate_section(subtotal)
