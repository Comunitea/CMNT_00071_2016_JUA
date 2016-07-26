# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api


class account_invocice(models.Model):
    _inherit = "account.invoice"
    
    @api.one
    @api.depends('origin_invoices_ids')
    def _get_refund_numbers(self):
        number = ''
        inv_numbers = [x.number for x in self.origin_invoices_ids]
        self.refunded_numbers = ','.join(inv_numbers)

    refunded_numbers = fields.Char('Refund invoices',
                                  compute=_get_refund_numbers,
                                  store=True)
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
