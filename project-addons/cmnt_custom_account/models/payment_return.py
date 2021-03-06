# -*- coding: utf-8 -*-
# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class PaymentReturn(models.Model):

    _inherit = 'payment.return'

    invoice_ids = fields.One2many('account.invoice', 'return_id', 'Invoices')
    invoices_count = fields.Integer(compute='_get_invoices_count')

    @api.multi
    def _get_invoices_count(self):
        for payment_return in self:
            payment_return.invoices_count = len(payment_return.invoice_ids)

    @api.multi
    def action_view_invoices(self):
        action = self.env.ref('account.action_invoice_tree2').read()
        action = action[0]
        domain = eval(action['domain'])
        domain += [('id', 'in', self.invoice_ids.ids)]
        action['domain'] = str(domain)
        return action

    # @api.multi
    # def action_confirm(self):
    #     res = super(PaymentReturn, self).action_confirm()
    #     ref = 'cmnt_custom_account.cmnt_notificacion_devolucion_bancaria'
    #     return_template = self.env.ref(ref)

    #     ccc = '???'
    #     ref_sepa = 'account_banking_sepa_direct_debit.export_sdd_008_001_02'
    #     sepa_export = self.env.ref(ref_sepa)
    #     domain = [
    #         ('journal', '=', self.journal_id.id),
    #         ('payment_order_type', '=', 'debit'),
    #         ('type', '=', sepa_export.id),
    #     ]
    #     payment_mode = self.env['payment.mode'].search(domain, limit=1)
    #     if payment_mode and payment_mode.bank_id:
    #         ccc = payment_mode.bank_id.acc_number
    #     for return_line in self.line_ids:
    #         if return_line.partner_id:
    #             ctx = {}
    #             ctx.update({
    #                 'amount': return_line.amount,
    #                 'ccc': ccc,
    #                 'company': self.company_id
    #             })
    #             return_template.with_context(ctx).\
    #                 send_mail(return_line.partner_id.id)
    #     return res
