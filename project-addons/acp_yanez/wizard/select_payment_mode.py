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

#from mx import DateTime
#import netsvc
import time
from openerp.tools.translate import _


class acp_yanez_select_payment_mode(osv.osv_memory):
    _name = "acp_yanez.select_payment_mode"
    _description = "Selecionar Modo de Pago"
    _columns = {
        'sale_id': fields.many2one('sale.order', 'Pedido'),  
        'mode_ids': fields.one2many('acp_yanez.select_payment_mode_l','wiz_id', 'Modo de Pago'),  
    }

    
class acp_yanez_select_payment_mode_l(osv.osv_memory):
    _name = "acp_yanez.select_payment_mode_l"
    _description = "Selecionar Plazo de Pago"
    _columns = {
        'wiz_id': fields.many2one('acp_yanez.select_payment_mode', 'Pedido'),  
        'mode_id': fields.many2one('payment.mode', 'Modo de Pago'),  
    }
   
    def select(self, cr, uid, ids, context=None):
        mode_obj = self.pool.get('payment.mode')
        account_tax = self.pool.get('account.tax') 
        term_obj = self.pool.get('account.payment.term')
        line_obj = self.pool.get('sale.order.line')
        sale_obj = self.pool.get('sale.order')
        ir_obj = self.pool.get('ir.attachment')        
        desgrose_obj = self.pool.get('acp_yanez.sale_order_desglose')
        payment_transaction_obj = self.pool.get('payment.transaction')

        for wiz in self.browse(cr, uid, ids, context=context):
            order = wiz.wiz_id.sale_id
            order.write({'payment_mode_id2':wiz.mode_id.id,'payment_term2':False,'dummy_mostrar_adjuntos':False,'dummy_mostrar_desglose':False})
            #elminimamos los plazos actuales
            for desglose in order.desglose_id:
                desglose.unlink(context=context)
                
            #eliminamos las lineas de pedido ocasionadas por los plazos
            for line in order.order_line:
                if line.orign_term_id:
                    line.unlink(context=context)             
            #Si es neecsario adjuntar documentos , mostramos el boton
            if wiz.mode_id.tipo_documento:
                dummy_mostrar_adjuntos = True
                #Comprobamos por si ya están los documentos adjuntados
                if wiz.mode_id.guardar == 'cliente':
                    #buscamos en el cliente por si ya esta subido con anterioridad
                    _ids = ir_obj.search(cr, uid,[('tipo_documento','=',wiz.mode_id.tipo_documento),('res_model','=','res.partner'),('res_id','=',wiz.wiz_id.sale_id.partner_id.id)] ,context=context)
                    if len(_ids) > 0:
                        dummy_mostrar_adjuntos = False
                else:
                    #buscamos en el pedido por si ya esta subido con anterioridad o lo ha subido un administrador diretamente 
                    _ids = ir_obj.search(cr, uid,[('tipo_documento','=',wiz.mode_id.tipo_documento),('res_model','=','sale.order'),('res_id','=',wiz.wiz_id.sale_id.id)] ,context=context)
                    if len(_ids) > 0:
                        dummy_mostrar_adjuntos = False

                order.write({'dummy_mostrar_adjuntos':dummy_mostrar_adjuntos})
            #Si el modo de pago solo tiene una forma de pago...la ponemos directamente
            if len(wiz.mode_id.terms_ids) == 1:
                
                order.write({'payment_term2':wiz.mode_id.terms_ids[0].id})
                #volvemos a crear la lineas de pedido
                term = term_obj.browse(cr, uid,wiz.mode_id.terms_ids[0].id,context=context)
                fiscal_position_id = order.partner_id.property_account_position and order.partner_id.property_account_position.id or False 
                prodduct_added= False
                for pt_product in term.payment_term_product_ids:
                    prodduct_added= True
                    total = order.amount_untaxed
                    taxes = account_tax.browse(cr, uid, map(lambda x: x.id, pt_product.product_id.taxes_id))
                    fpos = fiscal_position_id and account_fiscal_position.browse(cr, uid, fiscal_position_id, context=context) or False
                    taxes_ids = account_fiscal_position.map_tax(cr, uid, fpos, taxes)
                    if pt_product.tipo == 'porcentaje':
                        price = total * (pt_product.valor/100)
                    if pt_product.tipo == 'fijo':             
                        continue
                    line_obj.create(cr, uid,{
                        'order_id': order.id,
                        'product_qty': 1.0,
                        'product_id': pt_product.product_id.id,
                        'name': pt_product.product_id.name,
                        'product_uom': pt_product.product_id.uom_po_id.id,
                        'price_unit': price,
                        'taxes_id': [(6, 0, taxes_ids)],
                        'orign_term_id': wiz.mode_id.terms_ids[0].id
                        }, context=context) 
                for pt_product in term.payment_term_product_ids:
                    prodduct_added= True
                    total = order.amount_total
                    taxes = account_tax.browse(cr, uid, map(lambda x: x.id, pt_product.product_id.taxes_id))
                    fpos = fiscal_position_id and account_fiscal_position.browse(cr, uid, fiscal_position_id, context=context) or False
                    taxes_ids = account_fiscal_position.map_tax(cr, uid, fpos, taxes)
                    if pt_product.tipo == 'porcentaje':
                        continue
                    if pt_product.tipo == 'fijo':             
                        price = pt_product.valor
                    line_obj.create(cr, uid,{
                        'order_id': order.id,
                        'product_qty': 1.0,
                        'product_id': pt_product.product_id.id,
                        'name': pt_product.product_id.name,
                        'product_uom': pt_product.product_id.uom_po_id.id,
                        'price_unit': price,
                        'taxes_id': [(6, 0, taxes_ids)],
                        'orign_term_id': wiz.mode_id.terms_ids[0].id
                        }, context=context)                        
                #calculamos los plazos  
                term = self.pool.get('account.payment.term').browse(cr, uid, wiz.mode_id.terms_ids[0].id, context=context )     
                term_compute =  term.compute(order.amount_total) 
                total_pagos=0
                for plazo in term_compute[0]:
                    total_pagos = total_pagos + 1
                    desgrose_obj.create(cr, uid,{ 'sale_id':order.id,'date':plazo[0],'importe':plazo[1] })          
                if total_pagos>1:
                    sale_obj.write(cr, uid,order.id,{'dummy_mostrar_desglose':True}) 
                #Creamos la transacción para el pago Online

            if wiz.mode_id.acquirer_id:

                acquirer_id = wiz.mode_id.acquirer_id.id
                # find an already existing transaction
                tx_id = False
                tx_ids = payment_transaction_obj.search(cr, uid,[('reference','like',order.name)], context=context )  
                    
                if len(tx_ids) > 1:
                    raise osv.except_osv(_('Error!'), _("Se ha encontrado mas de una transacción de pago.")) 
                        
                if tx_ids:
                    tx = payment_transaction_obj.browse(cr, uid,tx_ids[0], context=context ) 
                    if tx.state != 'draft':
                        raise osv.except_osv(_('Error!'), _("Transaccion ya confirmada.")) 
                if len(tx_ids) == 0:
                    country_id = order.partner_id.country_id and order.partner_id.country_id.id or False
                    if not country_id:
                        country_id = self.pool.get('res.country').search(cr, uid,[('code','=','ES')], limit=1)[0] 
    
                    tx_id = payment_transaction_obj.create(cr, uid, {
                        'acquirer_id': acquirer_id,
                        'type': 'form',
                        'amount': order.amount_total,
                        'currency_id': order.pricelist_id.currency_id.id,
                        'partner_id': order.partner_id.id,
                        'partner_country_id': country_id,
                        'reference': order.name,
                        'sale_order_id': order.id,
                    }, context=context)
                else:
                    tx_id = tx_ids[0]
                    
                # update quotation
                sale_obj.write(
                    cr, uid, order.id, {
                        'payment_acquirer_id': acquirer_id,
                        'payment_tx_id': tx_id
                    }, context=context)
            else:

                #buscamos las transacciones creadas y las borramos....
                tx_ids = payment_transaction_obj.search(cr, uid,[('reference','=',order.name)], context=context )  
                for tx_id_ in tx_ids:
                    if payment_transaction_obj.browse(cr, uid,tx_id_, context=context ).state != 'draft': 
                        raise osv.except_osv(_('Error!'), _("Esta intentando eliminar una transaccion ya confirmada.")) 
                    payment_transaction_obj.unlink(cr, uid,tx_ids, context=context )
                # update quotation
                sale_obj.write(
                        cr, uid, order.id, {
                            'payment_acquirer_id': False,
                            'payment_tx_id': False,
                            'ready_to_pay': False 
                        }, context=context)                        
                
















        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

