# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv

from datetime import datetime
#import netsvc
import time
from openerp.tools.translate import _


class res_users(osv.osv):
    _inherit = 'res.users'

    _columns = {
        'contrato_ids': fields.many2many('acp_contrato.contrato', 'acp_contrato_res_users_rel', string='Contratos', ondelete="restrict", copy=False),



     }







# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
