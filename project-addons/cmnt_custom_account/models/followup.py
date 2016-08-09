# -*- coding: utf-8 -*-
# © 2016 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, exceptions, _


class AccountFollowupFollowup(models.Model):

    _inherit = 'account_followup.followup'

    @api.model
    def launch_print(self):
        for followup in self.search([]):
            self.env['account_followup.print'].with_context(
                active_model='account_followup.followup',
                active_id=followup.id).create({}).do_process()
