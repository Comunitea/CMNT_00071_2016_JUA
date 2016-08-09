# -*- coding: utf-8 -*-
# © 2016 Comunitea Servicios Tecnológicos (<http://www.comunitea.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api
from openerp.exceptions import except_orm


class RepercuteCostWzd(models.TransientModel):
    _name = 'repercute.cost.wzd'

    partner_id = fields.Many2one('res.partner', 'Cliente',
                                 readonly=True)
    invoice_id = fields.Many2one('account.invoice', 'Añadir a factura')

    @api.model
    def default_get(self, fields):
        res = super(RepercuteCostWzd, self).default_get(fields)
        active_ids = self.env.context.get('active_ids')
        if not active_ids:
            return res
        active_id = self._context['active_id']
        line = self.env['account.invoice.line'].browse(active_id)
        if line.repercuted_invoice:
            raise except_orm("Error!",
                             "La linea de gasto ya está repercutida en una "
                             "factura")
        res.update(partner_id=line.contrato_id.partner_factura_id.id)
        return res

    def _get_invoice_vals(self, line):
        company_id = line.invoice_id.company_id.id
        domain = [('type', '=', 'sale'), ('company_id', '=', company_id)]
        journal = self.env['account.journal'].search(domain)[0]
        return {
            'name': u'Repercusión ' + fields.Date.today(),
            'origin': line.name,
            'date_invoice': fields.Date.today(),
            'user_id': self._uid,
            'partner_id': self.partner_id.id,
            'account_id': self.partner_id.property_account_receivable.id,
            'payment_term': self.partner_id.property_payment_term.id or False,
            'type': 'out_invoice',
            'fiscal_position': self.partner_id.property_account_position.id,
            'company_id': company_id,
            'currency_id': line.invoice_id.currency_id.id,
            'journal_id': journal.id,
            'dft_contrato_id': line.contrato_id.id or False
        }

    @api.multi
    def repercute_cost_line(self):
        active_id = self._context['active_id']
        line = self.env['account.invoice.line'].browse(active_id)
        invoice = self.invoice_id
        if not invoice:
            vals = self._get_invoice_vals(line)
            invoice = self.env['account.invoice'].create(vals)
        line.copy(default={'invoice_id': invoice.id})
        line.repercuted_invoice = invoice.id
        view = self.env.ref('account.invoice_form')
        view_id = view and view.id or False,
        return {
            'type': 'ir.actions.act_window',
            'name': 'Facturas de Cliente',
            'view_type': 'form',
            'view_mode': 'form',
            'context': "{'type':'out_invoice'}",
            'res_model': 'account.invoice',
            'nodestroy': True,
            'res_id': invoice.id,
            'target': 'current',
            'view_id': [view_id],
        }
