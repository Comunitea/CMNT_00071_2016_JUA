# -*- coding: utf-8 -*-
# © 2016 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    payment_term = fields.Many2one(required=True)
    payment_mode_id = fields.Many2one(required=True)
