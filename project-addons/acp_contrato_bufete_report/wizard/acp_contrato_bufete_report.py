# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2012 Tiny SPRL (http://tiny.be). All Rights Reserved
#
#    This module,
#    Copyright (C) 2013 KM Sistemas de Información, S.L. - http://www.kmsistemas.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
import datetime  
import openerp.addons.decimal_precision as dp
import time
from dateutil.relativedelta import relativedelta
from random import randint

def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)  # this will never fail
    return next_month - datetime.timedelta(days=next_month.day)
#===============================================================================
# Ventana de selección del informe a imprimir
#===============================================================================
class acp_contrato_bufete_report_wizard(osv.osv_memory):
    
    _name = 'acp_contrato.bufete.report.wizard'
    _description = "Asistente informes"
    _columns = {
        'report_model':fields.selection([
            ('acp_contrato.bufete.horas_letrado', 'Horas Letrado'),
            ('acp_contrato.bufete.horas_cliente', 'Horas Cliente'),
            ('acp_contrato.bufete.actuaciones', 'Actuaciones por Expediente'),
            ('acp_contrato.bufete.igualas', 'Actuaciones por Iguala'),            
            ], 'Informe', required = True),
    }


    def action_next(self, cr, uid, ids, context = None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [])
        data = data and data[0] or {}
        report_model_name = data['report_model']
                
        return {
            'view_type': 'form',
            "view_mode": 'form',
            'res_model': report_model_name + ".wizard",
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new',
         }


acp_contrato_bufete_report_wizard()



#===============================================================================
# Wizard para el informe seleccionado tipo 1: Informe Horas Letrado
#===============================================================================
class acp_contrato_bufete_horas_letrado_wizard(osv.osv_memory):

    _name = 'acp_contrato.bufete.horas_letrado.wizard'

    _columns = {
        'abogado_id': fields.many2one('res.partner', 'Letrado', required=False ),  
        'fecha_desde': fields.date('Desde fecha '),
        'fecha_hasta': fields.date('Hasta fecha '),      
    }

    def action_print(self, cr, uid, ids, context = None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [])
        data = data and data[0] or {}

        
        if data['fecha_desde']:
           fecha_desde_d = datetime.datetime.strptime(data['fecha_desde'], '%Y-%m-%d')
           fecha_desde_c = fecha_desde_d.strftime('%Y/%m/%d')
        else:
           fecha_desde_c = '2000/01/01' 

           
        if data['fecha_hasta']:
           fecha_hasta_d = datetime.datetime.strptime(data['fecha_hasta'], '%Y-%m-%d')
           fecha_hasta_c = fecha_hasta_d.strftime('%Y/%m/%d')
        else:
           fecha_hasta_c = '3000/01/01' 
           
        logo = self.pool.get('res.partner').browse(cr, uid, 1, context=context).company_id.logo
        parameters={}
        parameters['FECHA_DESDE'] = fecha_desde_c
        parameters['FECHA_HASTA'] = fecha_hasta_c
        parameters['LOGO'] = logo
        if data['abogado_id'] :   
            parameters['ABOGADO_ID'] = data['abogado_id'][0]          
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'acp_contrato_bu_horas_letrado_jasper',
            'datas': {
                'model': 'acp_contrato.bufete.horas_letrado.wizard',
                #'id': False,
                #'ids': False,
                'form': data,
                'parameters': parameters
            },
            'nodestroy': True,
        }

acp_contrato_bufete_horas_letrado_wizard()

#===============================================================================
# Wizard para el informe seleccionado tipo 2: Informe Horas Cliente
#===============================================================================
class acp_contrato_bufete_horas_cliente_wizard(osv.osv_memory):

    _name = 'acp_contrato.bufete.horas_cliente.wizard'
    _description = "Asistente informe horas cliente"
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Cliente', required = True ),  
        'fecha_desde': fields.date('Desde fecha inicio'),
        'fecha_hasta': fields.date('Hasta fecha inicio'),      
    }

    def action_print(self, cr, uid, ids, context = None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [])
        data = data and data[0] or {}

        
        
        if data['fecha_desde']:
           fecha_desde_d = datetime.datetime.strptime(data['fecha_desde'], '%Y-%m-%d')
           fecha_desde_c = fecha_desde_d.strftime('%Y/%m/%d')
        else:
           fecha_desde_c =  '2000/01/01'  

           
        if data['fecha_hasta']:
           fecha_hasta_d = datetime.datetime.strptime(data['fecha_hasta'], '%Y-%m-%d')
           fecha_hasta_c = fecha_hasta_d.strftime('%Y/%m/%d')
        else:
           fecha_hasta_c =  '3000/01/01'  
        logo = self.pool.get('res.partner').browse(cr, 1, data['partner_id'][0], context=context).company_id.logo
        parameters={}
        parameters['FECHA_DESDE'] = fecha_desde_c
        parameters['FECHA_HASTA'] = fecha_hasta_c
        parameters['LOGO'] = logo
        if data['partner_id'] :   
            parameters['CLIENTE_ID'] = data['partner_id'][0]                                  
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'acp_contrato_bu_horas_cliente_jasper',
            'datas': {
                'model': 'acp_contrato.contrato',
                #'id': False,
                #'ids': False,
                'form': data,
                'parameters': parameters
            },
            'nodestroy': True,
        }

acp_contrato_bufete_horas_cliente_wizard()
#===============================================================================
# Wizard para el informe seleccionado tipo 2: Informe Horas Cliente
#===============================================================================
class acp_contrato_bufete_actuaciones_wizard(osv.osv_memory):

    _name = 'acp_contrato.bufete.actuaciones.wizard'
    _description = "Asistente informe actuaciones"
    _columns = {
        'contrato_id': fields.many2one('acp_contrato.contrato', 'Expediente', required = True ),     
    }

    def action_print(self, cr, uid, ids, context = None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [])
        data = data and data[0] or {}
        ids = self.pool.get('acp_contrato.contrato').search(cr, uid, [('id','=',data['contrato_id'][0])] , context = context)
        if not ids:
            raise osv.except_osv(_('Información'), _("No se han encontrado registros con los criterios seleccionados. Repita la búsqueda con otros criterios."))

        logo = self.pool.get('acp_contrato.contrato').browse(cr, uid, data['contrato_id'][0], context=context).company_id.logo
                                 
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'acp_contrato_bu_tareas_jasper',
            'datas': {
                'model': 'acp_contrato.contrato',
                #'id': context.get('active_ids') and context.get('active_ids')[0] or False,
                #'ids': ids,
                'form': data,
                'parameters': {'CONTRATO_ID':  data['contrato_id'][0],
                               'LOGO': logo
                               }
            },
            'nodestroy': True,
        }

acp_contrato_bufete_actuaciones_wizard()


#===============================================================================
# Wizard para el informe seleccionado tipo 2: Informe Horas Igualas
#===============================================================================
class acp_contrato_bufete_igualas_report(osv.osv_memory):

    _name = 'acp_contrato.bufete.igualas.report'
    _description = "Informe igualas"
    _columns = {
        'report_id': fields.char('id', required = True ),     
        'partner_name': fields.char('Cliente', required = True ,size=255),     
        'iguala': fields.char('Iguala', required = True ,size=255),     
        'iguala_id': fields.integer('Iguala', required = True ),     
        'servicios': fields.char('Servicios', required = False ,size=255),     
        'horas_trimestre': fields.char('horas_trimestre', required = False ,size=255),     
        'riesgo_maximo': fields.float('riesgo_maximo', required = False ),     
        'descripcion': fields.char('descripcion', required = False ,size=255),     
        'servicio': fields.char('servicio', required = False ,size=255),     
        'tarea': fields.char('tarea', required = False ,size=255),     
        'subexpediente': fields.char('subexpediente', required = False ,size=255),     
        'solicitante': fields.char('solicitante', required = False ,size=255),     
        'finalizada': fields.char('finalizada', required = False ,size=255),     
        'dia_tarea': fields.char('dia_tarea', required = False ,size=255),     
        'horas_tarea': fields.float('horas_tarea', required = False ),     
        'riesgo_tarea': fields.float('riesgo_tarea', required = False ),     
        'usuario_tarea': fields.char('usuario_tarea', required = False ,size=255),     
        




    }

acp_contrato_bufete_igualas_report()
    
    
class acp_contrato_bufete_igualas_wizard(osv.osv_memory):

    _name = 'acp_contrato.bufete.igualas.wizard'
    _description = "Asistente informe igualas"
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Cliente', required = False ),     
        'mes':fields.selection([
            ('01', 'Enero'),
            ('02', 'Febrero'),
            ('03', 'Marzo'),
            ('04', 'Abril'),
            ('05', 'Mayo'),
            ('06', 'Junio'),
            ('07', 'Julio'),
            ('08', 'Agosto'),
            ('09', 'Septiembre'),
            ('10', 'Octubre'),
            ('11', 'Noviembre'),
            ('12', 'Diciembre'),
            ], 'Mes', required = False),
        'ejercicio': fields.integer('Año'),
        'fecha_desde': fields.date('Desde fecha inicio'),
        'fecha_hasta': fields.date('Hasta fecha inicio'),         
    }

    _defaults= {
        'ejercicio': lambda *a: time.strftime('%Y'),
        }

    def onchange_mes_id(self, cr, uid, ids, mes, ejercicio, context=None):
        context = context or {}
        if not mes:
            return {'value': {'fecha_desde':False,'fecha_hasta':False}}
        if not ejercicio:
            return {'value': {'fecha_desde':False,'fecha_hasta':False}}
            


        fecha_desde = str(ejercicio)+'-'+ mes +'-'+'01'
        fecha_hasta = last_day_of_month(datetime.datetime.strptime(fecha_desde , '%Y-%m-%d')).strftime('%Y-%m-%d') 

        
        return {'value': {'fecha_desde':fecha_desde,'fecha_hasta':fecha_hasta}}
        
    def action_print(self, cr, uid, ids,print_report=True, context = None):
        report_obj = self.pool.get('acp_contrato.bufete.igualas.report')
        expediente_obj = self.pool.get('acp_contrato.contrato')
        horas_obj = self.pool.get('acp_contrato.tarea_horas')
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [])
        data = data and data[0] or {}

        report_id =  datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(randint(0,999))
        if data['fecha_desde']:
           fecha_desde_d = datetime.datetime.strptime(data['fecha_desde'], '%Y-%m-%d').date()
           fecha_desde_c = fecha_desde_d.strftime('%Y/%m/%d')
        else:
           fecha_desde_c = '2000/01/01' 
           fecha_desde_d = datetime.datetime.strptime('2000/01/01', '%Y/%m/%d').date()

           
        if data['fecha_hasta']:
           fecha_hasta_d = datetime.datetime.strptime(data['fecha_hasta'], '%Y-%m-%d').date()
           fecha_hasta_c = fecha_hasta_d.strftime('%Y/%m/%d')
        else:
           fecha_hasta_c = '3000/01/01'
           fecha_hasta_d = datetime.datetime.strptime('3000/01/01', '%Y/%m/%d').date()
           
           
        #seleccionamos todos los expedientes que vencen el mes en el rango de fechas solicitado
        
        #seleccionamso todos los expediente iguala
        if data['partner_id']:
            expediente_iguala_ids = expediente_obj.search(cr, uid, [
                                                                ('partner_id','=',data['partner_id'][0]),
                                                                ('state','in',['exception','confirmed']),                                                                
                                                                ('fecha','<=',fecha_hasta_c),
                                                                ('tipo_contrato.name' ,'=', 'Iguala'),
                                                                ('contrato_plantilla' ,'=', True),
                                                                '|',('fecha_limite_asignada','=',False),
                                                                ('fecha_limite_asignada','>=',fecha_hasta_c),
                                                                ], context = context)
            print 'expediente_iguala_ids'
            print expediente_iguala_ids
        else:
            expediente_iguala_ids = expediente_obj.search(cr, uid, [
                                                                ('state','in',['exception','confirmed']),
                                                                ('fecha','<=',fecha_hasta_c),
                                                                ('tipo_contrato.name' ,'=', 'Iguala'),
                                                                ('contrato_plantilla' ,'=', True),
                                                                '|',('fecha_limite_asignada','=',False),
                                                                ('fecha_limite_asignada','>=',fecha_hasta_c),
                                                                ], context = context)

        #comprobamos si tiene un vencimiento entre las fechas del informe
        expedientes_ids = []
        for expediente in  expediente_obj.browse(cr, uid, expediente_iguala_ids, context = context):

            fecha_inicio = datetime.datetime.strptime(expediente.fecha, '%Y-%m-%d %H:%M:%S').date()
            fecha_vencimiento_mes_contrato = fecha_inicio 

                
            for i in range(0,50):
                fecha_vencimiento_mes_contrato = fecha_vencimiento_mes_contrato + relativedelta(months=+1)
                print 'fecha_vencimiento_mes_contrato'
                print fecha_vencimiento_mes_contrato
                print 'fecha_desde_d'
                print fecha_desde_d
                print 'fecha_hasta_d'
                print fecha_hasta_d
                if (fecha_vencimiento_mes_contrato >= fecha_desde_d) and (fecha_vencimiento_mes_contrato <= fecha_hasta_d):
                    print 'encontrada***************'
                    print fecha_vencimiento_mes_contrato

                    for expediente in  expediente_obj.browse(cr, uid, expediente.id, context = context):
                        #seleccionaos las horas desde la fecha - 1 dia hasta 30 dias atras

                        horas_ids = horas_obj.search(cr, uid, [
                                                                ('parent_id','=',expediente.id),
                                                                ('fecha','<',fecha_vencimiento_mes_contrato),
                                                                ('fecha','>=',fecha_vencimiento_mes_contrato + relativedelta(months=-1)),
                                                                ], context = context)

        
     
        
                        #para cada expediente buscamos las tareas que han tenido horas asignadas de un mes hacia atras
                        
                        for hora in horas_obj.browse(cr, uid, horas_ids, context = context):
                            if (hora.tarea_id.servicio_id.tipo_servicio.id == 2):
                                if (hora.tarea_id.state =='done'):
                                    finalizada = 'Si'
                                else:
                                    finalizada = 'No'
                                report_obj.create(cr, uid, {'report_id':report_id,
                                                    'partner_name': expediente.partner_id.name,
                                                    'iguala': expediente.name,     
                                                    'iguala_id': expediente.id,     
                                                    'servicios': expediente.observaciones,
                                                    'horas_trimestre': expediente.total_horas_trabajadas,     
                                                    'riesgo_maximo': expediente.riesgo_operacional,
                                                    'descripcion': hora.tarea_id.observaciones and hora.tarea_id.observaciones[0:250] or '',
                                                    'servicio': hora.tarea_id.servicio_id.name,
                                                    'tarea': hora.tarea_id.numero_tarea,     
                                                    'subexpediente': hora.contrato_id.name,     
                                                    'solicitante': hora.tarea_id.contrato_id.solicitante.name,  
                                                    'finalizada': finalizada,
                                                    'dia_tarea': hora.fecha,
                                                    'horas_tarea': hora.horas,
                                                    'riesgo_tarea': hora.tarea_id.riesgo_operacional,  
                                                    'usuario_tarea': hora.tarea_id.user_seg_id.name,   
                                                    }, context = context)
        

           

        logo = self.pool.get('res.company').browse(cr, uid, 1, context=context).logo
        
        if print_report:
            return self.action_return( cr, uid, ids,data,report_id,fecha_desde_c,fecha_hasta_c,logo, context = context)
        else:
            return  (data,report_id,fecha_desde_c,fecha_hasta_c,logo)                    


    def action_return(self, cr, uid, ids,data,report_id,fecha_desde_c,fecha_hasta_c,logo, context = None):
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'acp_contrato_bu_igualas_jasper',
            'datas': {
                'model': 'acp_contrato.contrato',
                #'id': context.get('active_ids') and context.get('active_ids')[0] or False,
                #'ids': ids,
                'form': data,
                'parameters': {
                               'REPORT_ID': report_id,
                               'FECHA_DESDE': fecha_desde_c,
                               'FECHA_HASTA': fecha_hasta_c,
                               'LOGO': logo                               
                               }
            },
            'nodestroy': True,
        }
acp_contrato_bufete_igualas_wizard()


