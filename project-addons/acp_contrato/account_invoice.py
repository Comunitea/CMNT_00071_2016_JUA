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
        'dft_contrato_id': fields.many2one('acp_contrato.contrato', 'Contrato', readonly=False,required=False),         
        'dft_servicio_id': fields.many2one('acp_contrato.servicio', 'Servicio', readonly=False,required=False),
        'dft_factprog_id': fields.many2one('acp_contrato.facturacion', 'Facturacion Programada', readonly=False,required=False),            
        'return_id': fields.many2one('payment.return', 'De la devolución'),
       }
account_invoice()

class account_invoice_line(osv.osv):
    _inherit = 'account.invoice.line'
    _columns = {
        'contrato_id': fields.many2one('acp_contrato.contrato', 'Contrato', readonly=False,required=False),             
        'servicio_id': fields.many2one('acp_contrato.servicio', 'Servicio', readonly=False,required=False),
        'factprog_id': fields.many2one('acp_contrato.facturacion', 'Facturacion Programada', readonly=False,required=False), 
        #'servicio_extra_id': fields.many2one('acp_contrato.servicio_producto_extra', 'Servicio Extra', readonly=False,required=False),   
        'tarea_id': fields.many2one('acp_contrato.tarea', 'Tarea', readonly=False,required=False), 
        'tarea_producto_id': fields.many2one('acp_contrato.tarea_producto', 'Tarea Producto', readonly=False,required=False),                   
        'sale_invoice_line_id': fields.many2one('account.invoice.line', 'Linea de factura relacionada', readonly=False,required=False),             
        'sale_invoice': fields.boolean('Refacturar', readonly=False, required=False),
        'repercuted_invoice': fields.many2one('account.invoice', 'Repercutido en', readonly=True),
        'return_id': fields.related('invoice_id', 'return_id', type='many2one', relation='payment.return', string='De la devolución')
        
        
       }  

    _defaults = {
      'contrato_id' : lambda self, cr, uid, context : context['contrato_id'] if context and 'contrato_id' in context else None,
      'servicio_id' : lambda self, cr, uid, context : context['servicio_id'] if context and 'servicio_id' in context else None,
      'factprog_id' : lambda self, cr, uid, context : context['factprog_id'] if context and 'factprog_id' in context else None,
      'sale_invoice': 1
         } 
       
    def open_inv_out(self,cr,uid,ids,context=None):
        mod_obj = self.pool.get('ir.model.data')
        if context is None:
            context = {}
        invoice_id = self.browse(cr, uid, ids, context=context)[0].invoice_id.id    
        res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
        res_id = res and res[1] or False,        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Facturas de Cliente',
            'view_type': 'form',
            'view_mode': 'form',
            'context': "{'type':'out_invoice'}",
            'res_model': 'account.invoice',
            'nodestroy': True,
            'res_id': invoice_id,   
            'target':'current', 
            'view_id': [res_id],                
            }  
            
    def open_inv_in(self,cr,uid,ids,context=None):
        mod_obj = self.pool.get('ir.model.data')
        if context is None:
            context = {}
        invoice_id = self.browse(cr, uid, ids, context=context)[0].invoice_id.id    
        res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_supplier_form')
        res_id = res and res[1] or False,        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Facturas de Proveedor',
            'view_type': 'form',
            'view_mode': 'form',
            'context': "{'type':'in_invoice'}",
            'res_model': 'account.invoice',
            'nodestroy': True,
            'res_id': invoice_id,   
            'target':'current', 
            'view_id': [res_id],                
            }  
  
account_invoice_line()

 





# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
