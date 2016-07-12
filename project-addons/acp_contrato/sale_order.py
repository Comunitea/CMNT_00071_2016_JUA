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
from datetime import datetime
from dateutil.relativedelta import relativedelta


#----------------------------------------------------------
# Sale Order
#----------------------------------------------------------
class sale_order(osv.osv):
    _inherit = 'sale.order'
    
    _columns = {
        'dft_contrato_id': fields.many2one('acp_contrato.contrato', 'Contrato', readonly=False,required=False,copy=False),         
        'dft_servicio_id': fields.many2one('acp_contrato.servicio', 'Servicio', readonly=False,required=False,copy=False),         
        'perioricidad': fields.selection([
                     ('mensual','Mensual'),
                     ('trimestral','Trimestral'),
                     ('semestral','Semestral'),                     
                     ('anual','Anual'),
                      ], 'Periodicidad',  select=True),
        'tipo_contrato': fields.many2one('acp_contrato.tipo_contrato', 'Tipo de Contrato', select=True,required=False),
        'referencia': fields.char('Referencia', size=120, required=False ),
              }     


    def crea_contrato(self,cr,uid,ids,context=None):
        print "<<<<<<<<<<<<<<<<<<  CREA CONTRATO"
        contrato_obj = self.pool.get('acp_contrato.contrato')
        contrato_producto_obj = self.pool.get('acp_contrato.contrato_producto')
        facturacion_obj = self.pool.get('acp_contrato.facturacion')
        conceptos_factura_obj = self.pool.get('acp_contrato.conceptos_factura')
        fechas_factura_obj = self.pool.get('acp_contrato.fechas_facturacion')
        programar_servicio_obj = self.pool.get('acp_contrato.programar_servicio')
        fechas_servicio_obj = self.pool.get('acp_contrato.fechas_servicio')
        
        
        
        order_obj = self.pool.get('sale.order')
        order_line_obj = self.pool.get('sale.order.line')
        
        if len(ids) > 1:
            return True                
            
        order = order_obj.browse(cr,uid,ids[0],context=context)    
        facturacion_id = False
        fechas_factura_id = False
        programar_servicio_id = False

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
        contrato_id = contrato_obj.create(cr, uid, {'name': '/',
                                                    'referencia': order.referencia or order.name,
                                                    'partner_id': order.partner_id.id,
                                                    'sale_id':order.id,
                                                    'pricelist_id': order.pricelist_id.id,
                                                    'partner_direccion_id': order.partner_shipping_id.id,
                                                    'partner_factura_id': order.partner_invoice_id.id,
                                                    'perioricidad':   order.perioricidad,
                                                    'tipo_contrato': order.tipo_contrato.id, 
                                                    'fecha': datetime.strptime(fields.datetime.now(), '%Y-%m-%d %H:%M:%S')
                                                    }, context=context)  

                                                                                    
                                                                                         
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
            #la lineas de tipo material las creamos como materiales del contrato

            if (line.product_id.type == 'consu') or (line.product_id.type == 'product'):
                for x in range(0, int(line.product_uom_qty)):
                    contrato_producto_obj.create(cr, uid, {'contrato_id': contrato_id,
                                                           'product_id': line.product_id.id,
                                                           'tipo_producto_n': line.product_id.tipo_producto.name,
                                                    }, context=context)  
                order_line_obj.write(cr, uid, line.id, {'contrato_id': contrato_id}, context=context)
                
            # Crea la programación de facturacion de articulos de servicios
            line_tipo_servicio = ''
            if line.tipo_servicio.name:
                line_tipo_servicio = line.tipo_servicio.name.upper()
                
            if (line.product_id.type == 'service') and  line_tipo_servicio.find('INSTALA') == -1:                    
                if not facturacion_id:
                    facturacion_id = facturacion_obj.create(cr, uid, {'contrato_id': contrato_id,
                                                                      'name': 'Facturación ' + order.perioricidad,
                                                                      'autofactura': True,
                                                                    }, context=context)   
                    if facturacion_id:
                        for num_mes in range(0,12,rango_factura):
                            print "<<<<<<<<<<< Mes programacion facturacion: ",num_mes
                            mes_factura_d = datetime.today()+ relativedelta(months=num_mes)
                            mes_factura = mes_factura_d.strftime('%m')
                            fechas_factura_id = fechas_factura_obj.create(cr, uid, {'facturacion_id': facturacion_id,
                                                                                    'mes': mes_factura,
                                                                                    'dia': 1,
                                                                                    }, context=context)                         
                
                conceptos_factura_obj.create(cr, uid, {'facturacion_id': facturacion_id,
                                                       'product_id': line.product_id.id,
                                                       'name': line.product_id.name_get()[0][1],
                                                       'cantidad': line.product_uom_qty,
                                                       'importe': line.price_unit
                                                       }, context=context)
                                                       
                order_line_obj.write(cr, uid, line.id, {'contrato_id': contrato_id}, context=context)   
        
        self.write(cr, uid, ids, {'dft_contrato_id': contrato_id}, context=context)

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

        
        
class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    std = [
            ('draft', 'Presupuesto borrador'),
            ('sent', 'Presupuesto enviado'),
            ('cancel', 'Desestimado'),
            ('waiting_date', 'Esparando fecha planificada'),
            ('progress', 'Presupuest oestimado (Aceptado)'),
            ('manual', 'Venta a facturar'),
            ('shipping_except', 'Excepción en envio'),
            ('invoice_except', 'Excepcion en factura'),
            ('done', 'Realizado'),
            ]
            
    perioricidad = [
            ('mensual','Mensual'),
            ('trimestral','Trimestral'),
            ('semestral','Semestral'),                     
            ('anual','Anual'),
            ]            
    _columns = {
        'contrato_id' : fields.many2one('acp_contrato.contrato', 'Contrato', readonly=False,required=False,copy=False),            
        'servicio_id': fields.many2one('acp_contrato.servicio', 'Servicio', readonly=False,required=False,copy=False),         
        'order_state': fields.related('order_id','state' , type='selection',selection=std , string='Estado'),
        'perioricidad_servicio': fields.related('product_id','perioricidad_servicio' , type='selection',selection=perioricidad , string='Perioridad Mantenimiento'),          
        'tipo_servicio': fields.related('product_id','tipo_servicio',type="many2one",relation="acp_contrato.tipo_servicio",string="Servicio Mantenimiento",required=False,store=True) ,                                    
     }    
    _defaults = {
      'contrato_id': lambda self, cr, uid, context : context['contrato_id'] if context and 'contrato_id' in context else None,
      'servicio_id' : lambda self, cr, uid, context : context['servicio_id'] if context and 'servicio_id' in context else None          
   }  
  
    def open_so(self,cr,uid,ids,context=None):
       
        if context is None:
            context = {}
        order_id = self.browse(cr, uid, ids, context=context)[0].order_id.id    
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pedido de Venta',
            'view_type': 'form',
            'view_mode': 'form',
            'context': context,
            'res_model': 'sale.order',
            'nodestroy': True,
            'res_id': order_id, 
            'target':'current', 
            }
    
    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):
        res = {}
        res = super(sale_order_line, self)._prepare_order_line_invoice_line(cr, uid, line, account_id=account_id, context=context)
        res['contrato_id'] = line.contrato_id and line.contrato_id.id or False
        res['servicio_id'] = line.servicio_id and line.servicio_id.id or False
        return res    
sale_order_line()






# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
