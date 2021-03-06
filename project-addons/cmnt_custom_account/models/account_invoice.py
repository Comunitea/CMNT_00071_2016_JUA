# -*- coding: utf-8 -*-
# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api, _
from openerp.exceptions import except_orm


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    payment_term = fields.Many2one(required=True, readonly=False)
    payment_mode_id = fields.Many2one(required=True)

    @api.multi
    def action_move_create(self):
        sepa_ref = 'account_banking_sepa_direct_debit.export_sdd_008_001_02'
        export_type = self.env.ref(sepa_ref)
        for inv in self:
            pay_mode = inv.payment_mode_id
            if pay_mode and pay_mode.type.id == export_type.id \
                    and not inv.mandate_id and inv.type == 'out_invoice':
                err = _('You selected a payment mode thar requires a direct'
                        ' debit mandate for this customer')
                raise except_orm(_('Error!'), err)
        return super(AccountInvoice, self).action_move_create()

    def action_number(self, cr, uid, ids, context=None):
        res = super(AccountInvoice, self).action_number(cr, uid, ids, context)
        for invoice in self.browse(cr, uid, ids, context):
            if invoice.move_id:
                new_ref = invoice.supplier_invoice_number or invoice.number
                invoice.move_id.write({'ref': new_ref})
                for l in invoice.move_id.line_id:
                    l.write({'ref': new_ref})
        return res
