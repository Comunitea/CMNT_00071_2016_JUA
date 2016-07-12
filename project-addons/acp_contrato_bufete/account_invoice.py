# -*- coding: utf-8 -*-
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

#----------------------------------------------------------
# 
#----------------------------------------------------------

class account_invoice(osv.osv):
    _inherit = 'account.invoice'

    _columns = {
        'tipo_contrato_id': fields.related(
                              'dft_contrato_id',
                              'tipo_contrato',
                              type="many2one",
                              relation="acp_contrato.tipo_contrato",
                              string="Tipo expediente",
                              required=False,
                              store=False) ,   
         }
    def action_genera_factura(self,cr,uid,ids,context=None):
        ctx = dict()
        ctx.update({
            'default_invoice_id': self.browse(cr, uid, ids).id,
        })
        
        mod_obj = self.pool.get('ir.model.data')
        res = mod_obj.get_object_reference(cr, uid, 'acp_contrato_bufete', 'view_genera_factura_bu')
        res_id = res and res[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'name': 'Generar Factura Ventas',
            'view_type': 'form',
            'view_mode': 'form',
            'context': ctx,
            'res_model': 'acp_contrato.genera_factura',
            'target':'new',
            'view_id': [res_id],
            }      
account_invoice()


 





# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
