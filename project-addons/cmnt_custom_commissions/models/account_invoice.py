# -*- coding: utf-8 -*-
# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api


class AccountInvoiceLine(models.Model):

    _inherit = 'account.invoice.line'

    @api.model
    def _default_agents(self):
        super(AccountInvoiceLine, self)._default_agents()
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
    def product_id_change(
            self, product, uom_id, qty=0, name='',
            type='out_invoice', partner_id=False, fposition_id=False,
            price_unit=False, currency_id=False, company_id=None):

        res = super(AccountInvoiceLine, self).product_id_change(
            product, uom_id, qty, name, type, partner_id,
            fposition_id, price_unit, currency_id, company_id)
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


class AccountInvoiceLineAgent(models.Model):

    _inherit = 'account.invoice.line.agent'

    pending_agent_line = fields.Many2many(
        comodel_name='pending.sale.commission.settlement.line',
        relation='pending_settlement_agent_line_rel',
        column1='pending_agent_line_id', column2='settlement_id',
        copy=False)

    @api.depends('invoice_line.price_subtotal', 'invoice_line.exempt_price')
    def _compute_amount(self):
        """
        Repetimos el cálculo de la comisión en el agente descontando el campo
        exento de comisión
        """
        super(AccountInvoiceLineAgent, self)._compute_amount()
        for line in self:
            line.amount = 0.0
            if (not line.invoice_line.product_id.commission_free and
                    line.commission):
                l = line.invoice_line
                subtotal = l.invoice_line_tax_id.compute_all(
                    (l.price_unit * (1 - (l.discount or 0.0) / 100.0)),
                    l.quantity, l.product_id, line.invoice.partner_id)

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
                # Refunds commissions are negative
                if line.invoice.type in ('out_refund', 'in_refund'):
                    line.amount = -line.amount
