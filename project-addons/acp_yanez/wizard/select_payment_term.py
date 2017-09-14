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

#from datetime import datetime
#import netsvc
import time
from openerp.tools.translate import _


class acp_yanez_select_payment_term(osv.osv_memory):
    _name = "acp_yanez.select_payment_term"
    _description = "Selecionar Plazo de Pago"
    _columns = {
        'sale_id': fields.many2one('sale.order', 'Pedido'),  
        'term_ids': fields.one2many('acp_yanez.select_payment_term_l','wiz_id', 'Plazo de Pago'),  
    }

    
class acp_yanez_select_payment_term_l(osv.osv_memory):
    _name = "acp_yanez.select_payment_term_l"
    _description = "Selecionar Plazo de Pago"
    _columns = {
        'wiz_id': fields.many2one('acp_yanez.select_payment_term', 'Pedido'),  
        'term_id': fields.many2one('account.payment.term', 'Plazo de Pago'),  
    }
   
    def select(self, cr, uid, ids, context=None):
        account_fiscal_position = self.pool.get('account.fiscal.position')
        account_tax = self.pool.get('account.tax') 
        term_obj = self.pool.get('account.payment.term')
        line_obj = self.pool.get('sale.order.line')
        sale_obj = self.pool.get('sale.order')
        desgrose_obj = self.pool.get('acp_yanez.sale_order_desglose')
        for wiz in self.browse(cr, uid, ids, context=context):
            order = wiz.wiz_id.sale_id
            if order.tipo_contrato.name == 'Iguala' and wiz.term_id.name != 'Pago inmediato':
                 raise osv.except_osv(_('Error!'), _('El único plazo de pago válido para los presupuestos cuyo expediente es de tipo Iguala es pago inmediato.'))
            order.write({'payment_term2':wiz.term_id.id,'dummy_mostrar_desglose':False})

            #elminimamos los plazos actuales
            for desglose in order.desglose_id:
                desglose.unlink(context=context)
                
            #eliminamos las lineas de pedido ocasionadas por los plazos
            for line in order.order_line:
                if line.orign_term_id:
                    line.unlink(context=context)       
            #volvemos a crear la lineas de pedido
            term = term_obj.browse(cr, uid,wiz.term_id.id,context=context)
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
                    'orign_term_id': wiz.term_id.id
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
                    'orign_term_id': wiz.term_id.id
                    }, context=context)                        
            #calculamos los plazos  
            term = self.pool.get('account.payment.term').browse(cr, uid, wiz.term_id.id, context=context )     
            term_compute =  term.compute(order.amount_total) 
            total_pagos=0
            for plazo in term_compute[0]:
                total_pagos = total_pagos + 1
                desgrose_obj.create(cr, uid,{ 'sale_id':order.id,'date':plazo[0],'importe':plazo[1] })          
            if total_pagos>1:
                sale_obj.write(cr, uid,order.id,{'dummy_mostrar_desglose':True}) 
                    
        
        print 'compruebo'
        print prodduct_added
        if prodduct_added:
            print 'prodduct_added'
            warning = {
                'title': _('Precio Extra!'),
                'message' : _('Este metodo depago lleva un coste añadido, compruebe el total del pedido y los plazos de pago.')
            }
            return {'warning': warning}          
        return True    
                  
                           
            #calcularmos los plazos y los creamos


        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

