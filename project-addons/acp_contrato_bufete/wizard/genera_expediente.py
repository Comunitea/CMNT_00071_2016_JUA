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
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class acp_contrato_genera_expediente(osv.osv_memory):
    """ Genera expediente a partir de otro expediente """

    _name = 'acp_contrato.genera_expediente'
    _description = 'Genera expediente a partir de otro expediente'

    def _get_tipo_contrato(self, cr, uid, *args):
        try:
            proxy = self.pool.get('ir.model.data')
            result = proxy.get_object_reference(cr, uid, 'acp_contrato_bufete', 'subexpediente')
            return result[1]
        except Exception, ex:
            return False


    def onchange_contrato_id(self,cr,uid,ids, contrato_id,context=None):
        contrato_obj = self.pool.get('acp_contrato.contrato')
        contrato = contrato_obj.browse(cr,uid, contrato_id,context=context)
        materia_ids = [x.materia_id.id for x in contrato.contrato_materia_ids]
        print materia_ids
        return {'domain':{'materia_id':[('id',      'in' ,materia_ids)]}}

    _columns = {
        'contrato_id': fields.many2one('acp_contrato.contrato', 'Expediente', required=True),
        'tipo_contrato': fields.many2one('acp_contrato.tipo_contrato', 'Tipo de contrato', select=True,required=True),
        'partner_id': fields.many2one('res.partner', 'Cliente', select=True,required=True),
        'solicitante': fields.many2one('res.partner', 'Solicitante', select=True,required=True),
        'area': fields.selection([
                     ('Judicial','Judicial'),
                     ('Mercantil','Mercantil'),
                      ], 'Área', required=False, select=True),
        'materia_id': fields.many2one('acp_contrato.materia', 'Materia', select=True, required=True),
        'oficina_id': fields.many2one('acp_contrato.oficina', 'Oficina', select=True,required=False),
        'organo_legislativo_id': fields.many2one('acp_contrato.organo_legislativo', 'Organo Legislativo', select=True),
        'fase_judicial_id': fields.many2one('acp_contrato.fase_judicial', 'Fase Judicial', select=True),
    }

    _defaults = {
        'tipo_contrato' : _get_tipo_contrato,
    }

    def action_cancel(self, cr, uid, ids, context=None):
        return {'type':'ir.actions.act_window_close'}



    def action_genera_expediente(self, cr, uid, ids, context=None):
        print '<<<<<<<<<<<<<<<<<  GENERA EXPEDIENTE'
        mod_obj = self.pool.get('ir.model.data')
        mod_hr_employee_obj = self.pool.get('hr.employee')
        mod_partner_obj = self.pool.get('res.partner')
        mod_users_obj = self.pool.get('res.users')

        data = self.read(cr, uid, ids, [], context=context)[0]
        contrato_id = data['contrato_id'][0]
        materia_id = data['materia_id'][0]

        area = ''
        if data['area']:
            area = data['area']

        oficina_id = ''
        if data['oficina_id']:
            oficina_id = data['oficina_id'][0]

        organo_legislativo_id = ''
        if data['organo_legislativo_id']:
            organo_legislativo_id = data['organo_legislativo_id'][0]

        fase_judicial_id = ''
        if data['fase_judicial_id']:
            fase_judicial_id = data['fase_judicial_id'][0]
        if data['solicitante']:
            solicitante_id = data['solicitante'][0]

        contrato_obj = self.pool.get('acp_contrato.contrato')
        contrato_rel_obj = self.pool.get('acp_contrato.contrato_relacionado')
        contrato_ids = contrato_obj.browse(cr,uid,contrato_id,context)
        tipo_contrato_id  = mod_obj.get_object_reference(cr, uid, 'acp_contrato_bufete', 'subexpediente')[1]
        for contrato in contrato_ids:
            #si el usuario que está creando el contrato es un abogado, lo anadimos al expedidnte
            #en la pestaá de abogados
            abogado_id = False
            abogado_rec = []
            #hr_employee = mod_hr_employee_obj.search(cr, uid,[('user_id','=',uid)],context=context)
            #if hr_employee:
            es_abobado = mod_users_obj.browse(cr, uid,uid,context=context).partner_id.abogado
            if es_abobado:
                abogado_id = mod_users_obj.browse(cr, uid,uid,context=context).partner_id.id
            if abogado_id:
                abogado_rec = [(0, 6,  {'abogado_id':abogado_id })]
            #creamos el contrato
            new_contrato_id = contrato_obj.create(cr, uid, {'referencia': contrato.name,
                                                        'partner_id': contrato.partner_id.id,
                                                        'solicitante': solicitante_id,
                                                        'pricelist_id': contrato.pricelist_id.id,
                                                        'partner_direccion_id': contrato.partner_direccion_id.id,
                                                        'partner_factura_id': contrato.partner_factura_id.id,
                                                        'perioricidad':   contrato.perioricidad,
                                                        'tipo_contrato': tipo_contrato_id,
                                                        'fecha': datetime.strptime(fields.datetime.now(), '%Y-%m-%d %H:%M:%S'),
                                                        'area': area,
                                                        'materia_id': materia_id,
                                                        'oficina_id': oficina_id,
                                                        'organo_legislativo_id': organo_legislativo_id,
                                                        'fase_judicial_id': fase_judicial_id,
                                                        'parent_id': contrato_ids.id,
                                                        'abogado_ids': abogado_rec
                                                        }, context=context)


        '''
    def onchange_abogado_id(self, cr, uid, ids, rec_id, context=None):
        if not rec_id:
            return {'value': {'email': False, 'phone': False,  'mobile': False, 'fax': False}}

        part = self.pool.get('res.partner').browse(cr, uid, rec_id, context=context)
        val = {
            'email': part.email,
            'phone': part.phone,
            'mobile': part.mobile,
            'fax': part.fax,
        }
        return {'value': val}

    _columns = {
        'contrato_id': fields.many2one('acp_contrato.contrato', 'Expediente', required=True, ondelete='cascade'),
        'abogado_id': fields.many2one('res.partner', 'Abogado', required=True, change_default=True, select=True),
        'email': fields.related('abogado_id','email', type="char", string="Email") ,
        'phone': fields.related('abogado_id','phone', type="char", string="Teléfono") ,
        'mobile': fields.related('abogado_id','mobile', type="char", string="Movil") ,
        'fax': fields.related('abogado_id','fax', type="char", string="Fax") ,
        '''
        # Abre la pantalla de contratos
        return {
            'type': 'ir.actions.act_window',
            'name': 'acp_contrato.contrato.form',
            'view_type': 'form',
            'view_mode': 'form',
            'context': context,
            'res_model': 'acp_contrato.contrato',
            'nodestroy': True,
            'res_id': new_contrato_id,
            'target':'current',
            }


acp_contrato_genera_expediente()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
