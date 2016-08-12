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
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import SUPERUSER_ID,api
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class acp_contrato_partido_judicial(osv.osv):
    _name = "acp_contrato.partido_judicial"
    _description = "Partidos Judicials"

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.name + ' [' + record.state_id.name +']'
            res.append((record.id, name))
        return res


    _columns = {
        'name': fields.char('Nombre', size=60, required=True,select=True),
        'state_id': fields.many2one('res.country.state', 'Provincia',required=True),
        'descripcion': fields.text('Descripcion'),
    }
    _defaults = {
        'active': 1,
    }
acp_contrato_partido_judicial()


class acp_contrato_materia(osv.osv):
    _name = "acp_contrato.materia"
    _description = "Materias de contratos"
    _columns = {
        'name': fields.char('Nombre', size=60, required=True,select=True),
        'descripcion': fields.text('Descripcion'),
        'active': fields.boolean('Activo', help="Permite ocultar este registro sin eliminarlo."),
    }
    _defaults = {
        'active': 1,
    }
acp_contrato_materia()

class acp_contrato_oficina(osv.osv):
    _name = "acp_contrato.oficina"
    _description = "Oficinas de contratos"
    _columns = {
        'name': fields.char('Nombre', size=60, required=True,select=True),
        'descripcion': fields.text('Descripcion'),
        'active': fields.boolean('Activo', help="Permite ocultar este registro sin eliminarlo."),
    }
    _defaults = {
        'active': 1,
    }
acp_contrato_oficina()

class acp_contrato_organo_legislativo(osv.osv):
    _name = "acp_contrato.organo_legislativo"
    _description = "Organo Legislativo de contratos"
    _columns = {
        'name': fields.char('Nombre', size=60, required=True,select=True),
        'descripcion': fields.text('Descripcion'),
        'active': fields.boolean('Activo', help="Permite ocultar este registro sin eliminarlo."),
    }
    _defaults = {
        'active': 1,
    }
acp_contrato_organo_legislativo()

class acp_contrato_fase_judicial(osv.osv):
    _name = "acp_contrato.fase_judicial"
    _description = "Fases Judiciales de contratos"
    _columns = {

        'name': fields.char('Nombre', size=60, required=True,select=True),
        'descripcion': fields.text('Descripcion'),
        'active': fields.boolean('Activo', help="Permite ocultar este registro sin eliminarlo."),
    }
    _defaults = {
        'active': 1,
    }
acp_contrato_organo_legislativo()


class acp_contrato_contrato(osv.osv):
    _inherit = "acp_contrato.contrato"


    def _progreso(self,cr, uid,ids,fields,arg,context):
        x={}
        for record in self.browse(cr, uid, ids):




            if record.parent_id and record.parent_id.tipo_contrato.name == 'Iguala':
                try:
                    x[record.id] = (record.total_horas_trabajadas / record.total_horas_facturadas) * 100.0
                except ZeroDivisionError:
                    x[record.id] = 100.0
            else:
                record.total_trabajado
                try:
                    x[record.id] = (record.total_trabajado / record.total_facturado) * 100.0
                except ZeroDivisionError:
                    x[record.id] = 100.0
        return x

    def _get_voucher_line_sale(self,cr, uid,ids,fields,arg,context):
        x={}
        for record in self.browse(cr, uid, ids):
            sql='''select account_voucher_line.id from account_voucher_line,account_voucher
                   where account_voucher.id =account_voucher_line.voucher_id
                   and account_voucher.type in ('sale','sale_refund')
                   and account_voucher_line.contrato_id=%s'''%(record.id)

            cr.execute(sql)

            x[record.id] =  map(lambda x: x[0], cr.fetchall())
        return x
    def _get_tarea_lineas(self,cr, uid,ids,fields,arg,context):
        data_pool = self.pool['ir.model.data']
        dummy, tipo_id = data_pool.get_object_reference(cr, uid, 'acp_contrato_bufete', 'act_prof_bufete')
        groups =[g.is_portal for g in self.pool.get('res.users').browse(cr, uid, uid).groups_id]

        usuario_portal = False
        if True in groups:
            usuario_portal = True
        x={}
        for record in self.browse(cr, uid, ids):
            if usuario_portal:
                sql='''select acp_contrato_tarea.id
                   from acp_contrato_tarea, acp_contrato_servicio
                   where acp_contrato_tarea.servicio_id = acp_contrato_servicio.id
                   and acp_contrato_servicio.tipo_servicio = %s
                   and acp_contrato_tarea.contrato_id=%s'''%(tipo_id,record.id)
            else:
                sql='''select acp_contrato_tarea.id
                   from acp_contrato_tarea, acp_contrato_servicio
                   where acp_contrato_tarea.servicio_id = acp_contrato_servicio.id
                   and acp_contrato_tarea.contrato_id=%s'''%(record.id)

            cr.execute(sql)

            x[record.id] =  map(lambda x: x[0], cr.fetchall())
        return x

    def _get_voucher_line_purchase(self,cr, uid,ids,fields,arg,context):
        x={}
        for record in self.browse(cr, uid, ids):
            sql='''select account_voucher_line.id from account_voucher_line,account_voucher
                   where account_voucher.id =account_voucher_line.voucher_id
                   and account_voucher.type in ('purchase','purchase_refund')
                   and account_voucher_line.contrato_id=%s'''%(record.id)

            cr.execute(sql)

            x[record.id] =  map(lambda x: x[0], cr.fetchall())
        return x


    def _total_trabajado(self, cr, uid, ids, field_name, arg, context=None):
        if not ids:
            return {}
        tarea_horas_obj = self.pool.get('acp_contrato.tarea_horas')
        employee_obj = self.pool.get('hr.employee')
        product_obj = self.pool.get('product.product')
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')

        x = dict.fromkeys(ids, 0)
        for record in self.browse(cr, uid, ids):
            tarea_horas_ids = tarea_horas_obj.search(cr, uid, [('contrato_id','=',record.id),('tarea_id.servicio_id.tipo_servicio.id', '=', 2)], context=context)
            tota_trabajado = 0.0
            for tarea_hora in  tarea_horas_obj.browse(cr, uid, tarea_horas_ids, context=context):
                employee_id = employee_obj.search(cr, uid, [('user_id','=',tarea_hora.tarea_id.user_seg_id.id)], limit=1,context=context)

                if employee_id:
                    employee = employee_obj.browse(cr, uid, employee_id[0], context=context)
                    if employee.product_rel_id:
                        ctx=dict(context)
                        ctx.update({'pricelist': record.pricelist_id.id})
                        product = product_obj.browse(cr,uid,employee.product_rel_id.id,context=ctx)
                        try:
                            product.product_tmpl_id.check_access_rule("read")
                        except (osv.except_osv, orm.except_orm):
                            continue
                        try:
                            record.pricelist_id.check_access_rule("read")
                        except (osv.except_osv, orm.except_orm):
                            continue
                        price = product.price
                        #taxes = product.taxes_id
                        #taxes = tax_obj.compute_all(cr, uid, taxes, price, tarea_hora.horas, employee.product_rel_id, record.partner_id)
                        cur = record.pricelist_id.currency_id
                        #price_final = cur_obj.round(cr, uid, cur, taxes['total_included'])
                        price_final = cur_obj.round(cr, uid, cur,tarea_hora.horas*price)
                        tota_trabajado = tota_trabajado + price_final

            x[record.id] = tota_trabajado
        return x
    def _total_coste(self, cr, uid, ids, field_name, arg, context=None):
        if not ids:
            return {}
        tarea_horas_obj = self.pool.get('acp_contrato.tarea_horas')
        employee_obj = self.pool.get('hr.employee')
        product_obj = self.pool.get('product.product')
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')

        x = dict.fromkeys(ids, 0)
        for record in self.browse(cr, uid, ids):
            tarea_horas_ids = tarea_horas_obj.search(cr, uid, [('contrato_id','=',record.id),('tarea_id.servicio_id.tipo_servicio.id', '=', 2)], context=context)
            tota_trabajado = 0.0
            for tarea_hora in  tarea_horas_obj.browse(cr, uid, tarea_horas_ids, context=context):
                employee_id = employee_obj.search(cr, uid, [('user_id','=',tarea_hora.tarea_id.user_seg_id.id)], limit=1,context=context)

                if employee_id:
                    employee = employee_obj.browse(cr, uid, employee_id[0], context=context)
                    if employee.product_rel_id:

                        #ctx=dict(context)
                        #ctx.update({'pricelist': record.pricelist_id.id})
                        product = product_obj.browse(cr,uid,employee.product_rel_id.id,context=context)
                        try:
                            product.product_tmpl_id.check_access_rule("read")
                        except (osv.except_osv, orm.except_orm):
                            continue
                        try:
                            record.pricelist_id.check_access_rule("read")
                        except (osv.except_osv, orm.except_orm):
                            continue
                        price = product.standard_price
                        #taxes = product.supplier_taxes_id
                        #taxes = tax_obj.compute_all(cr, uid, taxes, price, tarea_hora.horas, employee.product_rel_id, record.partner_id)
                        cur = record.pricelist_id.currency_id
                        #price_final = cur_obj.round(cr, uid, cur, taxes['total_included'])
                        price_final = cur_obj.round(cr, uid, cur, product.standard_price * tarea_hora.horas)
                        tota_trabajado = tota_trabajado + price_final

            x[record.id] = tota_trabajado
        return x

    def _total_facturado(self, cr, uid, ids, field_name, arg, context=None):
        if not ids:
            return {}

        x = dict.fromkeys(ids, 0)
        invoice_line_obj = self.pool.get('account.invoice.line')
        cur_obj = self.pool.get('res.currency')
        for record in self.browse(cr, uid, ids):
            tota_trabajado = 0.0
            invoice_line_ids = invoice_line_obj.search(cr,SUPERUSER_ID,['&',('invoice_id.type','in',['out_invoice','out_refund']),('contrato_id','=',record.id)],context=context)

            for invoice_line in invoice_line_obj.browse(cr,SUPERUSER_ID,invoice_line_ids,context=context):

                if invoice_line.invoice_id.state  in ['open','paid']:
                    if invoice_line.product_id and invoice_line.product_id.computar_en_expedientes:
                        cur = invoice_line.invoice_id.currency_id
                        val = val1 = 0.0
                        val1 = invoice_line.price_subtotal
                        #val = sale_order_line.order_id._amount_line_tax( sale_order_line, context=context)
                        total_included = cur_obj.round(cr, uid, cur, val) + cur_obj.round(cr, uid, cur, val1)
                        tota_trabajado = tota_trabajado + total_included

            x[record.id] = tota_trabajado + record.saldo_acumulado
        return x

    def _total_horas_facturadas(self, cr, uid, ids, field_name, arg, context=None):
        if not ids:
            return {}

        x={}
        contrato_obj = self.pool.get('acp_contrato.contrato')
        for record in self.browse(cr, uid, ids):
            if  record.contrato_plantilla:
                horas = 0.0
                for materia in record.contrato_materia_ids:
                    horas = horas + materia.horas
                x[record.id] = horas
            else:
                horas = 0.0
                if record.parent_id and record.parent_id.tipo_contrato.name == 'Iguala':
                    for materia in record.parent_id.contrato_materia_ids:
                        if materia.materia_id.id == record.materia_id.id:
                            horas = horas + materia.horas
                x[record.id] = horas
        return x

    def _total_horas_trabajadas_expediente(self, cr, uid, ids, field_name, arg, context=None):
        if not ids:
            return {}
        tarea_horas_obj = self.pool.get('acp_contrato.tarea_horas')
        employee_obj = self.pool.get('hr.employee')
        product_obj = self.pool.get('product.product')
        x={}
        for record in self.browse(cr, uid, ids):
            if  record.contrato_plantilla:
                x[record.id] = record.total_horas_trabajadas
            else:
                tota_trabajado= 0.0
                if record.parent_id and record.parent_id.tipo_contrato.name == 'Iguala':
                    hoy = (datetime.now()).date()
                    fecha_inicio = record.parent_id.fecha
                    fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d %H:%M:%S').date()
                    fecha_inicio_trimestre = False
                    fecha_fin_trimestre = False
                    for i in range(0,50):
                        fecha_inicio = fecha_inicio
                        fecha_fin = fecha_inicio + relativedelta(months=+3)
                        if (fecha_inicio <= hoy) and (fecha_fin >= hoy):
                            fecha_inicio_trimestre = fecha_inicio
                            fecha_fin_trimestre = fecha_fin
                            break
                        fecha_inicio = fecha_fin
                    if fecha_inicio_trimestre and fecha_fin_trimestre:
                        tarea_horas_ids = tarea_horas_obj.search(cr, uid, [('contrato_id','=',record.id),('fecha','>=',fecha_inicio_trimestre),('fecha','<=',fecha_fin_trimestre)], context=context)
                        tota_trabajado = 0.0
                        for tarea_hora in  tarea_horas_obj.browse(cr, uid, tarea_horas_ids, context=context):
                          tota_trabajado = tota_trabajado + tarea_hora.horas
                x[record.id] = tota_trabajado
        return x

    def _total_horas_trabajadas_totales(self, cr, uid, ids, field_name, arg, context=None):
        if not ids:
            return {}
        x={}
        contrato_obj = self.pool.get('acp_contrato.contrato')
        tarea_horas_obj = self.pool.get('acp_contrato.tarea_horas')
        for record in self.browse(cr, uid, ids):
            if  record.contrato_plantilla:
                horas = 0.0
                hoy = (datetime.now()).date()
                fecha_inicio = record.fecha
                fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d %H:%M:%S').date()
                fecha_inicio_trimestre = False
                fecha_fin_trimestre = False
                for i in range(0,50):
                    fecha_inicio = fecha_inicio
                    fecha_fin = fecha_inicio + relativedelta(months=+3)
                    if (fecha_inicio <= hoy) and (fecha_fin >= hoy):
                        fecha_inicio_trimestre = fecha_inicio
                        fecha_fin_trimestre = fecha_fin
                        break
                    fecha_inicio = fecha_fin
                if fecha_inicio_trimestre and fecha_fin_trimestre:
                    #calculamso el total de horas en este trimestre
                    tarea_horas_ids = tarea_horas_obj.search(cr, uid, [('parent_id','=',record.id),('fecha','>=',fecha_inicio_trimestre),('fecha','<=',fecha_fin_trimestre)], context=context)
                    tota_trabajado = 0.0
                    for tarea_hora in  tarea_horas_obj.browse(cr, uid, tarea_horas_ids, context=context):
                        horas = horas + tarea_hora.horas
                x[record.id] = horas
            else:
                horas = 0.0
                hoy = (datetime.now()).date()
                if record.parent_id and record.parent_id.tipo_contrato.name == 'Iguala':
                    fecha_inicio = record.parent_id.fecha
                    fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d %H:%M:%S').date()
                    fecha_inicio_trimestre = False
                    fecha_fin_trimestre = False
                    for i in range(0,50):
                        fecha_inicio = fecha_inicio
                        fecha_fin = fecha_inicio + relativedelta(months=+3)
                        if (fecha_inicio <= hoy) and (fecha_fin >= hoy):
                            fecha_inicio_trimestre = fecha_inicio
                            fecha_fin_trimestre = fecha_fin
                            break
                        fecha_inicio = fecha_fin
                    if fecha_inicio_trimestre and fecha_fin_trimestre:
                        #calculamso el total de horas en este trimestre
                        tarea_horas_ids = tarea_horas_obj.search(cr, uid, [('contrato_id.materia_id','=',record.materia_id.id),('parent_id','=',record.parent_id.id),('fecha','>=',fecha_inicio_trimestre),('fecha','<=',fecha_fin_trimestre)], context=context)
                        tota_trabajado = 0.0
                        for tarea_hora in  tarea_horas_obj.browse(cr, uid, tarea_horas_ids, context=context):
                            horas = horas + tarea_hora.horas
                x[record.id] = horas
        return x

    def new_tarea_portal(self,cr,uid,ids,context=None):
        '''
        contrato=self.pool.get('acp_contrato.contrato').browse(cr, uid, ids[0], context=context)
        servicio_ids = self.pool.get('acp_contrato.servicio').search(cr, uid, [('contrato_id','=',ids[0]),('tipo_servicio','=',2)], context=context)
        servicio=self.pool.get('acp_contrato.servicio').browse(cr, uid, servicio_ids[0], context=context)
        print 'servicio'
        print servicio
        tarea_obj=self.pool.get('acp_contrato.tarea')
        contrato=servicio.contrato_id
        #Comprobamos que el contrato está abierto
        if servicio.contrato_id.state not in  ['confirmed','exception']:
            raise osv.except_osv(
                        _('No puede realizar acciones en este contrato'),
                        _('El contrato no esta abierto.'))

        #comprobamos que no existe ninguna actividad que bloquee el contrato
        bloqueo_contrato_ids = tarea_obj.search(cr, uid,        [('contrato_id','=',contrato.id),('actividad_id.bloquear_contrato','=',True),('state','=','open')], context=context)
        if len(bloqueo_contrato_ids) > 0:
            raise osv.except_osv(
                        _('No puede realizar acciones en este contrato'),
                        _('Existen actividades que estan bloqueando este contrato, cierre estas actividades antes de continnuar.'))

        #comprobamos que no existe ninguna actividad que bloquee el servicio
        bloqueo_servicio_ids = tarea_obj.search(cr, uid,        [('servicio_id','=',servicio.id),('actividad_id.bloquear_servicio','=',True),('state','=','open')], context=context)
        if len(bloqueo_servicio_ids) > 0:
            raise osv.except_osv(
                        _('No puede realizar acciones en este servicio'),
                        _('Existen actividades que estan bloqueando este servicio, cierre estas actividades antes de continnuar.'))
        '''
        return {
            'type': 'ir.actions.act_window',
            'name': 'Mensaje',
            'view_type': 'form',
            'view_mode': 'form',
            'context': context,
            'res_model': 'acp_contrato_bufete.nuevo_mensaje',
            'nodestroy': True,
            'target':'new',
            }

    _columns = {

        'fecha_cierre': fields.datetime('Fecha Cierre', select=True),
        'area': fields.selection([
                     ('Judicial','Judicial'),
                     ('Mercantil','Mercantil'),
                      ], 'Área', required=False, select=True),
        'materia_id': fields.many2one('acp_contrato.materia', 'Materia', select=True,required=False),
        'horas_estimadas' : fields.float('Horas estimadas', digits_compute= dp.get_precision('Account'), required=False),
        'oficina_id': fields.many2one('acp_contrato.oficina', 'Oficina', select=True,required=False),
        'organo_legislativo_id': fields.many2one('acp_contrato.organo_legislativo', 'Organo jurisdiccional', select=True),
        'fase_judicial_id': fields.many2one('acp_contrato.fase_judicial', 'Fase Judicial', select=True),
        'numero_auto': fields.char('Número Autos', size=60),
        'procurador_ids': fields.one2many('acp_contrato.contrato_procurador', 'contrato_id','Procuradores'),
        'abogado_ids': fields.one2many('acp_contrato.contrato_abogado', 'contrato_id','Abogados'),
        'contrario_ids': fields.one2many('acp_contrato.contrato_contrario', 'contrato_id','Contrarios'),
        'tarea_lineas': fields.function(_get_tarea_lineas,method=True,type='one2many',relation='acp_contrato.tarea', string="Tareas",copy=False),
        'progreso': fields.function(_progreso,method=True,type='float', string="Consumo"),
        'state': fields.selection([
                     ('open','Borrador'),
                     ('confirmed','Vivo'),
                     ('exception','Excepción'),
                     ('cancel','Anulado'),
                     ('done','Arhivado')
                      ], 'Estado', required=True, select=True),
        #'origen_cliente_id' : fields.many2one('acp_yanez.origen_cliente', 'Origen Cliente', help="Origenes de Clientes"),
        'crm_tracking_campaign' : fields.many2one('crm.tracking.campaign', 'Campaign', help="Campañas de Marketing"),
        'nota_interna': fields.text('Nota Interna'),
        'tipo_contrato': fields.many2one('acp_contrato.tipo_contrato', 'Tipo de Expediente', select=True,required=True),
        'name': fields.char('Expediente', size=30, required=True, select=True),
        'partner_direccion_id': fields.many2one('res.partner', 'Dirección del Expediente', select=True,required=True),
        'contrato_materia_ids': fields.one2many('acp_contrato.contrato_materia', 'contrato_id','Materias'),
        'fecha_limite_asignada': fields.date('Fecha limite asiganda'),
        'voucher_line_sale': fields.function(_get_voucher_line_sale,method=True,type='one2many',relation='account.voucher.line', string="Recibos de Ventas",copy=False),
        'voucher_line_purchase': fields.function(_get_voucher_line_purchase,method=True,type='one2many',relation='account.voucher.line', string="Recibos de Compras",copy=False),
        'riesgo_operacional':  fields.float('Riego operacional', digits_compute= dp.get_precision('Account'), required=False),
        'solicitante': fields.many2one('res.partner', 'Solicitante', select=True,required=False),
        'total_horas_facturadas': fields.function(_total_horas_facturadas, digits_compute= dp.get_precision('Account'), string="Horas Facturadas en iguala"),
        'total_horas_trabajadas_expediente': fields.function(_total_horas_trabajadas_expediente,  digits_compute= dp.get_precision('Account'),  string="Horas Trabajadas Expediente (Trimestre)"),
        'total_horas_trabajadas': fields.function(_total_horas_trabajadas_totales,  digits_compute= dp.get_precision('Account'),  string="Horas totales trabajadas (Trimestre)"),
        'total_trabajado': fields.function(_total_trabajado,  digits_compute= dp.get_precision('Account'),  string="Total Trabajado"),
        'total_coste': fields.function(_total_coste,  digits_compute= dp.get_precision('Account'),  string="Total Coste"),
        'total_facturado': fields.function(_total_facturado, digits_compute= dp.get_precision('Account'), string="Total Facturado"),
        'pais_id': fields.many2one('res.country', 'Pais', select=True,required=False),
        'riesgo': fields.selection([
                     ('alto','Alto'),
                     ('probable','Probable'),
                     ('remoto','Remoto'),
                      ], 'Riesgo', required=False, select=True),
        'valor_economico':  fields.float('Valor económico', digits_compute= dp.get_precision('Account'), required=False),
        'costas_tasadas':  fields.float('Costas tasadas (JBI)', digits_compute= dp.get_precision('Account'), required=False),
        'fecha_archivo': fields.date('Fecha archivo'),
        'originales_custodia': fields.boolean('Originales en custodia'),
        'custodia_version_firmada': fields.boolean('Custodia versión firmada'),
        'expediente_fisico': fields.boolean('Expediente fisico'),
        'recobrado': fields.char('Recobrado'),
        'autos': fields.char('Autos'),
        'ultimo_estado': fields.char('Último estado'),
        }

    _defaults = {
        'contrato_plantilla': False
    }
    def wkf_action_confirmed(self, cr, uid, ids, context=None):
        #enviamo correo electronico
        mail_ids = []
        data_pool = self.pool['ir.model.data']
        mailmess_pool = self.pool['mail.message']
        mail_pool = self.pool['mail.mail']
        template_pool = self.pool['email.template']
        contrato_obj = self.pool.get('acp_contrato.contrato')
        dummy, template_id = data_pool.get_object_reference(cr, uid, 'acp_contrato_bufete', 'acp_email_template_aviso_abogado')
        for contrato in contrato_obj.browse(cr,uid, ids, context=context):

            for abogado in contrato.abogado_ids:










                mail_id = template_pool.send_mail(cr, uid, template_id, abogado.id, context=context)
                mail_ids.append(mail_id)

        if mail_ids:
            res = mail_pool.send(cr, uid, mail_ids, context=context)


















        return super(acp_contrato_contrato, self).wkf_action_confirmed(cr, uid, ids, context=context)
    def wkf_action_done(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        res = super(acp_contrato_contrato, self).wkf_action_done(cr, uid, ids, context=context)
        email_template_obj = self.pool.get('email.template')
        partner_obj = self.pool.get('res.partner')

        #enviar email a cliente
        if 1==1:

            ir_model_data = self.pool.get('ir.model.data')
            try:
                template_id = ir_model_data.get_object_reference(cr, uid, 'acp_contrato_bufete', 'acp_email_template_aviso_cierre_cliente')[1]
            except ValueError:
                template_id = False
            try:
                compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
            except ValueError:
                compose_form_id = False

            part = self.browse(cr, uid, ids[0], context=context).partner_id
            if template_id:

                values = email_template_obj.generate_email(cr, uid, template_id, ids[0], context=context)
                values['res_id'] = ids[0]
                values['partner_ids'] = [part.id]
                values['notified_partner_ids'] = [part.id]
                values['email_to'] = part.email
                values['notification'] = True
                mail_mail_obj = self.pool.get('mail.mail')
                msg_id = mail_mail_obj.create(cr, uid, values, context=context)
                if msg_id:
                    mail_mail_obj.send(cr, uid, [msg_id], context=context)

        #enviar email a administracion
        if 1==1:

            ir_model_data = self.pool.get('ir.model.data')
            try:
                template_id = ir_model_data.get_object_reference(cr, uid, 'acp_contrato_bufete', 'acp_email_template_aviso_cierre_administracion')[1]
            except ValueError:
                template_id = False
            try:
                compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
            except ValueError:
                compose_form_id = False

            #part = self.browse(cr, uid, ids[0], context=context).partner_id


            if template_id:

                values = email_template_obj.generate_email(cr, uid, template_id, ids[0], context=context)
                values['res_id'] = ids[0]
                #values['partner_ids'] = [part.id]
                #values['notified_partner_ids'] = [part.id]
                #values['email_to'] = part.email
                values['notification'] = True
                mail_mail_obj = self.pool.get('mail.mail')
                msg_id = mail_mail_obj.create(cr, uid, values, context=context)
                if msg_id:
                    mail_mail_obj.send(cr, uid, [msg_id], context=context)
        return res


    def create(self, cr, uid, vals, context=None):
        new_id = super(acp_contrato_contrato, self).create(cr, uid, vals, context=context)
        #Creamos por defecto el servicio
        serv = {}
        if new_id:
            tipo_servicio_ids = self.pool.get('acp_contrato.tipo_servicio').search(cr, uid,[('name','in',['Gestiones Administrativas','Actuaciones Profesionales'])], context=context)
            for serv in tipo_servicio_ids:
                tipo_servicio = self.pool.get('acp_contrato.tipo_servicio').browse(cr, uid, serv)
                serv = {
                    'contrato_id': new_id,
                    'fecha': vals['fecha'],
                    'partner_id': vals['partner_id'],
                    'partner_direccion_id': vals['partner_direccion_id'],
                    'partner_factura_id': vals['partner_factura_id'],
                    'tipo_servicio' : tipo_servicio.id,
                    'state' : 'open',
                    }
                serv_id = self.pool.get('acp_contrato.servicio').create(cr, uid, serv, context=context)

        return new_id
    '''
    def action_xxx(self, cr, uid, ids, context=None):
        inv = self.pool.get('account.invoice')
        for i in range (1,501):
            numero =  self.pool.get('ir.sequence').get_id(cr, uid, 84,'id',context=context)


            vals={
            'internal_number':numero,
            'number':numero,
            'invoice_number':numero,
            'partner_id':1,
            'account_id':443,
            'type':'out_invoice',
            'journal_id':2,
            'currency_id':1
            }
            inv.create(cr, uid, vals,context=context)
    '''

    def action_crear_expediente(self, cr, uid, ids, context=None):

        ctx = dict()
        tipo_contrato = False
        try:
            proxy = self.pool.get('ir.model.data')
            result = proxy.get_object_reference(cr, uid, 'acp_contrato_bufete', 'subexpediente')
            tipo_contrato =result[1]
        except Exception, ex:
            tipo_contrato = False

        ctx.update({
            'default_solicitante': self.browse(cr, uid, ids).partner_id.id,
            'default_contrato_id': self.browse(cr, uid, ids).id,
            'default_tipo_contrato': tipo_contrato,
            'default_partner_id':self.browse(cr, uid, ids).partner_id.id,
        })

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'acp_contrato.genera_expediente',
            'target': 'new',
            'context': ctx,
        }

    def new_voucher_sale(self,cr,uid,ids,context=None):
        mod_obj = self.pool.get('ir.model.data')
        if context is None:
            context = {}
        res = mod_obj.get_object_reference(cr, uid, 'account_voucher', 'view_sale_receipt_form')
        res_id = res and res[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'name': 'Recibos de Ventas',
            'view_type': 'form',
            'view_mode': 'form',
            'context': "{'default_type': 'sale', 'type': 'sale'}",
            'res_model': 'account.voucher',
            'nodestroy': True,
            'target':'current',
            'view_id': [res_id],
            }

    def new_voucher_purchase(self,cr,uid,ids,context=None):
        mod_obj = self.pool.get('ir.model.data')
        if context is None:
            context = {}
        res = mod_obj.get_object_reference(cr, uid, 'account_voucher', 'view_purchase_receipt_form')
        res_id = res and res[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'name': 'Recibos de Compras',
            'view_type': 'form',
            'view_mode': 'form',
            'context': "{'default_type': 'purchase', 'type': 'purchase'}",
            'res_model': 'account.voucher',
            'nodestroy': True,
            'target':'current',
            'view_id': [res_id],
            }

acp_contrato_contrato()

class acp_contrato_contrato_procurador(osv.osv):
    _name = "acp_contrato.contrato_procurador"
    _description = "Procuradores de los contratos"
    _inherit = ['mail.thread']
    def action_procurador_send(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'acp_contrato_bufete', 'acp_email_template_aviso_procurador')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'acp_contrato.contrato_procurador',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def onchange_procurador_id(self, cr, uid, ids, rec_id, context=None):
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
        'procurador_id': fields.many2one('res.partner', 'Procurador', required=True, change_default=True, select=True),
        'email': fields.related('procurador_id','email', type="char", string="Email") ,
        'phone': fields.related('procurador_id','phone', type="char", string="Teléfono") ,
        'mobile': fields.related('procurador_id','mobile', type="char", string="Movil") ,
        'fax': fields.related('procurador_id','fax', type="char", string="Fax") ,
        'partidos_judiciales': fields.related('procurador_id','partidos_judiciales', type="many2many",relation='acp_contrato.partido_judicial', string="Partidos Judiciales") ,

    }

    def create(self, cr, uid, vals, context=None):
        email_template_obj = self.pool.get('email.template')
        partner_obj = self.pool.get('res.partner')
        if context is None:
            context = {}
        new_id = super(acp_contrato_contrato_procurador, self).create(cr, uid, vals, context=context)
        if vals.get('procurador_id', False):



            ir_model_data = self.pool.get('ir.model.data')
            try:
                template_id = ir_model_data.get_object_reference(cr, uid, 'acp_contrato_bufete', 'acp_email_template_aviso_procurador')[1]
            except ValueError:
                template_id = False
            try:
                compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
            except ValueError:
                compose_form_id = False



            if template_id:



                values = email_template_obj.generate_email(cr, uid, template_id, new_id, context=context)
                values['res_id'] = new_id
                values['partner_ids'] = [vals.get('procurador_id', False)]
                values['notified_partner_ids'] = [vals.get('procurador_id', False)]
                values['email_to'] = self.pool.get('res.partner').browse(cr, uid, vals.get('procurador_id', False), context=context).email
                values['notification'] = True
                mail_mail_obj = self.pool.get('mail.mail')
                msg_id = mail_mail_obj.create(cr, uid, values, context=context)
                if msg_id:
                    mail_mail_obj.send(cr, uid, [msg_id], context=context)


        return new_id



acp_contrato_contrato_procurador()


class acp_contrato_contrato_contratio(osv.osv):
    _name = "acp_contrato.contrato_contrario"
    _description = "Contrarios de los contratos"

    def onchange_procurador_id(self, cr, uid, ids, rec_id, context=None):
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
        'name': fields.char( 'Nombre',size=120),
        'contrato_id': fields.many2one('acp_contrato.contrato', 'Expediente', required=True, ondelete='cascade'),
        'email': fields.char( 'Email',size=120),
        'phone': fields.char( 'Telefono',size=20),
        'mobile': fields.char( 'Movil',size=20),
        'fax': fields.char( 'Fax',size=20),
    }

acp_contrato_contrato_contratio()

class acp_contrato_contrato_abogado(osv.osv):
    _name = "acp_contrato.contrato_abogado"
    _description = "Abogados de los contratos"
    _inherit = ['mail.thread']
    def action_abogado_send(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'acp_contrato_bufete', 'acp_email_template_aviso_abogado')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'acp_contrato.contrato_procurador',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

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
    }


    def create(self, cr, uid, vals, context=None):
        email_template_obj = self.pool.get('email.template')
        partner_obj = self.pool.get('res.partner')
        if context is None:
            context = {}
        new_id = super(acp_contrato_contrato_abogado, self).create(cr, uid, vals, context=context)
        if vals.get('abogado_id', False):



            ir_model_data = self.pool.get('ir.model.data')
            try:
                template_id = ir_model_data.get_object_reference(cr, uid, 'acp_contrato_bufete', 'acp_email_template_aviso_abogado')[1]
            except ValueError:
                template_id = False
            try:
                compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
            except ValueError:
                compose_form_id = False



            if template_id:



                values = email_template_obj.generate_email(cr, uid, template_id, new_id, context=context)
                values['res_id'] = new_id
                values['partner_ids'] = [vals.get('abogado_id', False)]
                values['notified_partner_ids'] = [vals.get('abogado_id', False)]
                values['email_to'] = self.pool.get('res.partner').browse(cr, uid, vals.get('abogado_id', False), context=context).email
                values['notification'] = True
                mail_mail_obj = self.pool.get('mail.mail')
                msg_id = mail_mail_obj.create(cr, uid, values, context=context)
                if msg_id:
                    mail_mail_obj.send(cr, uid, [msg_id], context=context)


        return new_id

acp_contrato_contrato_abogado()


class acp_contrato_tarea(osv.osv):
    _inherit = "acp_contrato.tarea"

    def _horas(self, cr, uid, ids, field_name, arg, context=None):
        if not ids:
            return {}

        x={}
        for record in self.browse(cr, uid, ids):
            try:
                sql='''select sum(horas)
                                from acp_contrato_tarea,acp_contrato_tarea_horas
                                where acp_contrato_tarea_horas.tarea_id = acp_contrato_tarea.id
                                and acp_contrato_tarea.id = %s '''%(record.id)

                cr.execute(sql)
                x[record.id] = cr.fetchall()[0][0] or 0.0
            except TypeError:
                 x[record.id] = 0
        return x

    _columns = {
        'resultado': fields.text('Resultado'),
        'riesgo_operacional':  fields.float('Riego operacional', digits_compute= dp.get_precision('Account'), required=False),
        'seguimiento': fields.selection([
                     ('pendiente','Pendiente de factura'),
                     ('recibida','Factura recibida'),
                      ], 'Seguimiento'),
        'tiempo_tarea': fields.function(_horas,  digits_compute= dp.get_precision('Account'),  string="Horas trabajadas"),
        'contrato_id': fields.related(
                              'servicio_id',
                              'contrato_id',
                              type="many2one",
                              relation="acp_contrato.contrato",
                              string="Expediente",
                              required=False,
                              store=True) ,
    }


    def create(self, cr, uid, vals, context=None):


        servicio_id = vals['servicio_id']

        actividad=self.pool.get('acp_contrato.actividad').browse(cr, uid, vals['actividad_id'], context=context)
        servicio=self.pool.get('acp_contrato.servicio').browse(cr, uid, servicio_id, context=context)
        contrato=servicio.contrato_id

        if contrato.parent_id and contrato.parent_id.tipo_contrato.name == 'Iguala':
            act_prof_bufete = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'acp_contrato_bufete', 'act_prof_bufete')
            if (contrato.total_horas_trabajadas > contrato.total_horas_facturadas) and (servicio.tipo_servicio.id == act_prof_bufete[1]):
                raise osv.except_osv(
                        _('Error'),
                        _('Se ha excedido el importe acordado para este expediente.'))
        else:
            act_prof_bufete = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'acp_contrato_bufete', 'act_prof_bufete')
            if (contrato.total_trabajado > contrato.total_facturado) and (servicio.tipo_servicio.id == act_prof_bufete[1]):
                raise osv.except_osv(
                        _('Error'),
                        _('Se ha excedido el importe acordado para este expediente.'))


        return super(acp_contrato_tarea, self).create(cr, uid, vals, context=context)


    def close_seg(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'seguimiento': 'recibida'}, context=context)
acp_contrato_tarea()

class acp_contrato_servicio(osv.osv):
    _inherit = "acp_contrato.servicio"

    def get_name_bufete_(self, cr, uid, ids, field_name, arg, context):

        if not ids:
            return {}
        res = {}

        servicios = self.browse(cr, uid, ids, context)
        for servicio in servicios:
            name =   servicio.contrato_id.name + '/' + str(servicio.numero_servicio)
            res[servicio.id] = name
        return res

    _columns = {
        'contrato_id': fields.many2one('acp_contrato.contrato', 'Expediente', select=True,required=True,ondelete='cascade',change_default=True),
        'name': fields.function(get_name_bufete_, method=True, string='Name',type='char' ),
        'operario_ids': fields.one2many('acp_contrato.servicio_operario', 'servicio_id','Operarios'),
    }

acp_contrato_servicio()

class acp_contrato_contrato_producto(osv.osv):
    _inherit = "acp_contrato.contrato_producto"

    _columns = {
        'contrato_id': fields.many2one('acp_contrato.contrato', 'Expediente', required=True, ondelete='cascade'),
    }
acp_contrato_contrato_producto()

class acp_contrato_servicio_producto(osv.osv):
    _inherit = "acp_contrato.servicio_producto"

    _columns = {
        'contrato_id': fields.related('servicio_id','contrato_id',type="many2one",relation="acp_contrato.contrato",string="Expediente",required=False,store=True) ,

    }
acp_contrato_servicio_producto()

class acp_contrato_facturacion(osv.osv):
    _inherit = "acp_contrato.facturacion"

    _columns = {
        'contrato_id': fields.many2one('acp_contrato.contrato', 'Expediente', required=True, ondelete='cascade'),
    }

class acp_contrato_contrato_materia(osv.osv):
    _name = "acp_contrato.contrato_materia"
    _description = "Materias de expedientes de iguala"

    _columns = {
        'contrato_id': fields.many2one('acp_contrato.contrato', 'Expediente', required=True, ondelete='cascade'),
        'materia_id': fields.many2one('acp_contrato.materia', 'Materia', select=True, required=True),
        'horas': fields.float('Horas', digits_compute= dp.get_precision('Product UoS'), required=True, change_default=True),
    }
acp_contrato_facturacion()



class acp_contrato_mail_pop(osv.osv):
    """ CRM Lead Case """
    _inherit = "acp_contrato.mail_pop"



    def get_receipt_id(self, cr, uid,contrato_id ,servicio_id, context=None):
        contrato = self.pool.get('acp_contrato.contrato').browse(cr, uid, contrato_id, context=context)
        if contrato.abogado_ids:
            abobado = contrato.abogado_ids[0]
            user_id = self.pool.get('res.users').search(cr, uid, [('partner_id','=',abobado.abogado_id.id)])
            if len(user_id) > 0:
                return user_id[0]
            else:
                return SUPERUSER_ID
        else:
            return SUPERUSER_ID
acp_contrato_mail_pop()












# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
