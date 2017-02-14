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
from openerp import tools,SUPERUSER_ID,api
import HTMLParser
import html2text
class acp_contrato_tipo_producto(osv.osv):
    _name = "acp_contrato.tipo_producto"
    _description = "Tipos de producto"
    _columns = {

        'name': fields.char('Nombre', size=60, required=True,select=True),
        'descripcion': fields.text('Descripcion'),
        'active': fields.boolean('Activo', help="Permite ocultar este registro sin eliminarlo."),
    }
    _defaults = {
        'active': 1,
    }

    _sql_constraints = [
        ('unique_tipo_producto', 'unique(name)', 'Tipo de producto debe ser unico !'),

    ]

acp_contrato_tipo_producto()


class acp_contrato_tipo_contrato(osv.osv):
    _name = "acp_contrato.tipo_contrato"
    _description = "Tipos de contrato"
    _columns = {

        'name': fields.char('Nombre', size=60, required=True,select=True),
        'descripcion': fields.text('Descripcion'),
        'active': fields.boolean('Activo', help="Permite ocultar este registro sin eliminarlo."),
    }
    _defaults = {
        'active': 1,
    }
acp_contrato_tipo_contrato()


class acp_contrato_tipo_servicio(osv.osv):
    _name = "acp_contrato.tipo_servicio"
    _description = "Tipos de servicio"
    _columns = {

        'name': fields.char('Nombre', size=60, required=True,select=True),
        'descripcion': fields.text('Descripcion'),
        'copia_materiales': fields.boolean('Copiar lista de materiales', help="Si está activo se copiará la lista de materiales del contrato al crear este tipo de servicio."),
        'recibir_mail': fields.boolean('Recibir email', help="Si está activo este servicio se usará para crear las tareas de emails recibidos (Solo un servicio debe tener este campo activo)"),
        'actividad_inicial_id': fields.many2one('acp_contrato.actividad', 'Actividad', required=False, ondelete='restrict',help="Tarea inicial que se creará cuando cree un servicio de este tipo"),
        'user_seg_id': fields.many2one('res.users', 'Asignar a', required=False, ondelete='restrict',help="Usuario al que se asignará la tarea"),
        'copiar_descripcion': fields.boolean('Copiar descripcion a la tarea', help="Copia la descripcion del servicio a la tarea que se crea."),
        'active': fields.boolean('Activo', help="Permite ocultar este registro sin eliminarlo."),
    }
    _defaults = {
        'active': 1,
    }
acp_contrato_tipo_contrato()


class acp_contrato_actividad(osv.osv):
    _name = "acp_contrato.actividad"
    _description = "Tipos de Actividades"
    _columns = {

        'code': fields.char('Código', size=60, required=True,select=True),
        'name': fields.char('Descripcion', size=150, required=True,select=True),
        'estado_inicial': fields.selection([
                     ('open','Abierto'),
                     ('done','Cerrado'),
                      ], 'Estado Inicial de la Actividad', required=True, select=True),
        'tipo': fields.selection([
                     ('anular','Anular'),
                     ('finalizar','Finalizar'),
                     ('reabrir','Re-Abrir'),
                     ('reclamacion','Reclamacion'),
                     ('espera','Espera'),
                     ('cita','Cita'),
                     ('contacto','Contacto'),
                     ('mail_recibido','email recibido'),
                     ('enviar_mail','Enviar email'),
                     ('material','Material'),
                     ('otro','Otro'),
                      ], 'Tipo de actividad', required=True, select=True),
        'tipo_servicio': fields.many2one('acp_contrato.tipo_servicio', 'Tipo Servicio', select=True,required=False,help="Si se configura un tipo de servicio, esta actividad estará solo disponible para este tipo de servicio."),
        'horas': fields.integer('Horas límite para el cierre', select=True, help="Pasadas estas horas desde la fecha de creación de la actividad, se mostrará un aviso en el contrato/servicio."),
        'bloquear_servicio': fields.boolean('Bloquear Servicio', select=True, help="Si está marcado, esta actividad bloquará el servicio, impidiendo que se creen actividades nuevas hasta que se finalice esta"),
        'bloquear_contrato': fields.boolean('Bloquear Contrato', select=True, help="Si está marcado, esta actividad bloquará el contrato, impidiendo que se creen actividades nuevas hasta que se finalice esta"),
        'especial_atencion': fields.boolean('Especial Atención', select=True, help="Si está marcado, esta actividad se mostrará en el cuadro 'Especial Atención' del contrato hasta que se finalice."),
        'enviar_mensaje': fields.boolean('Enviame un mensaje cuando se finalize la actividad',  help="Enviará un mensaje al cerrarse la actividad a la persona que creó la actividad( siempre que la persona que tiene asignada la actividad sea diferente de la persona que creó la actividad"),
        'cerrar_automaticamente': fields.boolean('Cerrar automáticamente', select=True, help="Si está activo, se cerrará la actividad automáticamente en el momento de crear una nueva actividad en el servicio( este parámtro no afecta si la actividad esta marcada para bloquear contrato o servicio)"),
        'mostrar_en_resumen': fields.boolean('Mostrar en Resumen', select=True, help="Si está marcado, esta actividad se mostrará en el resumen de actividades"),
        'active': fields.boolean('Activo', help="Permite ocultar este registro sin eliminarlo."),
        'prioridad': fields.selection([
                     ('3','Baja'),
                     ('2','Media'),
                     ('1','Alta'),
                      ], 'Prioridad por defecto', required=True),
        'producto_lineas': fields.one2many('acp_contrato.actividad_producto', 'actividad_id', 'Materiales-Mano de Obra de la Tarea'),
        'alarm_ids': fields.many2many('acp_contrato.alarm', 'acp_contrato_activiada_rel', string='Recordatorios', ondelete="restrict", help="Recordatorios por defecto para esta actividad"),
    }
    _order='name'
    _defaults = {
        'active': 1,
        'prioridad':'2'
    }
acp_contrato_actividad()



class acp_contrato_actividad_producto(osv.osv):
    _name = "acp_contrato.actividad_producto"
    _description = "Productos asociados a actividades"

    _columns = {
        'actividad_id': fields.many2one('acp_contrato.actividad', 'Actividad', required=True, ondelete='cascade'),
        'product_id': fields.many2one('product.product', 'Producto', required=True, change_default=True, select=True),
        'cantidad': fields.float('Cantidad', digits_compute= dp.get_precision('Product UoS'), required=True  ),
        'invoice_state': fields.selection([
                     ('noaplicable','No Aplicable'),
                     ('parafacturar','Para Facturar'),
                     ('facturado','Facturado')
            ], 'Estado Factura', required=True, select=True),
    }

    _defaults = {
        'invoice_state':'noaplicable',
    }
acp_contrato_actividad_producto()



class acp_contrato_motivo_anulacion(osv.osv):
    _name = "acp_contrato.motivo_anulacion"
    _description = "Tipos de motivo de anulacion"
    _columns = {

        'name': fields.char('Nombre', size=60, required=True,select=True),
        'descripcion': fields.text('Descripcion'),
        'active': fields.boolean('Activo', help="Permite ocultar este registro sin eliminarlo."),
    }
    _defaults = {
        'active': 1,
    }
acp_contrato_motivo_anulacion()

class acp_contrato_mail_pop(osv.osv):
    """ CRM Lead Case """
    _name = "acp_contrato.mail_pop"
    _description = "emails recibidos"
    _inherit = ['mail.thread', 'ir.needaction_mixin']




    _columns = {
        'partner_id': fields.many2one('res.partner', 'Contacto', ondelete='set null', track_visibility='onchange',
            select=True),

        #'id': fields.integer('ID', readonly=True),
        'name': fields.char('Asunto', required=False, select=1),
        'email_from': fields.char('Remitente', size=128, help="Email address of the contact", select=1),
        'create_date': fields.datetime('Fecha', readonly=False),
        'email_cc': fields.char('CC', help="These email addresses will be added to the CC field of all inbound and outbound emails for this record before being sent. Separate multiple email addresses with a comma"),
        'description': fields.html('Mensaje'),
        'contrato_id': fields.many2one('acp_contrato.contrato', 'Contrato', required=False, ondelete='cascade'),

    }

    _order='create_date desc'

    #sobr escribir este metod para obtener un destinatario diferente
    def get_receipt_id(self, cr, uid,contrato_id ,servicio_id, context=None):
        return SUPERUSER_ID


    def create(self, cr, uid, vals, context=None):
        if vals['name']:
            contrato_id = self.pool.get('acp_contrato.contrato').search(cr, uid, [('name','ilike',vals['name'])])
            if not contrato_id:
                name_split = []
                name_split2 = []
                name_split = vals['name'].split(' ')

                for name in name_split:
                    for nam2 in name.split(':'):
                        name_split2.append  (nam2)

                for name in name_split2:
                    if name[:3].upper() == 'EXP' and len(name) > 10:
                        contrato_id = self.pool.get('acp_contrato.contrato').search(cr, uid, [('name','=',name.upper())])
                        if contrato_id:
                            break;


            if len(contrato_id) > 0:
                vals['contrato_id'] = contrato_id[0]
                res = super(acp_contrato_mail_pop, self).create(cr, uid, vals, context=context)
                #buscamos el servicio donde asignar la tarea
                servicio_id = self.pool.get('acp_contrato.servicio').search(cr, uid, [('contrato_id','=',contrato_id[0]),('recibir_mail','=',True)])
                if len(servicio_id) > 0:
                    try:
                        servicio_id = servicio_id[0]
                        servicio = self.pool.get('acp_contrato.servicio').browse(cr, uid, servicio_id, context=context)
                        contrato = self.pool.get('acp_contrato.contrato').browse(cr, uid, contrato_id[0], context=context)
                        ir_model_data = self.pool.get('ir.model.data')
                        try:
                            actividad_id = ir_model_data.get_object_reference(cr, uid, 'acp_contrato', 'EMAIL_RECIBIDO')[1]
                        except ValueError:
                            actividad_id = False
                        h = HTMLParser.HTMLParser()
                        y = html2text.HTML2Text()
                        y.ignore_images = True
                        y.strong_mark = ''
                        y.emphasis_mark = ''
                        tarea={
                            'servicio_id': servicio_id,
                            'tipo_servicio': servicio.tipo_servicio.id,
                            'partner_id': servicio.contrato_id.partner_id.id,
                            'contrato_id': contrato_id[0],
                            'mail_pop_id': res,
                            'user_id': SUPERUSER_ID,
                            'fecha': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'actividad_id': actividad_id,
                            'tipo': 'mail_recibido',
                            'fecha_limite': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'observaciones': y.handle(h.unescape(vals['description'])),
                            'user_seg_id': self.get_receipt_id(cr, uid, contrato_id[0] ,servicio_id,context=context),
                            'prioridad': '2',
                            'state': 'open',
                            'create_note':False
                             }
                        tarea_id = self.pool.get('acp_contrato.tarea').create(cr, uid, tarea, context=context)
                        return res
                    except:
                         return res
        return super(acp_contrato_mail_pop, self).create(cr, uid, vals, context=context)

    def on_change_partner_id(self, cr, uid, ids, partner_id, context=None):
        values = {}
        if partner_id:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
            values = {
                'partner_name': partner.parent_id.name if partner.parent_id else partner.name,
                'contact_name': partner.name if partner.parent_id else False,
                'title': partner.title and partner.title.id or False,
                'street': partner.street,
                'street2': partner.street2,
                'city': partner.city,
                'state_id': partner.state_id and partner.state_id.id or False,
                'country_id': partner.country_id and partner.country_id.id or False,
                'email_from': partner.email,
                'phone': partner.phone,
                'mobile': partner.mobile,
                'fax': partner.fax,
                'zip': partner.zip,
                'function': partner.function,
            }
        return {'value': values}
    def message_new(self, cr, uid, msg, custom_values=None, context=None):
        """ Overrides mail_thread message_new that is called by the mailgateway
            through message_process.
            This override updates the document according to the email.
        """

        if custom_values is None:
            custom_values = {}
        defaults = {
            'name':  msg.get('subject') or _("No Subject"),
            'description':  msg.get('body') or _("No Body"),
            'email_from': msg.get('from'),
            'email_cc': msg.get('cc'),
            'partner_id': msg.get('author_id', False),
            'user_id': False,
        }
        if msg.get('author_id'):
            defaults.update(self.on_change_partner_id(cr, uid, None, msg.get('author_id'), context=context)['value'])
        defaults.update(custom_values)
        return super(acp_contrato_mail_pop, self).message_new(cr, uid, msg, custom_values=defaults, context=context)


    def message_update(self, cr, uid, ids, msg, update_vals=None, context=None):
        """ Overrides mail_thread message_update that is called by the mailgateway
            through message_process.
            This method updates the document according to the email.
        """
        return self.message_new(cr, uid, msg, custom_values=None, context=context)


class acp_contrato_motivo_espera(osv.osv):
    _name = "acp_contrato.motivo_espera"
    _description = "Tipos de motivo_espera"
    _columns = {

        'name': fields.char('Nombre', size=60, required=True,select=True),
        'descripcion': fields.text('Descripcion'),
        'fecha_limite': fields.boolean('Mostrar Aviso?'),
        'horas': fields.integer('Horas'),
        'active': fields.boolean('Activo', help="Permite ocultar este registro sin eliminarlo."),
     }
    _defaults = {
        'active': 1,
    }
acp_contrato_motivo_espera()


class acp_contrato_resolucion(osv.osv):
    _name = "acp_contrato.resolucion"
    _description = "Tipos de resolucion"
    _columns = {

        'name': fields.char('Nombre', size=60, required=True,select=True),
        'descripcion': fields.char('Descripcion', size=150),
        'active': fields.boolean('Activo', help="Permite ocultar este registro sin eliminarlo."),
    }
    _defaults = {
        'active': 1,
    }
acp_contrato_resolucion()

class acp_contrato_motivo_reclamacion(osv.osv):
    _name = "acp_contrato.motivo_reclamacion"
    _description = "Tipos de motivo reclamacion"
    _columns = {

        'name': fields.char('Nombre', size=60, required=True,select=True),
        'descripcion': fields.char('Descripcion', size=150),
        'active': fields.boolean('Activo', help="Permite ocultar este registro sin eliminarlo."),
    }
    _defaults = {
        'active': 1,
    }
acp_contrato_motivo_reclamacion()

class acp_contrato_contrato(osv.osv):
    _name = "acp_contrato.contrato"
    _description = "Contrato"
    _inherit = ['mail.thread']

    def action_contrato_send(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'acp_contrato', 'acp_contrato_email_template')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'acp_contrato.contrato',
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

    def onchange_partner_id(self, cr, uid, ids, part, context=None):

        if not part:
             return {'value': {'partner_direccion_id': False, 'partner_factura_id': False, 'pricelist_id': False}}

        part = self.pool.get('res.partner').browse(cr, uid, part, context=context)
        addr = self.pool.get('res.partner').address_get(cr, uid, [part.id], [ 'invoice','delivery'])
        val = {
            'partner_factura_id': addr['invoice'],
            'partner_direccion_id': addr['delivery'],
        }
        pricelist = part.property_product_pricelist and part.property_product_pricelist.id or False
        if pricelist:
            val['pricelist_id'] = pricelist


        return {'value': val}



    def _get_inv_lines_out(self,cr, uid,ids,fields,arg,context):
        x={}
        company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
        for record in self.browse(cr, uid, ids):
            sql='''select account_invoice_line.id from account_invoice_line,account_invoice
                   where account_invoice.id =account_invoice_line.invoice_id
                   and account_invoice.type in ('out_invoice')
                   and account_invoice_line.contrato_id=%s
                   and account_invoice.company_id=%s''' % (record.id, company_id)

            cr.execute(sql)

            x[record.id] =  map(lambda x: x[0], cr.fetchall())
        return x
    def _get_inv_lines_out_refund(self,cr, uid,ids,fields,arg,context):
        x={}
        company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
        for record in self.browse(cr, uid, ids):
            sql='''select account_invoice_line.id from account_invoice_line,account_invoice
                   where account_invoice.id =account_invoice_line.invoice_id
                   and account_invoice.type in ('out_refund')
                   and account_invoice_line.contrato_id=%s
                   and account_invoice.company_id=%s''' % (record.id, company_id)

            cr.execute(sql)

            x[record.id] =  map(lambda x: x[0], cr.fetchall())
        return x
    def _get_inv_lines_in(self,cr, uid,ids,fields,arg,context):
        x={}
        company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
        for record in self.browse(cr, uid, ids):
            sql='''select account_invoice_line.id from account_invoice_line,account_invoice
                   where account_invoice.id =account_invoice_line.invoice_id
                   and account_invoice.type in ('in_invoice')
                   and account_invoice_line.contrato_id=%s
                   and account_invoice.company_id=%s''' % (record.id, company_id)
            cr.execute(sql)

            x[record.id] =  map(lambda x: x[0], cr.fetchall())
        return x
    def _get_inv_lines_in_refund(self,cr, uid,ids,fields,arg,context):
        x={}
        company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
        for record in self.browse(cr, uid, ids):
            sql='''select account_invoice_line.id from account_invoice_line,account_invoice
                   where account_invoice.id =account_invoice_line.invoice_id
                   and account_invoice.type in ('in_refund')
                   and account_invoice_line.contrato_id=%s
                   and account_invoice.company_id=%s''' % (record.id, company_id)

            cr.execute(sql)

            x[record.id] =  map(lambda x: x[0], cr.fetchall())
        return x
    def  _get_total_out_refund(self,cr, uid,ids,fields,arg,context):
        res = {}
        for record in self.browse(cr, uid, ids, context):
            total = 0.0
            for l in record.invoice_line_out:

                total += l.price_subtotal
            for l in record.invoice_line_out_refund:
                total -= l.price_subtotal
            res[record.id] = total
        return res
    def  _get_total_in_refund(self,cr, uid,ids,fields,arg,context):
        res = {}
        for record in self.browse(cr, uid, ids, context):
            total = 0.0
            for l in record.invoice_line_in:
                total += l.price_subtotal
            for l in record.invoice_line_in_refund:
                total -= l.price_subtotal
            res[record.id] = total
        return res
    def _get_resumen_lineas(self,cr, uid,ids,fields,arg,context):
        x={}
        for record in self.browse(cr, uid, ids):
            sql='''select acp_contrato_tarea.id from acp_contrato_tarea,acp_contrato_servicio
                   where acp_contrato_servicio.contrato_id =%s
                   and acp_contrato_servicio.id=acp_contrato_tarea.servicio_id
                   and acp_contrato_tarea.mostrar_en_resumen=True'''%(record.id)

            cr.execute(sql)

            x[record.id] =  map(lambda x: x[0], cr.fetchall())
        return x
    def _get_especial_atencion_lineas(self,cr, uid,ids,fields,arg,context):
        x={}
        for record in self.browse(cr, uid, ids):
            sql='''select acp_contrato_tarea.id from acp_contrato_tarea,acp_contrato_servicio
                   where acp_contrato_servicio.contrato_id =%s
                   and acp_contrato_servicio.id=acp_contrato_tarea.servicio_id
                   and acp_contrato_tarea.especial_atencion=True and acp_contrato_tarea.state='open' '''%(record.id)

            cr.execute(sql)

            x[record.id] =  map(lambda x: x[0], cr.fetchall())

        return x
    def _get_hours_next_act(self,cr, uid,ids,fields,arg,context):
        x={}
        for record in self.browse(cr, uid, ids):
            sql='''select (extract(epoch from inter)/3600)::integer
            from (select (coalesce(min(fecha_limite),'2222-06-16 00:00:00')- now() at time zone 'UTC') as inter
            from acp_contrato_tarea where state = 'open' and contrato_id= %s) x'''%(record.id)

            cr.execute(sql)
            x[record.id] = cr.fetchall()[0][0]
        return x
    def _get_name_referencia(self,cr, uid,ids,fields,arg,context):
        x={}
        for record in self.browse(cr, uid, ids):
            x[record.id] = record.name + "-" +record.referencia
        return x
    def _attachment_count(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x,0), ids))

        for c in self.browse(cr, uid, ids, context):
            res[c.id] = len(self.pool.get('ir.attachment').search(cr, uid, [('contrato_id','=',ids[0])]))
        return res

    def _get_attachment_ids(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x,0), ids))

        for c in self.browse(cr, uid, ids, context):
            res[c.id] = self.pool.get('ir.attachment').search(cr, uid, [('contrato_id','=',ids[0])])
        return res


    def _total_horas_hoy(self, cr, uid, ids, field_name, arg, context=None):

        if not ids:
            return {}

        x = dict.fromkeys(ids, 0)
        for record in self.browse(cr, uid, ids):
            try:
                sql='''select sum(horas)
                       from acp_contrato_tarea,acp_contrato_tarea_horas
                       where acp_contrato_tarea_horas.tarea_id = acp_contrato_tarea.id
                       and acp_contrato_tarea.user_seg_id =%s
                       and acp_contrato_tarea_horas.fecha = current_date '''%(uid)

                cr.execute(sql)
                x[record.id] = cr.fetchall()[0][0] or 0.0
            except TypeError:
                 x[record.id] = 0
        return x

    def _total_horas_objetivo(self, cr, uid, ids, field_name, arg, context=None):

        if not ids:
            return {}

        x = dict.fromkeys(ids, 0)

        for record in self.browse(cr, uid, ids):
            try:

                sql='''select horas_objetivo
                       from hr_employee
                       where resource_id =(select id from resource_resource where user_id=%s limit 1)
                        '''%(uid)

                cr.execute(sql)

                x[record.id] = cr.fetchall()[0][0] or 0.0
            except IndexError:
                 x[record.id] = 0
        return x
    def _entiempo(self, cr, uid, ids, field_name, arg, context=None):
        if not ids:
            return {}

        x = dict.fromkeys(ids, 0)
        for record in self.browse(cr, uid, ids):
            try:
                if record.total_horas_hoy >= record.total_horas_objetivo:
                    x[record.id] = 1
                else:
                    x[record.id] = 0
            except ZeroDivisionError:
                    x[record.id] = 0


        return x


    _columns = {
        'company_id': fields.many2one('res.company', 'Campañia', required=True,select=True),
        'name': fields.char('Número', size=30, required=True, select=True,copy=False),
        'name_referencia': fields.function(_get_name_referencia,method=True,type='char', string="Nombre"),
        'parent_id': fields.many2one('acp_contrato.contrato', 'Contrato relacionado', select=True,required=False),
        'child_ids': fields.one2many('acp_contrato.contrato','parent_id', 'Contrato relacionados', required=False),
        'sale_id': fields.many2one('sale.order', 'Pedido que generó el expediente', required=False,copy=False),
        'pricelist_id': fields.many2one('product.pricelist', 'Tarifa', required=True, readonly=False,  help="Tarifa."),
        'contrato_plantilla': fields.boolean('Plantilla', help="Contrato tipo plantilla"),
        'currency_id': fields.related('pricelist_id', 'currency_id', type="many2one", relation="res.currency", string="Currency", readonly=True, required=True),
        'referencia': fields.char('Referencia', size=120, required=True, select=True,copy=False),
        'state': fields.selection([
                     ('open','Borrador'),
                     ('confirmed','Confirmado'),
                     ('exception','Excepción'),
                     ('cancel','Anulado'),
                     ('done','Finalizdo')
                      ], 'Estado', required=True, select=True),

        'partner_id': fields.many2one('res.partner', 'Cliente', select=True,required=True),
        'partner_direccion_id': fields.many2one('res.partner', 'Dirección del contato', select=True,required=True),
        'partner_factura_id': fields.many2one('res.partner', 'Dirección de factura', select=True,required=True),
        'tipo_contrato': fields.many2one('acp_contrato.tipo_contrato', 'Tipo de contrato', select=True,required=True),
        'fecha': fields.datetime('Fecha de alta', required=True, select=True,copy=False),
        'baja': fields.boolean('Dado de Baja'  ),
        'fecha_baja': fields.date('Fecha Baja'  ),
        'motivo_baja': fields.text('Motivo Baja', ),
        'user_id': fields.many2one('res.users', 'Responsable', select=True,required=True),
        'contrato_lineas': fields.one2many('acp_contrato.servicio', 'contrato_id', 'Servicios'),
        'tarea_lineas': fields.one2many('acp_contrato.tarea', 'contrato_id', 'Tareas',copy=False),
        'resumen_lineas': fields.function(_get_resumen_lineas,method=True,type='one2many',relation='acp_contrato.tarea', string="Resumen",copy=False),
        'especial_atencion_lineas': fields.function(_get_especial_atencion_lineas,method=True,type='one2many',relation='acp_contrato.tarea', string="Resumen",copy=False),
        'invoice_line_out': fields.function(_get_inv_lines_out,method=True,type='one2many',relation='account.invoice.line', string="Facturas de Salida",copy=False),
        'invoice_line_out_refund': fields.function(_get_inv_lines_out_refund,method=True,type='one2many',relation='account.invoice.line', string="Facturas Rectificativas",copy=False),
        'invoice_line_in': fields.function(_get_inv_lines_in,method=True,type='one2many',relation='account.invoice.line', string="Facturas de Entrada",copy=False),
        'invoice_line_in_refund': fields.function(_get_inv_lines_in_refund,method=True,type='one2many',relation='account.invoice.line', string="Facturas Rectificativas",copy=False),
        'total_out_refund': fields.function(_get_total_out_refund,method=True,type='float', string="Total Ingreso"),
        'total_in_refund': fields.function(_get_total_in_refund,method=True,type='float', string="Total Gasto"),
        'sale_order_line': fields.one2many('sale.order.line', 'contrato_id', 'Presupuestos Venta',copy=False),
        'purchase_order_lineas': fields.one2many('purchase.order.line', 'contrato_id', 'Presupuestos Compra',copy=False),
        'hours_next_act': fields.function(_get_hours_next_act,method=True,type='integer', string="Horas Proxima Tarea"),
        'perioricidad': fields.selection([
                     ('unica','Única'),
                     ('semanal','Semanal'),
                     ('quincenal','Quincenal'),
                     ('mensual','Mensual'),
                     ('trimestral','Trimestral'),
                     ('semestral','Semestral'),
                     ('anual','Anual')
                      ], 'Periodicidad',  select=True),
        'observaciones': fields.text('Descripción'),
        'facturacion_lineas': fields.one2many('acp_contrato.facturacion', 'contrato_id', 'Facturacion',copy=True),
        'programar_servicio_lineas': fields.one2many('acp_contrato.programar_servicio', 'contrato_id', 'Servicios Programados'),
        'producto_lineas': fields.one2many('acp_contrato.contrato_producto', 'contrato_id', 'Materiales del Contrato'),
        'producto_servicio_lineas': fields.one2many('acp_contrato.servicio_producto', 'contrato_id', 'Materiales del Contrato',copy=False),
        'cliente_servicio': fields.boolean('Utilizar cliente de servicio', help="El cliente utilizado para la facturación será el indicado a nivel de servicio./ Este campo se utiliza para contratos genericos"),
        'attachment_ids': fields.function(_get_attachment_ids, string='Documentos', type='one2many',  relation='ir.attachment',copy=False),
        'attachment_count': fields.function(_attachment_count, string='# Documentos', type='integer'),
        'entiempo': fields.function(_entiempo,  type='integer',  string="en tiempo"),
        'total_horas_hoy': fields.function(_total_horas_hoy,  digits_compute= dp.get_precision('Account'),  string="Horas trabajadas hoy"),
        'total_horas_objetivo': fields.function(_total_horas_objetivo,  digits_compute= dp.get_precision('Account'),  string="Horas objetivo"),
        'total_horas_hoy2': fields.function(_total_horas_hoy,  digits_compute= dp.get_precision('Account'),  string="Horas trabajadas hoy"),
        'total_horas_objetivo2': fields.function(_total_horas_objetivo,  digits_compute= dp.get_precision('Account'),  string="Horas objetivo"),
        'emails': fields.one2many('acp_contrato.mail_pop', 'contrato_id', 'Buzón de entrada'),
        'horas_acumuladas':  fields.float('Horas acumuladas', digits=(16,2), required=False,help="Este campo se sumará a las horas trabajadas. \n Este campo se usa para expedientes/contratos importados de sistemas antiguos"  ),
        'saldo_acumulado':  fields.float('Saldo acumulado', digits_compute= dp.get_precision('Account'), required=False,help="Este campo se sumará a las horas trabajadas. \n Este campo se usa para expedientes/contratos importados de sistemas antiguos"  ),
        'recurso_ids': fields.many2many('res.users', 'acp_contrato_res_users_rel', string='Recursos', ondelete="restrict", copy=False),

        }

    '''
        'fechas_mantenimiento_line': fields.one2many('acp_supra.fecha_mantenimiento', 'contrato_id', 'Fechas Mantenimientos'),
        'conceptos_mantenimiento_line': fields.one2many('acp_supra.conceptos_mantenimiento', 'contrato_id', 'Conceptos a Facturar'),
    '''


    _defaults = {
        'fecha': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'state': 'open',
        'user_id': lambda obj, cr, uid, context: uid,
        'company_id': lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, [uid], context)[0].company_id.id,
        'cliente_servicio' : False,
        'name': '/',
        'referencia': '/',
    }
    _sql_constraints = [
        ('unique_contratos', 'unique(company_id,name,partner_id)', 'Contrato duplicado !'),

    ]
    _order='fecha desc'

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.get('name', '/') == '/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'acp_contrato.contrato') or '/'
        return super(acp_contrato_contrato, self).create(cr, uid, vals, context=context)

    def new_tarea_portal(self,cr,uid,ids,context=None):
        #programar
        return True

    def new_servicio(self,cr,uid,ids,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Servicios',
            'view_type': 'form',
            'view_mode': 'form',
            'context': context,
            'res_model': 'acp_contrato.servicio',
            'nodestroy': True,
            'target':'current',
            }
    def new_so(self,cr,uid,ids,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pedido de Venta',
            'view_type': 'form',
            'view_mode': 'form',
            'context': context,
            'res_model': 'sale.order',
            'nodestroy': True,
            'target':'current',
            }
    def new_po(self,cr,uid,ids,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pedido de Compra',
            'view_type': 'form',
            'view_mode': 'form',
            'context': context,
            'res_model': 'purchase.order',
            'nodestroy': True,
            'target':'current',
            }

    def new_inv_out(self,cr,uid,ids,context=None):
        mod_obj = self.pool.get('ir.model.data')
        if context is None:
            context = {}
        res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
        res_id = res and res[1] or False,
        context.update({'type': 'out_invoice'})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Facturas de Cliente',
            'view_type': 'form',
            'view_mode': 'form',
            'context': context,
            'res_model': 'account.invoice',
            'nodestroy': True,
            'target':'current',
            'view_id': [res_id],
            }
    def new_inv_out_refund(self,cr,uid,ids,context=None):
        mod_obj = self.pool.get('ir.model.data')
        if context is None:
            context = {}
        res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
        res_id = res and res[1] or False,
        context.update({'type': 'out_refund'})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Facturas de Cliente',
            'view_type': 'form',
            'view_mode': 'form',
            'context': context,
            'res_model': 'account.invoice',
            'nodestroy': True,
            'target':'current',
            'view_id': [res_id],
            }
    def new_inv_in(self,cr,uid,ids,context=None):
        mod_obj = self.pool.get('ir.model.data')
        if context is None:
            context = {}
        res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_supplier_form')
        res_id = res and res[1] or False,
        context.update({'type':'in_invoice'})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Facturas de Proveedores',
            'view_type': 'form',
            'view_mode': 'form',
            'context': context,
            'res_model': 'account.invoice',
            'nodestroy': True,
            'target':'current',
            'view_id': [res_id],
            }
    def new_inv_in_refund(self,cr,uid,ids,context=None):
        mod_obj = self.pool.get('ir.model.data')
        if context is None:
            context = {}
        res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_supplier_form')
        res_id = res and res[1] or False,
        context.update({'type':'in_refund'})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Facturas Rectificativa',
            'view_type': 'form',
            'view_mode': 'form',
            'context': context,
            'res_model': 'account.invoice',
            'nodestroy': True,
            'target':'current',
            'view_id': [res_id],
            }


    def open_map(self, cr, uid, ids, context=None):
        address_obj= self.pool.get('acp_contrato.contrato')
        exp = address_obj.browse(cr, uid, ids, context=context)[0]
        url="http://maps.google.com/maps?oi=map&q="
        if exp.street:
            url+=exp.street.replace(' ','+')
        if exp.city:
            url+='+'+exp.city.replace(' ','+')
        if exp.state_id:
            url+='+'+exp.state_id.name.replace(' ','+')
        if exp.country_id:
            url+='+'+exp.country_id.name.replace(' ','+')
        if exp.zip:
            url+='+'+exp.zip.replace(' ','+')
        return {
        'type': 'ir.actions.act_url',
        'url':url,
        'target': 'new'
        }
    def onchange_zip_id(self, cursor, uid, ids, zip_id, context=None):
        if not zip_id:
            return {}
        if isinstance(zip_id, list):
            zip_id = zip_id[0]
        bzip = self.pool['res.better.zip'].browse(cursor, uid, zip_id, context=context)
        return {'value': {'zip': bzip.name,
                          'city': bzip.city,
                          'country_id': bzip.country_id.id if bzip.country_id else False,
                          'state_id': bzip.state_id.id if bzip.state_id else False,
                          }
                }

    def onchange_state(self, cr, uid, ids, state_id, context=None):
        if state_id:
            country_id = self.pool.get('res.country.state').browse(cr, uid, state_id, context).country_id.id
            return {'value':{'country_id':country_id}}
        return {}


    def wkf_action_confirmed(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'confirmed'}, context=context)
        return True
    def wkf_action_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'done'}, context=context)
        return True

    def wkf_action_exception(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'exception'}, context=context)
        return True
    def wkf_action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
        return True

    def wkf_start(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'open'})
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_create(uid, 'acp_contrato.contrato', ids[0], cr)
        return True
    def wkf_set_confirmed(self, cr, uid, ids, context=None):

        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'acp_contrato.contrato', ids[0], 'set_confirmed', cr)
        return True

    def wkf_set_done(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'acp_contrato.contrato', ids[0], 'set_done', cr)
        return True



    def wkf_set_exception(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'acp_contrato.contrato', ids[0], 'set_exception', cr)
        return True
    def wkf_set_ignore_exception(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")


        tareas_ids = self.pool.get('acp_contrato.tarea').search(cr, uid, [('contrato_id','=',ids[0]),('especial_atencion','=',True),('state','=','open')], context=context)
        for tareas_id in tareas_ids:
            self.pool.get('acp_contrato.tarea').browse(cr, uid, tareas_id, context).close_act()


        wf_service.trg_validate(uid, 'acp_contrato.contrato', ids[0], 'set_ignore_exception', cr)
        return True
    def wkf_set_reopen_done(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'acp_contrato.contrato', ids[0], 'set_reopen_done', cr)
        return True
    def wkf_set_cancel(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'acp_contrato.contrato', ids[0], 'set_cancel', cr)
        return True
acp_contrato_contrato()

class acp_contrato_servicio(osv.osv):
    _name = "acp_contrato.servicio"
    _description = "Servicios de Contratos"
    _inherit = ['mail.thread']

    def get_partner_id(self, cr, uid, ids, field_name, context):
        if not ids:
            return {}
        res = {}

        servicios = self.browse(cr, uid, ids, context)
        for servicio in servicios:

            if servicio.contrato_id.cliente_servicio:
                if field_name == 'partner_id':
                    res[servicio.id] = servicio.partner_id.id
                if field_name == 'partner_direccion_id' :
                    res[servicio.id] = servicio.partner_direccion_id.id
                if field_name == 'partner_factura_id' :
                    res[servicio.id] = servicio.partner_factura_id.id
            else:
                if field_name == 'partner_id':
                    res[servicio.id] = servicio.contrato_id.partner_id.id
                if field_name == 'partner_direccion_id' :
                    res[servicio.id] = servicio.contrato_id.partner_direccion_id.id
                if field_name == 'partner_factura_id' :
                    res[servicio.id] = servicio.contrato_id.partner_factura_id.id
        return res



    def get_name_(self, cr, uid, ids, field_name, arg, context):

        if not ids:
            return {}
        res = {}

        servicios = self.browse(cr, uid, ids, context)
        for servicio in servicios:
            name =   servicio.tipo_servicio.name + '/' + str(servicio.numero_servicio)
            if servicio.referencia != '/':
                name = name + '/' + servicio.referencia
            res[servicio.id] = name

        return res
    def _get_inv_lines_out(self,cr, uid,ids,fields,arg,context):
        x={}
        for record in self.browse(cr, uid, ids):
            sql='''select account_invoice_line.id from account_invoice_line,account_invoice
                   where account_invoice.id =account_invoice_line.invoice_id
                   and account_invoice.type in ('out_invoice')
                   and account_invoice_line.servicio_id=%s'''%(record.id)

            cr.execute(sql)

            x[record.id] =  map(lambda x: x[0], cr.fetchall())
        return x
    def _get_inv_lines_out_refund(self,cr, uid,ids,fields,arg,context):
        x={}
        for record in self.browse(cr, uid, ids):
            sql='''select account_invoice_line.id from account_invoice_line,account_invoice
                   where account_invoice.id =account_invoice_line.invoice_id
                   and account_invoice.type in ('out_refund')
                   and account_invoice_line.servicio_id=%s'''%(record.id)

            cr.execute(sql)

            x[record.id] =  map(lambda x: x[0], cr.fetchall())
        return x
    def _get_inv_lines_in(self,cr, uid,ids,fields,arg,context):
        x={}
        for record in self.browse(cr, uid, ids):
            sql='''select account_invoice_line.id from account_invoice_line,account_invoice
                   where account_invoice.id =account_invoice_line.invoice_id
                   and account_invoice.type in ('in_invoice')
                   and account_invoice_line.servicio_id=%s'''%(record.id)

            cr.execute(sql)

            x[record.id] =  map(lambda x: x[0], cr.fetchall())
        return x
    def _get_inv_lines_in_refund(self,cr, uid,ids,fields,arg,context):
        x={}
        for record in self.browse(cr, uid, ids):
            sql='''select account_invoice_line.id from account_invoice_line,account_invoice
                   where account_invoice.id =account_invoice_line.invoice_id
                   and account_invoice.type in ('in_refund')
                   and account_invoice_line.servicio_id=%s'''%(record.id)

            cr.execute(sql)

            x[record.id] =  map(lambda x: x[0], cr.fetchall())
        return x
    def  _get_total_out_refund(self,cr, uid,ids,fields,arg,context):
        res = {}
        for record in self.browse(cr, uid, ids, context):
            total = 0.0
            for l in record.invoice_line_out:
                total += l.price_subtotal
            for l in record.invoice_line_out_refund:
                total -= l.price_subtotal
            res[record.id] = total
        return res
    def  _get_total_in_refund(self,cr, uid,ids,fields,arg,context):
        res = {}
        for record in self.browse(cr, uid, ids, context):
            total = 0.0
            for l in record.invoice_line_in:
                total += l.price_subtotal
            for l in record.invoice_line_in_refund:
                total -= l.price_subtotal
            res[record.id] = total
        return res

    def open_servicio(self,cr,uid,ids,context=None):

        if context is None:
            context = {}
        return {
            'type': 'ir.actions.act_window',
            'name': 'Servicio',
            'view_type': 'form',
            'view_mode': 'form',
            'context': context,
            'res_model': 'acp_contrato.servicio',
            'nodestroy': True,
            'res_id': ids[0],
            'target':'current',
            }
    def new_inv_out(self,cr,uid,ids,context=None):
        mod_obj = self.pool.get('ir.model.data')
        if context is None:
            context = {}
        res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
        res_id = res and res[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'name': 'Facturas de Cliente',
            'view_type': 'form',
            'view_mode': 'form',
            'context': "{'type':'out_invoice'}",
            'res_model': 'account.invoice',
            'nodestroy': True,
            'target':'current',
            'view_id': [res_id],
            }
    def new_inv_out_refund(self,cr,uid,ids,context=None):
        mod_obj = self.pool.get('ir.model.data')
        if context is None:
            context = {}
        res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
        res_id = res and res[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'name': 'Facturas Rectificativa',
            'view_type': 'form',
            'view_mode': 'form',
            'context': "{'type':'out_refund'}",
            'res_model': 'account.invoice',
            'nodestroy': True,
            'target':'current',
            'view_id': [res_id],
            }
    def new_inv_in(self,cr,uid,ids,context=None):
        mod_obj = self.pool.get('ir.model.data')
        if context is None:
            context = {}
        res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_supplier_form')
        res_id = res and res[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'name': 'Facturas de Proveedores',
            'view_type': 'form',
            'view_mode': 'form',
            'context': "{'type':'in_invoice'}",
            'res_model': 'account.invoice',
            'nodestroy': True,
            'target':'current',
            'view_id': [res_id],
            }
    def new_inv_in_refund(self,cr,uid,ids,context=None):
        mod_obj = self.pool.get('ir.model.data')
        if context is None:
            context = {}
        res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_supplier_form')
        res_id = res and res[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'name': 'Facturas Rectificativa',
            'view_type': 'form',
            'view_mode': 'form',
            'context': "{'type':'in_refund'}",
            'res_model': 'account.invoice',
            'nodestroy': True,
            'target':'current',
            'view_id': [res_id],
            }
    def new_tarea(self,cr,uid,ids,context=None):

        servicio=self.pool.get('acp_contrato.servicio').browse(cr, uid, ids[0], context=context)
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

        return {
            'type': 'ir.actions.act_window',
            'name': 'Tarea',
            'view_type': 'form',
            'view_mode': 'form',
            'context': {'default_contrato_id':contrato.id,'default_partner_id':servicio.partner_id.id},
            'res_model': 'acp_contrato.tarea',
            'nodestroy': True,
            'target':'current',
            }


    def _get_hours_next_act(self,cr, uid,ids,fields,arg,context):
        x={}
        for record in self.browse(cr, uid, ids):
            sql='''select (extract(epoch from inter)/3600)::integer
            from (select (coalesce(min(fecha_limite),'2222-06-16 00:00:00')- now() at time zone 'UTC') as inter
            from acp_contrato_tarea where state = 'open' and servicio_id= %s) x'''%(record.id)

            cr.execute(sql)
            x[record.id] = cr.fetchall()[0][0]
        return x

    def onchange_partner_id(self, cr, uid, ids, part, context=None):

        if not part:
             return {'value': {'partner_direccion_id': False, 'partner_factura_id': False}}

        part = self.pool.get('res.partner').browse(cr, uid, part, context=context)
        addr = self.pool.get('res.partner').address_get(cr, uid, [part.id], [ 'invoice','delivery'])

        val = {
            'partner_factura_id': addr['invoice'],
            'partner_direccion_id': addr['delivery'],
        }
        return {'value': val}


    def get_default_partner_id(self, cr, uid, ids, contrato_id, partner_id, partner_direccion_id, partner_factura_id, context=None):

        if not contrato_id:
            val = {
                'partner_id': partner_id,
                'partner_direccion_id':partner_direccion_id,
                'partner_factura_id': partner_factura_id,
            }
        else:
            contrato = self.pool.get('acp_contrato.contrato').browse(cr, uid, contrato_id, context=context)
            if not contrato.cliente_servicio:
                val = {
                    'partner_id': contrato.partner_id.id,
                    'partner_direccion_id': contrato.partner_direccion_id.id,
                    'partner_factura_id': contrato.partner_factura_id.id,
                    'cliente_servicio': contrato.cliente_servicio,
                }
            else:
                val = {
                    'partner_id': partner_id,
                    'partner_direccion_id':partner_direccion_id,
                    'partner_factura_id': partner_factura_id,
                    'cliente_servicio': contrato.cliente_servicio,
                }

        return {'value': val}

    def _get_producto_tarea(self,cr, uid,ids,fields,arg,context):
        x={}
        for record in self.browse(cr, uid, ids):
            sql='''select acp_contrato_tarea_producto.id
                   from acp_contrato_tarea,acp_contrato_tarea_producto
                   where acp_contrato_tarea.id = acp_contrato_tarea_producto.tarea_id
                   and acp_contrato_tarea.servicio_id=%s'''%(record.id)

            cr.execute(sql)

            x[record.id] =  map(lambda x: x[0], cr.fetchall())
        return x

    def _get_horas_estimadas(self,cr, uid,ids,fields,arg,context):
        x={}
        for servicio in self.browse(cr, uid, ids):
            total_horas = 0.0
            for tarea in servicio.tarea_lineas:
                for hora in tarea.horas_lineas:
                    total_horas += hora.horas
            x[servicio.id] =  total_horas
        return x

    def _progreso(self,cr, uid,ids,fields,arg,context):
        x={}
        for record in self.browse(cr, uid, ids):


            try:
                x[record.id] = (record.horas_reales / record.horas_estimadas) * 100.0
            except ZeroDivisionError:
                x[record.id] = 100.0
        return x

    _columns = {
        'contrato_id': fields.many2one('acp_contrato.contrato', 'Contrato', select=True,required=True,ondelete='cascade',change_default=True),
        'numero_servicio': fields.char('Numero Servicio', required=True, select=True),
        'referencia': fields.char('Referencia', size=120, required=True, select=True,copy=False),
        'fecha': fields.datetime('Fecha', required=True, select=True),
        'user_id': fields.many2one('res.users', 'Usuario', select=True,required=True),
        'tipo_servicio': fields.many2one('acp_contrato.tipo_servicio', 'Tipo Servicio', select=True,required=True),
        'recurso_ids': fields.one2many('acp_contrato.servicio_recurso', 'servicio_id','Recursos'),
        'observaciones': fields.text('Observaciones'),
        'state': fields.selection([
                     ('open','Abierto'),
                     ('cancel','Anulado'),
                     ('done','Finalizado')
            ], 'Estado', required=True, select=True),
        'invoice_state': fields.selection([
                     ('noaplicable','No Aplicable'),
                     ('parafacturar','Para Facturar'),
                     ('facturado','Facturado')
            ], 'Estado Factura', required=True, select=True),
        'tarea_lineas': fields.one2many('acp_contrato.tarea', 'servicio_id', 'Tareas'),
        'cliente_servicio': fields.related('contrato_id', 'cliente_servicio', type="boolean", string="Cliente Servicio"),
        'partner_id': fields.many2one('res.partner', 'Cliente', select=True, required=True),
        'partner_direccion_id': fields.many2one('res.partner', 'Dirección del contato', select=True, required=True),
        'partner_factura_id': fields.many2one('res.partner', 'Dirección de factura', select=True, required=True),
        'name': fields.function(get_name_, method=True, string='Name',type='char' ),
        'invoice_line_out': fields.function(_get_inv_lines_out,method=True,type='one2many',relation='account.invoice.line', string="Facturas de Salida"),
        'invoice_line_out_refund': fields.function(_get_inv_lines_out_refund,method=True,type='one2many',relation='account.invoice.line', string="Facturas Rectificativas"),
        'invoice_line_in': fields.function(_get_inv_lines_in,method=True,type='one2many',relation='account.invoice.line', string="Facturas de Entrada"),
        'invoice_line_in_refund': fields.function(_get_inv_lines_in_refund,method=True,type='one2many',relation='account.invoice.line', string="Facturas Rectificativas"),
        'total_out_refund': fields.function(_get_total_out_refund,method=True,type='float', string="Total Ingreso"),
        'total_in_refund': fields.function(_get_total_in_refund,method=True,type='float', string="Total Gasto"),
        'sale_order_line': fields.one2many('sale.order.line', 'servicio_id', 'Presupuestos Venta'),
        'purchase_order_line': fields.one2many('purchase.order.line', 'servicio_id', 'Presupuestos Compra'),
        'hours_next_act': fields.function(_get_hours_next_act,method=True,type='integer', string="Horas Proxima Actividad"),
        'afacturar': fields.float('A Facturar', digits_compute= dp.get_precision('Account'), required=False  ),
        'producto_lineas': fields.one2many('acp_contrato.servicio_producto', 'servicio_id', 'Materiales del Servicio'),
        'recibir_mail': fields.related(
                              'tipo_servicio',
                              'recibir_mail',
                              type="boolean",
                              string="Recibir emails",
                              required=False,
                              store=False,
                              help="Si está activo este servicio se usará para crear las tareas de emails recibidos (Solo un servicio debe tener este campo activo)") ,
        #'producto_extra_lineas': fields.one2many('acp_contrato.servicio_producto_extra', 'servicio_id', 'Materiales Extra del Servicio'),
        'servicio_prog_id': fields.many2one('acp_contrato.programar_servicio', 'Servicio Programado', readonly=False,required=False),
        'producto_tarea_lineas': fields.function(_get_producto_tarea,method=True,type='one2many',relation='acp_contrato.tarea_producto', string="Productos Tareas"),
        'horas_estimadas': fields.float('Horas estimadas', required=False  ),
        'horas_facturables': fields.float('Horas facturables',  required=False  ),
        'horas_reales': fields.function(_get_horas_estimadas,method=True,type='float',  string="Horas reales"),
        'progreso': fields.function(_progreso,method=True,type='float', string="Progreso"),
    }
    _defaults = {
        'fecha': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': lambda obj, cr, uid, context: uid,
        'state' : 'open',
        'invoice_state':'noaplicable',
        'numero_servicio' : '/',
        'referencia':'/'
    }
    _order='fecha desc'
    def new_so(self,cr,uid,ids,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pedido de Venta',
            'view_type': 'form',
            'view_mode': 'form',
            'context': context,
            'res_model': 'sale.order',
            'nodestroy': True,
            'target':'current',
            }

    def new_po(self,cr,uid,ids,context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pedido de Compra',
            'view_type': 'form',
            'view_mode': 'form',
            'context': context,
            'res_model': 'purchase.order',
            'nodestroy': True,
            'target':'current',
            }
    def create(self, cr, uid, vals, context=None):

        if vals.get('numero_servicio', '/') == '/':
            vals['numero_servicio'] = self.pool.get('ir.sequence').get(cr, uid, 'acp_contrato.contrato_servicio') or '/'


        tipo_servicio_obj =  self.pool.get('acp_contrato.tipo_servicio')
        servicio_obj =  self.pool.get('acp_contrato.servicio')
        contrato_obj =  self.pool.get('acp_contrato.contrato')
        contrato_rec = contrato_obj.browse(cr, uid, vals['contrato_id'], context=context)
        #si no esta configurado para introducir el cliente en el servicio
        #se toman los datos del contrato
        if not contrato_rec.cliente_servicio:
            vals['partner_id'] = contrato_rec.partner_id.id
            vals['partner_direccion_id'] = contrato_rec.partner_direccion_id.id
            vals['partner_factura_id'] = contrato_rec.partner_factura_id.id

        res = super(acp_contrato_servicio, self).create(cr, uid, vals, context=context)
        servicio_rec = servicio_obj.browse(cr, uid, res, context=context)
        tipo_servicio_rec = tipo_servicio_obj.browse(cr, uid, vals['tipo_servicio'], context=context)


        if  vals['tipo_servicio']:
            if tipo_servicio_rec.copia_materiales:
                #copiamos la lista de materiales en el servicio
                servicio_producto_obj = self.pool.get('acp_contrato.servicio_producto')
                if 'servicio_prog_id' in vals and vals['servicio_prog_id']:
                    producto_contrato_ids = self.pool.get('acp_contrato.contrato_producto').search(cr, uid, [('contrato_id','=',vals['contrato_id']),('programar_servicio_id','=',vals['servicio_prog_id'])])
                else:
                    producto_contrato_ids = self.pool.get('acp_contrato.contrato_producto').search(cr, uid, [('contrato_id','=',vals['contrato_id']),('programar_servicio_id','=',False)])

                for producto_contrato in self.pool.get('acp_contrato.contrato_producto').browse(cr, uid, producto_contrato_ids, context=context):
                    servicio_producto = {
                            'contrato_id': producto_contrato.contrato_id.id,
                            'servicio_id': res,
                            'product_id': producto_contrato.product_id.id,
                            'contrato_producto_id': producto_contrato.id,
                            'prodlot_id': producto_contrato.prodlot_id.id,
                            'ubicacion' : producto_contrato.ubicacion,
                            'observaciones': producto_contrato.observaciones,
                            'tipo_producto_n': producto_contrato.product_id.tipo_producto.name,
                            }
                    servicio_producto_obj.create(cr, uid, servicio_producto, context=context)
            if tipo_servicio_rec.actividad_inicial_id:
                ob = ''
                if vals.has_key('observaciones'):
                    ob = vals['observaciones']
                print 'servicio_rec.partner_id '
                print servicio_rec.partner_id
                print servicio_rec.partner_id.id
                tarea={
                      'servicio_id': res,
                      'tipo_servicio': tipo_servicio_rec.id,
                      'contrato_id': servicio_rec.contrato_id and servicio_rec.contrato_id.id or False,
                      'partner_id': servicio_rec.partner_id and servicio_rec.partner_id.id or False,
                      'user_id': SUPERUSER_ID,
                      'fecha': time.strftime('%Y-%m-%d %H:%M:%S'),
                      'actividad_id': tipo_servicio_rec.actividad_inicial_id.id,
                      'tipo': tipo_servicio_rec.actividad_inicial_id.tipo,
                      'fecha_limite': time.strftime('%Y-%m-%d %H:%M:%S'),
                      'observaciones': ob,
                      'user_seg_id': tipo_servicio_rec.user_seg_id and tipo_servicio_rec.user_seg_id.id or False,
                      'prioridad': '2',
                      'state': 'open',
                      'create_note':False
                             }
                tarea_id = self.pool.get('acp_contrato.tarea').create(cr, uid, tarea, context=context)
        return res



acp_contrato_servicio()

class acp_contrato_servicio_recurso(osv.osv):
    _name = "acp_contrato.servicio_recurso"
    _description = "Recurso de los servicios"

    _columns = {
                'servicio_id': fields.many2one('acp_contrato.servicio', 'Servicio', required=True, ondelete='cascade'),
                'contrato_id': fields.related('servicio_id','contrato_id',type='many2one',relation='acp_contrato.contrato',string='Servicio'),
                'recurso_id': fields.many2one('res.users', 'Recurso', required=True, change_default=True, select=True),
                'inicial': fields.boolean('Inicial'),
    }

acp_contrato_servicio_recurso()


class acp_contrato_tarea(osv.osv):
    _name = "acp_contrato.tarea"
    _inherit = ['mail.thread']
    _description = "Tareas de los servicios"

    def _get_partner_name(self, cr, uid, ids, field_name, arg, context):
        res={}
        reads = self.browse(cr, uid, ids, context)

        for record in reads:

            if record.partner_id and record.partner_id.comercial:
                p = record.partner_id.comercial
            else:
                p = record.partner_id.name
            res[record.id] = p
        return res
    def _get_detalle(self, cr, uid, ids, field_name, arg, context):
        res={}
        reads = self.browse(cr, uid, ids, context)

        for record in reads:
            desc_obs = ''
            obs = record.observaciones or ''
            obs2 = record.nota_facturacion or ''
            h = HTMLParser.HTMLParser()
            y = html2text.HTML2Text()
            y.ignore_images = True
            y.strong_mark = ''
            y.emphasis_mark = ''


            if obs:
                desc_obs = ' Observaciones:' + y.handle(h.unescape(obs))[0:250]
            if obs2:
                desc_obs = desc_obs + ' ***NOTA INTERNA***:' + obs2


            desc = desc_obs

            if record.tipo == 'anular':
                mot = record.motivo_anulacion_id and record.motivo_anulacion_id.name or ''
                desc = 'Motivo Anulación:' + mot + ' Observaciones:' + desc_obs
            if record.tipo == 'reclamacion':
                recl = record.motivo_reclamacion_id and record.motivo_reclamacion_id.name or ''
                desc = 'Motivo Reclamación:' + recl + ' Observaciones:' + desc_obs
            if record.tipo == 'espera':
                esp = record.motivo_espera_id and record.motivo_espera_id.name or ''
                desc = 'Motivo de Espera:' + esp + desc_obs
            if record.tipo == 'cita':
                desc = 'Cita/Reunion :' + desc_obs
            if record.tipo == 'contacto':
                desc = desc_obs
                # desc = str(record.contacto or '') + ', Tipo:' + str(record.tipo_contacto or '') + ', Relacion:' + str(record.relacion or '') + ', Telefonos:' + str(record.phone or '') + ' ' +  str(record.mobile or '') + desc_obs

            res[record.id] = desc
        return res

    def open_tarea(self,cr,uid,ids,context=None):

        if context is None:
            context = {}
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tarea',
            'view_type': 'form',
            'view_mode': 'form',
            'context': context,
            'res_model': 'acp_contrato.tarea',
            'nodestroy': True,
            'res_id': ids[0],
            'target':'current',
            }
    def _get_hours_to_act(self,cr, uid,ids,fields,arg,context):
        x={}
        for record in self.browse(cr, uid, ids):
            if record.state == 'open':
                sql='''select (extract(epoch from inter)/3600)::integer
                from (select (coalesce(fecha_limite,'2222-06-16 00:00:00')- now() at time zone 'UTC') as inter
                from acp_contrato_tarea where state = 'open' and id= %s) x'''%(record.id)

                cr.execute(sql)
                x[record.id] = cr.fetchall()[0][0]
            else:
                x[record.id] = 999


        return x
    def _get_hours(self,cr, uid,ids,fields,arg,context):
        x={}
        for record in self.browse(cr, uid, ids):
            sql='''select sum(horas)
                from acp_contrato_tarea_horas where tarea_id = %s '''%(record.id)

            cr.execute(sql)
            x[record.id] = cr.fetchall()[0][0]

        return x
    def get_name_(self, cr, uid, ids, field_name, arg, context):

        if not ids:
            return {}
        res = {}

        segs = self.browse(cr, uid, ids, context)
        for seg in segs:
            name =   str(seg.servicio_id.name) + '-' + str(seg.numero_tarea)
            res[seg.id] = name

        return res

    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id

    _columns = {
        'name': fields.function(get_name_, method=True, string='Name',type='char'),
        'servicio_id': fields.many2one('acp_contrato.servicio', 'Servicio', select=True,required=True,ondelete='cascade'),
        'tipo_servicio': fields.many2one('acp_contrato.tipo_servicio', 'Tipo Servicio', select=True,required=True),
        'contrato_id': fields.related(
                              'servicio_id',
                              'contrato_id',
                              type="many2one",
                              relation="acp_contrato.contrato",
                              string="Contrato",
                              required=False,
                              store=True) ,
        'partner_id': fields.many2one('res.partner', 'Cliente', select=True,required=True),
        'mail_pop_id': fields.many2one('acp_contrato.mail_pop', 'Ver email completo', select=True,required=False),
        'numero_tarea': fields.integer('Numero', required=True, select=True),
        'user_id': fields.many2one('res.users', 'Usuario', select=True,required=True),
        'parent_id': fields.many2one('acp_contrato.tarea', 'Tarea predecesora', select=True,required=False),
        'parent_actividad_id': fields.related(
                              'parent_id',
                              'actividad_id',
                              type="many2one",
                              relation="acp_contrato.actividad",
                              string="Tipo",
                              required=False,
                              store=False) ,
        'child_ids': fields.one2many('acp_contrato.tarea', 'parent_id','Tareas generadas', select=True,required=False),
        'fecha': fields.datetime('Fecha', required=True, select=True),
        'fecha_fin': fields.datetime('Fecha Finalización', required=False),
        'actividad_id': fields.many2one('acp_contrato.actividad', 'Actividad', select=True,required=False),
        'tipo': fields.selection([
                     ('anular','Anular'),
                     ('finalizar','Finalizar'),
                     ('reabrir','Re-Abrir'),
                     ('reclamacion','Reclamacion'),
                     ('asignarrecurso','Asignar Recurso'),
                     ('espera','Espera'),
                     ('cita','Cita'),
                     ('mail_recibido','Mail Recibido'),
                     ('enviar_mail','Enviar Email'),
                     ('contacto','Contacto'),
                     ('material','Material'),
                     ('otro','Otro'),
                      ], 'Tipo de actividad', required=True, select=True),
        'fecha_limite': fields.datetime('Fecha Limite'),
        'motivo_espera_id': fields.many2one('acp_contrato.motivo_espera', 'Motivo Espera', select=True),
        'motivo_anulacion_id': fields.many2one('acp_contrato.motivo_anulacion', 'Motivo Anulación', select=True),
        'reclamacion_fundada': fields.boolean('Fundada-Infundada'),
        'observaciones': fields.text('Descripción tarea'),
        'informado': fields.boolean('Informado'),
        'motivo_reclamacion_id': fields.many2one('acp_contrato.motivo_reclamacion', 'Motivo Reclamación', select=True),
        'nota_facturacion': fields.text('Nota Interna'),
        'especial_atencion': fields.boolean('Especial Atención', select=True),
        'user_seg_id': fields.many2one('res.users', 'Asignar a', select=True,required=True),
        'is_created' : fields.boolean('Created' , copy=False)            ,
        'mostrar_en_resumen': fields.boolean('Mostrar en Resumen',select=True, help="Si está marcado, esta actividad se mostrará en el resumen de actividades"),
        'especial_atencion': fields.boolean('Especial Atención', select=True, help="Si está marcado, esta actividad se mostrará en el cuadro 'Especial Atención' del contrato hasta que se finalice."),
        'enviar_mensaje': fields.boolean('Enviar mensaje al finalizar',  help="Enviará un mensaje al cerrarse la actividad a la persona que creó la actividad( siempre que la persona que tiene asignada la actividad sea diferente de la persona que creó la actividad"),
        'create_note' : fields.boolean('Crear Nota')            ,
        'company_id': fields.many2one('res.company', 'Company'),
        'prioridad': fields.selection([
                     ('3','Baja'),
                     ('2','Media'),
                     ('1','Alta'),
                      ], 'Prioridad', required=True),
        'detalle': fields.function(
            _get_detalle,
            type='text',
            method=True,
            string='Detalle'),
        'partner_name': fields.function(
            _get_partner_name,
            type='char',
            method=True,
            string='Detalle'),
        'state': fields.selection([
                     ('open','Abierto'),
                     ('done','Cerrado'),
                      ], 'Estado', required=True, select=True),
        'hours_to_act': fields.function(_get_hours_to_act,method=True,type='integer', string="Horas Proxima Actividad"),
        'tota_horas': fields.function(_get_hours,method=True,type='float', string="Horas"),
        'producto_lineas': fields.one2many('acp_contrato.tarea_producto', 'tarea_id', 'Materiales-Mano de Obra de la Tarea'),
        'horas_lineas': fields.one2many('acp_contrato.tarea_horas', 'tarea_id', 'Horas de la tarea'),
        'alarm_ids': fields.many2many('acp_contrato.alarm', 'acp_contrato_alarm_calendar_event_rel', string='Recordatorios', ondelete="restrict", copy=False),
    }
    _order='fecha desc'
    _defaults = {
        'fecha': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': lambda obj, cr, uid, context: uid,
        'user_seg_id': lambda obj, cr, uid, context: uid,
        'invoice_state':'noaplicable',
        'company_id': _get_default_company,
        'prioridad':'2'
    }


    def open_map(self, cr, uid, ids, context=None):
        address_obj= self.pool.get('acp_contrato.contrato')
        exp = address_obj.browse(cr, uid, ids, context=context)[0]
        url="http://maps.google.com/maps?oi=map&q="
        if exp.street:
            url+=exp.street.replace(' ','+')
        if exp.city:
            url+='+'+exp.city.replace(' ','+')
        if exp.state_id:
            url+='+'+exp.state_id.name.replace(' ','+')
        if exp.country_id:
            url+='+'+exp.country_id.name.replace(' ','+')
        if exp.zip:
            url+='+'+exp.zip.replace(' ','+')
        return {
        'type': 'ir.actions.act_url',
        'url':url,
        'target': 'new'
        }
    def onchange_zip_id(self, cursor, uid, ids, zip_id, context=None):
        if not zip_id:
            return {}
        if isinstance(zip_id, list):
            zip_id = zip_id[0]
        bzip = self.pool['res.better.zip'].browse(cursor, uid, zip_id, context=context)
        return {'value': {'zip': bzip.name,
                          'city': bzip.city,
                          'country_id': bzip.country_id.id if bzip.country_id else False,
                          'state_id': bzip.state_id.id if bzip.state_id else False,
                          }
                }

    def onchange_state(self, cr, uid, ids, state_id, context=None):
        if state_id:
            country_id = self.pool.get('res.country.state').browse(cr, uid, state_id, context).country_id.id
            return {'value':{'country_id':country_id}}
        return {}
    def create(self, cr, uid, vals, context=None):

        vals['is_created'] = True
        servicio_id = vals['servicio_id']

        actividad=self.pool.get('acp_contrato.actividad').browse(cr, uid, vals['actividad_id'], context=context)
        servicio=self.pool.get('acp_contrato.servicio').browse(cr, uid, servicio_id, context=context)
        contrato=servicio.contrato_id
        actividad_tipo = actividad.tipo
        actividad_especial_atencion = actividad.especial_atencion
        #asignamos el cliente
        #vals['partner_id'] = servicio.contrato_id.partner_id.id

        #comprobamos que no existe ninguna actividad que bloquee el contrato
        bloqueo_contrato_ids = self.search(cr, uid,         [('contrato_id','=',contrato.id),('actividad_id.bloquear_contrato','=',True),('state','=','open')], context=context)
        if len(bloqueo_contrato_ids) > 0:
            raise osv.except_osv(
                        _('No puede realizar acciones en este contrato'),
                        _('Existen actividades que estan bloqueando este contrato, cierre estas actividades antes de continnuar.'))

        #comprobamos que no existe ninguna actividad que bloquee el servicio
        bloqueo_servicio_ids = self.search(cr, uid,         [('servicio_id','=',servicio_id),('actividad_id.bloquear_servicio','=',True),('state','=','open')], context=context)
        if len(bloqueo_servicio_ids) > 0:
            raise osv.except_osv(
                        _('No puede realizar acciones en este servicio'),
                        _('Existen actividades que estan bloqueando este servicio, cierre estas actividades antes de continnuar.'))

        #creamos la nota
        if vals['create_note']:

            if vals.get('observaciones',False):
               obs = vals.get('observaciones',False)
            else:
               obs = ''

            note=self.pool.get('note.note')
            note.create(cr, uid, {'memo': contrato.name + '/' + servicio.name + ':' + obs}, context=context)

        #cerramos las actividades anteriores del Servicio que estan marcadas como "cerrar automáticamente"
        seguimientos_abiertos_ids = self.search(cr, uid,        [('servicio_id','=',servicio_id),('actividad_id.cerrar_automaticamente','=',True),('state','=','open')], context=context)
        if len(seguimientos_abiertos_ids) > 0:
            for seg_id in seguimientos_abiertos_ids:
                self.write(cr, uid, seg_id, {'state': 'done'}, context=context)

        if servicio.state == 'cancel' and actividad_tipo<>'reabrir':
            raise osv.except_osv(
                        _('Este Servicio está anulado'),
                        _('Este Servicio está anulado, no se puede realizar ninguna acción, re-abra el Servicio para poder crear tareas.'))
        if servicio.state == 'done' and actividad_tipo<>'reabrir':
            raise osv.except_osv(
                        _('Este Servicio está finalizado'),
                        _('Este Servicio está finalizado, no se puede realizar ninguna acción, re-abra el Servicio para poder crear tareas.'))

        if actividad_tipo=='anular':
            servicio.write({'state': 'cancel'}, context=context)
        if actividad_tipo=='finalizar':
            servicio.write( {'state': 'done'}, context=context)
        if actividad_tipo=='reabrir':
            servicio.write({'state': 'open'}, context=context)

        if vals.get('especial_atencion',False) :
            contrato.wkf_set_exception()




        cr.execute("""  select coalesce(max(numero_tarea)+1,1)
                                from acp_contrato_tarea
                                where servicio_id = %s""" % servicio_id)
        res = cr.fetchall()
        vals['numero_tarea'] = res[0][0]


        user_id = uid
        user_seg_id = vals.get('user_seg_id',False)

        #asignamos el recurso
        recursos = [recurso.recurso_id.id for recurso in servicio.recurso_ids]
        if user_seg_id not in recursos:
            if len(recursos) > 0:
                servicio.write({'recurso_ids': [(0, 0, {'recurso_id': user_seg_id,'servicio_id':servicio_id,'inicial':False})]}, context=context)
            else:
                servicio.write({'recurso_ids': [(0, 0, {'recurso_id': user_seg_id,'servicio_id':servicio_id,'inicial':True})]}, context=context)
        recursos = [recurso.recurso_id.id for recurso in servicio.recurso_ids]
        if user_id not in recursos:
            if len(recursos) > 0:
                servicio.write({'recurso_ids': [(0, 0, {'recurso_id': user_id,'servicio_id':servicio_id,'inicial':False})]}, context=context)
            else:
                servicio.write({'recurso_ids': [(0, 0, {'recurso_id': user_id,'servicio_id':servicio_id,'inicial':True})]}, context=context)
        #creamos la tarea
        res = super(acp_contrato_tarea, self).create(cr, uid, vals, context=context)
        #Comprobar si hay que enviar un mensaje
        if user_id and user_seg_id:
            if (user_id <> user_seg_id)  :

                ctx = dict(context)
                ctx.update({
                    'default_model': 'acp_contrato.tarea',
                    'default_res_id': res,
                    'default_composition_mode': 'comment',
                    'mark_so_as_sent': True
                })
                mail_obj = self.pool.get('mail.compose.message')

                if vals.get('observaciones',False):
                   obs = vals.get('observaciones',False).replace('\n', '<br />')

                else:
                   obs = ''

                #partner_id = self.pool.get('res.users').browse(cr, SUPERUSER_ID, user_seg_id, context=context).partner_id.id
                sql='''select partner_id from res_users
                       where id =  %s '''%(user_seg_id)
                cr.execute(sql)
                partner_id =cr.dictfetchall()[0]['partner_id']

                if 'default_parent_id' in ctx:
                    del ctx['default_parent_id']
                subject = contrato.name + ' NUEVA ACTIVIDAD ASIGNADA:' + self.pool.get('acp_contrato.actividad').browse(cr, uid, vals.get('actividad_id',False), context=context).name
                body = contrato.name + ' NUEVA ACTIVIDAD ASIGNADA:' + self.pool.get('acp_contrato.actividad').browse(cr, uid, vals.get('actividad_id',False), context=context).name + ' , Observaciones:' + obs
                mail_id = mail_obj.create(cr, uid, {'partner_ids':[(6, 0, [partner_id])],'subject':subject,'body':body}, context=ctx)
                mail_obj.browse(cr, uid, mail_id, context).send_mail()

        return res

    def close_act(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'done','fecha_fin':datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, context=context)
        #Comprobar si hay que enviar un mensaje al finalizar y enviarlo
        enviar_mensaje = self.browse(cr, uid, ids[0], context=context).enviar_mensaje
        if enviar_mensaje:
            tarea = self.browse(cr, uid, ids[0], context=context)
            user_id = tarea.user_id.id
            user_seg_id = tarea.user_seg_id.id
            if user_id <> user_seg_id:
                ctx = dict(context)
                ctx.update({
                    'default_model': 'acp_contrato.tarea',
                    'default_res_id': ids[0],
                    'default_composition_mode': 'comment',
                    'mark_so_as_sent': True
                })
                mail_obj = self.pool.get('mail.compose.message')


                partner_id = self.browse(cr, uid, ids[0], context=context).user_id.partner_id.id
                subject = 'Actividad:' + tarea.actividad_id.name + ' Finalizada'
                body = 'Actividad:' + tarea.actividad_id.name + ' Finalizada, Observaciones:' + str(tarea.observaciones or '')
                mail_id = mail_obj.create(cr, uid, {'partner_ids':[(6, 0, [partner_id])],'subject':subject,'body':body}, context=ctx)
                mail_obj.browse(cr, uid, mail_id, context).send_mail()


        #Si el contrato esta en excepcion comprobar si hay mas actividades en excepcion y si no hay pasarlo a open
        contrato = self.browse(cr, uid, ids[0], context=context).contrato_id
        if contrato.state == 'exception':
            seguimientos_ids = self.pool.get('acp_contrato.tarea').search(cr, uid, [('contrato_id','=',contrato.id),('especial_atencion','=',True),('state','=','open')], context=context)
            if len(seguimientos_ids) == 0:
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'acp_contrato.contrato', contrato.id, 'set_ignore_exception', cr)



        return True

    def onchange_servicio_id(self, cr, uid, ids, servicio_id, context=None):
        v = {}
        v['tipo_servicio'] = False
        if servicio_id:
            servicio = self.pool.get('acp_contrato.servicio').browse(cr, uid, servicio_id, context=context)
            v['tipo_servicio'] = servicio.tipo_servicio.id
        return {'value': v}
    def onchange_actividad_id(self, cr, uid, ids, actividad_id, fecha, servicio_id, context=None):
        v = {}
        if actividad_id:

            actividad = self.pool.get('acp_contrato.actividad').browse(cr, uid, actividad_id, context=context)
            servicio = self.pool.get('acp_contrato.servicio').browse(cr, uid, servicio_id, context=context)
            fecha_d=datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')
            v['fecha_limite'] = (fecha_d + timedelta(hours=actividad.horas)).strftime('%Y-%m-%d %H:%M:%S')
            v['tipo'] = actividad.tipo
            v['especial_atencion'] = actividad.especial_atencion
            v['mostrar_en_resumen'] = actividad.mostrar_en_resumen
            v['state'] = actividad.estado_inicial
            v['enviar_mensaje'] = actividad.enviar_mensaje
            v['prioridad'] = actividad.prioridad


            producto_lineas = []
            for prod in  actividad.producto_lineas:
                x= self.pool.get('acp_contrato.tarea_producto').onchange_product_id(cr, uid, False, prod.product_id.id, context=context)



                producto_lineas.append((0, 6,  {'invoice_state':prod.invoice_state,'tax_id':x['value']['tax_id'], 'importe':x['value']['importe'],'product_id': prod.product_id,'invoice_state':prod.invoice_state ,'cantidad':prod.cantidad}))
            v['producto_lineas'] = producto_lineas

            if actividad.alarm_ids:
                v['alarm_ids']= actividad.alarm_ids
        else:
                v['fecha_limite'] = ''
                v['tipo'] = ''
                v['mostrar_en_resumen'] = ''
                v['state'] = ''
                v['especial_atencion']=''
                v['enviar_mensaje'] = ''
                v['prioridad']= ''
                v['alarm_ids']= ''
        return {'value': v}
    def onchange_motivo_espera_id(self, cr, uid, ids, motivo_espera_id, fecha, context=None):
        v = {}
        if motivo_espera_id:
            motivo_espera = self.pool.get('acp_contrato.motivo_espera').browse(cr, uid, motivo_espera_id, context=context)
            if motivo_espera.fecha_limite:
                fecha_d=datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')
                v['fecha_limite'] = (fecha_d + timedelta(hours=motivo_espera.horas)).strftime('%Y-%m-%d %H:%M:%S')
            else:
                v['fecha_limite']=''
        else:
            v['fecha_limite']=''
        return {'value': v}

    def _send_mail(self, cr, uid, ids, email_from=tools.config.get('email_from', False),
                                template_xmlid=False, force=False, context=None):

        res = False



        mail_ids = []
        data_pool = self.pool['ir.model.data']
        mailmess_pool = self.pool['mail.message']
        mail_pool = self.pool['mail.mail']
        template_pool = self.pool['email.template']

        if not isinstance(ids, (tuple, list)):
            ids = [ids]

        dummy, template_id = data_pool.get_object_reference(cr, uid, 'acp_contrato', template_xmlid)


        for tarea in self.browse(cr, uid, ids, context=context):
            if tarea.user_seg_id.partner_id.email and email_from and (tarea.user_seg_id.partner_id.email != email_from or force):

                mail_id = template_pool.send_mail(cr, uid, template_id, tarea.id, context=context)

                #vals = {}
                #the_mailmess = mail_pool.browse(cr, uid, mail_id, context=context).mail_message_id
                #mailmess_pool.write(cr, uid, [the_mailmess.id], vals, context=context)
                mail_ids.append(mail_id)

        if mail_ids:
            res = mail_pool.send(cr, uid, mail_ids, context=context)

        return res

    def new_tarea(self,cr,uid,ids,context=None):

        tarea_obj=self.pool.get('acp_contrato.tarea')

        tarea=tarea_obj.browse(cr, uid, ids[0], context=context)
        servicio=tarea.servicio_id
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

        return {
            'type': 'ir.actions.act_window',
            'name': 'Tarea',
            'view_type': 'form',
            'view_mode': 'form',
            'context': {'default_parent_id':ids[0],'default_servicio_id':servicio.id,'default_contrato_id':contrato.id,'default_partner_id':servicio.partner_id.id},
            'res_model': 'acp_contrato.tarea',
            'nodestroy': True,
            'target':'current',
            }

acp_contrato_tarea()

class acp_contrato_contrato_producto(osv.osv):
    _name = "acp_contrato.contrato_producto"
    _description = "Productos del contrato de mantenimientor"

    def onchange_product_id(self, cr, uid, ids, product, context=None):
        if not product:
             return {'value': {'tipo_producto': False,'prodlot_id': False}}

        product_rec = self.pool.get('product.product').browse(cr, uid, product, context=context)


        val = {
            'tipo_producto': product_rec.tipo_producto and product_rec.tipo_producto.id or False,
            'tipo_producto_n': product_rec.tipo_producto and product_rec.tipo_producto.name or False,
            'prodlot_id': False
        }
        return {'value': val}

    _columns = {
        'contrato_id': fields.many2one('acp_contrato.contrato', 'Contrato', required=True, ondelete='cascade'),
        'product_id': fields.many2one('product.product', 'Producto', required=True, change_default=True, select=True),
        'tipo_producto': fields.related('product_id', 'tipo_producto', type='many2one', relation='acp_contrato.tipo_producto', string="Tipo de Producto", readonly="1"),
        'tipo_producto_n': fields.char(string="Tipo de Producto Nombre", size=120),
        'prodlot_id': fields.many2one('stock.production.lot', 'Numero de Serie', domain="[('product_id','=',product_id)]"),
        'historico_ids': fields.one2many('acp_contrato.servicio_producto','contrato_producto_id', 'Historico de servicios'),
        'ubicacion': fields.char('Ubicación', size=64, required=False),
        'estado': fields.selection([
            ('enservicio', 'En Servicio'),
            ('fueraenservicio', 'Fuera de Servicio'),
            ('reserva', 'En la Reserva'),
            ], 'Estado', select=True,required=True),
        'observaciones': fields.text('Observaciones'),
        'programar_servicio_id': fields.many2one('acp_contrato.programar_servicio', 'Programar Servicio', required=False),
    }
    _defaults = {
        'satisfactorio': 'no',
        'estado': 'enservicio',
        }

    def create(self, cr, uid, vals, context=None):
        res = super(acp_contrato_contrato_producto, self).create(cr, uid, vals, context=context)
        # Si esta configurado en el producto se crea la programación
        programar_servicio_obj = self.pool.get('acp_contrato.programar_servicio')
        product_obj = self.pool.get('product.product')
        fechas_servicio_obj = self.pool.get('acp_contrato.fechas_servicio')
        product = product_obj.browse(cr, uid,vals['product_id'],context=context)

        if product.tipo_servicio.id and product.perioricidad_servicio:
            programar_servicio_ids = programar_servicio_obj.search(cr, uid, [('contrato_id','=',vals['contrato_id']),('tipo_servicio_id','=',product.tipo_servicio.id),('perioricidad','=',product.perioricidad_servicio)])
            if not programar_servicio_ids:
                nombre_servicio = product.tipo_servicio.name.upper() + " "+ product.perioricidad_servicio.upper()
                programar_servicio_id = programar_servicio_obj.create(cr, uid, {'contrato_id': vals['contrato_id'],
                                                                                'name': nombre_servicio,
                                                                                'contratado': True,
                                                                                'tipo_servicio_id': product.tipo_servicio.id,
                                                                                'perioricidad': product.perioricidad_servicio,
                                                                                }, context=context)
                if programar_servicio_id:
                    rango_servicio = 0
                    if product.perioricidad_servicio:
                        if product.perioricidad_servicio == 'mensual':
                            rango_servicio = 1
                        if product.perioricidad_servicio == 'trimestral':
                            rango_servicio = 3
                        if product.perioricidad_servicio == 'semestral':
                            rango_servicio = 6
                        if product.perioricidad_servicio == 'anual':
                            rango_servicio = 12
                        for num_mes in range(0,12,rango_servicio):
                            mes_servicio_d = datetime.today()+ relativedelta(months=num_mes)
                            mes_servicio = mes_servicio_d.strftime('%m')
                            fechas_servicio_id = fechas_servicio_obj.create(cr, uid, {'programacion_id': programar_servicio_id,
                                                                                      'mes': mes_servicio,
                                                                                      'dia': 1,
                                                                                       }, context=context)
            else:
                programar_servicio_id = programar_servicio_ids[0]

            self.write(cr, uid, res, {'programar_servicio_id': programar_servicio_id}, context=context)


        return res
acp_contrato_contrato_producto()

class acp_contrato_servicio_producto(osv.osv):
    _name = "acp_contrato.servicio_producto"
    _description = "Productos del servicio"
    def onchange_product_id(self, cr, uid, ids, product, context=None):
        if not product:
             return {'value': {'tipo_producto': False,'prolot_id': False}}

        product_rec = self.pool.get('product.product').browse(cr, uid, product, context=context)


        val = {
            'tipo_producto': product_rec.tipo_producto and product_rec.tipo_producto.id or False,
            'tipo_producto_n': product_rec.tipo_producto and product_rec.tipo_producto.name or False,
            'prolot_id': False
        }
        return {'value': val}
    _SELECTION = [
            ('enservicio', 'En Servicio'),
            ('fueraenservicio', 'Fuera de Servicio'),
            ('reserva', 'En la Reserva'),
            ]

    _columns = {
        'contrato_id': fields.related('servicio_id','contrato_id',type="many2one",relation="acp_contrato.contrato",string="Contrato",required=True,store=True) ,
        'fecha': fields.related('servicio_id','fecha',type="datetime",string="Fecha",store=False) ,
        'servicio_id': fields.many2one('acp_contrato.servicio', 'Servicio', required=True, ondelete='cascade'),
        'contrato_producto_id':fields.many2one('acp_contrato.contrato_producto', 'Producto del contrato', required=True, ondelete='restrict'),
        'product_id': fields.related('contrato_producto_id', 'product_id', type='many2one', relation='product.product', string="Producto", readonly="1",store=True),
        'tipo_producto': fields.related('product_id', 'tipo_producto', type='many2one', relation='acp_contrato.tipo_producto', string="Tipo de Producto", readonly="1"),
        'tipo_producto_n': fields.char(string="Tipo de Producto Nombre", size=64),
        'prodlot_id': fields.related('contrato_producto_id', 'prodlot_id', type='many2one', relation='stock.production.lot', string="Numero de Serie", store=True),
        'ubicacion': fields.related('contrato_producto_id', 'ubicacion', type='char', string="Ubicación", store=True),
        'estado': fields.related('contrato_producto_id','estado',selection=_SELECTION,type='selection',string="Estado",store=True),
        'satisfactorio': fields.selection([
            ('si', 'Si'),
            ('no', 'No'),
            ], 'Satisfactorio', select=True,required=True),
        'observaciones': fields.text('Observaciones'),
    }
    _defaults = {
        'satisfactorio': 'no',
        'estado': 'enservicio',
        }
acp_contrato_servicio_producto()


class acp_contrato_tarea_producto(osv.osv):
    _name = "acp_contrato.tarea_producto"
    _description = "Productos asociados a tareas"

    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        user_obj = self.pool.get('res.users')
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.importe
            taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.cantidad, line.product_id, False)
            cur = user_obj.browse(cr, uid,uid).company_id.currency_id
            #cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total_included'])
        return res

    def onchange_product_id(self, cr, uid, ids, product, context=None):
        if not product:
             return {'value': {'tipo_producto': False,'tipo_producto_n':False,'tax_id':False,'importe':0.0,'prolot_id': False}}

        product_rec = self.pool.get('product.product').browse(cr, uid, product, context=context)

        taxes = product_rec.taxes_id
        #taxes = fpos.map_tax(taxes)



        val = {
            'tipo_producto': product_rec.tipo_producto and product_rec.tipo_producto.id or False,
            'tipo_producto_n': product_rec.tipo_producto and product_rec.tipo_producto.name or False,
            'tax_id':taxes,
            'importe':product_rec.lst_price,
            'prolot_id': False
        }
        return {'value': val}
    _columns = {
        'tarea_id': fields.many2one('acp_contrato.tarea', 'Tarea', required=True, ondelete='cascade'),
        'product_id': fields.many2one('product.product', 'Producto', required=True, change_default=True, select=True),
        'tipo_producto': fields.related('product_id', 'tipo_producto', type='many2one', relation='acp_contrato.tipo_producto', string="Tipo de Producto", readonly="1"),
        'tipo_producto_n': fields.char(string="Tipo de Producto Nombre", size=64),
        'prodlot_id': fields.many2one('stock.production.lot', 'Numero de Serie', domain="[('product_id','=',product_id),('tipo_producto','=',tipo_producto)]"),
        'cantidad': fields.float('Cantidad', digits_compute= dp.get_precision('Product UoS'), required=True  ),
        'importe': fields.float('Importe',  digits_compute=dp.get_precision('Product Price'), required=True  ),
        'tax_id': fields.many2many('account.tax', 'acp_contrato_tarea_producto_tax', 'order_line_id', 'tax_id','Impuestos'),
        'subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
        'ubicacion': fields.char('Ubicación', size=64, required=False),
        'incluir':    fields.boolean('Incluir en la lista de materiales a  mantener',help="* Indica si este producto debe incluirse ne la lista de materiales a mantener."),
        'observaciones': fields.text('Observaciones'),
        'invoice_state': fields.selection([
                     ('noaplicable','No Aplicable'),
                     ('parafacturar','Para Facturar'),
                     ('facturado','Facturado')
            ], 'Estado Factura', required=True, select=True),
        'contrato_id': fields.related('tarea_id','contrato_id',type="many2one",relation="acp_contrato.contrato",string="Contrato",required=False,store=True) ,
        'servicio_id': fields.related('tarea_id','servicio_id',type="many2one",relation="acp_contrato.servicio",string="Servicio",required=False,store=True) ,
        'partner_id': fields.many2one('res.partner', 'Cliente', required=False, select=True,store=True),
        'servicio_fecha': fields.related('servicio_id','fecha', type="date", string="Fecha", required=False) ,
    }

    _defaults = {
        'invoice_state':'noaplicable',
        'cantidad': 1.00
    }



    def create(self, cr, uid, vals, context=None):

        if vals.get('tarea_id',False):

            tarea=self.pool.get('acp_contrato.tarea').browse(cr, uid, vals.get('tarea_id',False), context=context)
            #asignamos el cliente

            vals['partner_id'] = tarea.servicio_id.contrato_id.partner_id.id

        res = super(acp_contrato_tarea_producto, self).create(cr, uid, vals, context=context)
        # si se marca la opcion de incluir insertar en la lista de materiales del contrato
        if vals.get('incluir',False):
            tp=self.pool.get('acp_contrato.tarea_producto').browse(cr, uid,res,context=context)
            servicio = tp.tarea_id.servicio_id
            contrato = tp.tarea_id.servicio_id.contrato_id
            args = [('contrato_id', '=' ,contrato.id), ('product_id', '=', vals['product_id']), ('estado','=','enservicio')]
            if vals['prodlot_id']:
                args.append(('prodlot_id', '=', vals['prodlot_id']))
            else:
                args.append(('prodlot_id', '=', False))
            contrato_producto_obj = self.pool.get('acp_contrato.contrato_producto')
            servicio_producto_obj = self.pool.get('acp_contrato.servicio_producto')


            contrato_producto = {
                    'contrato_id': contrato.id,
                    'product_id': vals.get('product_id',False),
                    'prodlot_id': vals.get('prodlot_id',False),
                    'ubicacion' : vals.get('ubicacion',False),
                    'estado': 'enservicio',
                    'observaciones': vals['observaciones'],
                    'tipo_producto_n': tp.product_id.tipo_producto.name,
                    }
            contrato_producto_id = contrato_producto_obj.create(cr, uid, contrato_producto, context=context)
            servicio_producto = {
                    'servicio_id': servicio.id,
                    'contrato_id': contrato.id,
                    'product_id': vals.get('product_id',False),
                    'contrato_producto_id': contrato_producto_id,
                    'prodlot_id': vals.get('prodlot_id',False),
                    'ubicacion' : vals.get('ubicacion',False),
                    'observaciones': vals['observaciones'],
                    'tipo_producto_n': tp.product_id.tipo_producto.name,
                    }
            servicio_producto_obj.create(cr, uid, servicio_producto, context=context)

        return res


acp_contrato_tarea_producto()


class acp_contrato_tarea_horas(osv.osv):
    _name = "acp_contrato.tarea_horas"
    _description = "Horas asociados a tareas"


    _columns = {
        'tarea_id': fields.many2one('acp_contrato.tarea', 'Tarea', required=True, ondelete='cascade'),
        'fecha': fields.date('Fecha' ,required=True ),
        'horas': fields.float('Horas', required=True  ),
        'descripcion': fields.text('Descripción', required=False  ),
        'contrato_id': fields.related(
                              'tarea_id',
                              'contrato_id',
                              type="many2one",
                              relation="acp_contrato.contrato",
                              string="Contrato",
                              required=False,
                              store=True) ,
        'parent_id': fields.related(
                              'contrato_id',
                              'parent_id',
                              type="many2one",
                              relation="acp_contrato.contrato",
                              string="Contrato padre",
                              required=False,
                              store=False) ,
    }

    _defaults = {
        'fecha': lambda *a: time.strftime('%Y-%m-%d'),
        }



acp_contrato_tarea_horas()



class acp_contrato_facturacion(osv.osv):
    _name = "acp_contrato.facturacion"
    _description = "Facturacion de contratos"
    _columns = {
        'contrato_id': fields.many2one('acp_contrato.contrato', 'Contrato', required=True, ondelete='cascade'),
        'name': fields.char('Descripcion', required=True,size=60),
        'autofactura':    fields.boolean('Facturar Automaticamente',
                help='* Si está marcado, se realizará la factura de forma automatica cuando \
                    \n* se lanza el proceso de facturacion de contratos. \
                    \n* Si no está marcado, la factura se creará desde el servicioo contrato de forma manual. '),
        'generar_pedido':    fields.boolean('Generar Pedido de Venta',
                help='* Si está marcado se generará un Pedido de Venta en vez de una factura, \
                    \n* esto permite agregar productos antes de facturar y generar albaranes de entrega. '),
        'fechas_lineas': fields.one2many('acp_contrato.fechas_facturacion', 'facturacion_id', 'Fechas de factura',copy=True),
        'conceptos_lineas': fields.one2many('acp_contrato.conceptos_factura', 'facturacion_id', 'Conceptos a facturar',copy=True),
        'invoice_state': fields.selection([
                     ('noaplicable','No Aplicable'),
                     ('parafacturar','Para Facturar'),
                     ('facturado','Facturado'),
            ], 'Estado Factura', required=True, select=True),
    }

    _defaults = {
        'autofactura': True,
        'materiales': True,
        'generar_pedido': False,
        'invoice_state':'noaplicable',
        }
acp_contrato_facturacion()
class acp_contrato_fechas_facturaion(osv.osv):
    _name = "acp_contrato.fechas_facturacion"
    _description = "Fechas de facturacion"
    _columns = {
        'facturacion_id': fields.many2one('acp_contrato.facturacion', 'Facturacion', required=True,ondelete='cascade'),
        'mes': fields.selection([
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
            ], 'Mes', required=True),
        'dia': fields.integer('Día Facturación'),
         }

acp_contrato_fechas_facturaion()
class acp_contrato_conceptos_factura(osv.osv):
    _name = "acp_contrato.conceptos_factura"
    _description = "Conceptos a Facturar"
    _columns = {
        'facturacion_id': fields.many2one('acp_contrato.facturacion', 'Facturacion', required=True, ondelete='cascade'),
        'product_id': fields.many2one('product.product', 'Producto', required=True, change_default=True, select=True),
        'name': fields.char('Descripcion', required=True),
        'cantidad': fields.float('Cantidad', digits_compute= dp.get_precision('Product UoS'), required=True  ),
        'importe': fields.float('Importe',  digits_compute=dp.get_precision('Product Price'), required=True  ),

    }
acp_contrato_conceptos_factura()

class acp_contrato_programar_servicio(osv.osv):
    _name = "acp_contrato.programar_servicio"
    _description = "Programación de Servicios"
    _columns = {
        'contrato_id': fields.many2one('acp_contrato.contrato', 'Contrato', required=True, ondelete='cascade'),
        'name': fields.char('Descripcion', required=True,size=60),
        'tipo_servicio_id': fields.many2one('acp_contrato.tipo_servicio', 'Tipo de Servicio', required=True, select=True),
        'invoice_state': fields.selection([
                     ('noaplicable','No Aplicable'),
                     ('parafacturar','Para Facturar'),
                     ('facturado','Facturado')
            ], 'Estado Factura', required=False, select=True),
        'contratado': fields.boolean('Contratado', help="Si no se marca esta opcion, se generará una oportunidad de negocio en vez de un servicio"),
        'fechas_lineas': fields.one2many('acp_contrato.fechas_servicio', 'programacion_id', 'Fechas de Servicios'),
        'perioricidad': fields.selection([
                     ('mensual','Mensual'),
                     ('trimestral','Trimestral'),
                     ('semestral','Semestral'),
                     ('anual','Anual'),
                      ], 'Periodicidad'),

    }
    _defaults = {
        'invoice_state':'noaplicable',
        'materiales': True,
        'contratado': True,
    }
acp_contrato_programar_servicio()
class acp_contrato_fechas_servicio(osv.osv):
    _name = "acp_contrato.fechas_servicio"
    _description = "Fechas de los Servicios Programados"
    _columns = {
        'programacion_id': fields.many2one('acp_contrato.programar_servicio', 'Programacion', required=True, ondelete='cascade'),
        'mes': fields.selection([
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
            ], 'Mes', required=True),
        'dia': fields.integer('Día Servicio'),
         }
    _defaults = {
        'contratado': 1,
    }
acp_contrato_fechas_servicio()

#no se usa , se mantiene por compatibilidad
class acp_contrato_servicio_operario(osv.osv):
    _name = "acp_contrato.servicio_operario"
    _description = "Operarios de los servicios"

    _columns = {
                'name': fields.char( 'Nombre',seze=120),
        'servicio_id': fields.many2one('acp_contrato.servicio', 'Servicio', required=True, ondelete='cascade'),
        'operario_id': fields.many2one('res.partner', 'Operario', required=True, change_default=True, select=True),
    }

acp_contrato_servicio_operario()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
