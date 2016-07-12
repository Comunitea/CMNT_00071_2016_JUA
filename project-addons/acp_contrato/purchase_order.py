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
# Purchase Order
#----------------------------------------------------------
class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    
    _columns = {
        'dft_contrato_id': fields.many2one('acp_contrato.contrato', 'Contrato', readonly=False,required=False),        	
        'dft_servicio_id': fields.many2one('acp_contrato.servicio', 'Servicio', readonly=False,required=False),        	
        
              }     
  
purchase_order()
class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'
    
    _columns = {
        'contrato_id': fields.many2one('acp_contrato.contrato', 'Contrato', readonly=False,required=False),        	
        'servicio_id': fields.many2one('acp_contrato.servicio', 'Servicio', readonly=False,required=False),        	
        'partner_ref': fields.related('order_id', 'partner_ref', string="Referencia", type='char', size=64, store=False),	
        
              }     
    _defaults = {
      'contrato_id' : lambda self, cr, uid, context : context['contrato_id'] if context and 'contrato_id' in context else None,
      'servicio_id' : lambda self, cr, uid, context : context['servicio_id'] if context and 'servicio_id' in context else None      	
   }  
    def open_po(self,cr,uid,ids,context=None):
       
        if context is None:
            context = {}
        order_id = self.browse(cr, uid, ids, context=context)[0].order_id.id    
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pedido de Compra',
            'view_type': 'form',
            'view_mode': 'form',
            'context': context,
            'res_model': 'purchase.order',
            'nodestroy': True,
            'res_id': order_id,	
            'target':'current',	
            }  
purchase_order_line()

#----------------------------------------------------------
# Sale Order
#----------------------------------------------------------
class purchase_order(osv.osv):
    _inherit = 'purchase.order'

    def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):

        res = {}
        res = super(purchase_order, self)._prepare_inv_line( cr, uid, account_id, order_line, context=context)
        res['servicio_id'] = order_line.servicio_id and order_line.servicio_id.id or False
        res['contrato_id'] = order_line.contrato_id and order_line.contrato_id.id or False
        return res
 
purchase_order()



 





# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
