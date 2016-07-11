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

from mx import DateTime
#import netsvc
import time
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from dateutil.relativedelta import relativedelta



#----------------------------------------------------------
# Sale Order
#----------------------------------------------------------
class sale_order(osv.osv):
    _inherit = 'sale.order'
    
    def _descripcion_lineas(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        result = {}		
        for sale in self.browse(cr, uid, ids, context=context):
            desc = ''
            for line in sale.order_line:
                desc = desc + line.name + ' \n'
            result[sale.id] = desc
        return result  
        
    def _descripcion_iguala(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        result = {}		
        for sale in self.browse(cr, uid, ids, context=context):
            desc = ''
            for line in sale.order_line:
                for materia in line.line_materia_ids:
                    d= materia.materia_id.name + ' con límite de '+str(int(materia.horas))+' horas contratadas ' + (sale.perioricidad or '') 
                    desc = desc + d + ' \n'
            result[sale.id] = desc
        return result 

    _columns = {
        'fecha_falidez': fields.date('Valido Hasta', required=False),
        'materia_id': fields.many2one('acp_contrato.materia', 'Materia',  required=False),
        'horas': fields.float('Horas estimadas', digits=(16, 2), required=False),
        'descripcion_lineas': fields.function(_descripcion_lineas, string='Descripción', type="text" ), 
        'riesgo_operacional': fields.float('Riesgo operacional', digits=(16, 2), required=False),
        'meses_contratado': fields.integer('Número de meses contratados', required=False),        
        'descripcion_iguala': fields.function(_descripcion_iguala, string='Descripción iguala', type="text" ), 

              }  
    
    # Para bufete se modifica la forma de generar contrato desde pedidos de venta
    def crea_contrato_bufete(self,cr,uid,ids,context=None):
        contrato_obj = self.pool.get('acp_contrato.contrato')
        contrato_materia_obj = self.pool.get('acp_contrato.contrato_materia')                        
        order_obj = self.pool.get('sale.order')
        order_line_obj = self.pool.get('sale.order.line')
        contrato_producto_obj = self.pool.get('acp_contrato.contrato_producto')
        facturacion_obj = self.pool.get('acp_contrato.facturacion')
        conceptos_factura_obj = self.pool.get('acp_contrato.conceptos_factura')
        fechas_factura_obj = self.pool.get('acp_contrato.fechas_facturacion')
        
        descripcion = ''
        
        if len(ids) > 1:
            return True                
            
        order = order_obj.browse(cr,uid,ids[0],context=context)    
        facturacion_id = False
        fecha_confirmaciond = datetime.strptime(order.fecha_confirmacion, '%Y-%m-%d')        
        '''            
        if not order.perioricidad:

            raise osv.except_osv(
                        _('Faltan datos'),
                        _('Indique la periodicidad para poder crear el contrato.'))    
        '''
        if order.dft_contrato_id:

            raise osv.except_osv(
                        _('Error'),
                        _('Ya se ha generado para este pedido.'))        
        if not order.tipo_contrato:

            raise osv.except_osv(
                        _('Faltan datos'),
                        _('Indique el tipo de contrato para poder crear el contrato.'))                             
                        
        #creamos el contrato
        print 'fields.datetime.now() fields.datetime.now()fields.datetime.now()fields.datetime.now()'
        print fields.datetime.now()
        contrato_id = contrato_obj.create(cr, uid, {'name': '/',
                                                    'referencia': order.referencia or order.name,
                                                    'partner_id': order.partner_id.id,
                                                    'sale_id':order.id,                                                    
                                                    'pricelist_id': order.pricelist_id.id,
                                                    'partner_direccion_id': order.partner_shipping_id.id,
                                                    'partner_factura_id': order.partner_invoice_id.id,
                                                    'perioricidad':   order.perioricidad,
                                                    'tipo_contrato': order.tipo_contrato.id, 
                                                    'fecha': datetime.strptime(order.fecha_confirmacion + ' 06:00:00', '%Y-%m-%d %H:%M:%S'),
                                                    'riesgo_operacional':order.riesgo_operacional,      
                                                    }, context=context)  
        if order.tipo_contrato.name == 'Iguala':
            if not order.perioricidad:
                raise osv.except_osv(
                            _('Faltan datos'),
                            _('Indique la periodicidad para poder crear el contrato.'))    
            for line in order.order_line:
                descripcion = descripcion + line.name + ' \n'
                for materia in line.line_materia_ids:
                        contrato_materia_obj.create(cr, uid, {'contrato_id': contrato_id,
                                                               'materia_id': materia.materia_id.id,
                                                               'horas': materia.horas}, context=context)  
                                
                order_line_obj.write(cr, uid, line.id, {'contrato_id': contrato_id}, context=context) 
            contrato_obj.write(cr, uid, contrato_id, {'contrato_plantilla': True,'observaciones': descripcion,'fecha_limite_asignada':fecha_confirmaciond+ relativedelta(months=order.meses_contratado)}, context=context)
        else: 
            for line in order.order_line:
                order_line_obj.write(cr, uid, line.id, {'contrato_id': contrato_id}, context=context)
                
            contrato_obj.write(cr, uid, contrato_id, {'observaciones': order.descripcion_lineas,'horas_estimadas': order.horas,'materia_id': order.materia_id.id}, context=context)
            
        self.write(cr, uid, ids, {'dft_contrato_id': contrato_id}, context=context)
        #ponemos el pedido como realizado
        if order.tipo_contrato.name == 'Iguala':
            self.write(cr, uid, ids, {'state': 'done'}, context=context)        
            
            

        rango_factura = 0
        if order.perioricidad:
            print "<<<<<<<<<<<<<<<<<<  order.perioricidad: ",order.perioricidad  
            if order.perioricidad == 'mensual':
                rango_factura = 1
            if order.perioricidad == 'trimestral':
                rango_factura = 3
            if order.perioricidad == 'semestral':
                rango_factura = 6
            if order.perioricidad == 'anual':
                rango_factura = 12                                               

        for line in order.order_line:
                
            # Crea la programación de facturacion de articulos
            if order.tipo_contrato.name == 'Iguala':    
                if not order.perioricidad: 
                    raise osv.except_osv(
                        _('Faltan datos'),
                        _('Indique la periodicidad para poder crear el contrato.')) 
                if not facturacion_id:
                    facturacion_id = facturacion_obj.create(cr, uid, {'contrato_id': contrato_id,
                                                                      'name': 'Facturación ' + order.perioricidad,
                                                                      'autofactura': True,
                                                                    }, context=context)   
                    if facturacion_id:
                        for num_mes in range(0,12,rango_factura):
                            print "<<<<<<<<<<< Mes programacion facturacion: ",num_mes
                            mes_factura_d = fecha_confirmaciond+ relativedelta(months=num_mes)
                            mes_factura = mes_factura_d.strftime('%m')
                            fechas_factura_id = fechas_factura_obj.create(cr, uid, {'facturacion_id': facturacion_id,
                                                                                    'mes': mes_factura,
                                                                                    'dia': fecha_confirmaciond.strftime('%d'),
                                                                                    }, context=context)                         
                
                conceptos_factura_obj.create(cr, uid, {'facturacion_id': facturacion_id,
                                                       'product_id': line.product_id.id,
                                                       'name': line.product_id.name_get()[0][1],
                                                       'cantidad': line.product_uom_qty,
                                                       'importe': line.price_unit
                                                       }, context=context)
                                                       
                order_line_obj.write(cr, uid, line.id, {'contrato_id': contrato_id}, context=context)   
            
        # Abre la pantalla de contratos                                             
        return {
            'type': 'ir.actions.act_window',
            'name': 'acp_contrato.contrato.form',
            'view_type': 'form',
            'view_mode': 'form',
            'context': context,
            'res_model': 'acp_contrato.contrato',
            'nodestroy': True,
            'res_id': contrato_id, 
            'target':'current', 
            }


class sale_order_line_materia(osv.osv):
    _name = "sale.order.line.materia"
    _description = "Materias lineas de pedidos de venta"
    
            
    _columns = {
        'line_id': fields.many2one('sale.order.line', 'Linea Pedido Venta', required=False, ondelete='cascade'),
        'materia_id': fields.many2one('acp_contrato.materia', 'Materia',  required=True, change_default=True),
        'horas': fields.float('Horas', digits_compute= dp.get_precision('Product UoS'), required=True, change_default=True),
              }                    
            
sale_order_line_materia()    
           
                     
        
class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
               
    _columns = {
        'line_materia_ids' : fields.one2many('sale.order.line.materia', 'line_id', 'Materias Pedidos Ventas'),      
     }    
     

  
   
sale_order_line()






# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
