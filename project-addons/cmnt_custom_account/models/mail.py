# -*- coding: utf-8 -*-
# © 2016 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, exceptions, _


class MailMail(models.Model):

    _inherit = 'mail.mail'

    @api.model
    def _get_partner_access_link(self, mail, partner=None):
        if mail.model == 'payment.order':
            return False
        return super(MailMail, self)._get_partner_access_link(mail, partner)
