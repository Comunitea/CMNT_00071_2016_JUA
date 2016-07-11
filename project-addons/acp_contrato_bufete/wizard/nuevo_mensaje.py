# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import netsvc
from openerp import SUPERUSER_ID
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class acp_contrato_bufete_nuevo_mensaje(osv.osv_memory):
 
    _name = 'acp_contrato_bufete.nuevo_mensaje'
    _description = 'Nuevo mensaje desde portal'
    
    def _get_users(self,cr,uid,context):
        contrato = self.pool.get('acp_contrato.contrato').browse(cr, uid, context.get('active_id'), context=context) 

        L=[]
        for c in contrato.abogado_ids:
            user_id = self.pool.get('res.users').search(cr, uid, [('partner_id','=',c.abogado_id.id)], context=context)
            user = self.pool.get('res.users').browse(cr, uid, user_id[0], context=context)
            L.append((user.id,user.name))
        return L
        

    _columns = {
        'msg': fields.text('Texto', required=True),
        'user_seg_id': fields.selection(_get_users, 'Enviar a', required=True),
    }



    def send_msg(self, cr, uid, ids, context=None):
        
        msg = self.pool.get('acp_contrato_bufete.nuevo_mensaje').browse(cr, uid, ids[0], context=context) 
        servicio_ids = self.pool.get('acp_contrato.servicio').search(cr, uid, [('contrato_id','=',context.get('active_id')),('tipo_servicio','=',2)], context=context)
        servicio=self.pool.get('acp_contrato.servicio').browse(cr, uid, servicio_ids[0], context=context)
        actividad_id = self.pool.get('acp_contrato.actividad').browse(cr, uid, 1, context=context) 
        ir_model_data = self.pool.get('ir.model.data')
        try:
            actividad_id = ir_model_data.get_object_reference(cr, uid, 'acp_contrato_bufete', 'ACT_MENSAJE_DE_CLIENTE')[1]
            actividad = self.pool.get('acp_contrato.actividad').browse(cr, uid, actividad_id, context=context) 
        except ValueError:
            actividad_id = False


        if (context.get('active_model')  == 'acp_contrato.contrato'):

            tarea={
                      'servicio_id': servicio.id,
                      'tipo_servicio': 2,            
                      'contrato_id': context.get('active_id'),
                      'partner_id':servicio.partner_id.id,
                      'user_id': uid,                
                      'fecha': time.strftime('%Y-%m-%d %H:%M:%S'),                
                      'actividad_id': actividad.id,        
                      'tipo': actividad.tipo,
                      'fecha_limite': time.strftime('%Y-%m-%d %H:%M:%S'),
                      'observaciones': msg.msg,
                      'user_seg_id': msg.user_seg_id,      
                      'prioridad': '2',   
                      'state': 'open',
                      'create_note':False
                             }
            tarea_id = self.pool.get('acp_contrato.tarea').create(cr, SUPERUSER_ID, tarea, context=context) 
        return True
acp_contrato_bufete_nuevo_mensaje()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
