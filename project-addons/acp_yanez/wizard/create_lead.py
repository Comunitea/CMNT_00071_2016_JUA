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

import base64
from tempfile import TemporaryFile

from openerp import tools,SUPERUSER_ID
from openerp.osv import osv, fields

class wizard_create_lead(osv.osv_memory):


    _name = 'acp_yanez.wizard_create_lead'
    _columns = {
        'company_id': fields.selection([('1', 'Juárez Bufete Internacional, S.L.P'),
                                    ('3', 'Juárez Escuela de Formación, S.L.')
                                    ],
            string='Compañia', required=True),
    }


    def create_lead(self,cr,uid,ids,context=None):
        if context is None:
            context = {}

        if context.has_key('active_model') and context.get('active_model') == 'event.registration':

            data = self.browse(cr, uid, ids, context=context)[0]
            lead_obj=self.pool.get('crm.lead')
            e_registration_obj=self.pool.get('event.registration')
            user_obj=self.pool.get('res.users')
            user = user_obj.browse(cr, uid, uid)
            reg = e_registration_obj.browse(cr, uid, context.get('active_id'))
            actual_company = user.company_id.id
            vals = {'partner_id': reg.partner_id.id ,
                    'partner_name' : reg.name,
                    'email_from': reg.email,
                    'phone': reg.phone,
                    'name': reg.event_id.name,
                    'event_registration_id': reg.id ,
                    'event_id': reg.event_id.id,     
                    'type':'opportunity',
                    'company_id': data.company_id
                    }
            print 'valsvalsvalsvalsvalsvalsvalsvalsvalsvalsvals'
            print vals
            user.write({'company_id':int(data.company_id)})
            lead_id = lead_obj.create(cr,uid,vals,context=context)
            user.write({'company_id':actual_company})
            e_registration_obj.write(cr, uid, reg.id,{'crm_lead_id':lead_id},context=context)
        return True
    '''
    def create_lead(self, cr, uid, ids, context=None):
        msg = ''
        project_obj = self.pool.get('project.project')
        task_obj = self.pool.get('project.task')
        contract_obj = self.pool.get('hr.contract')
        calendario_dia_obj = self.pool.get('acp_hr_extra.calendario_dia')
        
        if context is None:
            context = {}
        data = self.browse(cr, uid, ids, context=context)[0]
        project = project_obj.browse(cr, uid, context['active_id'], context=context)
        
        desde = datetime.strptime(data.from_date, '%Y-%m-%d').date()
        hasta = datetime.strptime(data.to_date, '%Y-%m-%d').date()  
        total_dias = int((hasta - desde).days) +1
        if int((hasta - desde).days) < 0:
                        raise osv.except_osv(_('Error!'),'La fecha final no puede ser menor que la fecha inicial')
        if (data.from_hora >= data.to_hora) and not data.dia_siguiente:
                        raise osv.except_osv(_('Error!'),'La hora final no puede ser menor que la hora inicial, si la tarea termina en otro dia marque la casilla correspondiente')        
        if not data.employee_id.actualmente_contratado:
                        raise osv.except_osv(_('Error!'),'El empledo no está contratado actualmente')  
                        
        #obtenemos los dias fectivos del calendario
        festivos = []
        if project.calendario_id:
             festivos = calendario_dia_obj.search_read(cr, uid,  [('calendario_id','=', project.calendario_id.id)],['dia'], context=context)
             
        if festivos:
            festivos = [rec['dia'] for rec in festivos]
        print 'festivos fin'
        print festivos            
        #obtenemos el contrato del empleado
        cr.execute("select  id from hr_contract " \
                   "where employee_id = " + str(data.employee_id.id) + " " \
                   "and current_date >=  date_start and " \
                   "(current_date <= date_end or date_end is null)")
        res = cr.fetchall()               
        if len(res) > 0:
            contrato_id = res[0][0]
        else:
            raise osv.except_osv(_('Error!'),'No encuentro un contrato activo para este empleado')  
        
        horas_mensuales_contrato = contract_obj.browse(cr, uid, contrato_id, context=context).horas_mensuales
        print 'horas_mensuales_contrato'
        print horas_mensuales_contrato
        dias_seleccionados = []
        horas={}
        if data.dias_semana:
            if data.lunes:
                dias_seleccionados.append('1')
                horas['1']={'from_hora':data.lunes_from_hora , 'to_hora':data.lunes_to_hora}
            if data.martes:
                dias_seleccionados.append('2')
                horas['2']={'from_hora':data.martes_from_hora , 'to_hora':data.martes_to_hora}
            if data.miercoles:
                dias_seleccionados.append('3')
                horas['3']={'from_hora':data.miercoles_from_hora , 'to_hora':data.miercoles_to_hora}
            if data.jueves:
                dias_seleccionados.append('4')
                horas['4']={'from_hora':data.jueves_from_hora , 'to_hora':data.jueves_to_hora}
            if data.viernes:
                dias_seleccionados.append('5')
                horas['5']={'from_hora':data.viernes_from_hora , 'to_hora':data.viernes_to_hora}
            if data.sabado:
                dias_seleccionados.append('6')
                horas['6']={'from_hora':data.sabado_from_hora , 'to_hora':data.sabado_to_hora}
            if data.domingo:
                dias_seleccionados.append('0')
                horas['0']={'from_hora':data.domingo_from_hora , 'to_hora':data.domingo_to_hora}

        for i in range(total_dias):
            
            curr_fecha =  desde + timedelta(days=i)
            if not data.trabajar_festivos:
                if curr_fecha.strftime('%Y-%m-%d') in festivos:
                    msg = msg + 'ATENCION: Dia festivo: ' + curr_fecha.strftime('%d-%m-%Y') + ' No se he creado tarea. \n'
                    continue
            if data.dias_semana:
                if curr_fecha.strftime('%w') in dias_seleccionados:
          


                    task_obj.create(cr, uid,{
                        'project_id': project.id,
                        'date_deadline': curr_fecha,
                        'employee_id': data.employee_id.id,
                        'name': data.descripcion,
                        'from_hora': horas[curr_fecha.strftime('%w')]['from_hora'],
                        'to_hora': horas[curr_fecha.strftime('%w')]['to_hora'],
                        'dia_siguiente' :data.dia_siguiente,
                        }, context=context)       
            else:
                task_obj.create(cr, uid,{
                    'project_id': project.id,
                    'date_deadline': curr_fecha,
                    'employee_id': data.employee_id.id,
                    'name': data.descripcion,
                    'from_hora': data.from_hora,
                    'to_hora': data.to_hora,   
                    'dia_siguiente' :data.dia_siguiente,                 
                    }, context=context)       



            cr.execute("select  sum(planned_hours) " \
                       "from project_task " \
                       "where employee_id = " + str(data.employee_id.id) + " " \
                       "and to_char(date_deadline,'YYYYMM') = '" + curr_fecha.strftime("%Y%m") + "'")
            res = cr.fetchall() 

            total_horas = res[0][0]
            print 'total_horas'
            print curr_fecha.strftime("%Y%m")
            print total_horas
            if not total_horas:
                total_horas = 0.0
            #calculamos el porcentaje de horas asignadas con respecto al contrato
            if (total_horas * 100.0 / horas_mensuales_contrato) >= 100.0:
                msg= msg + '\n' + 'Ha asignado un '+str((total_horas * 100.0 / horas_mensuales_contrato))+'% de las horas contratadas a este empleado . \n Total Horas contrato:' +str(horas_mensuales_contrato)+ '\n Horas Asignadas:' + str(total_horas) + '\n'

            if total_horas > (horas_mensuales_contrato * 1.30):
                if data.permitir_sobrepasar:
                    msg= msg + '\n' + 'Se ha sobrepasado el 30% de horas mensuales para este empleado. \n Total Horas contrato:' +str(horas_mensuales_contrato)+ '\n Horas Asignadas:' + str(total_horas) + '\n'
                else:
                    raise osv.except_osv(_('Error!'),'Se ha sobrepasado el total de horas mensuales para este empleado. \n Total Horas contrato:' +str(horas_mensuales_contrato)+ '\n Horas Asignadas:' + str(total_horas) + '\n NO SE HAN GENERADO TAREAS¡¡¡')

        if len(msg) == 0:
            msg = msg + 'Proceso terminado correctamente \n'
        mess_id = self.pool.get('acp_wizard.message').create(cr, uid, {'text':msg})
        return {'name':_("Information"),
                  'view_mode': 'form',
                  'view_id': False,
                  'view_type': 'form',
                  'res_model': 'acp_wizard.message',
                  'res_id': mess_id,
                  'type': 'ir.actions.act_window',
                  'nodestroy': False,
                  'target': 'new',
                  'domain': '[]',
                  }  

        #return {'type': 'ir.actions.act_window_close'}
    '''        
 

wizard_create_lead()      

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

