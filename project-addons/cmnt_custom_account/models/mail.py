# -*- coding: utf-8 -*-
# © 2016 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class MailMail(models.Model):

    _inherit = 'mail.mail'

    @api.model
    def _get_partner_access_link(self, mail, partner=None):
        if mail.model == 'payment.order':
            return False
        return super(MailMail, self)._get_partner_access_link(mail, partner)


class MailComposeMessage(models.Model):

    _inherit = 'mail.compose.message'

    @api.model
    def get_mail_values(self, wizard, res_ids):
        """
        Avoid seand mail to leads or partners marked with opt_out field.
        """
        results = super(MailComposeMessage, self).get_mail_values(wizard,
                                                                  res_ids)
        results2 = results.copy()
        for k in results2:
            if wizard.model == 'crm.lead':
                lead = self.env['crm.lead'].browse(k)
                if lead.opt_out or (lead.partner_id and
                                    lead.partner_id.opt_out):
                    del results[k]
            elif wizard.model == 'res.partner':
                partner = self.env['res.partner'].browse(k)
                if partner.opt_out:
                    del results[k]
        return results
