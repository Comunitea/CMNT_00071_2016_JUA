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
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
 
class acp_yanez_origen_cliente(osv.osv):
    _name = "acp_yanez.origen_cliente"
    _description = "Origenes de Clientes"
    _columns = {
        
        'name': fields.char('Nombre', size=60, required=True,select=True),
        'descripcion': fields.text('Descripcion'),
        'active': fields.boolean('Activo', help="Permite ocultar este registro sin eliminarlo."),           
    }    
    _defaults = {
        'active': 1,
    }
    
    _sql_constraints = [
        ('unique_origen_cliente', 'unique(name)', 'Origen de Cliente debe ser unico !'),
        
    ]
    
acp_yanez_origen_cliente()

class acp_yanez_account_payment_term_product(osv.osv):
    _name = 'acp_yanez.account_payment_term_product'
    _columns = {
        'term_id': fields.many2one('account.payment.term', 'Plazo de Pago'),        
        'product_id': fields.many2one('product.product', 'Producto'),        
        'tipo': fields.selection(
                [('fijo', 'Importe Fijo'),('porcentaje', 'porcentaje')],
                'Tipo', required=True),        
        'valor': fields.float('Valor', digits_compute= dp.get_precision('Product Price')),
    }
 
acp_yanez_account_payment_term_product()

class acp_yanez_sale_order_desglose(osv.osv):
    _name = 'acp_yanez.sale_order_desglose'
    _columns = {
        'sale_id': fields.many2one('sale.order', 'Pedido', required=True,ondelete='cascade'),        
        'date': fields.date('Fecha Vencimiento'),
        'importe': fields.float('Importe', digits_compute= dp.get_precision('Product Price')),
    }
 
acp_yanez_sale_order_desglose()

class acp_yanez_sale_attachment(osv.osv):


    _name = "acp_yanez.sale_attachment"
    _columns = {
        'sale_id': fields.many2one('sale.order', 'Pedido', required=True,ondelete='cascade'),    
        'name': fields.char('Descripción', required=True),
        'tipo': fields.selection(
                [('justificante', 'Justificante Transferencia'),('mandato', 'Mandato')],
                'Tipo', required=True),         
        'data': fields.binary('Documento', required=True),
        'data_fname': fields.char('Nombre'),        
        'active': fields.boolean('Active', help="The active field allows you to hide the category without removing it."),        
    }
    _defaults = {
        'active': 1,
    }    
    def borrar(self, cr, uid, ids, context=None):  
        print 'borrarborrarborrarborrarborrarborrarborrar'
        for o in self.browse(cr, uid, ids):
            print 'ooooooooooooooo'
            print o
            o.write({'active':False})
        #self.unlink(cr, uid, ids, context=context)     
        return True


acp_yanez_sale_attachment()

class acp_yanez_invoice(osv.osv):
    _name = "acp_yanez.invoice"
    _description = "Historico de facturas"
    _columns = {
        
        'name': fields.char('Número', size=60, required=True,select=True),
        'date': fields.date('Fecha', required=True),
        'descripcion': fields.text('Descripcion'),
        'total': fields.float('Total Factura', digits_compute= dp.get_precision('Account')),
        'partner_id': fields.many2one('res.partner', 'Cliente'),
    }    
    
    _sql_constraints = [
        ('unique_name', 'unique(name)', 'Numero de factura debe ser unico !'),
        
    ]
    
acp_yanez_invoice()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

